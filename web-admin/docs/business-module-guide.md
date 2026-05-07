# Business Module Guide

Use this guide when adding real business modules after the RBAC base.

## Module Definition

Before implementation, define:

- Module name and user goal.
- Data entity and important fields.
- List filters and sorting needs.
- Detail, create, edit, and delete workflows.
- Permission codes.
- Menu entry and route path.
- Backend API endpoints.
- Frontend page and route metadata.
- Tests and acceptance criteria.

Start from `templates/业务模块模板.md`.

## Backend Pattern

Default CRUD modules should follow the existing RBAC layering:

- ORM entity in `backend/app/database/entity/`.
- Repository helpers in `backend/app/database/repository/`.
- Service functions in `backend/app/service/`.
- Routes under `backend/app/apis/`.
- Permission checks with `@jwt_required()` and `@require_permission()`.
- Responses through `ok()` and `fail()`.

Add tests for:

- Missing token.
- Missing permission.
- List/filter behavior.
- Create/update validation.
- Delete behavior and association constraints.
- Unified response shape.

## Frontend Pattern

Default management pages should follow the existing Users/Roles/Menus pattern:

- API functions in `frontend/src/api/`.
- Route child under `AppLayout`.
- View under `frontend/src/views/`.
- Pinia store only if state is shared beyond one page.
- i18n keys in both languages.
- `meta.tab`, `meta.keepAlive`, and `meta.titleKey` for tabbed pages.

The UI should include loading, empty, validation, success, and failure states.

## Permission And Menu Pattern

For a module named `order`, default permission codes are:

- `order:list`
- `order:read`
- `order:create`
- `order:update`
- `order:delete`

Add module-specific actions only when the workflow needs them.

When adding permissions or menus, update backend constants, frontend i18n, seed/menu setup, `docs/rbac-and-menu.md`, and the module document.

## Acceptance Checklist

A business module is ready when:

- API contracts are documented.
- Permission codes are documented and seeded.
- Menu entry appears for authorized users only.
- Frontend route is blocked for unauthorized users.
- Backend tests pass.
- Frontend build passes.
- Manual acceptance notes are recorded under `docs/acceptance/` when user-facing behavior changed.
