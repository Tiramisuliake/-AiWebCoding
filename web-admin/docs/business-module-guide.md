# 业务模块开发指南

本指南用于在 RBAC 基座之上新增真实业务模块。

## 模块定义

实现前先定义：

- 模块名称与用户目标。
- 数据实体和关键字段。
- 列表筛选与排序需求。
- 详情、新建、编辑、删除流程。
- 权限码。
- 菜单入口和路由路径。
- 后端 API。
- 前端页面和路由 metadata。
- 测试与验收标准。

从 `templates/业务模块模板.md` 开始编写模块文档。

## 后端模式

默认 CRUD 模块沿用现有 RBAC 分层：

- ORM 实体放在 `backend/app/database/entity/`。
- Repository 辅助函数放在 `backend/app/database/repository/`。
- Service 函数放在 `backend/app/service/`。
- 路由放在 `backend/app/apis/`。
- 权限检查使用 `@jwt_required()` 和 `@require_permission()`。
- 响应通过 `ok()` 和 `fail()` 返回。

测试至少覆盖：

- 未带 token。
- 缺少权限。
- 列表与筛选。
- 新建/更新校验。
- 删除行为和关联约束。
- 统一响应格式。

## 前端模式

默认管理页面沿用 Users/Roles/Menus 的模式：

- API 函数放在 `frontend/src/api/`。
- 路由作为 `AppLayout` 子路由。
- 页面放在 `frontend/src/views/`。
- 只有跨页面共享状态时才新增 Pinia store。
- 中英文文案都写入 i18n。
- 需要进入标签页体系的页面配置 `meta.tab`、`meta.keepAlive`、`meta.titleKey`。

页面必须明确 loading、empty、validation、success、failure 状态。

## 权限与菜单模式

如果模块名为 `order`，默认权限码为：

- `order:list`
- `order:read`
- `order:create`
- `order:update`
- `order:delete`

只有业务流程确实需要时，才增加模块专用动作权限。

新增权限或菜单时，同步更新后端常量、前端 i18n、seed/菜单初始化、`docs/rbac-and-menu.md` 和模块文档。

## 验收清单

业务模块达到以下条件后才算完成：

- API 契约已记录。
- 权限码已记录并完成 seed。
- 授权用户可以看到菜单并访问页面。
- 未授权用户不能访问路由或 API。
- 后端测试通过。
- 前端构建通过。
- 用户可见行为变化时，在 `docs/acceptance/` 下记录人工验收结果。
