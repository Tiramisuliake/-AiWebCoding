"""基础因子：MA5/20/60、20d/60d 收益率、20d 波动率"""

import math

import pandas as pd

from factor.registry import register


@register("ma5")
def calc_ma5(df: pd.DataFrame) -> pd.Series:
    return df["close"].rolling(window=5, min_periods=5).mean()


@register("ma20")
def calc_ma20(df: pd.DataFrame) -> pd.Series:
    return df["close"].rolling(window=20, min_periods=20).mean()


@register("ma60")
def calc_ma60(df: pd.DataFrame) -> pd.Series:
    return df["close"].rolling(window=60, min_periods=60).mean()


@register("return_20d")
def calc_return_20d(df: pd.DataFrame) -> pd.Series:
    return df["close"].pct_change(periods=20)


@register("return_60d")
def calc_return_60d(df: pd.DataFrame) -> pd.Series:
    return df["close"].pct_change(periods=60)


@register("volatility_20d")
def calc_volatility_20d(df: pd.DataFrame) -> pd.Series:
    daily_return = df["close"].pct_change()
    return daily_return.rolling(window=20, min_periods=20).std() * math.sqrt(252)
