"""
A股涨跌停规则引擎

主板: ±10%
科创板: ±20%  (688xxx)
创业板: ±20%  (300xxx)
北交所: ±30%  (8xxxxx)
ST/*ST: ±5%
新股首日: 无限制 (注册制)
"""
from enum import Enum


class BoardType(Enum):
    MAIN = "主板"          # ±10%, 60xxxx/00xxxx
    GEM = "创业板"         # ±20%, 300xxx
    STAR = "科创板"        # ±20%, 688xxx
    BSE = "北交所"         # ±30%, 8xxxxx
    ST = "ST"              # ±5%


def get_board_type(symbol: str, is_st: bool = False) -> BoardType:
    """根据股票代码判断板块"""
    if is_st:
        return BoardType.ST
    code = symbol.replace("SH.", "").replace("SZ.", "").replace("BJ.", "")
    if code.startswith("300"):
        return BoardType.GEM
    if code.startswith("688"):
        return BoardType.STAR
    if code.startswith("8"):
        return BoardType.BSE
    return BoardType.MAIN


def limit_pct(board: BoardType) -> float:
    """涨跌停百分比"""
    return {
        BoardType.MAIN: 0.10,
        BoardType.GEM: 0.20,
        BoardType.STAR: 0.20,
        BoardType.BSE: 0.30,
        BoardType.ST: 0.05,
    }[board]


class LimitPriceEngine:
    """涨跌停引擎"""

    def __init__(self, symbol: str, prev_close: float, is_st: bool = False):
        self.symbol = symbol
        self.board = get_board_type(symbol, is_st)
        self.pct = limit_pct(self.board)
        self.prev_close = prev_close
        self.limit_up = round(prev_close * (1 + self.pct), 2)
        self.limit_down = round(prev_close * (1 - self.pct), 2)

    def is_at_limit_up(self, price: float) -> bool:
        return price >= self.limit_up

    def is_at_limit_down(self, price: float) -> bool:
        return price <= self.limit_down

    def clamp_price(self, price: float) -> float:
        """将价格限制在涨跌停范围内"""
        return max(self.limit_down, min(self.limit_up, price))

    def can_trade(self, price: float, direction: str) -> tuple[bool, str]:
        """
        判断能否以指定价格交易
        direction: BUY/SELL
        涨停: 买不进 (除非有人卖)
        跌停: 卖不出 (除非有人买)
        """
        if direction == "BUY" and self.is_at_limit_up(price):
            return False, f"{self.symbol} 涨停 ({self.limit_up}), 买盘排队中"
        if direction == "SELL" and self.is_at_limit_down(price):
            return False, f"{self.symbol} 跌停 ({self.limit_down}), 卖盘封死"
        return True, "OK"

    def summary(self) -> dict:
        return {
            "symbol": self.symbol,
            "board": self.board.value,
            "limit_pct": f"{self.pct*100}%",
            "prev_close": self.prev_close,
            "limit_up": self.limit_up,
            "limit_down": self.limit_down,
        }
