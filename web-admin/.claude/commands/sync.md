# /sync

## 用途

按照当前代码行为同步项目文档。

## 先读

1. `.claude/docs/index.md`
2. `.codex/docs/project-state.md`
3. `.codex/docs/api-contracts.md`
4. `.codex/docs/architecture.md`
5. `.codex/docs/rbac-and-menu.md`

## 步骤

1. 检查变更过的后端 routes、services、models，以及前端 routes、stores 和 API clients。
2. 端点、payload、筛选条件或响应数据变化时，更新 `.codex/docs/api-contracts.md`。
3. 结构或数据流变化时，更新 `.codex/docs/architecture.md`。
4. 权限码、菜单规则或本地化变化时，更新 `.codex/docs/rbac-and-menu.md`。
5. 功能完成时，更新 `.codex/docs/project-state.md` 和 `.codex/docs/todos.md`。
6. 用户可见流程完成时，在 `.codex/docs/acceptance/` 增加验收记录。

## 输出

返回：

- 已更新文档。
- 用作依据的代码事实。
- 仍然陈旧或未解决的文档区域。
