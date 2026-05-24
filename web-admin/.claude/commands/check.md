# /check

## 用途

对当前改动运行代码和文档验证。

## 先读

1. `CLAUDE.md`
2. `.codex/docs/project-state.md`
3. `git status --short` 中的变更文件

## 步骤

1. 确认当前改动范围，优先只跑改动区域的聚焦测试。
2. 在 `web-admin/` 下运行：

```powershell
python scripts/run_ci.py --quick
```

3. 在 `web-admin/backend/` 下运行：

```powershell
python -m pytest tests -v
```

4. 在 `web-admin/` 下运行：

```powershell
npm --prefix frontend run build
```

5. GitHub Actions 对应三项检查：
   - `quality`：`python scripts/run_ci.py --quick`
   - `backend-tests`：`python -m pytest tests -v`
   - `frontend-build`：`npm ci` + `npm run build`

6. 检查失败时，报告第一个可操作失败点和可能归属区域。
7. 不隐藏会影响发布信心的 warning。

## 输出

返回：

- 已运行命令。
- 每条命令的通过/失败结果。
- 重要 warning。
- 必须修复项或可信结论。
