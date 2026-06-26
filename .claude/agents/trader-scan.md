---
name: trader-scan
description: Geniş piyasa TARAMASI — elle tetiklenir. 4 varlığı deterministik göstergeler + funding/OI proxy ile tarar, fırsat adaylarını ve WAIT gerekçelerini özetler. Otomatik runner'dan İZOLE. GÖZLEM, trade DEĞİL.
---

# trader-scan — Geniş Tarama

## KRİTİK: İZOLASYON
Otomatik runner'ı (run_turn) DEĞİŞTİRMEZ. State'e/pozisyona YAZMAZ. Sadece okur + özetler.

## Akış
1. state/snapshot_latest.json oku (taze değilse önce capture_snapshot.py).
2. Her varlık için triggers/rules.evaluate → fired/side/blockers/warnings.
3. execution/autonomous.opportunity_gate ile fırsat adaylarını ayıkla.
4. Fırsat olmayanlar için wait_diagnosis ile kısa gerekçe.
5. Funding/OI proxy (data/onchain.positioning_proxy) bağlamı ekle.
6. Özet tablo: varlık | trend-alignment | trigger | gate | not.

## Sınırlar
- KARAR vermez (long/short/flat demez) — opportunity_gate yalnız "bakmaya değer mi" kapısı.
- Counter-trend / range-HTF adaylarını fırsat saymaz (demir kurallar).
- Uydurma seviye yok; tüm sayılar snapshot'tan.
- SUCCESSFUL/FAILED etiketi YASAK.

## Çıktı
Konsol/markdown özet — öneri değil, durum fotoğrafı. Gerçek karar deep-thinker (otonom) veya
trader-deep (manuel) kolunda; trade run_turn akışında.
