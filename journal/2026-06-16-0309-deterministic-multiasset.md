# Otonom Tur (deterministic-trader) — 2026-06-16 03:09:13 UTC

> A/B agent: **deterministic-trader** · **TESTNET/PAPER · GERÇEK PARA YOK** · risk-bazlı sizing (%1.5/%30/%100-guard).

## PİYASA REJİMİ: **MIXED** (günlük) — {'up': 1, 'down': 2, 'range': 1}

| Varlık | Fiyat | 1d-trend | counter-trend (long) | trigger | Karar |
|---|---|---|---|---|---|
| BTC | $65730.0 | down | ⚠️ EVET | ❌ | **KAPANDI** |
| ETH | $1771.0 | down | ⚠️ EVET | ❌ | **WAIT** |
| XRP | $1.2178 | range | hayır | ❌ | **WAIT** |
| HYPE | $67.999 | up | hayır | ❌ | **WAIT** |

## Karar (detaylı)
- **Karar zamanı:** 2026-06-16 03:09:13 UTC.
- **forward-test sayacı:** 0.
- KAPANDI BTC stop_hit net -0.9867% (fee $0.90) · baseline edge: False · etiket YOK (L-02)
- WAIT BTC: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- WAIT ETH: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- AÇIK XRP: anlık $1.2178 · K/Z $-20.02 (-1.64%)
- AÇIK HYPE: anlık $67.999 · K/Z +$6.11 (+0.61%)

*Determinism kodda; ikisi de AYNI sizing/risk (adil A/B); deep-thinker turlar arası öğrenmez; emir testnet/paper, gerçek para YOK.*
