from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base


PRICE = Numeric(12, 4)       # 价格类（最大 99999999.9999）
AMOUNT = Numeric(20, 2)      # 成交额（最大 999999999999999999.99 ≈ 10^18）
TURNOVER = Numeric(8, 4)     # 百分比（最大 9999.9999%）
FACTOR_VAL = Numeric(20, 6)  # 因子值（动量/收益率可能负，须够大）
SCORE = Numeric(8, 4)        # 0~100 评分
RATIO = Numeric(10, 4)       # 比率（收益率/回撤等）


class DailyPrice(Base):
    __tablename__ = "quant_daily_price"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(10), nullable=False)
    trade_date: Mapped[date] = mapped_column(nullable=False)
    open: Mapped[Decimal] = mapped_column(PRICE, nullable=False)
    high: Mapped[Decimal] = mapped_column(PRICE, nullable=False)
    low: Mapped[Decimal] = mapped_column(PRICE, nullable=False)
    close: Mapped[Decimal] = mapped_column(PRICE, nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    amount: Mapped[Decimal] = mapped_column(AMOUNT, nullable=False)
    turnover: Mapped[Optional[Decimal]] = mapped_column(TURNOVER, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    __table_args__ = (
        UniqueConstraint("code", "trade_date", name="uq_daily_code_date"),
        Index("ix_daily_trade_date", "trade_date"),
        Index("ix_daily_code_date", "code", "trade_date"),
    )


class MinutePrice(Base):
    __tablename__ = "quant_minute_price"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(10), nullable=False)
    trade_date: Mapped[date] = mapped_column(nullable=False)
    trade_time: Mapped[datetime] = mapped_column(nullable=False)
    period: Mapped[str] = mapped_column(String(5), nullable=False)
    open: Mapped[Decimal] = mapped_column(PRICE, nullable=False)
    high: Mapped[Decimal] = mapped_column(PRICE, nullable=False)
    low: Mapped[Decimal] = mapped_column(PRICE, nullable=False)
    close: Mapped[Decimal] = mapped_column(PRICE, nullable=False)
    volume: Mapped[int] = mapped_column(BigInteger, nullable=False)
    amount: Mapped[Decimal] = mapped_column(AMOUNT, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    __table_args__ = (
        UniqueConstraint("code", "trade_time", "period", name="uq_minute_code_time_period"),
        Index("ix_minute_code_date_period", "code", "trade_date", "period"),
        Index("ix_minute_trade_date", "trade_date"),
    )


class AssetPool(Base):
    __tablename__ = "quant_asset_pool"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(10), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)


class FactorValue(Base):
    __tablename__ = "quant_factor_value"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    trade_date: Mapped[date] = mapped_column(nullable=False)
    factor_name: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[Decimal] = mapped_column(FACTOR_VAL, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    __table_args__ = (
        UniqueConstraint("code", "trade_date", "factor_name", name="uq_factor_code_date_name"),
        Index("ix_factor_trade_date", "trade_date"),
    )


class FactorScore(Base):
    __tablename__ = "quant_factor_score"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    trade_date: Mapped[date] = mapped_column(nullable=False)
    factor_name: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_value: Mapped[Decimal] = mapped_column(FACTOR_VAL, nullable=False)
    score: Mapped[Decimal] = mapped_column(SCORE, nullable=False)
    rank_pct: Mapped[Decimal] = mapped_column(SCORE, nullable=False)
    composite_score: Mapped[Decimal] = mapped_column(SCORE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    __table_args__ = (
        UniqueConstraint("code", "trade_date", "factor_name", name="uq_score_code_date_name"),
        Index("ix_score_date_composite", "trade_date", "composite_score"),
    )


class TradingSignal(Base):
    __tablename__ = "quant_trading_signal"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    trade_date: Mapped[date] = mapped_column(nullable=False)
    strategy_name: Mapped[str] = mapped_column(String(50), nullable=False)
    signal: Mapped[str] = mapped_column(String(10), nullable=False)
    strength: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    __table_args__ = (
        UniqueConstraint("code", "trade_date", "strategy_name", name="uq_signal_code_date_strategy"),
        Index("ix_signal_trade_date", "trade_date"),
    )


class BacktestResult(Base):
    __tablename__ = "quant_backtest_result"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    strategy_name: Mapped[str] = mapped_column(String(50), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
    initial_capital: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    final_capital: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    total_return: Mapped[Decimal] = mapped_column(RATIO, nullable=False)
    annual_return: Mapped[Decimal] = mapped_column(RATIO, nullable=False)
    max_drawdown: Mapped[Decimal] = mapped_column(RATIO, nullable=False)
    sharpe_ratio: Mapped[Decimal] = mapped_column(RATIO, nullable=False)
    win_rate: Mapped[Decimal] = mapped_column(RATIO, nullable=False)
    trade_count: Mapped[int] = mapped_column(nullable=False)
    params_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
