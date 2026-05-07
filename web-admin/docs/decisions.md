# Decisions

## D1: Use Flask-RESTX

- Date: 2026-04-12
- Decision: Use Flask-RESTX for REST API namespaces and Swagger UI.
- Reason: Namespaces and generated `/api/docs` fit this admin API and reduce boilerplate.

## D2: Use SQLAlchemy Scoped Sessions

- Date: 2026-04-12
- Decision: Use configured scoped sessions instead of ad hoc global session handling.
- Reason: Request/thread isolation and predictable cleanup are important for Flask deployment and tests.

## D3: Use Application Factory

- Date: 2026-04-12
- Decision: Initialize Flask through `create_app()`.
- Reason: Supports development/testing/production config and avoids brittle global app setup.

## D4: Use Unified API Responses

- Date: 2026-04-12
- Decision: Wrap API responses as `{"code": 0, "data": {}, "msg": "ok"}`.
- Reason: Frontend can handle business status consistently across modules.

## D5: Use Repo-Local Command Playbooks

- Date: 2026-05-07
- Decision: Store command workflows in `commands/*.md`.
- Reason: The playbooks are client-agnostic and easy for Codex to read in any window.

## D6: Archive Old Planning State

- Date: 2026-05-07
- Decision: Keep old generated planning files under `.plans/archive/`.
- Reason: Historical context remains available without confusing current development.
