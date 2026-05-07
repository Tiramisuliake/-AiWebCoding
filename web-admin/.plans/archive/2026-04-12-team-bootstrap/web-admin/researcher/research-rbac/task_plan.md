# research-rbac - 任务计划

> 任务：T1 — RBAC DB Schema + API 契约设计
> 状态：in_progress
> 创建时间：2026-04-12

## 目标

为 web-admin 通用 CRUD 管理系统首期模块（用户/角色/权限）设计：
1. MySQL 数据库表结构（RBAC 模型）
2. Flask-RESTX Namespace 风格的 API 端点契约

## 步骤清单

- [x] 创建任务文件夹
- [x] 读取架构文档（architecture.md / invariants.md）
- [x] 读取 API 契约框架（api-contracts.md）
- [ ] 研究 RBAC 最佳实践
- [ ] 设计 DB Schema（5 张表）
- [ ] 设计 API 端点列表（auth/users/roles/permissions）
- [ ] 输出完整结论到 findings.md
- [ ] 更新 docs/api-contracts.md
- [ ] 更新根 findings.md 索引
- [ ] SendMessage 汇报 team-lead

## 约束来源

- INV-1: 所有非公开 API 必须 @jwt_required()
- INV-2: 密码 bcrypt 哈希存储
- INV-5: RBAC 权限检查
- INV-6: 删除需检查关联数据
- INV-7: 统一响应格式 {"code": 0, "data": {}, "msg": "ok"}
- SD-2: SQLAlchemy scoped_session
