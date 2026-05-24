# /crud

## 用途

按统一模式新增业务 CRUD 模块，覆盖后端、前端、RBAC、菜单、测试和文档。

## 先读

1. `.codex/docs/business-module-guide.md`
2. `.claude/templates/业务模块模板.md`
3. `.codex/docs/api-contracts.md`
4. `.codex/docs/rbac-and-menu.md`
5. `.claude/backend.md`
6. `.claude/frontend.md`

## 步骤

1. 定义模块名、实体字段、列表筛选和校验规则。
2. 定义权限码（`module:list/read/create/update/delete`）和菜单路由。
3. 后端实现：
   - `entity/models.py` 新增 ORM 模型
   - `repository/` 查询辅助函数
   - `service/` 业务逻辑（含校验 + 事务）
   - `apis/` namespace + routes + `@require_permission`
   - `const/permissions.py` 权限码 + 本地化映射
   - `scripts/seed.py` 菜单入口
   - pytest 覆盖（未授权 / 缺权限 / 正常路径 / 校验失败 / 删除约束）
4. 前端实现：
   - `src/api/rbac.js` API 函数
   - `router/index.js` 路由注册（含 meta）
   - `src/views/` 页面（表格+搜索+弹窗模式）
   - `i18n/messages.js` zh-CN + en-US 文案
5. 更新 `.codex/docs/api-contracts.md`、`.codex/docs/rbac-and-menu.md` 和模块文档。
6. 运行后端测试、前端构建和 CI（见 `.claude/commands/check.md`）。

## 输出

返回：

- 模块名称和路由。
- 新增 API 端点。
- 新增权限码。
- 新增菜单入口。
- 已运行检查和结果。
- 人工验收记录。
