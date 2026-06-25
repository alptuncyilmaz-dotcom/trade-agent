"""
run_deepthinker.py — A/B'nin LLM kolu (deep-thinker) için TAZE karar üretir.
Ne yapar: .claude/agents/deep-thinker.md + challenger.md kurallarını ve state/snapshot_latest.json'daki
          GÜNCEL veriyi okur; her varlık için analyst→challenger→karar yaptırır; demir-kural guard'larından
          geçirip kararı state/deepthinker_decision.json'a YENİDEN yazar.
Neden:    Eski karar dosyası asla yeniden kullanılmaz — her tur taze analiz. apply_deepthinker.py bu dosyayı uygular.
LLM:      Headless `claude -p` (veya ANTHROPIC_API_KEY varsa anthropic SDK). Erişilemezse güvenli all-WAIT yazar.
"""

import json
import os
import re
import subprocess
import sys

AGENT_DT = ".claude/agents/deep-thinker.md"
AGENT_CH = ".claude/agents/challenger.md"
SNAPSHOT = "state/snapshot_latest.json"
DECISION = "state/deepthinker_decision.json"
COINS = ["BTC", "ETH", "XRP", "HYPE"]


def read_text(path):
    with open(path) as f:
        return f.read()


def build_prompt(dt_rules, ch_rules, snapshot):
    return f"""Sen deep-thinker'sın: kripto perp OTONOM trader (TESTNET/PAPER — gerçek para YOK).
Aşağıdaki anayasaya HARFİYEN uy. Turlar arası ÖĞRENME yok; sadece bu snapshot'a bak.

=== deep-thinker.md ===
{dt_rules}

=== challenger.md ===
{ch_rules}

=== GÜNCEL SNAPSHOT (state/snapshot_latest.json) ===
{json.dumps(snapshot, indent=2)}

Görev: {", ".join(COINS)} varlıklarının HER BİRİ için sırayla:
1. ANALYST: tez + side/entry/stop/target/confidence.
2. CHALLENGER: aynı tezi farklı lensten çürüt (karar verme, boş itiraz yok).
3. KARAR: trade aç YA DA WAIT.

Demir kurallar (ihlal = otomatik WAIT'e düşürülür):
- Counter-trend açma YASAK (1d down iken buy yok; 1d up iken sell yok).
- 1d trend "range" ise WAIT (range-HTF).
- Geçerli trigger yoksa kural-bazlı kanıt zayıf → WAIT eğilimli ol (over-trading fee sessiz katil — L-03).
- RSI>65 = H-03 geç-giriş riski.
- Uydurma seviye yok; entry/stop/target snapshot'taki price/atr'den türet.
- Sıralama: buy → stop < entry < target ; sell(short) → target < entry < stop.

ÇIKTI: SADECE aşağıdaki şemada tek bir JSON nesnesi döndür, başka hiçbir metin/markdown yok:
{{
  "analysis": {{ "BTC": {{"analyst": "...", "challenger": "..."}} }},
  "decisions": {{ "BTC": {{"side":"buy|sell","entry":0,"stop":0,"target":0,"confidence":"low|medium|high","thesis":"...","detailed_rationale":"..."}} }},
  "waits": {{ "ETH": "kısa neden" }}
}}
Trade açılmayan varlık "waits"e, açılan "decisions"a girer. Her varlık ya decisions ya waits'te olmalı."""


def cli_env():
    """Headless `claude -p` için temiz env: host-enjekte nested oturum değişkenlerini
    soyar (bunlar CLI'yi host-auth bekler hale getirip 'Not logged in' yapar) ve
    setup-token'ı ~/.claude/.credentials.json'dan CLAUDE_CODE_OAUTH_TOKEN olarak geçirir."""
    env = dict(os.environ)
    for k in ("CLAUDECODE", "CLAUDE_CODE_CHILD_SESSION", "CLAUDE_CODE_ENTRYPOINT",
              "CLAUDE_CODE_EXECPATH", "CLAUDE_CODE_SESSION_ID", "CLAUDE_AGENT_SDK_VERSION",
              "CLAUDE_CODE_SDK_HAS_OAUTH_REFRESH", "CLAUDE_CODE_SDK_HAS_HOST_AUTH_REFRESH"):
        env.pop(k, None)
    if not env.get("CLAUDE_CODE_OAUTH_TOKEN"):
        creds = os.path.expanduser("~/.claude/.credentials.json")
        try:
            tok = json.load(open(creds)).get("oauth_token")
            if tok:
                env["CLAUDE_CODE_OAUTH_TOKEN"] = tok
        except (OSError, ValueError):
            pass
    return env


def call_llm(prompt):
    """(text, error) döndürür. Önce ANTHROPIC_API_KEY/SDK, yoksa headless claude CLI."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            client = anthropic.Anthropic()
            model = os.environ.get("DT_MODEL", "claude-opus-4-8")
            msg = client.messages.create(
                model=model, max_tokens=4000,
                messages=[{"role": "user", "content": prompt}],
            )
            return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text"), None
        except Exception as e:
            return None, f"SDK hata: {e}"

    cmd = ["claude", "-p", prompt, "--output-format", "text"]
    if os.environ.get("DT_MODEL"):
        cmd += ["--model", os.environ["DT_MODEL"]]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=cli_env())
    except FileNotFoundError:
        return None, "claude CLI bulunamadı"
    except subprocess.TimeoutExpired:
        return None, "claude CLI timeout"
    out = (r.stdout or "").strip()
    low = out.lower()
    auth_fail = any(s in low for s in ("not logged in", "invalid bearer", "failed to authenticate", "401"))
    if r.returncode != 0 or auth_fail or not out:
        return None, f"claude CLI başarısız: {(r.stderr or out or 'boş çıktı').strip()[:200]}"
    return out, None


def extract_json(text):
    """LLM çıktısından ilk geçerli JSON nesnesini çıkarır (markdown fence toleranslı)."""
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fence.group(1) if fence else text
    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("JSON nesnesi bulunamadı")
    return json.loads(candidate[start:end + 1])


def guard(decisions, waits, snapshot):
    """Demir-kural güvenlik ağı: ihlal eden kararları WAIT'e düşürür."""
    safe_dec, safe_wait = {}, dict(waits or {})
    for coin, p in (decisions or {}).items():
        asset = snapshot["assets"].get(coin)
        if not asset:
            continue

        def demote(reason):
            safe_wait[coin] = f"guard: {reason}"

        side = p.get("side")
        if side not in ("buy", "sell"):
            demote(f"geçersiz side '{side}'"); continue
        try:
            entry, stop, target = float(p["entry"]), float(p["stop"]), float(p["target"])
        except (KeyError, TypeError, ValueError):
            demote("entry/stop/target eksik veya sayısal değil"); continue
        if min(entry, stop, target) <= 0:
            demote("seviye <= 0"); continue
        if asset["trends"]["1d"] == "range":
            demote("range-HTF (1d range) → WAIT"); continue
        if side == "buy" and asset["is_counter_trend_long"]:
            demote("counter-trend long (1d down)"); continue
        if side == "sell" and asset["is_counter_trend_short"]:
            demote("counter-trend short (1d up)"); continue
        if side == "buy" and not (stop < entry < target):
            demote("buy sıralama bozuk (stop<entry<target değil)"); continue
        if side == "sell" and not (target < entry < stop):
            demote("short sıralama bozuk (target<entry<stop değil)"); continue
        safe_dec[coin] = p
    return safe_dec, safe_wait


def write_decision(decisions, waits, analysis=None, meta=None):
    payload = {"decisions": decisions, "waits": waits}
    if analysis:
        payload["analysis"] = analysis
    if meta:
        payload["_meta"] = meta
    with open(DECISION, "w") as f:
        json.dump(payload, f, indent=2)


def all_wait(snapshot, reason):
    return {c: reason for c in snapshot["assets"].keys()}


def main():
    snapshot = json.load(open(SNAPSHOT))
    print(f"  deep-thinker: snapshot {snapshot['timestamp']} (rejim: {snapshot['regime']}) okundu")

    prompt = build_prompt(read_text(AGENT_DT), read_text(AGENT_CH), snapshot)
    text, err = call_llm(prompt)

    if err:
        # LLM erişilemedi: stale kararı ASLA yeniden kullanma → güvenli all-WAIT yaz.
        waits = all_wait(snapshot, f"LLM erişilemedi ({err}) — güvenli WAIT")
        write_decision({}, waits, meta={"llm": "unavailable", "error": err, "snapshot_ts": snapshot["timestamp"]})
        print(f"  ⚠ LLM erişilemedi: {err}")
        print("  → Güvenli all-WAIT yazıldı (stale karar kullanılmadı).")
        for c, r in waits.items():
            print(f"    WAIT {c}: {r}")
        sys.exit(2)

    try:
        parsed = extract_json(text)
    except Exception as e:
        waits = all_wait(snapshot, f"LLM çıktısı parse edilemedi ({e}) — güvenli WAIT")
        write_decision({}, waits, meta={"llm": "parse_error", "error": str(e), "raw": text[:500]})
        print(f"  ⚠ Parse hatası: {e}")
        sys.exit(2)

    analysis = parsed.get("analysis", {})
    for coin in COINS:
        a = analysis.get(coin, {})
        if a:
            print(f"\n  — {coin} —")
            print(f"    ANALYST: {a.get('analyst', '')}")
            print(f"    CHALLENGER: {a.get('challenger', '')}")

    decisions, waits = guard(parsed.get("decisions", {}), parsed.get("waits", {}), snapshot)
    write_decision(decisions, waits, analysis=analysis,
                   meta={"llm": "ok", "snapshot_ts": snapshot["timestamp"]})

    print("\n  KARAR (taze):")
    for coin, p in decisions.items():
        print(f"    {coin} {p['side']}: entry {p['entry']} stop {p['stop']} target {p['target']} ({p.get('confidence')})")
    for coin, r in waits.items():
        print(f"    WAIT {coin}: {r}")
    print(f"\n  → {DECISION} yazıldı (eski dosya kullanılmadı).")


if __name__ == "__main__":
    main()
