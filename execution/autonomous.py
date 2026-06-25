"""
execution/autonomous.py — deep-thinker otonom akışının yardımcıları.
Ne yapar:
  - opportunity_gate: bir varlık ANALİZE değer mi (önce demir kurallar/trigger ile ön-eler).
  - wait_diagnosis: trade yoksa NEDEN WAIT olduğunu yapısal, kısa gerekçeye çevirir.
  - build_decision_context: LLM'e verilecek varlık-başı bağlamı (sayılar + ön-değerlendirme) kurar.
Neden:
  deep-thinker her tur 4 varlığı sıfırdan düşünüyor (turlar arası öğrenme YOK — CLAUDE.md kural 9).
  Gate, LLM'i yalnız gerçek fırsatlara yönlendirip over-trading'i (L-03) kısar; wait_diagnosis
  kararın DOSYADA yaşaması (kural 10) için tutarlı WAIT metni üretir; context, "uydurma yok / kaynak
  zorunlu" (kural 6) ilkesini somut sayılara bağlar.
Çıktı: Saf yardımcılar — I/O yok. LLM çağrısı run_deepthinker.py'de.
"""

from triggers import rules


def opportunity_gate(asset):
    """Ön-eleme: bu varlıkta meşru bir giriş fırsatı OLABİLİR mi?
    Döner: (passes: bool, side: str|None, reason: str).
    Geçerse LLM derin analiz yapar; geçmezse doğrudan WAIT (LLM harcanmaz).
    Not: Gate KARAR vermez — sadece 'bakmaya değer mi' kapısıdır."""
    tr = rules.evaluate(asset)
    if tr.blockers:
        return False, None, "; ".join(tr.blockers)
    if not tr.fired:
        return False, None, "; ".join(tr.reasons) or "geçerli trigger yok"
    reason = "; ".join(tr.reasons)
    if tr.warnings:
        reason += " | uyarı: " + "; ".join(tr.warnings)
    return True, tr.side, reason


def wait_diagnosis(asset):
    """Trade açılmayan varlık için kısa, yapısal WAIT gerekçesi üretir.
    state/deepthinker_decision.json'daki 'waits' metinleriyle aynı dille tutarlı."""
    tr = rules.evaluate(asset)
    trend_1d = asset["trends"]["1d"]
    parts = []
    if tr.blockers:
        parts.append("; ".join(tr.blockers))
    elif not tr.fired:
        parts.append("; ".join(tr.reasons) or "trigger yok")
    # bağlamsal renk
    align = "/".join(f"{tf}:{v}" for tf, v in asset["trends"].items())
    parts.append(f"trend {align}")
    parts.append(f"RSI {asset['rsi']}, MACDh {asset['macd_hist']}")
    if tr.warnings:
        parts.append("uyarı: " + "; ".join(tr.warnings))
    return " | ".join(parts)


def build_decision_context(snapshot):
    """LLM'e verilecek varlık-başı bağlam sözlüğü.
    Her varlık: ham sayılar + ön-değerlendirme (gate sonucu). LLM bunu okuyup analyst/challenger yapar.
    'Uydurma yok': tüm seviyeler snapshot'tan; ATR stop/target önerisi yalnız referans."""
    ctx = {"timestamp": snapshot.get("timestamp"), "regime": snapshot.get("regime"), "assets": {}}
    for coin, a in snapshot["assets"].items():
        passes, side, reason = opportunity_gate(a)
        atr = a["atr"]
        price = a["price"]
        # Referans seviyeler (run_deterministic ile aynı 1.5×/3.0× ATR mantığı)
        if side == "buy":
            ref_stop, ref_target = round(price - 1.5 * atr, 4), round(price + 3.0 * atr, 4)
        elif side == "sell":
            ref_stop, ref_target = round(price + 1.5 * atr, 4), round(price - 3.0 * atr, 4)
        else:
            ref_stop = ref_target = None
        ctx["assets"][coin] = {
            "price": price, "rsi": a["rsi"], "macd_hist": a["macd_hist"],
            "macd_line": a["macd_line"], "signal_line": a["signal_line"], "atr": atr,
            "funding": a["funding"], "funding_class": rules.classify_funding(a["funding"]),
            "trends": a["trends"], "trigger": a["trigger"],
            "gate": {"opportunity": passes, "side": side, "reason": reason},
            "reference_levels": {"entry": price, "stop": ref_stop, "target": ref_target},
        }
    return ctx
