---
name: git-workflow
description: 当前 ai-web-coding 项目的 Git 双远端、分支、提交、PR、CI 和发版工作流。用于用户要求推送、提交、创建分支、开 PR、查看 GitHub Actions、同步 Gitee/GitHub、发版、推 tag、配置 main 保护规则时；默认 origin=Gitee 主远端，github=GitHub PR/CI 镜像，默认分支为 main。
---

# ai-web-coding Git 工作流

## 远端职责

| remote | 位置 | 用途 |
|---|---|---|
| `origin` | `git@gitee.com:tiramisulike/ai-web-coding.git` | Gitee 主远端 |
| `github` | `https://github.com/Tiramisuliake/-AiWebCoding.git` | GitHub PR/CI 镜像 |

默认分支 `main`。两端保持同步，完成后用以下命令确认：

```powershell
git ls-remote --heads origin main
git ls-remote --heads github main
```

## 分支规范

| 类型 | 格式 | 示例 |
|---|---|---|
| 新功能 | `feature/<topic>` | `feature/order-module` |
| 缺陷修复 | `fix/<topic>` | `fix/menu-filter` |
| 文档 | `docs/<topic>` | `docs/claude-workflow` |
| CI/构建 | `ci/<topic>` | `ci/web-admin-actions` |

分支名使用小写字母、数字和短横线；避免空格、中文、下划线。

## 提交规范

```
type(scope): 摘要
```

允许 type：`feat` / `fix` / `docs` / `refactor` / `test` / `chore` / `ci` / `build`

摘要可以写中文，保持短句。示例：`feat(users): 新增用户导出功能`

## PR 规范

1. 从最新 `main` 创建工作分支。
2. 推送到 GitHub：`git push -u github <branch>`
3. 在 GitHub 创建 PR，base 为 `main`。
4. 等待 `quality`、`backend-tests`、`frontend-build` 通过。
5. 合并后同步 Gitee：

```powershell
git fetch github main
git checkout main
git pull --ff-only github main
git push origin main
```

## 默认推送规则

- 在 `main` 上说"推送" → 双端推送：`git push origin main` + `git push github main`
- 在工作分支上说"推送" → 只推 GitHub：`git push -u github <branch>`
- 用户明确"只推 Gitee / 只推 GitHub" → 按字面执行

## 有未提交改动时

不要静默提交，先查看：

```powershell
git status --short --branch
git diff --stat
```

## CI 与 main 保护

GitHub Actions workflow：`.github/workflows/web-admin-ci.yml`，PR gate 三项：`quality` / `backend-tests` / `frontend-build`

应用 main 保护（需 GitHub CLI 登录）：

```powershell
gh api --method PUT repos/Tiramisuliake/-AiWebCoding/branches/main/protection --input .github/branch-protection-main.json
```

## 发版与 tag

只有用户明确说"发版"或给出版本号时才处理 tag，双端推送：

```powershell
git push origin --tags
git push github --tags
```

## 禁止事项

- 不要 force push `main`
- 不要把未验证的工作直接推到 `main`
- 不要在工作区有未提交改动时自动切分支或重置
- 不要把 tag 当作普通推送的一部分
