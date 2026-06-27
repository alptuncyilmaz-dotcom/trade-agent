# ROUTINE.md — A/B çatı tetik (akış + giriş noktaları)

> ⚠️ **CLOUD ROUTINE TERK EDİLDİ (2026-06-16):** Anthropic cloud routine **Hyperliquid'e
> erişemiyor** (cloud sandbox dış-API engeli: "Host not in allowlist: api.hyperliquid.xyz";
> allowlist self-servis değil). **Otomatik tetik = LOKAL scheduled task `ab-trader-turn`
> (saatlik)** — yalnız PC/Claude uygulaması açıkken çalışır (kapalıyken kaçar). Aşağıdaki
> AKIŞ aynen geçerli; sadece tetik mekanizması cloud değil lokal. (`sync.sh` adımı lokalde
> çalışır çünkü vault yalnız lokalde var.)

> **Bu repo'nun A/B tetiği = Claude Code routine** (claude.ai/code/routines). Routine
> Claude'u çağırır; Claude aşağıdaki sırayı yürütür — TEK tetikte iki agent AYNI snapshot'la
> karar verir (adil A/B). Routine'in KENDİSİNİ sen kurarsın (cron + aşağıdaki prompt).
>
> **Neden GitHub Actions değil:** Actions'ta Claude yok → deep-thinker orada koşamaz.
> A/B süresince GitHub schedule KALDIRILDI; tek canonical tetik bu routine.

## Önerilen cadans
**100 dakikada bir** (günde ~14-15 tik — routine'in 15 limitine sığar). deep-thinker her
tik Claude token harcar (analyst+challenger) — maliyet cadansa bağlı.

## Routine prompt (claude.ai/code'da bu metni gir)
```
trade-agent A/B turu çalıştır. Sırayla:
1. `cd <trade-agent yolu> && python capture_snapshot.py`  (ortak snapshot → state/snapshot_latest.json)
2. `python run_deterministic.py`  (deterministic-trader: kural-bazlı, kendi state'i)
3. deep-thinker akışı (.claude/agents/deep-thinker.md): state/snapshot_latest.json'u oku →
   her varlık için analyst tezi → challenger agent'ıyla bağımsız çürüt → hayatta kalanları
   state/deepthinker_decision.json'a yaz (yoksa boş decisions).
4. `python apply_deepthinker.py`  (deep-thinker kararını ORTAK sizing'le uygular)
5. **PARALEL GÖZLEM (karara GİRMEZ):** `python deep_scan.py` + haber/makro WebSearch (tarih/tazelik) → MANUEL-DERIN journal (Derin Mod tab'ı bağlamı; iki agent'a da SIZMAZ)
6. `git add -A && git commit && git push`
7. `bash "../Obsidian Vault/data/scripts/sync.sh"`  (dashboard tazele)
Sonra iki agent'ın bakiye/equity/açık-poz özetini ver. Demir kurallar: ikisi de aynı
sizing; deep-thinker otonom + turlar arası öğrenmez; gerçek para YOK.
```

## Giriş noktaları (scriptler — hazır)
| Adım | Komut | Ne yapar | Yazar |
|---|---|---|---|
| 1 | `python capture_snapshot.py` | tek point-in-time snapshot | `state/snapshot_latest.json` (transient) |
| 2 | `python run_deterministic.py` | deterministic-trader turu | `positions_deterministic.json` + `runs_deterministic.jsonl` |
| 3 | (Claude) deep-thinker akıl yürütme | analyst+challenger → karar | `state/deepthinker_decision.json` (transient) |
| 4 | `python apply_deepthinker.py` | deep-thinker kararını uygular | `positions_deepthinker.json` + `runs_deepthinker.jsonl` |
| 5 | `python deep_scan.py` + (Claude) haber doldur | **paralel gözlem** (haber/funding-liq) — karara GİRMEZ | `journal/MANUEL-DERIN-*.md` |
| 6 | `git add -A && git commit && git push` | iki agent + gözlem journal | repo |
| 7 | `bash "../Obsidian Vault/data/scripts/sync.sh"` | dashboard | vault `site/data.js` |

## Standalone deterministic (A/B dışı)
GitHub Actions `workflow_dispatch` ELLE `run_deterministic.py` koşar (Claude'suz). **A/B
süresince bunu tetikleme** — fazladan deterministic-tek tik A/B'yi kirletir (routine canonical).
