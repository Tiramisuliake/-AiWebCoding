# 数据模型与 API 速查

## 数据模型

| 表 | 关键字段 | 关系 |
|---|---|---|
| `users` | id, username(unique), email(unique), password_hash, is_active, created_at | M2M Role |
| `roles` | id, name(unique), description | M2M User / Permission / Menu |
| `permissions` | id, name, code(unique), description | M2M Role |
| `menus` | id, name, parent_id(自引用), route_path, icon, sort, is_visible, is_enabled, permission_code | M2M Role |
| `token_blocklist` | id, jti(unique), created_at | — |

关联表（M2M）：`user_roles`、`role_permissions`、`role_menus`，均有 CASCADE DELETE。

**权限码格式**：`module:action`，例如 `user:create`、`role:assign_permission`、`order:list`。

**菜单 `permission_code`**：连接菜单与权限。前端路由守卫用它过滤可访问路径；角色联动分配时用它校验权限是否在菜单管辖范围内。

## API 端点速查

基础前缀 `/api` · Swagger UI `/api/docs` · 健康检查 `/health`

| 路径 | 方法 | 权限 |
|---|---|---|
| /auth/login | POST | 无需 |
| /auth/logout | POST | jwt |
| /auth/refresh | POST | jwt(refresh) |
| /users | GET | user:list |
| /users | POST | user:create |
| /users/{id} | GET / PUT / DELETE | user:read / update / delete |
| /users/{id}/roles | GET | user:read |
| /users/{id}/roles | POST | user:assign_role |
| /users/{id}/roles/{rid} | DELETE | user:assign_role |
| /roles | GET | role:list |
| /roles | POST | role:create |
| /roles/{id} | GET / PUT / DELETE | role:read / update / delete |
| /roles/{id}/permissions | GET | role:read |
| /roles/{id}/permissions | POST | role:assign_permission |
| /roles/{id}/menus | GET | role:read |
| /roles/{id}/menus | POST | role:assign_menu |
| /permissions | GET | permission:list |
| /permissions/{id} | GET | permission:read |
| /menus | GET | menu:list |
| /menus | POST | menu:create |
| /menus/{id} | GET / PUT / DELETE | menu:read / update / delete |
| /menus/my-tree | GET | jwt 即可 |

## 内置权限码（23 个）

```
user:list  user:read  user:create  user:update  user:delete  user:assign_role
role:list  role:read  role:create  role:update  role:delete
role:assign_permission  role:assign_menu
permission:list  permission:read
menu:list  menu:read  menu:create  menu:update  menu:delete
```
