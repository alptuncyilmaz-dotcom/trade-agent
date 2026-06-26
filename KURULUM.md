# ASİMETRİ SİSTEMİ — TIPATIP KURULUM REHBERİ (başka PC)

> Bu dosyayı baştan sona uygula → sistem **sak diye çalışır**. Her adım komutuyla. Atlama.
> Hazırlayan: Can'ın sistemi · Tarih: 2026-06-22 · Hedef: yeni bir Mac/Linux PC.
>
> 📦 **BU PAKETTE İKİ REPO ZATEN VAR** (`Obsidian Vault/` + `trade-agent/`, kardeş).
> **Adım 3'ü (git clone) ATLA** — paketin içinde `bash setup.sh` çalıştır, sonra Adım 5+'ya geç.
> (Adım 3 yalnız sıfırdan GitHub'dan kuracak biri için referans.)

---

## 0. SİSTEM NEDİR (30 saniyelik resim)

İki AYRI git reposu, bir **kardeş klasör** altında çalışır:

| Repo | Ne | Para? |
|---|---|---|
| **asimetri-vault** (Obsidian Vault) | NASDAQ small-cap **equity araştırma** (lowcap+solid tarama, karar İNSANIN) + statik **HTML dashboard** | gerçek para YOK (kâğıt portföy) |
| **trade-agent** | Kripto perp **A/B/C otonom forward-test** (Hyperliquid BTC/ETH/XRP/HYPE) — det vs deep-thinker vs aggressive | **TESTNET/PAPER — GERÇEK PARA YOK** |

- **Determinizm KODDA, yargı LLM'de.** Python katmanları (veri/feature/sizing/execution) anahtarsız çalışır; **LLM agentlar (tarama, deep-thinker, challenger) Claude Code ister.**
- **Dashboard** = statik HTML (`site/index.html`), canlı feed yok; `sync.sh` ile `data.js` üretilir.

---

## 1. ÖNKOŞULLAR (yeni PC'ye kur)

| Araç | Sürüm | Neden | Kurulum (macOS) |
|---|---|---|---|
| **git** | herhangi | repoları çek | `brew install git` |
| **Python** | **3.11+** (3.14 test edildi) | tüm Python katmanı (`dict \| None`, `from __future__`) | `brew install python@3.14` |
| **Claude Code** | güncel | **LLM agentlar ZORUNLU** (tarama, deep-thinker, challenger). Deterministik kısım Claude'suz da çalışır. | Anthropic'ten Claude Code (CLI/Desktop) |
| **Node.js** | 18+ (OPSİYONEL) | yalnız `site/` dashboard testleri (playwright) | `brew install node` |

> **Claude Code olmadan:** dashboard + `run_deterministic.py` + `run_aggressive.py` (saf Python, kural-bazlı) çalışır. **deep-thinker kolu + equity taramaları çalışmaz** (LLM gerekir).

---

## 2. ⚠️ KLASÖR YAPISI (EN KRİTİK — yanlışsa sistem KIRILIR)

İki repo **AYNI üst klasör** altında, **TAM ŞU İSİMLERLE** olmalı (kod göreli yol `_VAULT.parent / "trade-agent"` ve `../Obsidian Vault` kullanır):

```
<herhangi-bir-üst-klasör>/
├── Obsidian Vault/        ← asimetri-vault reposu (İSİM BİREBİR, boşluk dahil)
│   ├── CLAUDE.md  STATUS.md  data/  site/  scans/  ...
└── trade-agent/           ← trade-agent reposu (İSİM BİREBİR)
    ├── CLAUDE.md  run_aggressive.py  state/  ...
```

- Vault klasör adı **`Obsidian Vault`** (boşluklu) olmalı; trade-agent **`trade-agent`**.
- İkisi **aynı parent**'ta yan yana. Farklı isim/yer → `sync.sh` ve dashboard trade-agent'ı bulamaz.
- macOS'ta örnek üst klasör: `~/Documents/`. Yani `~/Documents/Obsidian Vault` + `~/Documents/trade-agent`.

---

## 3. REPOLARI AL (iki yol — biri)

### Yol A — GitHub erişimi varsa (private repo)
```bash
cd ~/Documents
git clone https://github.com/cank2001/asimetri-vault.git "Obsidian Vault"
git clone https://github.com/cank2001/trade-agent.git
```
(GitHub kullanıcı + token gerekir — repolar PRIVATE.)

### Yol B — Can klasörleri zip'leyip yolladıysa
Zip'leri `~/Documents/` altına aç; klasör adları **`Obsidian Vault`** ve **`trade-agent`** olsun.
- **`.venv` klasörlerini KOPYALAMA** (makineye-özel mutlak yol içerir, kırık olur) — Adım 4'te yeniden kurulur. Zaten genelde `.gitignore`'da.

---

## 4. PYTHON KURULUMU (iki ayrı venv)

```bash
# --- trade-agent ---
cd ~/Documents/trade-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt        # pytest (çekirdek katmanlar bağımlılıksız stdlib)
deactivate

# --- vault veri katmanı ---
cd ~/Documents/"Obsidian Vault"/data
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt        # yfinance + pytest (yfinance kırılırsa Stooq fallback)
deactivate
```

> **Otomasyon:** Bu adımı tek komutta yapmak için bu klasördeki **`setup.sh`** dosyasını kullan (Adım 9).

---

## 5. .ENV KURULUMU (gizli anahtarlar — çoğu OPSİYONEL)

```bash
# trade-agent (kripto) — anahtar GEREKMEZ; read mainnet-public, para yok
cd ~/Documents/trade-agent
cp .env.example .env
#   HL_TESTNET_KEY=        ← BOŞ bırakılabilir (sistem yalnız /info READ kullanır)
#   ONCHAIN_API_KEY=       ← BOŞ (ücretsiz kaynak yok)
#   HL_FORCE_TESTNET_READ= ← BOŞ (mainnet read varsayılan)

# vault veri (equity)
cd ~/Documents/"Obsidian Vault"/data
cp .env.example .env
#   SEC_USER_AGENT="Ad Soyad email@example.com"  ← ZORUNLU (EDGAR 403 vermesin); kendi adını yaz
#   FINNHUB_API_KEY=       ← OPSİYONEL (boşsa haber boş döner, tarama yine çalışır)
```

**Özet:** Kripto tarafı **sıfır anahtarla** çalışır (paper). Equity tarafı yalnız `SEC_USER_AGENT` ister (EDGAR kuralı; herhangi geçerli "Ad email" yeter).

---

## 6. DOĞRULAMA (kurulum sağlam mı — testler)

```bash
# trade-agent: 71 test (sizing/kaldıraç/izolasyon/short/agresif/dup-fix)
cd ~/Documents/trade-agent
.venv/bin/python -m pytest tests -q          # → "71 passed" beklenir

# vault dashboard testi (OPSİYONEL — Node gerekir)
cd ~/Documents/"Obsidian Vault"/site
npm install                                   # ilk sefer (playwright)
npx playwright install chromium               # tarayıcı indir
npx playwright test                           # → "17 passed"
```

Hepsi yeşilse kurulum sağlam.

---

## 7. ÇALIŞTIRMA — EQUITY TARAMA (Claude Code ile)

Equity tarama LLM agentlarıdır. Vault klasöründe **Claude Code aç** ve şunu de:
- Lowcap tarama: `lowcap-scan` agent'ını tetikle (haftalık COLD tarama).
- Solid tarama: `solid-scan` agent'ı.
- Her tarama `scans/YYYY-MM-DD.md` üretir; karar İNSANIN (`journal.md`).
- Detay: `Obsidian Vault/CLAUDE.md` "Haftalık döngü" + `.claude/agents/`.

> Bunlar Claude Code subagentları (`.claude/agents/lowcap-scan.md` vb.). Claude Code olmadan çalışmaz.

---

## 8. ÇALIŞTIRMA — KRİPTO A/B/C TURU (asıl motor)

**Sıra (ROUTINE.md'deki gibi):**
```bash
cd ~/Documents/trade-agent
.venv/bin/python capture_snapshot.py      # 1. ortak snapshot (4 varlık fiyat/funding/feature) → state/snapshot_latest.json
.venv/bin/python run_deterministic.py     # 2. deterministic-trader turu (kural, 1-5x) — Claude'suz çalışır
.venv/bin/python run_aggressive.py        # 2b. aggressive-trader turu (5-20x, %5 risk) — Claude'suz çalışır
# 3. deep-thinker: Claude Code'da .claude/agents/deep-thinker.md akışı → state/deepthinker_decision.json yaz
.venv/bin/python apply_deepthinker.py     # 4. deep-thinker kararını ORTAK sizing'le uygula
# 5. (ops) deep_scan.py + haber → MANUEL-DERIN journal (Derin Mod bağlamı)
git add -A && git commit -m "A/B/C turu" && git push   # 6. (repo bağlıysa)
bash ~/Documents/"Obsidian Vault"/data/scripts/sync.sh # 7. dashboard tazele
```

- **1, 2, 2b, 4** = saf Python (Claude'suz). **3 (deep-thinker)** = Claude Code gerekir.
- Üç agent **TAM İZOLE**: ayrı `state/positions_*.json` + `runs_*.jsonl` + ayrı $4000 bakiye.
- Çatı/akış dokümanı: `trade-agent/ROUTINE.md`.

---

## 9. DASHBOARD (cam)

```bash
# tazele (trade-agent pull + data.js üret):
bash ~/Documents/"Obsidian Vault"/data/scripts/sync.sh
# aç:
open ~/Documents/"Obsidian Vault"/site/index.html      # macOS — tarayıcıda açılır
```
- 5 tab: Genel (özet+3 equity çizgi+A/B/C metrik) · İşlemler · Runlar · Derin Mod · Equity.
- Statik; `data.js` snapshot. Her tur sonrası `sync.sh` çalıştır (otomatik değil).

---

## 10. OTOMATİK SAATLİK TUR (OPSİYONEL — lokal scheduled task)

Sistem saatlik otonom dönsün istiyorsan: Claude Code'da **scheduled task** kur (adı `ab-trader-turn`, cron `0 * * * *`), prompt = Adım 8 sırası. Detay: `trade-agent/ROUTINE.md` + Can'ın `~/.claude/scheduled-tasks/ab-trader-turn/SKILL.md`'si referans.
- **Yalnız PC/Claude açıkken** çalışır (kapalıyken o tur kaçar).
- Cloud routine ÇALIŞMAZ (Anthropic sandbox Hyperliquid'i blokluyor — `Host not in allowlist`).

---

## 11. STATE: DEVAM MI, TEMİZ BAŞLANGIÇ MI? (karar ver)

Repolar mevcut state'i (`state/positions_*.json`, `runs_*.jsonl`) içerir.
- **Devam (tıpatıp aynı geçmiş):** dokunma — sistem bıraktığı yerden sürer (det ~$3967, deep ~$3855, agg ~$2087, fwd 25/4/22).
- **Temiz başlangıç ($4000, fwd 0):** her `state/positions_*.json`'da `balance`/`equity`=4000, `forward_test_count`=0, `positions`={} yap; `state/runs_*.jsonl` dosyalarını boşalt. (Sıfırdan ölçüm.)

> Bakiye GERÇEK paper trade verisidir — temiz başlangıç istemiyorsan dokunma.

---

## 12. KRİTİK KURALLAR / SINIRLAR (oku — sistemin anayasası)

- **TESTNET/PAPER — GERÇEK PARA YOK.** Kripto emir endpoint'i bilerek tanımsız; mainnet emri imkânsız. Read mainnet-public (para yok).
- **Equity: karar İNSANIN.** AI al/sat demez; tez + gerekçeli görüş üretir.
- **Uydurma yok · point-in-time (leakage yok) · fee+funding dahil · tez≠fiyat.**
- **Faz disiplini:** faz İÇİNDE config sabit, değişiklik faz GEÇİŞİNDE + veriye dayalı (heves değil).
- Tam anayasa: `Obsidian Vault/CLAUDE.md`, `trade-agent/CLAUDE.md`, `trade-agent/strategy/`.

---

## 13. SIK SORUNLAR (troubleshooting)

| Belirti | Sebep | Çözüm |
|---|---|---|
| `sync.sh` trade-agent'ı bulamıyor | Klasör kardeş/isim yanlış | Adım 2: `Obsidian Vault` + `trade-agent` aynı parent, isim birebir |
| `ModuleNotFoundError` | venv kurulmadı/aktif değil | Adım 4; komutlarda `.venv/bin/python` kullan |
| Hyperliquid `Host not in allowlist` | Kısıtlı sandbox/ağ | Normal PC'de olmaz; cloud routine kullanma (Adım 10) |
| EDGAR `403` | `SEC_USER_AGENT` boş | Adım 5: `data/.env`'de "Ad email" yaz |
| yfinance hata/boş | yfinance kırılgan | Otomatik Stooq fallback'e düşer (bağımlılıksız); sorun değil |
| deep-thinker çalışmıyor | Claude Code yok | Adım 1: Claude Code kur (LLM kolu için zorunlu) |
| `.venv` taşındı/kırık | venv mutlak-yollu | Kopyalama; her PC'de yeniden kur (Adım 4) |
| dashboard eski veri | `sync.sh` çalışmadı | Her tur sonrası `bash data/scripts/sync.sh` |
| Python sözdizimi hatası | Python <3.11 | 3.11+ kur (Adım 1) |

---

## 14. DOSYA HARİTASI (hangi dosya ne — hızlı referans)

**trade-agent/**
- `capture_snapshot.py` → ortak snapshot (3 agent aynı veri). `run_deterministic.py` / `run_aggressive.py` → kural kolları. `apply_deepthinker.py` → LLM kolu uygula. `run_turn.py` → ORTAK motor (sizing/kaldıraç/P&L/log).
- `execution/sizing.py` (%1.5 det / %5 agg risk) · `leverage.py` (5x det / 5-20x agg + likidasyon kapısı) · `decision.py` · `autonomous.py` (stop/target path-check).
- `features/` (indicators, trend) · `triggers/rules.py` (LLM ne zaman) · `data/` (ohlcv, funding).
- `.claude/agents/` (deep-thinker, challenger, trader-scan/refresh) · `strategy/` (lessons, candidate-factors, vizyon) · `state/` (positions/runs — CANLI) · `journal/` · `ROUTINE.md` · `CLAUDE.md`.

**Obsidian Vault/**
- `site/` (index.html + app.js + style.css + data.js) → dashboard. `data/scripts/refresh_site_data.py` → data.js üret · `sync.sh` → tek-komut tazele · `data/scripts/*.py` (EDGAR/fiyat/scoring/confidence).
- `.claude/agents/` (lowcap/solid scan+refresh, challenger) · `_engine/` (framework, lessons, track-record) · `scans/` · `watchlist.md` · `journal.md` · `portfolio.md` · `CLAUDE.md` · `STATUS.md`.

---

## ✅ HIZLI BAŞLANGIÇ (özet — bu 6 komut + Claude Code)
```bash
cd ~/Documents
git clone <vault-url> "Obsidian Vault" && git clone <trade-agent-url>     # veya zip aç
bash ~/Documents/asimetri-KURULUM/setup.sh                                 # venv+pip+.env (bu klasördeki script)
cd ~/Documents/trade-agent && .venv/bin/python -m pytest tests -q          # 71 passed
.venv/bin/python capture_snapshot.py && .venv/bin/python run_deterministic.py && .venv/bin/python run_aggressive.py
bash ~/Documents/"Obsidian Vault"/data/scripts/sync.sh && open ~/Documents/"Obsidian Vault"/site/index.html
```
deep-thinker kolu + equity taramaları için: ilgili repoda **Claude Code aç**, agent'ı tetikle.

— SON —
