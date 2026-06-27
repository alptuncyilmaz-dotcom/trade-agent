# onchain-research.md — Ücretsiz on-chain flow kaynak araştırması

> Otonom protokol gereği (INSA-TRADER.md Bölüm 6): implementasyon boşluğu →
> internette araştır, kararı `logs/`'a yaz. Bu o kayıt.

**Tarih:** 2026-06-13
**Soru:** Exchange inflow/outflow (on-chain akış) için güvenilir ÜCRETSİZ API var mı?

## Bulgu: HAYIR (güvenilir ücretsiz exchange-netflow kaynağı yok)

| Kaynak | Ücretsiz exchange flow? | Not |
|---|---|---|
| Glassnode | ❌ | Exchange netflow paid tier; free tier sınırlı on-chain metrik |
| CryptoQuant | ❌ | Exchange flow paid; free çok kısıtlı |
| Nansen | ❌ | Tamamen paid |
| Coinglass API | ⚠️ kısmi | funding / OI / liquidation free-ish; gerçek on-chain netflow DEĞİL |
| blockchain.com charts | ❌ | Ağ geneli metrikler var ama borsa-spesifik netflow güvenilir değil |

## Karar
- **Sinyal UYDURULMAZ.** `onchain.py` `available: False` döner.
- Sistem **funding + OHLCV** ile başlar (INSA-TRADER.md'nin öngördüğü fallback).
- Bu eksiklik rapora "Veri durumu" altında yazılır.
- İleride: ücretli kaynak (Glassnode/CryptoQuant) bağlanabilir VEYA Coinglass'ın
  funding/OI verisi ayrı bir "türev sinyali" katmanı olarak değerlendirilebilir
  (on-chain flow değil ama tamamlayıcı). Bu **plumbing** kararı — çekirdek
  disipline dokunmaz; eklenirse yine testnet-only, sinyal-uydurmama kuralları geçerli.
