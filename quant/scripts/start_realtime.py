"""启动实时行情 WebSocket 服务"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger
from utils.logger import setup_logger

setup_logger()


def main():
    from collector.realtime import start_server

    logger.info("===== 实时行情推送服务启动 =====")
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        logger.info("收到中断信号，服务退出")


if __name__ == "__main__":
    main()
