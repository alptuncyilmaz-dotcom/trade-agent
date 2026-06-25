"""
execution/decision.py — Karar JSON şeması + validate_decision (demir-kural güvenlik ağı).
Ne yapar: deep-thinker/deterministic'in ürettiği kararları şema ve demir kurallara karşı doğrular;
          ihlal eden kararları gerekçesiyle WAIT'e düşürür.
Neden:   apply_deepthinker.py PARA HAREKET ETTİREN kod (paper de olsa kayıt tutar). LLM ya da
         kural hatası buraya kadar gelmesin diye TEK doğrulama kapısı. run_deepthinker.py'deki
         inline guard burada formelleşti ve tek otorite oldu (CLAUDE.md demir disiplinler).
Çıktı:   Saf doğrulama — I/O yok. (clean_decisions, clean_waits) döndürür.
"""

# Karar dosyası şeması (state/deepthinker_decision.json ile birebir):
#   {
#     "decisions": { "BTC": {side, entry, stop, target, confidence, thesis, detailed_rationale} },
#     "waits":     { "ETH": "kısa neden" }
#   }
DECISION_FIELDS = ("side", "entry", "stop", "target")          # zorunlu sayısal/karar alanları
OPTIONAL_FIELDS = ("confidence", "thesis", "detailed_rationale")
VALID_SIDES = ("buy", "sell")
VALID_CONFIDENCE = ("low", "medium", "high")


def validate_params(params):
    """Tek bir kararın ŞEMA geçerliliği (snapshot'tan bağımsız).
    Döner: (ok: bool, hata: str | None)."""
    if not isinstance(params, dict):
        return False, "karar nesne değil"
    side = params.get("side")
    if side not in VALID_SIDES:
        return False, f"geçersiz side '{side}'"
    try:
        entry = float(params["entry"]); stop = float(params["stop"]); target = float(params["target"])
    except (KeyError, TypeError, ValueError):
        return False, "entry/stop/target eksik veya sayısal değil"
    if min(entry, stop, target) <= 0:
        return False, "seviye <= 0 (uydurma/eksik)"
    # Sıralama: buy → stop < entry < target ; sell(short) → target < entry < stop
    if side == "buy" and not (stop < entry < target):
        return False, "buy sıralama bozuk (stop<entry<target değil)"
    if side == "sell" and not (target < entry < stop):
        return False, "short sıralama bozuk (target<entry<stop değil)"
    conf = params.get("confidence")
    if conf is not None and conf not in VALID_CONFIDENCE:
        return False, f"geçersiz confidence '{conf}'"
    return True, None


def validate_against_snapshot(params, asset):
    """Şemadan geçen kararı DEMİR KURALLARA karşı doğrular (snapshot bağlamı gerekir).
    Döner: (ok: bool, hata: str | None)."""
    trend_1d = asset["trends"]["1d"]
    side = params["side"]
    # Range-HTF → WAIT
    if trend_1d == "range":
        return False, "range-HTF (1d range) → WAIT"
    # Counter-trend açma yasak
    if side == "buy" and asset.get("is_counter_trend_long"):
        return False, "counter-trend long (1d down) → YASAK"
    if side == "sell" and asset.get("is_counter_trend_short"):
        return False, "counter-trend short (1d up) → YASAK"
    # Stop/entry, mevcut fiyatın doğru tarafında mı (uydurma seviye koruması)
    price = asset["price"]
    if side == "buy" and not (params["stop"] < price):
        return False, "buy stop güncel fiyatın üstünde (anlamsız)"
    if side == "sell" and not (params["stop"] > price):
        return False, "short stop güncel fiyatın altında (anlamsız)"
    return True, None


def validate_decision(decision, snapshot):
    """Tüm karar dosyasını doğrular. İhlaller WAIT'e düşürülür (asla sessizce geçmez).
    Döner: (clean_decisions, clean_waits) — apply_* doğrudan bunları kullanabilir."""
    raw_dec = decision.get("decisions", {}) or {}
    waits = dict(decision.get("waits", {}) or {})
    clean = {}

    for coin, params in raw_dec.items():
        asset = snapshot["assets"].get(coin)
        if asset is None:
            waits[coin] = "guard: snapshot'ta yok"
            continue
        ok, err = validate_params(params)
        if not ok:
            waits[coin] = f"guard: {err}"
            continue
        ok, err = validate_against_snapshot(params, asset)
        if not ok:
            waits[coin] = f"guard: {err}"
            continue
        clean[coin] = params

    return clean, waits


def empty_decision():
    """Boş/iskelet karar nesnesi."""
    return {"decisions": {}, "waits": {}}
