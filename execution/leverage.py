"""
execution/leverage.py — Kaldıraç + pozisyon boyutu hesabı (maks 5x, vol-ölçek, güvene bağlı).
Ne yapar: Risk-bazlı notional'ı hesaplar, ardından volatilite ve güven (confidence) ile ölçekler,
          tüm demir tavanlara kırpar.
Neden:   run_deterministic/apply_deepthinker'daki düz compute_sizing yalnız risk+poz tavanı
         uyguluyordu. CLAUDE.md kural 4 (%1.5 risk / %30 poz tavan / %100 teminat-guard / maks 5x)
         tam burada toplanır; deep-thinker'ın 'confidence'ı ve yüksek volatilite kaldıracı KÜÇÜLTÜR.
Çıktı:   Sizing (dataclass) — saf hesap, I/O yok.
"""

from dataclasses import dataclass

# --- Demir tavanlar (CLAUDE.md kural 4 — Faz-1 sabit) ---
RISK_PCT = 0.015        # trade başına maks kayıp: bakiyenin %1.5'i
MAX_POS_PCT = 0.30      # tek pozisyon notional tavanı: bakiyenin %30'u
MAX_LEVERAGE = 5.0      # kaldıraç tavanı
COLLATERAL_GUARD = 1.00 # %100 teminat-guard: kullanılan marj <= bakiye

# Güven çarpanları — düşük güven daha küçük poz açar (over-trading/yanlış-tez maliyetini sınırlar)
CONFIDENCE_MULT = {"low": 0.5, "medium": 0.75, "high": 1.0, None: 0.75}

# Volatilite ölçeği: ATR/fiyat oranı yükseldikçe kaldıraç düşürülür.
# Eşikler oransal ATR'ye göre (örn. %3 ATR = orta-yüksek vol).
VOL_LOW = 0.02          # <= %2 ATR/price → tam ölçek
VOL_HIGH = 0.06         # >= %6 ATR/price → en düşük ölçek


@dataclass
class Sizing:
    notional: float      # USD pozisyon büyüklüğü
    leverage: float      # notional / bakiye, tavanlara kırpılmış
    risk_usd: float      # niyetlenen dolar risk (bakiye * RISK_PCT)
    used_margin: float   # notional / leverage (teminat-guard kontrolü)
    notes: list

    def as_dict(self):
        return {
            "notional": self.notional, "leverage": self.leverage,
            "risk_usd": round(self.risk_usd, 2), "used_margin": round(self.used_margin, 2),
            "notes": self.notes,
        }


def _vol_scale(atr, entry):
    """ATR/price oranını [VOL_HIGH..VOL_LOW] aralığında lineer 1.0→0.4 ölçeğe çevirir.
    Neden: yüksek volatilitede aynı dolar-risk daha büyük fiyat salınımı demek; kaldıracı kısarak
    teminat-guard ihlalini ve gap-stop riskini azaltırız."""
    if entry <= 0:
        return 1.0
    vol = atr / entry
    if vol <= VOL_LOW:
        return 1.0
    if vol >= VOL_HIGH:
        return 0.4
    # lineer interpolasyon: VOL_LOW→1.0, VOL_HIGH→0.4
    frac = (vol - VOL_LOW) / (VOL_HIGH - VOL_LOW)
    return round(1.0 - frac * 0.6, 3)


def compute_sizing(balance, entry, stop, atr=None, confidence="medium"):
    """Risk-bazlı pozisyon boyutu + kaldıraç.

    Adımlar:
      1. risk_usd = balance * RISK_PCT
      2. stop_dist = |entry - stop| / entry  → notional = risk_usd / stop_dist  (risk kuralı)
      3. confidence ve vol-ölçeği uygula (küçültür, asla büyütmez)
      4. MAX_POS_PCT, MAX_LEVERAGE ve %100 teminat-guard ile kırp
    Döner: Sizing. notional 0 ise pozisyon açılamaz (geçersiz stop)."""
    notes = []
    stop_dist = abs(entry - stop) / entry if entry else 0
    if stop_dist == 0:
        return Sizing(0.0, 0.0, balance * RISK_PCT, 0.0, ["geçersiz stop mesafesi (0) → açılamaz"])

    risk_usd = balance * RISK_PCT
    notional = risk_usd / stop_dist

    # Güven ölçeği
    cmult = CONFIDENCE_MULT.get(confidence, 0.75)
    if cmult != 1.0:
        notes.append(f"confidence={confidence} × {cmult}")
    notional *= cmult

    # Volatilite ölçeği
    if atr is not None:
        vscale = _vol_scale(atr, entry)
        if vscale < 1.0:
            notes.append(f"vol-ölçek × {vscale} (ATR/price={round(atr/entry,4)})")
        notional *= vscale

    # Poz tavanı
    cap = balance * MAX_POS_PCT
    if notional > cap:
        notes.append(f"poz tavanı %{int(MAX_POS_PCT*100)} kırpıldı")
        notional = cap

    # leverage = maruziyet oranı (notional/balance) — run_deterministic ile aynı konvansiyon.
    # <1 olabilir (kaldıraçsız, notional bakiyenin altında); MAX_LEVERAGE'a kırpılır.
    leverage = notional / balance if balance else 0
    if leverage > MAX_LEVERAGE:
        notes.append(f"kaldıraç {MAX_LEVERAGE}x tavanına kırpıldı")
        leverage = MAX_LEVERAGE
        notional = balance * MAX_LEVERAGE

    # Kullanılan marj: kaldıraçsızken (notional<=bakiye) notional kadar; kaldıraçlıyken bakiyeyi
    # aşamaz. Efektif kaldıraç max(1, oran) → marj = notional/efektif = min(notional, balance).
    # %100 teminat-guard (CLAUDE.md kural 4) bu yapıyla daima sağlanır.
    used_margin = min(notional, balance * COLLATERAL_GUARD)

    return Sizing(
        notional=round(notional, 2),
        leverage=round(leverage, 2),
        risk_usd=risk_usd,
        used_margin=round(used_margin, 2),
        notes=notes,
    )
