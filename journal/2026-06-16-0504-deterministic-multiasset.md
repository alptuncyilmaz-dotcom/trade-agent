# Otonom Tur (deterministic-trader) — 2026-06-16 05:04:37 UTC

> A/B agent: **deterministic-trader** · **TESTNET/PAPER · GERÇEK PARA YOK** · risk-bazlı sizing (%1.5/%30/%100-guard).

## PİYASA REJİMİ: **MIXED** (günlük) — {'up': 1, 'down': 2, 'range': 1}

| Varlık | Fiyat | 1d-trend | counter-trend (long) | trigger | Karar |
|---|---|---|---|---|---|
| BTC | $65927.0 | down | ⚠️ EVET | ❌ | **WAIT** |
| ETH | $1763.1 | down | ⚠️ EVET | ❌ | **WAIT** |
| XRP | $1.2254 | range | hayır | ❌ | **WAIT** |
| HYPE | $71.083 | up | hayır | ✅ | **AÇILDI** |

## Karar (detaylı)
- **Karar zamanı:** 2026-06-16 05:04:37 UTC.
- **forward-test sayacı:** 0.
- KAPANDI HYPE target_hit net 3.5794% (fee $0.92) · baseline edge: False · etiket YOK (L-02)
- AÇILDI HYPE buy entry 71.083 / stop 69.29 / target 74.02 · 1.0x · notional $1229.0843 · LONG: RSI 74.8, MACD_hist +0.15, ATR 1.12; çok-TF 15m:up / 1h:up / 4h:up / 1d:up (HTF buy ile uyumlu, counter-trend değil); kaldıraç 1.0x (1.0x — vol_frac=0.0158 (ters-ölçek 0.8), güven=medium (tavan 2.0x), challenger=temiz, likidasyon 0 stop 69'ın ötesinde); boyut: notional $1229.0843 / margin $1229.0843 (risk $61.4542=%1.5 balance, sınır: poz-tavanı(%30)).
- WAIT BTC: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- WAIT ETH: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- AÇIK XRP: anlık $1.2254 · K/Z $-12.53 (-1.03%)
- AÇIK HYPE: anlık $71.083 · K/Z +$0.0 (+0.0%)

*Determinism kodda; ikisi de AYNI sizing/risk (adil A/B); deep-thinker turlar arası öğrenmez; emir testnet/paper, gerçek para YOK.*
