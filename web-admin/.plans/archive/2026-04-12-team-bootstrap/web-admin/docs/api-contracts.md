# web-admin - API 契约

> 前后端接口定义。字段名和类型的真理源头。
> 维护者：devs（添加/变更端点时**必须**更新）
> 状态：已按当前脚手架实现同步

## 统一响应格式

所有接口返回统一格式：

```json
{
  "code": 0,
  "data": {},
  "msg": "ok"
}
```

HTTP 状态码：
- 200: 成功
- 201: 创建成功
- 400: 请求参数错误
- 401: 未认证（Token 缺失或过期）
- 403: 无权限
- 404: 资源不存在
- 409: 数据冲突（唯一键冲突）
- 500: 服务器内部错误

错误码约定：
- `0`: 成功
- `1001`: 参数校验失败
- `1002`: 资源不存在
- `1003`: 唯一键冲突（重复数据）
- `2001`: 认证失败
- `2002`: 权限不足
- `5001`: 服务器内部错误

## Auth API（认证）

### POST /api/auth/login
Request:
```json
{ "username": "string", "password": "string" }
```
Response:
```json
{
  "code": 0,
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "user": { "id": 1, "username": "admin", "roles": ["admin"] }
  },
  "msg": "ok"
}
```

### POST /api/auth/logout
需 JWT。将当前 token 加入 blocklist。

Response:
```json
{ "code": 0, "data": null, "msg": "ok" }
```

### POST /api/auth/refresh
需 Refresh Token（Authorization 头传 refresh token）。

Response:
```json
{ "code": 0, "data": { "access_token": "string" }, "msg": "ok" }
```

## Users API（用户管理）

所有端点需 `@jwt_required()`，并进行 `user:*` 权限检查。

### GET /api/users
Query:
- `page` 默认 1
- `per_page` 默认 20，最大 100
- `keyword` 可选，按用户名/邮箱模糊搜索
- `is_active` 可选（`0` 或 `1`）

Response:
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "is_active": true,
        "created_at": "2026-04-12T09:00:00",
        "roles": ["admin"]
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 20,
    "pages": 1
  },
  "msg": "ok"
}
```

### POST /api/users
Request:
```json
{
  "username": "string",
  "email": "string",
  "password": "string(>=8)",
  "is_active": true,
  "role_ids": [1, 2]
}
```
Response: `201` + 统一格式。

### GET /api/users/{id}
返回单个用户详情。

### PUT /api/users/{id}
Request（可选字段）:
```json
{
  "email": "string",
  "password": "string(>=8)",
  "is_active": true
}
```

### DELETE /api/users/{id}
删除用户。

### GET /api/users/{id}/roles
返回用户角色明细。

### POST /api/users/{id}/roles
Request:
```json
{ "role_ids": [1, 2] }
```
行为：追加分配（幂等）。

### DELETE /api/users/{id}/roles/{role_id}
移除用户单个角色。

## Roles API（角色管理）

所有端点需 `@jwt_required()`，并进行 `role:*` 权限检查。

### GET /api/roles
Query:
- `page` 默认 1
- `per_page` 默认 20，最大 100

Response:
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "admin",
        "description": "System administrator",
        "created_at": "2026-04-12T09:00:00",
        "permission_count": 14
      }
    ],
    "total": 1,
    "page": 1,
    "per_page": 20,
    "pages": 1
  },
  "msg": "ok"
}
```

### POST /api/roles
Request:
```json
{
  "name": "editor",
  "description": "Editor role",
  "permission_ids": [1, 2, 3]
}
```
Response: `201` + 统一格式。

### GET /api/roles/{id}
返回角色详情（含权限列表）。

### PUT /api/roles/{id}
Request:
```json
{
  "name": "editor",
  "description": "Updated description"
}
```

### DELETE /api/roles/{id}
若角色仍绑定用户，返回 `1001`（不允许删除）。

### GET /api/roles/{id}/permissions
返回角色权限明细。

### POST /api/roles/{id}/permissions
Request:
```json
{ "permission_ids": [1, 2, 3] }
```
行为：覆盖写（完整替换该角色权限集合）。

### GET /api/roles/{id}/menus
返回角色菜单明细。

### POST /api/roles/{id}/menus
Request（兼容两种模式）:
```json
{ "menu_ids": [1, 2, 3] }
```
或
```json
{ "menu_ids": [1, 2, 3], "permission_ids": [11, 12] }
```

行为：
- 仅 `menu_ids`：保持原有菜单覆盖写；
- 携带 `permission_ids`：同请求内同时覆盖写角色菜单与角色权限（单事务）；
- 携带 `permission_ids` 时，需同时具备 `role:assign_menu` 与 `role:assign_permission`；
- 若 `permission_ids` 超出本次 `menu_ids` 可管辖权限范围，返回 `400 + code=1001` 且不落库。

## Permissions API（权限管理）

所有端点需 `@jwt_required()`，并进行 `permission:*` 权限检查。

### GET /api/permissions
返回全量权限列表（无分页）。

### GET /api/permissions/{id}
返回单个权限详情。
