"""网络相关工具：禁用系统代理避免影响 AkShare/requests 调用"""

import os

import requests
from loguru import logger


def disable_proxy():
    """
    禁用系统代理。

    Windows 上 requests 会读取注册表的 ProxyServer 配置，
    即使环境变量清空也可能走代理。这里通过：
    1. 清空环境变量
    2. monkey-patch requests.Session.trust_env = False
    确保所有 HTTP 请求绕过代理。
    """
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "ALL_PROXY", "all_proxy"):
        os.environ.pop(key, None)
    os.environ["NO_PROXY"] = "*"
    os.environ["no_proxy"] = "*"

    _orig_init = requests.Session.__init__

    def _patched_init(self, *args, **kwargs):
        _orig_init(self, *args, **kwargs)
        self.trust_env = False
        self.proxies = {}

    requests.Session.__init__ = _patched_init
    logger.debug("已禁用系统代理（NO_PROXY=* + trust_env=False）")


_PROXY_DISABLED = False


def ensure_proxy_disabled():
    """幂等版本，多次调用只生效一次"""
    global _PROXY_DISABLED
    if not _PROXY_DISABLED:
        disable_proxy()
        _PROXY_DISABLED = True
