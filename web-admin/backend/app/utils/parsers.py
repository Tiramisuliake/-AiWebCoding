def parse_bool(value, default=None):
    if value in (1, "1", True, "true", "True"):
        return True
    if value in (0, "0", False, "false", "False"):
        return False
    return default


__all__ = ["parse_bool"]
