# 前端 Agent 指南

## 范围

本目录包含 Vue 3 SPA、Element Plus UI、Pinia stores、路由守卫、API 客户端、i18n 文案和设计令牌。

先读 `../AGENTS.md` 和 `../.codex/docs/project-state.md`，再读本文件。

## 架构规则

- 新增或重写页面优先使用 Vue 3 `script setup` 和 Composition API。
- 后端请求统一通过 `src/api/http.js`、`src/api/auth.js`、`src/api/rbac.js`。
- 认证状态放在 `src/stores/auth.js`。
- 菜单访问状态放在 `src/stores/menu.js`。
- 标签页状态放在 `src/stores/tabs.js`。
- 语言状态放在 `src/stores/locale.js`，文案放在 `src/i18n/messages.js`。
- 认证后的布局壳层行为放在 `src/components/AppLayout.vue`。

## 路由与访问控制

- 新增认证页面必须作为 `AppLayout` 的子路由。
- 需要进入标签页体系的页面必须配置 `tab`、`keepAlive`、`titleKey`。
- 路由守卫会加载 `/api/menus/my-tree`，并阻止访问不在 `allowedPaths` 中的路径。
- 新增由菜单驱动的页面时，必须有匹配的后端菜单记录和权限映射。

## UI 与文案

- 保持现有 Element Plus 管理后台风格。
- 主题值使用 `src/assets/design-tokens.css`；不要绕过 token 直接硬编码新主题色，除非明确新增 token。
- 所有用户可见文案都必须同时加入 `zh-CN` 和 `en-US`。
- 权限和菜单管理页面采用中文优先展示，权限码保留为技术标识。
- 新增管理页面优先沿用 Users、Roles、Permissions、Menus 的表格/搜索/弹窗模式。

## 新增前端功能

新增业务模块时：

- 增加 API client 函数。
- 增加路由和页面视图。
- 在文档中说明菜单和权限 seed 预期。
- 为所有用户可见文案增加 i18n key。
- 需要进入标签页的页面增加 tab metadata。
- 明确 loading、empty、validation、success、failure 状态。
- 前端 payload 或 query 参数变化时，更新 `.codex/docs/api-contracts.md`。

## 检查

在 `web-admin/` 目录运行：

```powershell
npm --prefix frontend run build
python scripts/run_ci.py --quick
```

涉及视觉或路由变化时，使用 Vite dev server 做手工验证。
