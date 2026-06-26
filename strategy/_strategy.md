# strategy/_strategy.md — Yaşayan Strateji Dokümanı (v0.1)

> 7. katman: yavaş evrilen, insan-okunur strateji + stop + giriş mantığı.
> **Trade'ler her zaman taze forward veride; bu doküman birikimli öğrenme.** Bu ayrım overfitting'i engeller.
> Reflection ÖNERİR, insan ONAYLAR. **Aktif dersler (graduate olmuş):** `strategy/lessons.md`. Bu doküman aday hipotez.

## Durum: FAZ 1 (temel ölçüm)
Doküman ilk testnet trade'lerinden + reflection'dan dolar. **Uydurma kural eklenmez.**

## Çekirdek ilkeler (değişmez — disiplinden gelir)
- **Asimetrik R:R.** Geniş hedef / dar stop mantığı. Dar TP + geniş SL YASAK (felaket kuyruğu).
- **Win-rate hedefi YOK.** Pozitif expectancy + kontrollü drawdown.
- **Trigger-only giriş.** `triggers/rules.py` ateşlemeden işlem yok.
- **4 perp (BTC/ETH/XRP/HYPE).** Varlık-bazlı state, çakışma yok.
- **Funding maliyettir.** Uzun tutuşta funding'i tez gerekçesine kat.
- **Öğrenme yalnız iki kaynaktan:** (a) testnet forward, (b) dış strateji araştırması. **Geçmiş veride backtest YASAK** (leakage + overfitting → "backtest tuzağı").

## Dış strateji araştırması (deep-thinker/scan doldurur — DAMITARAK)
> Araştırılan strateji = **HİPOTEZ**, kural değil. Kaynak+tarihle damıtılır, "Aday hipotezler"de ileri-teste sokulur.

- **Time-series / trend-following momentum** · kaynak: arXiv sistematik trend-following + risk-yönetimli kripto tahsisi · tarih: 2025–2026 · **son 1–3 yıl:** en sağlam sistematik edge (backtest Sharpe ~2.4–3.0, maxDD daha düşük). · **karşılaştırma:** trigger katmanımız (MACD/RSI) momentum-yanlı → örtüşür; eksik = **risk-yönetimli pozisyon tahsisi** (vol-targeting). · **zayıf nokta:** sonuçlar BACKTEST (bizde kanıt değil); rejim kırılınca whipsaw.
- **Funding/basis carry** · kaynak: BIS WP "Crypto carry" + türev raporları · tarih: 2025 · **son 1–3 yıl:** tarihsel kârlı AMA 2024–25 funding bastırılmış → carry daralmış. · **karşılaştırma:** funding'i zaten maliyet/feature olarak alıyoruz; carry'yi ayrı strateji yapmıyoruz. · **zayıf nokta:** çoğu carry çift-bacak/çapraz-borsa ister — kapsamımız dışı. **Carry'ye bel bağlama.**
- **Overfitting uyarısı (meta)** · kaynak: çoklu · **bulgu:** %100+ backtest getirisi, >5–7 parametre, <50 trade, zayıf OOS = overfit. · **karşılaştırma:** "backtest tuzağı" + win-rate-yok disiplinlerimizi DOĞRULAR (dış teyit, yeni kural değil).

## ⛔ Backtest tuzağı (yapma)
Geçmiş veride strateji fit/optimize etme: (a) leakage — model cutoff-öncesini bilebilir; (b) overfitting — diziye curve-fit. Bu **çöptür.** Görürsen `logs/`'a "ders yok — backtest tuzağı" yaz, devam etme.

## Giriş mantığı (taslak — forward veriyle kalibre)
<!-- [koşul] → [yön] → [stop/target mantığı]. İlk trade'ler + reflection ile dolar. -->
- Mevcut: trigger = (RSI ekstrem) ∧ (MACD cross teyitli); yön = HTF trend (counter-trend açma); stop ≈ 1.5×ATR, target ≈ 3.0×ATR (asimetrik R:R).

## Stop / pozisyon boyutu
- Sizing = risk-bazlı (%1.5/stop-mesafe), %30 poz tavanı, %100 teminat-guard (`execution/sizing.py`). Kaldıraç kod-sınırlı (`leverage.py`, ≤5x, vol+güven+likidasyon).

## Aday hipotezler (terfi etmedi — PROMOTE-SWEEP bekliyor)
> (1) reflection tek-olay adayları, (2) dış araştırma damıtması. Hepsi testnet forward'da sınanır; terfi tekrar paterni + insan onayı. Backtest sonucu BURAYA GİRMEZ.
- **[H-01]** · kaynak: dış araştırma (trend-following) · **hipotez:** MACD sinyal-üstü geçiş + fiyat SMA20/50 üstü + funding nötr iken asimetrik long pozitif beklenti. · durum: **bekliyor** · terfi: hayır (insan onayı + ~30–50 trade).
- **[H-02]** · kaynak: dış araştırma (vol-targeting) · **hipotez:** pozisyon boyutu ATR-ters ölçeklenirse drawdown düşer. · durum: bekliyor · terfi: hayır.
- **[H-03]** · kaynak: forward-test BTC-001 (stop derin analiz) · **hipotez:** RSI>65 tek MACD-cross = geç/düşük-edge; HTF trend+rejim olmadan 1h counter-trend long kaybeder. · durum: 1 olay · terfi: hayır. ✅ sistem-gap kapatıldı (`features/trend.py`); hipotez hâlâ forward-test bekliyor.
