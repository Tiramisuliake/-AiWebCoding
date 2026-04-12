# web-admin - 架构决策记录

> 记录每个决策及其理由。

---

## D1: Flask-RESTX 替代 Flask-RESTful

- 日期: 2026-04-12
- 决策: 使用 Flask-RESTX 而非 Flask-RESTful
- 理由: Flask-RESTX 自动生成 Swagger UI（/api/docs），Namespace 路由组织更清晰，内置 @api.expect() 校验和 api.model() 序列化，减少样板代码
- 考虑过的替代方案: Flask-RESTful（功能较少，无 Swagger）、FastAPI（需要切换语言生态）

## D2: SQLAlchemy scoped_session 会话工厂

- 日期: 2026-04-12
- 决策: 使用 scoped_session 而非直接使用 db.session
- 理由: scoped_session 按线程/请求隔离会话，避免多请求共享同一 session 导致的状态污染；更适合 Flask 多线程部署场景
- 考虑过的替代方案: Flask-SQLAlchemy 内置 db.session（在多线程场景下需要额外配置）

## D3: Application Factory 模式

- 日期: 2026-04-12
- 决策: 使用 create_app() 工厂函数初始化 Flask 应用
- 理由: 支持不同环境配置（dev/test/prod），方便 pytest 创建测试实例，避免循环导入
- 考虑过的替代方案: 直接 app = Flask(__name__)（不便于测试和多环境）

## D4: 统一响应格式

- 日期: 2026-04-12
- 决策: 所有 API 响应格式统一为 `{"code": 0, "data": {}, "msg": "ok"}`
- 理由: 前端可统一处理响应，code=0 表示成功，非 0 为业务错误码，与 HTTP 状态码配合使用
- 考虑过的替代方案: 直接返回裸数据（前端处理复杂），JSend 格式（不够简洁）
