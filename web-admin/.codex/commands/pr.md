# /pr

## 用途

通过 GitHub 创建或更新 PR，触发 web-admin CI，并在合并后同步 Gitee 主远端。

## 先读

1. `.codex/skills/git-workflow/SKILL.md`
2. `.github/workflows/web-admin-ci.yml`
3. `git status --short --branch`
4. `git remote -v`

## 步骤

1. 确认当前不在 `main` 直接开发；非平凡改动使用 `codex/<topic>`、`feature/<topic>`、`fix/<topic>`、`docs/<topic>` 或 `ci/<topic>`。
2. 有未提交改动时，先确认改动范围和提交信息，不要静默提交。
3. 本地运行与改动相关的检查，至少覆盖：

```powershell
python scripts/run_ci.py --quick
python -m pytest tests -v
npm ci
npm run build
```

其中 pytest 在 `web-admin/backend` 下运行，npm 命令在 `web-admin/frontend` 下运行。

4. 推送当前工作分支到 GitHub：

```powershell
git push -u github <branch>
```

5. 创建 PR，base 为 `main`，使用 `.github/pull_request_template.md` 填写验证和风险。
6. 等待 GitHub Actions 的 `quality`、`backend-tests`、`frontend-build` 全部通过。
7. PR 合并后同步 Gitee：

```powershell
git fetch github main
git checkout main
git pull --ff-only github main
git push origin main
```

## main 保护配置

GitHub CLI 登录后，可应用 main 分支保护：

```powershell
gh api --method PUT repos/Tiramisuliake/-AiWebCoding/branches/main/protection --input .github/branch-protection-main.json
```

保护规则要求 `quality`、`backend-tests`、`frontend-build` 通过，禁止 force push 和删除分支。

## 输出

返回：

- 当前分支和提交。
- PR 链接。
- 三项 CI 检查结果。
- GitHub main 与 Gitee main 是否同步。
