"""
data/ohlcv.py — Hyperliquid mum (OHLCV) verisi çekme katmanı.
Ne yapar: Bir varlık+interval için candleSnapshot çeker, kapanış/yüksek/düşük serilerine ayırır.
Neden:   capture_snapshot.py içindeki inline fetch buraya taşındı — veri çekme tek katmanda toplandı,
         features/indicators saf hesap olarak kalsın. OKUMA mainnet (CLAUDE.md kural 2).
Çıktı:   Saf veri — gösterge/karar yok.
"""

import time
import requests

BASE_URL = "https://api.hyperliquid.xyz/info"
INTERVALS = ["15m", "1h", "4h", "1d"]
INTERVAL_MS = {"15m": 900000, "1h": 3600000, "4h": 14400000, "1d": 86400000}
CANDLE_COUNT = 100


def fetch_candles(coin, interval, count=CANDLE_COUNT):
    """Hyperliquid'den ham mum listesi (her mum: o/h/l/c/v/t dict). count mum geriye gider."""
    now = int(time.time() * 1000)
    start = now - INTERVAL_MS[interval] * count
    payload = {"type": "candleSnapshot",
               "req": {"coin": coin, "interval": interval, "startTime": start, "endTime": now}}
    r = requests.post(BASE_URL, json=payload, timeout=10)
    r.raise_for_status()
    return r.json()


def closes(candles):
    """Kapanış serisi (float)."""
    return [float(c["c"]) for c in candles]


def highs(candles):
    return [float(c["h"]) for c in candles]


def lows(candles):
    return [float(c["l"]) for c in candles]


def fetch_multi_tf(coin, intervals=INTERVALS, count=60, pause=0.2):
    """Birden çok TF için kapanış serileri: {interval: [closes]}. Trend hesabı için kullanılır.
    pause: Hyperliquid'e nazik olmak için TF'ler arası kısa bekleme."""
    out = {}
    for interval in intervals:
        out[interval] = closes(fetch_candles(coin, interval, count))
        time.sleep(pause)
    return out
