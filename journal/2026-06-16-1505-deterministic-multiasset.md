# Otonom Tur (deterministic-trader) — 2026-06-16 15:05:36 UTC

> A/B agent: **deterministic-trader** · **TESTNET/PAPER · GERÇEK PARA YOK** · risk-bazlı sizing (%1.5/%30/%100-guard).

## PİYASA REJİMİ: **MIXED** (günlük) — {'up': 1, 'down': 1, 'range': 2}

| Varlık | Fiyat | 1d-trend | counter-trend (long) | trigger | Karar |
|---|---|---|---|---|---|
| BTC | $65699.0 | down | ⚠️ EVET | ❌ | **WAIT** |
| ETH | $1782.7 | range | hayır | ❌ | **WAIT** |
| XRP | $1.2109 | range | hayır | ❌ | **KAPANDI** |
| HYPE | $73.706 | up | hayır | ✅ | **WAIT** |

## Karar (detaylı)
- **Karar zamanı:** 2026-06-16 15:05:36 UTC.
- **forward-test sayacı:** 2.
- KAPANDI XRP stop_hit net -2.4155% (fee $1.09) · baseline edge: False · etiket YOK (L-02)
- WAIT BTC: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- WAIT ETH: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- WAIT XRP: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- AÇIK HYPE: anlık $73.706 · K/Z $-30.62 (-2.43%)

*Determinism kodda; ikisi de AYNI sizing/risk (adil A/B); deep-thinker turlar arası öğrenmez; emir testnet/paper, gerçek para YOK.*
