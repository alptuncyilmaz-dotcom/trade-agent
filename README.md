# trade-agent

Kripto perp (tek varlık: BTC veya ETH) **forward-test + araştırma** sistemi. Hyperliquid **testnet/paper ONLY — gerçek para YOK.** Vault'un kardeşi ama AYRI repo, ayrı git.

> Dürüst beklenti: LLM-güdümlü trader'ın fee+funding sonrası piyasayı yenmesi düşük ihtimal. Değer: kendi strateji dokümanını üreten + ileri-test eden öğretici sistem. Kurallar `CLAUDE.md`'de.

## 7 katman (determinism kodda, judgment LLM'de)
| # | Katman | Dizin | Ne |
|---|---|---|---|
| 1 | Veri (point-in-time) | `data/` | OHLCV (`ohlcv.py`) + funding (`funding.py`) + on-chain (`onchain.py` — gap) + `snapshot.py` (look-ahead öldür) |
| 2 | Feature | `features/` | RSI/MACD/ATR/SMA/EMA/likidite (`indicators.py`) — KOD hesaplar |
| 3 | Decision agent | `.claude/agents/trader-scan.md` | snapshot → JSON tez/entry/stop/target |
| 4 | Execution sim | `execution/simulator.py` | fee + funding + slippage DAHİL paper-fill |
| 5 | Evaluation | `evaluation/metrics.py` | expectancy / profit factor / max DD / Sharpe |
| 6 | Reflection agent | `.claude/agents/trader-refresh.md` | sonuç → neden + aday öğrenim |
| 7 | Strateji doc | `strategy/` | yavaş evrilen, insan-okunur |

Ek: `triggers/rules.py` (LLM ne zaman çalışır), `decision.py` (JSON şema), `journal/` (tez/sonuç/neden ayrı).

## Kurulum
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # HL_TESTNET_KEY (sadece testnet)
```
Çekirdek katmanlar bağımlılıksız (stdlib). Hyperliquid `/info` read düz HTTP.

## Veri akışı (özet)
`ohlcv.get_candles` + `funding.get_funding` → `indicators.compute_features` → `snapshot.build_snapshot(as_of)` → (trigger ateşlerse) `trader-scan` JSON karar → `simulator.simulate_round_trip` → `metrics.summarize` → `trader-refresh` neden + `strategy/` öneri.

## Güvenlik sınırları (DEĞİŞMEZ — bkz CLAUDE.md)
Testnet-only EMİR · win-rate hedefi yok · point-in-time (leakage yok) · tez≠fiyat · fee+funding+slippage · trigger-only · anchor asimetrik · uydurma yok. **Hiçbir cutoff-öncesi sonuç performans kanıtı değildir.**

**Okuma mainnet, emir testnet (KARAR 3):** Fiyat/funding/feature OKUMA'sı varsayılan **mainnet** (derin likidite → feature kalitesi; public read, para yok). **EMİR yine testnet/paper** — order endpoint tanımsız, mainnet emri imkânsız. Testnet okumayı zorla: `HL_FORCE_TESTNET_READ=1`.

## Test
```bash
python -m pytest tests -v
```
6 test: feature unit · point-in-time enforce · execution sim maliyet · evaluation metrik · decision JSON şema · **testnet bağlantı smoke** (gerçek mainnet emir DEĞİL).

## Veri durumu
- ✅ OHLCV + funding: Hyperliquid testnet `/info` (ücretsiz, anahtarsız read).
- ⚠️ On-chain exchange flow: **güvenilir ücretsiz kaynak yok** (bkz `logs/onchain-research.md`) → `onchain.py` `available:False`, sinyal uydurmaz. Sistem funding+OHLCV ile çalışır.
