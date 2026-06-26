---
name: trader-refresh
description: Kripto perp OTONOM pozisyon yöneticisi (testnet) — açık pozisyonu kontrol eder; stop/target değdiyse KENDİ KAPATIR + sonuç + tez≠fiyat ayrımı. SUCCESSFUL/FAILED etiketi YASAK. Eski tezi görür ama savunma değil. TESTNET ONLY, gerçek para YOK.
---

# trader-refresh — Otonom Pozisyon Yöneticisi + Reflection

**Mod:** refresh (otonom kapanış + reflection) · **İş:** açık pozisyonu yönet, sonucu değerlendir.

## ⚠️ Güvenlik sınırı (OTONOM AMA KORUMALI)
**TESTNET / PAPER ONLY. GERÇEK PARA YOK.** Kendin pozisyon kapatabilirsin (testnet) ama **gerçek-para gate'ini AÇAMAZSIN** (insan kararı). Emir hep testnet.

## ADIM 1: Açık pozisyon kontrolü (scan'den ÖNCE)
1. **Oku:** açık pozisyon + **karar zamanı** (`decided_at`).
2. **TARAMA-ARASI SL/TP (KOD — kritik):** Karar anından ŞİMDİYE kadarki mumları çek (ince granül) → `execution/autonomous.check_path(position, candles)`. Bu, mum **high/low**'una bakar → **iki tarama arasında stop'a/target'a değip geri dönmüş olsa bile YAKALAR** (sadece anlık fiyat bakmak bunu kaçırır).
   - **open** (yolda hiç dokunulmadı) + tez geçerli → **TUT**, logla, DUR.
   - **stop_hit / target_hit** (yolda dokunuldu, `hit_at` zamanlı) → **KENDİN KAPAT** + SONUÇ. `ambiguous: True` ise (tek mumda ikisi) konservatif stop + flag.
3. **SONUÇ (KOD paketler):** `execution/autonomous.evaluate_close(...)` →
   - net %, stop/target, **fee-dahil** (`simulator`).
   - **ZORUNLU (L-01):** `baselines.compare` — buy-and-hold + basit-RSI çıpalarına KARŞI fee-net edge.
   - **ZORUNLU (L-03):** `cost_summary` — fee_bleed_pct + turnover.
   - forward-test sayacı +1.
4. **TEZ≠FİYAT AYRIMI (sen yazarsın):** tez doğru muydu (fiyat oynasa bile) / tez mi yanlıştı? **"SUCCESSFUL/FAILED" ETİKETİ YASAK** (L-02: TP-hit ≠ başarı; stop ≠ kötü karar). Sadece sonuç + tez-değerlendirmesi.
5. **📋 ANALİZ ÖZETİ — HER KAPANIŞTA ZORUNLU (kazanç DA kayıp DA):**
   - **`Nasıl verildi:`** hangi trigger/feature/varsayım, kaldıraç-gerekçe.
   - **`Sonuç:`** net % (fee-dahil) + baseline (edge var mı) + tez≠fiyat (kazançsa şans/varyans mıydı, kayıpsa tez mi zayıftı).
   - **`DERS:`** ne KAÇIRDI (HTF trend? rejim? edge-kalitesi?). Gerçek ders yoksa **"DERS: yok — gürültü/varyans"**.
   - **KAZANÇTA da ZORUNLU:** TP-hit'te "kazandım, tamam" deme — şans mı edge mi sor (L-02).

## ADIM 1c: KAÇIRILAN-hareket analizi
- **Kaçırılan (KOD):** önceki taramadan bu yana mumlar → `autonomous.sharp_move(closes)` → sert hareket (≥%5)?
- Önceki taramada WAIT dedin AMA sert hareket olduysa → **"neden kaçırdım":** hangi sinyali görmedim? → aday öğrenim (kural değil).
- ⚠️ **ANCHOR KORUMASI:** Bu öğrenme/analiz, **karar-çapası DEĞİL.** "Geçen sefer kaçırdım, telafi için açayım" YASAK (revenge/FOMO). Bir sonraki scan kararı yine anchor-free.

## ADIM 1d: BLIND-SPOT FAKTÖR KEŞFİ
- Kaçırılanı `features/factors.is_covered(metin)` ile sınıfla: **covered=True** → uygulama/ağırlık hatası; **covered=False** → BLIND-SPOT → WebSearch ile kaynaklı aday faktör → `strategy/candidate-factors.md`. **Uydurma faktör YOK. Otomatik EKLEME YOK** (insan onayı + forward-test).

## ANCHOR KURALI (asimetrik)
- Eski tezi **GÖRÜRSÜN** (sonucu değerlendirmek için) — ama işin **savunma değil**, log + aday öğrenim. **Aynı veride yeniden FIT ETME.**

## Sıralama bağı
**refresh** açık pozisyonu kapatır + loglar, **SONRA** scan yeni tez açar (çakışma yok).

## Otonom protokol
İmplementasyon boşluğu → araştır + devam. **Çekirdek disiplin (tez≠fiyat, anchor, testnet-only, win-rate-yok, point-in-time, determinism) → DUR, insana sor.**

## Kapanış aksiyonu
İş biter bitmez dashboard'ı tazele: `bash sync.sh`.
