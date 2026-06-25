"""
execution/simulator.py — Paper-fill simülatörü (fee + funding + slippage dahil).
Ne yapar: Bir pozisyonun gerçekçi giriş/çıkış dolgusunu ve net K/Z'sini hesaplar; taker fee,
          funding taşıma maliyeti ve slippage'i içerir.
Neden:   apply_*'taki net_pnl yalnız fee*2 sayıyordu. Gerçek perp'te slippage + funding sessiz
         maliyettir (L-03: over-trading fee sessiz katil). Baseline'ı dürüst yenmek için (L-01)
         maliyetler tam modellenmeli. TESTNET/PAPER — gerçek emir yok.
Çıktı:   FillResult / TradeResult (dataclass) — saf hesap, I/O yok.
"""

from dataclasses import dataclass

# --- Maliyet parametreleri ---
TAKER_FEE = 0.00035       # %0.035 taker (giriş + çıkış ayrı alınır)
DEFAULT_SLIPPAGE_BPS = 2.0  # 2 bps (~%0.02) varsayılan kayma; piyasa emri varsayımı
# Funding 8 saatte bir tahakkuk eder; bizim tur periyodu saatlik → period başına funding/ ~ ham oran.
# Basitlik için: funding_cost = notional * funding_rate * funding_periods (işaret yöne göre).


@dataclass
class FillResult:
    side: str
    requested: float    # istenen fiyat
    filled: float       # slippage sonrası gerçekleşen fiyat
    slippage_usd: float


@dataclass
class TradeResult:
    side: str
    entry: float
    exit: float
    notional: float
    gross_pnl: float    # ham yön K/Z (maliyet öncesi)
    fees: float         # giriş+çıkış taker
    funding: float      # taşıma funding maliyeti (+ = bize maliyet)
    slippage: float     # giriş+çıkış kayma maliyeti
    net_pnl: float      # gross - fees - funding - slippage

    def as_dict(self):
        return {
            "side": self.side, "entry": self.entry, "exit": self.exit, "notional": self.notional,
            "gross_pnl": round(self.gross_pnl, 2), "fees": round(self.fees, 2),
            "funding": round(self.funding, 4), "slippage": round(self.slippage, 2),
            "net_pnl": round(self.net_pnl, 2),
        }


def simulate_fill(side, price, slippage_bps=DEFAULT_SLIPPAGE_BPS):
    """Slippage'i fiyata uygular. Kayma DAİMA aleyhe: alışta yukarı, satışta aşağı dolgu.
    Neden aleyhe: paper sonuçların iyimser kaymaması için muhafazakâr varsayım."""
    slip = price * (slippage_bps / 10000.0)
    if side == "buy":
        filled = price + slip
    else:  # sell / short giriş
        filled = price - slip
    return FillResult(side=side, requested=round(price, 6), filled=round(filled, 6),
                      slippage_usd=round(abs(filled - price), 6))


def funding_cost(notional, side, funding_rate, periods=1):
    """Taşıma funding maliyeti. funding_rate>0 → long öder, short alır (Hyperliquid konvansiyonu).
    Döner: pozitif = bize MALİYET, negatif = bize kredi."""
    flow = notional * funding_rate * periods
    # long, pozitif funding'i öder (maliyet = +flow); short tersini alır (maliyet = -flow)
    return round(flow if side == "buy" else -flow, 6)


def simulate_trade(side, entry, exit_price, notional, funding_rate=0.0,
                   funding_periods=1, slippage_bps=DEFAULT_SLIPPAGE_BPS):
    """Tam round-trip simülasyonu: slippage'li giriş+çıkış, taker fee*2, funding taşıma.

    notional: pozisyon büyüklüğü (USD, nominal). PnL oransal hareket × notional.
    Döner: TradeResult (net_pnl bakiyeye eklenecek nihai sayı)."""
    fill_in = simulate_fill(side, entry, slippage_bps)
    # Çıkışta ters taraf dolgusu (kapanış da piyasa emri): long kapanışı = sell, short kapanışı = buy
    close_side = "sell" if side == "buy" else "buy"
    fill_out = simulate_fill(close_side, exit_price, slippage_bps)

    eff_entry = fill_in.filled
    eff_exit = fill_out.filled
    move = ((eff_exit - eff_entry) / eff_entry) if side == "buy" else ((eff_entry - eff_exit) / eff_entry)
    gross_pnl = notional * move

    fees = notional * TAKER_FEE * 2
    fund = funding_cost(notional, side, funding_rate, funding_periods)
    slippage = fill_in.slippage_usd / fill_in.requested * notional + \
               fill_out.slippage_usd / fill_out.requested * notional

    net_pnl = gross_pnl - fees - fund - slippage
    return TradeResult(
        side=side, entry=round(eff_entry, 6), exit=round(eff_exit, 6), notional=notional,
        gross_pnl=gross_pnl, fees=fees, funding=fund, slippage=slippage, net_pnl=net_pnl,
    )
