# web-admin Agent Guide

## Project State

`web-admin` is a working Flask + Vue RBAC admin system. The base platform is complete enough for business-module development:

- Auth: login, logout, refresh token, token blocklist.
- Users: CRUD, paging, multi-field search, role assignment.
- Roles: CRUD, permission assignment, menu assignment, combined menu-permission assignment.
- Permissions: list/detail, Chinese-first display rules.
- Menus: tree CRUD, role menu grants, `/api/menus/my-tree`, hidden/disabled filtering.
- Frontend shell: login, route guard, dynamic menu access, tab persistence, draggable closable tabs.

The next phase is real business feature development on top of this base, not scaffold creation.

## Source Of Truth

Use this order when documents disagree:

1. Current code behavior.
2. `docs/project-state.md`.
3. `docs/api-contracts.md`.
4. `docs/architecture.md`.
5. `docs/decisions.md`.
6. `.plans/archive/` historical material.

Do not treat `.plans/archive/` as current project state. It exists only for traceability.

## Repository Map

```text
web-admin/
  AGENTS.md                  # Long-term agent entrypoint
  CLAUDE.md                  # Compatibility pointer
  commands/                  # Repo-local command playbooks
  docs/                      # Current project truth source
  templates/                 # Business/document templates
  backend/                   # Flask-RESTX API
  frontend/                  # Vue 3 SPA
  scripts/                   # Project checks
```

Read the nearest `AGENTS.md` before changing a subsystem:

- Backend work: `backend/AGENTS.md`
- Frontend work: `frontend/AGENTS.md`
- Business feature work: `docs/business-module-guide.md`

## Common Commands

Run commands from `web-admin/` unless noted otherwise.

```powershell
python scripts/run_ci.py --quick
python scripts/run_ci.py
npm --prefix frontend run build
npm --prefix frontend run dev
python backend/run.py
python backend/scripts/db_schema.py init-db
python backend/scripts/seed.py --create-tables
```

Run backend pytest from `backend/`:

```powershell
python -m pytest tests -v
```

## Development Rules

- Keep changes scoped to the requested feature or fix.
- For API, schema, permission, menu, or behavior changes, update `docs/api-contracts.md`, `docs/rbac-and-menu.md`, or the relevant business module document in the same task.
- Do not hardcode secrets, database passwords, access tokens, or refresh tokens in source files.
- Do not bypass backend layering for complex database logic.
- Do not break the unified response shape:

```json
{ "code": 0, "data": {}, "msg": "ok" }
```

- Do not expose protected resources without JWT and permission checks unless the endpoint is explicitly public.
- Do not change permission codes, menu route mappings, or localization rules without updating backend constants, frontend i18n, seed/menu initialization, and docs.

## Subagent Policy

Use subagents only for independent, clearly bounded work that can run in parallel. The main agent owns user alignment, final integration, conflict handling, verification, and delivery.

Every subagent assignment must include:

- Goal and acceptance criteria.
- Context files to read.
- Allowed write scope.
- Files or areas that must not be changed.
- Required checks.
- Expected final report: changed files, tests run, risks, and open questions.

Workers are not alone in the codebase. They must preserve unrelated edits, avoid reverting others' work, and adapt to existing changes.

Prefer local work for tightly coupled changes, urgent blockers, or tasks whose next step depends on the result.

## Documentation Policy

- `docs/` is the current living documentation set.
- `commands/` contains reusable Codex playbooks such as `/start`, `/dev`, `/crud`, `/check`, and `/sync`.
- `templates/` contains copy-ready structures for business modules, project state, todos, and general docs.
- `.plans/archive/` is historical. Read it only when investigating why an old decision was made.

Before finishing feature work, run the smallest relevant check first, then broaden if the change affects shared contracts.
