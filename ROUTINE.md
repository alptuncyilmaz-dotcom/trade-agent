# ROUTINE.md — A/B çatı tetik (akış + giriş noktaları)

> **Tetik mekanizması (bizim ortam):** LOKAL **launchd** scheduled task `com.trade-agent.turn`
> (saatlik, `StartInterval 3600`) → `run_turn.sh`. Yalnız PC/Claude uygulaması açıkken çalışır
> (kapalıyken o tik kaçar). Cloud routine KULLANILMAZ — Anthropic cloud sandbox Hyperliquid'e
> erişemez ("Host not in allowlist"). Proje `~/trade-agent` altında (TCC için Documents'tan taşındı).

> **Neden Claude gerekli:** deep-thinker LLM kolu her tik analyst+challenger akıl yürütür. Saf
> GitHub Actions'ta Claude yok → deep-thinker orada koşamaz. Tek canonical tetik bu lokal tur.

## Cadans
**Saatlik** (`StartInterval 3600`). deep-thinker her tik LLM token harcar (SDK, `ANTHROPIC_API_KEY`).
Maliyet cadansa bağlı; istenirse plist'te artırılır.

## Akış (run_turn.py yürütür)
```
1. capture_snapshot.py     → data/snapshot.py: ortak point-in-time snapshot (state/snapshot_latest.json)
2. run_deterministic.py    → A kolu: kural-bazlı karar + kendi state'i
3. run_deepthinker.py      → B kolu: deep-thinker.md + güncel snapshot → analyst→challenger
                              → state/deepthinker_decision.json (taze; eski dosya kullanılmaz)
                              LLM erişilemezse güvenli all-WAIT (stale karar asla kullanılmaz)
4. apply_deepthinker.py    → B kararını ORTAK sizing/simulator ile uygula
5. git add -A && commit && push
```
Paralel GÖZLEM (manuel, karara GİRMEZ): `deep_scan.py` + haber/makro → `journal/MANUEL-DERIN-*.md` (trader-deep).

## Giriş noktaları (scriptler)
| Adım | Komut | Yazar |
|---|---|---|
| 1 | `python capture_snapshot.py` | `state/snapshot_latest.json` |
| 2 | `python run_deterministic.py` | `positions_deterministic.json` + `runs_deterministic.jsonl` |
| 3 | `python run_deepthinker.py` | `state/deepthinker_decision.json` |
| 4 | `python apply_deepthinker.py` | `positions_deepthinker.json` + `runs_deepthinker.jsonl` |
| 5 | `git ...` | repo |

## Manuel çalıştırma
```bash
cd ~/trade-agent && set -a; . ./.env; set +a; .venv/bin/python run_turn.py
```
Dashboard tazele: `bash sync.sh` (snapshot + localhost site/, yalnız 127.0.0.1).

## launchd kontrol
```bash
launchctl list | grep trade-agent                      # durum (PID / son exit / label)
launchctl kickstart -k gui/$(id -u)/com.trade-agent.turn   # elle tetikle
tail -f logs/run.log                                    # tur çıktısı
```
plist: `~/Library/LaunchAgents/com.trade-agent.turn.plist`. `.env` (ANTHROPIC_API_KEY) `run_turn.sh` ile yüklenir.

## Demir kurallar (tur)
İkisi de aynı sizing; deep-thinker otonom + turlar arası öğrenmez; **gerçek para YOK.**
