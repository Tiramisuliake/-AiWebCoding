


Now I have a good understanding of the project from the code map. This is a web-admin project with a Flask backend and Vue.js frontend featuring RBAC (Role-Based Access Control) management. Let me create the README.

# AI Web Coding

一个基于 Flask 后端和 Vue 3 前端的企业级 RBAC 管理系统。

## 项目简介

ai-web-coding 是一个完整的前后端分离管理后台系统，采用 Flask-RESTX 构建 RESTful API，Vue 3 + Vite 构建前端界面。系统实现了完整的基于角色的访问控制（RBAC）功能，包括用户管理、角色管理、权限管理和菜单管理模块。

## 技术栈

### 后端
- **框架**: Flask + Flask-RESTX
- **数据库**: SQLAlchemy ORM
- **认证**: JWT (PyJWT)
- **任务队列**: Celery
- **数据库支持**: MySQL / PostgreSQL

### 前端
- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **状态管理**: Pinia
- **路由**: Vue Router
- **国际化**: vue-i18n

## 功能特性

- 用户管理：创建、编辑、删除用户，分配角色
- 角色管理：创建角色，分配权限和菜单
- 权限管理：查看系统所有权限及其中文描述
- 菜单管理：树形菜单结构，支持动态菜单
- 认证登录：JWT 令牌认证，支持刷新令牌
- 菜单本地化：自动将菜单名称同步为中文

## 目录结构

```
ai-web-coding/
├── web-admin/
│   ├── backend/               # Flask 后端
│   │   ├── app/
│   │   │   ├── apis/          # API 路由
│   │   │   ├── components/   # 公共组件
│   │   │   ├── conf/         # 配置
│   │   │   ├── const/        # 常量
│   │   │   ├── database/     # 数据库模型和仓库
│   │   │   ├── service/      # 业务逻辑
│   │   │   ├── tasks/        # Celery 任务
│   │   │   └── utils/        # 工具函数
│   │   ├── scripts/          # 脚本工具
│   │   └── tests/            # 测试
│   └── frontend/             # Vue 3 前端
│       ├── src/
│       │   ├── api/         # API 请求
│       │   ├── assets/      # 静态资源
│       │   ├── components/  # 组件
│       │   ├── composables/ # 组合式函数
│       │   ├── i18n/        # 国际化
│       │   ├── router/      # 路由
│       │   ├── stores/      # Pinia 状态管理
│       │   └── views/       # 页面视图
│       └── vite.config.js
└── start-frontend.ps1       # 前端启动脚本
```

## 快速开始

### 后端启动

1. 进入后端目录：
```bash
cd web-admin/backend
```

2. 创建虚拟环境并安装依赖：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

3. 复制配置示例文件：
```bash
cp .env.example .env
```

4. 初始化数据库：
```bash
python manage.py db init
python manage.py db migrate
python manage.py db upgrade
```

5. 种子数据（创建管理员账户）：
```bash
python scripts/seed.py
```

6. 启动服务：
```bash
python run.py
```

### 前端启动

```bash
cd web-admin/frontend
npm install
npm run dev
```

或使用 PowerShell 脚本（Windows）：
```powershell
.\start-frontend.ps1
```

## API 接口

| 模块 | 接口 | 说明 |
|------|------|------|
| 认证 | POST /api/auth/login | 用户登录 |
| 认证 | POST /api/auth/logout | 登出 |
| 认证 | POST /api/auth/refresh | 刷新令牌 |
| 用户 | GET/POST /api/users | 用户列表/创建 |
| 用户 | GET/PUT/DELETE /api/users/{id} | 用户 CRUD |
| 角色 | GET/POST /api/roles | 角色列表/创建 |
| 角色 | GET/PUT/DELETE /api/roles/{id} | 角色 CRUD |
| 权限 | GET /api/permissions | 权限列表 |
| 菜单 | GET /api/menus | 菜单列表 |
| 菜单 | GET /api/menus/my-tree | 用户菜单树 |

## 环境变量

后端配置（`.env`）：

```
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/web_admin
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=86400
```

## 测试

```bash
cd web-admin/backend
pytest tests/
```

## 许可证

MIT License