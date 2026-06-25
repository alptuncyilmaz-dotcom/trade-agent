"""
capture_snapshot.py — Hyperliquid'den 4 varlık snapshot çeker.
Ne yapar: BTC/ETH/XRP/HYPE için fiyat, RSI, MACD, ATR, funding, çok-TF trend hesaplar.
Neden: deep-thinker ve deterministic-trader için ortak point-in-time veri üretir.
Çıktı: state/snapshot_latest.json
"""

import json
import time
import requests
import numpy as np
from datetime import datetime, timezone

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

def compute_rsi(closes, period=14):
    closes = np.array(closes, dtype=float)
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)

def compute_macd(closes, fast=12, slow=26, signal=9):
    closes = np.array(closes, dtype=float)
    def ema(arr, n):
        result = np.zeros_like(arr)
        result[0] = arr[0]
        k = 2 / (n + 1)
        for i in range(1, len(arr)):
            result[i] = arr[i] * k + result[i-1] * (1 - k)
        return result
    ema_fast = ema(closes, fast)
    ema_slow = ema(closes, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return round(float(hist[-1]), 4), round(float(macd_line[-1]), 4), round(float(signal_line[-1]), 4)

def compute_atr(highs, lows, closes, period=14):
    trs = []
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1]))
        trs.append(tr)
    return round(float(np.mean(trs[-period:])), 4)

def compute_trend(closes):
    if len(closes) < 20:
        return "range"
    sma20 = np.mean(closes[-20:])
    sma50 = np.mean(closes[-50:]) if len(closes) >= 50 else sma20
    price = closes[-1]
    if price > sma20 and sma20 > sma50:
        return "up"
    elif price < sma20 and sma20 < sma50:
        return "down"
    return "range"

def compute_trigger(rsi, macd_hist, macd_line, signal_line):
    rsi_ob = rsi >= 70
    rsi_os = rsi <= 30
    macd_cross_up = macd_hist > 0 and macd_line > signal_line
    macd_cross_dn = macd_hist < 0 and macd_line < signal_line
    if (rsi_ob or rsi_os) and (macd_cross_up or macd_cross_dn):
        return True
    return False

def build_coin_snapshot(coin):
    print(f"  {coin} çekiliyor...")
    candles_1d = fetch_candles(coin, "1d", 100)
    closes_1d = [float(c["c"]) for c in candles_1d]
    highs_1d = [float(c["h"]) for c in candles_1d]
    lows_1d = [float(c["l"]) for c in candles_1d]

    rsi = compute_rsi(closes_1d)
    macd_hist, macd_line, signal_line = compute_macd(closes_1d)
    atr = compute_atr(highs_1d, lows_1d, closes_1d)

    trends = {}
    for interval in INTERVALS:
        c = fetch_candles(coin, interval, 60)
        cl = [float(x["c"]) for x in c]
        trends[interval] = compute_trend(cl)
        time.sleep(0.2)

    funding_data = fetch_funding(coin)
    price = closes_1d[-1]

    trigger = compute_trigger(rsi, macd_hist, macd_line, signal_line)

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
