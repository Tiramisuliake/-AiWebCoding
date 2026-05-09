# /add-todo

## 用途

向 `.codex/docs/todos.md` 添加结构化待办。

## 先读

1. `.codex/docs/todos.md`
2. `.codex/templates/待办清单模板.md`

## 步骤

1. 明确任务、模块、优先级、来源和验收标准。
2. 除非工作已经开始，否则状态使用 `open`。
3. 只有紧急故障或安全问题使用 `P0`。
4. 在 `.codex/docs/todos.md` 中新增或更新一行。
5. 避免重复添加已有待办。

## 输出

返回：

- 已新增或更新的待办。
- 优先级和理由。
- 验收标准。
