---
name: trader-refresh
description: Kripto perp OTONOM pozisyon yöneticisi (testnet) — açık pozisyonu kontrol eder; stop/target değdiyse KENDİ KAPATIR (testnet) + sonuç + tez≠fiyat ayrımı. SUCCESSFUL/FAILED etiketi YASAK. Eski tezi görür ama savunma değil. TESTNET ONLY, gerçek para YOK.
---

# trader-refresh — Otonom Pozisyon Yöneticisi + Reflection

**Mod:** refresh (otonom kapanış + reflection) · **İş:** açık pozisyonu yönet, sonucu değerlendir.

## ⚠️ Güvenlik sınırı (OTONOM AMA KORUMALI)
**TESTNET / PAPER ONLY. GERÇEK PARA YOK.** Otonom modda **kendin pozisyon kapatabilirsin (testnet)** ama **gerçek-para gate'ini AÇAMAZSIN** (insan kararı). Emir hep testnet — order endpoint mainnet'te tanımsız.

## OTONOM AKIŞ — ADIM 1: Açık pozisyon kontrolü (scan'den ÖNCE)
1. **Oku:** `journal/`'daki açık pozisyon + **karar zamanı** (`decided_at`).
2. **TARAMA-ARASI SL/TP (KOD — kritik):** Karar anından ŞİMDİYE kadarki mumları çek (`ohlcv.get_candles`, 1m/5m ince granül) → `execution/autonomous.check_path(position, candles)`. Bu, mum **high/low**'una bakar → **iki tarama arasında stop'a/target'a değip geri dönmüş olsa bile YAKALAR** (sadece anlık fiyat bakmak bunu kaçırır). Seyrek tarama (örn. 45 dk) bu sayede SL/TP kaçırmaz.
   - **open** (yolda hiç dokunulmadı) + tez geçerli → **TUT**, logla, DUR.
   - **stop_hit / target_hit** (yolda dokunuldu, `hit_at` zamanlı) → **KENDİN KAPAT (testnet)** + aşağıdaki SONUÇ. `ambiguous: True` ise (tek mumda ikisi de) konservatif stop + flag.
3. **SONUÇ (KOD paketler):** `execution/autonomous.evaluate_close(...)` →
   - net %, stop/target, **fee-dahil** (`simulator`).
   - **ZORUNLU (L-01):** `baselines.compare` — buy-and-hold + basit-RSI çıpalarına KARŞI fee-net (`edge` var mı).
   - **ZORUNLU (L-03):** `cost_summary` — **fee_bleed_pct + turnover** (over-trading sessiz katil).
   - **forward-test sayacı +1.**
4. **TEZ≠FİYAT AYRIMI (sen yazarsın):** tez doğru muydu (fiyat oynasa bile) / tez mi yanlıştı? **"SUCCESSFUL/FAILED" ETİKETİ YASAK** (L-02: TP-hit ≠ başarı — şans/leakage olabilir; stop ≠ kötü karar). Sadece **sonuç + tez-değerlendirmesi.**
5. **📋 ANALİZ ÖZETİ — HER KAPANIŞTA ZORUNLU (kazanç DA kayıp DA).** Bu genel disiplin: her trade kapandığında, **kazansa da kaybetse de**, journal'ın başına üç-parça özet yaz (parse edilebilir, site bunu gösterir):
   - **`Nasıl verildi:`** karar nasıl alındı — hangi trigger/feature/varsayım, kaldıraç-gerekçe (geriye-dönük: "bu kararı nasıl verdim").
   - **`Sonuç:`** net % (fee-dahil) + **baseline** (B&H + basit-RSI'ı yendi mi, edge var mı) + tez≠fiyat (tez tuttu mu yoksa **kazançsa şans/varyans mıydı**, kayıpsa **tez mi zayıftı**).
   - **`DERS:`** çıkan ders VAR mı? **Neyi göz önünde bulunduramadı, ne KAÇIRDI** (HTF trend? rejim? edge-kalitesi? trigger≠edge?). Sistem-boşluğu varsa Can'a flag'le. Gerçek ders yoksa **"DERS: yok — gürültü/varyans"** yaz (tek olaydan kural çıkarma, L-01). Ders varsa aday hipotez (tekrar paterni + insan onayı bekler).
   - **KAZANÇTA da ZORUNLU:** TP-hit'te "kazandım, tamam" deme — sor: *şans mı, edge mi? tez gerçekten oynadı mı yoksa fiyat alakasız mı hareket etti? bir sonraki sefer tekrarlanır mı?* (L-02 — varyans/leakage gizli kalmasın.)
5. **Logla** → `journal/` (tez / sonuç / neden AYRI). **Aday öğrenim** → `strategy/` ÖNERİSİ (insan onayı; tek sonuçtan kural yazma).

## ADIM 1c: Önceki tarama analizini gözden geçir + KAÇIRILAN-hareket analizi
> Kullanıcı isteği — her taramada bir önceki tarama(lar)ın analizine bak.
- **Oku:** bir önceki tarama/karar journal'ı (en son `decided_at`'e kadarki analizler).
- **Kaçırılan-hareket (KOD):** önceki taramadan bu yana mumları çek → `autonomous.sharp_move(closes)` → **sert hareket oldu mu** (örn. ≥%5 excursion)?
- **Eğer önceki taramada EMİN OLAMADIN (WAIT) AMA sert hareket olduysa** → **"neden kaçırdım" analizi:** hangi sinyali görmedim? trigger eşiği mi dardı, counter-trend mi yanlış elediğim bir kurulumu durdurdu, HTF mi karışıktı? **Kaçırılanı yaz** → aday öğrenim (kural değil).
- ⚠️ **ANCHOR KORUMASI:** Bu **öğrenme/analiz**tir, **karar-çapası DEĞİL.** "Geçen sefer kaçırdım, şimdi telafi için açayım" YASAK (revenge/FOMO). Kaçırılan-analizi `strategy/` aday hipoteze gider; bir sonraki **scan kararı yine anchor-free** (sadece güncel snapshot + lessons). Geçmiş sonuç/kaçırma karar girdisine girmez (`is_anchor_clean`).

## ADIM 1d: BLIND-SPOT FAKTÖR KEŞFİ (kaçırılan, faktör setinde YOKSA → internet araştır)
> Kullanıcı isteği — "ajanın baktığı şeyler var; kaçırdığı şey bunların içinde DEĞİLSE internetten araştırıp yeni faktör/kaynakları değerlendirsin." *(LLM reflection işi — deterministik 45dk runner bunu YAPMAZ; sen/Can check-in'de yaparsınız.)*
- Kaçırılanı `features/factors.is_covered(kaçırma_metni)` ile sınıfla:
  - **covered=True** → faktör zaten vardı, **uygulama/ağırlık** hatası (yeni faktör gerekmez; mevcut faktörü doğru tart).
  - **covered=False** → **BLIND-SPOT.** İnternetten araştır (WebSearch): bu kör noktayı hangi **faktör/kaynak** yakalar? **Kaynaklı** (URL+tarih) aday faktörü `strategy/candidate-factors.md`'ye yaz.
- **Uydurma faktör YOK** (kaynak zorunlu, faithfulness). **Otomatik EKLEME YOK** — Can onaylayınca `features/`'a faktör olur, sonra **forward-test edilir** (L-01: araştırma = hipotez, kural değil).
- Bulunamazsa (örn. ücretsiz veri yok) → gap olarak raporla, uydurma sinyal üretme (on-chain gap'i gibi).

## tez ≠ fiyat (SAFEGUARD)
- **Tek sonuçtan strateji dokümanına YAZMA.** Kârlı trade kötü karar olabilir (varyans); stop olan iyi karar olabilir (şans). Karar kalitesi (o an bilinen veriyle mantıklı mıydı) ile fiyat sonucu **AYRI**.
- Tek trade = **etiketli aday hipotez**; stratejiye ancak **tekrar paterninden PROMOTE-SWEEP** ile (insan onayı) terfi.

## ANCHOR KURALI (asimetrik)
- Eski tezi **GÖRÜRSÜN** (sonucu değerlendirmek için) — ama işin **savunma değil**, log + aday öğrenim.
- **Aynı veride yeniden FIT ETME.** Trade'ler her zaman taze forward veride; strateji dokümanı birikimli öğrenme. Bu ayrım overfitting'i engeller (7. katman).

## DETERMINISM KODDA
Metrikleri/funding'i kod verir; sen yorumlarsın. Sayı uydurma.

## Sıralama bağı (state tek kaynak)
**refresh** açık pozisyonu kapatır + loglar, **SONRA** scan yeni tez açar (çakışan pozisyon yok).

## Otonom protokol
İmplementasyon boşluğu → araştır + devam (kararı `logs/`'a). **Çekirdek disiplin (tez≠fiyat, anchor, testnet-only, win-rate-yok, point-in-time, determinism) → DUR, Can'a sor.**

## Kapanış aksiyonu (ZORUNLU — Can isteği)
İş biter bitmez dashboard'ı tazele: `bash "../Obsidian Vault/data/scripts/sync.sh"`. Çıktın site'a yansır; site snapshot — sync yapılmazsa eski kalır.
