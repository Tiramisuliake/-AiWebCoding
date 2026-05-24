"""策略基类"""

from abc import ABC, abstractmethod

import pandas as pd


class BaseStrategy(ABC):
    name: str = "base"

    @abstractmethod
    def generate_signals(self, code: str, df: pd.DataFrame) -> list[dict]:
        """
        生成交易信号。

        参数:
            code: 资产代码
            df: 包含 OHLCV + 因子列的 DataFrame，按 trade_date 升序

        返回:
            [{"code", "trade_date", "strategy_name", "signal", "strength", "reason"}, ...]
        """
