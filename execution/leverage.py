"""
execution/leverage.py — Kaldıraç ÖNERİSİ (kod-sınırlı, L-04). Boyuttan (sizing.py) AYRI.
Ne yapar: suggest_leverage — vol-ölçek (ATR ters) + güvene bağlı + likidasyon kapısı + 5x sert tavan.
Neden:   CLAUDE.md kural 1: kaldıraç SERBEST değil, KODDAN. Ajan yalnız bu sınır içinde seçer.
         Kaldıraç notional'ı (PnL'i) değiştirmez — marj kilidini ve likidasyon mesafesini belirler.
         Likidasyon kapısı: seçilen kaldıraçta likidasyon fiyatı stop'tan UZAKTA olmalı (yoksa stop anlamsız).
Çıktı:   LeverageSuggestion (dataclass) — saf hesap, I/O yok.
"""

from dataclasses import dataclass

MAX_LEVERAGE = 5.0          # SERT TAVAN (ajan aşamaz, kod reddeder)
LIQ_SAFETY = 0.80           # likidasyon mesafesi stop mesafesinin en az 1/0.80=1.25 katı olmalı

# Güven tavanları (CLAUDE.md): low→~1x, medium→≤2x, high→≤5x (ama vol+likidasyon+challenger şartlı)
CONFIDENCE_CAP = {"low": 1.0, "medium": 2.0, "high": MAX_LEVERAGE, None: 2.0}

# Vol-ölçek: ATR/price oranı yükseldikçe kaldıraç düşer.
VOL_LOW = 0.02              # <= %2 ATR/price → tam izinli
VOL_HIGH = 0.06             # >= %6 ATR/price → düşük


@dataclass
class LeverageSuggestion:
    leverage: float
    caps: dict               # her kapının verdiği üst sınır (şeffaflık)
    notes: list

    def as_dict(self):
        return {"leverage": self.leverage, "caps": self.caps, "notes": self.notes}


def _vol_cap(atr, price):
    """ATR/price → izinli üst kaldıraç (VOL_LOW'da MAX, VOL_HIGH'da ~1x)."""
    if price <= 0:
        return MAX_LEVERAGE
    vol = atr / price
    if vol <= VOL_LOW:
        return MAX_LEVERAGE
    if vol >= VOL_HIGH:
        return 1.0
    frac = (vol - VOL_LOW) / (VOL_HIGH - VOL_LOW)
    return round(MAX_LEVERAGE - frac * (MAX_LEVERAGE - 1.0), 2)


def _liq_cap(entry, stop, side):
    """Likidasyon kapısı: lev arttıkça likidasyon entry'ye yaklaşır (liq_dist≈entry/lev).
    Likidasyon mesafesi stop mesafesinden büyük olmalı → lev < entry/stop_dist (güvenlik payıyla)."""
    stop_dist = abs(entry - stop)
    if stop_dist == 0:
        return 1.0
    raw = entry / stop_dist          # liq_dist > stop_dist ⇒ lev < entry/stop_dist
    return max(1.0, round(raw * LIQ_SAFETY, 2))


def liquidation_price(entry, side, leverage):
    """Yaklaşık izole-marj likidasyon fiyatı (bakım marjı/fee ihmal — muhafazakâr proxy)."""
    if leverage <= 0:
        return None
    if side == "buy":
        return round(entry * (1 - 1 / leverage), 4)
    return round(entry * (1 + 1 / leverage), 4)


def suggest_leverage(entry, stop, side, atr, price, confidence="medium", challenger_clean=True):
    """Kod-türetilmiş kaldıraç önerisi. Tüm kapıların MİNİMUMU, 5x tavanına kırpılır.
    high güven ANCAK düşük-vol + temiz challenger ile tam açılır; low daima ~1x."""
    notes = []
    conf_cap = CONFIDENCE_CAP.get(confidence, 2.0)
    vol_cap = _vol_cap(atr, price)
    liq_cap = _liq_cap(entry, stop, side)

    lev = min(conf_cap, vol_cap, liq_cap, MAX_LEVERAGE)

    # high güven temiz-challenger değilse medium gibi davranır (gürültüye yüksek kaldıraç verme)
    if confidence == "high" and not challenger_clean:
        lev = min(lev, CONFIDENCE_CAP["medium"])
        notes.append("high ama challenger temiz değil → medium tavanı")

    lev = max(1.0, round(lev, 2))
    caps = {"confidence": conf_cap, "vol": vol_cap, "liquidation": liq_cap, "hard": MAX_LEVERAGE}
    if lev == liq_cap:
        notes.append("likidasyon kapısı bağladı (liq mesafesi > stop)")
    if lev == vol_cap and vol_cap < conf_cap:
        notes.append(f"vol-ölçek bağladı (ATR/price={round(atr/price,4) if price else 0})")
    return LeverageSuggestion(lev, caps, notes)
