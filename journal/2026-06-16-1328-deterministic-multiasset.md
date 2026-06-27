# Otonom Tur (deterministic-trader) — 2026-06-16 13:28:27 UTC

> A/B agent: **deterministic-trader** · **TESTNET/PAPER · GERÇEK PARA YOK** · risk-bazlı sizing (%1.5/%30/%100-guard).

## PİYASA REJİMİ: **MIXED** (günlük) — {'up': 1, 'down': 1, 'range': 2}

| Varlık | Fiyat | 1d-trend | counter-trend (long) | trigger | Karar |
|---|---|---|---|---|---|
| BTC | $66040.0 | down | ⚠️ EVET | ❌ | **WAIT** |
| ETH | $1802.3 | range | hayır | ❌ | **WAIT** |
| XRP | $1.23 | range | hayır | ❌ | **WAIT** |
| HYPE | $75.544 | up | hayır | ✅ | **AÇILDI** |

## Karar (detaylı)
- **Karar zamanı:** 2026-06-16 13:28:27 UTC.
- **forward-test sayacı:** 2.
- KAPANDI HYPE target_hit net 3.98% (fee $1.14) · baseline edge: True · etiket YOK (L-02)
- AÇILDI HYPE buy entry 75.544 / stop 73.24 / target 79.31 · 1.0x · notional $1258.6627 · LONG: RSI 74.3, MACD_hist +0.48, ATR 1.44; çok-TF 15m:up / 1h:up / 4h:up / 1d:up (HTF buy ile uyumlu, counter-trend değil); kaldıraç 1.0x (1.0x — vol_frac=0.0190 (ters-ölçek 0.6), güven=medium (tavan 2.0x), challenger=temiz, likidasyon 0 stop 73'ın ötesinde); boyut: notional $1258.6627 / margin $1258.6627 (risk $62.9331=%1.5 balance, sınır: poz-tavanı(%30)).
- WAIT BTC: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- WAIT ETH: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- AÇIK XRP: anlık $1.23 · K/Z $-7.99 (-0.65%)
- AÇIK HYPE: anlık $75.544 · K/Z +$0.0 (+0.0%)

*Determinism kodda; ikisi de AYNI sizing/risk (adil A/B); deep-thinker turlar arası öğrenmez; emir testnet/paper, gerçek para YOK.*
