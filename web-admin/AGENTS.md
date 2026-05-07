# web-admin Agent 协作指南

## 项目现状

`web-admin` 是一个已经可运行的 Flask + Vue RBAC 管理后台。当前已经完成基础平台能力，可以开始真正的业务模块开发：

- 认证：登录、退出、刷新令牌、令牌黑名单。
- 用户：CRUD、分页、多字段搜索、角色分配。
- 角色：CRUD、权限分配、菜单分配、菜单与权限联动分配。
- 权限：列表/详情、中文优先展示规则。
- 菜单：树形 CRUD、角色菜单授权、`/api/menus/my-tree`、隐藏/禁用过滤。
- 前端壳层：登录、路由守卫、动态菜单访问、标签页持久化、可拖拽标签页。

下一阶段是基于这套 RBAC 基座开发业务功能，不是继续搭脚手架。

## 真理源顺序

当文档之间出现差异时，按以下顺序判断：

1. 当前代码行为。
2. `docs/project-state.md`。
3. `docs/api-contracts.md`。
4. `docs/architecture.md`。
5. `docs/decisions.md`。
6. `.plans/archive/` 历史材料。

不要把 `.plans/archive/` 当作当前项目状态。它只用于追溯历史上下文。

## 仓库地图

```text
web-admin/
  AGENTS.md                  # Agent 长期入口
  CLAUDE.md                  # 兼容指针文件
  commands/                  # 仓库内命令手册
  docs/                      # 当前项目文档真理源
  templates/                 # 业务与文档模板
  backend/                   # Flask-RESTX API
  frontend/                  # Vue 3 SPA
  scripts/                   # 项目检查脚本
```

修改某个子系统前，先读最近的 `AGENTS.md`：

- 后端任务：`backend/AGENTS.md`
- 前端任务：`frontend/AGENTS.md`
- 业务功能任务：`docs/business-module-guide.md`

## 常用命令

除特别说明外，默认在 `web-admin/` 下运行：

```powershell
python scripts/run_ci.py --quick
python scripts/run_ci.py
npm --prefix frontend run build
npm --prefix frontend run dev
python backend/run.py
python backend/scripts/db_schema.py init-db
python backend/scripts/seed.py --create-tables
```

后端测试需要在 `backend/` 目录运行：

```powershell
python -m pytest tests -v
```

## 开发规则

- 改动范围要贴合当前任务，避免无关重构。
- 新增或变更 API、数据结构、权限、菜单、关键行为时，必须同步更新 `docs/api-contracts.md`、`docs/rbac-and-menu.md` 或对应业务模块文档。
- 不要在源码中硬编码密钥、数据库密码、access token、refresh token。
- 不要绕过后端分层在路由里直接写复杂数据库逻辑。
- 不要破坏统一响应格式：

```json
{ "code": 0, "data": {}, "msg": "ok" }
```

- 除明确公开的接口外，不要暴露未鉴权资源。
- 不要在未同步后端常量、前端 i18n、seed/菜单初始化和文档的情况下改动权限码、菜单路由映射或本地化规则。

## Subagent 使用规则

Subagent 只用于独立、边界清晰、可以并行的任务。主 Agent 负责用户对齐、最终集成、冲突处理、验证和交付。

每个 Subagent 任务必须包含：

- 目标与验收标准。
- 需要读取的上下文文件。
- 允许修改的路径范围。
- 禁止修改的文件或区域。
- 必须运行的检查。
- 完成汇报要求：修改文件、测试结果、风险和开放问题。

Worker 不是独自在代码库里工作。必须保留无关改动，不得回滚他人的工作，并适配已有变更。

对于强耦合改动、阻塞主流程的工作，或下一步依赖结果的任务，优先由主 Agent 本地完成。

## 文档规则

- `docs/` 是当前活文档。
- `commands/` 存放可复用 Codex 工作流，如 `/start`、`/dev`、`/crud`、`/check`、`/sync`。
- `templates/` 存放业务模块、项目状态、待办、通用文档模板。
- `.plans/archive/` 是历史档案。只有追溯旧决策原因时才读取。

完成业务功能前，先运行与改动最相关的最小检查；如果改动影响共享契约，再扩大到完整检查。
