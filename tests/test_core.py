"""
tests/test_core.py — Çekirdek katman birim testleri (offline).
Kapsam: feature · point-in-time · execution sim (maliyet) · evaluation metrik · decision şema ·
        sizing/leverage tavanları + likidasyon kapısı.
Çalıştır: .venv/bin/python -m pytest tests -v
"""

from features import indicators, trend, factors
from data import snapshot as snap
from execution import simulator, sizing, leverage, decision, baselines, autonomous
from evaluation import metrics


# 1) FEATURE — indikatör temel davranış
def test_indicators_basic():
    up = list(range(1, 60))           # monoton artan
    assert indicators.compute_rsi(up) > 50
    assert indicators.compute_trend(up) == "up"
    assert indicators.compute_trend(list(range(60, 1, -1))) == "down"
    h, line, sig = indicators.compute_macd(up)
    assert isinstance(h, float)


# 2) POINT-IN-TIME — as_of sonrası mum dışlanır (look-ahead yok)
def test_point_in_time_filter():
    candles = [{"t": 1000, "c": 1}, {"t": 2000, "c": 2}, {"t": 3000, "c": 3}]
    assert len(snap._pit(candles, None)) == 3
    assert [c["t"] for c in snap._pit(candles, 2000)] == [1000, 2000]  # 3000 dışlandı


# 3) EXECUTION SIM — fee/funding/slippage net_pnl'e GİRER
def test_simulator_costs_included():
    # maliyetsiz brüt = notional*move; net daha düşük olmalı (fee+slippage)
    r = simulator.simulate_trade("buy", 100, 110, notional=1000, slippage_bps=2, funding_rate=0.0001, funding_periods=3)
    assert r.fees > 0 and r.slippage > 0
    assert r.net_pnl < r.gross_pnl  # maliyetler düştü
    # slippage_bps=0, funding=0 → fee-only (Faz-1 A/B bazı)
    r0 = simulator.simulate_trade("buy", 100, 110, notional=1000, slippage_bps=0, funding_rate=0, funding_periods=0)
    assert abs(r0.funding) == 0 and r0.slippage == 0


# 4) EVALUATION — expectancy / profit factor / leakage bayrağı
def test_metrics():
    m = metrics.summarize([10, -5, 8, -3, 12])
    assert m["n_trades"] == 5
    assert round(m["expectancy"], 2) == 4.4
    assert m["profit_factor"] > 1
    # tek-yön + çok yüksek → leakage şüphesi tetiklenebilir
    assert "leakage_suspect" in m


# 5) DECISION — şema + demir kural guard
def test_decision_validate():
    asset = {"trends": {"1d": "up"}, "price": 100, "is_counter_trend_long": False, "is_counter_trend_short": False}
    snapshot = {"assets": {"BTC": asset}}
    good = {"decisions": {"BTC": {"side": "buy", "entry": 100, "stop": 98, "target": 106}}, "waits": {}}
    clean, waits = decision.validate_decision(good, snapshot)
    assert "BTC" in clean and "BTC" not in waits
    # bozuk sıralama → WAIT'e düşer
    bad = {"decisions": {"BTC": {"side": "buy", "entry": 100, "stop": 106, "target": 98}}, "waits": {}}
    clean2, waits2 = decision.validate_decision(bad, snapshot)
    assert "BTC" not in clean2 and "BTC" in waits2
    # kaldıraç tavanı
    ok, _ = decision.validate_leverage(6.0)
    assert not ok
    assert decision.validate_leverage(3.0)[0]


# 6) SIZING + LEVERAGE — risk tavanı + likidasyon kapısı
def test_sizing_and_leverage():
    sz = sizing.compute_sizing(4000, 100, 98)   # %2 stop → notional = 60/0.02 = 3000, %30 tavanı=1200
    assert sz.notional == 1200.0
    assert sz.used_margin <= 4000
    # likidasyon kapısı: dar stop → düşük kaldıraç tavanı
    lev = leverage.suggest_leverage(100, 99.5, "buy", atr=1.0, price=100, confidence="high")
    assert lev.leverage <= 5.0
    # low güven → ~1x
    lev_low = leverage.suggest_leverage(100, 90, "buy", atr=1.0, price=100, confidence="low")
    assert lev_low.leverage <= 1.0


# 6b) AGGRESSIVE (C kolu) — yüksek risk/kaldıraç, default'lar KORUNUR
def test_aggressive_profile():
    # default (det) ile aggressive aynı entry/stop → aggressive notional DAHA BÜYÜK (%5 vs %1.5)
    det = sizing.compute_sizing(4000, 100, 95)  # %5 stop
    agg = sizing.compute_sizing(4000, 100, 95, risk_pct=sizing.RISK_PCT_AGGRESSIVE,
                                max_pos_pct=sizing.MAX_POS_PCT_AGGRESSIVE)
    assert agg.notional > det.notional
    assert round(agg.notional / det.notional, 1) == round(0.05 / 0.015, 1)  # ~3.33×
    # default max_leverage=5 davranışı DEĞİŞMEDİ (Faz-1 koruması). Dar stop (99) → likidasyon kapısı
    # geniş (80x), düşük vol → kaldıraç max_leverage tavanına dayanır.
    lev5 = leverage.suggest_leverage(100, 99, "buy", atr=1.0, price=100, confidence="high")
    assert lev5.leverage == 5.0
    # aggressive 20x tavanı: aynı kurulumda 5x'ten yüksek (kaldıraç farkı görünür)
    lev20 = leverage.suggest_leverage(100, 99, "buy", atr=1.0, price=100, confidence="high", max_leverage=20)
    assert lev20.leverage > 5.0 and lev20.leverage <= 20.0
    # confidence cap orantısı: max_lev=5'te high=5 (default korunur)
    assert leverage._confidence_cap("high", 5.0) == 5.0
    assert leverage._confidence_cap("medium", 5.0) == 2.0


# 7) TREND + ANCHOR — counter-trend simetri + anchor temizliği
def test_trend_and_anchor():
    assert trend.is_counter_trend("buy", "down") is True
    assert trend.is_counter_trend("sell", "up") is True
    assert trend.is_counter_trend("buy", "up") is False
    assert trend.market_regime(["down", "down", "down", "up"]) == "broad_bear"
    assert autonomous.is_anchor_clean({"rsi": 30, "trend": "up"}) is True
    assert autonomous.is_anchor_clean({"last_pnl": 50}) is False
    covered, fac = factors.is_covered("RSI aşırı alımdaydı")
    assert covered and fac == "rsi"


# 8) CHECK_PATH — mum high/low ile tarama-arası SL/TP yakalama
def test_check_path_candles():
    pos = {"side": "buy", "stop": 95, "target": 110}
    # yolda low 94'e değdi (stop) → stop_hit
    candles = [{"t": 1, "h": 102, "l": 94}, {"t": 2, "h": 108, "l": 99}]
    assert autonomous.check_path(pos, candles)["status"] == "stop_hit"
    # hiç değmedi → open
    candles2 = [{"t": 1, "h": 101, "l": 99}]
    assert autonomous.check_path(pos, candles2)["status"] == "open"


# 9) BASELINES — B&H + basit-RSI karşılaştırma (L-01)
def test_baselines():
    c = baselines.compare(0.05, 100, 110, "buy", entry_rsi=25)  # trade %5, B&H %10
    assert c["buy_hold_pct"] == 0.1
    assert c["beats_all"] is False  # B&H'yi yenemedi
