# System Invariants

Violating these boundaries is a critical bug.

## Security

- All non-public API endpoints require JWT.
- Permissioned resources require the matching RBAC permission.
- Passwords are stored as bcrypt hashes, never plaintext.
- JWT secrets and database credentials come from environment/config, not source code.
- Revoked access and refresh tokens must be rejected.

## API Contracts

- API responses use the unified response shape.
- Business validation errors use stable business error codes.
- Frontend API clients must match `docs/api-contracts.md`.

## Data And Persistence

- Database operations use SQLAlchemy ORM and configured sessions.
- Request-scoped sessions are removed at teardown.
- Menu tree construction must handle malformed or cyclic data safely.
- Destructive operations must respect service-layer association rules.

## Frontend Access

- Authenticated pages are guarded by login state.
- Menu-backed routes are constrained by `/api/menus/my-tree`.
- Tab persistence must sanitize inaccessible routes after permission changes.

## Documentation

- API, permission, menu, and architecture changes update the matching document in `docs/`.
- Historical archive files must not be used as current implementation guidance.
