"""每日数据采集入口：A股 + ETF 日线"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger
from utils.logger import setup_logger

setup_logger()


def main():
    parser = argparse.ArgumentParser(description="采集 A股/ETF 日线数据")
    parser.add_argument("--start-date", help="起始日期 YYYYMMDD（默认增量采集）")
    parser.add_argument("--type", choices=["stock", "etf", "all"], default="all",
                        help="采集类型（默认 all）")
    args = parser.parse_args()

    from collector.stock_collector import collect_all_stocks
    from collector.etf_collector import collect_all_etfs

    logger.info("===== 日线数据采集开始 =====")

    results = {}
    if args.type in ("stock", "all"):
        results["stock"] = collect_all_stocks(args.start_date)
    if args.type in ("etf", "all"):
        results["etf"] = collect_all_etfs(args.start_date)

    logger.info("===== 日线数据采集完成 =====")
    for asset_type, r in results.items():
        logger.info("{}: 写入 {} 条, 成功 {}, 失败 {}",
                    asset_type, r["total_rows"], r["success"], r["failed"])


if __name__ == "__main__":
    main()
