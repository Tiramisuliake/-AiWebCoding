# backend-dev - 任务计划

> 角色: 后端开发工程师
> 状态: blocked_by_T1（等待 researcher 完成 DB Schema 设计）
> 分配的任务: T2 — Flask-RESTX 项目初始化 + 认证模块

## 任务

- [ ] T2: 后端项目初始化 + 认证模块（解锁后执行）
  - [ ] 在 web-admin/backend/ 初始化项目（app factory 模式）
  - [ ] 配置 SQLAlchemy scoped_session 会话工厂
  - [ ] 配置 Flask-JWT-Extended
  - [ ] 创建 User/Role/Permission ORM 模型（依据 researcher 的 DB Schema）
  - [ ] 实现认证 Namespace：POST /api/auth/login, /logout, /refresh
  - [ ] TDD：先写 pytest 测试（RED），再实现（GREEN），重构（IMPROVE）
  - [ ] 覆盖率 ≥ 80%
  - [ ] 运行 scripts/run_ci.py，PASS 后请求 reviewer 审查

## 备注

- 工作目录：G:\py\aiweb\web-admin\backend\
- 依赖：.plans/web-admin/researcher/research-rbac/findings.md
- 技术栈：Flask + Flask-RESTX + SQLAlchemy(scoped_session) + Flask-JWT-Extended + Celery + pytest
- MySQL：localhost:3306, root/123456
- 统一响应格式：{"code": 0, "data": {}, "msg": "ok"}
