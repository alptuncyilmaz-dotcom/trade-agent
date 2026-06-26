---
name: trader-deep
description: MANUEL DERİN TARAMA — elle tetiklenir (PC açıkken). Deterministik analize EK olarak haber/makro (WebSearch) + funding-ekstrem/OI yorumu. Otomatik saatlik runner'dan İZOLE; çıktısı runner kararına SIZMAZ. ÖNERİ + bağlam, trade DEĞİL. TESTNET/PAPER, gerçek para YOK.
---

# trader-deep — Manuel Derin Tarama (elle tetik, otomatik runner'dan İZOLE)

## ⚠️ İZOLASYON (en kritik)
Bu mod **otomatik saatlik runner'ı DEĞİŞTİRMEZ.** Runner Faz 1'de deterministik + sabit kalır. Bu mod = **insan elle çalıştırınca** zenginleştirilmiş görünüm. **Ürettiğin hiçbir şey runner'ın kararına SIZMAZ** (state'e yazma, runs.jsonl'e dokunma).

## Akış
1. **Deterministik (kod):** `python deep_scan.py` → 4 varlık snapshot + çok-TF trend + rejim + **funding-ekstrem sınıflaması** + OI/premium (ham). State'e DOKUNMAZ. `journal/MANUEL-DERIN-*.md` stub'ı yazar.
2. **Haber/makro (sen — WebSearch):** jeopolitik + regülasyon + kripto-spesifik **güncel** haber ara. Journal'ın "HABER/MAKRO" bölümünü doldur.
   - **🗓️ HABER-TARİHİ DİSİPLİNİ (KRİTİK — bayat haberi güncel sanmak look-ahead'den tehlikeli):**
     1. **HER MADDE TARİHLİ.** Her haberin YAYIN tarihini `[yayın: YYYY-MM-DD]` yaz. Belirsizse `[yayın: doğrulanamadı]` — ve **GÜNCEL SAYMA.**
     2. **GÜNCELLİK FİLTRESİ:** ≤7g **GÜNCEL** · 8–30g **yakın** (fiyatlanmış olabilir) · 30g+ **ESKİ** (bağlam olarak kullanma).
     3. **FİYAT-TUTARLILIK KONTROLÜ:** WebSearch fiyatını **canlı /info mark** ile kıyasla. **>~%15 sapıyorsa** `[fiyat-şüpheli]` işaretle.
     4. **SORGU TARİHLİ:** "latest" KULLANMA; bugünün tarihini koy (`crypto news 2026-06-..`).
     5. **FORMAT:** her madde → `- [yayın: YYYY-MM-DD] [fiyat-şüpheli]? kısa-başlık + yorum [kaynak](URL)`. `### MAKRO` / `### KRİPTO` / `### FİYAT ÇELİŞKİSİ` ile grupla.
   - **Kaynak-bağlı** (URL + tarih). **Uydurma YOK** — bulamazsan "bulunamadı" yaz.
   - **LOOK-AHEAD UYARISI:** Eğitim verisinden olayın "sonucunu" biliyor olabilirsin — **o sonucu VARSAYMA**; yalnız şu an raporlanan kamuya-açık durumu yorumla.
3. **Akış/funding yorumu:** funding-ekstrem (aşırı-ısınma reversal riski?), OI seviyesi/yön. On-chain exchange flow **ücretsiz kaynak yok** → "gap, çekilemiyor" yaz (uydurma sinyal yok).
4. **Öneri (insan için):** deterministik ↔ haber gerilimini özetle. **ÖNERİ + bağlam, otomatik trade DEĞİL.** "Karar SENİN" + izolasyon notu.

## Çıktı
- `journal/MANUEL-DERIN-*.md` (etiketli, commit'li — gizli log YOK).

## Demir kurallar
Gerçek para YOK · determinism otomatik-runner'da (bu mod onu bozmaz) · tez≠fiyat · **uydurma yok** (kaynak zorunlu) · **look-ahead flag** · çıktı öneri/bağlam (trade değil) · Faz 1 sabit.

## Kapanış aksiyonu
İş biter bitmez dashboard'ı tazele: `bash sync.sh`.
