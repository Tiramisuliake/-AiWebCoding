# research-rbac - 调研发现

> 任务：T1 — RBAC DB Schema + API 契约设计
> 状态：complete
> 完成时间：2026-04-12

---

## 一、RBAC 模型选择

[RESEARCH] 采用 **Flat RBAC（扁平型 RBAC）**，理由：
- 首期模块无需角色继承（Hierarchical RBAC）复杂性
- 满足 INV-5：用户权限通过 user_roles → role_permissions 两跳查询
- 扩展路径清晰：后期可加 parent_role_id 支持角色继承，不需要改现有表结构

核心关系：**用户 M:N 角色，角色 M:N 权限**

---

## 二、MySQL 数据库 Schema

[ARCHITECTURE] 5 张表，所有表使用 InnoDB 引擎，字符集 utf8mb4。

### 2.1 完整 DDL

```sql
-- 1. 用户表
CREATE TABLE users (
    id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
    username      VARCHAR(64)  NOT NULL,
    email         VARCHAR(128) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,          -- bcrypt hash (INV-2)
    is_active     TINYINT(1)   NOT NULL DEFAULT 1, -- 1=启用, 0=禁用
    created_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
                                ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email    (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 2. 角色表
CREATE TABLE roles (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name        VARCHAR(64)  NOT NULL,
    description VARCHAR(255)          DEFAULT NULL,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_roles_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- 3. 权限表
CREATE TABLE permissions (
    id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name        VARCHAR(128) NOT NULL,  -- 显示名，如"创建用户"
    code        VARCHAR(128) NOT NULL,  -- 权限标识符，如"user:create"
    description VARCHAR(255)          DEFAULT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_permissions_code (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';

-- 4. 用户-角色关联表
CREATE TABLE user_roles (
    user_id INT UNSIGNED NOT NULL,
    role_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (user_id, role_id),
    KEY idx_user_roles_role_id (role_id),
    CONSTRAINT fk_ur_user FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_ur_role FOREIGN KEY (role_id) REFERENCES roles(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户-角色关联';

-- 5. 角色-权限关联表
CREATE TABLE role_permissions (
    role_id       INT UNSIGNED NOT NULL,
    permission_id INT UNSIGNED NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    KEY idx_rp_permission_id (permission_id),
    CONSTRAINT fk_rp_role FOREIGN KEY (role_id) REFERENCES roles(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_rp_permission FOREIGN KEY (permission_id)
        REFERENCES permissions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色-权限关联';
```

### 2.2 表关系图

```
users           user_roles         roles         role_permissions    permissions
+----------+    +----------+    +----------+    +----------------+   +----------+
| id (PK)  |←──| user_id  |    | id (PK)  |←──| role_id        |   | id (PK)  |
| username |    | role_id  |──→| name     |    | permission_id  |──→| name     |
| email    |    +----------+    | desc...  |    +----------------+   | code     |
| pwd_hash |                    | created  |                         | desc...  |
| is_active|                    +----------+                         +----------+
| created  |
| updated  |
+----------+
```

### 2.3 设计决策说明

| 决策 | 说明 |
|------|------|
| password_hash VARCHAR(255) | bcrypt 输出固定 60 字符，预留扩展 (INV-2) |
| is_active 而非软删除 | 用户禁用比删除更安全，保留历史关联数据 |
| permissions.code 唯一约束 | code 是业务逻辑判断依据（如 "user:create"），必须唯一 |
| 关联表使用 ON DELETE CASCADE | 角色/权限被删时自动清理关联，满足 INV-6 |
| users 无 deleted_at | 首期不实现软删除，简化实现；后期可加列 |
| permissions 无 created_at | 权限是系统内置的，无需记录创建时间 |

### 2.4 预置权限 code 规范

格式：`<资源>:<动作>`

```
user:list       用户列表
user:read       查看用户详情
user:create     创建用户
user:update     更新用户
user:delete     删除用户
user:assign_role  分配角色

role:list
role:read
role:create
role:update
role:delete
role:assign_permission

permission:list
permission:read
```

---

## 三、Flask-RESTX API 端点契约

[ARCHITECTURE] 所有响应遵循 INV-7 统一格式：`{"code": 0, "data": {}, "msg": "ok"}`

### 3.1 Namespace 总览

| Namespace | 前缀 | 说明 |
|-----------|------|------|
| auth_ns | /api/auth | 认证（公开路由） |
| users_ns | /api/users | 用户 CRUD（需 JWT） |
| roles_ns | /api/roles | 角色 CRUD（需 JWT） |
| permissions_ns | /api/permissions | 权限查询（需 JWT） |

### 3.2 Auth Namespace（/api/auth）

已在 api-contracts.md 中定义，见原文。补充说明：
- POST /api/auth/login — 公开，不需 JWT
- POST /api/auth/logout — 需 @jwt_required()，将 jti 加入黑名单
- POST /api/auth/refresh — 需 @jwt_required(refresh=True)

### 3.3 Users Namespace（/api/users）

所有端点需 `@jwt_required()`，权限码见括号。

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | /api/users | user:list | 用户列表（支持分页） |
| POST | /api/users | user:create | 创建用户 |
| GET | /api/users/{id} | user:read | 用户详情 |
| PUT | /api/users/{id} | user:update | 更新用户信息 |
| DELETE | /api/users/{id} | user:delete | 删除用户（级联清理 user_roles） |
| GET | /api/users/{id}/roles | user:read | 获取用户的角色列表 |
| POST | /api/users/{id}/roles | user:assign_role | 为用户分配角色 |
| DELETE | /api/users/{id}/roles/{role_id} | user:assign_role | 移除用户的某角色 |

**GET /api/users — 请求参数**
```
page     int  默认 1
per_page int  默认 20，最大 100
keyword  str  可选，按 username/email 模糊搜索
is_active int 可选，0 或 1 过滤
```

**GET /api/users — 响应**
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
    "total": 100,
    "page": 1,
    "per_page": 20,
    "pages": 5
  },
  "msg": "ok"
}
```

**POST /api/users — 请求体**
```json
{
  "username": "string",    // 必填，唯一
  "email": "string",       // 必填，唯一，合法邮箱格式
  "password": "string",    // 必填，≥8 字符
  "is_active": true,       // 可选，默认 true
  "role_ids": [1, 2]       // 可选，初始分配角色
}
```

**POST /api/users — 响应**
```json
{
  "code": 0,
  "data": {
    "id": 2,
    "username": "newuser",
    "email": "new@example.com",
    "is_active": true,
    "created_at": "2026-04-12T09:00:00",
    "roles": []
  },
  "msg": "ok"
}
```

**PUT /api/users/{id} — 请求体（均可选，PATCH 语义）**
```json
{
  "email": "string",
  "password": "string",    // 修改密码
  "is_active": true
}
```

**GET /api/users/{id}/roles — 响应**
```json
{
  "code": 0,
  "data": {
    "user_id": 1,
    "roles": [
      { "id": 1, "name": "admin", "description": "管理员" }
    ]
  },
  "msg": "ok"
}
```

**POST /api/users/{id}/roles — 请求体**
```json
{ "role_ids": [1, 2] }  // 追加（幂等，已有的跳过）
```

### 3.4 Roles Namespace（/api/roles）

所有端点需 `@jwt_required()`。

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | /api/roles | role:list | 角色列表（支持分页） |
| POST | /api/roles | role:create | 创建角色 |
| GET | /api/roles/{id} | role:read | 角色详情（含权限列表） |
| PUT | /api/roles/{id} | role:update | 更新角色信息 |
| DELETE | /api/roles/{id} | role:delete | 删除角色（级联清理关联） |
| GET | /api/roles/{id}/permissions | role:read | 获取角色的权限列表 |
| POST | /api/roles/{id}/permissions | role:assign_permission | 为角色分配权限（覆盖写） |

**GET /api/roles — 响应**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "admin",
        "description": "系统管理员",
        "created_at": "2026-04-12T09:00:00",
        "permission_count": 14
      }
    ],
    "total": 3,
    "page": 1,
    "per_page": 20,
    "pages": 1
  },
  "msg": "ok"
}
```

**POST /api/roles — 请求体**
```json
{
  "name": "editor",
  "description": "内容编辑员",
  "permission_ids": [1, 2, 3]   // 可选，初始权限
}
```

**POST /api/roles/{id}/permissions — 请求体（覆盖写）**
```json
{ "permission_ids": [1, 2, 3] }   // 完整替换该角色的权限集合
```

**GET /api/roles/{id} — 响应（含权限列表）**
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "name": "admin",
    "description": "系统管理员",
    "created_at": "2026-04-12T09:00:00",
    "permissions": [
      { "id": 1, "name": "创建用户", "code": "user:create" }
    ]
  },
  "msg": "ok"
}
```

### 3.5 Permissions Namespace（/api/permissions）

权限是系统内置数据，首期只支持查询（不支持前端增删改）。

| 方法 | 路径 | 权限码 | 说明 |
|------|------|--------|------|
| GET | /api/permissions | permission:list | 全量权限列表（无分页，通常 < 100 条） |
| GET | /api/permissions/{id} | permission:read | 权限详情 |

**GET /api/permissions — 响应**
```json
{
  "code": 0,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "创建用户",
        "code": "user:create",
        "description": "允许创建新用户账号"
      }
    ],
    "total": 14
  },
  "msg": "ok"
}
```

---

## 四、错误码规范

| code | 场景 |
|------|------|
| 0 | 成功 |
| 1001 | 参数校验失败 |
| 1002 | 资源不存在（404 场景） |
| 1003 | 重复数据（如 username 已存在） |
| 2001 | 未认证（Token 缺失/过期） |
| 2002 | 权限不足 |
| 5001 | 服务器内部错误 |

---

## 五、SQLAlchemy Model 设计提示

给 backend-dev 的实现提示：

1. **User 模型** 需实现 `check_password(plain)` 方法（bcrypt verify），`set_password(plain)` 方法
2. **scoped_session**（SD-2）：在 `extensions.py` 用 `db = SQLAlchemy()` 配合 `session_options={"autoflush": False}` 防止意外 flush
3. **权限检查装饰器**：建议实现 `@require_permission("user:create")` 自定义装饰器，内部调用 `get_jwt_identity()` 查用户权限集合
4. **用户权限查询**（关键查询）：
   ```python
   # 获取用户所有权限 code 集合
   user.roles → role.permissions → permission.code
   # 用 SQLAlchemy relationship + lazy="dynamic" 或二次查询
   ```
5. **关联表无需独立 Model**：`user_roles` 和 `role_permissions` 用 `Table` 对象 + `relationship(secondary=...)` 实现即可

---

## 六、安全考量

对应不变量检查：

| 不变量 | 实现要求 |
|--------|---------|
| INV-1 | users/roles/permissions 所有端点加 @jwt_required() |
| INV-2 | 只存 password_hash，POST/PUT 时用 bcrypt.generate_password_hash() |
| INV-5 | 每个需要鉴权的端点验证当前用户有对应 permission.code |
| INV-6 | 删除 role 时检查 user_roles 中是否还有用户使用（或提示管理员先解除）；ON DELETE CASCADE 处理 DB 层面清理 |

---

## 七、依赖关系

- T2（backend-dev 实现认证模块）依赖此 findings.md 的 DB Schema + API 契约
- 本文档是 T2 的输入
