"""策略注册表：名称 → 策略类映射"""

from strategy.base import BaseStrategy
from strategy.bollinger_strategy import BollingerStrategy
from strategy.ma_cross import MaCrossStrategy
from strategy.macd_strategy import MacdStrategy
from strategy.rsi_strategy import RsiStrategy


_STRATEGIES: dict[str, type[BaseStrategy]] = {
    MaCrossStrategy.name: MaCrossStrategy,
    RsiStrategy.name: RsiStrategy,
    MacdStrategy.name: MacdStrategy,
    BollingerStrategy.name: BollingerStrategy,
}


def get_strategy(name: str, **kwargs) -> BaseStrategy:
    if name not in _STRATEGIES:
        raise KeyError(f"未注册的策略: {name}，可用: {list(_STRATEGIES.keys())}")
    return _STRATEGIES[name](**kwargs)


def list_strategies() -> list[str]:
    return list(_STRATEGIES.keys())
