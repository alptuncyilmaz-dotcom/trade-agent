---
name: trader-refresh
description: Otonom pozisyon yöneticisi — stop/target değdiyse KAPATIR + tez≠fiyat analizi. SUCCESSFUL/FAILED etiketi YASAK. TESTNET ONLY.
---

# trader-refresh — Pozisyon Yöneticisi

## Akış
1. Açık pozisyonu oku
2. Stop/target değdi mi kontrol et
3. Değdiyse kapat + net % (fee dahil) + baseline karşılaştır
4. Tez≠fiyat ayrımı — SUCCESSFUL/FAILED etiketi YASAK
5. Özet yaz: Nasıl verildi / Sonuç / DERS
