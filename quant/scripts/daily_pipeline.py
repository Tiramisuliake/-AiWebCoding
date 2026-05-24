"""全流程一键运行：采集 → 因子 → 信号 → 回测 → 报告 → 飞书推送"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger
from sqlalchemy import select

from utils.logger import setup_logger
from utils.notifier import notify_error, notify_pipeline_summary

setup_logger()


def _load_active_assets():
    from db.models import AssetPool
    from db.session import get_session, remove_session
    session = get_session()
    try:
        return session.execute(
            select(AssetPool).where(AssetPool.is_active == True)
        ).scalars().all()
    finally:
        remove_session()


def main():
    logger.info("========== 量化投研日常流程开始 ==========")

    summary = {
        "stock_rows": 0, "etf_rows": 0, "factor_count": 0,
        "signal_count": 0, "backtest_count": 0, "errors": [],
    }

    try:
        assets = _load_active_assets()
        logger.info("活跃资产 {} 个", len(assets))
    except Exception as e:
        logger.error("加载资产池失败: {}", e)
        summary["errors"].append(f"加载资产池: {e}")
        notify_error("加载资产池", str(e))
        return

    # 1. 数据采集
    try:
        logger.info("----- 步骤 1/5: 日线数据采集 -----")
        from collector.stock_collector import collect_all_stocks
        from collector.etf_collector import collect_all_etfs
        stock_result = collect_all_stocks()
        etf_result = collect_all_etfs()
        summary["stock_rows"] = stock_result.get("total_rows", 0)
        summary["etf_rows"] = etf_result.get("total_rows", 0)
        logger.info("采集完成: A股 {} 条, ETF {} 条",
                    summary["stock_rows"], summary["etf_rows"])
    except Exception as e:
        logger.error("数据采集失败: {}", e)
        summary["errors"].append(f"数据采集: {e}")

    # 2. 因子计算
    try:
        logger.info("----- 步骤 2/5: 因子计算 -----")
        from scripts.compute_factors import compute_for_asset

        for asset in assets:
            summary["factor_count"] += compute_for_asset(asset.code, asset.name)
        logger.info("因子计算完成: {} 条", summary["factor_count"])
    except Exception as e:
        logger.error("因子计算失败: {}", e)
        summary["errors"].append(f"因子计算: {e}")

    # 3. 策略信号（全部策略）
    try:
        logger.info("----- 步骤 3/5: 策略信号生成 -----")
        from scripts.run_strategy import run_for_asset
        from strategy.registry import get_strategy, list_strategies

        for strategy_name in list_strategies():
            strategy = get_strategy(strategy_name)
            logger.info("运行策略: {}", strategy_name)
            for asset in assets:
                summary["signal_count"] += run_for_asset(asset.code, asset.name, strategy)
        logger.info("信号生成完成: {} 条", summary["signal_count"])
    except Exception as e:
        logger.error("策略信号生成失败: {}", e)
        summary["errors"].append(f"信号生成: {e}")

    # 4. 回测
    try:
        logger.info("----- 步骤 4/5: 策略回测 -----")
        from scripts.run_backtest import backtest_asset
        from backtest.engine import BacktestConfig
        from strategy.registry import list_strategies

        config = BacktestConfig()
        for strategy_name in list_strategies():
            for asset in assets:
                if backtest_asset(asset.code, asset.name, strategy_name, config):
                    summary["backtest_count"] += 1
        logger.info("回测完成: {} 次", summary["backtest_count"])
    except Exception as e:
        logger.error("回测失败: {}", e)
        summary["errors"].append(f"回测: {e}")

    # 5. 报告
    try:
        logger.info("----- 步骤 5/5: 生成报告 -----")
        from report.daily_report import generate_signal_report, generate_backtest_report
        from strategy.registry import list_strategies

        generate_signal_report()
        for strategy_name in list_strategies():
            generate_backtest_report(strategy_name)
    except Exception as e:
        logger.error("报告生成失败: {}", e)
        summary["errors"].append(f"报告: {e}")

    # 6. 飞书推送汇总
    try:
        notify_pipeline_summary(summary)
        logger.info("飞书汇总推送完成")
    except Exception as e:
        logger.warning("飞书推送失败: {}", e)

    logger.info("========== 量化投研日常流程完成 ==========")
    logger.info("汇总: {}", summary)


if __name__ == "__main__":
    main()
