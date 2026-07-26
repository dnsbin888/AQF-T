"""
A股交易日历
"""
from datetime import date, timedelta


# A股2026年主要节假日 (简化版)
HOLIDAYS_2026 = {
    date(2026, 1, 1), date(2026, 1, 2),    # 元旦
    date(2026, 2, 16), date(2026, 2, 17), date(2026, 2, 18), date(2026, 2, 19), date(2026, 2, 20),  # 春节
    date(2026, 4, 6),                        # 清明
    date(2026, 5, 1), date(2026, 5, 4), date(2026, 5, 5),  # 劳动节
    date(2026, 6, 22),                       # 端午
    date(2026, 9, 28),                       # 中秋
    date(2026, 10, 1), date(2026, 10, 2), date(2026, 10, 5), date(2026, 10, 6), date(2026, 10, 7),  # 国庆
}

WEEKEND = {5, 6}  # 周六=5, 周日=6


def is_trading_day(d: date) -> bool:
    """判断是否为A股交易日"""
    if d in HOLIDAYS_2026:
        return False
    if d.weekday() in WEEKEND:
        return False
    return True


def next_trading_day(d: date) -> date:
    """下一个交易日"""
    d = d + timedelta(days=1)
    while not is_trading_day(d):
        d = d + timedelta(days=1)
    return d


def prev_trading_day(d: date) -> date:
    """上一个交易日"""
    d = d - timedelta(days=1)
    while not is_trading_day(d):
        d = d - timedelta(days=1)
    return d


def trading_days_between(start: date, end: date) -> list[date]:
    """两个日期之间的所有交易日"""
    days = []
    current = start
    while current <= end:
        if is_trading_day(current):
            days.append(current)
        current += timedelta(days=1)
    return days


def trading_session(d: date) -> str:
    """判断当前时段"""
    from datetime import datetime
    now = datetime.now()
    morning_open = now.replace(hour=9, minute=30, second=0)
    morning_close = now.replace(hour=11, minute=30, second=0)
    afternoon_open = now.replace(hour=13, minute=0, second=0)
    afternoon_close = now.replace(hour=15, minute=0, second=0)

    if not is_trading_day(d):
        return "CLOSED"
    if morning_open <= now < morning_close:
        return "MORNING_SESSION"
    if morning_close <= now < afternoon_open:
        return "LUNCH_BREAK"
    if afternoon_open <= now < afternoon_close:
        return "AFTERNOON_SESSION"
    return "CLOSED"
