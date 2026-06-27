# strategy/_strategy.md — Yaşayan Strateji Dokümanı (v0.1, başlangıç)

> 7. katman: yavaş evrilen, insan-okunur strateji + stop + giriş mantığı.
> **Trade'ler her zaman taze forward veride; bu doküman birikimli öğrenme.**
> Bu ayrım overfitting'i engeller. Reflection agent ÖNERİR, insan ONAYLAR.
> **Aktif dersler (graduate olmuş kurallar):** `strategy/lessons.md`. Bu doküman aday hipotez; lessons.md insan-onaylı aktif kural.

## Durum: BAŞLANGIÇ (forward-test öncesi)
Henüz trade yok → birikmiş ders yok. Bu doğru. Doküman ilk testnet
trade'lerinden + reflection'dan dolar. **Uydurma kural eklenmez.**

## Çekirdek ilkeler (değişmez — disiplinden gelir)
- **Asimetrik R:R.** Geniş hedef / dar stop mantığı. Dar TP + geniş SL YASAK (felaket kuyruğu).
- **Win-rate hedefi YOK.** Pozitif expectancy + kontrollü drawdown.
- **Trigger-only giriş.** `triggers/rules.py` ateşlemeden işlem yok.
- **Tek perp (BTC veya ETH).** Değişken sayısını düşük tut.
- **Funding maliyettir.** Uzun tutuşta funding'i tez gerekçesine kat.
- **Öğrenme yalnız iki kaynaktan:** (a) **testnet forward**, (b) **dış strateji araştırması**. **Geçmiş veride backtest ile strateji öğrenmek YASAK** (leakage + overfitting → "backtest tuzağı").

## Dış strateji araştırması (scan agent doldurur — DAMITARAK)
> EKLEME 1. Araştırılan strateji = **HİPOTEZ**, kural değil. Buraya kaynak+tarihle damıtılır, aşağıdaki "Aday hipotezler"de ileri-teste sokulur.

Format (her giriş):
- **[Strateji adı]** · kaynak: [URL/yayın] · tarih: [YYYY-MM] · son 1–3 yıl: [ne işe yaramış / yaramamış]
- **Kendi framework'le karşılaştırma:** [örtüşen / çelişen yan]
- **Eksik/zayıf nokta:** [ne kanıtlanmamış, hangi rejime bağlı]

<!-- scan agent cold analizde doldurur. Uydurma kaynak YOK. -->

- **Time-series / trend-following momentum** · kaynak: arXiv "Systematic Trend-Following with Adaptive Portfolio Construction" + "Talyxion / risk-managed crypto allocation" · tarih: 2025–2026 · **son 1–3 yıl:** EN sağlam sistematik edge. AdaptiveTrend 150+ parite, 2022–2024 Sharpe ~2.41, maxDD −12.7%; risk-yönetimli trend tahsisi Binance futures Jan2023–Aug2025 Sharpe ~3.02, maxDD ~7.8% (buy-hold'un drawdown'unu yener). · **Framework'le karşılaştırma:** bizim trigger katmanı (MACD/RSI) zaten momentum-yanlı → örtüşür; eksik olan **risk-yönetimli pozisyon tahsisi** (vol-targeting). · **Zayıf nokta:** sonuçlar BACKTEST — bizim disiplinde kanıt DEĞİL; trend rejimi kırılınca whipsaw; çoklu-parite bizde tek-perp (BTC) ile daralıyor.
- **Funding/basis carry** · kaynak: BIS WP 1087 "Crypto carry" + BitMEX 2025 Q2 türev raporu · tarih: 2025 · **son 1–3 yıl:** tarihsel olarak kârlı AMA 2024–25'te funding **bastırılmış** (ekstrem olaylar −%90) → carry kârı **daralmış**. · **Framework'le karşılaştırma:** funding'i zaten maliyet/feature olarak alıyoruz; carry'yi ayrı strateji yapmıyoruz. · **Zayıf nokta:** mevcut düşük-funding rejiminde edge ince; çoğu carry çift-bacak (long+short, çapraz-borsa) ister — tek-perp testnet kapsamımız dışında. **Şimdilik carry'ye bel bağlama.**
- **Overfitting uyarısı (meta)** · kaynak: çoklu (Cointester 2026, stoic.ai) · **bulgu:** %100+ yıllık backtest getirisi, >5–7 parametre, <50 trade, zayıf OOS = overfit işareti. · **Framework'le:** bizim "backtest tuzağı" + win-rate-yok + expectancy-anlamlılığı disiplinlerini DOĞRULAR. Eklenecek kural değil, mevcut disiplinin dış teyidi.

## ⛔ Backtest tuzağı (yapma)
Geçmiş veride strateji **fit/optimize** etmeye kalkma. Sebep: (a) leakage — model cutoff-öncesini bilebilir; (b) overfitting — diziye curve-fit. Bu **aday öğrenim bile değildir, çöptür.** Görürsen `logs/`'a "ders yok — backtest tuzağı" yaz, devam etme.

## Giriş mantığı (taslak — forward veriyle kalibre edilecek)
<!-- Boş: ilk trade'ler + reflection ile dolar. Format: [koşul] → [yön] → [stop/target mantığı] -->

## Stop / pozisyon boyutu
<!-- Boş: ATR-tabanlı stop mesafesi + $ risk kuralı forward veriyle netleşir. -->

## Aday hipotezler (henüz terfi etmedi — PROMOTE-SWEEP bekliyor)
> İki kaynaktan beslenir: (1) **reflection** tek-olay adayları, (2) **dış strateji araştırması** (yukarıdaki bölümden damıtılan). Hepsi **testnet forward'da sınanır**; canlı kurala terfi tekrar paterni + **insan onayıyla**.
<!-- Boş: scan (dış araştırma) + refresh (tek-olay) buraya yazar. Backtest sonucu BURAYA GİRMEZ (tuzak). -->
- **[H-XX]** · kaynak: [reflection trade-id | dış araştırma] · hipotez: [...] · forward-test durumu: [bekliyor/sınanıyor/N trade] · terfi: [hayır — insan onayı bekliyor]
- **[H-01]** · kaynak: dış araştırma (trend-following, 2026-06-13) · **hipotez:** BTC perp'te MACD sinyal-üstü geçiş + fiyat SMA20/50 üstü + funding nötr iken asimetrik long (≈1.6×ATR stop, ≈2.5R hedef) pozitif beklenti verir. · forward-test durumu: **bekliyor** (0 trade — ilk decision aşağıda) · terfi: **hayır** — insan onayı + ~30–50 forward trade anlamlılığı gerekir
- **[H-02]** · kaynak: dış araştırma (vol-targeting, 2026-06-13) · **hipotez:** pozisyon boyutu ATR-ters (volatilite yüksekken küçült) ile ölçeklenirse drawdown düşer. · forward-test durumu: **bekliyor** · terfi: **hayır**
- **[H-03]** · kaynak: forward-test BTC 2026-06-14-BTC-001 (stop_hit derin analizi) · **hipotez:** RSI>65 iken tek bir MACD-cross trigger'ı **geç/düşük-edge** girişdir; **higher-timeframe (4h/günlük) trend bağlamı + çok-varlık rejim** olmadan 1h counter-trend long açmak kaybeder. **Kaçırılan:** edge-kalite değerlendirmesi (trigger fire ≠ edge) + geniş trend. · forward-test durumu: **1 olay (BTC-001) — basit-RSI flat bu trade'i yendi**; tekrar paterni bekliyor · terfi: **hayır** (tek olay, kural değil)
  - ✅ **SİSTEM-GAP KAPATILDI (2026-06-14):** `features/trend.py` eklendi — çok-TF trend (15m/1h/4h/1d) + `market_regime` (broad_bull/bear/mixed) + `is_counter_trend`; snapshot `market_context` taşıyor; trader-scan counter-trend kuralı. **Canlı doğrulama:** o an rejim **BROAD_BEAR** + BTC long **counter-trend=True** → feature olsaydı uyarırdı. (Hipotezin KENDİSİ hâlâ forward-test bekliyor — feature var diye kural terfi etmez.)
