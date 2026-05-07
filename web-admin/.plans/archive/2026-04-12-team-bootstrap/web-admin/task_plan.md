# web-admin - 主计划

> 状态: PHASE_0 — 调研中
> 创建: 2026-04-12
> 更新: 2026-04-12
> 团队: web-admin（researcher, backend-dev, frontend-dev, reviewer）
> 决策记录: .plans/web-admin/decisions.md

---

## 1. 项目概述

通用 CRUD 管理后台，前后端分离。首期实现用户/角色/权限（RBAC）基础模块。
技术栈：Flask-RESTX + MySQL + SQLAlchemy + JWT（后端）/ Vue 3 + Element Plus（前端）

---

## 2. 文档索引

| 文档 | 位置 | 内容 |
|------|------|------|
| 架构 | docs/architecture.md | 系统组件、项目结构、数据流 |
| API 契约 | docs/api-contracts.md | 所有端点定义（字段、格式） |
| 不变量 | docs/invariants.md | 不可违反的系统边界 |
| 导航地图 | docs/index.md | 各文档 section 和行号范围 |

---

## 3. 阶段概览

### 阶段 0：调研与架构设计（当前）
- researcher：设计 RBAC DB Schema + API 契约初稿
- team-lead：确认架构方向，更新 docs/architecture.md 和 docs/api-contracts.md

### 阶段 1：后端核心开发
- backend-dev：项目初始化（app factory）+ 认证模块（JWT login/logout/refresh）
- backend-dev：用户/角色/权限 CRUD API
- 依赖：阶段 0 的 DB Schema 和 API 契约

### 阶段 2：前端开发（可与阶段 1 并行）
- frontend-dev：Vue 3 脚手架 + 设计系统（ui-ux-pro-max skill）
- frontend-dev：登录页 + 路由守卫 + 通用 Layout
- frontend-dev：用户/角色/权限管理页面

### 阶段 3：联调 + 代码审查
- reviewer：审查后端 API 安全性和代码质量
- reviewer：审查前端代码质量
- 全栈联调，修复集成问题

### 阶段 4：Celery 任务（阶段 3 完成后）
- backend-dev：Celery worker 配置（Redis broker）
- backend-dev：定时任务示例 + 耗时计算任务示例

---

## 4. 任务汇总

| # | 任务 | 负责人 | 状态 | 计划文件 |
|---|------|--------|------|----------|
| T1 | RBAC DB Schema + API 契约设计 | researcher | in_progress | .plans/web-admin/researcher/research-rbac/ |
| T2 | 后端项目初始化 + 认证模块 | backend-dev | blocked_by_T1 | .plans/web-admin/backend-dev/task-auth/ |
| T3 | 前端脚手架 + 登录页 | frontend-dev | in_progress | .plans/web-admin/frontend-dev/task-scaffold/ |
| T4 | 代码审查（待命） | reviewer | waiting | — |

---

## 5. 当前阶段

**阶段 0 进行中**：

- [x] 团队搭建完成
- [ ] researcher 完成 RBAC DB Schema + API 契约设计（T1）
- [ ] team-lead 确认架构方向，更新 docs/
- [ ] 解锁 T2（后端开发）

