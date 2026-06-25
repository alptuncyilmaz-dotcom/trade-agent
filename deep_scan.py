"""
deep_scan.py — Manuel derin tarama.
Ne yapar: snapshot + funding/OI proxy yorumu üretir, haber/makro bağlamı için zemin hazırlar.
Neden: otomatik runner'dan izole, elle tetiklenir, karar değil bağlam üretir.
Çıktı: journal/MANUEL-DERIN-{timestamp}.md
"""

import json
import os
from datetime import datetime, timezone

def load_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return default

def classify_funding(f):
    f = abs(f)
    if f > 0.0001:
        return "ekstrem"
    elif f > 0.00005:
        return "yuksek"
    elif f > 0.00001:
        return "normal-yukari"
    else:
        return "normal"

def trend_alignment(trends):
    vals = list(trends.values())
    if all(v == "up" for v in vals):
        return "TAM YUKARI"
    elif all(v == "down" for v in vals):
        return "TAM ASAGI"
    elif vals[-1] == "up":
        return "HTF yukari"
    elif vals[-1] == "down":
        return "HTF asagi"
    return "karisik"

def main():
    snapshot = load_json("state/snapshot_latest.json")
    if not snapshot:
        print("Snapshot yok — once capture_snapshot.py calistir.")
        return

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = []
    lines.append(f"# MANUEL DERIN TARAMA — {ts}")
    lines.append("")
    lines.append("> Elle tetiklendi · read-only · otomatik runner'dan IZOLE.")
    lines.append("> Bu ONERI + baglam, otomatik trade DEGIL.")
    lines.append("")
    lines.append(f"**Rejim:** {snapshot.get('regime','?').upper()}")
    lines.append("")

    lines.append("## Deterministik analiz")
    lines.append("")
    lines.append("| Varlik | Fiyat | RSI | MACDh | ATR | Funding | Funding-sinif | 1d-trend | Trigger |")
    lines.append("|--------|-------|-----|-------|-----|---------|---------------|----------|---------|")

    for coin, a in snapshot["assets"].items():
        fc = classify_funding(a["funding"])
        trigger_str = "YES" if a["trigger"] else "NO"
        lines.append(
            f"| {coin} | ${a['price']} | {a['rsi']} | {a['macd_hist']} | "
            f"{a['atr']} | {a['funding']:.2e} | {fc} | {a['trends']['1d']} | {trigger_str} |"
        )

    lines.append("")
    lines.append("## Funding / OI yorumu (PROXY)")
    lines.append("")
    for coin, a in snapshot["assets"].items():
        fc = classify_funding(a["funding"])
        alignment = trend_alignment(a["trends"])
        premium = a["markPx"] - a["oraclePx"]
        premium_str = f"+{premium:.4f}" if premium >= 0 else f"{premium:.4f}"
        rsi_note = ""
        if a["rsi"] > 70:
            rsi_note = " | RSI asiri-alim — gec-giris riski (H-03)"
        elif a["rsi"] < 30:
            rsi_note = " | RSI asiri-satim — potansiyel dip"
        lines.append(
            f"- **{coin}** (${a['price']}, OI {a['openInterest']:.0f}): "
            f"funding {fc} ({a['funding']:.2e}); premium {premium_str}; "
            f"trend alignment: {alignment}{rsi_note}"
        )

    lines.append("")
    lines.append("## Haber / Makro (trader-deep dolduracak)")
    lines.append("")
    lines.append("> Bu bolum bos birakiliyor — haber/makro WebSearch ile doldurulur.")
    lines.append("> Her madde: [yayin: YYYY-MM-DD] baslik + kaynak(URL)")
    lines.append("> Web fiyati canli mark'tan >%15 saparsa [fiyat-suphelisi] isle.")
    lines.append("")
    lines.append("### Makro")
    lines.append("- [ ] FOMC / Fed durumu")
    lines.append("- [ ] Dolar endeksi / enflasyon")
    lines.append("")
    lines.append("### Kripto")
    lines.append("- [ ] BTC ETF akim")
    lines.append("- [ ] Onemli on-chain / likidite haberi")
    lines.append("")
    lines.append("## Oneri (karar SENIN)")
    lines.append("")
    lines.append("> trader-deep agent bu bolumu dolduracak. GOZLEM, otomatik trade DEGIL.")
    lines.append("")
    lines.append("---")
    lines.append(f"*Uretildi: {ts} | Otomatik runner'dan izole | Gercek para YOK*")

    os.makedirs("journal", exist_ok=True)
    fname = f"journal/MANUEL-DERIN-{ts}.md"
    with open(fname, "w") as f:
        f.write("\n".join(lines))

    print(f"Tamamlandi: {fname}")
    print(f"Rejim: {snapshot.get('regime')}")
    for coin, a in snapshot["assets"].items():
        print(f"  {coin}: ${a['price']} | RSI {a['rsi']} | funding {classify_funding(a['funding'])} | {a['trends']['1d']}")

if __name__ == "__main__":
    main()
