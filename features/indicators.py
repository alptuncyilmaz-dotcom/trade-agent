"""
features/indicators.py — Saf teknik gösterge hesapları (RSI/MACD/ATR/SMA/EMA/trend).
Ne yapar: Kapanış/yüksek/düşük serilerinden tek-tip gösterge değerleri üretir.
Neden: capture_snapshot.py içindeki inline hesaplar burada toplandı; tüm kollar (deterministic,
       deep-thinker, simulator, backtest) AYNI matematiği kullansın diye tek kaynak. Değerler
       capture_snapshot.py ile birebir aynı kalacak şekilde yazıldı (snapshot ile tutarlılık şart).
Not:   Hiçbir karar vermez, hiçbir I/O yapmaz — sadece sayı→sayı. Karar triggers/ ve execution/'da.
"""

import numpy as np


def ema(values, period):
    """Üstel hareketli ortalama. İlk değeri seed alır (capture_snapshot ile aynı davranış).
    Neden seed=ilk değer: kısa serilerde (100 mum) klasik SMA-seed ile fark ihmal edilebilir
    ve mevcut snapshot üretimiyle uyum korunur."""
    arr = np.asarray(values, dtype=float)
    if len(arr) == 0:
        return arr
    out = np.zeros_like(arr)
    out[0] = arr[0]
    k = 2 / (period + 1)
    for i in range(1, len(arr)):
        out[i] = arr[i] * k + out[i - 1] * (1 - k)
    return out


def sma(values, period):
    """Basit hareketli ortalama (son `period` bar). Yetersiz veri varsa mevcut tümünün ortalaması."""
    arr = np.asarray(values, dtype=float)
    if len(arr) == 0:
        return float("nan")
    return float(np.mean(arr[-period:]))


def compute_rsi(closes, period=14):
    """Wilder olmayan, basit ortalamalı RSI (capture_snapshot ile aynı).
    avg_loss=0 ise 100 döner (bölme-sıfır koruması). Neden basit ortalama: snapshot ile birebir
    uyum + Faz-1'de gösterge sabit (CLAUDE.md kural 7: faz içinde yeni faktör/yöntem eklenmez)."""
    arr = np.asarray(closes, dtype=float)
    if len(arr) < period + 1:
        return 50.0  # yetersiz veri → nötr
    deltas = np.diff(arr)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def compute_macd(closes, fast=12, slow=26, signal=9):
    """MACD → (hist, macd_line, signal_line). Histogram = macd_line - signal_line.
    Neden hist ayrı döner: trigger sistemi cross yönünü hist işaretinden okur (triggers/rules.py)."""
    arr = np.asarray(closes, dtype=float)
    ema_fast = ema(arr, fast)
    ema_slow = ema(arr, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return round(float(hist[-1]), 4), round(float(macd_line[-1]), 4), round(float(signal_line[-1]), 4)


def compute_atr(highs, lows, closes, period=14):
    """Average True Range — volatilite ölçüsü. True Range = max(H-L, |H-Cprev|, |L-Cprev|).
    Neden ATR: stop/target mesafesi (1.5×/3.0×ATR) ve leverage vol-ölçeği bundan türer."""
    highs = np.asarray(highs, dtype=float)
    lows = np.asarray(lows, dtype=float)
    closes = np.asarray(closes, dtype=float)
    trs = []
    for i in range(1, len(closes)):
        tr = max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
        trs.append(tr)
    if not trs:
        return 0.0
    return round(float(np.mean(trs[-period:])), 4)


def compute_trend(closes):
    """Tek-TF trend etiketi: up / down / range (SMA20 vs SMA50 + fiyat konumu).
    Neden 3 durum: 'range' demir kuralda WAIT'i tetikler (range-HTF → WAIT)."""
    arr = np.asarray(closes, dtype=float)
    if len(arr) < 20:
        return "range"  # yetersiz veri → yön iddiası yok
    s20 = np.mean(arr[-20:])
    s50 = np.mean(arr[-50:]) if len(arr) >= 50 else s20
    price = arr[-1]
    if price > s20 and s20 > s50:
        return "up"
    if price < s20 and s20 < s50:
        return "down"
    return "range"


def realized_vol(closes, period=14):
    """Getiri std'si (volatilite proxy) — leverage vol-ölçeği için alternatif/teyit ölçü.
    Neden ATR yanında: ATR fiyat-birimli, realized_vol oransız; ikisi birlikte aşırı-kaldıraç guard'ı sağlar."""
    arr = np.asarray(closes, dtype=float)
    if len(arr) < 2:
        return 0.0
    rets = np.diff(arr) / arr[:-1]
    return round(float(np.std(rets[-period:])), 6)
