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
from execution import simulator, baselines

# ATR çarpanları — stop/target referansı (run_deterministic ile aynı: 1.5× / 3.0×).
STOP_ATR_MULT = 1.5
TARGET_ATR_MULT = 3.0

# Anchor kirliliği — karar bağlamında ASLA bulunmaması gereken anahtarlar (geçmiş sonuca demir atma).
ANCHOR_FORBIDDEN = ("past_results", "win_streak", "last_pnl", "previous_trade", "pnl_history")
SHARP_MOVE_PCT = 0.05  # ≥%5 excursion = "sert hareket" (kaçırılan-hareket analizi)


def reference_levels(price, atr, side):
    """Yöne göre referans stop/target (1.5×/3.0× ATR). Tek kaynak: hem deterministic kol hem
    deep-thinker bağlamı buradan üretir. side None ise (None, None)."""
    if side == "buy":
        return round(price - STOP_ATR_MULT * atr, 4), round(price + TARGET_ATR_MULT * atr, 4)
    if side == "sell":
        return round(price + STOP_ATR_MULT * atr, 4), round(price - TARGET_ATR_MULT * atr, 4)
    return None, None


def opportunity_gate(asset, allow_counter_trend=False):
    """Ön-eleme: bu varlıkta meşru bir giriş fırsatı OLABİLİR mi?
    Döner: (passes: bool, side: str|None, reason: str).
    Geçerse LLM derin analiz yapar; geçmezse doğrudan WAIT (LLM harcanmaz).
    allow_counter_trend=True yalnız C (aggressive) kolu için — counter-trend dip-alımı açar.
    Not: Gate KARAR vermez — sadece 'bakmaya değer mi' kapısıdır."""
    tr = rules.evaluate(asset, allow_counter_trend)
    if tr.blockers:
        return False, None, "; ".join(tr.blockers)
    if not tr.fired:
        return False, None, "; ".join(tr.reasons) or "geçerli trigger yok"
    reason = "; ".join(tr.reasons)
    if tr.warnings:
        reason += " | uyarı: " + "; ".join(tr.warnings)
    return True, tr.side, reason


def wait_diagnosis(asset, allow_counter_trend=False):
    """Trade açılmayan varlık için kısa, yapısal WAIT gerekçesi üretir.
    state/deepthinker_decision.json'daki 'waits' metinleriyle aynı dille tutarlı."""
    tr = rules.evaluate(asset, allow_counter_trend)
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


def check_path(position, candles):
    """TARAMA-ARASI yol kontrolü: karar anından bu yana ki mumların HIGH/LOW'una bakar.
    Sadece anlık fiyat değil — iki tarama arasında stop'a/target'a değip dönmüş olsa bile YAKALAR.
    Döner: {status, hit_at, ambiguous}. status: open|stop_hit|target_hit. İlk değen kazanır;
    tek mumda ikisi de değdiyse ambiguous=True → konservatif stop."""
    side = position["side"]
    stop = position["stop"]
    target = position["target"]
    for c in candles:
        hi = float(c["h"]); lo = float(c["l"]); t = c.get("t")
        if side == "buy":
            hit_stop = lo <= stop
            hit_target = hi >= target
        else:
            hit_stop = hi >= stop
            hit_target = lo <= target
        if hit_stop and hit_target:
            return {"status": "stop_hit", "hit_at": t, "ambiguous": True}  # konservatif
        if hit_stop:
            return {"status": "stop_hit", "hit_at": t, "ambiguous": False}
        if hit_target:
            return {"status": "target_hit", "hit_at": t, "ambiguous": False}
    return {"status": "open", "hit_at": None, "ambiguous": False}


def evaluate_close(position, exit_price, entry_rsi, funding_rate=0.0, funding_periods=0):
    """Kapanışı paketler: net % (fee-dahil, simulator) + baseline karşılaştırma (L-01) + cost özeti (L-03)."""
    res = simulator.simulate_trade(position["side"], position["entry"], exit_price,
                                   position["notional"], funding_rate=funding_rate,
                                   funding_periods=funding_periods, slippage_bps=0.0)
    net_pct = (res.net_pnl / position["notional"]) if position["notional"] else 0.0
    base = baselines.compare(net_pct, position["entry"], exit_price, position["side"], entry_rsi)
    cost = {
        "fees": round(res.fees, 4), "funding": round(res.funding, 4), "slippage": round(res.slippage, 4),
        "fee_bleed_pct": round((res.fees + abs(res.funding) + res.slippage) / position["notional"], 6)
        if position["notional"] else 0.0,
    }
    return {"net_pnl": round(res.net_pnl, 2), "net_pct": round(net_pct, 6),
            "baseline": base, "cost_summary": cost}


def sharp_move(closes, threshold=SHARP_MOVE_PCT):
    """Kapanış serisinde ilk değere göre maksimum |excursion| ≥ threshold mı? (kaçırılan-hareket)."""
    if not closes:
        return {"sharp": False, "max_excursion": 0.0}
    base = closes[0]
    if base == 0:
        return {"sharp": False, "max_excursion": 0.0}
    exc = max(abs(c - base) / base for c in closes)
    return {"sharp": exc >= threshold, "max_excursion": round(exc, 4)}


def is_anchor_clean(context):
    """Karar bağlamı geçmiş-sonuç anahtarlarından temiz mi? (anchor-free — CLAUDE.md kural 8).
    Yasak anahtar bulunursa False → karar reddedilmeli."""
    def scan(obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if any(f in str(k).lower() for f in ANCHOR_FORBIDDEN):
                    return False
                if not scan(v):
                    return False
        elif isinstance(obj, list):
            return all(scan(x) for x in obj)
        return True
    return scan(context)


def build_decision_context(snapshot, lessons=None):
    """LLM'e verilecek varlık-başı bağlam + (opsiyonel) lessons yüzeyi.
    Her varlık: ham sayılar + ön-değerlendirme (gate). 'Uydurma yok': seviyeler snapshot'tan.
    Anchor-free: geçmiş SONUÇ koyulmaz (is_anchor_clean ile doğrulanabilir)."""
    ctx = {"timestamp": snapshot.get("timestamp"), "regime": snapshot.get("regime"), "assets": {}}
    if lessons:
        ctx["lessons"] = lessons  # zamansız disiplin (geçmiş sonuç DEĞİL)
    for coin, a in snapshot["assets"].items():
        passes, side, reason = opportunity_gate(a)
        atr = a["atr"]
        price = a["price"]
        # Referans seviyeler — tek kaynak: reference_levels (1.5×/3.0× ATR)
        ref_stop, ref_target = reference_levels(price, atr, side)
        ctx["assets"][coin] = {
            "price": price, "rsi": a["rsi"], "macd_hist": a["macd_hist"],
            "macd_line": a["macd_line"], "signal_line": a["signal_line"], "atr": atr,
            "funding": a["funding"], "funding_class": rules.classify_funding(a["funding"]),
            "trends": a["trends"], "trigger": a["trigger"],
            "gate": {"opportunity": passes, "side": side, "reason": reason},
            "reference_levels": {"entry": price, "stop": ref_stop, "target": ref_target},
        }
    return ctx
