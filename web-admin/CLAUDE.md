# CLAUDE.md — web-admin 项目入口

前后端分离的企业级 RBAC 管理后台。详细规则在 `.claude/` 子目录，Git 完整规则在 `.codex/skills/git-workflow/SKILL.md`。

## 技术栈

| 层 | 技术 | 端口 |
|---|---|---|
| 后端 | Python 3 / Flask 3 / Flask-RESTX / SQLAlchemy / JWT / Celery | 5000 |
| 前端 | Vue 3 / Vite 6 / Pinia / Element Plus 2.9 / Axios | 5173 |
| DB | MySQL（生产）/ SQLite 内存（测试）| — |

## 快速启动

```powershell
# 后端
cd web-admin/backend; python run.py

# 首次初始化 DB
python scripts/seed.py --create-tables --password yourpassword

# 前端（Windows）
.\start-frontend.ps1
```

## 目录速查

```
backend/app/
  apis/           路由层（薄：输入校验 → service → ok()/fail()）
  service/        业务逻辑层（校验、事务、业务规则）
  database/
    entity/models.py     ORM 模型 + 关联表
    repository/          查询构建器
    conn/session.py      scoped session
  components/response.py ok() / fail()
  components/authz.py    @require_permission 装饰器
  conf/config.py         环境配置
  const/permissions.py   23 个内置权限码

frontend/src/
  api/            http.js + auth.js + rbac.js（所有后端请求走这里）
  stores/         auth / menu / tabs / locale
  router/index.js 路由守卫（RBAC + 认证）
  components/AppLayout.vue  壳层：侧边栏 + 标签页 + 内容区
  views/          6 页面：Login Dashboard Users Roles Permissions Menus
  i18n/messages.js zh-CN / en-US 文案
```

## .claude/ 文件索引

| 文件 | 内容 |
|---|---|
| `.claude/backend.md` | 后端分层规则、响应格式、JWT、新增功能步骤 |
| `.claude/frontend.md` | Vue 3 规范、Stores、路由守卫、Tab、i18n、新增功能步骤 |
| `.claude/data.md` | 数据模型、权限码规则、API 端点速查 |
| `.claude/workflow.md` | 系统不变量、文档同步触发规则 |

## 命令手册

| 命令 | 用途 |
|---|---|
| `/start` | 新会话快速定位 |
| `/dev` | 功能开发流程 |
| `/crud` | 新增 CRUD 模块 |
| `/check` | 运行代码检查 |
| `/pr` | 创建 PR 并同步双远端 |
| `/push` | 按双远端规则推送 |
| `/sync` | 同步项目文档 |
| `/next` | 建议下一项工作 |
| `/progress` | 项目进度报告 |
| `/update-status` | 更新项目状态 |
| `/add-todo` | 添加结构化待办 |
| `/publish` | 创建版本 tag 并双端发版 |
| `/init-docs` | 修复缺失文档骨架 |
