# web-admin - 系统不变量

> 不可违反的系统边界。违反其中任何一条 = CRITICAL Bug。
> 每条不变量注明：能否自动化？当前状态（已有测试 / 无测试 / 人工检查）

## 安全边界

- INV-1: 所有非公开 API 端点必须通过 `@jwt_required()` 验证 — 状态：无测试
- INV-2: 密码必须使用 bcrypt 哈希存储，禁止明文存储 — 状态：无测试
- INV-3: JWT 密钥（JWT_SECRET_KEY）必须从环境变量读取，禁止硬编码 — 状态：golden_rules.py 扫描
- INV-4: 数据库连接字符串（包含密码）必须从环境变量读取 — 状态：golden_rules.py 扫描

## 数据隔离

- INV-5: 用户只能查看/修改自己有权限的资源（RBAC 检查） — 状态：无测试
- INV-6: 删除操作（用户/角色）必须检查关联数据，防止孤立记录 — 状态：无测试

## 接口契约

- INV-7: 所有 API 响应必须符合统一格式 `{"code": 0, "data": {}, "msg": "ok"}` — 状态：无测试
- INV-8: API 字段名必须与 api-contracts.md 中的定义一致 — 状态：人工检查

## 数据库

- INV-9: 所有数据库操作必须通过 SQLAlchemy ORM，禁止原始 SQL 字符串拼接 — 状态：golden_rules.py 可检测
- INV-10: 每个请求结束后必须正确关闭/归还 SQLAlchemy session — 状态：无测试
