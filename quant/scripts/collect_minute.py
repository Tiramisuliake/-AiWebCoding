"""分钟级数据采集入口"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger
from utils.logger import setup_logger

setup_logger()


def main():
    parser = argparse.ArgumentParser(description="采集分钟级 K 线数据")
    parser.add_argument("--periods", help="周期列表，逗号分隔（如 1,5,15,30,60）")
    args = parser.parse_args()

    from collector.minute_collector import collect_all_minutes

    periods = args.periods.split(",") if args.periods else None

    logger.info("===== 分钟级数据采集开始 =====")
    result = collect_all_minutes(periods)
    logger.info("===== 分钟级数据采集完成: {} =====", result)


if __name__ == "__main__":
    main()
