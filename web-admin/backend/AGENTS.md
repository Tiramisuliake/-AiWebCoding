# 后端 Agent 指南

## 范围

本目录包含 Flask-RESTX API、SQLAlchemy 模型与仓储、服务层、Celery 接入、脚本和 pytest 测试。

先读 `../AGENTS.md` 和 `../.codex/docs/project-state.md`，再读本文件。

## 架构规则

- Flask 应用只能通过 `app.create_app()` 创建。
- 请求处理放在 `app/apis/*/routes.py`。
- 业务逻辑放在 `app/service/`。
- 数据访问辅助逻辑放在 `app/database/repository/`。
- ORM 模型与关联表放在 `app/database/entity/`。
- 通用响应、权限、分页、序列化、本地化辅助逻辑放在 `app/components/`。
- 配置放在 `app/conf/config.py`，扩展初始化放在 `app/conf/extensions.py`。

不要在路由处理函数中直接写复杂数据库逻辑。

## API 与响应规则

- 业务 API 路由统一位于 `/api` 下。
- API 文档入口为 `/api/docs`。
- 使用 `app/components/response.py` 中的 `ok()` 和 `fail()`。
- 保持响应格式一致：

```json
{ "code": 0, "data": {}, "msg": "ok" }
```

- 预期内业务异常使用 `ServiceError`，由路由层转换为响应。
- 参数校验失败使用 `1001`，资源不存在使用 `1002`，冲突使用 `1003`，认证失败使用 `2001`，权限不足使用 `2002`，服务端错误使用 `5001`。

## 认证、RBAC 与 Session

- 受保护接口必须使用 `@jwt_required()`。
- 需要权限控制的接口还必须使用 `@require_permission("module:action")`。
- `admin` 角色放行逻辑在 authz service 中实现，不要在路由层重复实现。
- 数据库操作只使用 SQLAlchemy ORM，不拼接 SQL 字符串。
- 使用 `app/database/conn/` 中配置好的 scoped session。
- 请求结束依赖 app teardown 清理 session。

## 新增后端功能

新增业务模块时：

- 定义或更新 ORM 实体和 repository 辅助函数。
- 增加 service 函数，放入校验、事务边界和业务规则。
- 增加 Flask-RESTX namespace/routes。
- 增加权限码和中文本地化映射。
- 模块需要导航时，同步 seed/菜单初始化。
- 更新 `.codex/docs/api-contracts.md` 和 `.codex/docs/rbac-and-menu.md`。
- 增加 pytest 覆盖认证、权限、正常路径、校验失败和删除规则。

## 检查

后端测试在 `web-admin/backend/` 目录运行：

```powershell
python -m pytest tests -v
```

项目 CI 在 `web-admin/` 目录运行：

```powershell
python scripts/run_ci.py
```

开发时可以先跑更窄的 pytest 目标，交付前再跑完整后端测试。
