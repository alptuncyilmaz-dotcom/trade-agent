# CLAUDE.md — Trade-Agent Anayasası

> Para hareket ettiren kod. AYRI repo. Bu bir ARAŞTIRMA + forward-test sistemi.

## Demir disiplinler (DEĞİŞMEZ)
1. TESTNET / PAPER ONLY. GERÇEK PARA YOK.
2. OKUMA mainnet, EMİR testnet.
3. 4 varlık: BTC · ETH · XRP · HYPE
4. Sizing: %1.5 risk / %30 poz tavan / %100 teminat-guard. Kaldıraç maks 5x.
5. Counter-trend açma yasak. Range-HTF → WAIT.
6. Uydurma yok. Kaynak zorunlu.
7. Faz 1 içinde config sabit — yeni faktör eklenmez.
8. Tez ≠ fiyat. SUCCESSFUL/FAILED etiketi yasak.
9. Anchor-free scan. Turlar arası öğrenme yok.
10. Karar DOSYADA yaşar, sohbette değil.

## A/B mimarisi
- deterministic-trader: kural bazlı (RSI/MACD/trend/rejim)
- deep-thinker: LLM analyst → challenger → otonom karar
- Aynı snapshot, aynı sizing, ayrı bakiye ($4000 her biri)

## Aktif lessons
- L-01: LLM trader fee sonrası B&H'yi yenmiyor — baseline karşılaştır
- L-02: Aşırı yüksek Sharpe = leakage şüphesi
- L-03: Over-trading fee sessiz katil
- H-03: RSI>65 + aşırı-uzamış = geç giriş riski (WAIT eğilimi)

## Faz durumu
FAZ 1 — temel ölçüm. Config sabit. ~30 trade hedef.
