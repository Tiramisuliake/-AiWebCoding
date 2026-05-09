# 决策记录

## D1：使用 Flask-RESTX

- 日期：2026-04-12
- 决策：使用 Flask-RESTX 组织 REST API namespaces 和 Swagger UI。
- 理由：Namespace 与自动生成的 `/api/docs` 适合当前管理后台 API，可减少样板代码。

## D2：使用 SQLAlchemy Scoped Sessions

- 日期：2026-04-12
- 决策：使用配置好的 scoped session，不使用临时全局 session。
- 理由：请求/线程隔离与可预测清理对 Flask 部署和测试都很重要。

## D3：使用 Application Factory

- 日期：2026-04-12
- 决策：通过 `create_app()` 初始化 Flask 应用。
- 理由：支持 development/testing/production 配置，并避免脆弱的全局 app 初始化。

## D4：使用统一 API 响应

- 日期：2026-04-12
- 决策：API 响应统一包装为 `{"code": 0, "data": {}, "msg": "ok"}`。
- 理由：前端可以在不同模块之间一致处理业务状态。

## D5：使用仓库内命令手册

- 日期：2026-05-07
- 决策：将命令工作流放在 `.codex/commands/*.md`。
- 理由：这种手册不依赖特定客户端，任何 Codex 窗口都可以读取。

## D6：归档旧计划状态

- 日期：2026-05-07
- 决策：把旧生成式计划文件保留在 `.plans/archive/`。
- 理由：保留历史上下文，同时避免干扰当前开发。
