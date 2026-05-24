# 前端架构与规则

## Vue 3 规范

- 只用 `<script setup>` + Composition API，禁用 Options API。
- 后端请求只通过 `src/api/http.js`、`auth.js`、`rbac.js` 发起，不直接调 axios。
- 跨页面共享状态才新增 Pinia store；页面内部状态用 `ref`/`reactive`。

## Pinia Stores 职责边界

| Store | 职责 | localStorage 键 |
|---|---|---|
| `auth.js` | tokens、user 摘要、login/logout | `web_admin_access_token` 等 |
| `menu.js` | 用户菜单树、allowedPaths（Set） | — |
| `tabs.js` | 标签页状态、拖排序、权限清洗 | `web_admin_tabs_state_v1` |
| `locale.js` | 当前语言（固定 zh-CN） | `web_admin_locale` |

## 路由守卫（RBAC）

`router/index.js` 的 `beforeEach` 三步：

1. 未登录访问受保护路由 → 跳 `/login`。
2. 已登录访问 `/login` → 跳 dashboard。
3. 首次认证路由访问 → 加载 `/api/menus/my-tree`，之后每次校验 `menuStore.hasPath(to.path)`，不在 `allowedPaths` 内则跳第一个可访问路径。

**不要在页面层重复实现访问控制**，守卫已统一处理。

## Tab 系统

- dashboard tab 固定在最左侧，不可关闭、不参与拖拽。
- 新增需进入标签体系的页面，路由 meta 必须包含：

```js
meta: { requiresAuth: true, tab: true, keepAlive: true, titleKey: 'xxx.title' }
```

- Tab 状态持久化到 localStorage，刷新恢复时过滤已无权限的标签。

## i18n

- `useI18n` composable（`src/composables/useI18n.js`）提供 `t('feature.key')` 函数。
- 所有用户可见文案必须同时写 `zh-CN` 和 `en-US`（`src/i18n/messages.js`）。
- 权限码展示键格式：`permissions.codeNames.{module_action}`（下划线替换冒号）。
- 不要绕过 `design-tokens.css` 直接硬编码新主题色。

## API Client 层

```
src/api/http.js   axios 实例：注入 Bearer token，401 时清 session 跳登录
src/api/auth.js   login / logout / refresh
src/api/rbac.js   users / roles / permissions / menus 全部 CRUD
```

## 新增前端功能步骤

1. `src/api/rbac.js` — 增加 API 函数（对应后端新端点）。
2. `src/router/index.js` — 注册子路由（AppLayout 子路由），配置 meta。
3. `src/views/` — 新建页面，沿用 Users/Roles 的表格-搜索-弹窗模式。
4. `src/i18n/messages.js` — 补充 zh-CN + en-US 文案。
5. 页面明确处理 loading、empty、validation、success、failure 五种状态。
6. 同步 `.codex/docs/api-contracts.md`。
