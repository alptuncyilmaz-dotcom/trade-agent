"""
apply_psikomanyak.py — D kolu (psikomanyak) kararını uygular. TAM İZOLE.
Ne yapar: psikomanyak_decision.json'u okur; maks 1 açık poz kuralıyla açar/kapatır.
Boyut:   notional = 1× bakiye (≤$4000 cap); kaldıraç = LLM seçimi [5,20]'ye kıstırılmış
         (muhafazakâr vol/liq kapıları YOK — psikomanyak likidasyon riskini kucaklar).
Maliyet/kapanış: simulator (fee-only, Faz-1) — diğer kollarla aynı motor.
Çıktı:   state/positions_psikomanyak.json + runs_psikomanyak.jsonl
TESTNET/PAPER — GERÇEK PARA YOK.
"""

import json
from datetime import datetime, timezone

from execution import simulator

STATE = "state/positions_psikomanyak.json"
DECISION = "state/psikomanyak_decision.json"
RUNS = "runs_psikomanyak.jsonl"
POS_PCT = 1.0      # notional = 1× bakiye (≤$4k cap)
LEV_MIN, LEV_MAX = 5.0, 20.0
MAX_POS = 2        # aynı anda maks açık pozisyon (2026-06-28: 1→2, daha aktif gözlem)


def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def append_jsonl(path, record):
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")


def valid_levels(side, entry, stop, target):
    """buy: stop<entry<target ; sell: target<entry<stop."""
    if side == "buy":
        return stop < entry < target
    if side == "sell":
        return target < entry < stop
    return False


def main():
    snapshot = load_json(SNAPSHOT := "state/snapshot_latest.json")
    state = load_json(STATE, {"phase": "faz1", "balance": 4000, "positions": {}})
    dec = load_json(DECISION, {"decision": None, "wait_reason": "karar yok"})

    if not snapshot:
        print("Snapshot yok — önce capture_snapshot.py çalıştır.")
        return

    balance = state["balance"]
    positions = state.get("positions", {})
    timestamp = datetime.now(timezone.utc).isoformat()
    log = []

    # --- Açık pozisyonu kontrol et / kapat (maks 1) ---
    to_close = []
    for coin, pos in positions.items():
        asset = snapshot["assets"].get(coin)
        if not asset:
            continue
        price = asset["price"]
        status = simulator.check_path(pos, price)
        if status in ("stop_hit", "target_hit"):
            res = simulator.simulate_trade(pos["side"], pos["entry"], price, pos["notional"],
                                           funding_rate=0.0, funding_periods=0, slippage_bps=0.0)
            balance = round(balance + res.net_pnl, 2)
            pnl_pct = (res.gross_pnl / pos["notional"] * 100) if pos["notional"] else 0.0
            to_close.append(coin)
            log.append({"coin": coin, "action": status, "net_pnl": round(res.net_pnl, 2), "price": price})
            print(f"  KAPANDI {coin} {status}: {round(pnl_pct,2)}% net ${round(res.net_pnl,2)}")
        else:
            pnl_pct = ((price - pos["entry"]) / pos["entry"]) if pos["side"] == "buy" else ((pos["entry"] - price) / pos["entry"])
            print(f"  AÇIK {coin}: ${price} K/Z {round(pnl_pct*100,2)}%")

    for coin in to_close:
        del positions[coin]

    # --- Yeni karar: maks MAX_POS poz; dolu ya da aynı coin zaten açıksa AÇMA ---
    decision = dec.get("decision")
    dcoin = decision.get("coin") if decision else None
    if decision and dcoin in positions:
        print(f"  {dcoin} zaten açık — atlandı.")
        log.append({"coin": dcoin, "action": "skip_dup", "reason": "zaten açık"})
    elif len(positions) >= MAX_POS:
        print(f"  Açık poz dolu ({list(positions)}) — maks {MAX_POS}, yeni açılmadı.")
        if decision:
            log.append({"coin": dcoin, "action": "skip_max", "reason": f"maks {MAX_POS} poz dolu"})
    elif decision:
        coin = decision.get("coin")
        side = decision.get("side")
        entry = float(decision.get("entry", 0) or 0)
        stop = float(decision.get("stop", 0) or 0)
        target = float(decision.get("target", 0) or 0)
        lev = decision.get("leverage", LEV_MIN)
        try:
            lev = max(LEV_MIN, min(LEV_MAX, float(lev)))   # [5,20]'ye kıstır
        except (TypeError, ValueError):
            lev = LEV_MIN
        if not valid_levels(side, entry, stop, target):
            print(f"  ⚠ GEÇERSİZ seviye {coin} {side} (entry {entry} stop {stop} target {target}) — açılmadı.")
            log.append({"coin": coin, "action": "invalid_levels", "side": side, "entry": entry, "stop": stop, "target": target})
        else:
            notional = round(balance * POS_PCT, 2)         # 1× bakiye ≤ $4k
            positions[coin] = {
                "side": side, "entry": entry, "stop": stop, "target": target,
                "notional": notional, "leverage": round(lev, 2),
                "thesis": decision.get("thesis"), "decided_at": timestamp,
            }
            log.append({"coin": coin, "action": "open_new", "side": side, "entry": entry,
                        "notional": notional, "leverage": round(lev, 2)})
            print(f"  AÇILDI {coin} {side}: ${entry} stop:${stop} target:${target} (notional ${notional} lev {round(lev,2)}x)")
    else:
        print(f"  WAIT: {dec.get('wait_reason')}")
        log.append({"action": "wait", "reason": dec.get("wait_reason")})

    state["balance"] = balance
    state["positions"] = positions
    save_json(STATE, state)

    append_jsonl(RUNS, {"timestamp": timestamp, "agent": "psikomanyak", "balance": balance,
                        "regime": snapshot.get("regime"), "log": log})
    print(f"\nTamamlandı. Bakiye: ${balance} | Açık pozisyon: {len(positions)}")


if __name__ == "__main__":
    main()
