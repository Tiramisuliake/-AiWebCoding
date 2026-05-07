# Project State

## Current Phase

The RBAC platform base is complete. The project is ready for real business-module development.

## Implemented Capabilities

- Backend app factory, environment configuration, SQLAlchemy scoped session, JWT, bcrypt, CORS, Celery initialization.
- Auth API: login, logout, refresh token, token blocklist.
- User management: CRUD, paging, keyword and field search, active-state filter, role assignment.
- Role management: CRUD, permission assignment, menu assignment, combined menu-permission assignment.
- Permission management: list/detail, optional paging, multi-field filters.
- Menu management: tree CRUD, route mapping, role assignment, user menu tree, hidden/disabled filtering, cycle-safe tree handling.
- Chinese-first permission and menu localization with startup sync flags.
- Frontend login, layout shell, menu-based route guard, Pinia stores, tab persistence, draggable closable tabs.

## Entrypoints

- Backend app: `backend/app/__init__.py`
- Backend run script: `backend/run.py`
- API namespaces: `backend/app/apis/`
- ORM models: `backend/app/database/entity/models.py`
- Frontend app: `frontend/src/main.js`
- Frontend router: `frontend/src/router/index.js`
- Frontend layout: `frontend/src/components/AppLayout.vue`
- Frontend API clients: `frontend/src/api/`

## Current Checks

Known good verification from 2026-05-07:

- `python -m pytest tests -v` from `backend/`: 24 passed.
- `npm --prefix frontend run build` from `web-admin/`: passed with existing chunk-size warning only.

Preferred current commands from `web-admin/`:

```powershell
npm --prefix frontend run build
python scripts/run_ci.py
```

Run backend tests from `web-admin/backend/`:

```powershell
python -m pytest tests -v
```

## Documentation State

- `docs/` is current.
- `.plans/archive/` is historical only.
- `CLAUDE.md` is a compatibility pointer.
- Root project README files outside `web-admin/` may lag this documentation.

## Next Work

Start new business modules with `docs/business-module-guide.md` and `templates/业务模块模板.md`. Each module should define data shape, API, permissions, menu entry, frontend page, tests, and acceptance criteria before implementation.
