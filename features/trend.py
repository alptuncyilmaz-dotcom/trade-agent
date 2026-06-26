"""
features/trend.py — Çok-TF trend + piyasa rejimi + counter-trend bayrağı (H-03 çözümü).
Ne yapar: 15m/1h/4h/1d trendleri toplar, broad rejim sınıflar, bir yönün HTF'ye karşı olup olmadığını söyler.
Neden:   H-03 (BTC-001 stop'unun kök sebebi tek-TF körlüğü). Snapshot bu geniş bağlamı taşır;
         deterministic + deep-thinker counter-trend açmayı bu sayede engeller (CLAUDE.md A/B simetri).
Çıktı:   Saf hesap (indicators.compute_trend üstüne) — I/O yok.
"""

from features import indicators


def multi_tf_trend(closes_by_tf):
    """{tf: [closes]} → {tf: 'up'|'down'|'range'} (indicators.compute_trend tek kaynak)."""
    return {tf: indicators.compute_trend(cl) for tf, cl in closes_by_tf.items()}


def market_regime(trends_1d_list):
    """1d trend çoğunluğu → 'broad_bull' / 'broad_bear' / 'mixed'. 3+ aynı yön = broad.
    snapshot.compute_regime ile aynı eşik (bear/bull/mixed adlarının broad_ önekli hali)."""
    counts = {"up": 0, "down": 0, "range": 0}
    for t in trends_1d_list:
        counts[t] = counts.get(t, 0) + 1
    if counts["up"] >= 3:
        return "broad_bull"
    if counts["down"] >= 3:
        return "broad_bear"
    return "mixed"


def is_counter_trend(side, trend_1d):
    """Bir yön HTF (1d) trende KARŞI mı? Simetrik: buy+down=True, sell+up=True.
    Keyfi eşik YOK — short, long'un birebir simetrik tersi (CLAUDE.md A/B simetri)."""
    if side == "buy":
        return trend_1d == "down"
    if side == "sell":
        return trend_1d == "up"
    return False


def market_context(closes_by_tf, regime, side=None):
    """Snapshot'a gömülecek market_context bloğu: çok-TF trend + rejim + (varsa) counter-trend bayrağı."""
    trends = multi_tf_trend(closes_by_tf)
    ctx = {"trends": trends, "regime": regime}
    if side is not None:
        ctx["is_counter_trend"] = is_counter_trend(side, trends.get("1d", "range"))
    return ctx
