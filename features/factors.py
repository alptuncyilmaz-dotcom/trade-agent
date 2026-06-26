"""
features/factors.py — Mevcut faktör seti + blind-spot sınıflandırması.
Ne yapar: Faz-1'de KULLANILAN faktörleri sabitler (CURRENT_FACTORS); bir "kaçırma" metninin mevcut
          faktörlerden biriyle kaplanıp kaplanmadığını söyler (is_covered).
Neden:   trader-refresh blind-spot keşfi (CLAUDE.md): kaçırılan sinyal faktör setinde YOKSA →
          internetten araştır → candidate-factors.md. Kaplıysa → uygulama/ağırlık hatası (yeni faktör yok).
Çıktı:   Saf — I/O yok. Faz-1 config SABİT (kural 7): bu set faz içinde değişmez.
"""

# Faz-1 aktif faktörler → tanıma anahtar kelimeleri (TR/EN, kaba eşleşme).
CURRENT_FACTORS = {
    "rsi": ["rsi", "aşırı alım", "aşırı satım", "overbought", "oversold"],
    "macd": ["macd", "cross", "kesişim", "histogram", "momentum"],
    "atr": ["atr", "volatilite", "volatility", "stop mesafe"],
    "funding": ["funding", "fonlama", "ekstrem funding"],
    "open_interest": ["open interest", "oi", "açık pozisyon"],
    "trend": ["trend", "sma", "ema", "htf", "yön"],
    "regime": ["rejim", "regime", "broad", "bull", "bear"],
}


def is_covered(miss_text):
    """Kaçırma metni mevcut bir faktörle kaplı mı? Döner: (covered: bool, factor: str|None).
    covered=True → uygulama/ağırlık hatası (yeni faktör gerekmez). False → BLIND-SPOT (araştır)."""
    low = (miss_text or "").lower()
    for factor, keys in CURRENT_FACTORS.items():
        if any(k in low for k in keys):
            return True, factor
    return False, None


def factor_names():
    """Aktif faktör adları (loglama/şeffaflık)."""
    return sorted(CURRENT_FACTORS.keys())
