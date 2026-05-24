"""因子注册表：名称 → 计算函数映射"""

_REGISTRY: dict[str, callable] = {}


def register(name: str):
    def decorator(func):
        _REGISTRY[name] = func
        return func
    return decorator


def get_factor_func(name: str):
    if name not in _REGISTRY:
        raise KeyError(f"未注册的因子: {name}")
    return _REGISTRY[name]


def list_factors() -> list[str]:
    return list(_REGISTRY.keys())
