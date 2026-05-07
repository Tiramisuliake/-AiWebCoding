# /crud

## Purpose

Add a business CRUD module consistently across backend, frontend, RBAC, menu, tests, and docs.

## Read First

1. `docs/business-module-guide.md`
2. `templates/业务模块模板.md`
3. `docs/api-contracts.md`
4. `docs/rbac-and-menu.md`
5. `backend/AGENTS.md`
6. `frontend/AGENTS.md`

## Steps

1. Define module name, entity fields, list filters, and validation rules.
2. Define permission codes and menu route.
3. Add backend entity, repository, service, namespace/routes, seed/menu updates, and tests.
4. Add frontend API client, route, view, i18n copy, and tab metadata.
5. Update `docs/api-contracts.md`, `docs/rbac-and-menu.md`, and the module document.
6. Run backend tests, frontend build, and CI.

## Output

Return:

- Module name and route.
- API endpoints added.
- Permission codes added.
- Menu entry added.
- Checks run and results.
- Any manual acceptance notes.
