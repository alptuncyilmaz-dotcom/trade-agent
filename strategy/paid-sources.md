# paid-sources.md — İLERİDE ALINACAK PARALI KAYNAKLAR (tek liste, çapraz-sistem)

> **Bu SADECE BİR LİSTE — şimdi hiçbir paralı kaynak ALINMAZ/entegre EDİLMEZ.**
> Bu oturumda ve önceki kararlarda "bedava yok / paralı / kısıtlı" diye ertelenen
> tüm veri kaynakları tek yerde. Hem **trader** (kripto) hem **equity** (lowcap/solid)
> maddeleri burada (çapraz-sistem planlama dokümanı). **Davranış/özellik DEĞİL** — bilgi yazımı.
>
> **Alma tetiği (ikisi birden, o gün geldiğinde TEK BAKIŞTA değerlendirilecek):**
> - **(a) Kanıt:** Mevcut **bedava** sistem **Faz 2+'da edge gösterdi mi?** Edge kanıtlanmadan
>   paralı veriye para harcamak anlamsız (L-01: tek-test/varsayımdan kural çıkmaz).
> - **(b) Bütçe:** Gelir/bütçe kararı — **İNSAN.** AI almaz, önermez-zorlamaz; sadece liste tutar.
>
> **"Bir noktada hepsi BİRDEN değerlendirilecek"** — tek tek değil; o gün gelince bu liste
> baştan sona okunup "neyi neden alacağız, hangi sırayla" kararı insan tarafından verilir.
> İlgili bedava-durum dokümanı: `../data/onchain.py`, vault `_engine/veri-plani.md`, `deep_scan.py` (`_LIQ_SOURCE_NOTE`).

---

## TRADER (kripto perp)

### P-01 — Likidasyon haritası (fiyat-seviyesi liq-heatmap)
- **Olası kaynak:** CoinGlass API (ücretli tier), Hyperdash benzeri liq-feed.
- **Ne işe yarar:** Fiyatın hangi seviyelerinde stop/likidasyon **kümeleri** olduğunu gösterir → cascade/dönüş noktaları, **stop-hunt** bölgeleri.
- **Hangi kararı/fonksiyonu iyileştirir:** [H-04] giriş-stop-hedef bütünlüğü değerlendirmesi (stop'u likidite-avı bölgesinin DIŞINA koyma); `deep_scan._pressure_read` giriş-bölgesi yorumunu **proxy'den gerçeğe** taşır; otonom stop yerleştirme (Faz 2+ değerlendirilirse).
- **Neden gerek(ecek):** Şu an `deep_scan` yalnız funding+premium+OI'den **PROXY** çıkarım yapıyor — gerçek seviye-haritası DEĞİL. H-04 "stop yanlıştı mı" sorusunu veri ile güçlendirir.
- **Bedava alternatif neden yetersiz:** Resmi Hyperliquid `/info` yalnız **toplam OI + funding + premium + mark/oracle** verir (seviye-bazlı liq dağılımı YOK); CoinGlass liq-map'i sitede bedava görünür ama **API'si ücretli**; moondev/thunderhead 3.-taraf uçlar **doğrulanmamış/kırılgan**.
- **Çapraz-ref:** `candidate-factors.md` → **F-03** (liquidation gap) + **H-04**; `deep_scan.py` → `_LIQ_SOURCE_NOTE`.

### P-02 — Exchange inflow/outflow + on-chain akış
- **Olası kaynak:** Glassnode, CryptoQuant, Nansen (hepsi netflow = paid tier).
- **Ne işe yarar:** Borsalara para giriş/çıkışı (birikim/dağıtım), büyük cüzdan hareketleri → pozisyonlanma/yön bağlamı.
- **Hangi kararı/fonksiyonu iyileştirir:** `candidate-factors.md` **"ADAY GİRDİ"** (haber/akış'ı otomatik karara katma) kararının **veri ayağı**.
- **Neden gerek(ecek):** `data/onchain.py` şu an **`available: False`** (uydurma sinyal üretmez). Akış sinyali olmadan "ADAY GİRDİ" uygulanamaz.
- **Bedava alternatif neden yetersiz:** Glassnode netflow paid; CryptoQuant exchange-flow paid (free çok kısıtlı); Nansen tamamen paid; Coinglass free yalnız funding/OI (gerçek netflow değil); blockchain.com charts yetersiz. **Güvenilir bedava netflow YOK** (onchain.py `_RESEARCH` notlarında kayıtlı).
- **Çapraz-ref:** `candidate-factors.md` → **"ADAY GİRDİ"**; `data/onchain.py` → `available: False` + araştırma notları.

---

## EQUITY (lowcap + solid)

### P-03 — Yapısal / premium screener
- **Olası kaynak:** Ücretli yapısal hisse screener (tüm NASDAQ evrenini fundamental/teknik filtreyle tarayan).
- **Ne işe yarar:** Sektör-agnostik taramayı **AI'nın bildiği isimlerin ötesine** genişletir — en erken/keşfedilmemiş (0-analist) isimleri yapısal veriyle bulur.
- **Hangi kararı/fonksiyonu iyileştirir:** `discovery.py` keşif evreni; **"Bilinen sınır"** (AI sadece eğitim verisi + web'den bildiği isimleri getirir, tüm evreni taramaz).
- **Neden gerek(ecek):** Şu an keşif EDGAR full-text + web ile sınırlı → "neden hep benzer isimler" sorununun yapısal çözümü budur.
- **Bedava alternatif neden yetersiz:** Kapsamlı/güvenilir yapısal screener verisi bedava değil; EDGAR keşfi keyword/event'e bağlı, evren-taraması değil.
- **Çapraz-ref:** vault `CLAUDE.md` → "Bilinen sınır"; `data/scripts/discovery.py` → "screener bağlanana kadarki en iyi keşif kanalı".

### P-04 — Premium fundamental veri (tahmin/consensus/temiz comps)
- **Olası kaynak:** Ücretli fundamental veri (analist tahmini, consensus, temizlenmiş karşılaştırılabilirler).
- **Ne işe yarar:** İleriye-dönük DCF + comps (çarpan) analizi.
- **Hangi kararı/fonksiyonu iyileştirir:** Solid sistem değerleme derinliği (şu an **DCF YAPILMIYOR** — kasıtlı, veri yok diye).
- **Neden gerek(ecek):** EDGAR yalnız **ham/geçmiş** finansal verir; tahmin/consensus/temiz comps yok → DCF girdileri eksik.
- **Bedava alternatif neden yetersiz:** EDGAR ground-truth ama ileriye-dönük değil; bedava aggregator tahminleri micro-cap'te null/eski/güvenilmez.
- **Çapraz-ref:** `_engine/framework-solid.md` (değerleme); `_engine/veri-plani.md` (EDGAR sınırı).

---

## DURUM NOTU — kısıtlanan/kırılan BEDAVA kaynaklar (izleme, satın-alma değil)
> Bunlar "alınacak paralı kaynak" değil; **bedava kaynakların durumu** — biri daha
> bozulursa paralı muadil (ör. Polygon.io, Tiingo) bu listeye P-05+ olarak girer.
> Kaynak: standing memory + `_engine/veri-plani.md`.

| Bedava kaynak | Durum | Etki / mevcut çözüm |
|---|---|---|
| **yfinance** | Şub 2025 piyasa-geneli koptu; şimdi stabil | Fiyat/MA — **Stooq fallback** zorunlu kuruldu (`prices.py`), akış güvende |
| **Alpha Vantage** | Free tier **25 req/gün'e** düştü (standing memory) | Düşük hacim — yedek olarak bile sınırlı; birincil değil |
| **IEX Cloud** | **Kapandı** (standing memory) | Artık kullanılmıyor; EDGAR + yfinance/Stooq omurgası bundan etkilenmedi |

---

*Bu doküman yalnız PLANLAMA listesidir. Hiçbir paralı kaynak şimdi alınmaz/entegre edilmez.
Faz 1 dokunulmaz; davranış/özellik eklenmedi (bilgi yazımı). Alma kararı: edge-kanıtı (Faz 2+) + bütçe → İNSAN.*
