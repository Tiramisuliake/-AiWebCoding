# 项目状态

## 当前阶段

RBAC 基座已经完成。项目可以开始真正的业务模块开发。

## 已实现能力

- 后端 app factory、环境配置、SQLAlchemy scoped session、JWT、bcrypt、CORS、Celery 初始化。
- 认证 API：登录、退出、刷新令牌、令牌黑名单。
- 用户管理：CRUD、分页、关键词与多字段搜索、启用状态筛选、角色分配。
- 角色管理：CRUD、权限分配、菜单分配、菜单与权限联动分配。
- 权限管理：列表/详情、可选分页、多字段筛选。
- 菜单管理：树形 CRUD、路由映射、角色菜单授权、用户菜单树、隐藏/禁用过滤、循环数据安全处理。
- 权限和菜单中文优先本地化，以及启动同步开关。
- 前端登录、布局壳层、基于菜单的路由守卫、Pinia stores、标签页持久化、可拖拽标签页。

## 入口文件

- 后端 app：`backend/app/__init__.py`
- 后端启动脚本：`backend/run.py`
- API namespaces：`backend/app/apis/`
- ORM models：`backend/app/database/entity/models.py`
- 前端 app：`frontend/src/main.js`
- 前端 router：`frontend/src/router/index.js`
- 前端布局：`frontend/src/components/AppLayout.vue`
- 前端 API clients：`frontend/src/api/`

## 当前检查状态

2026-05-07 已知通过的验证：

- 在 `backend/` 下运行 `python -m pytest tests -v`：24 passed。
- 在 `web-admin/` 下运行 `npm --prefix frontend run build`：通过，仅保留既有 chunk-size 警告。

当前推荐命令：

```powershell
npm --prefix frontend run build
python scripts/run_ci.py
```

后端测试在 `web-admin/backend/` 下运行：

```powershell
python -m pytest tests -v
```

## 文档状态

- `docs/` 是当前活文档。
- `.plans/archive/` 只保留历史材料。
- `CLAUDE.md` 是兼容指针文件。
- `web-admin/` 外层 README 可能落后于当前文档。

## 下一步

使用 `docs/business-module-guide.md` 和 `templates/业务模块模板.md` 开始新增业务模块。每个模块在实现前应定义数据结构、API、权限、菜单入口、前端页面、测试和验收标准。
