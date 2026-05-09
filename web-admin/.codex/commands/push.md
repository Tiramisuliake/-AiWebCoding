# /push

## 用途

按当前项目的双远端规则推送代码。

## 先读

1. `.codex/skills/git-workflow/SKILL.md`
2. `git status --short --branch`
3. `git remote -v`

## 步骤

1. 确认当前分支。
2. 如果工作区有未提交改动，先确认提交范围，不要静默提交。
3. 如果当前分支是 `main` 且工作区干净，执行双端推送：

```powershell
git push origin main
git push github main
```

4. 如果当前分支不是 `main`，默认推到 GitHub 用于 PR：

```powershell
git push -u github <branch>
```

5. 如果用户明确说“只推 Gitee”或“只推 GitHub”，按字面只推对应远端。
6. 只有用户明确说“发版”或“推 tag”时，才推送 tag。

## 输出

返回：

- 当前提交。
- 推送目标和结果。
- 是否有未推送 tag。
