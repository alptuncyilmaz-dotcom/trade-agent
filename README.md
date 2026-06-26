# trade-agent

Kripto perp (BTC · ETH · XRP · HYPE) üzerinde **A/B araştırma + forward-test** sistemi.
**TESTNET / PAPER ONLY — gerçek para YOK.** Tam anayasa: [CLAUDE.md](CLAUDE.md).

## A/B mimarisi
İki kol, **aynı snapshot + aynı sizing**, ayrı $4000 bakiye:
- **A — deterministic-trader** (`run_deterministic.py`): saf kural (RSI/MACD/trend/rejim).
- **B — deep-thinker** (`run_deepthinker.py`): LLM analyst → challenger → otonom karar.

## Veri akışı (saatlik tur)
```
capture_snapshot.py        # data/snapshot.py → ohlcv+funding+onchain + indicators + rules
   → run_deterministic.py  # A kolu
   → run_deepthinker.py    # B kolu (LLM; SDK ANTHROPIC_API_KEY ile)
   → apply_deepthinker.py  # B kararını simülatörle uygula
   → git push
```
Tek komut: `run_turn.py` (saatlik launchd → `run_turn.sh`).

## Katmanlar (tek-kaynak)
| Katman | Sorumluluk |
|--------|-----------|
| `data/` | Hyperliquid ham veri: ohlcv, funding, onchain(proxy), snapshot kurucu |
| `features/indicators.py` | RSI/MACD/ATR/SMA/EMA/trend — saf hesap |
| `triggers/rules.py` | Tetik + demir-kural değerlendirme (counter-trend, range-HTF, H-03) |
| `execution/` | decision (şema+guard), leverage (sizing), simulator (fill+fee+funding+slippage), autonomous (gate/wait/context) |
| `evaluation/metrics.py` | expectancy, profit factor, max DD, Sharpe (+leakage bayrağı) |
| `strategy/` | _strategy, lessons, candidate-factors, paid-sources |
| `.claude/agents/` | deep-thinker, challenger, trader-deep, trader-refresh, trader-scan |

## Demir disiplinler (özet)
1. Testnet/paper — gerçek para yok. 2. Oku mainnet, emir testnet. 3. Counter-trend açma yasak.
4. Range-HTF → WAIT. 5. Sizing: %1.5 risk / %30 poz / %100 teminat-guard / maks 5x.
6. Uydurma yok, kaynak zorunlu. 7. Faz-1 config sabit. 8. SUCCESSFUL/FAILED etiketi yasak.
9. Turlar arası öğrenme yok. 10. Karar dosyada yaşar.

## Kurulum
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # ANTHROPIC_API_KEY=... (deep-thinker SDK için; .env gitignore'lu)
.venv/bin/python run_turn.py
```

## Faz durumu
**FAZ 1** — temel ölçüm, config sabit, ~30 trade hedef. Faktör eklemek: `strategy/candidate-factors.md`.
