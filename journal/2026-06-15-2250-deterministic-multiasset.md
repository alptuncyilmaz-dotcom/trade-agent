# Otonom Tur (deterministic-trader) — 2026-06-15 22:50:02 UTC

> A/B agent: **deterministic-trader** · **TESTNET/PAPER · GERÇEK PARA YOK** · risk-bazlı sizing (%1.5/%30/%100-guard).

## PİYASA REJİMİ: **MIXED** (günlük) — {'up': 1, 'down': 2, 'range': 1}

| Varlık | Fiyat | 1d-trend | counter-trend (long) | trigger | Karar |
|---|---|---|---|---|---|
| BTC | $66177.0 | down | ⚠️ EVET | ❌ | **WAIT** |
| ETH | $1788.6 | down | ⚠️ EVET | ❌ | **KAPANDI** |
| XRP | $1.2381 | range | hayır | ✅ | **AÇILDI** |
| HYPE | $66.711 | up | hayır | ❌ | **WAIT** |

## Karar (detaylı)
- **Karar zamanı:** 2026-06-15 22:50:02 UTC.
- **forward-test sayacı:** 7.
- KAPANDI ETH stop_hit net -1.571% (fee $0.89) · baseline edge: False · etiket YOK (L-02)
- KAPANDI XRP stop_hit net -2.0117% (fee $0.89) · baseline edge: False · etiket YOK (L-02)
- AÇILDI XRP buy entry 1.2381 / stop 1.21 / target 1.28 · 1.0x · notional $1221.3061 · RSI 58.3, MACD_hist -0.00, ATR 0.02; çok-TF 15m:range / 1h:up / 4h:up / 1d:range (counter-trend değil); kaldıraç 1.0x (1.0x — vol_frac=0.0127 (ters-ölçek 0.9), güven=low (tavan 1.0x), challenger=temiz, likidasyon 0 stop 1'ın ötesinde); boyut: notional $1221.3061 / margin $1221.3061 (risk $61.0653=%1.5 balance, sınır: poz-tavanı(%30)).
- WAIT ETH: trigger ateşlemedi (birincil kapı — net fırsat sinyali yok); rejim: mixed
- AÇIK BTC: anlık $66177.0 · K/Z $-6.77 (-0.68%)
- AÇIK XRP: anlık $1.2381 · K/Z +$0.0 (+0.0%)
- AÇIK HYPE: anlık $66.711 · K/Z $-12.95 (-1.29%)

*Determinism kodda; ikisi de AYNI sizing/risk (adil A/B); deep-thinker turlar arası öğrenmez; emir testnet/paper, gerçek para YOK.*
