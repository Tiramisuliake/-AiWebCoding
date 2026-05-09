# 开发流程

## 推荐命令流

普通功能：

```text
/start -> /dev -> /check -> /sync -> /progress
```

CRUD 业务模块：

```text
/start -> /crud -> /check -> /sync -> /progress
```

这些命令是仓库内 `.codex/commands/` 的说明文档，不是客户端原生命令。

## 功能开发流程

1. 阅读 `AGENTS.md`、`.codex/docs/project-state.md` 和相关子系统指南。
2. 使用 `.codex/templates/业务模块模板.md` 创建或更新业务模块文档。
3. 定义 API、权限码、菜单入口、前端路由、测试和需要同步的文档。
4. 实现最小可验证功能切片。
5. 在同一个改动中同步 API/RBAC/项目状态文档。
6. 运行相关检查。
7. 对用户可见行为，在 `.codex/docs/acceptance/` 下记录验收结果。

## PR 与 CI 流程

非平凡改动使用 GitHub PR 触发 CI，Gitee 仍作为主远端保留。

1. 从最新 `main` 创建工作分支。
2. 按 `.codex/skills/git-workflow/SKILL.md` 提交。
3. 推送工作分支到 GitHub 并创建 PR。
4. 等待 `quality`、`backend-tests`、`frontend-build` 通过。
5. 合并后将 GitHub `main` 同步到 Gitee `origin/main`。

## Subagent 任务格式

独立并行任务使用以下格式：

```md
目标：
上下文：
允许修改范围：
禁止修改：
验收标准：
必须运行的检查：
最终汇报：
```

主 Agent 负责集成结果并运行最终验证。

## Worker 汇报格式

```md
修改文件：
运行检查：
结果：
风险：
开放问题：
```

## 文档同步规则

- API 请求、响应、查询参数变化时，更新 `.codex/docs/api-contracts.md`。
- 权限或菜单变化时，更新 `.codex/docs/rbac-and-menu.md`。
- 业务功能完成时，更新 `.codex/docs/project-state.md` 和 `.codex/docs/todos.md`。
- 架构变化时，更新 `.codex/docs/architecture.md` 和 `.codex/docs/decisions.md`。
- 验收结果写入 `.codex/docs/acceptance/`。
