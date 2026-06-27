# lessons.md — Trader Yaşayan Dersleri (aktif kurallar)
> Trade-agent'a özgü. Equity `_engine/lessons.md`'den AYRI (domain karışmaz).
> **Genel ilke (zamansız) — per-trade snapshot'a GİRMEZ.** Strateji/değerlendirme
> katmanında okunur (decision anında geleceğe dair bilgi değil; yöntem disiplini).
> Format: `[L-XX] · [🟢/🔴/⚠️] · kural · kökeni`. 🟢 edge-burada · 🔴 yakan-patern · ⚠️ uyarı/çelişki.

## Aktif Kurallar

- **[L-01] · 🔴 · LLM trader maliyetten sonra buy-and-hold'u yenmiyor.** Standalone LLM trading, fee+funding sonrası genelde basit buy-and-hold'un altında kalıyor (FINSABER, StockBench). **Uygulama:** trader expectancy'sini her zaman **buy-and-hold + basit RSI kuralına KARŞI, fee-net** ölç. Bu iki baseline'ı yenmiyorsa stratejiyi **graduate ETME** (gerçek-para gate'ine yaklaştırma). · *kökeni: deep-research 2026-06-13 (FINSABER / StockBench)*

- **[L-02] · 🔴 · Near-100% BUY veya Sharpe>3-4 = önce leakage şüphesi.** Aşırı yüksek isabet/Sharpe gördüğünde ilk hipotez **performans değil, sızıntı** olmalı (look-ahead / narrative kontaminasyonu / yanlışlıkla geleceği gören snapshot). **Uygulama:** böyle bir sonuç çıkarsa DUR, point-in-time zincirini denetle; "iyi sonuç" diye kutlama. · *kökeni: deep-research 2026-06-13 (TradingAgents #203 dersi)*

- **[L-03] · 🔴 · Over-trading / fee = sessiz katil.** Sık işlem fee+funding ile getiriyi sessizce yer (örn. Gemini-tabanlı ajanda ~%13 fee bleed). **Uygulama:** **turnover ve toplam fee/funding'i birinci-sınıf metrik** yap — expectancy/Sharpe ile birlikte her değerlendirmede izle ve raporla. Trigger-only disiplini bunun ilk savunması. · *kökeni: deep-research 2026-06-13 (Gemini fee-bleed gözlemi)*

- **[L-04] · 🟢 · LLM'in gerçek değeri: risk/drawdown kontrolü + haber yorumu + insan-döngüde araştırma — standalone alpha DEĞİL.** Beklentiyi buna sabitle: LLM'i "alpha üreten kara kutu" değil, **risk yönetimi + niteliksel haber/bağlam yorumu + insan-loop araştırma asistanı** olarak konumla. **Uygulama:** sistemin başarı tanımını "piyasayı yen" yerine "drawdown'u kontrol et + bağlamı doğru oku + insana iyi araştırma ver" olarak ölç. · *kökeni: deep-research 2026-06-13*

## Ham Arşiv
<!-- Boş — forward-test retrolarından birikir. Decision snapshot'ına GİRMEZ. -->
