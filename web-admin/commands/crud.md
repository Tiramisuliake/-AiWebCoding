# /crud

## 用途

按统一模式新增业务 CRUD 模块，覆盖后端、前端、RBAC、菜单、测试和文档。

## 先读

1. `docs/business-module-guide.md`
2. `templates/业务模块模板.md`
3. `docs/api-contracts.md`
4. `docs/rbac-and-menu.md`
5. `backend/AGENTS.md`
6. `frontend/AGENTS.md`

## 步骤

1. 定义模块名、实体字段、列表筛选和校验规则。
2. 定义权限码和菜单路由。
3. 新增后端实体、repository、service、namespace/routes、seed/菜单更新和测试。
4. 新增前端 API client、路由、页面、i18n 文案和标签页 metadata。
5. 更新 `docs/api-contracts.md`、`docs/rbac-and-menu.md` 和模块文档。
6. 运行后端测试、前端构建和 CI。

## 输出

返回：

- 模块名称和路由。
- 新增 API 端点。
- 新增权限码。
- 新增菜单入口。
- 已运行检查和结果。
- 人工验收记录。
