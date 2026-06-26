# trade-agent

Kripto perp (BTC · ETH · XRP · HYPE) **A/B araştırma + forward-test** sistemi. Hyperliquid
**testnet/paper ONLY — gerçek para YOK.** Tam anayasa: [CLAUDE.md](CLAUDE.md).

> Dürüst beklenti: LLM-güdümlü trader'ın fee+funding sonrası piyasayı yenmesi düşük ihtimal (L-01).
> Değer: kendi strateji dokümanını üreten + ileri-test eden, **kuralı LLM'e karşı ölçen** öğretici sistem.

## A/B mimarisi
İki kol, **aynı snapshot + aynı sizing**, ayrı $4000 bakiye, ayrı state/runs:
- **A — deterministic-trader** (`run_deterministic.py`): saf kural (RSI/MACD/trend/rejim, LLM YOK).
- **B — deep-thinker** (`run_deepthinker.py` → `apply_deepthinker.py`): LLM analyst → challenger → otonom karar.

Soru: LLM+challenger akıl yürütmesi saf kuralları yenebilir mi? ~30+ trade sonra VERİYLE karşılaştır.

## 7 katman (determinism kodda, judgment LLM'de)
| # | Katman | Dizin | Ne |
|---|---|---|---|
| 1 | Veri (point-in-time) | `data/` | OHLCV (`ohlcv.py`) + funding (`funding.py`) + on-chain proxy (`onchain.py`) + `snapshot.py` |
| 2 | Feature | `features/` | RSI/MACD/ATR/SMA/EMA (`indicators.py`) + çok-TF trend/rejim (`trend.py`) — KOD hesaplar |
| 3 | Decision | A: `run_deterministic.py` · B: `.claude/agents/deep-thinker.md` | snapshot → JSON tez/entry/stop/target |
| 4 | Execution sim | `execution/` | sizing + leverage + fee/funding/slippage'li `simulator.py` |
| 5 | Evaluation | `evaluation/metrics.py` | expectancy / PF / maxDD / Sharpe + `baselines` (B&H + RSI) |
| 6 | Reflection | `.claude/agents/trader-refresh.md` | sonuç → neden + aday öğrenim |
| 7 | Strateji doc | `strategy/` | yavaş evrilen, insan-okunur |

Ek: `triggers/rules.py` (LLM ne zaman çalışır), `execution/decision.py` (JSON şema+guard), `execution/autonomous.py` (gate/path-check/anchor), `journal/` (tez/sonuç/neden ayrı).

## Veri akışı (özet)
`ohlcv.fetch_candles` + `funding.fetch_funding` → `indicators` + `trend` → `snapshot.build_snapshot` →
(trigger ateşlerse) decision → `simulator.simulate_trade` → `metrics.summarize` + `baselines.compare` → reflection + `strategy/`.

## Kurulum
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env        # ANTHROPIC_API_KEY=... (deep-thinker SDK; .env gitignore'lu)
.venv/bin/python run_turn.py
```
Saatlik otomatik tetik: lokal launchd `com.trade-agent.turn` → `run_turn.sh` (akış: [ROUTINE.md](ROUTINE.md)).

## Test
```bash
.venv/bin/python -m pytest tests -v
```

## Güvenlik sınırları (DEĞİŞMEZ — bkz CLAUDE.md)
Testnet-only EMİR · win-rate hedefi yok · point-in-time (leakage yok) · tez≠fiyat · fee+funding+slippage · trigger-only · anchor asimetrik · uydurma yok. **Hiçbir cutoff-öncesi sonuç performans kanıtı değildir.**

## Veri durumu
- ✅ OHLCV + funding + OI: Hyperliquid `/info` (ücretsiz, anahtarsız read).
- ⚠️ On-chain exchange flow: **güvenilir ücretsiz kaynak yok** (bkz `logs/onchain-research.md`) → `data/onchain.py` proxy, sinyal uydurmaz. Gerçek kaynaklar: `strategy/paid-sources.md`.
