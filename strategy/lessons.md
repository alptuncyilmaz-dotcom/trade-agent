# lessons.md — Trader Yaşayan Dersleri (aktif kurallar)
> **Genel ilke (zamansız) — per-trade snapshot'a GİRMEZ.** Strateji/değerlendirme
> katmanında okunur (decision anında geleceğe dair bilgi değil; yöntem disiplini).
> Format: `[L-XX] · [🟢/🔴/⚠️] · kural · kökeni`. 🟢 edge-burada · 🔴 yakan-patern · ⚠️ uyarı/çelişki.
> Bu doküman insan-onaylı AKTİF kural; aday hipotezler `strategy/_strategy.md` + `candidate-factors.md`.

## Aktif Kurallar

- **[L-01] · 🔴 · LLM trader maliyetten sonra buy-and-hold'u yenmiyor.** Standalone LLM trading, fee+funding sonrası genelde basit buy-and-hold'un altında kalıyor. **Uygulama:** trader expectancy'sini her zaman **buy-and-hold + basit RSI kuralına KARŞI, fee-net** ölç (`execution/baselines.compare`). Bu iki baseline'ı yenmiyorsa stratejiyi graduate ETME. · *kökeni: deep-research 2026-06-13 (FINSABER / StockBench)*

- **[L-02] · 🔴 · Near-100% isabet veya Sharpe>3-4 = önce leakage şüphesi.** Aşırı yüksek isabet/Sharpe gördüğünde ilk hipotez **performans değil, sızıntı** olmalı (look-ahead / narrative kontaminasyonu). **Uygulama:** böyle sonuç çıkarsa DUR, point-in-time zincirini denetle; "iyi sonuç" diye kutlama. (`metrics.summarize` leakage bayrağı kaldırır.) · *kökeni: deep-research 2026-06-13 (TradingAgents dersi)*

- **[L-03] · 🔴 · Over-trading / fee = sessiz katil.** Sık işlem fee+funding ile getiriyi sessizce yer. **Uygulama:** **turnover ve toplam fee/funding'i birinci-sınıf metrik** yap — expectancy/Sharpe ile birlikte izle. Trigger-only disiplini ilk savunma. · *kökeni: deep-research 2026-06-13 (Gemini fee-bleed)*

- **[L-04] · 🟢 · LLM'in gerçek değeri: risk/drawdown kontrolü + haber yorumu + insan-döngüde araştırma — standalone alpha DEĞİL.** **Uygulama:** başarı tanımını "piyasayı yen" yerine "drawdown'u kontrol et + bağlamı doğru oku + insana iyi araştırma ver" olarak ölç. · *kökeni: deep-research 2026-06-13*

- **[H-03] · ⚠️ · RSI>65 tek-trigger = geç/düşük-edge giriş.** HTF (4h/1d) trend + çok-varlık rejim bağlamı olmadan 1h counter-trend açmak kaybeder. **Aday ders** (henüz terfi etmedi — forward-test bekliyor); `features/trend.py` sistem-gap'i kapattı ama hipotez hâlâ sınanıyor. · *kökeni: forward-test BTC-001 stop derin analizi*

## Ham Arşiv
<!-- Boş — forward-test retrolarından birikir. Decision snapshot'ına GİRMEZ. -->
