---
name: git-workflow
description: 当前 ai-web-coding 项目的 Git 双远端、分支、提交、PR、CI 和发版工作流。用于用户要求推送、提交推送、创建分支、开 PR、查看 GitHub Actions、同步 Gitee/GitHub、发版、推 tag、配置或检查 main 保护规则时；默认 origin=Gitee 主远端，github=GitHub PR/CI 镜像，默认分支为 main。
---

# ai-web-coding Git 工作流

## 远端职责

当前项目有两个固定远端：

| remote | 位置 | 用途 |
|---|---|---|
| `origin` | `git@gitee.com:tiramisulike/ai-web-coding.git` | Gitee 主远端 |
| `github` | `https://github.com/Tiramisuliake/-AiWebCoding.git` | GitHub PR/CI 镜像远端 |

默认分支是 `main`。`main` 必须保持 Gitee 和 GitHub 同步，完成后用以下命令确认：

```powershell
git ls-remote --heads origin main
git ls-remote --heads github main
```

## 分支规范

非平凡改动先建工作分支，再通过 GitHub PR 触发 CI：

| 类型 | 分支格式 | 示例 |
|---|---|---|
| Codex 日常任务 | `codex/<topic>` | `codex/github-ci` |
| 新功能 | `feature/<topic>` | `feature/order-module` |
| 缺陷修复 | `fix/<topic>` | `fix/menu-filter` |
| 文档调整 | `docs/<topic>` | `docs/codex-workflow` |
| CI/构建 | `ci/<topic>` | `ci/web-admin-actions` |

分支名使用小写字母、数字和短横线；避免空格、中文、下划线。

## 提交规范

提交信息使用：

```text
type(scope): summary
```

允许的 `type`：

- `feat`：新增业务能力。
- `fix`：修复缺陷。
- `docs`：文档或 Codex 资料。
- `refactor`：不改变行为的重构。
- `test`：测试。
- `chore`：维护性调整。
- `ci`：CI、PR、自动化配置。
- `build`：依赖、构建链路。

`summary` 可以写中文，保持短句。例如：

```text
ci(github): 添加 web-admin PR gate
docs(codex): 扩展双远端工作流
```

## PR 规范

GitHub 负责 PR 和 CI 可视化，Gitee 仍是主远端。

1. 从最新 `main` 创建工作分支。
2. 提交后先推到 GitHub：

```powershell
git push -u github <branch>
```

3. 在 GitHub 创建 PR，base 为 `main`。
4. 等待 `quality`、`backend-tests`、`frontend-build` 通过。
5. 合并 PR 后拉取 GitHub `main`，再同步推送到 Gitee：

```powershell
git fetch github main
git checkout main
git pull --ff-only github main
git push origin main
```

如果用户明确要求直接双端推送 `main`，必须先确认工作区干净且当前分支是 `main`。

## 默认推送规则

用户在 `main` 上说“推送”时，默认理解为双端推送：

```powershell
git push origin main
git push github main
```

用户明确说“只推 Gitee”时，只执行：

```powershell
git push origin main
```

用户明确说“只推 GitHub”时，只执行：

```powershell
git push github main
```

用户在工作分支上说“推送”时，默认只推 GitHub，用于创建或更新 PR：

```powershell
git push -u github <branch>
```

## 有未提交改动时

不要静默提交。先查看：

```powershell
git status --short --branch
git diff --stat
```

如果用户说“提交推送”，先确认改动范围和提交信息，再提交并双端推送。

## GitHub CI 与 main 保护

GitHub Actions workflow 位于仓库根目录 `.github/workflows/web-admin-ci.yml`，PR gate 包含：

- `quality`
- `backend-tests`
- `frontend-build`

main 分支保护规则保存在仓库根目录 `.github/branch-protection-main.json`。登录 GitHub CLI 后可应用：

```powershell
gh api --method PUT repos/Tiramisuliake/-AiWebCoding/branches/main/protection --input .github/branch-protection-main.json
```

分支保护要求三项检查通过，禁止 force push 和删除分支，默认不强制 reviewer 数量。

## 发版与 tag

只有用户明确说“发版”“推 tag”或给出版本号时，才处理 tag。

推送 tag 时双端执行：

```powershell
git push origin --tags
git push github --tags
```

## 完成后验证

推送后检查：

```powershell
git status --short --branch
git log -1 --oneline --decorate
```

确认 `origin/main` 和 `github/main` 指向同一个 HEAD。

## 禁止事项

- 不要 force push `main`。
- 不要把未完成或未验证的工作直接推到 `main`。
- 不要在工作区有未提交改动时自动切分支、提交或重置。
- 不要改远端命名，除非用户明确要求。
- 不要把 tag 当作普通推送的一部分。
