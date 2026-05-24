# 后端架构与规则

## 分层职责

```
路由层 (apis/)       HTTP 输入解析 → 调 service → ok()/fail() 响应
Service 层           校验、业务规则、事务边界、ServiceError 抛出
Repository 层        SQLAlchemy 查询封装，返回 ORM 对象
Entity 层 (models.py) ORM 模型定义，不含业务逻辑
```

路由层不写复杂 DB 逻辑。Service 层是主战场。

## 统一响应格式

```python
from app.components.response import ok, fail

return ok(data)          # {"code": 0, "data": ..., "msg": "ok"}

# service 中抛出，路由层统一捕获
raise ServiceError(code=1002, msg="用户不存在", http_status=404)
# → {"code": 1002, "data": null, "msg": "用户不存在"}
```

业务错误码：

| 码 | 含义 |
|---|---|
| `1001` | 参数校验失败 |
| `1002` | 资源不存在 |
| `1003` | 唯一键冲突 |
| `2001` | 认证失败 |
| `2002` | 权限不足 |
| `5001` | 服务端内部错误 |

## 认证与权限装饰器

```python
@jwt_required()                      # 只验 JWT 有效性
@require_permission("user:create")   # JWT + RBAC 双重检查
def create_user():
    ...
```

- `admin` 角色由 `authz_service` 自动放行，路由层不重复判断。
- 两个装饰器必须同时存在（`jwt_required` 在外层）。

## JWT 机制

- access token：30 分钟，`Authorization: Bearer` 头传递。
- refresh token：7 天，logout 时与 access token 一起写入 `TokenBlocklist`。
- 每次请求查 blocklist，已撤销一律拒绝。

## Session 规则

- 只用 `get_session()` 取 scoped session（`app/database/conn/session.py`）。
- 不手动 `session.close()`，app teardown 统一清理。
- 只用 ORM，禁止拼 SQL 字符串。

## App 初始化

Flask 应用只通过 `app.create_app()` 工厂创建。配置在 `app/conf/config.py`，扩展（jwt/bcrypt/celery）在 `app/conf/extensions.py`。

## 新增后端功能步骤

1. `entity/models.py` — 定义 ORM 模型和关联表。
2. `repository/` — 添加 `get_*_by_id`、`build_*_select` 等查询辅助函数。
3. `service/` — 实现业务逻辑（校验 + 事务边界）。
4. `apis/` — 建 Flask-RESTX namespace + routes，绑 `@require_permission`。
5. `const/permissions.py` — 增加权限码常量。
6. `service/rbac_seed_service.py` — 补充权限中文本地化映射。
7. `scripts/seed.py` — 增加菜单入口。
8. `tests/` — 补 pytest：未带 token、缺权限、正常路径、校验失败、删除约束。
9. 同步 `.codex/docs/api-contracts.md` 和 `.codex/docs/rbac-and-menu.md`。
