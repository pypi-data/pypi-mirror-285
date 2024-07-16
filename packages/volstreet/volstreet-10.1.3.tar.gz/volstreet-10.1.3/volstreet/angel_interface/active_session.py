from volstreet import config
from collections import namedtuple

ProxyObj = namedtuple("ProxyObj", ["userId"])


class ActiveSession:
    if config.backtest_mode:
        obj = ProxyObj(userId="backtester")
    else:
        obj = None
        login_data = None
