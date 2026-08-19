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
        self.qmt_degraded = False  # QMT 首次调用失败后自动降级
        self.ak_kline_degraded = False  # akshare K线首次失败后自动降级
        self.ak_available = AK_AVAILABLE
        self._zt_df_cache = None  # 涨停池缓存

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

            # 缓存涨停池供 fetch_watchlist 复用
            self._zt_df_cache = zt_df

            limit_up_count = len(zt_df) if zt_df is not None else 0
            limit_down_count = len(dt_df) if dt_df is not None else 0

            # 连板高度
            max_height = 1
            board_ladder = {}
            if zt_df is not None and '连板数' in zt_df.columns:
                heights = zt_df['连板数'].value_counts().to_dict()
                max_height = max(heights.keys()) if heights else 1
                board_ladder = {f"{k}板": v for k, v in sorted(heights.items()) if k >= 2}

            # ── 炸板池 / 昨日涨停池 (统一口径: 与统一生态 market_sentiment_factors 对齐) ──
            zb_df = None
            prev_df = None
            try:
                zb_df = ak.stock_zt_pool_zbgc_em(date=date)
            except Exception as e:
                print(f"[MarketData] 炸板池获取失败: {e}")
            try:
                prev_df = ak.stock_zt_pool_previous_em(date=date)
            except Exception as e:
                print(f"[MarketData] 昨日涨停池获取失败: {e}")

            # 炸板率 = 炸板池/(涨停池+炸板池) (行业标准, 与统一生态 blow_rate 一致)
            if zt_df is not None and zb_df is not None:
                _zt_zb_total = len(zt_df) + len(zb_df)
                zhatban_rate = len(zb_df) / _zt_zb_total if _zt_zb_total > 0 else 0.30
            elif zt_df is not None and '炸板次数' in zt_df.columns:
                zhatban_stocks = (zt_df['炸板次数'] > 0).sum()
                zhatban_rate = zhatban_stocks / max(len(zt_df), 1)
            else:
                zhatban_rate = 0.30  # 默认

            # 晋级率 = 今日继续涨停(连板≥2) / 昨日涨停数 (胜率, 与统一生态 promote_rate 一致)
            if zt_df is not None and prev_df is not None and '连板数' in zt_df.columns:
                second_plus = int((zt_df['连板数'] >= 2).sum())
                promotion_rate = second_plus / max(len(prev_df), 1)
            elif board_ladder:
                first_board = zt_df[zt_df['连板数'] == 1].shape[0] if zt_df is not None else 0
                second_plus = sum(v for k, v in board_ladder.items())
                promotion_rate = second_plus / max(first_board, 1)
            else:
                promotion_rate = 0.25

            # 北向资金 (B-2: 2024年后实时披露关闭, 接口常不可用 → 缺失=None中性, 不伪造0值)
            north_net = None
            try:
                north_df = ak.stock_hsgt_north_net_flow_in_em(symbol="北上")
                if north_df is not None and len(north_df) > 0:
                    north_net = float(north_df.iloc[-1]['value'])
            except Exception:
                north_net = None

            # 提取涨停池股票代码 (用于 watchlist)
            limit_up_symbols = []
            if zt_df is not None and '代码' in zt_df.columns:
                limit_up_symbols = zt_df['代码'].dropna().astype(str).tolist()

            return {
                "limit_up_count": limit_up_count,
                "limit_down_count": limit_down_count,
                "max_board_height": max_height,
                "zhatban_rate": round(zhatban_rate, 2),
                "board_ladder": board_ladder,
                "promotion_rate": round(promotion_rate, 2),
                "north_bound_net": round(north_net, 1) if north_net is not None else None,
                "margin_balance_change": None,  # 融资余额接口滞后(SSE 10日) → 缺失=中性, 见B-2
                "limit_up_symbols": limit_up_symbols,
                "_meta": {
                    "source": "akshare",
                    "date": date,
                    "data_freshness": {
                        "margin_balance_change": "unavailable",  # 数据源能力缺失，非真实0值
                        "zhatban_rate": "统一口径: 炸板池/(涨停池+炸板池)",
                        "promotion_rate": "统一口径: 今日连板≥2/昨日涨停数",
                    }
                }
            }

        except Exception as e:
            print(f"[MarketData] akshare error: {e}, using fallback")
            return self._fetch_fallback()

    def _fetch_fallback(self, reason: str = "") -> dict:
        """Fail-safe fallback (B-4, 2026-08-20) — 数据不可得时返回"缺失"标记。

        由 MarketRegimeEngine 判定 退潮/stop (fail-closed)。
        绝不返回伪造假市场数据 — 08-17 P0: 假数据(涨停50/跌停15)导致 AQF-T 误判 回暖/放行,
        而真实市场(涨停106/跌停41)应判 退潮/stop。
        """
        return {
            "limit_up_count": None,
            "limit_down_count": None,
            "max_board_height": None,
            "zhatban_rate": None,
            "board_ladder": {},
            "promotion_rate": None,
            "north_bound_net": None,
            "margin_balance_change": None,
            "_meta": {
                "source": "fallback-failsafe",
                "date": datetime.now().strftime("%Y%m%d"),
                "reason": reason or "市场数据源不可用",
                "data_freshness": {"all": "unavailable"},
            },
        }

    # ═══════════════════════════════════════════════════════════
    # 活跃股票列表 (→ Watchlist)
    # ═══════════════════════════════════════════════════════════

    def fetch_active_symbols(self, limit: int = 20) -> list[str]:
        """
        获取当日活跃股票代码列表

        优先从涨停池取（最活跃的标的），不足时补充默认池。
        仅 EOD 可用（akshare 涨停池盘后才有数据）。

        Returns:
            ["000001", "600519", ...]  最多 limit 只
        """
        symbols = []
        try:
            if self.ak_available:
                today = datetime.now().strftime("%Y%m%d")
                zt_df = ak.stock_zt_pool_em(date=today)
                if zt_df is not None and '代码' in zt_df.columns:
                    codes = zt_df['代码'].dropna().astype(str).tolist()
                    # 去重，去空，限制数量
                    seen = set()
                    for c in codes:
                        c = c.strip()
                        if c and c not in seen and len(c) == 6 and c.isdigit():
                            seen.add(c)
                            symbols.append(c)
                            if len(symbols) >= limit:
                                break
        except Exception as e:
            print(f"[MarketData] fetch_active_symbols error: {e}")

        # 不足时用默认池补充
        if len(symbols) < limit:
            defaults = [
                "000001", "000858", "002594", "300750", "600519",
                "601012", "688981", "300059", "002230", "000002",
                "600036", "601318", "000333", "002475", "300124",
                "603259", "600809", "000725", "002415", "300274",
            ]
            for d in defaults:
                if d not in symbols:
                    symbols.append(d)
                if len(symbols) >= limit:
                    break

        return symbols[:limit]

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
        """获取单只股票完整数据 — 依次尝试 QMT → akshare K线 → 涨停池"""
        result = None
        if self.qmt_connected and not self.qmt_degraded:
            result = self._fetch_from_qmt(symbol)
            if result is None:
                # QMT 首次失败后自动降级，避免后续重复错误
                if not self.qmt_degraded:
                    print("[MarketData] QMT 个股数据获取失败，自动降级到 akshare/涨停池")
                    self.qmt_degraded = True
        if result is None and self.ak_available:
            # 先试完整K线（可能被代理拦截），失败则从涨停池取基础数据
            result = self._fetch_stock_from_akshare(symbol)
        if result is None:
            result = self._fetch_from_limitup_pool(symbol)
        return result

    def _fetch_from_limitup_pool(self, symbol: str) -> Optional[dict]:
        """
        从已缓存的涨停池数据构造个股 watchlist 条目

        涨停池已有: 最新价, 涨跌幅, 换手率, 行业, 连板数, 封板资金
        缺失(硬编码): MA(用最新价近似), L2(默认值), ctx(从涨停池推导)
        """
        if self._zt_df_cache is None:
            return None

        zt_df = self._zt_df_cache
        if '代码' not in zt_df.columns:
            return None

        row = zt_df[zt_df['代码'].astype(str).str.strip() == symbol.strip()]
        if row.empty:
            return None

        row = row.iloc[0]
        price = float(row.get('最新价', 0))
        change_pct = float(row.get('涨跌幅', 0))
        turnover = float(row.get('换手率', 0))
        amount = float(row.get('成交额', 0))
        sector = str(row.get('所属行业', ''))
        board_count = int(row.get('连板数', 1))
        zhatban_count = int(row.get('炸板次数', 0))
        seal_fund = float(row.get('封板资金', 0))
        float_mv = float(row.get('流通市值', 0))

        # 从涨停统计推导连板信息
        stats_str = str(row.get('涨停统计', '1/1'))
        # 格式: "5/4" = 5天4板

        features = {
            "symbol": symbol,
            "ma_5": price,           # EOD 模式下 MA 用最新价近似
            "ma_20": price,
            "volume_ratio": 1.5,     # 涨停股通常放量
            "theme_heat": 0.7,
            "sector_score": 0.6,
            "sector": sector,
            "sector_limit_up_change": 0.2,
            "sector_fund_flow": seal_fund / max(float_mv, 1) * 100 if float_mv > 0 else 5,
            "sector_fund_flow_avg": 3,
            "sector_pct": change_pct / 100,
            "sector_volume_change": 0.3,
            "is_leader": board_count >= 3,
            "stock_5d_return": change_pct / 100,
            "market_5d_return": 0.0,
            "sector_5d_return": change_pct / 200,
            "leader_5d_return": change_pct / 100 if board_count >= 3 else 0.01,
        }

        l2_features = {
            "symbol": symbol,
            "net_big_flow": seal_fund * 0.3 if seal_fund > 0 else 0,
            "seal_ratio": min(seal_fund / max(float_mv, 1) * 100, 15) if float_mv > 0 else 3.0,
            "ddy": 0.5,
        }

        ctx = {
            "symbol": symbol,
            "board_count": board_count,
            "break_drop_pct": 0.03,
            "white_above_yellow": zhatban_count == 0,
            "buy_absorption": zhatban_count <= 1,
            "big_order_on_break": seal_fund > 100_000_000,
            "sector_limit_up_count": 5,
            "follower_count": max(0, board_count - 1),
            "theme_days": 2,
            "theme_name": sector,
            "reseal_1min_vol": 300,
            "first_seal_1min_vol": 500,
            "break_to_reseal_min": 8,
            "linkage_count": max(0, board_count - 1),
            "seal_ratio": min(seal_fund / max(float_mv, 1), 0.10) if float_mv > 0 else 0.03,
            "longhu_seats": 2 if board_count >= 3 else 1,
            "auction_amount": amount * 0.05,
            "float_market_cap": float_mv / 1e8 if float_mv > 0 else 30,
            "gap_up_pct": min(change_pct / 100, 0.10),
            "sector": sector,
            "sector_limit_up_change": 0.2,
            "sector_fund_flow": seal_fund / max(float_mv, 1) * 100 if float_mv > 0 else 5,
            "sector_fund_flow_avg": 3,
            "sector_pct": change_pct / 100,
            "sector_volume_change": 0.3,
            "is_leader": board_count >= 3,
            "stock_5d_return": change_pct / 100,
            "market_5d_return": 0.0,
            "sector_5d_return": change_pct / 200,
            "leader_5d_return": change_pct / 100 if board_count >= 3 else 0.01,
        }

        return {
            "symbol": symbol,
            "features": features,
            "l2_features": l2_features,
            "ctx": ctx,
        }

    def _to_qmt_symbol(self, code: str) -> str:
        """将纯数字代码转为 QMT xtdata 格式 (加交易所后缀)"""
        code = code.strip()
        if len(code) != 6 or not code.isdigit():
            return code
        if code.startswith(("60", "68")):
            return f"{code}.SH"
        elif code.startswith(("00", "30", "002", "003")):
            return f"{code}.SZ"
        elif code.startswith(("8", "4")):
            return f"{code}.BJ"
        return f"{code}.SZ"  # 默认深圳

    def _fetch_from_qmt(self, symbol: str) -> dict:
        """从 QMT xtdata 获取实时数据"""
        try:
            qmt_sym = self._to_qmt_symbol(symbol)
            # 日K数据
            bars = xtdata.get_market_data_ex(
                stock_list=[qmt_sym],
                period="1d",
                count=30,
            )

            # L2数据 (逐笔/盘口 — 仅在交易时段)
            l2_transaction = xtdata.get_l2_transaction(qmt_sym)
            l2_quote = xtdata.subscribe_quote(qmt_sym, period="l2quote")

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
        if self.ak_kline_degraded:
            return None  # 已降级，跳过避免重复错误
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
            if not self.ak_kline_degraded:
                print(f"[MarketData] akshare K线获取失败，自动降级到涨停池数据")
                self.ak_kline_degraded = True
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
