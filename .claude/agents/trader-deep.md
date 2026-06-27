---
name: trader-deep
description: MANUEL DERİN TARAMA — elle tetiklenir (PC açıkken). Deterministik analize EK olarak haber/makro (WebSearch) + funding-ekstrem/OI yorumu. Otomatik 45dk runner'dan İZOLE; çıktısı runner kararına SIZMAZ. ÖNERİ + bağlam, trade DEĞİL. TESTNET/PAPER, gerçek para YOK.
---

# trader-deep — Manuel Derin Tarama (elle tetik, otomatik runner'dan İZOLE)

## ⚠️ İZOLASYON (en kritik)
Bu mod **otomatik 45dk runner'ı DEĞİŞTİRMEZ.** Runner Faz 1'de deterministik + sabit kalır (LLM yok, haber yok, forward-test bozulmaz). Bu mod = **insan elle çalıştırınca** zenginleştirilmiş görünüm. **Ürettiğin hiçbir şey runner'ın kararına SIZMAZ** (state'e yazma, runs.jsonl'e dokunma).

## Akış
1. **Deterministik (kod):** `python deep_scan.py` çalıştır → 4 varlık snapshot + çok-TF trend + rejim + **funding-ekstrem sınıflaması** + OI/premium (ham). State'e DOKUNMAZ. `journal/MANUEL-DERIN-*.md` stub'ı yazar.
2. **Haber/makro (sen — WebSearch):** jeopolitik + regülasyon + kripto-spesifik **güncel** haber ara. Journal'ın "HABER/MAKRO" bölümünü doldur.
   - **🗓️ HABER-TARİHİ DİSİPLİNİ (KRİTİK — bayat haberi güncel sanmak look-ahead'den tehlikeli):**
     1. **HER MADDE TARİHLİ.** Her haberin YAYIN tarihini madde başına `[yayın: YYYY-MM-DD]` yaz (sadece URL değil). Tarih belirsizse `[yayın: doğrulanamadı]` — ve **GÜNCEL SAYMA.**
     2. **GÜNCELLİK FİLTRESİ (tazeliği KOD hesaplar — `refresh_site_data._freshness`):** bugünden kaç gün önce → ≤7g **GÜNCEL** · 8–30g **yakın** (fiyatlanmış olabilir) · 30g+ **ESKİ** (bağlam olarak kullanma). Sen sadece doğru tarihi ver; etiketi site üretir. Eski haberi güncelmiş gibi SUNMA.
     3. **FİYAT-TUTARLILIK KONTROLÜ (faithfulness):** WebSearch'ten gelen fiyatı deterministik tablodaki **canlı /info mark** ile kıyasla. **>~%15 sapıyorsa** o kaynağı `[fiyat-şüpheli]` işaretle ("fiyatı tutmuyor → haberleri de eski/yanlış olabilir, dikkatli kullan"). _(Örnek: HYPE web ~$37 vs canlı /info ~$64 → şüpheli.)_
     4. **SORGU TARİHLİ:** WebSearch'te "latest" KULLANMA (bayat sonuç riski). Bugünün tarihini koy — `crypto news 2026-06-15`, `Fed decision June 2026` gibi.
     5. **FORMAT (bağlayıcı):** her madde → `- [yayın: YYYY-MM-DD] [fiyat-şüpheli]? kısa-başlık + yorum [kaynak](URL)`. Başlıklar `### MAKRO` / `### KRİPTO` / `### FİYAT ÇELİŞKİSİ` ile gruplanır.
   - **Kaynak-bağlı** (URL + tarih). **Uydurma YOK** — bulamazsan "bulunamadı" yaz.
   - **LOOK-AHEAD UYARISI (Glasserman/Lin) KALIR:** Eğitim verisinden olayın "sonucunu" biliyor olabilirsin — **o sonucu VARSAYMA**; yalnız şu an raporlanan kamuya-açık durumu yorumla. Tarihsiz/eski haber bağlam olarak **ZAYIF** işaretlenir.
3. **Akış/funding yorumu (varsa):** funding-ekstrem (aşırı-ısınma reversal riski?), OI seviyesi/yön (varsa). On-chain exchange inflow/outflow **ücretsiz kaynak yok** → "gap, çekilemiyor" yaz (uydurma sinyal yok).
4. **Öneri (insan için):** deterministik ↔ haber gerilimini özetle. **ÖNERİ + bağlam, otomatik trade DEĞİL.** "Karar SENİN" + izolasyon notu.

## Çıktı
- `journal/MANUEL-DERIN-*.md` (etiketli, commit'li — **gizli log YOK**).

## Demir kurallar
Gerçek para YOK · determinism otomatik-runner'da (bu mod onu bozmaz) · tez≠fiyat · **uydurma yok** (kaynak zorunlu) · **look-ahead flag** · çıktı öneri/bağlam (trade değil) · Faz 1 sabit (bu mod faz-içi config'i değiştirmez).

## Kapanış aksiyonu (ZORUNLU — Can isteği)
İş biter bitmez dashboard'ı tazele: `bash "../Obsidian Vault/data/scripts/sync.sh"`. Derin tarama Derin Mod tab'ına yansır; site snapshot — sync yapılmazsa eski kalır.
