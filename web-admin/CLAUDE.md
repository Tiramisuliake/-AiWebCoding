# web-admin - 团队运营手册

> 由 CCteam-creator-cn 自动生成。
> 此文件让 team-lead 的团队知识在上下文压缩后仍然保持。

## Team-Lead 控制平面

- team-lead = 主对话，不是生成的 agent
- team-lead 负责用户对齐、范围控制、任务分解和阶段推进
- team-lead 维护项目全局文件：主 `task_plan.md`、`decisions.md` 和此 `CLAUDE.md`
- **前端技能约束**：所有前端设计与实现任务默认使用 `ui-ux-pro-max` skill，不再使用其他 UI skill
- **禁用独立子智能体**：团队存在后，所有工作通过 SendMessage 交给队友。不要启动独立的 Agent/子智能体（Explore、general-purpose 等）——唯一例外：用 `team_name` 生成新队友加入团队

## 团队花名册

| 名称 | 角色 | 模型 | 核心能力 |
|------|------|------|---------|
| researcher | 探索/研究 | sonnet | DB Schema 设计、API 规划、代码搜索（只读不改代码） |
| backend-dev | 后端开发 | sonnet | Flask-RESTX + SQLAlchemy + JWT + Celery + pytest |
| frontend-dev | 前端开发 | sonnet | Vue 3 + Element Plus + ui-ux-pro-max skill |
| reviewer | 代码审查 | sonnet | 安全/质量/API 一致性审查（只读源码） |

## 技术栈

```
后端：Flask + Flask-RESTX + MySQL(localhost:3306, root/123456)
     + SQLAlchemy(scoped_session 会话工厂)
     + Flask-JWT-Extended + Celery + pytest

前端：Vue 3 + Element Plus + Vite + Pinia + Vue Router + Axios
     （ui-ux-pro-max skill 提供设计系统）

Celery：定时任务 + 耗时计算（Redis 作为 broker）
```

## 任务下发协议

### TaskCreate 描述格式
一句话范围 + 验收标准 + .plans/ 路径
示例：`"实现用户认证模块。输入：researcher 的 DB Schema。输出：可用的登录/注销 API + pytest 测试。详见 .plans/web-admin/backend-dev/task-auth/task_plan.md"`

### 大任务（功能开发）——发送前检查 4 项

**在给任何 agent 下发大任务前，检查消息中是否包含以下 4 项：**

1. **范围和目标**：要做什么、验收标准
2. **文档提醒**："请创建 `<前缀>-<任务名>/` 任务文件夹（含 task_plan.md + findings.md + progress.md），并在你的根 findings.md 中添加索引条目"
3. **依赖说明**：依赖哪些调研/任务的结论，关键文件路径
4. **审查预期**：完成后是否需要 reviewer 审查

### 各角色任务文件夹前缀
- researcher：`research-<主题>/`
- backend-dev / frontend-dev：`task-<名称>/`
- reviewer：`review-<目标>/`

### 小任务（Bug 修复、配置变更）
直接 SendMessage 说明改动，不需要任务文件夹，也不需要审查。

## 通信速查

| 操作 | 命令 |
|------|------|
| 给单个 agent 分配任务 | `SendMessage(to: "<名称>", message: "...")` |
| 广播（慎用） | `SendMessage(to: "*", message: "...")` |
| dev 请求代码审查 | dev 直接联系 reviewer（不经过 team-lead） |

## 状态检查

| 要检查什么 | 怎么做 |
|-----------|--------|
| 全局概览 | `TaskList` — 所有任务、负责人、阻塞情况 |
| 快速扫描 | 并行读各 agent 的 `progress.md` |
| 深入了解 | 读 agent 的 `findings.md`（索引）→ 再看具体任务文件夹 |
| 方向检查 | 读 `.plans/web-admin/task_plan.md` |
| 恢复项目 | 读 `.plans/web-admin/team-snapshot.md` → 从缓存 prompt 启动 agent |

读取顺序：**progress**（到哪了）→ **findings**（遇到什么）→ **task_plan**（目标是什么）

## 文档索引（知识库）

> **导航地图**：`.plans/web-admin/docs/index.md` 有各文档的 section 级导航（含行号范围）。
> 需要在 docs/ 中查找信息时先 Read 它。

| 文档 | 位置 | 维护者 |
|------|------|--------|
| 导航地图 | .plans/web-admin/docs/index.md | team-lead/reviewer |
| 架构 | .plans/web-admin/docs/architecture.md | team-lead, devs |
| API 契约 | .plans/web-admin/docs/api-contracts.md | devs（API 变更时**必须**同步） |
| 不变量 | .plans/web-admin/docs/invariants.md | team-lead, reviewer |

**Doc-Code Sync 规则**：当代码变更了 API 或架构时，对应的 docs/ 文件**必须**在同一个任务中同步更新。

## 自动化检查

| 检查 | 脚本 | 执行什么 |
|------|------|---------|
| 黄金原则 | scripts/golden_rules.py | 文件大小、密钥、console.log、文档新鲜度、不变量覆盖 |
| CI | scripts/run_ci.py | 黄金原则 + pytest（后端）|

## 审查维度

| # | 维度 | 权重 | STRONG 表现 | WEAK 表现 |
|---|------|------|------------|---------|
| RD-1 | API 设计一致性 | 高 | RESTful 规范，统一响应格式 `{"code":0,"data":{},"msg":"ok"}`，端点风格一致，Namespace 清晰 | 端点命名随意，响应格式不统一，有的返回裸数据有的返回包装格式 |
| RD-2 | 安全性 | 高 | JWT 覆盖所有受保护路由，无 SQL 注入风险，无硬编码密钥，输入校验完整 | 有路由未做 JWT 验证，存在硬编码密钥或直接 SQL 字符串拼接 |
| RD-3 | 测试覆盖 | 中 | pytest 覆盖率 ≥ 80%，核心 API（认证、CRUD）有集成测试，边界条件覆盖 | 只有简单单元测试，核心 API 无测试，只测开心路径 |

## 核心协议

| 协议 | 触发时机 | 操作 |
|------|---------|------|
| 需求对齐 | 开发前 | researcher 先出 DB Schema + API 契约，team-lead 确认后再开发 |
| 代码审查 | 大功能/新模块完成 | dev 在 findings.md 写改动摘要 + 文件路径，SendMessage 给 reviewer |
| CI 门禁 | 任何代码变更后 | 运行 `python scripts/run_ci.py`，PASS 后才能提交 reviewer |
| 3-Strike 上报 | agent 报告 3 次失败 | 读其 progress.md，给新方向或重新分配 |
| 阶段推进 | 阶段完成 | 调研完：读 researcher findings 更新主计划；开发完：等 reviewer [OK]/[WARN] |
| 上下文溢出 | agent 报告上下文过长 | 进度已存文件，恢复或生成继任者 |

## Known Pitfalls

（初始为空，从 3-Strike 解决方案和 reviewer [BLOCK] 修复中积累）

## 风格决策

| # | 决策 | 来源 | 状态 |
|---|------|------|------|
| SD-1 | 后端统一响应格式：`{"code": 0, "data": {}, "msg": "ok"}` | 架构设计 Session 1 | Manual |
| SD-2 | SQLAlchemy 使用 `scoped_session` 会话工厂，不直接用 `db.session` | 架构设计 Session 1 | Manual |
| SD-3 | Flask app 使用 Application Factory 模式（`create_app()`） | 架构设计 Session 1 | Manual |

## 文件结构

```
G:\py\aiweb\web-admin\
  CLAUDE.md                   ← 此文件
  scripts/
    golden_rules.py           ← 通用代码质量检查
    run_ci.py                 ← CI 脚本（黄金原则 + pytest）
  backend/                    ← backend-dev 创建
  frontend/                   ← frontend-dev 创建
  .plans/web-admin/
    task_plan.md              ← 主计划导航图
    team-snapshot.md          ← 缓存入职 prompts（压缩后恢复用）
    findings.md / progress.md / decisions.md
    docs/
      index.md / architecture.md / api-contracts.md / invariants.md
    researcher/
      task_plan.md / findings.md / progress.md
      research-rbac/          ← 首期调研任务文件夹
    backend-dev/
      task_plan.md / findings.md / progress.md
    frontend-dev/
      task_plan.md / findings.md / progress.md
    reviewer/
      task_plan.md / findings.md / progress.md
```

