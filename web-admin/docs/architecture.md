# Architecture

## Overview

`web-admin` is a frontend-backend separated admin application.

```text
Vue 3 SPA
  -> Axios with JWT
Flask-RESTX API under /api
  -> service layer
  -> repository layer
  -> SQLAlchemy ORM
  -> database

Flask app -> Celery -> Redis broker/result backend
```

## Backend Structure

```text
backend/
  app/
    __init__.py              # create_app()
    apis/                    # Flask-RESTX namespaces
    service/                 # business logic
    database/
      entity/                # SQLAlchemy models and association tables
      repository/            # query/write helpers
      conn/                  # engine/session helpers
    components/              # response, permission, serializers, pagination, localization
    conf/                    # config and extension setup
    const/                   # error codes and permission constants
    tasks/                   # Celery tasks
    utils/                   # small helpers
  scripts/                   # schema, seed, upgrade scripts
  tests/                     # pytest suite
```

The route layer converts HTTP input/output. Services own validation, transactions, and business rules. Repositories encapsulate data access. Entities define persistence shape.

## Frontend Structure

```text
frontend/src/
  api/                       # Axios client functions
  components/AppLayout.vue   # authenticated shell, menu, tabs
  router/index.js            # routes and guards
  stores/                    # auth, menu, tabs, locale
  views/                     # admin pages
  i18n/messages.js           # zh-CN/en-US copy
  assets/                    # design tokens and base CSS
```

The frontend shell loads the user's menu tree after login, derives allowed paths, and blocks inaccessible routes.

## Main Data Flows

### Login

1. Frontend posts credentials to `/api/auth/login`.
2. Backend validates user and password hash.
3. Backend returns access token, refresh token, and user summary.
4. Frontend stores tokens and loads `/api/menus/my-tree`.
5. Router allows only menu-authorized paths.

### Protected API Request

1. Axios injects `Authorization: Bearer <access_token>`.
2. Flask-JWT-Extended validates the token and blocklist state.
3. Route-level permission decorator checks RBAC.
4. Service performs validation and repository calls.
5. Response is wrapped with the unified response shape.

### Role Menu And Permission Assignment

1. Frontend submits `menu_ids` and optional `permission_ids` to `/api/roles/{id}/menus`.
2. Backend requires `role:assign_menu`.
3. If permissions are included, backend also requires `role:assign_permission`.
4. Backend verifies permissions are within the submitted menu scope.
5. Menus and permissions are updated in one transaction.

## Configuration

Configuration is loaded through `backend/app/conf/config.py`. Development may load `backend/.env` or `backend/.env.example`; production must provide required secrets and database configuration through environment variables.
