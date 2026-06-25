"""
run_turn.py — A/B tur orkestratörü.
Ne yapar: capture_snapshot → run_deterministic → deep-thinker analizi → apply_deepthinker → log
Neden: tek komutla tam turu çalıştırır, saatlik scheduled task bunu çağırır.
"""

import subprocess
import sys
import json
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
    print(f"=== A/B TUR BAŞLADI — {datetime.now(timezone.utc).isoformat()} ===")

    if not run("capture_snapshot.py"):
        print("Snapshot başarısız — tur durdu.")
        return

    run("run_deterministic.py")

    print("\n▶ deep-thinker: snapshot okundu, analiz için Claude Code gerekli")
    print("  Not: deep-thinker analizi manuel tetik ile claude.ai'den yapılıyor.")

    run("apply_deepthinker.py")

    print(f"\n=== TUR TAMAMLANDI — {datetime.now(timezone.utc).isoformat()} ===")

if __name__ == "__main__":
    main()
