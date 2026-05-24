"""多因子选股模型：截面标准化、打分、加权合成、排序"""

from datetime import date
from decimal import Decimal

import pandas as pd
from loguru import logger
from sqlalchemy import select

from config.settings import settings
from db.models import FactorScore, FactorValue
from db.session import get_session, remove_session


# 因子方向：True = 正向（值大评分高），False = 反向（值小评分高）
FACTOR_DIRECTIONS = {
    "ma5": True,
    "ma20": True,
    "ma60": True,
    "return_20d": True,
    "return_60d": True,
    "volatility_20d": False,
    "turnover": True,
}


def compute_scores(trade_dt: date, weights: dict | None = None) -> int:
    """
    计算指定日期所有资产的多因子评分。

    流程：
    1. 取该日所有因子值
    2. 按因子做截面排名 → 百分位（rank_pct）
    3. 反向因子翻转（1 - rank_pct）
    4. 评分 = rank_pct * 100
    5. 综合评分 = sum(rank_pct * weight)
    6. 写入 factor_score
    """
    if weights is None:
        weights = settings.MULTI_FACTOR_WEIGHTS

    session = get_session()
    try:
        factor_names = list(weights.keys())
        rows = session.execute(
            select(FactorValue).where(
                FactorValue.trade_date == trade_dt,
                FactorValue.factor_name.in_(factor_names),
            )
        ).scalars().all()

        if not rows:
            logger.info("{} 无因子数据，跳过", trade_dt)
            return 0

        df = pd.DataFrame([{
            "code": r.code,
            "factor_name": r.factor_name,
            "value": float(r.value),
        } for r in rows])

        pivot = df.pivot_table(index="code", columns="factor_name", values="value")

        score_records = []
        for factor_name in factor_names:
            if factor_name not in pivot.columns:
                logger.warning("因子 {} 在 {} 无数据，跳过", factor_name, trade_dt)
                continue

            direction = FACTOR_DIRECTIONS.get(factor_name, True)
            ranks = pivot[factor_name].rank(method="average", ascending=direction, pct=True)
            pivot[f"{factor_name}_rank"] = ranks
            pivot[f"{factor_name}_score"] = ranks * 100

        pivot["composite"] = 0.0
        total_weight = 0.0
        for factor_name, weight in weights.items():
            rank_col = f"{factor_name}_rank"
            if rank_col in pivot.columns:
                pivot["composite"] += pivot[rank_col].fillna(0.5) * weight
                total_weight += weight

        if total_weight > 0:
            pivot["composite"] = pivot["composite"] / total_weight

        count = 0
        for code, row in pivot.iterrows():
            composite = round(float(row["composite"]) * 100, 4)
            for factor_name in factor_names:
                rank_col = f"{factor_name}_rank"
                score_col = f"{factor_name}_score"
                if rank_col not in pivot.columns or pd.isna(row.get(rank_col)):
                    continue

                exists = session.execute(
                    select(FactorScore.id).where(
                        FactorScore.code == code,
                        FactorScore.trade_date == trade_dt,
                        FactorScore.factor_name == factor_name,
                    )
                ).scalar()
                if exists:
                    continue

                session.add(FactorScore(
                    code=code,
                    trade_date=trade_dt,
                    factor_name=factor_name,
                    raw_value=Decimal(str(row[factor_name])),
                    score=Decimal(str(round(float(row[score_col]), 4))),
                    rank_pct=Decimal(str(round(float(row[rank_col]), 4))),
                    composite_score=Decimal(str(composite)),
                ))
                count += 1

        session.commit()
        logger.info("{} 因子评分完成，写入 {} 条", trade_dt, count)
        return count

    except Exception as e:
        session.rollback()
        logger.error("{} 因子评分失败: {}", trade_dt, e)
        return 0
    finally:
        remove_session()


def select_top_stocks(trade_dt: date, top_n: int | None = None) -> list[dict]:
    """按综合评分选出 top N"""
    if top_n is None:
        top_n = settings.MULTI_FACTOR_TOP_N

    session = get_session()
    try:
        rows = session.execute(
            select(
                FactorScore.code,
                FactorScore.composite_score,
            )
            .where(FactorScore.trade_date == trade_dt)
            .distinct()
            .order_by(FactorScore.composite_score.desc())
            .limit(top_n)
        ).all()

        result = [{"code": r[0], "composite_score": float(r[1])} for r in rows]
        logger.info("{} 选出 top {}: {}", trade_dt, top_n, [r["code"] for r in result])
        return result
    finally:
        remove_session()
