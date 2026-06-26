# vizyon-uzun-vade.md — Faz 3+ uzak hedefler (ŞİMDİ KURMA — ölçülmüş veri sonrası)

> **Bu dosya UYGULAMA DEĞİL, yön.** Buradaki hiçbir şey Faz 1/2'de kurulmaz. Tetik: A/B
> baseline + **aylarca ölçülmüş veri**. Erken kurmak = overfitting = sistemi batırır.
> Hafıza ilkesi (CLAUDE.md): vizyon da sohbette değil DOSYADA yaşar.

## REJİM ADAPTASYONU — "yaşayan mega trader" hedefi (FAZ 3+)

**Hedef:** agentlar piyasa rejimine ayak uydursun. Bir strateji 2022-23 kazanır, 2024-25
batırabilir (rejim değişir); statik kural er ya da geç rejim-uyumsuzluğundan ölür.

### ⚠️ KRİTİK UYARI — iki tuzak
1. **HINDSIGHT OVERFITTING:** Bunu "geçmişten rejim tanımla, ona fit et" diye kurmak YASAK.
   Rejim değişimi ancak **SONRADAN** belli olur — gerçek anda "geçici düşüş mü kalıcı rejim mi"
   BİLİNMEZ. Geçmişe fit = backtest/hindsight yasağının tam ihlali.
2. **"Yaşayan/öğrenen" ≠ LLM otomatik adapte olur:** LLM **seanslar arası ÖĞRENMEZ**
   (deep-thinker turlar arası öğrenmez — sabit kurallar). Adaptasyon sihirle gelmez;
   **ELLE kural yazmaktan** gelir.

### ✅ DOĞRU YOL
- A/B (ve ileride A-B-C-D) **zaten rejim etkisini ÖLÇÜYOR.** Aylarca veri biriktikçe "hangi
  sistem hangi koşulda kazanıyor" deseni **kendiliğinden ÇIKAR** (ölçülmüş, fit edilmemiş).
- Rejim-farkında kural **O BULGUDAN SONRA** yazılır — **önce ölç, sonra adapte.**
- **Faz 3+ işi:** A/B baseline + aylarca veri sonrası. ŞİMDİ kurmak = overfitting.

> Özet: "yaşayan sistem" = **ölçerek evrilen** sistem (CLAUDE.md ÇEKİRDEK FELSEFE), heveSle sürekli
> değişen değil. Rejim adaptasyonu bu felsefenin en uzak ucu — en çok veri, en çok sabır ister.
