"""
apply_deepthinker.py — deep-thinker kararlarını uygular.
Ne yapar: deepthinker_decision.json'u okur, sizing hesaplar, pozisyonları açar/kapatır.
Neden: deep-thinker LLM karar üretir, bu script kararı deterministic ile AYNI sizing+maliyet
       modeliyle uygular. check_path/kapanış/sizing tek kaynaktan (execution/*) gelir → A/B'nin iki
       kolu tam simetrik (CLAUDE.md: aynı snapshot, aynı sizing). Duplikasyon yok.
Çıktı: state/positions_deepthinker.json + runs_deepthinker.jsonl
"""

import json
from datetime import datetime, timezone

from execution import sizing, leverage, simulator

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
        price = asset["price"]
        status = simulator.check_path(pos, price)
        if status in ("stop_hit", "target_hit"):
            # Faz-1 maliyet modeli = fee-only (slippage/funding kapalı) — deterministic kolla SİMETRİK.
            res = simulator.simulate_trade(pos["side"], pos["entry"], price, pos["notional"],
                                           funding_rate=0.0, funding_periods=0, slippage_bps=0.0)
            balance = round(balance + res.net_pnl, 2)
            pnl_pct = (res.gross_pnl / pos["notional"] * 100) if pos["notional"] else 0.0
            to_close.append(coin)
            log.append({"coin": coin, "action": status, "net_pnl": round(res.net_pnl, 2), "price": price})
            print(f"  KAPANDI {coin} {status}: {round(pnl_pct,2)}% net ${round(res.net_pnl,2)}")

    for coin in to_close:
        del positions[coin]

    # deep-thinker kararlarını uygula
    for coin, params in decision.get("decisions", {}).items():
        if coin in positions:
            print(f"  {coin} zaten açık — atlandı")
            continue
        entry = params["entry"]
        stop = params["stop"]
        # Sizing (notional) = risk-bazlı, deterministic kolla AYNEN (CLAUDE.md "aynı sizing").
        sz = sizing.compute_sizing(balance, entry, stop)
        # Kaldıraç AYRI + kod-türetilmiş; deep-thinker confidence'ı YALNIZ kaldıraç kapısında kullanılır
        # (notional'ı = PnL'i değiştirmez → A/B adil kalır).
        asset = snapshot["assets"].get(coin, {})
        lev = leverage.suggest_leverage(entry, stop, params["side"], asset.get("atr", 0), entry,
                                        confidence=params.get("confidence", "medium"))
        if sz.notional > 0:
            positions[coin] = {
                "side": params["side"],
                "entry": entry,
                "stop": stop,
                "target": params["target"],
                "notional": sz.notional,
                "leverage": lev.leverage,
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
