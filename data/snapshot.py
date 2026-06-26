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


def build_coin_snapshot(coin, ctxs):
    """Tek varlık snapshot'ı. ctxs: (universe, asset_ctxs) — funding tek istekten paylaşılır."""
    print(f"  {coin} çekiliyor...")
    candles_1d = ohlcv.fetch_candles(coin, "1d", 100)
    closes_1d = ohlcv.closes(candles_1d)
    highs_1d = ohlcv.highs(candles_1d)
    lows_1d = ohlcv.lows(candles_1d)

    rsi = indicators.compute_rsi(closes_1d)
    macd_hist, macd_line, signal_line = indicators.compute_macd(closes_1d)
    atr = indicators.compute_atr(highs_1d, lows_1d, closes_1d)

    multi = ohlcv.fetch_multi_tf(coin, count=60)
    trends = {tf: indicators.compute_trend(cl) for tf, cl in multi.items()}

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


def main():
    print(f"Snapshot çekiliyor — {datetime.now(timezone.utc).isoformat()}")
    ctxs = funding_mod.fetch_all_ctxs()  # tek istek, tüm varlıklarda paylaşılır
    snapshots = []
    for coin in COINS:
        try:
            snapshots.append(build_coin_snapshot(coin, ctxs))
            time.sleep(0.3)
        except Exception as e:
            print(f"  {coin} HATA: {e}")

    regime = compute_regime(snapshots)
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "regime": regime,
        "assets": {s["coin"]: s for s in snapshots},
    }
    with open(SNAPSHOT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Tamamlandı. Rejim: {regime}")
    for s in snapshots:
        trigger_str = "✅ TRIGGER" if s["trigger"] else "❌"
        print(f"  {s['coin']}: ${s['price']} | RSI {s['rsi']} | MACDh {s['macd_hist']} | 1d:{s['trends']['1d']} | {trigger_str}")


if __name__ == "__main__":
    main()
