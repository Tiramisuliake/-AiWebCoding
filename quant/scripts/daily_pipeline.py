"""全流程一键运行：采集 → 因子 → 信号 → 回测 → 报告"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger
from utils.logger import setup_logger

setup_logger()


def main():
    logger.info("========== 量化投研日常流程开始 ==========")

    # 1. 数据采集
    try:
        logger.info("----- 步骤 1/5: 日线数据采集 -----")
        from collector.stock_collector import collect_all_stocks
        from collector.etf_collector import collect_all_etfs
        stock_result = collect_all_stocks()
        etf_result = collect_all_etfs()
        logger.info("采集完成: A股 {} 条, ETF {} 条",
                     stock_result["total_rows"], etf_result["total_rows"])
    except Exception as e:
        logger.error("数据采集失败: {}", e)

    # 2. 因子计算
    try:
        logger.info("----- 步骤 2/5: 因子计算 -----")
        from scripts.compute_factors import compute_for_asset
        from db.models import AssetPool
        from db.session import get_session, remove_session
        from sqlalchemy import select

        session = get_session()
        assets = session.execute(
            select(AssetPool).where(AssetPool.is_active == True)
        ).scalars().all()
        remove_session()

        factor_total = 0
        for asset in assets:
            factor_total += compute_for_asset(asset.code, asset.name)
        logger.info("因子计算完成: {} 条", factor_total)
    except Exception as e:
        logger.error("因子计算失败: {}", e)

    # 3. 策略信号
    try:
        logger.info("----- 步骤 3/5: 策略信号生成 -----")
        from scripts.run_strategy import run_for_asset
        from strategy.ma_cross import MaCrossStrategy

        strategy = MaCrossStrategy()
        signal_total = 0
        for asset in assets:
            signal_total += run_for_asset(asset.code, asset.name, strategy)
        logger.info("信号生成完成: {} 条", signal_total)
    except Exception as e:
        logger.error("策略信号生成失败: {}", e)

    # 4. 回测
    try:
        logger.info("----- 步骤 4/5: 策略回测 -----")
        from scripts.run_backtest import backtest_asset
        from backtest.engine import BacktestConfig

        config = BacktestConfig()
        bt_success = 0
        for asset in assets:
            if backtest_asset(asset.code, asset.name, "ma_cross", config):
                bt_success += 1
        logger.info("回测完成: 成功 {} / {}", bt_success, len(assets))
    except Exception as e:
        logger.error("回测失败: {}", e)

    # 5. 报告
    try:
        logger.info("----- 步骤 5/5: 生成报告 -----")
        from report.daily_report import generate_signal_report, generate_backtest_report

        generate_signal_report()
        generate_backtest_report()
    except Exception as e:
        logger.error("报告生成失败: {}", e)

    logger.info("========== 量化投研日常流程完成 ==========")


if __name__ == "__main__":
    main()
