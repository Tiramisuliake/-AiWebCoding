# 系统不变量与文档同步

## 系统不变量

**安全**
- 密码必须 bcrypt 哈希，不能明文存储。
- JWT 密钥和 DB 凭证来自环境变量/配置文件，不能硬编码。
- 已撤销 token 必须被拒绝（每次请求查 `TokenBlocklist`）。

**API 契约**
- 响应必须用 `ok()`/`fail()` 包装，格式 `{code, data, msg}`。
- 业务错误使用对应错误码，不能用 HTTP 状态码替代。

**数据持久化**
- 只用 SQLAlchemy ORM，不拼 SQL 字符串。
- scoped session 由 teardown 清理，不手动 close。
- 菜单树构建必须处理循环 `parent_id`（防死循环）。
- 删除前必须经过 service 层关联约束检查（有子菜单不能删父菜单）。

**前端访问控制**
- 认证路由必须受登录状态保护，不能绕过守卫。
- 菜单驱动路由必须受 `menuStore.hasPath()` 约束。
- Tab 恢复时必须过滤已无权限的路由。

## 文档同步触发规则

- API 变化 → 更新 `.codex/docs/api-contracts.md`
- 权限/菜单变化 → 更新 `.codex/docs/rbac-and-menu.md`
- 功能完成 → 更新 `.codex/docs/project-state.md` + `.codex/docs/todos.md`
- 架构变化 → 更新 `.codex/docs/architecture.md`
- 用户可见流程验收 → 写入 `.codex/docs/acceptance/`
