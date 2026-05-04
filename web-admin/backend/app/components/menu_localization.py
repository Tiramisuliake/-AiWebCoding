from __future__ import annotations

import re

BUILTIN_MENU_ROUTE_NAME_ZH = {
    "/": "仪表盘",
    "/users": "用户管理",
    "/roles": "角色管理",
    "/permissions": "权限列表",
    "/menus": "菜单管理",
}

BUILTIN_MENU_NAME_EXACT_ZH = {
    "dashboard": "仪表盘",
    "users": "用户管理",
    "roles": "角色管理",
    "permissions": "权限列表",
    "menus": "菜单管理",
    "permission management": "权限管理",
}

MENU_NAME_TOKEN_ZH = {
    "admin": "管理",
    "analytics": "分析",
    "api": "接口",
    "app": "应用",
    "audit": "审计",
    "center": "中心",
    "config": "配置",
    "content": "内容",
    "create": "创建",
    "dashboard": "仪表盘",
    "data": "数据",
    "delete": "删除",
    "detail": "详情",
    "disabled": "禁用",
    "edit": "编辑",
    "enabled": "启用",
    "feature": "功能",
    "group": "分组",
    "hidden": "隐藏",
    "home": "首页",
    "info": "信息",
    "job": "任务",
    "jobs": "任务",
    "list": "列表",
    "log": "日志",
    "logs": "日志",
    "manage": "管理",
    "management": "管理",
    "menu": "菜单",
    "menus": "菜单",
    "monitor": "监控",
    "node": "节点",
    "ops": "运维",
    "operation": "运维",
    "operations": "运维",
    "overview": "概览",
    "permission": "权限",
    "permissions": "权限",
    "profile": "资料",
    "read": "查看",
    "report": "报表",
    "reports": "报表",
    "role": "角色",
    "roles": "角色",
    "root": "根",
    "setting": "设置",
    "settings": "设置",
    "status": "状态",
    "system": "系统",
    "task": "任务",
    "tasks": "任务",
    "team": "团队",
    "tool": "工具",
    "tools": "工具",
    "update": "更新",
    "user": "用户",
    "users": "用户",
    "view": "查看",
}


def contains_cjk(value: str) -> bool:
    if not value:
        return False
    return bool(re.search(r"[\u4e00-\u9fff]", value))


def _split_words(name: str) -> list[str]:
    if not name:
        return []

    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    normalized = re.sub(r"[_\-]+", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    if not normalized:
        return []
    return normalized.split(" ")


def normalize_menu_name_to_cn(name: str, route_path: str | None = None) -> str:
    raw_name = str(name or "").strip()
    if not raw_name:
        return raw_name

    if contains_cjk(raw_name):
        return raw_name

    route_name = BUILTIN_MENU_ROUTE_NAME_ZH.get((route_path or "").strip())
    if route_name:
        return route_name

    exact_name = BUILTIN_MENU_NAME_EXACT_ZH.get(raw_name.lower())
    if exact_name:
        return exact_name

    words = _split_words(raw_name)
    if not words:
        return raw_name

    translated_words: list[str] = []
    translated_count = 0
    for word in words:
        lowered = word.lower()
        translated = MENU_NAME_TOKEN_ZH.get(lowered)
        if translated:
            translated_words.append(translated)
            translated_count += 1
            continue
        translated_words.append(word)

    joined = "".join(translated_words).strip()
    if not joined:
        return raw_name

    if translated_count == 0 and not contains_cjk(joined):
        return f"菜单 {joined}"

    if not contains_cjk(joined):
        return f"菜单 {joined}"
    return joined


__all__ = [
    "BUILTIN_MENU_NAME_EXACT_ZH",
    "BUILTIN_MENU_ROUTE_NAME_ZH",
    "MENU_NAME_TOKEN_ZH",
    "contains_cjk",
    "normalize_menu_name_to_cn",
]

