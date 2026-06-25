"""
apply_deepthinker.py — deep-thinker kararlarını uygular.
Ne yapar: deepthinker_decision.json'u okur, sizing hesaplar, pozisyonları açar/kapatır.
Neden: deep-thinker LLM karar üretir, bu script kararı deterministic sizing ile uygular.
Çıktı: state/positions_deepthinker.json + runs_deepthinker.jsonl
"""

import json
from datetime import datetime, timezone

RISK_PCT = 0.015
MAX_POS_PCT = 0.30
TAKER_FEE = 0.00035

def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def append_jsonl(path, record):
    with open(path, "a") as f:
        f.write(json.dumps(record) + "\n")

def compute_sizing(balance, entry, stop):
    stop_dist = abs(entry - stop) / entry
    if stop_dist == 0:
        return 0, 0
    risk_usd = balance * RISK_PCT
    notional = risk_usd / stop_dist
    notional = min(notional, balance * MAX_POS_PCT)
    leverage = min(round(notional / balance, 2), 5.0)
    return round(notional, 2), leverage

def check_path(position, asset):
    price = asset["price"]
    side = position["side"]
    stop = position["stop"]
    target = position["target"]
    if side == "buy":
        if price <= stop:
            return "stop_hit"
        if price >= target:
            return "target_hit"
    else:
        if price >= stop:
            return "stop_hit"
        if price <= target:
            return "target_hit"
    return "open"

def main():
    snapshot = load_json("state/snapshot_latest.json")
    state = load_json("state/positions_deepthinker.json", {"phase": "faz1", "balance": 4000, "positions": {}})
    decision = load_json("state/deepthinker_decision.json", {"decisions": {}, "waits": {}})

    if not snapshot:
        print("Snapshot yok — önce capture_snapshot.py çalıştır.")
        return

    balance = state["balance"]
    positions = state.get("positions", {})
    timestamp = datetime.now(timezone.utc).isoformat()
    log = []

    # Açık pozisyonları kontrol et
    to_close = []
    for coin, pos in positions.items():
        asset = snapshot["assets"].get(coin)
        if not asset:
            continue
        status = check_path(pos, asset)
        if status in ("stop_hit", "target_hit"):
            price = asset["price"]
            entry = pos["entry"]
            side = pos["side"]
            pnl_pct = ((price - entry) / entry) if side == "buy" else ((entry - price) / entry)
            fee = pos["notional"] * TAKER_FEE * 2
            net_pnl = pos["notional"] * pnl_pct - fee
            balance = round(balance + net_pnl, 2)
            to_close.append(coin)
            log.append({"coin": coin, "action": status, "net_pnl": round(net_pnl, 2), "price": price})
            print(f"  KAPANDI {coin} {status}: {round(pnl_pct*100,2)}% net ${round(net_pnl,2)}")

    for coin in to_close:
        del positions[coin]

    # deep-thinker kararlarını uygula
    for coin, params in decision.get("decisions", {}).items():
        if coin in positions:
            print(f"  {coin} zaten açık — atlandı")
            continue
        entry = params["entry"]
        stop = params["stop"]
        notional, leverage = compute_sizing(balance, entry, stop)
        if notional > 0:
            positions[coin] = {
                "side": params["side"],
                "entry": entry,
                "stop": stop,
                "target": params["target"],
                "notional": notional,
                "leverage": leverage,
                "confidence": params.get("confidence"),
                "thesis": params.get("thesis"),
                "decided_at": timestamp,
            }
            log.append({"coin": coin, "action": "open_new", "side": params["side"], "entry": entry})
            print(f"  AÇILDI {coin} {params['side']}: ${entry} stop:${stop} target:${params['target']}")

    # Wait log
    for coin, reason in decision.get("waits", {}).items():
        print(f"  WAIT {coin}: {reason}")
        log.append({"coin": coin, "action": "wait", "reason": reason})

    # Açık pozisyon durumu
    for coin, pos in positions.items():
        if coin not in decision.get("decisions", {}):
            asset = snapshot["assets"].get(coin, {})
            price = asset.get("price", pos["entry"])
            pnl_pct = ((price - pos["entry"]) / pos["entry"]) if pos["side"] == "buy" else ((pos["entry"] - price) / pos["entry"])
            print(f"  AÇIK {coin}: ${price} K/Z {round(pnl_pct*100,2)}%")

    state["balance"] = balance
    state["positions"] = positions
    save_json("state/positions_deepthinker.json", state)

    run_record = {
        "timestamp": timestamp,
        "agent": "deepthinker",
        "balance": balance,
        "regime": snapshot.get("regime"),
        "log": log,
    }
    append_jsonl("runs_deepthinker.jsonl", run_record)
    print(f"\nTamamlandı. Bakiye: ${balance} | Açık pozisyon: {len(positions)}")

if __name__ == "__main__":
    main()
