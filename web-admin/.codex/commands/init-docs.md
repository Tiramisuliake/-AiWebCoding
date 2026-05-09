# /init-docs

## 用途

创建或修复项目文档骨架。

## 先读

1. `AGENTS.md`
2. `.codex/docs/index.md`
3. `.codex/templates/文档模板.md`
4. `.codex/templates/项目状态模板.md`
5. `.codex/templates/业务模块模板.md`

## 步骤

1. 检查 `.codex/docs/`、`.codex/commands/`、`.codex/templates/` 是否存在。
2. 检查 `.codex/docs/index.md` 中列出的文件是否存在。
3. 使用模板补齐缺失文件。
4. 未经用户明确要求，不覆盖非空文档。
5. 汇报缺失、创建和跳过的文件。

## 输出

返回：

- 已存在文档。
- 已创建文档。
- 已跳过文档。
- 仍需要人工补充的内容。
