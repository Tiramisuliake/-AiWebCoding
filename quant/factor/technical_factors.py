"""技术指标因子：RSI、MACD、布林带、KDJ、ATR"""

import pandas as pd

from factor.registry import register


@register("rsi14")
def calc_rsi14(df: pd.DataFrame) -> pd.Series:
    """RSI 14：相对强弱指标，>70 超买，<30 超卖"""
    delta = df["close"].diff()
    gain = delta.where(delta > 0, 0).rolling(window=14, min_periods=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=14).mean()
    rs = gain / loss.replace(0, 1e-9)
    return 100 - (100 / (1 + rs))


@register("macd_dif")
def calc_macd_dif(df: pd.DataFrame) -> pd.Series:
    """MACD DIF：12 日 EMA - 26 日 EMA"""
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()
    return ema12 - ema26


@register("macd_dea")
def calc_macd_dea(df: pd.DataFrame) -> pd.Series:
    """MACD DEA：DIF 的 9 日 EMA"""
    dif = calc_macd_dif(df)
    return dif.ewm(span=9, adjust=False).mean()


@register("macd_hist")
def calc_macd_hist(df: pd.DataFrame) -> pd.Series:
    """MACD 柱：(DIF - DEA) * 2"""
    return (calc_macd_dif(df) - calc_macd_dea(df)) * 2


@register("boll_mid")
def calc_boll_mid(df: pd.DataFrame) -> pd.Series:
    """布林带中轨：20 日 MA"""
    return df["close"].rolling(window=20, min_periods=20).mean()


@register("boll_upper")
def calc_boll_upper(df: pd.DataFrame) -> pd.Series:
    """布林带上轨：MA20 + 2 * 20日std"""
    mid = calc_boll_mid(df)
    std = df["close"].rolling(window=20, min_periods=20).std()
    return mid + 2 * std


@register("boll_lower")
def calc_boll_lower(df: pd.DataFrame) -> pd.Series:
    """布林带下轨：MA20 - 2 * 20日std"""
    mid = calc_boll_mid(df)
    std = df["close"].rolling(window=20, min_periods=20).std()
    return mid - 2 * std


@register("kdj_k")
def calc_kdj_k(df: pd.DataFrame) -> pd.Series:
    """KDJ K 值（9 日周期）"""
    low_min = df["low"].rolling(window=9, min_periods=9).min()
    high_max = df["high"].rolling(window=9, min_periods=9).max()
    rsv = (df["close"] - low_min) / (high_max - low_min).replace(0, 1e-9) * 100
    return rsv.ewm(com=2, adjust=False).mean()


@register("kdj_d")
def calc_kdj_d(df: pd.DataFrame) -> pd.Series:
    """KDJ D 值：K 的 3 日 SMA"""
    k = calc_kdj_k(df)
    return k.ewm(com=2, adjust=False).mean()


@register("kdj_j")
def calc_kdj_j(df: pd.DataFrame) -> pd.Series:
    """KDJ J 值：3K - 2D"""
    return 3 * calc_kdj_k(df) - 2 * calc_kdj_d(df)


@register("atr14")
def calc_atr14(df: pd.DataFrame) -> pd.Series:
    """ATR 14：真实波幅，衡量价格波动幅度"""
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift()).abs()
    low_close = (df["low"] - df["close"].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=14, min_periods=14).mean()


@register("volume_ratio")
def calc_volume_ratio(df: pd.DataFrame) -> pd.Series:
    """量比：当日成交量 / 过去 5 日平均成交量"""
    avg_vol = df["volume"].rolling(window=5, min_periods=5).mean().shift(1)
    return df["volume"] / avg_vol.replace(0, 1e-9)
