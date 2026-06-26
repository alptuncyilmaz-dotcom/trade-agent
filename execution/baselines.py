"""
execution/baselines.py — Baseline karşılaştırma (L-01: B&H + basit-RSI'ı fee-net yen).
Ne yapar: Bir trade'in net getirisini iki çıpaya karşı kıyaslar: (1) buy-and-hold, (2) basit-RSI kuralı.
Neden:   CLAUDE.md L-01 — LLM/kural trader fee sonrası B&H'yi yenmiyorsa graduate ETME. Her kapanışta
         `trader-refresh` bu karşılaştırmayı ZORUNLU çalıştırır; edge var mı görünür olur.
Çıktı:   Saf hesap, I/O yok.
"""

# Basit-RSI baseline: RSI<=30 iken long, RSI>=70 iken short (yoksa flat) — naif çıpa.
RSI_LONG = 30
RSI_SHORT = 70


def buy_hold_return(entry, exit_price, side="buy"):
    """B&H oransal getiri (trade ile aynı yönde tutulmuş gibi)."""
    if entry <= 0:
        return 0.0
    move = (exit_price - entry) / entry
    return round(move if side == "buy" else -move, 6)


def simple_rsi_return(entry_rsi, entry, exit_price):
    """Basit-RSI çıpası: giriş RSI'sine göre yön seçer, B&H gibi tutar. Flat ise 0."""
    if entry_rsi <= RSI_LONG:
        return buy_hold_return(entry, exit_price, "buy")
    if entry_rsi >= RSI_SHORT:
        return buy_hold_return(entry, exit_price, "sell")
    return 0.0  # flat — naif kural sinyal vermez


def compare(trade_net_pct, entry, exit_price, side, entry_rsi):
    """Trade net getirisini (fee-DAHİL, oran) çıpalara karşı kıyaslar.
    Döner: edge sözlüğü. `beats_all` ikisini de yeniyorsa True (L-01 graduate ölçütü)."""
    bh = buy_hold_return(entry, exit_price, side)
    rsi_base = simple_rsi_return(entry_rsi, entry, exit_price)
    return {
        "trade_net_pct": round(trade_net_pct, 6),
        "buy_hold_pct": bh,
        "simple_rsi_pct": rsi_base,
        "edge_vs_bh": round(trade_net_pct - bh, 6),
        "edge_vs_rsi": round(trade_net_pct - rsi_base, 6),
        "beats_all": trade_net_pct > bh and trade_net_pct > rsi_base,
    }
