# Otonom Tur (deep-thinker) — 2026-06-15 22:05:03 UTC

> A/B agent: **deep-thinker** · **TESTNET/PAPER · GERÇEK PARA YOK** · risk-bazlı sizing (%1.5/%30/%100-guard).

## PİYASA REJİMİ: **MIXED** (günlük) — {'up': 1, 'down': 1, 'range': 2}

| Varlık | Fiyat | 1d-trend | counter-trend (long) | trigger | Karar |
|---|---|---|---|---|---|
| BTC | $66412.0 | down | ⚠️ EVET | ❌ | **WAIT** |
| ETH | $1811.9 | range | hayır | ✅ | **AÇILDI** |
| XRP | $1.2516 | range | hayır | ❌ | **WAIT** |
| HYPE | $68.232 | up | hayır | ❌ | **WAIT** |

## Karar (detaylı)
- **Karar zamanı:** 2026-06-15 22:05:03 UTC.
- **forward-test sayacı:** 0.
- AÇILDI ETH buy entry 1811.9 / stop 1787.39 / target 1852.04 · 1.0x · notional $1200.0 · ANALYST: snapshot'taki tek tetikleyen ETH; trend-uyumlu (1h/4h up, 1d range), aşırı-alım DEĞİL (RSI 69.9<70), funding nötr → geçerli momentum girişi. CHALLENGER: MACDh +0.09 ince/zayıf cross; RSI 69.9 geç-giriş eşiğinde (H-03); 1d range → düşük-edge, chop riski. KARAR (deep-thinker): geçerli tetik + trend-uyumu nedeniyle AL ama challenger uyarısını LOW confidence (→1x kaldıraç) + risk-bazlı küçük boyut (%1.5 tavan) ile absorbe et — küçük, kontrollü bahis. Asimetrik R:R (1.6×ATR stop / 2.62×ATR hedef).; kaldıraç 1.0x (1.0x — vol_frac=0.0085 (ters-ölçek 1.4), güven=low (tavan 1.0x), challenger=temiz, likidasyon 9 stop 1787'ın ötesinde); boyut: notional $1200.0 / margin $1200.0 (risk $60.0=%1.5 balance, sınır: poz-tavanı(%30)).
- WAIT BTC: trigger yok — MACDh -71.22 (negatif momentum) + 1d:down; long için zemin yok
- WAIT XRP: trigger yok — MACDh ~0.00 (momentum nötr); fırsat değil
- WAIT HYPE: trigger yok — MACDh -0.15 (negatif); 1d:up olsa da tetik yok, zorla giriş yok
- AÇIK ETH: anlık $1811.9 · K/Z +$0.0 (+0.0%)

*Determinism kodda; ikisi de AYNI sizing/risk (adil A/B); deep-thinker turlar arası öğrenmez; emir testnet/paper, gerçek para YOK.*
