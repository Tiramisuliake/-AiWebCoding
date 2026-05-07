# RBAC And Menu Rules

## Data Model

Current RBAC and navigation tables:

- `users`
- `roles`
- `permissions`
- `menus`
- `user_roles`
- `role_permissions`
- `role_menus`
- `token_blocklist`

`users`, `roles`, `permissions`, and `menus` are ORM entities. The three join tables model many-to-many grants. `token_blocklist` stores revoked token ids.

## Permission Codes

Built-in permission codes currently include:

- `user:list`, `user:read`, `user:create`, `user:update`, `user:delete`, `user:assign_role`
- `role:list`, `role:read`, `role:create`, `role:update`, `role:delete`, `role:assign_permission`, `role:assign_menu`
- `permission:list`, `permission:read`
- `menu:list`, `menu:read`, `menu:create`, `menu:update`, `menu:delete`

When adding a business module, use the same `module:action` pattern, for example `order:list`, `order:read`, `order:create`, `order:update`, `order:delete`.

## Authorization Semantics

- Protected routes require JWT.
- Permissioned routes require `@require_permission("module:action")`.
- Users with the `admin` role are allowed by the authz service.
- Non-admin users receive permissions through roles.
- Role permission assignment accepts valid ids and reports invalid ids/warnings.

## Menu Semantics

- Menus are hierarchical through `parent_id`.
- `route_path` links backend menu records to frontend routes.
- `permission_code` links a menu to the permission needed for that page or feature.
- `/api/menus/my-tree` filters hidden or disabled menus.
- Admin users receive all visible and enabled menus.
- Non-admin users receive menus granted to their roles.
- Menu tree builders must guard against cycle data.

## Combined Role Menu And Permission Assignment

`POST /api/roles/{role_id}/menus` supports updating menus and, optionally, permissions in one request.

Rules:

- `menu_ids` is required.
- `permission_ids` is optional.
- Including `permission_ids` requires `role:assign_permission` in addition to `role:assign_menu`.
- Included permissions must belong to the selected menus' manageable scope.
- If permission scope validation fails, no menu or permission update is written.

## Chinese-First Localization

Permissions and menus are Chinese-first in admin UI:

- Permission list displays Chinese name plus a separate permission-code column.
- Assignment dialogs should display `中文权限名（permission:code）`.
- Menu names should default to Chinese.
- Permission codes remain stable technical identifiers.

When adding built-in permission codes, update:

- `backend/app/const/permissions.py`
- `frontend/src/i18n/messages.js`
- Seed or startup sync logic if needed.
- This document and `docs/api-contracts.md` if API behavior changes.

When adding built-in menus or naming rules, update:

- `backend/app/components/menu_localization.py`
- Seed/menu initialization scripts.
- Frontend route metadata and i18n copy.
- `docs/business-module-guide.md` if the module pattern changes.
