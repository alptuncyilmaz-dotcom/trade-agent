# onchain-research.md — Ücretsiz on-chain flow kaynak araştırması

> Otonom protokol gereği (CLAUDE.md): implementasyon boşluğu → internette araştır, kararı
> `logs/`'a yaz. Bu o kayıt.

**Tarih:** 2026-06-13
**Soru:** Exchange inflow/outflow (on-chain akış) için güvenilir ÜCRETSİZ API var mı?

## Bulgu: HAYIR (güvenilir ücretsiz exchange-netflow kaynağı yok)

| Kaynak | Ücretsiz exchange flow? | Not |
|---|---|---|
| Glassnode | ❌ | Exchange netflow paid tier; free tier sınırlı |
| CryptoQuant | ❌ | Exchange flow paid; free çok kısıtlı |
| Nansen | ❌ | Tamamen paid |
| Coinglass API | ⚠️ kısmi | funding / OI / liquidation free-ish; gerçek on-chain netflow DEĞİL |
| blockchain.com charts | ❌ | Ağ geneli metrikler var ama borsa-spesifik netflow güvenilir değil |

## Karar
- **Sinyal UYDURULMAZ.** `data/onchain.py` `available: False` döner (eksik alanlar `ücretsiz-kaynak-yok`).
- Sistem **funding + OHLCV + OI** ile çalışır.
- Bu eksiklik rapora "Veri durumu" altında yazılır.
- İleride: ücretli kaynak (`strategy/paid-sources.md` P-02) VEYA Coinglass'ın funding/OI verisi ayrı
  "türev sinyali" katmanı olarak değerlendirilebilir. Bu **plumbing** kararı — çekirdek disipline
  dokunmaz; eklenirse yine testnet-only, sinyal-uydurmama kuralları geçerli.
