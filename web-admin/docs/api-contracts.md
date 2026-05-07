# API 契约

## 通用规则

- 基础前缀：`/api`
- Swagger UI：`/api/docs`
- 健康检查：`/health`
- 除特别说明外，受保护接口使用 access token。
- 刷新接口使用 refresh token。

成功响应：

```json
{ "code": 0, "data": {}, "msg": "ok" }
```

常用错误码：

| 错误码 | 含义 |
|---|---|
| `1001` | 参数校验失败 |
| `1002` | 资源不存在 |
| `1003` | 唯一键或数据冲突 |
| `2001` | 认证失败 |
| `2002` | 权限不足 |
| `5001` | 服务端内部错误 |

## 认证 Auth

### `POST /api/auth/login`

请求：

```json
{ "username": "admin", "password": "password123" }
```

响应 `data`：

```json
{
  "access_token": "string",
  "refresh_token": "string",
  "user": { "id": 1, "username": "admin", "roles": ["admin"] }
}
```

### `POST /api/auth/logout`

需要 access token。

请求：

```json
{ "refresh_token": "string" }
```

行为：撤销当前 access token 和匹配的 refresh token。

### `POST /api/auth/refresh`

需要在 `Authorization: Bearer <refresh_token>` 中传 refresh token。

响应 `data`：

```json
{ "access_token": "string" }
```

## 用户 Users

所有用户接口都需要 JWT 和对应 `user:*` 权限。

### `GET /api/users`

权限：`user:list`

查询参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| `page` | int | 默认 `1`，最小 `1` |
| `per_page` | int | 默认 `20`，最大 `100` |
| `keyword` | string | 用户名/邮箱模糊搜索 |
| `username` | string | 逗号分隔搜索词，最多 5 个 |
| `email` | string | 逗号分隔搜索词，最多 5 个 |
| `role` | string | 逗号分隔搜索词，最多 5 个 |
| `is_active` | bool | 可选 |

响应 `data`：

```json
{
  "items": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "is_active": true,
      "created_at": "2026-05-07T00:00:00",
      "updated_at": "2026-05-07T00:00:00",
      "roles": ["admin"]
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

### `POST /api/users`

权限：`user:create`

请求：

```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "is_active": true,
  "role_ids": [1, 2]
}
```

### `GET /api/users/{user_id}`

权限：`user:read`

返回单个用户详情。

### `PUT /api/users/{user_id}`

权限：`user:update`

支持部分字段更新，常见字段包括 `email`、`password`、`is_active`。

### `DELETE /api/users/{user_id}`

权限：`user:delete`

删除用户，成功时返回 `data: null`。

### `GET /api/users/{user_id}/roles`

权限：`user:read`

返回用户已分配角色。

### `POST /api/users/{user_id}/roles`

权限：`user:assign_role`

请求：

```json
{ "role_ids": [1, 2] }
```

行为：应用有效角色 id，并返回无效 id 与 warnings。

### `DELETE /api/users/{user_id}/roles/{role_id}`

权限：`user:assign_role`

移除用户的单个角色。

## 角色 Roles

所有角色接口都需要 JWT 和对应 `role:*` 权限。

### `GET /api/roles`

权限：`role:list`

查询参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| `page` | int | 默认 `1`，最小 `1` |
| `per_page` | int | 默认 `20`，最大 `100` |
| `name` | string | 逗号分隔搜索词，最多 5 个 |

### `POST /api/roles`

权限：`role:create`

请求：

```json
{
  "name": "editor",
  "description": "Editor role",
  "permission_ids": [1, 2]
}
```

### `GET /api/roles/{role_id}`

权限：`role:read`

返回角色详情。

### `PUT /api/roles/{role_id}`

权限：`role:update`

支持部分字段更新，常见字段为 `name` 和 `description`。

### `DELETE /api/roles/{role_id}`

权限：`role:delete`

按 service 规则删除角色。

### `GET /api/roles/{role_id}/permissions`

权限：`role:read`

返回角色权限。

### `POST /api/roles/{role_id}/permissions`

权限：`role:assign_permission`

请求：

```json
{ "permission_ids": [1, 2, 3] }
```

行为：应用有效权限 id，并返回无效 id 与 warnings。

### `GET /api/roles/{role_id}/menus`

权限：`role:read`

返回角色菜单。

### `POST /api/roles/{role_id}/menus`

权限：`role:assign_menu`

请求：

```json
{ "menu_ids": [1, 2, 3] }
```

或：

```json
{ "menu_ids": [1, 2, 3], "permission_ids": [11, 12] }
```

行为：

- 只传 `menu_ids`：更新角色菜单分配。
- 同时传 `permission_ids`：除 `role:assign_menu` 外，还需要 `role:assign_permission`。
- 同时传 `permission_ids`：权限必须在所选菜单可管辖范围内。
- 权限越界时返回 `400` 和 code `1001`，并且不写入菜单或权限。

## 权限 Permissions

所有权限接口都需要 JWT 和对应 `permission:*` 权限。

### `GET /api/permissions`

权限：`permission:list`

查询参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| `page` | int | 可选；不传则返回全部 |
| `per_page` | int | 可选，最大 `100` |
| `name` | string | 逗号分隔搜索词，最多 5 个 |
| `code` | string | 逗号分隔搜索词，最多 5 个 |
| `description` | string | 逗号分隔搜索词，最多 5 个 |

### `GET /api/permissions/{permission_id}`

权限：`permission:read`

返回权限详情。

## 菜单 Menus

菜单管理接口需要 JWT 和对应 `menu:*` 权限。`/api/menus/my-tree` 只需要 JWT。

### `GET /api/menus`

权限：`menu:list`

查询参数：

| 参数 | 类型 | 说明 |
|---|---|---|
| `include_hidden` | bool | 默认 `true` |
| `include_disabled` | bool | 默认 `true` |
| `name` | string | 逗号分隔搜索词，最多 5 个 |

响应 `data`：

```json
{ "items": [{ "id": 1, "name": "仪表盘", "children": [] }] }
```

### `POST /api/menus`

权限：`menu:create`

请求：

```json
{
  "name": "订单管理",
  "parent_id": null,
  "route_path": "/orders",
  "icon": "List",
  "sort": 10,
  "is_visible": true,
  "is_enabled": true,
  "permission_code": "order:list"
}
```

### `GET /api/menus/my-tree`

需要 JWT。

行为：

- admin 用户返回全部可见且启用的菜单。
- 非 admin 用户返回其角色授权下可见且启用的菜单。

### `GET /api/menus/{menu_id}`

权限：`menu:read`

返回菜单详情。

### `PUT /api/menus/{menu_id}`

权限：`menu:update`

支持部分字段更新。父级变更不能产生循环。

### `DELETE /api/menus/{menu_id}`

权限：`menu:delete`

按 service 规则删除菜单。
