"""
run_turn.py — A/B/C tur orkestratörü.
Ne yapar: capture_snapshot → run_deterministic (A) → run_aggressive (C) → deep-thinker (B) → apply_deepthinker → git push
Neden: tek komutla tam turu çalıştırır, saatlik scheduled task bunu çağırır.
B kolu (deep-thinker) LLM gerektirir: ANTHROPIC_API_KEY varsa SDK, yoksa headless `claude -p`.
LLM erişilemezse güvenli all-WAIT yazıp nonzero çıkar — tur yine de güvenle ilerler.
"""

import subprocess
from datetime import datetime, timezone

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
    print(f"=== A/B/C TUR BAŞLADI — {datetime.now(timezone.utc).isoformat()} ===")

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

    print(f"\n=== TUR TAMAMLANDI — {datetime.now(timezone.utc).isoformat()} ===")

    git_push()

def git_push():
    subprocess.run(["git", "add", "-A"], cwd=".")
    subprocess.run(["git", "commit", "-m", f"tur: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M')}"], cwd=".")
    subprocess.run(["git", "push"], cwd=".")
    print("Git push tamamlandi.")

if __name__ == "__main__":
    main()
