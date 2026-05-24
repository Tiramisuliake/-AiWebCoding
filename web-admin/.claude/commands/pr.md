# /pr

## 用途

通过 GitHub 创建或更新 PR，触发 web-admin CI，并在合并后同步 Gitee 主远端。

## 先读

1. `.claude/skills/git-workflow/SKILL.md`
2. `.github/workflows/web-admin-ci.yml`
3. `git status --short --branch`
4. `git remote -v`

## 步骤

1. 确认当前不在 `main` 直接开发；非平凡改动使用 `feature/<topic>`、`fix/<topic>`、`docs/<topic>` 或 `ci/<topic>`。
2. 有未提交改动时，先确认改动范围和提交信息，不要静默提交。
3. 本地运行相关检查：

```powershell
# web-admin/ 下
python scripts/run_ci.py --quick
npm --prefix frontend run build

# web-admin/backend/ 下
python -m pytest tests -v
```

4. 推送工作分支到 GitHub：

```powershell
git push -u github <branch>
```

5. 创建 PR，base 为 `main`，使用 `.github/pull_request_template.md` 填写验证和风险。
6. 等待 `quality`、`backend-tests`、`frontend-build` 全部通过。
7. PR 合并后同步 Gitee：

```powershell
git fetch github main
git checkout main
git pull --ff-only github main
git push origin main
```

## main 保护配置

```powershell
gh api --method PUT repos/Tiramisuliake/-AiWebCoding/branches/main/protection --input .github/branch-protection-main.json
```

## 输出

返回：

- 当前分支和提交。
- PR 链接。
- 三项 CI 检查结果。
- GitHub main 与 Gitee main 是否同步。
