# CLAUDE.md — Trade-Agent Anayasası

> Para hareket ettiren kod. **AYRI repo, git gün 1'den.**
> Bu bir **ARAŞTIRMA + forward-test** sistemi — "para basan bot" DEĞİL.
> Kripto perp (BTC · ETH · XRP · HYPE), Hyperliquid. **TESTNET / PAPER — GERÇEK PARA YOK.**

---

## Demir disiplinler (DEĞİŞMEZ — değiştirmek insan onayı ister)

1. **TESTNET / PAPER ONLY. GERÇEK PARA YOK.** Order endpoint'i bilerek tanımsız (yalnız `/info` read). Gerçek-para gate'i = **pozitif expectancy'nin istatistiksel anlamlılığı** (~30–50 trade) + kontrollü drawdown. Bu gate'i AI açamaz.
   - **OKUMA mainnet, EMİR testnet.** Fiyat/funding/feature OKUMA'sı **mainnet**'ten (derin likidite → feature kalitesi). Bu sadece public read, para hareketi YOK. **EMİR/fill yine testnet/paper** — order endpoint hiçbir tabanda tanımlı değil → mainnet emri imkânsız. Okuma kaynağı ≠ emir hedefi.
   - **ÇOK-VARLIK: BTC · ETH · XRP · HYPE (4 perp).** Her tetikte 4'ü de taranır; trigger ateşleyende kod-sınırlı kaldıraçla açılır; varlık-bazlı state (çakışma yok). Eşzamanlı hareket = rejim bağlamı (sinyal değil).
   - **KARAR LOGLAMA: saat+tarih+detaylı gerekçe.** Her karar `decision.stamp_decision` (UTC `decided_at`) + `detailed_rationale` (ne göz önünde bulunduruldu/eksik) ile yazılır.
   - **KALDIRAÇ kod-sınırlı (`execution/leverage.py`).** SERT TAVAN **5x** (ajan aşamaz, kod reddeder). Vol-ölçek (ATR ile ters) + güvene bağlı (`low`→~1x, `medium`→≤2x; **5x ANCAK high+düşük-vol+temiz-challenger**) + **likidasyon mesafesi > stop mesafesi** (yoksa kod düşürür). `decision.validate_decision` kaldıracı doğrular; `simulator` fee/funding/slippage'i hesaba katar.
   - **ANLIK K/Z + bakiye:** her turda açık pozların mark-to-market gerçekleşmemiş K/Z'si; `equity = balance + ΣK/Z`. `balance` = gerçekleşen, `equity` = anlık.
2. **Determinism kodda, judgment LLM'de.** LLM grafik OKUMAZ, indikatör HESAPLAMAZ — structured JSON snapshot alır. Sayısal kesinlik `features/` katmanında.
3. **Point-in-time, look-ahead YOK.** Snapshot "o an bilinen" veriyi verir (as_of sonrası mumu dışlar). Hiçbir cutoff-öncesi sonuç performans kanıtı sayılmaz.
   - **Geçmişe gidip backtest ile strateji "öğrenmek" YASAK** — leakage + overfitting. "Kendini geliştirme" yalnız (a) **testnet forward** + (b) **dış strateji araştırması**. Backtest'e kalkılırsa → DUR, `logs/`'a "ders yok — backtest tuzağı" yaz.
4. **tez ≠ fiyat.** Kârlı trade kötü karar (varyans), stop iyi karar (şans) olabilir. Tek sonuçtan strateji yazılmaz — tekrar paterni + insan onayı (PROMOTE-SWEEP).
5. **Win-rate hedefi YOK.** Asimetrik R:R, pozitif beklenti. Dar TP + geniş SL → felaket kuyruğu. Ana metrik: expectancy / profit factor / max DD / Sharpe.
6. **Trigger-only LLM.** Kod trigger ateşleyince çalışır, her bar'da değil (`triggers/rules.py`).
7. **Fee + funding + slippage DAHİL.** Sıfır-maliyetli fill yalan üretir (`execution/simulator.py`).
8. **Anchor (asimetrik).** scan kendi eski tezini ham görmez (anchor-free); refresh görür ama savunma değil (log + aday öğrenim), aynı veride yeniden fit etmez.
9. **Uydurma yok.** Sinyal/rakam/sonuç uydurulmaz. On-chain flow ücretsiz kaynağı yok → eksik işaretlenir (`data/onchain.py available:False`), sahte sinyal üretilmez.
10. **Dış strateji araştırması = HİPOTEZ.** Dış stratejiler `strategy/`'ye kaynak+tarihle DAMITARAK yazılır; aday hipotezdir, kural değil. Terfi yalnız insan onayı.

---

## 7 katman
1. **Veri** (`data/`) — OHLCV + funding + on-chain proxy (point-in-time, `snapshot.py`).
2. **Feature** (`features/`) — RSI/MACD/ATR/SMA/EMA + trend/rejim (kod).
3. **Decision** — A: `run_deterministic.py` (kural) · B: `deep-thinker` (LLM analyst→challenger).
4. **Execution sim** (`execution/`) — sizing + leverage + fee/funding/slippage'li fill.
5. **Evaluation** (`evaluation/metrics.py`) — expectancy / PF / maxDD / Sharpe + baseline.
6. **Reflection** (`trader-refresh`) — sonuç → neden + aday öğrenim.
7. **Strateji doc** (`strategy/`) — yavaş evrilen, insan-okunur.

---

## 🅰️🅱️🅲️ A/B/C mimarisi (KURAL vs LLM vs AGGRESSIVE — hangisi daha iyi VERİYLE)
Üç agent paralel, **aynı snapshot**, **ayrı $4000 bakiye**, **ayrı state/runs**, **TAM İZOLE**. ~30+ trade sonra karşılaştır.
- **A — deterministic-trader** (`run_deterministic.py`): kural-bazlı (RSI/MACD/trend/rejim, LLM YOK). Sizing %1.5 risk / %30 poz / ≤5x.
- **B — deep-thinker** (`.claude/agents/deep-thinker.md` + `run_deepthinker.py` + `apply_deepthinker.py`): LLM-in-the-loop (analyst→challenger→karar), **otonom**, **turlar arası ÖĞRENMEZ**. A ile AYNI sizing (tek fark karar mekanizması).
- **C — aggressive-trader** (`run_aggressive.py`): A ile AYNI kural mantığı AMA yüksek-risk profili (%5 risk / %100 poz / ≤20x + likidasyon kapısı). Soru: yüksek risk/kaldıraç conservative kolları yener mi? A/B'nin sizing-fairness'ını bozmaz (C ayrı deney).
- **Motor ORTAK** (`run_turn.py`): snapshot, path-check kapatma, **risk-bazlı sizing** (`execution/sizing.py`), kaldıraç (`execution/leverage.py`), P&L, log. TEK fark = açma kararı.
- **SİZİNG (ikisi de AYNEN):** trade başına maks kayıp **%1.5×bakiye** (notional = risk$/stop_mesafe); tek poz ≤ **%30** bakiye; **%100 teminat-guard**; gerçekleşen bakiye üzerinden. Kaldıraç serbest seçilmez (koddan).
- **🔁 SİMETRİ — long + short:** İkisi de AYNI aksiyon uzayı. **deterministic yön = HTF trend** (`is_counter_trend` simetrik). **range-HTF → WAIT**. deep-thinker long+short serbest (counter-trend açmaz; short sıralama `target<entry<stop`).

---

## GELİŞİM DÖNGÜSÜ (ölç→öğren→veriyle-değiştir→tekrar-ölç)
> **ŞU AN: FAZ 1.** Sürekli ekleme (forward-test bozulur) ile hiç-dokunmama arasında. Her değişiklik **veriye** dayanır, hevese değil.

**KRİTİK KURAL:** Bir faz **İÇİNDE** konfigürasyon SABİT (yoksa o fazın verisi izole edilemez). Değişiklik **faz GEÇİŞLERİNDE**, veriye dayalı.

- **FAZ 1 — TEMEL ÖLÇÜM:** mevcut faktör seti (RSI/MACD/ATR/funding/trend/rejim) sabit; ~30 trade baseline. Yeni faktör EKLENMEZ ama tüm ham veri loglanır (Faz 2 geriye-dönük testi). Aday faktörler/dersler candidate dosyalarında birikir (uygulanmaz).
- **FAZ 2 — VERİYLE GELİŞİM:** baseline (B&H+RSI) fee-net yenildi mi? Aday faktörler ham veride test; tekrarlayan dersler kanıtlandıysa terfi; zayıf faktör çıkar.
- **FAZ 3+ — TEKRAR.** İnsan denetimi (her 2-3 günde): aday dersleri ayır (gerçek/hindsight/overfit), sayaç+baseline+fee kontrol. **Faz geçiş kararı İNSANIN.**

---

## Otonom protokol
İmplementasyon boşluğu (kütüphane, free API, bug) → araştır, doldur, devam; kararı `logs/`'a yaz. **Çekirdek disiplin / mimari / güvenlik sınırı (1–10) → değiştirmeden ÖNCE DUR + insana sor.**

## 🧠 Hafıza ilkesi (kararlar DOSYADA yaşar, sohbette değil)
Her önemli karar ilgili dosyaya yazılır — sohbet/context silinse de `CLAUDE.md` / `strategy/_strategy.md` / `lessons.md` / `candidate-factors.md` / `journal`'da CANLI kalır.

## Çalıştırma
Saatlik **lokal launchd** (`com.trade-agent.turn` → `run_turn.sh`) — yalnız PC/Claude açıkken. Akış: `ROUTINE.md`. deep-thinker LLM = `ANTHROPIC_API_KEY` (SDK, `.env`).
