# reviewer - 任务计划

> 角色: 代码审查工程师（只读源码）
> 状态: waiting（等待 dev 审查请求）
> 分配的任务: T4 — 待命，接受审查请求

## 任务

- [ ] T4: 待命，响应 backend-dev 和 frontend-dev 的审查请求
  - 收到请求后按审查流程执行
  - 对照 CLAUDE.md 中的 3 个审查维度评分（RD-1/RD-2/RD-3）
  - 完整报告写入 review-<target>/findings.md
  - 通知请求方 dev 和 team-lead

## 审查维度（来自 CLAUDE.md）

| # | 维度 | 权重 |
|---|------|------|
| RD-1 | API 设计一致性 | 高 |
| RD-2 | 安全性 | 高 |
| RD-3 | 测试覆盖 | 中 |

## 备注

- 只读源代码，不修改项目代码文件
- 可写 .plans/ 文件（审查报告、交叉引用）
- 审查时额外检查：api-contracts.md 是否同步更新（Doc-Code Sync）
