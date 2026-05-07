# /dev

## Purpose

Develop a new feature from business intent through implementation and verification.

## Read First

1. `AGENTS.md`
2. `docs/project-state.md`
3. `docs/business-module-guide.md`
4. `docs/api-contracts.md`
5. `docs/rbac-and-menu.md`
6. `backend/AGENTS.md` or `frontend/AGENTS.md` as needed.

## Steps

1. Clarify the feature goal, users, workflow, and acceptance criteria.
2. Create or update a business module document using `templates/业务模块模板.md`.
3. Define API, permission codes, menu entry, frontend route, tests, and docs to update.
4. Implement the smallest coherent slice.
5. Update API/RBAC/project docs in the same change.
6. Run relevant checks.
7. Record acceptance notes for user-facing behavior.

## Output

Return:

- Summary of feature behavior.
- Changed files grouped by backend, frontend, and docs.
- Checks run and results.
- Remaining risks or follow-up todos.
