# web-admin - 知识库索引

> 动态导航地图。team-lead/reviewer 维护此文件。
> 智能体：需要在 docs/ 中查找信息时先 Read 此文件。

| 文档 | 关键 Sections | 最后更新 |
|------|-------------|---------|
| architecture.md | §系统概览 (L1-20): 组件图 · §组件 (L22-40): 技术职责 · §目录结构 (L42-70): 文件布局 · §数据流 (L72-90): 认证+CRUD流程 | 2026-04-12 |
| api-contracts.md | §统一响应格式 (L1-20): 格式规范 · §Auth API (L22-60): login/logout/refresh | 2026-04-12 |
| invariants.md | §安全边界 (L1-15): JWT+密码+密钥 · §数据隔离 (L17-22): RBAC · §接口契约 (L24-28): 响应格式 · §数据库 (L30-35): ORM规范 | 2026-04-12 |

## 如何使用此索引

- 需要了解系统组件？→ 读 architecture.md §系统概览
- 需要 API 字段名？→ 读 api-contracts.md，跳到相关 section
- 检查变更是否违反边界？→ 读 invariants.md
- 查找目录结构？→ 读 architecture.md §目录结构

## 新鲜度日志

| 文档 | 上次审计 | 状态 |
|------|---------|------|
| architecture.md | 2026-04-12 | [OK] 初始版本 |
| api-contracts.md | 2026-04-12 | [OK] 初始框架（Auth 部分已填，Users/Roles/Permissions 待 researcher T1 完成后补充）|
| invariants.md | 2026-04-12 | [OK] 初始版本 |
