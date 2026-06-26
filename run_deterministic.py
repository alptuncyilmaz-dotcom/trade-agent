"""
run_deterministic.py — Kural bazlı A/B kolu (deterministic-trader).
Ne yapar: snapshot'tan triggers/rules ile karar verir (autonomous.opportunity_gate), leverage ile
          boyutlandırır, simulator ile paper-fill kapatır, metrics ile kümülatif performans raporlar.
Neden:   LLM olmadan saf kural performansını ölçmek (A/B testi A kolu). Tüm mantık tek kaynaktan
         (triggers/execution/evaluation) gelir — sizing/trigger/fill/pnl artık burada DUPLİKE DEĞİL.
Çıktı:   state/positions_deterministic.json + runs_deterministic.jsonl
"""

import json
from datetime import datetime, timezone

from execution import autonomous, sizing, leverage, simulator
from evaluation import metrics


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


def decide(asset):
    """Kural-bazlı karar — tek kaynak triggers/rules (autonomous.opportunity_gate üzerinden).
    Döner: (action, params|None, reason). Gate geçerse open + ATR referans seviyeleri, yoksa wait."""
    passes, side, reason = autonomous.opportunity_gate(asset)
    if not passes:
        return "wait", None, autonomous.wait_diagnosis(asset)
    stop, target = autonomous.reference_levels(asset["price"], asset["atr"], side)
    return "open", {"side": side, "entry": asset["price"], "stop": stop, "target": target}, reason


def load_closed_pnls(path):
    """Geçmiş + bu turdaki kapanmış trade'lerin net K/Z listesi (kümülatif metrik için)."""
    pnls = []
    try:
        with open(path) as f:
            for line in f:
                rec = json.loads(line)
                for d in rec.get("decisions", []):
                    if d.get("action") in ("stop_hit", "target_hit"):
                        pnls.append(d.get("net_pnl", 0.0))
    except FileNotFoundError:
        pass
    return pnls


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

    # --- Açık pozisyonları kontrol et / kapat (tek kaynak: simulator) ---
    to_close = []
    for coin, pos in positions.items():
        asset = snapshot["assets"].get(coin)
        if not asset:
            continue
        status = simulator.check_path(pos, asset["price"])
        if status in ("stop_hit", "target_hit"):
            # Faz-1 maliyet modeli = fee-only (slippage/funding kapalı → mevcut A/B bazını korur).
            res = simulator.simulate_trade(pos["side"], pos["entry"], asset["price"], pos["notional"],
                                           funding_rate=0.0, funding_periods=0, slippage_bps=0.0)
            balance = round(balance + res.net_pnl, 2)
            to_close.append(coin)
            decisions.append({"coin": coin, "action": status, "net_pnl": round(res.net_pnl, 2), "price": asset["price"]})
            print(f"  KAPANDI {coin} {status}: net ${round(res.net_pnl, 2)}")

    for coin in to_close:
        del positions[coin]

    # --- Yeni pozisyon kararları ---
    for coin, asset in snapshot["assets"].items():
        if coin in positions:
            price = asset["price"]
            pos = positions[coin]
            pnl_pct = ((price - pos["entry"]) / pos["entry"]) if pos["side"] == "buy" else ((pos["entry"] - price) / pos["entry"])
            print(f"  AÇIK {coin}: ${price} K/Z {round(pnl_pct*100,2)}%")
            decisions.append({"coin": coin, "action": "open", "price": price, "pnl_pct": round(pnl_pct*100, 2)})
            continue

        action, params, reason = decide(asset)
        if action == "open":
            # Sizing (notional) = risk-bazlı, İKİ KOL DA AYNEN (PnL bundan gelir → A/B adil).
            sz = sizing.compute_sizing(balance, params["entry"], params["stop"])
            # Kaldıraç AYRI ve kod-türetilmiş; deterministic = medium güven (≤2x). PnL'i değiştirmez.
            lev = leverage.suggest_leverage(params["entry"], params["stop"], params["side"],
                                            asset["atr"], params["entry"], confidence="medium")
            if sz.notional > 0:
                positions[coin] = {
                    "side": params["side"],
                    "entry": params["entry"],
                    "stop": params["stop"],
                    "target": params["target"],
                    "notional": sz.notional,
                    "leverage": lev.leverage,
                    "decided_at": timestamp,
                }
                decisions.append({"coin": coin, "action": "open_new", "side": params["side"], "entry": params["entry"], "reason": reason})
                print(f"  AÇILDI {coin} {params['side']}: ${params['entry']} stop:${params['stop']} target:${params['target']} (lev {sz.leverage})")
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

    # --- Kümülatif performans (tek kaynak: evaluation/metrics) ---
    all_pnls = load_closed_pnls("runs_deterministic.jsonl")
    if all_pnls:
        m = metrics.summarize(all_pnls)
        print(f"  Kümülatif: {m['n_trades']} trade | expectancy ${m['expectancy']} | "
              f"PF {m['profit_factor']} | win {m['win_rate']} | Sharpe {m['sharpe']}"
              + (" | ⚠ leakage şüphesi" if m['leakage_suspect'] else ""))


if __name__ == "__main__":
    main()
