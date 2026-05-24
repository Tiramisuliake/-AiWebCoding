# /dev

## 用途

从业务意图出发，完成新功能的设计、实现和验证。

## 先读

1. `CLAUDE.md`
2. `.codex/docs/project-state.md`
3. `.codex/docs/business-module-guide.md`
4. `.codex/docs/api-contracts.md`
5. `.codex/docs/rbac-and-menu.md`
6. 按需读取 `.claude/backend.md` 或 `.claude/frontend.md`

## 步骤

1. 明确功能目标、用户、流程和验收标准。
2. 使用 `.claude/templates/业务模块模板.md` 创建或更新业务模块文档。
3. 定义 API、权限码、菜单入口、前端路由、测试和需要同步的文档。
4. 实现最小可验证功能切片。
5. 在同一改动中更新 API/RBAC/项目状态文档。
6. 运行相关检查（见 `.claude/commands/check.md`）。
7. 对用户可见行为记录验收结果到 `.codex/docs/acceptance/`。

## 输出

返回：

- 功能行为摘要。
- 按后端、前端、文档分组的修改文件。
- 已运行检查和结果。
- 剩余风险或后续待办。
