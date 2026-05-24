# /publish

## 用途

创建版本 tag 并双端推送，完成发版流程。

## 先读

1. `.claude/skills/git-workflow/SKILL.md`
2. `git status --short --branch`
3. `git log --oneline -10`

## 步骤

1. 确认当前在 `main` 分支且工作区干净，否则中止。
2. 确认 `main` 与双远端同步：

```powershell
git fetch origin main
git fetch github main
git diff main origin/main --stat
git diff main github/main --stat
```

3. 如果用户未给出版本号，查看已有 tag 推导下一个版本：

```powershell
git tag --sort=-v:refname | Select-Object -First 5
```

4. 向用户确认版本号（格式 `vX.Y.Z`）和本次发版包含的主要变更。
5. 运行检查，确保发版质量：

```powershell
python -m pytest tests -v           # web-admin/backend/ 下
npm --prefix frontend run build     # web-admin/ 下
```

6. 创建带注释的 tag：

```powershell
git tag -a vX.Y.Z -m "vX.Y.Z: 变更摘要"
```

7. 双端推送 tag：

```powershell
git push origin --tags
git push github --tags
```

8. 确认 tag 到达双端：

```powershell
git ls-remote --tags origin | Select-String "vX.Y.Z"
git ls-remote --tags github | Select-String "vX.Y.Z"
```

## 输出

返回：

- 版本号和 tag 消息。
- 双端推送结果。
- 本次发版包含的提交范围（上一 tag 到当前）。
