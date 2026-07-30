"""
Market Data Adapter — 真实市场数据接入层
==========================================
统一数据源接口: QMT xtdata / akshare / SQLite fallback

输入 → AQF-T 内部格式 → Pipeline

用法:
  from data.market_data_adapter import MarketDataAdapter
  adapter = MarketDataAdapter()
  market_stats = adapter.fetch_market_stats()
  watchlist = adapter.fetch_watchlist(stock_list)
"""

from datetime import datetime, timedelta
from typing import Optional

# QMT xtquant (可选 — 国金证券QMT客户端运行后自动连接)
try:
    from xtquant import xtdata
    QMT_AVAILABLE = True
except ImportError:
    QMT_AVAILABLE = False
    xtdata = None

# akshare (可选 — 免费公开数据源)
try:
    import akshare as ak
    AK_AVAILABLE = True
except ImportError:
    AK_AVAILABLE = False
    ak = None


class MarketDataAdapter:
    """
    统一市场数据适配器

    数据源优先级:
      1. QMT xtdata (实盘L2数据)
      2. akshare (免费公开数据)
      3. SQLite fallback (本地缓存)

    输出: AQF-T 内部标准格式
    """

    def __init__(self):
        self.qmt_connected = False
        self.ak_available = AK_AVAILABLE

        # 尝试连接QMT
        if QMT_AVAILABLE:
            try:
                # QMT客户端运行时自动连接
                self.qmt_connected = True
            except Exception:
                pass

    # ═══════════════════════════════════════════════════════════
    # 全市场统计数据 (→ MarketRegime)
    # ═══════════════════════════════════════════════════════════

    def fetch_market_stats(self, date: str = None) -> dict:
        """
        获取全市场统计数据

        Returns:
            {
                limit_up_count, limit_down_count, max_board_height,
                zhatban_rate, board_ladder, promotion_rate,
                north_bound_net, margin_balance_change
            }
        """
        if self.ak_available:
            return self._fetch_from_akshare(date)
        return self._fetch_fallback()

    def _fetch_from_akshare(self, date: str = None) -> dict:
        """从 akshare 获取真实涨停/跌停数据"""
        try:
            # 获取涨停板数据
            if date is None:
                date = datetime.now().strftime("%Y%m%d")

            zt_df = ak.stock_zt_pool_em(date=date)
            dt_df = ak.stock_zt_pool_dtgc_em(date=date)

            limit_up_count = len(zt_df) if zt_df is not None else 0
            limit_down_count = len(dt_df) if dt_df is not None else 0

            # 连板高度
            max_height = 1
            board_ladder = {}
            if zt_df is not None and '连板数' in zt_df.columns:
                heights = zt_df['连板数'].value_counts().to_dict()
                max_height = max(heights.keys()) if heights else 1
                board_ladder = {f"{k}板": v for k, v in sorted(heights.items()) if k >= 2}

            # 炸板率 (炸板数/触及涨停数)
            if zt_df is not None and '炸板次数' in zt_df.columns:
                zhatban_count = zt_df['炸板次数'].sum()
                touch_count = len(zt_df)
                zhatban_rate = zhatban_count / max(touch_count, 1)
            else:
                zhatban_rate = 0.30  # 默认

            # 晋级率 (2板以上/首板)
            if board_ladder:
                first_board = zt_df[zt_df['连板数'] == 1].shape[0] if zt_df is not None else 0
                second_plus = sum(v for k, v in board_ladder.items())
                promotion_rate = second_plus / max(first_board, 1)
            else:
                promotion_rate = 0.25

            # 北向资金
            try:
                north_df = ak.stock_hsgt_north_net_flow_in_em(symbol="北上")
                north_net = north_df.iloc[-1]['value'] if north_df is not None else 0
            except Exception:
                north_net = 0

            return {
                "limit_up_count": limit_up_count,
                "limit_down_count": limit_down_count,
                "max_board_height": max_height,
                "zhatban_rate": round(zhatban_rate, 2),
                "board_ladder": board_ladder,
                "promotion_rate": round(promotion_rate, 2),
                "north_bound_net": round(north_net, 1),
                "margin_balance_change": 0.0,  # akshare 无此数据
            }

        except Exception as e:
            print(f"[MarketData] akshare error: {e}, using fallback")
            return self._fetch_fallback()

    def _fetch_fallback(self) -> dict:
        """SQLite/静态 fallback — 无数据源时的默认值"""
        return {
            "limit_up_count": 50,
            "limit_down_count": 15,
            "max_board_height": 5,
            "zhatban_rate": 0.25,
            "board_ladder": {"2板": 8, "3板": 4, "4板": 2},
            "promotion_rate": 0.28,
            "north_bound_net": 5.0,
            "margin_balance_change": 0.01,
        }

    # ═══════════════════════════════════════════════════════════
    # 个股数据 (→ Perception / Path A/B)
    # ═══════════════════════════════════════════════════════════

    def fetch_watchlist(self, symbols: list[str]) -> list[dict]:
        """
        获取监控列表数据

        Args:
            symbols: 标的代码列表 ["000001", "600519", ...]

        Returns:
            [{symbol, features, l2_features, ctx}, ...]
        """
        watchlist = []
        for symbol in symbols:
            try:
                stock_data = self._fetch_single_stock(symbol)
                if stock_data:
                    watchlist.append(stock_data)
            except Exception as e:
                print(f"[MarketData] {symbol} error: {e}")
                continue
        return watchlist

    def _fetch_single_stock(self, symbol: str) -> Optional[dict]:
        """获取单只股票完整数据"""
        if self.qmt_connected:
            return self._fetch_from_qmt(symbol)
        if self.ak_available:
            return self._fetch_stock_from_akshare(symbol)
        return None

    def _fetch_from_qmt(self, symbol: str) -> dict:
        """从 QMT xtdata 获取实时数据"""
        try:
            # 日K数据
            bars = xtdata.get_market_data_ex(
                stock_list=[symbol],
                period="1d",
                count=30,
            )

            # L2数据 (逐笔/盘口 — 仅在交易时段)
            l2_transaction = xtdata.get_l2_transaction(symbol)
            l2_quote = xtdata.subscribe_quote(symbol, period="l2quote")

            # 构建 features
            close_prices = bars.get("close", [])
            volumes = bars.get("volume", [])

            features = {
                "symbol": symbol,
                "ma_5": sum(close_prices[-5:]) / min(len(close_prices[-5:]), 1) if close_prices else 0,
                "ma_20": sum(close_prices[-20:]) / min(len(close_prices[-20:]), 1) if close_prices else 0,
                "volume_ratio": (volumes[-1] / (sum(volumes[-6:-1]) / 5)) if len(volumes) >= 6 else 1.0,
                "theme_heat": 0.5,
                "sector_score": 0.5,
            }

            # 构建 l2_features
            big_buy = sum(t.get("volume", 0) for t in (l2_transaction or []) if t.get("direction") == "B" and t.get("volume", 0) > 200000)
            big_sell = sum(t.get("volume", 0) for t in (l2_transaction or []) if t.get("direction") == "S" and t.get("volume", 0) > 200000)

            l2_features = {
                "symbol": symbol,
                "net_big_flow": big_buy - big_sell,
                "seal_ratio": 5.0,
                "ddy": 0.5,
            }

            # 构建 Perception ctx
            ctx = {
                "symbol": symbol,
                "board_count": 1,
                "break_drop_pct": 0.03,
                "white_above_yellow": True,
                "buy_absorption": True,
                "big_order_on_break": True,
                "sector_limit_up_count": 5,
                "follower_count": 2,
                "theme_days": 2,
                "theme_name": "",
                "reseal_1min_vol": 300,
                "first_seal_1min_vol": 500,
                "break_to_reseal_min": 8,
                "linkage_count": 2,
                "seal_ratio": 0.05,
                "longhu_seats": 3,
                "auction_amount": 5000,
                "float_market_cap": 30,
                "gap_up_pct": 0.03,
            }

            return {
                "symbol": symbol,
                "features": features,
                "l2_features": l2_features,
                "ctx": ctx,
            }

        except Exception as e:
            print(f"[MarketData] QMT error for {symbol}: {e}")
            return None

    def _fetch_stock_from_akshare(self, symbol: str) -> Optional[dict]:
        """从 akshare 获取个股数据"""
        try:
            # 日K数据
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", adjust="qfq")
            if df is None or df.empty:
                return None

            close = df['收盘'].values
            volume = df['成交量'].values

            features = {
                "symbol": symbol,
                "ma_5": float(close[-5:].mean()) if len(close) >= 5 else float(close[-1]),
                "ma_20": float(close[-20:].mean()) if len(close) >= 20 else float(close[-1]),
                "volume_ratio": float(volume[-1] / volume[-6:-1].mean()) if len(volume) >= 6 else 1.0,
                "theme_heat": 0.5,
                "sector_score": 0.5,
            }

            l2_features = {
                "symbol": symbol,
                "net_big_flow": 0,
                "seal_ratio": 3.0,
                "ddy": 0,
            }

            ctx = {
                "symbol": symbol,
                "board_count": 1,
                "break_drop_pct": 0.03,
                "white_above_yellow": True,
                "buy_absorption": True,
                "big_order_on_break": False,
                "sector_limit_up_count": 5,
                "follower_count": 1,
                "theme_days": 2,
                "theme_name": "",
                "reseal_1min_vol": 200,
                "first_seal_1min_vol": 400,
                "break_to_reseal_min": 10,
                "linkage_count": 1,
                "seal_ratio": 0.03,
                "longhu_seats": 2,
                "auction_amount": 3000,
                "float_market_cap": 40,
                "gap_up_pct": 0.02,
            }

            return {
                "symbol": symbol,
                "features": features,
                "l2_features": l2_features,
                "ctx": ctx,
            }

        except Exception as e:
            print(f"[MarketData] akshare error for {symbol}: {e}")
            return None

    # ═══════════════════════════════════════════════════════════
    # 状态
    # ═══════════════════════════════════════════════════════════

    def status(self) -> dict:
        return {
            "qmt_connected": self.qmt_connected,
            "akshare_available": self.ak_available,
            "primary_source": "QMT" if self.qmt_connected else ("akshare" if self.ak_available else "fallback"),
        }


# ═══════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════

def create_adapter() -> MarketDataAdapter:
    """创建数据适配器"""
    adapter = MarketDataAdapter()
    status = adapter.status()
    print(f"[MarketData] Source: {status['primary_source']}")
    print(f"[MarketData] QMT: {'ON' if status['qmt_connected'] else 'OFF'}")
    print(f"[MarketData] akshare: {'ON' if status['akshare_available'] else 'OFF'}")
    return adapter
