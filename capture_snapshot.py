"""
capture_snapshot.py — Hyperliquid'den 4 varlık snapshot çeker.
Ne yapar: BTC/ETH/XRP/HYPE için fiyat, RSI, MACD, ATR, funding, çok-TF trend hesaplar.
Neden: deep-thinker ve deterministic-trader için ortak point-in-time veri üretir.
Çıktı: state/snapshot_latest.json
"""

import json
import time
import requests
from datetime import datetime, timezone

from features import indicators
from triggers import rules

COINS = ["BTC", "ETH", "XRP", "HYPE"]
BASE_URL = "https://api.hyperliquid.xyz/info"
INTERVALS = ["15m", "1h", "4h", "1d"]
CANDLE_COUNT = 100

def fetch_candles(coin, interval, count=CANDLE_COUNT):
    now = int(time.time() * 1000)
    interval_ms = {"15m": 900000, "1h": 3600000, "4h": 14400000, "1d": 86400000}
    start = now - interval_ms[interval] * count
    payload = {"type": "candleSnapshot", "req": {"coin": coin, "interval": interval, "startTime": start, "endTime": now}}
    r = requests.post(BASE_URL, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_funding(coin):
    payload = {"type": "metaAndAssetCtxs"}
    r = requests.post(BASE_URL, json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()
    universe = data[0]["universe"]
    ctxs = data[1]
    for i, u in enumerate(universe):
        if u["name"] == coin:
            ctx = ctxs[i]
            return {
                "funding": float(ctx.get("funding", 0)),
                "openInterest": float(ctx.get("openInterest", 0)),
                "markPx": float(ctx.get("markPx", 0)),
                "oraclePx": float(ctx.get("oraclePx", 0)),
            }
    return {"funding": 0, "openInterest": 0, "markPx": 0, "oraclePx": 0}

def build_coin_snapshot(coin):
    # Gösterge hesapları tek kaynaktan: features/indicators. Tetik bool'u: triggers/rules.core_trigger.
    print(f"  {coin} çekiliyor...")
    candles_1d = fetch_candles(coin, "1d", 100)
    closes_1d = [float(c["c"]) for c in candles_1d]
    highs_1d = [float(c["h"]) for c in candles_1d]
    lows_1d = [float(c["l"]) for c in candles_1d]

    rsi = indicators.compute_rsi(closes_1d)
    macd_hist, macd_line, signal_line = indicators.compute_macd(closes_1d)
    atr = indicators.compute_atr(highs_1d, lows_1d, closes_1d)

    trends = {}
    for interval in INTERVALS:
        c = fetch_candles(coin, interval, 60)
        cl = [float(x["c"]) for x in c]
        trends[interval] = indicators.compute_trend(cl)
        time.sleep(0.2)

    funding_data = fetch_funding(coin)
    price = closes_1d[-1]

    trigger = rules.core_trigger(rsi, macd_hist, macd_line, signal_line)

    trend_1d = trends["1d"]
    is_counter_trend_long = trend_1d == "down"
    is_counter_trend_short = trend_1d == "up"

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
        "is_counter_trend_long": is_counter_trend_long,
        "is_counter_trend_short": is_counter_trend_short,
    }

def compute_regime(snapshots):
    counts = {"up": 0, "down": 0, "range": 0}
    for s in snapshots:
        counts[s["trends"]["1d"]] += 1
    dominant = max(counts, key=counts.get)
    if counts["up"] >= 3:
        return "bull"
    elif counts["down"] >= 3:
        return "bear"
    return "mixed"

def main():
    print(f"Snapshot çekiliyor — {datetime.now(timezone.utc).isoformat()}")
    snapshots = []
    for coin in COINS:
        try:
            s = build_coin_snapshot(coin)
            snapshots.append(s)
            time.sleep(0.3)
        except Exception as e:
            print(f"  {coin} HATA: {e}")

    regime = compute_regime(snapshots)
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "regime": regime,
        "assets": {s["coin"]: s for s in snapshots}
    }

    with open("state/snapshot_latest.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Tamamlandı. Rejim: {regime}")
    for s in snapshots:
        trigger_str = "✅ TRIGGER" if s["trigger"] else "❌"
        print(f"  {s['coin']}: ${s['price']} | RSI {s['rsi']} | MACDh {s['macd_hist']} | 1d:{s['trends']['1d']} | {trigger_str}")

if __name__ == "__main__":
    main()
