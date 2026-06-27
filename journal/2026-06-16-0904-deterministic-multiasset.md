# Otonom Tur (deterministic-trader) — 2026-06-16 09:04:58 UTC

> A/B agent: **deterministic-trader** · **TESTNET/PAPER · GERÇEK PARA YOK** · risk-bazlı sizing (%1.5/%30/%100-guard).

## PİYASA REJİMİ: **MIXED** (günlük) — {'up': 1, 'down': 0, 'range': 3}

| Varlık | Fiyat | 1d-trend | counter-trend (long) | trigger | Karar |
|---|---|---|---|---|---|
| BTC | $66794.0 | range | hayır | ❌ | **WAIT** |
| ETH | $1801.5 | range | hayır | ❌ | **WAIT** |
| XRP | $1.2464 | range | hayır | ❌ | **WAIT** |
| HYPE | $73.802 | up | hayır | ✅ | **AÇILDI** |

## Karar (detaylı)
- **Karar zamanı:** 2026-06-16 09:04:58 UTC.
- **forward-test sayacı:** 1.
- KAPANDI HYPE target_hit net 3.9941% (fee $1.13) · baseline edge: True · etiket YOK (L-02)
- AÇILDI HYPE buy entry 73.802 / stop 71.94 / target 76.85 · 1.0x · notional $1243.8115 · LONG: RSI 81.2, MACD_hist +0.47, ATR 1.17; çok-TF 15m:up / 1h:up / 4h:up / 1d:up (HTF buy ile uyumlu, counter-trend değil); kaldıraç 1.0x (1.0x — vol_frac=0.0158 (ters-ölçek 0.8), güven=medium (tavan 2.0x), challenger=temiz, likidasyon 0 stop 72'ın ötesinde); boyut: notional $1243.8115 / margin $1243.8115 (risk $62.1906=%1.5 balance, sınır: poz-tavanı(%30)).
- WAIT BTC: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- WAIT ETH: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- AÇIK XRP: anlık $1.2464 · K/Z +$8.19 (+0.67%)
- AÇIK HYPE: anlık $73.802 · K/Z +$0.0 (+0.0%)

*Determinism kodda; ikisi de AYNI sizing/risk (adil A/B); deep-thinker turlar arası öğrenmez; emir testnet/paper, gerçek para YOK.*
