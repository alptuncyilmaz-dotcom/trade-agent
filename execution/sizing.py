"""
execution/sizing.py — Risk-bazlı pozisyon BOYUTU (notional). Kaldıraçtan AYRI.
Ne yapar: %1.5 risk / stop-mesafe → notional; %30 poz tavanı; %100 teminat-guard.
Neden:   CLAUDE.md A/B kuralı — iki kol da AYNI sizing kullanır (tek fark karar mekanizması).
         Boyut (kaç $ notional) risk'ten gelir; KALDIRAÇ ayrı bir endişe (`leverage.py`) ve PnL'i
         değiştirmez (notional-bazlı). Bu ayrım Can'ın mimarisiyle hizalı (sizing.py ⊥ leverage.py).
Çıktı:   Sizing (dataclass) — saf hesap, I/O yok. PnL yalnız notional × fiyat-hareketinden gelir.
"""

from dataclasses import dataclass

# --- Demir sizing tavanları (CLAUDE.md — Faz-1 sabit) ---
RISK_PCT = 0.015        # deterministic/deep-thinker: trade başına maks kayıp %1.5
MAX_POS_PCT = 0.30      # deterministic/deep-thinker: tek pozisyon notional tavanı %30
COLLATERAL_GUARD = 1.00 # %100 teminat-guard: kullanılan marj <= bakiye
# C kolu (aggressive-trader) profili — daha yüksek risk/maruziyet:
RISK_PCT_AGGRESSIVE = 0.05      # %5 risk
MAX_POS_PCT_AGGRESSIVE = 1.00   # tek poz tavanı %100 (kaldıraç likidasyon kapısıyla sınırlı)


@dataclass
class Sizing:
    notional: float      # USD pozisyon büyüklüğü (PnL bundan gelir)
    risk_usd: float      # niyetlenen dolar risk (bakiye * RISK_PCT)
    used_margin: float   # min(notional, bakiye) — teminat-guard
    exposure: float      # notional / bakiye (maruziyet oranı)
    notes: list

    def as_dict(self):
        return {"notional": self.notional, "risk_usd": round(self.risk_usd, 2),
                "used_margin": round(self.used_margin, 2), "exposure": round(self.exposure, 3),
                "notes": self.notes}


def compute_sizing(balance, entry, stop, risk_pct=RISK_PCT, max_pos_pct=MAX_POS_PCT):
    """Risk-bazlı notional. notional = (bakiye*risk_pct) / stop_mesafe_oranı, max_pos_pct'e kırpılır.
    Default = deterministic/deep-thinker (%1.5 / %30 — ORTAK sizing). aggressive: %5 / %100."""
    notes = []
    if not entry:
        return Sizing(0.0, balance * risk_pct, 0.0, 0.0, ["geçersiz entry"])
    stop_dist = abs(entry - stop) / entry
    if stop_dist == 0:
        return Sizing(0.0, balance * risk_pct, 0.0, 0.0, ["geçersiz stop mesafesi (0)"])

    risk_usd = balance * risk_pct
    notional = risk_usd / stop_dist

    cap = balance * max_pos_pct
    if notional > cap:
        notes.append(f"poz tavanı %{int(max_pos_pct*100)} kırpıldı")
        notional = cap

    used_margin = min(notional, balance * COLLATERAL_GUARD)
    exposure = notional / balance if balance else 0.0
    return Sizing(round(notional, 2), risk_usd, round(used_margin, 2), exposure, notes)
