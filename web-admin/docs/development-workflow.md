# Development Workflow

## Recommended Command Flow

For a normal feature:

```text
/start -> /dev -> /check -> /sync -> /progress
```

For a CRUD business module:

```text
/start -> /crud -> /check -> /sync -> /progress
```

These are repo-local playbooks in `commands/`, not client-native commands.

## Feature Workflow

1. Read `AGENTS.md`, `docs/project-state.md`, and the relevant subsystem guide.
2. Create or update the business module document using `templates/业务模块模板.md`.
3. Define API, permission codes, menu entry, frontend route, tests, and docs to update.
4. Implement the smallest coherent slice.
5. Update API/RBAC/project docs in the same change.
6. Run relevant checks.
7. Record acceptance notes under `docs/acceptance/` for completed user-facing behavior.

## Subagent Assignment Format

Use this shape for independent parallel work:

```md
Goal:
Context:
Allowed write scope:
Do not change:
Acceptance criteria:
Required checks:
Final report:
```

The main agent integrates the result and runs final verification.

## Worker Final Report Format

```md
Changed files:
Checks run:
Result:
Risks:
Open questions:
```

## Documentation Sync Rules

- API request/response/query changes update `docs/api-contracts.md`.
- Permission/menu changes update `docs/rbac-and-menu.md`.
- Completed business features update `docs/project-state.md` and `docs/todos.md`.
- Architectural changes update `docs/architecture.md` and `docs/decisions.md`.
- Acceptance results go under `docs/acceptance/`.
