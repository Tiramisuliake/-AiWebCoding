import os
import sys
import traceback
from datetime import datetime, time, timedelta
from pathlib import Path

from loguru import logger

script_name = os.path.basename(sys.argv[0]) or "app.py"
logger.remove()


class Rotator:
    def __init__(self, *, size, at):
        now = datetime.now()

        self._size_limit = size
        self._time_limit = now.replace(
            hour=at.hour, minute=at.minute, second=at.second, microsecond=0
        )

        if now >= self._time_limit:
            self._time_limit += timedelta(days=1)

    def should_rotate(self, message, file):
        try:
            file.seek(0, 2)
            if file.tell() + len(message) > self._size_limit:
                return True
            if message.record["time"].timestamp() > self._time_limit.timestamp():
                self._time_limit += timedelta(days=1)
                return True
            return False
        except Exception:
            traceback.print_exc()
            return True


rotator = Rotator(size=1 * 1024 * 1024 * 30, at=time(0, 0, 0))

project_root = Path(__file__).resolve().parents[2]
logs_dir = project_root / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)
out_put_file_name = str(logs_dir / f"{script_name.split('.')[0]}_{{time:YYYY-MM-DD}}.log")

log_format = (
    "[<fg #00CC00><b>{time:YYYY-MM-DD HH:mm:ss.SSS}</b></fg #00CC00>] "
    "[<b>{level}</b>] [<fg #DDA0DD>{process}</fg #DDA0DD>] - "
    "[<fg #DDA0DD>{thread.name}</fg #DDA0DD>] "
    "<fg #FFA07A>{file}</fg #FFA07A>.<fg #FFA07A>{function}</fg #FFA07A>"
    "`<fg #EEE8AA>{line}</fg #EEE8AA><b>:</b> <fg #FF9933>{message}</fg #FF9933>"
)

logger.add(
    out_put_file_name,
    rotation=rotator.should_rotate,
    retention="30 days",
    encoding="UTF-8",
    enqueue=True,
    format=log_format,
    level="INFO",
)

logger.add(sys.stdout, colorize=True, format=log_format, level="DEBUG")
