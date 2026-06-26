# candidate-factors.md — Araştırılan ADAY faktörler (insan onayı bekler)

> **Blind-spot faktör keşfi.** Reflection bir kaçırmayı mevcut faktör setinde bulamazsa →
> internetten araştırır → kaynaklı aday faktörü BURAYA yazar. **Uydurma faktör YOK** (kaynak
> zorunlu). **Otomatik eklenmez** — insan onaylayınca `features/`'a faktör olur, sonra hipotez
> olarak forward-test edilir (Faz 2). Faz-1 içinde config SABİT (CLAUDE.md kural 7).

## Durum etiketleri
✅ veri-hazır · 🟡 proxy-var · 🔴 ücretsiz-kaynak-yok (bkz. `paid-sources.md`)

| Kod | Faktör | Ne ölçer | Veri |
|-----|--------|----------|------|
| **F-01** | Open Interest trendi | Pozisyon büyüklüğü artıyor/azalıyor (momentum teyidi vs zayıflık) | ✅ `data/funding` `openInterest` |
| **F-02** | Funding EKSTREM sınıfı | Aşırı-pozitif funding = aşırı-ısınmış long → reversal riski | ✅ `triggers/rules.classify_funding` |
| **F-03** | Likidasyon kümeleri | Stop yığılma bölgeleri → cascade/reversal, stop-hunt | 🔴 ücretli (P-01) |
| **F-04** | Portföy korelasyon kapısı | 4 korelasyonlu long = gizli tek-bahis; portföy-seviyesi risk | 🟡 closes'tan hesaplanır |
| **F-05** | Erken pozisyon kapama | Tez bozulunca SL/TP beklemeden çık (2×2 faktöriyel test) | ✅ mantık |

### Değerlendirme (faithfulness)
- **F-01 + F-02 güçlü adaylar:** veri elimizde (HL `openInterest` + `funding`), yeni bağımlılık YOK. Ama **hipotez** — eklenince forward-test edilir.
- **F-03 gerçek gap:** ücretsiz/güvenilir liq kaynağı yok (2026-06-15 teyit) → paralı (`paid-sources.md` P-01). Bulunamazsa F-01+F-02 ile devam (uydurma sinyal YOK).

## F-04 — PORTFÖY KORELASYON / KONSANTRASYON KAPISI
> Kaydedildi, UYGULANMADI (Faz 2). Kaynak: challenger cold-scan kör noktası.
- **Gözlem:** her pozisyon BAĞIMSIZ boyutlanıyor; 4 korelasyonlu long (BTC/ETH/XRP/HYPE aynı yön) → piyasa düşüşü hepsini BİRDEN vurur (gerçek risk tek-poz katı).
- **Mevcut kısmi koruma:** %1.5 risk + %30 poz tavanı + %100 teminat-guard korelasyon riskini KISMEN sınırlar — TAM koruma DEĞİL.
- **Aday çözüm (Faz 2):** portföy-seviyesi risk tavanı VEYA korelasyon-düzeltmeli boyutlama. Tetik: Faz 2 + veri.

## F-05 — ERKEN POZİSYON KAPAMA (SL/TP beklemeden risk görünce kapat)
> Kaydedildi, UYGULANMADI (Faz 2). Kaynak: A/B simetri kararıyla not edildi.
- **Fikir:** risk görünce (tez bozuldu / momentum döndü / funding-ekstrem) erken kapat. Şu an yalnız path-check ile kapanıyor.
- **TASARIM = 2×2 FAKTÖRİYEL:** A: det/YOK, B: deep/YOK, C: det/VAR, D: deep/VAR. A vs C = det'te fayda; B vs D = deep'te. Gizlice eklemek A/B'yi KİRLETİR; faktöriyel onu ölçülen değişken yapar.
- **BEDELİ:** 4 kol = $16k paper + 2 kat LLM kotası. **KOŞUL:** mevcut A/B ~30 trade stabilize olsun, sonra insan onayı.

## ADAY DERS (H-04) — GİRİŞ-STOP-HEDEF BİR BÜTÜN
> Kaydedildi, UYGULANMADI. Tetik: ~30 trade + patern (Faz 2).
- **Gözlem (BTC-001):** fiyat stop'a "uçtan" değip hedef yönüne döndü. **Üç yorum — tek trade AYIRAMAZ:** (a) entry yanlıştı, (b) stop likidite-avına açıktı, (c) sadece varyans.
- **KRİTİK:** "stop'u gevşet" tek başına yanlış olabilir — asıl sorun entry ise geniş stop daha büyük kayıp getirir. Entry+stop+hedef **bütün** olarak değerlendirilir.
- **Değerlendirme (Faz 2):** kaç trade stop'a değip döndü, o trade'lerde entry RSI/trend neydi, stop ATR'nin kaç katıydı. Veri hangisini gösterirse o düzeltilir.

## ERTELENMİŞ SİSTEM FİKİRLERİ
- **Uzun-vadeli "sağlam kripto" (al-tut):** mevcut momentum trader'dan AYRI sistem. **NEDEN ŞİMDİ DEĞİL:** Faz-1 edge'i ölçülmedi; yeni sistem sayacı sıfırlar. Kripto-fundamental veri bulanık/manipülasyona açık. Tetik: Faz 2+.
- **Haber/makro + exchange flow'u OTOMATİK karara katma:** deterministik mimariyi bozar (LLM/haber döngüye girer → varyans+maliyet), leakage riski (Glasserman/Lin), on-chain için ücretsiz kaynak yok (P-02). Tetik: Faz 2+. (Manuel mod `trader-deep` izole olarak zaten var.)

<!-- Sonraki blind-spot araştırmaları buraya birikir (kaynak+tarih). -->
