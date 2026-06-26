"""
data/snapshot.py — Point-in-time snapshot kurucu (A/B'nin ortak girdisi).
Ne yapar: 4 varlık için ohlcv+funding+onchain çeker, features/indicators ile gösterge, triggers/rules
          ile tetik bool'u hesaplar; rejimi bulur; state/snapshot_latest.json'a yazar.
Neden:   deterministik ve deep-thinker kolları AYNI snapshot'tan beslenir (CLAUDE.md). Veri çekme
         (data/*) ile hesap (features/triggers) ayrı; bu modül yalnız birleştirir. capture_snapshot.py
         ince giriş olarak buna delege eder.
Çıktı:   state/snapshot_latest.json
"""

import json
import time
from datetime import datetime, timezone

from data import ohlcv, funding as funding_mod, onchain
from features import indicators
from triggers import rules

COINS = ["BTC", "ETH", "XRP", "HYPE"]
SNAPSHOT_PATH = "state/snapshot_latest.json"


def _pit(candles, as_of):
    """Point-in-time filtre: as_of (ms) verilirse, o ana kadar AÇILMIŞ mumları tut (look-ahead yok).
    as_of None ise tümü (canlı)."""
    if as_of is None:
        return candles
    return [c for c in candles if float(c.get("t", 0)) <= as_of]


def build_coin_snapshot(coin, ctxs, as_of=None):
    """Tek varlık snapshot'ı. ctxs: (universe, asset_ctxs) — funding tek istekten paylaşılır.
    as_of (ms): point-in-time — o andan SONRAKİ mumlar dışlanır (CLAUDE.md kural 3, look-ahead yok)."""
    print(f"  {coin} çekiliyor...")
    candles_1d = _pit(ohlcv.fetch_candles(coin, "1d", 100), as_of)
    closes_1d = ohlcv.closes(candles_1d)
    highs_1d = ohlcv.highs(candles_1d)
    lows_1d = ohlcv.lows(candles_1d)

    rsi = indicators.compute_rsi(closes_1d)
    macd_hist, macd_line, signal_line = indicators.compute_macd(closes_1d)
    atr = indicators.compute_atr(highs_1d, lows_1d, closes_1d)

    # Çok-TF trend: as_of varsa ham mumları çekip filtrele (look-ahead yok); yoksa hızlı yol.
    trends = {}
    for tf in ohlcv.INTERVALS:
        cl = ohlcv.closes(_pit(ohlcv.fetch_candles(coin, tf, 60), as_of))
        trends[tf] = indicators.compute_trend(cl)
        time.sleep(0.2)

    funding_data = funding_mod.fetch_funding(coin, ctxs=ctxs)
    price = closes_1d[-1]
    trigger = rules.core_trigger(rsi, macd_hist, macd_line, signal_line)
    trend_1d = trends["1d"]

    return {
        "coin": coin,
        "price": round(price, 4),
        "rsi": rsi,
        "macd_hist": macd_hist,
        "macd_line": macd_line,
        "signal_line": signal_line,
        "atr": atr,
        "funding": funding_data["funding"],
        "openInterest": funding_data["openInterest"],
        "markPx": funding_data["markPx"],
        "oraclePx": funding_data["oraclePx"],
        "trends": trends,
        "trigger": trigger,
        "is_counter_trend_long": trend_1d == "down",
        "is_counter_trend_short": trend_1d == "up",
        "onchain": onchain.positioning_proxy(funding_data),  # bağlam (Faz-1'de karara girmez)
    }


def compute_regime(snapshots):
    """1d trend çoğunluğuna göre rejim: 3+ down → bear, 3+ up → bull, aksi → mixed."""
    counts = {"up": 0, "down": 0, "range": 0}
    for s in snapshots:
        counts[s["trends"]["1d"]] += 1
    if counts["up"] >= 3:
        return "bull"
    if counts["down"] >= 3:
        return "bear"
    return "mixed"


def build_snapshot(as_of=None):
    """Tüm varlıklar için snapshot dict döndürür (dosyaya YAZMAZ). as_of (ms) = point-in-time.
    Canlı kullanım: as_of=None. Backtest/debug: as_of geçilir (CLAUDE.md kural 3 — geçmiş yalnız plumbing)."""
    ctxs = funding_mod.fetch_all_ctxs()  # tek istek, tüm varlıklarda paylaşılır
    snapshots = []
    for coin in COINS:
        try:
            snapshots.append(build_coin_snapshot(coin, ctxs, as_of=as_of))
            time.sleep(0.3)
        except Exception as e:
            print(f"  {coin} HATA: {e}")
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "as_of": as_of,
        "regime": compute_regime(snapshots),
        "assets": {s["coin"]: s for s in snapshots},
    }


def main():
    print(f"Snapshot çekiliyor — {datetime.now(timezone.utc).isoformat()}")
    result = build_snapshot(as_of=None)
    regime = result["regime"]
    snapshots = list(result["assets"].values())
    with open(SNAPSHOT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Tamamlandı. Rejim: {regime}")
    for s in snapshots:
        trigger_str = "✅ TRIGGER" if s["trigger"] else "❌"
        print(f"  {s['coin']}: ${s['price']} | RSI {s['rsi']} | MACDh {s['macd_hist']} | 1d:{s['trends']['1d']} | {trigger_str}")


if __name__ == "__main__":
    main()
