# paid-sources.md — İLERİDE ALINACAK PARALI KAYNAKLAR (planlama listesi)

> **Bu SADECE BİR LİSTE — şimdi hiçbir paralı kaynak ALINMAZ/entegre EDİLMEZ.**
> "Bedava yok / paralı / kısıtlı" diye ertelenen veri kaynakları tek yerde. **Davranış/özellik DEĞİL** — bilgi yazımı.
>
> **Alma tetiği (ikisi birden):**
> - **(a) Kanıt:** Mevcut **bedava** sistem **Faz 2+'da edge gösterdi mi?** Edge kanıtlanmadan paralı veriye para harcamak anlamsız (L-01).
> - **(b) Bütçe:** Gelir/bütçe kararı — **İNSAN.** AI almaz, önermez-zorlamaz; sadece liste tutar.
>
> İlgili bedava-durum: `data/onchain.py`, `logs/onchain-research.md`, `deep_scan.py`.

---

## TRADER (kripto perp — bu repo)

### P-01 — Likidasyon haritası (fiyat-seviyesi liq-heatmap)
- **Olası kaynak:** CoinGlass API (ücretli tier), Hyperdash benzeri liq-feed.
- **Ne işe yarar:** Fiyatın hangi seviyelerinde stop/likidasyon **kümeleri** olduğunu gösterir → cascade/dönüş noktaları, **stop-hunt** bölgeleri.
- **Hangi kararı iyileştirir:** [H-04] giriş-stop-hedef bütünlüğü (stop'u likidite-avı bölgesinin DIŞINA koy); `deep_scan` giriş-bölgesi yorumunu **proxy'den gerçeğe** taşır; otonom stop yerleştirme (Faz 2+).
- **Neden gerek:** Şu an `deep_scan` yalnız funding+premium+OI'den **PROXY** çıkarım yapıyor — gerçek seviye-haritası DEĞİL.
- **Bedava alternatif neden yetersiz:** Hyperliquid `/info` yalnız toplam OI + funding + premium + mark/oracle verir (seviye-bazlı liq dağılımı YOK); CoinGlass liq-map sitede bedava görünür ama **API'si ücretli**; 3.-taraf uçlar doğrulanmamış/kırılgan.
- **Çapraz-ref:** `candidate-factors.md` → F-03 + H-04.

### P-02 — Exchange inflow/outflow + on-chain akış
- **Olası kaynak:** Glassnode, CryptoQuant, Nansen (hepsi netflow = paid tier).
- **Ne işe yarar:** Borsalara para giriş/çıkışı (birikim/dağıtım), büyük cüzdan hareketleri → pozisyonlanma/yön bağlamı.
- **Hangi kararı iyileştirir:** `candidate-factors.md` "haber/akış'ı otomatik karara katma" kararının **veri ayağı**.
- **Neden gerek:** `data/onchain.py` şu an **`available: False`** (uydurma sinyal üretmez). Akış sinyali olmadan bu aday uygulanamaz.
- **Bedava alternatif neden yetersiz:** Glassnode/CryptoQuant/Nansen netflow paid; Coinglass free yalnız funding/OI (gerçek netflow değil); blockchain.com yetersiz. **Güvenilir bedava netflow YOK** (bkz. `logs/onchain-research.md`).
- **Çapraz-ref:** `candidate-factors.md` → "ADAY GİRDİ"; `data/onchain.py`.

---

> **Not:** Equity (lowcap/solid) tarafı **ayrı bir sistem ve ayrı repo** — bu listede yer almaz.
> Bu doküman trade-agent (kripto perp) kapsamındadır.

---

*Bu doküman yalnız PLANLAMA listesidir. Hiçbir paralı kaynak şimdi alınmaz/entegre edilmez.
Faz 1 dokunulmaz. Alma kararı: edge-kanıtı (Faz 2+) + bütçe → İNSAN.*
