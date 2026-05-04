# AGENTS.md — web-admin 项目协作规范

## 项目概述

`web-admin` 是一个前后端分离的 RBAC 管理后台项目，当前已具备可运行的认证、用户、角色、权限、菜单管理能力，而不是仅脚手架阶段。

- 后端提供 `/api/*` REST 接口（Flask-RESTX）。
- 前端是 Vue 3 SPA（Element Plus + Pinia + Vue Router）。
- RBAC 采用用户-角色-权限模型，并扩展了角色-菜单授权与“我的菜单树”接口。

> 上下文获取原则：每次任务应结合 `.plans/`、`CLAUDE.md` 和实际代码综合判断，不固定读取顺序；按任务相关性读取，避免机械化流程。

---

## 技术栈

### 后端

- Python + Flask 3.x
- Flask-RESTX（Namespace 路由 + `/api/docs`）
- SQLAlchemy 2.x（`scoped_session` 会话工厂）
- Flask-JWT-Extended（access/refresh token）
- Flask-Bcrypt（密码哈希）
- Flask-Cors
- Celery 5.x + Redis（任务队列）
- PyMySQL（MySQL 驱动）
- pytest（接口测试）

### 前端

- Vue 3 + Vite 6
- Element Plus
- Pinia
- Vue Router
- Axios
- 自建 i18n（`zh-CN` / `en-US`）

---

## 目录结构说明

```text
web-admin/
  AGENTS.md
  CLAUDE.md
  .plans/web-admin/              # 规划、上下文与团队日志（存在部分过期）
  scripts/                       # 项目级 CI 与黄金规则脚本
  backend/
    app/
      __init__.py                # create_app 工厂入口
      apis/                      # auth/users/roles/permissions/menus 路由
      service/                   # 业务服务层
      database/
        conn/                    # engine/session 管理
        entity/                  # SQLAlchemy 模型
        repository/              # 数据访问封装
      components/                # 响应、权限装饰器、序列化、分页等
      conf/                      # 配置与扩展初始化
      const/                     # 错误码、默认权限码
      tasks/                     # Celery 任务
      utils/                     # logger、参数解析
    scripts/                     # DB 初始化、seed、菜单功能升级
    tests/                       # pytest（当前含 auth + menu）
    run.py
    celery_worker.py
  frontend/
    src/
      api/                       # axios 封装与 RBAC API 客户端
      stores/                    # auth/menu/tabs/locale
      router/                    # 路由与守卫
      views/                     # Dashboard/Login/Users/Roles/Permissions/Menus
      components/                # AppLayout
      i18n/ + composables/
      assets/                    # design tokens + base.css
```

---

## 前端开发规范

- 统一使用 Vue 3 `script setup` + Composition API。
- 页面数据请求统一走 `src/api/http.js`（含 token 注入与 401 处理）。
- 认证状态统一在 `stores/auth.js`，菜单权限状态统一在 `stores/menu.js`。
- 新页面必须接入路由守卫逻辑：未登录跳转 `/login`，且受 `allowedPaths` 控制。
- 保持现有设计令牌体系（`assets/design-tokens.css`），不要绕过 token 写硬编码主题色。
- 文案必须同步 `i18n/messages.js` 中英双语。
- 新增后台页面优先接入 `AppLayout` 的 tab 体系（`meta.tab`, `meta.keepAlive`, `meta.titleKey`）。

---

## 后端开发规范

- 必须走 Application Factory（`app.create_app()`），不要创建全局裸 `Flask()` 应用。
- 配置来源统一走 `app/conf/config.py`（环境变量 + profile 覆盖）。
- 数据访问遵循分层：`apis -> service -> repository -> entity`。
- 所有 DB 操作通过 SQLAlchemy ORM，不写字符串拼接 SQL。
- 会话管理统一使用 `database/conn/session.py` 的 `scoped_session`，请求结束依赖 teardown 清理。
- 统一使用 `components/response.py` 返回格式，不要返回裸字典。
- 权限控制统一使用 `@jwt_required()` + `@require_permission("xxx:yyy")`。
- 业务异常统一抛 `ServiceError`，由路由层转换为响应。

---

## API 约定

- 基础前缀：`/api`
- 文档入口：`/api/docs`
- 已注册 Namespace：`auth`、`users`、`roles`、`permissions`、`menus`
- 统一响应：

```json
{
  "code": 0,
  "data": {},
  "msg": "ok"
}
```

- JWT：
  - 登录返回 `access_token` + `refresh_token`
  - 受保护接口传 `Authorization: Bearer <access_token>`
  - 刷新接口使用 refresh token
- 典型错误码：`1001/1002/1003/2001/2002/5001`

---

## RBAC 权限设计现状

当前代码已落地“RBAC + 菜单授权”：

- 用户-角色：`user_roles`
- 角色-权限：`role_permissions`
- 角色-菜单：`role_menus`
- 菜单实体：`menus`
- 令牌黑名单：`token_blocklist`

权限码不仅包含 `user:* / role:* / permission:*`，还包含 `menu:*` 和 `role:assign_menu`。  
`admin` 角色在权限判断中默认放行；菜单树会过滤不可见或禁用菜单。

---

## 菜单、用户、角色、权限模块说明

- 菜单管理：已实现菜单树查询、增删改、按角色分配菜单、按用户返回可访问菜单树（`/api/menus/my-tree`）。
- 用户管理：已实现用户 CRUD、分页/多条件搜索、用户角色分配与移除。
- 角色管理：已实现角色 CRUD、角色权限覆盖写分配、角色菜单分配。
- 权限管理：已实现权限列表与详情查询（支持可选分页与多字段筛选）。

---

## 权限模块中文主导规则

- 权限相关页面默认“中文优先展示”，权限码仅作为技术标识保留。
- 推荐展示格式：
  - 权限列表：中文权限名 + 独立权限码列。
  - 分配权限弹窗/标签：`中文权限名（权限码）`。
- 禁止在权限模块直接使用英文 `permission.name` 作为主展示文案（除映射缺失时的回退场景）。
- 新增系统内置权限码时，必须同步更新：
  - 后端 `BUILTIN_PERMISSION_LOCALIZATION_ZH`（权限中文名/描述映射）。
  - 前端 `i18n/messages.js` 的 `permissions.codeNames` 与 `permissions.codeDescriptions`。
- 默认启用后端启动同步：`PERMISSION_CN_SYNC_ON_STARTUP=true`，用于将内置权限 `name/description` 自动收敛为中文。

---

## 菜单模块中文主导规则

- 菜单相关页面与菜单树展示默认中文主导，禁止将英文菜单名作为默认展示文案。
- 内置菜单名称必须保持中文（如：`仪表盘`、`用户管理`、`角色管理`、`权限列表`、`菜单管理`、`权限管理`）。
- 默认启用菜单中文同步：`MENU_CN_SYNC_ON_STARTUP=true`，用于启动时收敛历史英文菜单名。
- 默认启用写入归一化：`MENU_CN_FORCE_ON_WRITE=true`，创建/编辑菜单英文名时自动转为中文优先格式。
- 新增菜单命名规则时，必须同步维护 `backend/app/components/menu_localization.py` 的词典与映射。

---

## 常用启动、测试、构建命令

以下命令默认在 `web-admin/` 目录执行。

### 后端

- 安装依赖：`pip install -r backend/requirements.txt`
- 启动 API：`python backend/run.py`
- 初始化数据库（按 ORM 建表）：`python backend/scripts/db_schema.py init-db`
- 写入 RBAC 基础数据：`python backend/scripts/seed.py --create-tables`
- 运行测试：`python -m pytest backend/tests -v`

### 前端

- 安装依赖：`npm --prefix frontend install`
- 启动开发：`npm --prefix frontend run dev`
- 构建：`npm --prefix frontend run build`
- 预览：`npm --prefix frontend run preview`

### 项目级检查

- 快速检查：`python scripts/run_ci.py --quick`
- 完整 CI：`python scripts/run_ci.py`

---

## 代码修改原则

- 优先修根因，不做表面 patch。
- 改动保持最小化，避免无关重构。
- 新增 API、数据结构或关键行为时，同步更新 `.plans/web-admin/docs/` 对应文档。
- 不要覆盖用户已有本地改动；若发现冲突改动，先确认再处理。
- 提交前至少运行与改动相关的最小测试，再扩展到 `scripts/run_ci.py`。

---

## 后续开发注意事项

当前 `.plans` / `CLAUDE.md` 与代码存在时间差，开发前必须先以代码为准核实：

1. `task_plan.md` 仍显示阶段 0 / 后端阻塞，但后端与前端核心模块已实际实现。  
2. `docs/architecture.md` 的目录示例仍是早期草案（与当前 `app/conf`, `app/apis`, `app/database` 不完全一致）。  
3. `docs/api-contracts.md` 未覆盖菜单相关 API，且部分查询参数描述落后于实际实现（实际支持更多筛选项与可选分页）。  
4. `research-rbac/findings.md` 是初版 5 表方案，代码已扩展到菜单与 token blocklist 相关表。  

结论：继续开发时，优先基于“当前代码行为 + 必要文档补齐”推进。

---

## 禁止事项

- 禁止在代码中硬编码密钥、数据库密码、token。
- 禁止绕过 service/repository 分层在路由中直接写复杂 DB 逻辑。
- 禁止破坏统一响应格式或错误码语义。
- 禁止未鉴权暴露受保护资源接口（除登录、健康检查等明确公开接口）。
- 禁止在未评估影响时随意改动权限码与菜单路由映射。
- 禁止只改代码不更新契约文档（当接口/架构发生变化时）。
