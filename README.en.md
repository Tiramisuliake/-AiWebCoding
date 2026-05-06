# AI Web Coding

An enterprise-grade RBAC management system with a Flask backend and Vue 3 frontend.

## Project Overview

ai-web-coding is a complete frontend-backend separated management system, built with Flask-RESTX for RESTful APIs and Vue 3 + Vite for the frontend interface. The system implements a full Role-Based Access Control (RBAC) functionality, including modules for user management, role management, permission management, and menu management.

## Technology Stack

### Backend
- **Framework**: Flask + Flask-RESTX
- **Database**: SQLAlchemy ORM
- **Authentication**: JWT (PyJWT)
- **Task Queue**: Celery
- **Database Support**: MySQL / PostgreSQL

### Frontend
- **Framework**: Vue 3 (Composition API)
- **Build Tool**: Vite
- **State Management**: Pinia
- **Routing**: Vue Router
- **Internationalization**: vue-i18n

## Features

- **User Management**: Create, edit, delete users, and assign roles
- **Role Management**: Create roles and assign permissions and menus
- **Permission Management**: View all system permissions with their Chinese descriptions
- **Menu Management**: Tree-structured menus with dynamic menu support
- **Authentication**: JWT token authentication with refresh token support
- **Menu Localization**: Automatically synchronize menu names into Chinese

## Directory Structure

```
ai-web-coding/
├── web-admin/
│   ├── backend/               # Flask backend
│   │   ├── app/
│   │   │   ├── apis/          # API routes
│   │   │   ├── components/    # Common components
│   │   │   ├── conf/          # Configuration
│   │   │   ├── const/         # Constants
│   │   │   ├── database/      # Database models and repositories
│   │   │   ├── service/       # Business logic
│   │   │   ├── tasks/         # Celery tasks
│   │   │   └── utils/         # Utility functions
│   │   ├── scripts/           # Script tools
│   │   └── tests/             # Tests
│   └── frontend/              # Vue 3 frontend
│       ├── src/
│       │   ├── api/           # API requests
│       │   ├── assets/        # Static assets
│       │   ├── components/    # Components
│       │   ├── composables/   # Composition functions
│       │   ├── i18n/          # Internationalization
│       │   ├── router/        # Routing
│       │   ├── stores/        # Pinia state management
│       │   └── views/         # Page views
│       └── vite.config.js
└── start-frontend.ps1         # Frontend startup script
```

## Quick Start

### Backend Startup

1. Navigate to the backend directory:
```bash
cd web-admin/backend
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

3. Copy the configuration example file:
```bash
cp .env.example .env
```

4. Initialize the database:
```bash
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

5. Seed data (create admin account):
```bash
python scripts/seed.py
```

6. Start the server:
```bash
python run.py
```

### Frontend Startup

```bash
cd web-admin/frontend
npm install
npm run dev
```

Or use the PowerShell script (Windows):
```powershell
.\start-frontend.ps1
```

## API Endpoints

| Module | Endpoint | Description |
|--------|----------|-------------|
| Authentication | POST /api/auth/login | User login |
| Authentication | POST /api/auth/logout | Logout |
| Authentication | POST /api/auth/refresh | Refresh token |
| Users | GET/POST /api/users | Get user list / Create user |
| Users | GET/PUT/DELETE /api/users/{id} | User CRUD operations |
| Roles | GET/POST /api/roles | Get role list / Create role |
| Roles | GET/PUT/DELETE /api/roles/{id} | Role CRUD operations |
| Permissions | GET /api/permissions | Get permission list |
| Menus | GET /api/menus | Get menu list |
| Menus | GET /api/menus/my-tree | Get user-specific menu tree |

## Environment Variables

Backend configuration (`.env`):

```
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/web_admin
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400
```

## Testing

```bash
cd web-admin/backend
pytest tests/
```

## License

MIT License