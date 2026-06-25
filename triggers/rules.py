"""
triggers/rules.py — Kural-bazlı trigger sistemi (RSI/MACD/ATR/funding/trend).
Ne yapar: Bir varlık snapshot'ından geçerli giriş tetikleyici(leri) var mı, hangi yönde, hangi
          uyarılarla — yapısal olarak değerlendirir.
Neden:   capture_snapshot.py yalnız bool `trigger` üretiyordu; deterministic + deep-thinker'ın
         AYNI tetik tanımını paylaşması ve gerekçeyi (neden trigger/neden değil) görebilmesi için
         tek otorite. Demir kurallar (CLAUDE.md) burada makineleşir.
Çıktı:   TriggerResult (dataclass) — saf değerlendirme, I/O yok, karar/sizing yok.
"""

from dataclasses import dataclass, field
from typing import Optional, List

# --- Eşikler (Faz-1 sabit — CLAUDE.md kural 7) ---
RSI_OVERBOUGHT = 70      # >= → aşırı-alım (pro-trend short tetiği için)
RSI_OVERSOLD = 30        # <= → aşırı-satım (pro-trend long tetiği için)
RSI_LATE_LONG = 65       # > → H-03 geç-giriş riski (long'da uyarı)
RSI_LATE_SHORT = 35      # < → simetrik geç-giriş riski (short'ta uyarı)

# Funding sınıflandırma eşikleri (mutlak değer) — deep_scan.py ile uyumlu
FUNDING_EXTREME = 0.0001
FUNDING_HIGH = 0.00005
FUNDING_ELEVATED = 0.00001


@dataclass
class TriggerResult:
    coin: str
    fired: bool                      # geçerli, kurala uygun tetik var mı
    side: Optional[str]              # "buy" | "sell" | None
    reasons: List[str] = field(default_factory=list)   # tetiğin gerekçeleri
    warnings: List[str] = field(default_factory=list)   # H-03 vb. risk uyarıları
    blockers: List[str] = field(default_factory=list)   # demir-kural engelleri (counter-trend, range-HTF)

    def as_dict(self):
        return {
            "coin": self.coin, "fired": self.fired, "side": self.side,
            "reasons": self.reasons, "warnings": self.warnings, "blockers": self.blockers,
        }


def classify_funding(funding):
    """Funding oranını sözel sınıfa çevirir (mutlak büyüklük). deep_scan.py ile aynı eşikler."""
    f = abs(funding)
    if f > FUNDING_EXTREME:
        return "ekstrem"
    if f > FUNDING_HIGH:
        return "yuksek"
    if f > FUNDING_ELEVATED:
        return "normal-yukari"
    return "normal"


def macd_cross(asset):
    """MACD kesişim yönü: 'up' (boğa), 'down' (ayı), None.
    Neden hist + line/signal birlikte: tek başına histogram işareti gürültülü; line>signal teyidi şart."""
    h = asset["macd_hist"]
    line = asset["macd_line"]
    sig = asset["signal_line"]
    if h > 0 and line > sig:
        return "up"
    if h < 0 and line < sig:
        return "down"
    return None


def rsi_extreme(rsi):
    """RSI ekstremi: 'oversold' (<=30), 'overbought' (>=70), None."""
    if rsi <= RSI_OVERSOLD:
        return "oversold"
    if rsi >= RSI_OVERBOUGHT:
        return "overbought"
    return None


def evaluate(asset):
    """Bir varlığı değerlendirip TriggerResult döndürür.

    Tetik tanımı (capture_snapshot.compute_trigger ile aynı çekirdek):
      fired = (RSI ekstrem) AND (MACD cross teyitli)
    Yön ataması demir kurallarla sınırlandırılır:
      - 1d 'range'  → range-HTF blocker (WAIT)
      - 1d 'down'   → yalnız short meşru; long counter-trend blocker
      - 1d 'up'     → yalnız long meşru; short counter-trend blocker
    Uyarılar (engel değil, bilgi): H-03 geç-giriş, ekstrem funding.
    """
    coin = asset["coin"]
    rsi = asset["rsi"]
    trend_1d = asset["trends"]["1d"]
    cross = macd_cross(asset)
    ext = rsi_extreme(rsi)

    res = TriggerResult(coin=coin, fired=False, side=None)

    # --- Çekirdek tetik koşulu ---
    if ext is None or cross is None:
        if ext is None:
            res.reasons.append(f"RSI {rsi} ekstrem değil (>= {RSI_OVERBOUGHT} veya <= {RSI_OVERSOLD} bekleniyor)")
        if cross is None:
            res.reasons.append("MACD cross teyidi yok (hist ile line/signal aynı yönde değil)")
        # tetik yok → side yok; yine de demir-kural bağlamını ekle
        _annotate_context(res, asset, trend_1d)
        return res

    res.reasons.append(f"RSI {ext} ({rsi}) + MACD cross {cross}")

    # --- Yön + demir-kural engelleri ---
    if trend_1d == "range":
        res.blockers.append("range-HTF (1d range) → WAIT")
        _annotate_context(res, asset, trend_1d)
        return res

    if trend_1d == "down":
        # ayı: short pro-trend, long counter-trend (yasak)
        if cross == "up" or ext == "oversold":
            res.blockers.append("counter-trend long (1d down) → YASAK")
            _annotate_context(res, asset, trend_1d)
            return res
        res.fired = True
        res.side = "sell"
        if rsi < RSI_LATE_SHORT:
            res.warnings.append(f"H-03 simetrik: RSI {rsi} < {RSI_LATE_SHORT}, geç short riski")

    elif trend_1d == "up":
        if cross == "down" or ext == "overbought":
            res.blockers.append("counter-trend short (1d up) → YASAK")
            _annotate_context(res, asset, trend_1d)
            return res
        res.fired = True
        res.side = "buy"
        if rsi > RSI_LATE_LONG:
            res.warnings.append(f"H-03: RSI {rsi} > {RSI_LATE_LONG}, geç-giriş (aşırı-uzamış) riski")

    _annotate_context(res, asset, trend_1d)
    return res


def _annotate_context(res, asset, trend_1d):
    """Funding ekstremi gibi engel-olmayan bağlam uyarılarını ekler."""
    fc = classify_funding(asset["funding"])
    if fc in ("ekstrem", "yuksek"):
        res.warnings.append(f"funding {fc} ({asset['funding']:.2e}) — ters funding pozisyonu eritebilir")


def evaluate_all(snapshot):
    """Snapshot'taki tüm varlıklar için {coin: TriggerResult}."""
    return {coin: evaluate(asset) for coin, asset in snapshot["assets"].items()}
