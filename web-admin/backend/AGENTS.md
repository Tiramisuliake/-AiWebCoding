# Backend Agent Guide

## Scope

This directory contains the Flask-RESTX API, SQLAlchemy models/repositories, services, Celery wiring, scripts, and pytest tests.

Read the root `AGENTS.md` first, then this file for backend-specific rules.

## Architecture Rules

- Create Flask apps only through `app.create_app()`.
- Keep request handling in `app/apis/*/routes.py`.
- Put business logic in `app/service/`.
- Put database access helpers in `app/database/repository/`.
- Put ORM models and association tables in `app/database/entity/`.
- Keep shared response, permission, pagination, serialization, and localization helpers in `app/components/`.
- Keep configuration in `app/conf/config.py` and extension setup in `app/conf/extensions.py`.

Do not put complex database logic directly in route handlers.

## API And Response Rules

- All business API routes live under `/api`.
- API docs are exposed at `/api/docs`.
- Use `ok()` and `fail()` from `app/components/response.py`.
- Keep response shape consistent:

```json
{ "code": 0, "data": {}, "msg": "ok" }
```

- Use `ServiceError` for expected business failures and convert it in the route layer.
- Keep validation failures on code `1001`, missing resources on `1002`, conflicts on `1003`, auth failures on `2001`, permission failures on `2002`, and server failures on `5001`.

## Auth, RBAC, And Sessions

- Protected endpoints require `@jwt_required()`.
- Permissioned endpoints also require `@require_permission("module:action")`.
- `admin` role permission bypass behavior is implemented in the authz service; do not duplicate it in routes.
- Use SQLAlchemy ORM only. Do not build SQL with string concatenation.
- Use the configured scoped session helpers in `app/database/conn/`.
- Rely on app teardown to remove sessions at request end.

## Adding A Backend Feature

For a new business module:

- Define or update ORM entities and repository helpers.
- Add service functions with validation and transaction boundaries.
- Add Flask-RESTX namespace/routes.
- Add permission codes and Chinese localization mappings.
- Add seed/menu initialization when the module needs navigation.
- Update `docs/api-contracts.md` and `docs/rbac-and-menu.md`.
- Add pytest coverage for auth, permissions, happy path, validation, and destructive operations.

## Checks

Run backend tests from `web-admin/backend/`:

```powershell
python -m pytest tests -v
```

Run project CI from `web-admin/`:

```powershell
python scripts/run_ci.py
```

Use narrower pytest targets while developing, then run the full backend suite before delivery.
