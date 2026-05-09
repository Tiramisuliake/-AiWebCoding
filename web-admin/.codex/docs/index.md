# 文档索引

`.codex/docs/` 是当前项目的文档真理源，供 Agent 和工程师共同使用。

## 新窗口先读

1. `AGENTS.md`
2. `.codex/docs/project-state.md`
3. 与任务相关的子系统指南：
   - `backend/AGENTS.md`
   - `frontend/AGENTS.md`
4. 修改 API 行为时读 `.codex/docs/api-contracts.md`。
5. 修改权限、角色或菜单时读 `.codex/docs/rbac-and-menu.md`。

## 业务开发先读

1. `.codex/docs/business-module-guide.md`
2. `.codex/templates/业务模块模板.md`
3. `.codex/docs/api-contracts.md`
4. `.codex/docs/rbac-and-menu.md`
5. `.codex/docs/development-workflow.md`
6. `.codex/commands/dev.md` 或 `.codex/commands/crud.md`

## 验证与状态先读

1. `.codex/docs/todos.md`
2. `.codex/docs/project-state.md`
3. `.codex/docs/acceptance/`
4. `.codex/docs/decisions.md`
5. `.codex/docs/invariants.md`
6. `.codex/commands/check.md`
7. `.codex/commands/progress.md`

## 命令手册

| 命令 | 文件 | 用途 |
|---|---|---|
| `/start` | `.codex/commands/start.md` | 在新窗口快速理解项目。 |
| `/dev` | `.codex/commands/dev.md` | 基于业务文档开发功能。 |
| `/crud` | `.codex/commands/crud.md` | 按统一模式新增 CRUD 模块。 |
| `/check` | `.codex/commands/check.md` | 运行代码与文档检查。 |
| `/pr` | `.codex/commands/pr.md` | 创建 GitHub PR、等待 CI 并同步 Gitee。 |
| `/sync` | `.codex/commands/sync.md` | 按当前代码同步文档。 |
| `/next` | `.codex/commands/next.md` | 建议下一项有价值工作。 |
| `/progress` | `.codex/commands/progress.md` | 生成项目进度报告。 |
| `/update-status` | `.codex/commands/update-status.md` | 更新项目状态和待办。 |
| `/add-todo` | `.codex/commands/add-todo.md` | 添加结构化待办。 |
| `/init-docs` | `.codex/commands/init-docs.md` | 修复缺失的文档骨架。 |

## 历史材料

旧规划和生成的团队启动文件已经归档到 `.plans/archive/`。这些文件不是当前项目状态。
