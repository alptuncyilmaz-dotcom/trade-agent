# paid-sources.md — Ücretli / Harici Veri Kaynakları

> Faz-1 yalnız Hyperliquid ücretsiz API kullanır (OKUMA mainnet, EMİR testnet — CLAUDE.md kural 2).
> Aşağıdakiler Faz-2 aday faktörlerinin (candidate-factors.md) eksik verisini kapatır.
> Hiçbiri Faz-1'e eklenmez. Bir kaynak eklenmeden önce: maliyet, gecikme, kapsama not edilir.

## Eksik veri → kaynak eşlemesi
| İhtiyaç | Faktör | Olası kaynak | Not |
|---------|--------|--------------|-----|
| Likidasyon kümeleri / haritası | F-03 | Coinglass, Hyblock, Velo | Genelde ücretli/rate-limit; doğruluk değişken |
| Borsa giriş-çıkış akışları | onchain | Glassnode, CryptoQuant, Nansen | Pahalı; gecikmeli; CEX-merkezli |
| Balina/cüzdan transferleri | onchain | Arkham, Nansen, on-chain RPC | Etiketleme güvenilirliği sınırlı |
| Haber / makro | trader-deep | WebSearch (ücretsiz) | Her madde TARİHLİ [yayın: YYYY-MM-DD] + kaynak URL |
| Funding/OI geçmişi (derin) | F-01/F-02 | Hyperliquid (ücretsiz, sınırlı) | Şu an point-in-time; tarihçe için arşiv gerek |

## Değerlendirme kriterleri (eklemeden önce)
- **Maliyet/değer:** faktör expectancy'yi fee sonrası artırıyor mu? (yoksa ekleme)
- **Gecikme:** veri saatlik tura yetişiyor mu? Bayat veri = leakage/yanlış sinyal.
- **Doğrulanabilirlik:** kaynak uydurmaya açık mı? (CLAUDE.md kural 6 — kaynak zorunlu)
- **Bağımlılık:** tek sağlayıcıya kilitlenme riski.

## Şu anki duruş
Ücretli kaynak YOK. data/onchain.py eksik alanları `ücretsiz-kaynak-yok` olarak DÜRÜST işaretler —
uydurma proxy üretmez. Gerçek on-chain gelene dek bu faktörler park yerinde kalır.
