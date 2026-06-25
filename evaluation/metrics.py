"""
evaluation/metrics.py — Performans metrikleri (expectancy, profit factor, max DD, Sharpe).
Ne yapar: Kapanmış trade'lerin net K/Z listesinden ve bakiye eğrisinden özet metrikler üretir.
Neden:   A/B'nin amacı iki kolu DÜRÜST karşılaştırmak. L-01: baseline'ı (B&H) fee sonrası yen;
         L-02: aşırı yüksek Sharpe = leakage şüphesi. Bu modül her iki kolu ve baseline'ı aynı
         ölçütlerle değerlendirir; SUCCESSFUL/FAILED etiketi YOK (kural 8) — sadece sayı.
Çıktı:   Saf hesap, I/O yok. summarize() bir metrik sözlüğü döndürür.
"""

import math

# L-02 koruması: bu eşiğin üstündeki Sharpe otomatik 'leakage şüphesi' bayrağı kaldırır.
SHARPE_LEAKAGE_FLAG = 3.0


def expectancy(pnls):
    """Trade başına beklenen net K/Z = ortalama(net_pnl). Pozitif → kenar var (maliyet sonrası)."""
    if not pnls:
        return 0.0
    return round(sum(pnls) / len(pnls), 4)


def win_rate(pnls):
    """Kazanan trade oranı (net_pnl > 0)."""
    if not pnls:
        return 0.0
    wins = sum(1 for p in pnls if p > 0)
    return round(wins / len(pnls), 4)


def profit_factor(pnls):
    """Brüt kazanç / |brüt kayıp|. >1 kârlı. Kayıp yoksa float('inf') (tek-yön örneklem uyarısı)."""
    gains = sum(p for p in pnls if p > 0)
    losses = sum(p for p in pnls if p < 0)
    if losses == 0:
        return float("inf") if gains > 0 else 0.0
    return round(gains / abs(losses), 4)


def max_drawdown(equity):
    """Bakiye eğrisinden maksimum tepe-dip düşüş (oran). Döner: 0..1 (0.2 = %20 DD)."""
    if not equity:
        return 0.0
    peak = equity[0]
    max_dd = 0.0
    for v in equity:
        peak = max(peak, v)
        if peak > 0:
            dd = (peak - v) / peak
            max_dd = max(max_dd, dd)
    return round(max_dd, 4)


def sharpe(pnls, periods_per_year=None):
    """Sharpe oranı = ortalama(getiri) / std(getiri). periods_per_year verilirse yıllıklaştırır.
    Risksiz oran 0 varsayılır (kısa paper serisi). std=0 ise 0 döner.
    DİKKAT (L-02): tek/az trade'de Sharpe anlamsızdır; SHARPE_LEAKAGE_FLAG üstü değer şüphelidir."""
    n = len(pnls)
    if n < 2:
        return 0.0
    mean = sum(pnls) / n
    var = sum((p - mean) ** 2 for p in pnls) / (n - 1)
    std = math.sqrt(var)
    if std == 0:
        return 0.0
    s = mean / std
    if periods_per_year:
        s *= math.sqrt(periods_per_year)
    return round(s, 4)


def summarize(pnls, equity=None, periods_per_year=None):
    """Tüm metrikleri tek sözlükte toplar + leakage bayrağı.
    pnls: kapanmış trade net K/Z listesi. equity: bakiye eğrisi (opsiyonel, DD için)."""
    sh = sharpe(pnls, periods_per_year)
    result = {
        "n_trades": len(pnls),
        "expectancy": expectancy(pnls),
        "win_rate": win_rate(pnls),
        "profit_factor": profit_factor(pnls),
        "total_pnl": round(sum(pnls), 2) if pnls else 0.0,
        "max_drawdown": max_drawdown(equity) if equity else None,
        "sharpe": sh,
        "leakage_suspect": bool(abs(sh) > SHARPE_LEAKAGE_FLAG and len(pnls) < 30),
    }
    return result


def buy_hold_return(entry_price, exit_price, side="buy"):
    """Baseline B&H getirisi (oransal) — L-01 karşılaştırması için.
    A/B kolunun bunu fee sonrası yenmesi beklenir; yenemiyorsa kenar yok demektir."""
    if entry_price <= 0:
        return 0.0
    move = (exit_price - entry_price) / entry_price
    return round(move if side == "buy" else -move, 4)
