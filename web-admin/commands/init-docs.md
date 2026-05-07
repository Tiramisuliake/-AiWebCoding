# /init-docs

## Purpose

Create or repair the documentation skeleton for this project.

## Read First

1. `AGENTS.md`
2. `docs/index.md`
3. `templates/文档模板.md`
4. `templates/项目状态模板.md`
5. `templates/业务模块模板.md`

## Steps

1. Check that `docs/`, `commands/`, and `templates/` exist.
2. Check that all files listed in `docs/index.md` exist.
3. Recreate missing files from templates.
4. Do not overwrite non-empty documents without explicit user request.
5. Report missing, created, and skipped files.

## Output

Return:

- Existing docs.
- Created docs.
- Skipped docs.
- Any content that still needs human input.
