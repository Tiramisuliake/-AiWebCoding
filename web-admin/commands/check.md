# /check

## 用途

对当前改动运行代码和文档验证。

## 先读

1. `AGENTS.md`
2. `docs/project-state.md`
3. `git status --short` 中的变更文件。

## 步骤

1. 检查当前改动范围。
2. 尽可能先运行改动区域的聚焦测试。
3. 在 `web-admin/` 下运行：

```powershell
python scripts/run_ci.py --quick
npm --prefix frontend run build
```

4. 在 `web-admin/backend/` 下运行：

```powershell
python -m pytest tests -v
```

5. 如果检查失败，报告第一个可操作失败点和可能归属区域。
6. 不隐藏会影响发布信心的 warning。

## 输出

返回：

- 已运行命令。
- 每条命令的通过/失败结果。
- 重要 warning。
- 必须修复项或可信结论。
