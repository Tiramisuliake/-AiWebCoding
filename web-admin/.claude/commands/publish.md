# /publish

## 用途

创建版本 tag 并双端推送，完成发版流程。自动推导版本号和变更摘要，无需用户输入。

## 先读

1. `.claude/skills/git-workflow/SKILL.md`
2. `git status --short --branch`
3. `git log --oneline -10`
4. `git tag --sort=-v:refname | Select-Object -First 5`

## 自动版本号推导规则

读取最新 tag（如 `v2.0.0`），分析自该 tag 以来的所有 commit message，按以下规则推导：

| Commit 类型/关键词 | 版本递增 | 示例 |
|---|---|---|
| `BREAKING CHANGE` / `!:` / `feat!:` | major（X+1.0.0） | `v2.0.0` → `v3.0.0` |
| `feat:` / `feat(scope):` | minor（X.Y+1.0） | `v2.0.0` → `v2.1.0` |
| 仅 `fix:` / `docs:` / `chore:` / `refactor:` / `test:` / `ci:` / `build:` | patch（X.Y.Z+1） | `v2.0.0` → `v2.0.1` |

混合多种类型时取最高级别。无 tag 时从 `v0.1.0` 开始。

## 自动变更摘要规则

从 `git log <last-tag>..HEAD --oneline` 提取 commit message：
- 按类型分组（feat / fix / docs / 其他）
- 每组列前 5 条
- 用作 tag annotation 的正文

## 步骤

1. 确认当前在 `main` 分支且工作区干净（有未提交改动则提示并中止）。
2. 双远端同步检查：

```powershell
git fetch origin main
git fetch github main
git diff main origin/main --stat
git diff main github/main --stat
```

如果本地领先双端，先推送代码：`git push origin main; git push github main`。

3. 读取最新 tag 并按规则**自动推导**下一个版本号：

```powershell
git tag --sort=-v:refname | Select-Object -First 1
git log <last-tag>..HEAD --oneline
```

4. 自动生成 tag annotation（无需问用户）：

```
vX.Y.Z: <主要变更一句话摘要>

feat:
- <commit 1>
- <commit 2>
...

fix:
- <commit 1>
...
```

5. 简短告知用户：**"将发版 vX.Y.Z，包含 N 个 commit。"**（不要求确认，除非用户预先说"先确认"）。

6. 运行质量检查（如适用，前后端项目才跑）：

```powershell
python -m pytest tests -v           # web-admin/backend/ 下
npm --prefix frontend run build     # web-admin/ 下
```

检查失败则中止发版并报告。

7. 创建带注释 tag：

```powershell
git tag -a vX.Y.Z -m @'
<完整 annotation 文本>
'@
```

8. 双端推送 tag：

```powershell
git push origin --tags
git push github --tags
```

9. 验证 tag 到达双端：

```powershell
git ls-remote --tags origin | Select-String "vX.Y.Z"
git ls-remote --tags github | Select-String "vX.Y.Z"
```

## 输出

返回：
- 版本号、版本递增类型（major/minor/patch）和推导依据。
- Tag annotation 全文。
- 双端推送结果。
- 本次发版的 commit 范围（上一 tag .. 当前）。

## 跳过版本号推导

如果用户在 `/publish` 后跟具体版本号（如 `/publish v3.0.0`），直接用该版本号，跳过推导逻辑。
