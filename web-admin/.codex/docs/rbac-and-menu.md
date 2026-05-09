# RBAC 与菜单规则

## 数据模型

当前 RBAC 与导航相关表：

- `users`
- `roles`
- `permissions`
- `menus`
- `user_roles`
- `role_permissions`
- `role_menus`
- `token_blocklist`

`users`、`roles`、`permissions`、`menus` 是 ORM 实体。三个关联表用于表达多对多授权关系。`token_blocklist` 存储已撤销的 token id。

## 权限码

当前内置权限码包括：

- `user:list`、`user:read`、`user:create`、`user:update`、`user:delete`、`user:assign_role`
- `role:list`、`role:read`、`role:create`、`role:update`、`role:delete`、`role:assign_permission`、`role:assign_menu`
- `permission:list`、`permission:read`
- `menu:list`、`menu:read`、`menu:create`、`menu:update`、`menu:delete`

新增业务模块时，沿用 `module:action` 命名方式，例如 `order:list`、`order:read`、`order:create`、`order:update`、`order:delete`。

## 授权语义

- 受保护路由必须有 JWT。
- 需要权限的路由必须使用 `@require_permission("module:action")`。
- 拥有 `admin` 角色的用户由 authz service 放行。
- 非 admin 用户通过角色获得权限。
- 角色权限分配会应用有效 id，并返回无效 id 与 warnings。

## 菜单语义

- 菜单通过 `parent_id` 形成层级。
- `route_path` 连接后端菜单记录和前端路由。
- `permission_code` 连接菜单与访问该页面或功能所需的权限。
- `/api/menus/my-tree` 会过滤隐藏或禁用菜单。
- admin 用户获取全部可见且启用的菜单。
- 非 admin 用户获取其角色授权的菜单。
- 菜单树构建必须安全处理循环数据。

## 角色菜单与权限联动分配

`POST /api/roles/{role_id}/menus` 支持在同一次请求中更新菜单，并可选更新权限。

规则：

- `menu_ids` 必填。
- `permission_ids` 可选。
- 传入 `permission_ids` 时，除 `role:assign_menu` 外还需要 `role:assign_permission`。
- 传入的权限必须属于所选菜单可管辖范围。
- 权限范围校验失败时，不写入菜单和权限。

## 中文优先本地化

权限和菜单在管理后台中中文优先展示：

- 权限列表展示中文名，并用独立列展示权限码。
- 分配弹窗推荐展示 `中文权限名（permission:code）`。
- 菜单名称默认使用中文。
- 权限码保持为稳定的技术标识。

新增内置权限码时，需要更新：

- `backend/app/const/permissions.py`
- `frontend/src/i18n/messages.js`
- 必要时更新 seed 或启动同步逻辑。
- API 行为变化时，同步更新本文档和 `.codex/docs/api-contracts.md`。

新增内置菜单或菜单命名规则时，需要更新：

- `backend/app/components/menu_localization.py`
- seed/菜单初始化脚本。
- 前端路由 metadata 和 i18n 文案。
- 如果模块模式变化，同步更新 `.codex/docs/business-module-guide.md`。
