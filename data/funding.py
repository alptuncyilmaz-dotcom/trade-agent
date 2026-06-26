"""
data/funding.py — Hyperliquid funding / open interest / mark-oracle fiyat katmanı.
Ne yapar: metaAndAssetCtxs'ten bir varlığın funding oranı, açık pozisyon (OI), mark & oracle fiyatını çeker.
Neden:   Funding (F-02) ve OI (F-01) Faz-2 aday faktörleri (strategy/candidate-factors.md). Veri çekme
         tek katmanda olsun diye capture_snapshot'tan ayrıldı. Funding YORUMU triggers/rules'ta.
Çıktı:   Saf veri.
"""

import requests

from data.ohlcv import BASE_URL


def fetch_all_ctxs():
    """Tüm evren için (universe, ctxs) döndürür — tek istek. Çok varlık çekerken verimli."""
    r = requests.post(BASE_URL, json={"type": "metaAndAssetCtxs"}, timeout=10)
    r.raise_for_status()
    data = r.json()
    return data[0]["universe"], data[1]


def fetch_funding(coin, ctxs=None):
    """Bir varlığın funding/OI/mark/oracle değerleri. ctxs verilirse tekrar istek atmaz (verimli).
    Bulunamazsa sıfırlanmış sözlük döner (uydurma yok — CLAUDE.md kural 6)."""
    if ctxs is None:
        universe, ctxs = fetch_all_ctxs()
    else:
        universe, ctxs = ctxs
    for i, u in enumerate(universe):
        if u["name"] == coin:
            c = ctxs[i]
            return {
                "funding": float(c.get("funding", 0)),
                "openInterest": float(c.get("openInterest", 0)),
                "markPx": float(c.get("markPx", 0)),
                "oraclePx": float(c.get("oraclePx", 0)),
            }
    return {"funding": 0, "openInterest": 0, "markPx": 0, "oraclePx": 0}
