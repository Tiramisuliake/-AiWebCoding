# /start

## 用途

在新的 Claude Code 会话中快速理解项目并定位任务。

## 先读

1. `CLAUDE.md`
2. `.claude/docs/index.md`
3. `.codex/docs/project-state.md`
4. 如果用户提到后端或前端，再读对应文件：`.claude/backend.md` / `.claude/frontend.md`

## 步骤

1. 总结当前项目阶段和已实现能力。
2. 判断用户任务可能涉及的区域。
3. 只读取与任务相关的文档和代码入口。
4. 汇报当前状态、可能的下一步和即时风险。

## 输出

返回：

- 当前状态，3-5 条。
- 任务相关的文件/文档。
- 建议行动。
- 需要用户确认的阻塞或歧义。
