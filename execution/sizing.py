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
RISK_PCT = 0.015        # trade başına maks kayıp: bakiyenin %1.5'i
MAX_POS_PCT = 0.30      # tek pozisyon notional tavanı: bakiyenin %30'u
COLLATERAL_GUARD = 1.00 # %100 teminat-guard: kullanılan marj <= bakiye


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


def compute_sizing(balance, entry, stop):
    """Risk-bazlı notional. notional = (bakiye*%1.5) / stop_mesafe_oranı, %30'a kırpılır.
    Stop mesafesi 0 ise pozisyon açılamaz (notional 0). İKİ KOL DA AYNEN bunu kullanır."""
    notes = []
    if not entry:
        return Sizing(0.0, balance * RISK_PCT, 0.0, 0.0, ["geçersiz entry"])
    stop_dist = abs(entry - stop) / entry
    if stop_dist == 0:
        return Sizing(0.0, balance * RISK_PCT, 0.0, 0.0, ["geçersiz stop mesafesi (0)"])

    risk_usd = balance * RISK_PCT
    notional = risk_usd / stop_dist

    cap = balance * MAX_POS_PCT
    if notional > cap:
        notes.append(f"poz tavanı %{int(MAX_POS_PCT*100)} kırpıldı")
        notional = cap

    used_margin = min(notional, balance * COLLATERAL_GUARD)
    exposure = notional / balance if balance else 0.0
    return Sizing(round(notional, 2), risk_usd, round(used_margin, 2), exposure, notes)
