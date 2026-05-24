"""飞书机器人消息推送（自定义机器人，带签名校验）"""

from .network import ensure_proxy_disabled
ensure_proxy_disabled()

import base64
import hashlib
import hmac
import json
import time
from typing import Any

import requests
from loguru import logger


# 硬编码配置（后续可移到 .env）
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/27c1860e-ba1e-41f4-939e-0adb0ca028e6"
FEISHU_SECRET = "pcH8Y7tgCtnCkS8QMadVB"
FEISHU_TIMEOUT = 5


def _gen_sign(timestamp: int, secret: str) -> str:
    string_to_sign = f"{timestamp}\n{secret}"
    hmac_code = hmac.new(
        string_to_sign.encode("utf-8"), digestmod=hashlib.sha256
    ).digest()
    return base64.b64encode(hmac_code).decode("utf-8")


def _post(payload: dict) -> bool:
    timestamp = int(time.time())
    payload["timestamp"] = str(timestamp)
    payload["sign"] = _gen_sign(timestamp, FEISHU_SECRET)

    try:
        r = requests.post(FEISHU_WEBHOOK, json=payload, timeout=FEISHU_TIMEOUT)
        result = r.json()
        if result.get("code") == 0 or result.get("StatusCode") == 0:
            return True
        logger.warning("飞书推送失败: {}", result)
        return False
    except Exception as e:
        logger.error("飞书推送异常: {}", e)
        return False


def send_text(text: str) -> bool:
    """发送纯文本消息"""
    return _post({"msg_type": "text", "content": {"text": text}})


def send_card(title: str, fields: list[tuple[str, str]], theme: str = "blue") -> bool:
    """
    发送富卡片消息。

    参数:
        title: 卡片标题
        fields: [(键, 值), ...] 列表
        theme: 标题主题色 blue/green/red/orange/grey
    """
    elements = []
    if fields:
        rows = []
        for k, v in fields:
            rows.append({
                "is_short": True,
                "text": {"tag": "lark_md", "content": f"**{k}**\n{v}"},
            })
        elements.append({"tag": "div", "fields": rows})

    elements.append({
        "tag": "note",
        "elements": [{
            "tag": "plain_text",
            "content": f"quant · {time.strftime('%Y-%m-%d %H:%M:%S')}",
        }],
    })

    payload = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": theme,
            },
            "elements": elements,
        },
    }
    return _post(payload)


def notify_signals(strategy_name: str, signals: list[dict]) -> bool:
    """推送策略生成的交易信号"""
    if not signals:
        return True

    buys = [s for s in signals if s.get("signal") == "buy"]
    sells = [s for s in signals if s.get("signal") == "sell"]

    lines = [f"📊 策略 [{strategy_name}] 新生成 {len(signals)} 条信号"]
    if buys:
        lines.append(f"\n🟢 买入 ({len(buys)}):")
        for s in buys[:10]:
            lines.append(f"  • {s['code']} | {s.get('reason', '')}")
    if sells:
        lines.append(f"\n🔴 卖出 ({len(sells)}):")
        for s in sells[:10]:
            lines.append(f"  • {s['code']} | {s.get('reason', '')}")

    if len(signals) > 20:
        lines.append(f"\n... 还有 {len(signals) - 20} 条")

    return send_text("\n".join(lines))


def notify_pipeline_summary(summary: dict) -> bool:
    """推送 daily_pipeline 全流程汇总"""
    fields = [
        ("数据采集", f"A股 {summary.get('stock_rows', 0)} / ETF {summary.get('etf_rows', 0)}"),
        ("因子计算", f"{summary.get('factor_count', 0)} 条"),
        ("信号生成", f"{summary.get('signal_count', 0)} 条"),
        ("回测完成", f"{summary.get('backtest_count', 0)} 次"),
    ]
    if summary.get("errors"):
        fields.append(("⚠️ 错误", "\n".join(summary["errors"][:3])))

    theme = "red" if summary.get("errors") else "green"
    return send_card("📈 quant 日常流程完成", fields, theme=theme)


def notify_error(stage: str, error: str) -> bool:
    """推送错误告警"""
    return send_card(
        "❌ quant 流程异常",
        [("阶段", stage), ("错误", error[:500])],
        theme="red",
    )
