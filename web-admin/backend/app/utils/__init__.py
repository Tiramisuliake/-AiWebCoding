from .parsers import parse_bool

__all__ = ["logger", "parse_bool"]


def __getattr__(name):
    if name == "logger":
        from .logger import logger

        return logger
    raise AttributeError(name)
