# web-admin - 架构

> 维护者：team-lead, devs（架构变更后更新）

## 系统概览

前后端分离的通用 CRUD 管理后台。后端提供 RESTful API，前端通过 Axios 调用。JWT 负责认证，RBAC 控制权限。

```
[浏览器 Vue 3]
     ↓ Axios HTTP + JWT Token
[Flask-RESTX API]
     ↓ SQLAlchemy ORM
[MySQL 数据库]

[Celery Worker] ← Redis Broker ← Flask 发布任务
```

## 组件

| 组件 | 技术 | 职责 |
|------|------|------|
| API 服务 | Flask + Flask-RESTX | RESTful 接口，Swagger UI |
| ORM 层 | SQLAlchemy + scoped_session | 数据库操作，会话管理 |
| 认证 | Flask-JWT-Extended | Token 颁发、刷新、验证 |
| 异步任务 | Celery + Redis | 定时任务、耗时计算 |
| 前端 | Vue 3 + Vite | SPA，组件化 UI |
| UI 框架 | Element Plus | 表单、表格、弹窗组件 |
| 状态管理 | Pinia | 全局状态（用户信息、Token） |

## 目录结构（规划中，由 dev 按需调整）

```
web-admin/
  backend/
    app/
      __init__.py          ← create_app() 工厂
      config.py            ← 环境配置
      extensions.py        ← db, jwt, celery 初始化
      models/              ← SQLAlchemy ORM 模型
      api/
        __init__.py        ← API Blueprint 注册
        auth/              ← 认证 Namespace
        users/             ← 用户管理 Namespace
        roles/             ← 角色管理 Namespace
        permissions/       ← 权限管理 Namespace
      tasks/               ← Celery 任务
    tests/                 ← pytest 测试
    requirements.txt
    celery_worker.py
  frontend/
    src/
      api/                 ← Axios 请求封装
      components/          ← 通用组件
      views/               ← 页面组件
      stores/              ← Pinia stores
      router/              ← Vue Router
      assets/              ← CSS tokens, 静态资源
    vite.config.js
```

## 数据流

**认证流程**：
1. 前端 POST /api/auth/login（username + password）
2. 后端验证 → 返回 access_token + refresh_token
3. 前端存储 token（Pinia store + localStorage）
4. 后续请求在 Header 中携带 Authorization: Bearer <token>
5. 后端 @jwt_required() 装饰器验证

**CRUD 流程**：
前端表格/表单 → Axios 调用 API → Flask Namespace → SQLAlchemy → MySQL

## 技术栈版本（由 backend-dev/frontend-dev 确认后更新）

| 技术 | 版本 | 备注 |
|------|------|------|
| Python | 3.11+ | |
| Flask | 3.x | |
| Flask-RESTX | 1.x | Swagger UI 自动生成 |
| SQLAlchemy | 2.x | scoped_session |
| Flask-JWT-Extended | 4.x | |
| Celery | 5.x | Redis broker |
| Node.js | 20+ | 前端构建 |
| Vue | 3.x | Composition API |
| Element Plus | 2.x | |
| Vite | 5.x | |
