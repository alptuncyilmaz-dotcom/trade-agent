# 🔍 COLD SCAN (trader-scan + challenger akışı) — 2026-06-15 ~22:40 TSİ

> **Elle / LLM-in-the-loop analiz** (deterministik runner'dan AYRI). State/runs'a DOKUNULMADI.
> ÖNERİ + karşı-tez; **KARAR İNSANDA.** TESTNET/PAPER, gerçek para YOK. Anchor-free (point-in-time snapshot).
> NOT: 4 varlık da zaten açık (runner) → bu YENİ emir değil, akışı gösteren illüstratif cold-scan.

## Snapshot (point-in-time, read-only) · rejim: mixed
| Varlık | Fiyat | RSI | MACDh | trend (15m/1h/4h/1d) | ctr-long | trigger |
|---|---|---|---|---|---|---|
| BTC | 66546 | 61.6 | +16.25 | range/up/up/range | hayır | ✅ MACD |
| ETH | 1819.5 | 74.8 | +6.46 | range/up/up/range | hayır | ✅ (RSI aşırı-alım!) |
| XRP | 1.2749 | 85.3 | +0.01 | up/up/up/range | hayır | ✅ (RSI 85 aşırı-alım!) |
| HYPE | 67.426 | 65.2 | −0.07 | range/up/up/up | hayır | ❌ |

## ① ANALYST tezi (cold) — BTC long
En temiz aday: BTC. **side buy · entry 66546 · stop 65910 (1.6×ATR) · target 67587 · R:R 2.62:1 · kaldıraç 1.0x · güven low.**
Gerekçe: MACD trigger + trend-uyumlu (1h/4h up, counter-trend değil) + **RSI 61.6 sağlıklı** (ETH 74.8 / XRP 85.3 aşırı-alım → H-03 geç-giriş riski; BTC değil) + funding ~0 (ısınma yok). 1d:range → tam hizalı değil → low güven → 1.0x.

## ② CHALLENGER (farklı lens — karar vermez)
- **(c) Portföy konsantrasyonu [ASIL KÖR NOKTA]:** BTC bağımsız 2.62:1 gibi sunulmuş ama 4 eşzamanlı korelasyonlu long'un 4.'sü; gerçek risk tek-poz ATR'sinin katı.
- **(a)** 15m+1d range → trend-following edge zayıf; range'de target öncesi stop-toplama (mean-reversion) açık.
- **(d)** Stop 65910, yuvarlak 66000'in hemen altı → klasik likidite-avı/fitil bölgesi; R:R'yi sıfırlayabilir.
- **(b)** "low güven" tek-poz bazında; portföy bazında risk etiketi yok.
- **Funding:** anlık nötr (doğru) ama kalabalık long → funding pozitife dönüp 4 bacağı birden maliyetlendirebilir (ileri risk).

## ③ ANALYST cevabı (her itiraza)
- **(c) KABUL — tezi değiştirdim:** Bu belirleyici. Sistem portföy-seviyesi risk tavanı tutmuyor (her poz bağımsız $1000); 4 korelasyonlu long'da piyasa-geneli düşüş hepsini birden vurur. **BTC, 4. korelasyonlu long olarak EKLENMESİ disiplinsiz** — bağımsız temiz olsa da portföy konsantrasyonunu artırır.
- **(a) KABUL (kısmi):** Geçerli; low güven zaten bunu yansıtıyor. 1h/4h up + trigger sistemin tanımlı girişi ama range TF'ler edge'i zayıflatıyor → low güven korunur.
- **(d) KABUL:** Gerçek zayıflık. Kod sabit 1.6×ATR stop koyuyor, yuvarlak-rakam likidite kümesini hesaba KATMIYOR (H-04 "giriş-stop-hedef bütün" ile bağ). İşaretlendi.
- **(b) KABUL:** Doğru — portföy-seviyesi güven/risk kapısı yok (mevcut sistem gap'i, Can'a daha önce flag'lendi).
- **Funding:** KABUL (ileri risk) — izlenecek; şu an nötr, karar girdisi değil.

## ④ RAFİNE GÖRÜŞ (karar DEĞİL — İNSANA)
BTC bacağı **tek başına teknik olarak temiz** (RSI sağlıklı, counter-trend değil, funding nötr, asimetrik R:R) AMA **portföy bağlamında 4. korelasyonlu long → konsantrasyon artırır; disiplinli duruş: EKLEME veya mevcut long'lar çözülene kadar BEKLE.** Stop'u likidite-avı (66000) dışına almak ayrı bir iyileştirme (H-04).
**Tetiği Can çeker; al/sat demiyorum.**

*Determinism kodda; bu akış izole (runner'a sızmaz, Faz 1 sabit); tez≠fiyat; uydurma yok; karar insanda.*
