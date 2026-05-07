# Frontend Agent Guide

## Scope

This directory contains the Vue 3 SPA, Element Plus UI, Pinia stores, router guards, API clients, i18n messages, and design tokens.

Read the root `AGENTS.md` first, then this file for frontend-specific rules.

## Architecture Rules

- Use Vue 3 `script setup` and the Composition API for new or rewritten views.
- Call backend APIs through `src/api/http.js`, `src/api/auth.js`, and `src/api/rbac.js`.
- Keep auth state in `src/stores/auth.js`.
- Keep menu access state in `src/stores/menu.js`.
- Keep tab state in `src/stores/tabs.js`.
- Keep language state in `src/stores/locale.js` and messages in `src/i18n/messages.js`.
- Keep shared shell behavior in `src/components/AppLayout.vue`.

## Routing And Access

- New authenticated pages must be children of `AppLayout`.
- Route meta for tabbed pages must include `tab`, `keepAlive`, and `titleKey`.
- The route guard loads `/api/menus/my-tree` and blocks paths not present in `allowedPaths`.
- New menu-backed pages must have matching backend menu records and permission mappings.

## UI And Copy

- Preserve the existing Element Plus admin style.
- Use `src/assets/design-tokens.css` for theme values; do not hardcode new theme colors unless a token is missing and added intentionally.
- User-facing text must be added to both `zh-CN` and `en-US` in `src/i18n/messages.js`.
- Permission and menu management are Chinese-first by design; permission codes remain technical identifiers.
- New management pages should follow the existing table/search/dialog pattern in Users, Roles, Permissions, and Menus.

## Adding A Frontend Feature

For a new business module:

- Add API client functions.
- Add route and page view.
- Add menu/permission seed expectations to docs.
- Add i18n keys for all user-facing copy.
- Add tab metadata for pages that should appear in the shell.
- Keep loading, empty, validation, success, and failure states explicit.
- Update `docs/api-contracts.md` when frontend payloads or query parameters change.

## Checks

Run from `web-admin/`:

```powershell
npm --prefix frontend run build
python scripts/run_ci.py --quick
```

Use the Vite dev server for manual UI verification when a visual or routing change is made.
