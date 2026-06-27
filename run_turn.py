"""
run_turn.py — A/B/C tur orkestratörü (ROUTINE.md / KURULUM Adım 8 akışı, BİREBİR).
Ne yapar (7 adım): capture_snapshot → run_deterministic (A) → run_aggressive (C)
  → deep-thinker (B) → apply_deepthinker → deep_scan (gözlem journal) → git push → sync.sh (dashboard).
Neden: tek komutla tam turu çalıştırır, saatlik scheduled task bunu çağırır.
B kolu (deep-thinker) API KEY GEREKTİRMEZ: ANTHROPIC_API_KEY boş → headless `claude -p`
  (Claude Code girişiyle). LLM erişilemezse güvenli all-WAIT yazılır — tur yine de ilerler.
"""

import os
import subprocess
from datetime import datetime, timezone

SYNC_SH = "../Obsidian Vault/data/scripts/sync.sh"

PYTHON = ".venv/bin/python"

def run(script):
    print(f"\n▶ {script}")
    result = subprocess.run([PYTHON, script], capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"HATA: {result.stderr}")
        return False
    return True

def main():
    print(f"=== A/B/C/D TUR BAŞLADI — {datetime.now(timezone.utc).isoformat()} ===")

    if not run("capture_snapshot.py"):
        print("Snapshot başarısız — tur durdu.")
        return

    run("run_deterministic.py")   # A kolu (kural, %1.5 risk / 5x)
    run("run_aggressive.py")      # C kolu (kural, %5 risk / 20x) — TAM İZOLE

    print("\n▶ deep-thinker: agent kuralları + GÜNCEL snapshot → taze analyst/challenger kararı")
    # run_deepthinker.py eski karar dosyasını okumaz; her tur taze yazar.
    # LLM erişilemezse güvenli all-WAIT yazıp nonzero çıkar — tur yine de güvenle ilerler.
    if not run("run_deepthinker.py"):
        print("  Not: deep-thinker LLM üretmedi; güvenli WAIT kararı ile devam ediliyor.")

    run("apply_deepthinker.py")   # B kolu kararını ORTAK sizing ile uygula

    print("\n▶ psikomanyak: aşırı-risk LLM kolu (D) — tek-en-iyi momentum fırsatı, 5-20x")
    # D kolu TAM İZOLE (ayrı $4000/state); A/B/C ölçümüne KARIŞMAZ. LLM erişilemezse güvenli WAIT.
    if not run("run_psikomanyak.py"):
        print("  Not: psikomanyak LLM üretmedi; güvenli WAIT ile devam.")
    run("apply_psikomanyak.py")   # D kolu kararını İZOLE sizing ile uygula (notional≤1× / 5-20x)

    run("deep_scan.py")           # 5. PARALEL GÖZLEM → journal/MANUEL-DERIN-*.md (karara GİRMEZ)

    print(f"\n=== TUR TAMAMLANDI — {datetime.now(timezone.utc).isoformat()} ===")

    git_push()                    # 6. iki agent + gözlem journal → repo
    sync_dashboard()              # 7. dashboard tazele (vault site/data.js)

def git_push():
    subprocess.run(["git", "add", "-A"], cwd=".")
    subprocess.run(["git", "commit", "-m", f"tur: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M')}"], cwd=".")
    subprocess.run(["git", "push"], cwd=".")
    print("Git push tamamlandi.")

def sync_dashboard():
    """7. adım: vault dashboard'ını tazele (yalnız lokalde; vault yoksa atla)."""
    if not os.path.exists(SYNC_SH):
        print(f"  Not: sync.sh yok ({SYNC_SH}) — dashboard tazelenmedi (vault bu makinede yok?).")
        return
    print("\n▶ sync.sh — dashboard tazeleniyor")
    r = subprocess.run(["bash", SYNC_SH], capture_output=True, text=True)
    if r.stdout:
        print(r.stdout)
    if r.returncode != 0:
        print(f"  Not: sync.sh hata: {(r.stderr or '').strip()[:200]}")
    else:
        print("Dashboard tazelendi.")

if __name__ == "__main__":
    main()
