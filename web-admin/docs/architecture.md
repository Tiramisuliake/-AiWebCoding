# 架构说明

## 总览

`web-admin` 是前后端分离的管理后台。

```text
Vue 3 SPA
  -> Axios + JWT
Flask-RESTX API under /api
  -> service layer
  -> repository layer
  -> SQLAlchemy ORM
  -> database

Flask app -> Celery -> Redis broker/result backend
```

## 后端结构

```text
backend/
  app/
    __init__.py              # create_app()
    apis/                    # Flask-RESTX namespaces
    service/                 # 业务逻辑
    database/
      entity/                # SQLAlchemy 模型与关联表
      repository/            # 查询与写入辅助函数
      conn/                  # engine/session 辅助逻辑
    components/              # 响应、权限、序列化、分页、本地化
    conf/                    # 配置和扩展初始化
    const/                   # 错误码与权限常量
    tasks/                   # Celery 任务
    utils/                   # 小型工具函数
  scripts/                   # 建表、seed、升级脚本
  tests/                     # pytest 测试
```

路由层负责 HTTP 输入输出转换。Service 层负责校验、事务和业务规则。Repository 层封装数据访问。Entity 层定义持久化结构。

## 前端结构

```text
frontend/src/
  api/                       # Axios client functions
  components/AppLayout.vue   # 认证后布局壳层、菜单、标签页
  router/index.js            # 路由与守卫
  stores/                    # auth、menu、tabs、locale
  views/                     # 管理页面
  i18n/messages.js           # zh-CN/en-US 文案
  assets/                    # 设计令牌和基础 CSS
```

前端壳层会在登录后加载用户菜单树，推导可访问路径，并阻止访问未授权路由。

## 主要数据流

### 登录

1. 前端向 `/api/auth/login` 提交账号密码。
2. 后端校验用户和密码哈希。
3. 后端返回 access token、refresh token 和用户摘要。
4. 前端存储 token，并加载 `/api/menus/my-tree`。
5. 路由守卫只允许访问菜单授权路径。

### 受保护 API 请求

1. Axios 注入 `Authorization: Bearer <access_token>`。
2. Flask-JWT-Extended 校验 token 和黑名单状态。
3. 路由权限装饰器检查 RBAC 权限。
4. Service 层完成校验和 repository 调用。
5. 响应用统一响应格式包装。

### 角色菜单与权限联动分配

1. 前端向 `/api/roles/{id}/menus` 提交 `menu_ids` 和可选 `permission_ids`。
2. 后端要求 `role:assign_menu`。
3. 如果提交了权限，还要求 `role:assign_permission`。
4. 后端校验权限是否在所选菜单可管辖范围内。
5. 菜单和权限在同一事务中更新。

## 配置

配置通过 `backend/app/conf/config.py` 加载。开发环境可以读取 `backend/.env` 或 `backend/.env.example`；生产环境必须通过环境变量提供必要密钥和数据库配置。
