# candidate-factors.md — Aday Faktör Park Yeri (Faz 2)

> Faz-1 içinde config SABİT — buradaki hiçbir faktör Faz-1'e eklenmez (CLAUDE.md kural 7).
> Bunlar Faz-2 için aday; her biri ölçülebilir hipotez + veri durumu ile.

## Durum etiketleri
- ✅ veri-hazır · 🟡 proxy-var · 🔴 ücretsiz-kaynak-yok (bkz. paid-sources.md)

| Kod | Faktör | Hipotez | Veri |
|-----|--------|---------|------|
| F-01 | Open Interest trendi | OI artışı + fiyat trendi = teyit; OI düşüşü = zayıf hareket | ✅ (data/funding) |
| F-02 | Funding ekstrem sınıfı | Ekstrem funding = aşırı kalabalık taraf, ters-dönüş riski | ✅ (triggers/rules.classify_funding) |
| F-03 | Likidasyon kümeleri | Küme üstüne/altına stop avı; küme = mıknatıs | 🔴 ücretli |
| F-04 | Portföy korelasyon kapısı | 4 varlık yüksek korelasyonluyken eşzamanlı poz = gizli tek-bahis | 🟡 (closes'tan hesaplanır) |
| F-05 | Erken pozisyon kapama | Tez bozulduğunda target beklemeden çık (2×2 faktöriyel test) | ✅ (mantık, veri gerekmez) |

## Test protokolü (Faz-2'ye geçince)
1. Faz-1 ~30 trade baseline'ı kapanmadan faktör eklenmez.
2. Her faktör tek başına A/B: faktörlü kol vs faktörsüz kol, aynı snapshot/sizing.
3. Başarı ölçütü: fee sonrası expectancy ↑ VE B&H baseline'ı yenme (L-01), Sharpe leakage bayrağı yok (L-02).
4. Over-trading kontrolü: trade sayısı artıyorsa net expectancy düşmemeli (L-03).

## Bağlı modüller
- F-01/F-02 ham veri: [data/funding.py]
- F-03 proxy/eksik işaret: [data/onchain.py] (`liquidation_clusters: ücretsiz-kaynak-yok`)
- Metr: [evaluation/metrics.py]
