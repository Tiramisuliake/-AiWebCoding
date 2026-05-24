"""实时行情推送服务（WebSocket）"""

from utils.network import ensure_proxy_disabled
ensure_proxy_disabled()

import asyncio
import json
from datetime import datetime

import akshare as ak
import pandas as pd
from loguru import logger

try:
    import websockets
except ImportError:
    websockets = None

from config.settings import settings


_subscribers: dict = {}
_latest_quotes: dict = {}


def _fetch_spot_data() -> pd.DataFrame | None:
    """获取全市场实时行情快照"""
    try:
        df = ak.stock_zh_a_spot_em()
        return df
    except Exception as e:
        logger.error("获取实时行情失败: {}", e)
        return None


def _format_quote(row: pd.Series) -> dict:
    return {
        "code": str(row.get("代码", "")),
        "name": str(row.get("名称", "")),
        "price": float(row.get("最新价", 0) or 0),
        "change": float(row.get("涨跌额", 0) or 0),
        "change_pct": float(row.get("涨跌幅", 0) or 0),
        "volume": int(row.get("成交量", 0) or 0),
        "amount": float(row.get("成交额", 0) or 0),
        "high": float(row.get("最高", 0) or 0),
        "low": float(row.get("最低", 0) or 0),
        "open": float(row.get("今开", 0) or 0),
        "timestamp": datetime.now().isoformat(),
    }


async def _poll_loop():
    """定时轮询行情并推送给订阅者"""
    while True:
        try:
            df = await asyncio.to_thread(_fetch_spot_data)
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    quote = _format_quote(row)
                    _latest_quotes[quote["code"]] = quote

                for ws, codes in list(_subscribers.items()):
                    try:
                        payload = []
                        if codes is None or len(codes) == 0:
                            payload = list(_latest_quotes.values())[:50]
                        else:
                            payload = [_latest_quotes[c] for c in codes if c in _latest_quotes]

                        if payload:
                            await ws.send(json.dumps({
                                "type": "quote",
                                "data": payload,
                            }, ensure_ascii=False))
                    except Exception as e:
                        logger.warning("推送失败，移除订阅者: {}", e)
                        _subscribers.pop(ws, None)

        except Exception as e:
            logger.error("轮询失败: {}", e)

        await asyncio.sleep(settings.REALTIME_POLL_INTERVAL)


async def _handle_client(websocket):
    """处理 WebSocket 客户端连接"""
    client_addr = websocket.remote_address
    logger.info("客户端连接: {}", client_addr)
    _subscribers[websocket] = set()

    try:
        await websocket.send(json.dumps({
            "type": "welcome",
            "message": "已连接到 quant 实时行情",
            "poll_interval": settings.REALTIME_POLL_INTERVAL,
        }, ensure_ascii=False))

        async for message in websocket:
            try:
                msg = json.loads(message)
                action = msg.get("action")

                if action == "subscribe":
                    codes = set(msg.get("codes", []))
                    _subscribers[websocket] = codes
                    logger.info("{} 订阅: {}", client_addr, codes)
                    await websocket.send(json.dumps({
                        "type": "subscribed",
                        "codes": list(codes),
                    }, ensure_ascii=False))

                elif action == "unsubscribe":
                    codes = set(msg.get("codes", []))
                    current = _subscribers.get(websocket, set())
                    _subscribers[websocket] = current - codes
                    await websocket.send(json.dumps({
                        "type": "unsubscribed",
                        "codes": list(codes),
                    }, ensure_ascii=False))

                elif action == "ping":
                    await websocket.send(json.dumps({"type": "pong"}))

            except json.JSONDecodeError:
                logger.warning("非法消息: {}", message)
            except Exception as e:
                logger.error("处理消息失败: {}", e)

    except Exception as e:
        logger.info("客户端断开: {} ({})", client_addr, e)
    finally:
        _subscribers.pop(websocket, None)


async def start_server():
    if websockets is None:
        raise RuntimeError("未安装 websockets，请运行 pip install websockets")

    poll_task = asyncio.create_task(_poll_loop())

    logger.info(
        "WebSocket 服务启动: ws://{}:{} (轮询间隔 {}s)",
        settings.REALTIME_WS_HOST, settings.REALTIME_WS_PORT, settings.REALTIME_POLL_INTERVAL,
    )

    async with websockets.serve(
        _handle_client, settings.REALTIME_WS_HOST, settings.REALTIME_WS_PORT
    ):
        try:
            await poll_task
        except asyncio.CancelledError:
            logger.info("服务停止")
