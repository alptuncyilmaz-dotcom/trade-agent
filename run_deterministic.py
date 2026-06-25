"""
run_deterministic.py — Kural bazlı A/B kolu (deterministic-trader).
Ne yapar: snapshot'tan RSI/MACD/trend kurallarıyla karar verir, pozisyon açar/kapatır.
Neden: LLM olmadan saf kural performansını ölçmek (A/B testi A kolu).
Çıktı: state/positions_deterministic.json + runs_deterministic.jsonl
"""

import json
import time
from datetime import datetime, timezone

RISK_PCT = 0.015       # trade başına maks kayıp %1.5
MAX_POS_PCT = 0.30     # tek pozisyon maks %30
TAKER_FEE = 0.00035    # %0.035 taker fee

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

def decide(asset):
    rsi = asset["rsi"]
    macd_hist = asset["macd_hist"]
    trend_1d = asset["trends"]["1d"]
    trigger = asset["trigger"]

    if not trigger:
        return "wait", None, "trigger yok"

    if trend_1d == "range":
        return "wait", None, "range-HTF, edge yok"

    if trend_1d == "up":
        if asset["is_counter_trend_long"] == False:
            side = "buy"
            entry = asset["price"]
            atr = asset["atr"]
            stop = round(entry - 1.5 * atr, 4)
            target = round(entry + 3.0 * atr, 4)
            return "open", {"side": side, "entry": entry, "stop": stop, "target": target}, "HTF up + trigger"
        else:
            return "wait", None, "counter-trend long yasak"

    if trend_1d == "down":
        side = "sell"
        entry = asset["price"]
        atr = asset["atr"]
        stop = round(entry + 1.5 * atr, 4)
        target = round(entry - 3.0 * atr, 4)
        return "open", {"side": side, "entry": entry, "stop": stop, "target": target}, "HTF down + trigger"

    return "wait", None, "karar yok"

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
    state = load_json("state/positions_deterministic.json", {"phase": "faz1", "balance": 4000, "positions": {}})

    if not snapshot:
        print("Snapshot yok — önce capture_snapshot.py çalıştır.")
        return

    balance = state["balance"]
    positions = state.get("positions", {})
    timestamp = datetime.now(timezone.utc).isoformat()
    decisions = []

    # Açık pozisyonları kontrol et
    to_close = []
    for coin, pos in positions.items():
        asset = snapshot["assets"].get(coin)
        if not asset:
            continue
        status = check_path(pos, asset)
        if status in ("stop_hit", "target_hit"):
            entry = pos["entry"]
            price = asset["price"]
            side = pos["side"]
            pnl_pct = ((price - entry) / entry) if side == "buy" else ((entry - price) / entry)
            fee = pos["notional"] * TAKER_FEE * 2
            net_pnl = pos["notional"] * pnl_pct - fee
            balance = round(balance + net_pnl, 2)
            to_close.append(coin)
            decisions.append({"coin": coin, "action": status, "net_pnl": round(net_pnl, 2), "price": price})
            print(f"  KAPANDI {coin} {status}: {round(pnl_pct*100,2)}% net ${round(net_pnl,2)}")

    for coin in to_close:
        del positions[coin]

    # Yeni pozisyon kararları
    for coin, asset in snapshot["assets"].items():
        if coin in positions:
            price = asset["price"]
            pos = positions[coin]
            pnl_pct = ((price - pos["entry"]) / pos["entry"]) if pos["side"] == "buy" else ((pos["entry"] - price) / pos["entry"])
            print(f"  AÇIK {coin}: ${price} K/Z {round(pnl_pct*100,2)}%")
            decisions.append({"coin": coin, "action": "open", "price": price, "pnl_pct": round(pnl_pct*100,2)})
            continue

        action, params, reason = decide(asset)
        if action == "open":
            notional, leverage = compute_sizing(balance, params["entry"], params["stop"])
            if notional > 0:
                positions[coin] = {
                    "side": params["side"],
                    "entry": params["entry"],
                    "stop": params["stop"],
                    "target": params["target"],
                    "notional": notional,
                    "leverage": leverage,
                    "decided_at": timestamp,
                }
                decisions.append({"coin": coin, "action": "open_new", "side": params["side"], "entry": params["entry"], "reason": reason})
                print(f"  AÇILDI {coin} {params['side']}: ${params['entry']} stop:${params['stop']} target:${params['target']}")
        else:
            print(f"  WAIT {coin}: {reason}")
            decisions.append({"coin": coin, "action": "wait", "reason": reason})

    state["balance"] = balance
    state["positions"] = positions
    save_json("state/positions_deterministic.json", state)

    run_record = {
        "timestamp": timestamp,
        "agent": "deterministic",
        "balance": balance,
        "regime": snapshot.get("regime"),
        "decisions": decisions,
    }
    append_jsonl("runs_deterministic.jsonl", run_record)
    print(f"\nTamamlandı. Bakiye: ${balance} | Açık pozisyon: {len(positions)}")

if __name__ == "__main__":
    main()
