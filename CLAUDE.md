# CLAUDE.md — Trade-Agent Anayasası

> **🧭 SİSTEM GENELİ:** Tek-bakış durum (3 sistem + iki repo + faz + canlı durum) → `../asimetri-vault/STATUS.md`.
>
> Para hareket ettiren kod. **AYRI repo, git gün 1'den.** Obsidian vault'a GİRMEZ.
> Bu bir **ARAŞTIRMA + forward-test** sistemi — "para basan bot" DEĞİL.

---

## Demir disiplinler (DEĞİŞMEZ — değiştirmek insan onayı ister)

1. **TESTNET / PAPER ONLY. GERÇEK PARA YOK.** Hyperliquid testnet veya kâğıt. Order endpoint'i bilerek tanımsız (`hl_client.py` yalnız `/info` read). Gerçek-para gate'i = **pozitif expectancy'nin istatistiksel anlamlılığı** (~30–50 trade) + kontrollü drawdown. Bu gate'i AI açamaz.
   - **OKUMA mainnet, EMİR testnet (KARAR 3).** Fiyat/funding/feature OKUMA'sı **mainnet**'ten gelir (derin likidite → feature kalitesi; testnet ince: saatlik ~0.76 BTC, OI ~71). Bu sadece **public read**, para hareketi YOK. **EMİR/fill yine testnet/paper** — order endpoint hiçbir tabanda tanımlı değil → mainnet emri **imkânsız**. İki şey ayrı: okuma kaynağı ≠ emir hedefi. Testnet okumayı zorlamak: `HL_FORCE_TESTNET_READ=1`. Bu ayrım **gerçek-para gate'ini ve testnet-only emir sınırını DEĞİŞTİRMEZ.**
   - **TRADER OTONOM (testnet), EQUITY insan-kararlı — ayrı felsefe.** Bu repo'da (kripto perp) trader **kendi pozisyonunu açar/kapatır** — `trader-refresh` açık pozisyonu stop/target'a göre KAPATIR, `trader-scan` fırsat varsa AÇAR (hepsi **testnet/paper**, `execution/autonomous.py`). Otonomi gerçek-para gate'ini AÇMAZ (o insan kararı). **Asimetri vault'ta (equity) karar İNSANDA kalır** — orada AI al/sat demez. İki sistem bilinçle farklı: trader testnet'te otonom çünkü dürüst forward-test altyapısı (tez≠fiyat + baseline + anchor) var; equity'de gerçek sermaye + insan tetiği.
   - **ÇOK-VARLIK: BTC · ETH · XRP · HYPE (4 perp).** Başlangıçta tek-perp'ti (INSA-TRADER "tek perp ile başla"); loop sağlamlaştıkça Can kararıyla 4 varlığa genişletildi (2026-06-14). Her tetikte 4'ü de taranır; trigger ateşleyende kod-sınırlı kaldıraçla açılır; varlık-bazlı state (çakışma yok). Eşzamanlı hareket = rejim bağlamı (sinyal değil). Determinism/anchor/testnet-only/over-trading kuralları aynen geçerli.
   - **KARAR LOGLAMA: saat+tarih+detaylı gerekçe.** Her karar `decision.stamp_decision` (UTC `decided_at`) + `detailed_rationale` (ne göz önünde bulunduruldu/eksik) ile yazılır; stop'ta `trader-refresh` DERİN analiz yapar (neyi göremedi, ne kaçırdı). Geriye-dönük analiz için.
   - **KALDIRAÇ kod-sınırlı (`execution/leverage.py`, L-04 risk-boyutlandırma).** SERT TAVAN **5x** (Can kararıyla 3x→5x, 2026-06-15; ajan aşamaz, kod reddeder). Vol-ölçek (ATR ile ters) + güvene bağlı (`low`→~1x, `medium`→≤2x DEĞİŞMEDİ; **5x ANCAK high+düşük-vol+temiz-challenger**) + **likidasyon mesafesi > stop mesafesi** (yoksa stop anlamsız → kod düşürür). Not: deterministik runner yalnız low/medium üretir → pratikte ≤2x (Faz 1 ölçümü izole); 5x tavanı high-güven kurulumlarına açık. `decision.validate_decision` kaldıracı doğrular; `simulator` fee/funding/likidasyon hesabına katar. Yalnız testnet/paper — gerçek para YOK.
   - **ANLIK K/Z + bakiye:** her turda açık pozların mark-to-market gerçekleşmemiş K/Z'si hesaplanır (`run_turn._unrealized`); `equity = balance + ΣK/Z` state'e/runs.jsonl'e/journal'a yazılır → dashboard anlık fiyat + anlık K/Z + anlık bakiye gösterir. `balance` = gerçekleşen (kapanışlarla), `equity` = anlık.
2. **Determinism kodda, judgment LLM'de.** LLM grafik OKUMAZ, indikatör HESAPLAMAZ — structured JSON snapshot alır. Sayısal kesinlik `features/` katmanında.
3. **Point-in-time, look-ahead YOK.** Snapshot "o an bilinen" veriyi verir (`snapshot.build_snapshot` as_of sonrası mumu dışlar). **Hiçbir cutoff-öncesi sonuç performans kanıtı sayılmaz** (sadece plumbing/debug).
   - **Geçmiş-veri KALIN ÇİZGİ:** historical veri YALNIZCA plumbing/debug. Hiçbir geçmiş-veri sonucu performans VEYA öğrenim kanıtı **değildir**. **"Kendini geliştirme" yalnız iki kaynaktan:** (a) **ileri-test (testnet forward)**, (b) **dış strateji araştırması** (disiplin 10). **Geçmişe gidip backtest ile strateji "öğrenmek" YASAK** — leakage (model cutoff-öncesini bilebilir) + overfitting (diziye curve-fit). Ajan geçmiş veride strateji **fit/optimize** etmeye kalkarsa → **DUR, YAPMA**, `logs/`'a **"ders yok — backtest tuzağı"** yaz.
4. **tez ≠ fiyat.** Kârlı trade kötü karar (varyans), stop iyi karar (şans) olabilir. Karar kalitesi ≠ fiyat sonucu. Tek sonuçtan strateji yazılmaz — tekrar paterninden PROMOTE-SWEEP + insan onayı.
5. **Win-rate hedefi YOK.** Asimetrik R:R, pozitif beklenti. Dar TP + geniş SL → felaket kuyruğu (bir likidasyon seriyi siler). Ana metrik: expectancy / profit factor / max DD / Sharpe. Win-rate **tali**.
6. **Trigger-only LLM.** Kod trigger ateşleyince çalışır, her bar'da değil (`triggers/rules.py`). Maliyet + sinyal kalitesi.
7. **Fee + funding + slippage DAHİL.** Sıfır-maliyetli fill yalan üretir (`execution/simulator.py`).
8. **Anchor (asimetrik).** scan kendi eski tezini ham görmez; refresh görür ama savunma değil (log + aday öğrenim), aynı veride yeniden fit etmez.
9. **Uydurma yok.** Sinyal/rakam/sonuç uydurulmaz. On-chain flow ücretsiz kaynağı yok → eksik işaretlenir (`onchain.py available:False`), sahte sinyal üretilmez.
10. **Dış strateji araştırması = HİPOTEZ.** scan agent dış başarılı stratejileri (momentum/trend/funding-basis/on-chain) araştırır, `strategy/`'ye kaynak+tarihle DAMITARAK yazar; bunlar **aday hipotez**tir, doğrudan kural değil. Canlı kurala terfi **yalnız insan onayı** (PROMOTE-SWEEP). Araştırma genel/zamansız bilgidir — point-in-time snapshot'a geleceği SOKMAZ, anchor'ı bozmaz.

---

## 7 katman
1. **Veri** (`data/`) — OHLCV + funding + on-chain (point-in-time). 2. **Feature** (`features/`) — RSI/MACD/ATR/funding/likidite (kod). 3. **Decision agent** (`trader-scan`) — snapshot → JSON tez/entry/stop/target. 4. **Execution sim** (`execution/`) — fee+funding+slippage. 5. **Evaluation** (`evaluation/`) — expectancy/PF/maxDD/Sharpe. 6. **Reflection agent** (`trader-refresh`) — neden + aday öğrenim. 7. **Strateji doc** (`strategy/`) — yavaş evrilen.

## İki agent + tek challenger (OTONOM, testnet)
- `trader-scan` (otonom decision, **analyst**) — anchor-free, point-in-time, trigger-only. Fırsat varsa **testnet pozisyon AÇAR** (`autonomous.opportunity_gate`). **+ strateji-araştırma.**
- `trader-refresh` (otonom pozisyon yöneticisi) — açık pozisyonu kontrol eder; stop/target değdiyse **testnet KAPATIR** + sonuç + tez≠fiyat (etiket YASAK). Eski tezi görür ama savunma değil.
- `challenger` (**tek** karşı-tez lensi) — analyst tezini açmadan ÖNCE çürütür; **kendi pozisyon açmaz**, boş itiraz yok, farklı lens.
- **Sıralama:** refresh açık pozisyonu kontrol/kapatır → SONRA scan (fırsat varsa) açar (çakışan pozisyon yok, state tek kaynak = journal).

## 🅰️🅱️ A/B MİMARİSİ (2026-06-15 — KURAL vs LLM, hangisi daha iyi VERİYLE)
> Hedef: otonom kripto trader. Hangi karar mekanizması daha iyi BİLMİYORUZ → **A/B testi.**
> İki agent paralel, **aynı snapshot**, **ayrı $4000 bakiye**, **ayrı state/runs/journal**, **AYNI sizing**. ~30+ trade sonra VERİYLE karşılaştır.

- **deterministic-trader** (`run_deterministic.py`) — kural-bazlı (RSI/MACD/trend/rejim, LLM YOK). `positions_deterministic.json` + `runs_deterministic.jsonl`.
- **deep-thinker** (`.claude/agents/deep-thinker.md` + `apply_deepthinker.py`) — LLM-in-the-loop (analyst→challenger→karar), **otonom** (kendi uygular), **turlar arası ÖĞRENMEZ** (sabit kurallar; öğrenme A/B sonucundan+insandan). `positions_deepthinker.json` + `runs_deepthinker.jsonl`.
- **Motor ORTAK** (`run_turn.py`): snapshot, path-check kapatma, **risk-bazlı sizing** (`sizing.py`), kaldıraç (`leverage.py`), P&L, log. TEK fark = açma kararı (decider).
- **İZOLASYON:** her agent yalnız kendi state/runs/journal'ına yazar; diğerinin sermayesine ASLA dokunmaz (`test_isolation.py` garanti).
- **SİZİNG (ikisi de AYNEN — `sizing.py`, ayarlanabilir başlangıç eşiği):** trade başına maks kayıp **%1.5×bakiye** (notional = risk$/stop_mesafe); tek poz ≤ **%30** bakiye; **%100 teminat-guard** (kilitli margin ≤ bakiye); serbest-bakiye-farkında; GERÇEKLEŞEN bakiye üzerinden. Kaldıraç serbest seçilmez (koddan).
- **Çatı/tetik = Claude Code routine** (`ROUTINE.md`) — Actions'ta Claude yok → A/B süresince **GitHub schedule KALDIRILDI**; tek canonical tetik routine (capture_snapshot → run_deterministic + deep-thinker, aynı snapshot). Cadans 100dk.
- **Sayaç:** iki AYRI forward-test sayacı (~30 her biri). deep-thinker STOKASTİK → **30 MİNİMUM**, fazlası daha güvenilir.
- **⚠️ BAŞLANGIÇ ASİMETRİSİ (A/B YAKLAŞIK, kesin değil):** deterministic MEVCUT state'iyle başladı ($4087 + 4 açık poz, eski sabit-$1000 sizing'le açılmış); deep-thinker temiz $4000 + 0 poz + yeni risk-sizing. Yeni sizing yalnız BUNDAN SONRAki trade'lere uygulanır. Sonuç okunurken bu asimetri göz önünde tutulur.
- **CAPITAL-reset notu:** CAPITAL 1000→4000 geçişi pozisyon-boyutu MANTIĞINI değiştirmedi (her poz zaten 1000 baz alıyordu = etiket düzeltmesi); **risk-bazlı sizing eklenmesi = yeni sistem başlangıcı.**
- **🔁 SİMETRİ — long + short (2026-06-16, Can onayı):** İkisi de AYNI aksiyon uzayı (long+short), TEK fark karar mekanizması. **deterministic yön = HTF trend** (`is_counter_trend` ZATEN simetrik: buy+HTF-down=counter, sell+HTF-up=counter; **keyfi eşik YOK** — short = long'un birebir simetrik tersi). **range-HTF → WAIT** (yönsüz edge yok; eski gizli long-bias kaldırıldı); HTF-çatışma → WAIT. deep-thinker long+short serbest (yönü HTF+momentum ile akıl yürütür, counter-trend açmaz, short sıralama `target<entry<stop`). **fwd 0'dan başladı** (her iki state); **long-only dönem** (det fwd≤7, deep≤1) `era:"long_only"` etiketiyle ARŞİVDE (runs/journal SİLİNMEDİ); açık long pozlar kapanınca yeni fwd'yi kirletmez. **Faz-1 içinde bilinçli aksiyon-uzayı genişlemesi** — veri azken yapıldı, sayaç yeniden başladı (motor short'u zaten destekliyordu; yalnız karar mantığı + deep-thinker talimatı değişti).

## Analyst↔Challenger akışı (otonom — açmadan ÖNCE adversarial kapı)
1. **trader-scan** decision tezi üretir (JSON, kod-validate). 2. **challenger** çürütür (farklı lens) → "Challenger" bölümü. 3. **trader-scan** tek tek cevap + rafine tez; **orijinal+itiraz+cevap görünür** (retro). 4. **Challenger ciddi kırılma bulduysa → tez geçersiz say (`opportunity_gate` 'wait'), AÇMA.** Aksi halde **agent testnet'te AÇAR** (otonom). *(Equity'den fark: orada adım 4 = insan kararı; burada = agent testnet'te kendi açar — gerçek para YOK.)*
- **Ownership:** "Challenger" bölümü = challenger · tez + "Analyst cevabı" = trader-scan · son karar = insan · strateji dokümanı = refresh/insan · feature/metrik = kod.

## Veri/forward-test sıralaması (leakage öldür)
1. Cutoff-öncesi historical → SADECE plumbing/debug (performans kanıtı DEĞİL — leakage). 2. Cutoff-sonrası historical → zayıf pseudo-validation. 3. **Testnet forward → gerçek sınav.**

## GELİŞİM DÖNGÜSÜ (dönemsel — ölç→öğren→veriyle-değiştir→tekrar-ölç)
> Sürekli ekleme (forward-test bozulur) ile hiç-dokunmama (toy sistem) ARASINDA. Sistem gelişir AMA her değişiklik **veriye** dayanır, hevese DEĞİL. **ŞU AN: FAZ 1** (`state/positions.json` `phase`).

> **🧭 ÇEKİRDEK FELSEFE:** Olduğumuz nokta önemli değil — önemli olan her gün sistemi **ÖLÇEREK** geliştirmek. Sabit gelir sürekli iyileştirmeden gelir. **KRİTİK NÜANS:** iyileştirme = değişiklik **+ ÖLÇÜM**, sadece değişiklik DEĞİL. Sürekli yeni yetenek eklersen fwd hep sıfırlanır, baseline oturmaz, hangi değişikliğin işe yaradığını ÖLÇEMEZSİN. Disiplin: bir değişiklik → **stabilize et → veri topla → işe yaradı mı ÖLÇ → sonra sıradaki.** Yaşayan sistem = **ölçerek evrilen** sistem, sürekli değişen değil.

**KRİTİK KURAL:** Bir faz **İÇİNDE** konfigürasyon SABİT (yoksa o fazın verisi izole edilemez). Değişiklik **faz GEÇİŞLERİNDE**, veriye dayalı. *"Faz içinde heves-ekleme" YASAK; "faz geçişinde veri-değişiklik" beklenen.*

**FAZ 1 — TEMEL ÖLÇÜM** (mevcut ~30 trade, config SABİT):
- Mevcut faktör seti (RSI/MACD/ATR/funding/trend/rejim) **sabit** — amaç bir BAŞLANGIÇ NOKTASI ölçmek (baseline'ı yeniyor mu, expectancy ne, hangi aday tekrarlıyor). Sabit olmazsa sonraki gelişmelere referans olmaz.
- **Yeni faktör EKLENMEZ.** Ama **TÜM ham veri loglanır** (OI/premium/oracle — `runs.jsonl` `raw_unused`, **karara GİRMEZ**), Faz 2 geriye-dönük testi için.
- Aday faktörler (`strategy/candidate-factors.md`: F-01/F-02/F-03) + aday dersler (`_strategy.md`: H-03) candidate dosyalarında **birikir** (uygulanmaz).

**FAZ 2 — VERİYLE GELİŞİM** (~30 trade sonra, faz geçişi):
- Değerlendir: (a) mevcut sistem baseline'ı (B&H+RSI) **fee-net yendi mi**? (b) aday faktörler **loglanan ham veride geriye-dönük test** — "katsaydık iyileşir miydi?" (c) tekrarlayan aday dersler **kanıtlandı mı** → kurala terfi (d) zayıf/işe yaramayan faktör → **çıkar**.
- Sistem BURADA DEĞİŞİR — ama her değişiklik yukarıdaki **veriye** dayanır. İşe yaradığı **GÖSTERİLEN** faktör eklenir; gösterilemeyen beklemede kalır.
- Değişiklikten sonra **yeni sabit dönem** başlar (~20-30 trade), yeni halin etkisi ölçülür.

**FAZ 3+ — TEKRAR:** her dönem ölç→öğren→değiştir→sabit-dön→tekrar-ölç. 6 ayda 3-4 döngü.

**İNSAN DENETİMİ (her 2-3 günde):** aday dersleri oku (**gerçek / hindsight / overfit** ayır), sayaç + baseline + fee kontrol, anomali bak. **Faz geçiş kararı İNSANIN.** (Faz geçişi = config değişikliği = safeguard kapısı; AI otonom geçmez.)

## Otonom protokol
İmplementasyon boşluğu (kütüphane, free API, bug) → internette araştır, doldur, devam; kaynağı + kararı `logs/`'a yaz. **Çekirdek disiplin / mimari / güvenlik sınırı (yukarıdaki 1–9) → değiştirmeden ÖNCE DUR + Can'a sor.** Esnek plumbing'de, sabit safeguard'larda.

## Rapor formatı
İş sırasında tek satırlık faz güncellemeleri; sonda tek nihai rapor (sade-Türkçe özet + katman tablosu + test sonuçları + veri durumu + "Can kararı bekleyenler").

## 🧠 HAFIZA İLKESİ (kararlar DOSYADA yaşar, sohbette değil)
Vault (equity) ve trade-agent (kripto) **AYRI repo — yapısal duvar:** otomatik saatlik push equity geçmişini kirletmesin, erişim/izin ayrı kalsın, trader equity'ye yazamasın. **AMA kararlar + hafıza HER İKİSİNDE dosyalarda CANLI yaşar** — sohbet/context silinse de `CLAUDE.md` / `_strategy.md` / `lessons.md` / `candidate-factors.md` / `journal`'da kalır. **Her önemli karar ilgili dosyaya yazılır; hafıza sohbette değil DOSYADA yaşar.**
