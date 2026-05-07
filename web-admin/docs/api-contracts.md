# API Contracts

## Common Rules

- Base prefix: `/api`
- Swagger UI: `/api/docs`
- Health check: `/health`
- Protected endpoints use JWT access tokens unless noted.
- Refresh uses a JWT refresh token.

Success response:

```json
{ "code": 0, "data": {}, "msg": "ok" }
```

Common error codes:

| Code | Meaning |
|---|---|
| `1001` | Parameter validation failed |
| `1002` | Resource not found |
| `1003` | Unique/conflict error |
| `2001` | Authentication failed |
| `2002` | Permission denied |
| `5001` | Internal server error |

## Auth

### `POST /api/auth/login`

Request:

```json
{ "username": "admin", "password": "password123" }
```

Response data:

```json
{
  "access_token": "string",
  "refresh_token": "string",
  "user": { "id": 1, "username": "admin", "roles": ["admin"] }
}
```

### `POST /api/auth/logout`

Requires access token.

Request:

```json
{ "refresh_token": "string" }
```

Behavior: revokes current access token and matching refresh token.

### `POST /api/auth/refresh`

Requires refresh token in `Authorization: Bearer <refresh_token>`.

Response data:

```json
{ "access_token": "string" }
```

## Users

All user endpoints require JWT and the matching `user:*` permission.

### `GET /api/users`

Permission: `user:list`

Query:

| Name | Type | Notes |
|---|---|---|
| `page` | int | default `1`, min `1` |
| `per_page` | int | default `20`, max `100` |
| `keyword` | string | fuzzy username/email search |
| `username` | string | comma-separated terms, max 5 |
| `email` | string | comma-separated terms, max 5 |
| `role` | string | comma-separated terms, max 5 |
| `is_active` | bool | optional |

Response data:

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

Permission: `user:create`

Request:

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

Permission: `user:read`

Returns a single user detail.

### `PUT /api/users/{user_id}`

Permission: `user:update`

Request fields are partial. Supported fields include `email`, `password`, `is_active`, and role-related fields handled by service validation.

### `DELETE /api/users/{user_id}`

Permission: `user:delete`

Deletes a user and returns `data: null`.

### `GET /api/users/{user_id}/roles`

Permission: `user:read`

Returns assigned roles.

### `POST /api/users/{user_id}/roles`

Permission: `user:assign_role`

Request:

```json
{ "role_ids": [1, 2] }
```

Behavior: applies valid role ids and reports invalid ids/warnings.

### `DELETE /api/users/{user_id}/roles/{role_id}`

Permission: `user:assign_role`

Removes one role from the user.

## Roles

All role endpoints require JWT and the matching `role:*` permission.

### `GET /api/roles`

Permission: `role:list`

Query:

| Name | Type | Notes |
|---|---|---|
| `page` | int | default `1`, min `1` |
| `per_page` | int | default `20`, max `100` |
| `name` | string | comma-separated terms, max 5 |

### `POST /api/roles`

Permission: `role:create`

Request:

```json
{
  "name": "editor",
  "description": "Editor role",
  "permission_ids": [1, 2]
}
```

### `GET /api/roles/{role_id}`

Permission: `role:read`

Returns role detail.

### `PUT /api/roles/{role_id}`

Permission: `role:update`

Request fields are partial; commonly `name` and `description`.

### `DELETE /api/roles/{role_id}`

Permission: `role:delete`

Deletes a role when service rules allow it.

### `GET /api/roles/{role_id}/permissions`

Permission: `role:read`

Returns role permissions.

### `POST /api/roles/{role_id}/permissions`

Permission: `role:assign_permission`

Request:

```json
{ "permission_ids": [1, 2, 3] }
```

Behavior: applies valid permission ids and reports invalid ids/warnings.

### `GET /api/roles/{role_id}/menus`

Permission: `role:read`

Returns role menus.

### `POST /api/roles/{role_id}/menus`

Permission: `role:assign_menu`

Request:

```json
{ "menu_ids": [1, 2, 3] }
```

Or:

```json
{ "menu_ids": [1, 2, 3], "permission_ids": [11, 12] }
```

Behavior:

- `menu_ids` only: update role menu assignment.
- With `permission_ids`: requires both `role:assign_menu` and `role:assign_permission`.
- With `permission_ids`: submitted permissions must be within the selected menu permission scope.
- Out-of-scope permissions return `400` with code `1001` and do not write menus or permissions.

## Permissions

All permission endpoints require JWT and matching `permission:*` permission.

### `GET /api/permissions`

Permission: `permission:list`

Query:

| Name | Type | Notes |
|---|---|---|
| `page` | int | optional; if omitted, returns all |
| `per_page` | int | optional, max `100` |
| `name` | string | comma-separated terms, max 5 |
| `code` | string | comma-separated terms, max 5 |
| `description` | string | comma-separated terms, max 5 |

### `GET /api/permissions/{permission_id}`

Permission: `permission:read`

Returns permission detail.

## Menus

All menu management endpoints require JWT and matching `menu:*` permission. `/api/menus/my-tree` requires only JWT.

### `GET /api/menus`

Permission: `menu:list`

Query:

| Name | Type | Notes |
|---|---|---|
| `include_hidden` | bool | default `true` |
| `include_disabled` | bool | default `true` |
| `name` | string | comma-separated terms, max 5 |

Response data:

```json
{ "items": [{ "id": 1, "name": "仪表盘", "children": [] }] }
```

### `POST /api/menus`

Permission: `menu:create`

Request:

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

Requires JWT.

Behavior:

- Admin users receive all visible and enabled menus.
- Other users receive visible and enabled menus assigned through their roles.

### `GET /api/menus/{menu_id}`

Permission: `menu:read`

Returns menu detail.

### `PUT /api/menus/{menu_id}`

Permission: `menu:update`

Partial update. Parent changes must not create cycles.

### `DELETE /api/menus/{menu_id}`

Permission: `menu:delete`

Deletes a menu when service rules allow it.
