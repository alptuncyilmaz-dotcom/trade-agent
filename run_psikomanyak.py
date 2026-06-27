"""
run_psikomanyak.py — D kolu (psikomanyak) için TAZE karar üretir.
Ne yapar: .claude/agents/psikomanyak.md mandasını + GÜNCEL snapshot'ı okur; aşırı-risk iştahlı
          bir LLM'e 4 varlıktan TEK-EN-İYİ momentum fırsatını seçtirir (maks 1 poz, 5-20x);
          state/psikomanyak_decision.json'a yazar. apply_psikomanyak.py uygular.
LLM:      API KEY GEREKTİRMEZ — run_deepthinker.call_llm (headless `claude -p`, Claude Code girişi).
          Erişilemezse güvenli WAIT yazar. TESTNET/PAPER — gerçek para YOK.
"""

import json
import sys

from execution import autonomous
from run_deepthinker import call_llm, extract_json, read_text  # tek kaynak: aynı no-API-key mekanizma

AGENT = ".claude/agents/psikomanyak.md"
SNAPSHOT = "state/snapshot_latest.json"
DECISION = "state/psikomanyak_decision.json"
COINS = ["BTC", "ETH", "XRP", "HYPE"]


def build_prompt(rules, context):
    return f"""Sen psikomanyak'sın: AŞIRI YÜKSEK RİSK iştahlı kripto perp trader (TESTNET/PAPER — GERÇEK PARA YOK; bilerek patlaması serbest).
Aşağıdaki mandaya göre davran. Turlar arası ÖĞRENME yok; sadece bu snapshot.

=== psikomanyak.md (manda + araştırılmış strateji) ===
{rules}

=== GÜNCEL SNAPSHOT BAĞLAMI (kural-bazlı ön-değerlendirme — SENİ BAĞLAMAZ, yalnız referans) ===
# 'gate'/'reference_levels' muhafazakâr kol içindir; psikomanyak bunları AŞABİLİR (counter-trend/range serbest).
{json.dumps(context, indent=2)}

Görev: {", ".join(COINS)} arasından **TEK-EN-İYİ yüksek-momentum fırsatını** seç (maks 1 pozisyon). Momentum/breakout/funding-hizası ara; psikomanyak risk sever → eğilim AÇMAK yönünde, ama gerçekten hiçbir edge yoksa WAIT.
- side "buy" (long) veya "sell" (short). Asimetri: buy → stop<entry<target ; sell → target<entry<stop.
- entry/stop/target snapshot'taki price/atr'den TÜRET (uydurma yok). Stop ~%2 veya 1.5×ATR; target ~2-2.75× stop mesafesi.
- leverage: 5 ile 20 arası bir sayı (sen seç; risk iştahına göre).

ÇIKTI: SADECE şu şemada TEK JSON, başka metin/markdown YOK:
{{
  "decision": {{"coin":"BTC","side":"buy|sell","entry":0,"stop":0,"target":0,"leverage":10,"thesis":"...","detailed_rationale":"..."}},
  "wait_reason": null
}}
Fırsat yoksa: {{"decision": null, "wait_reason": "kısa neden"}}. decision VARSA tek coin olmalı."""


def write_decision(decision, wait_reason, meta):
    payload = {"decision": decision, "wait_reason": wait_reason, "_meta": meta}
    with open(DECISION, "w") as f:
        json.dump(payload, f, indent=2)


def main():
    snapshot = json.load(open(SNAPSHOT))
    print(f"  psikomanyak: snapshot {snapshot['timestamp']} (rejim: {snapshot['regime']}) okundu")

    context = autonomous.build_decision_context(snapshot)
    prompt = build_prompt(read_text(AGENT), context)
    text, err = call_llm(prompt)

    if err:
        write_decision(None, f"LLM erişilemedi ({err}) — güvenli WAIT", {"llm": "unavailable", "error": err})
        print(f"  ⚠ LLM erişilemedi: {err} → WAIT")
        sys.exit(2)

    try:
        parsed = extract_json(text)
    except Exception as e:
        write_decision(None, f"parse hatası ({e}) — WAIT", {"llm": "parse_error", "raw": text[:400]})
        print(f"  ⚠ Parse hatası: {e} → WAIT")
        sys.exit(2)

    decision = parsed.get("decision")
    wait_reason = parsed.get("wait_reason")
    write_decision(decision, wait_reason, {"llm": "ok", "snapshot_ts": snapshot["timestamp"]})

    if decision:
        print(f"  KARAR: {decision.get('coin')} {decision.get('side')} entry {decision.get('entry')} "
              f"stop {decision.get('stop')} target {decision.get('target')} lev {decision.get('leverage')}x")
        print(f"    tez: {decision.get('thesis','')}")
    else:
        print(f"  WAIT: {wait_reason}")
    print(f"  → {DECISION} yazıldı.")


if __name__ == "__main__":
    main()
