# candidate-factors.md — Araştırılan ADAY faktörler (insan onayı bekler)

> **Blind-spot faktör keşfi (kullanıcı isteği).** Reflection bir kaçırmayı mevcut
> faktör setinde (`features/factors.py CURRENT_FACTORS`) bulamazsa → internetten
> araştırır → kaynaklı aday faktörü BURAYA yazar. **Uydurma faktör YOK** (kaynak
> zorunlu). **Otomatik eklenmez** — Can onaylayınca `features/`'a faktör olur,
> sonra hipotez olarak forward-test edilir (L-01: tek-test/varsayımdan kural çıkmaz).

---

## Araştırma 2026-06-14 — kaynak: türev-piyasa sinyalleri (RSI/MACD ötesi)
> Tetik: BTC-001 stop derin analizi — mevcut set (RSI/MACD/ATR/funding-değeri/trend/
> rejim/hacim) **pozisyonlanma ve aşırılık** sinyallerini görmüyordu. Araştırma:
> [Gate web3 — OI/funding/liquidation](https://web3.gate.com/crypto-wiki/article/how-do-derivatives-market-signals-predict-crypto-price-movements-in-2025-futures-open-interest-funding-rates-and-liquidation-data-explained-20260206) · [Phemex — funding sinyali](https://phemex.com/academy/what-is-funding-rate-in-crypto-futures)

| Aday faktör | Ne ölçer | Veri | Durum |
|---|---|---|---|
| **[F-01] Open Interest trendi** | Pozisyon büyüklüğü artıyor/azalıyor (momentum teyidi vs zayıflık) | ✅ **ZATEN VAR** — `funding.get_funding` `openInterest` döndürüyor (kullanılmıyor) | **eklenebilir** (kod, veri hazır) |
| **[F-02] Funding EKSTREM sınıflaması** | Sadece değer değil: aşırı-pozitif (>~%0.05/saat) = aşırı-ısınmış long → reversal riski | ✅ **ZATEN VAR** — funding değeri çekiliyor; eşik sınıflaması eklenecek | **eklenebilir** (kod) |
| **[F-03] Liquidation kümeleri** | Stop yığılma bölgeleri → cascade/reversal noktaları | ⚠️ **GAP** — Hyperliquid /info kolay vermez; Coinglass tipi feed gerek (ücretsiz mi araştırılmalı) | **araştırma sürüyor** (gap) |

### Değerlendirme (faithfulness)
- **F-01 + F-02 güçlü adaylar:** veri zaten elimde (HL `openInterest` + `funding`), yeni bağımlılık YOK, araştırma bunların edge taşıdığını gösteriyor (OI+funding+liquidation entegre çerçeve tek-gösterge'den doğru). Ama **hipotez** — eklenince forward-test edilir.
- **F-03 gerçek gap:** liquidation verisi ücretsiz/güvenilir kaynak araştırması gerek (on-chain gap'ine benzer). Bulunamazsa F-01+F-02 ile devam, F-03 raporlanır (uydurma sinyal YOK). **Bedava kaynak yok teyit edildi (2026-06-15)** → gerçek liq-haritası için paralı kaynak gerekir: **bkz. [`paid-sources.md`](paid-sources.md) → P-01** (CoinGlass API vb.; Faz 2+ / bütçe kararı).
- **BTC-001 ile bağ:** F-02 (funding-ekstrem) o trade'de aşırı-ısınmayı, F-01 (OI) pozisyonlanma zayıflığını gösterebilirdi — RSI 66.5'in tek başına anlatamadığını tamamlar.

### Can kararı bekleyen
- F-01 (OI trendi) + F-02 (funding-ekstrem) `features/`'a faktör olarak eklensin mi? Onaylarsan `indicators`/`funding`'e ekler, `CURRENT_FACTORS`'a kaydeder, snapshot'a taşır, forward-test ederim.
- F-03 (liquidation) için ücretsiz kaynak araştırmasını derinleştireyim mi?

<!-- Sonraki blind-spot araştırmaları buraya birikir (kaynak+tarih). -->

---

## ADAY SİSTEM — uzun-vadeli "sağlam kripto" (al-tut) · 2026-06-14
> Mevcut **kısa-vade momentum trader'dan AYRI** bir sistem fikri. Kaydedildi, **uygulanmadı.**
- **Fikir:** Düşük batma-riski + gerçek kullanım/benimsenme olan kripto varlıkları **al-tut** (uzun ufuk) — equity "solid" sisteminin kripto karşılığı.
- **NEDEN ŞİMDİ DEĞİL:** (1) Mevcut kısa-vade trader'ın edge'i **henüz ölçülmedi** (forward-test ~1 trade); Faz 1 bitmeden yeni sistem açmak **sayacı sıfırlar** / ölçümü bozar. (2) Kripto-fundamental veri **bulanık + manipülasyona açık**: sahte hacim, anonim takım, şişirilmiş "ortaklık" duyuruları; bedava kaynakların güvenilirliği şüpheli (equity'deki EDGAR ground-truth'un karşılığı yok).
- **Tetik:** **Faz 2+** (mevcut trader edge'i ölçüldükten SONRA). O zaman: güvenilir fundamental veri kaynağı araştır → ayrı sistem olarak değerlendir (mevcut trader'ı bozmadan).
- Durum: **ERTELENDİ** (insan kararı, Faz 2+).

## ADAY GİRDİ — haber/makro + exchange flow'u OTOMATİK karara katma · 2026-06-14
> Manuel derin mod (`trader-deep`) bunu **insan-incelemesi için** kısmen karşılıyor. Buradaki aday: **otomatik runner'ın kararına** katma — AYRI ve **ERTELENMİŞ.**
- **NEDEN ŞİMDİ DEĞİL:** (1) Deterministik mimariyi bozar (LLM/haber döngüye girer → varyans + maliyet). (2) **Leakage riski (Glasserman/Lin)** — LLM eğitim verisinden olay sonucunu bilebilir. (3) On-chain exchange inflow/outflow için **güvenilir ücretsiz kaynak yok** (bkz. `data/onchain.py` available:False, F-03 gap). Veri ayağı paralı: **bkz. [`paid-sources.md`](paid-sources.md) → P-02** (Glassnode/CryptoQuant/Nansen; Faz 2+ / bütçe kararı).
- **Tetik:** **Faz 2+** değerlendir — o zaman: leakage-güvenli tasarım + güvenilir kaynak + maliyet/varyans analizi.
- Durum: **ERTELENDİ.** (Manuel mod izole olarak zaten var; otomatik-karara-katma ayrı.)

## ADAY DERS (H-04) — GİRİŞ-STOP-HEDEF BİR BÜTÜN · 2026-06-15
> **Kaydedildi, UYGULANMADI.** Tetik: ~30 trade + patern (Faz 2). Tek/az trade'de HİÇBİRİ değiştirilmez.

**Gözlem (BTC-001):** fiyat stop'a "uçtan" değip (63800) hedef yönüne döndü (65700).

**ÜÇ MÜMKÜN YORUM — tek trade AYIRAMAZ:**
- **(a) ENTRY yanlıştı** — 64500 erken/yüksekti (RSI 66.5, bkz. H-03); daha iyi giriş stop'u hiç yedirmezdi.
- **(b) STOP yanlıştı** — 64080 likidite-avına açıktı; biraz geniş stop dönüşü yakalardı.
- **(c) İkisi de doğruydu, sadece varyans** — bu sefer döndü, bir dahaki dönmeyebilir.

**KRİTİK:** "stop'u gevşet" TEK BAŞINA YANLIŞ olabilir — asıl sorun entry ise, geniş stop sadece **daha büyük kayıp** getirir. Entry + stop + hedef bir **BÜTÜN** olarak değerlendirilmeli, izole değil.

**Değerlendirme (Faz 2, ~30 trade):** şunlar sayılacak — kaç trade stop'a değip döndü (stop-hunt paterni), bu trade'lerde entry RSI/trend neydi (erken-giriş paterni mi), stop ATR'nin kaç katındaydı.

**VERİ hangisini gösterirse o düzeltilir:**
- Stop-sonrası-dönüşler **hep yüksek-RSI girişlerdeyse** → **ENTRY sorunu** (giriş disiplini sıkılaştır).
- Dönüşler **her girişte** oluyorsa → **STOP sorunu** (ATR-çarpanı / likidite-bölgesi).
- **Az örnekse** → varyans, dokunma.

**Karar:** Tek/az trade'de HİÇBİRİ değiştirilmez — **insan**, veri paterniyle karar verir. **Tetik: ~30 trade + patern.** (Bağ: H-03 geç-giriş; manuel `deep_scan` liq/funding-baskı proxy'si bu paterni gözlemeye yardımcı.)

## ADAY (F-04) — PORTFÖY KORELASYON / KONSANTRASYON KAPISI · 2026-06-15
> **Kaydedildi, UYGULANMADI (Faz 2 adayı).** Kaynak: challenger'ın 2026-06-15 cold-scan'de yakaladığı kör nokta.
- **Gözlem:** Sistem her pozisyonu BAĞIMSIZ boyutluyor; 4 korelasyonlu long (BTC/ETH/XRP/HYPE hepsi aynı yön) açıldığında piyasa-geneli düşüş hepsini BİRDEN vurur → gerçek risk tek-poz riskinin katı.
- **Mevcut kısmi koruma:** risk-bazlı sizing (%1.5) + %30 poz tavanı + %100 teminat-guard + serbest-bakiye-farkında boyutlama korelasyon riskini **KISMEN** sınırlar — ama **TAM korelasyon koruması DEĞİL** (4 bağımsız %1.5'lik korelasyonlu long = ~%6 korelasyonlu maruziyet).
- **Aday çözüm (Faz 2):** portföy-seviyesi risk tavanı (toplam korelasyonlu maruziyet sınırı) VEYA korelasyon-düzeltmeli boyutlama. **Tetik: Faz 2 + veri** (A/B'de konsantrasyonun gerçekten zarar verip vermediğini gör). Kurala terfi insan onayıyla.

## TEYİT — F-01/F-02/F-03 (yukarıda) kayıtlı, DOKUNULMADI
- F-01 (OI trendi), F-02 (funding-ekstrem), F-03 (liquidation gap) — yukarıdaki tabloda kayıtlı, değiştirilmedi. Hepsi **Faz 2 geriye-dönük test** bekliyor.

## ADAY (F-05) — ERKEN POZİSYON KAPAMA (SL/TP beklemeden risk görünce kapat) · 2026-06-16
> **Kaydedildi, UYGULANMADI (Faz 2 adayı).** Kaynak: Can — A/B simetri (long+short) kararıyla birlikte not edildi.
- **Fikir:** SL/TP'ye değmeden, risk görünce (tez bozuldu / momentum döndü / funding-ekstrem) pozisyonu erken kapat. Şu an yalnız path-check (stop/target) ile kapanıyor.
- **TASARIM = 2×2 FAKTÖRİYEL (A-B-C-D)** — erken kapamayı **karar mekanizmasından İZOLE** ölçer:
  - **A:** deterministic / erken-kapama YOK
  - **B:** deep-thinker / YOK
  - **C:** deterministic / VAR
  - **D:** deep-thinker / VAR
  - **A vs C** = det'te erken kapama faydalı mı; **B vs D** = deep-thinker'da. Erken kapamayı bir kola GİZLİCE eklemek A/B'yi KİRLETİR; faktöriyel onu **ÖLÇÜLEN değişken** yapar.
- **BEDELİ:** 4 kol = 4 kat state/bakiye (**$16k paper**), 2 LLM kolu (B+D) = 2 kat kota, 4 kat veri gereksinimi.
- **KOŞUL:** önce mevcut A/B (long+short) **~30 trade stabilize** olsun. Sonra insan onayıyla faktöriyele geç.
