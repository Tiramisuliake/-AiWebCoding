# A股/ETF 量化投研系统

基于 Python + AkShare 的 A股/ETF 量化投研系统，作为 web-admin 的子模块运行。

## 架构定位

- **web-admin 子模块**：共享 web_admin 数据库，复用 JWT/RBAC 做账号管理
- quant 表使用 `quant_` 前缀（如 `quant_daily_price`），与 web-admin 表共存
- **脚本独立运行**：数据采集、因子计算等脚本可直接 `python scripts/xxx.py`
- **API 端点**：后续加入 web-admin Flask 路由，走统一认证

## 技术栈

| 组件 | 技术 |
|---|---|
| 数据源 | AkShare（A股/ETF 日线、分钟级、实时行情） |
| ORM | SQLAlchemy 2.0（共享 web-admin 的 DeclarativeBase） |
| 数据库 | MySQL（与 web-admin 同库 web_admin） |
| 数据处理 | pandas |
| 实时推送 | websockets（WebSocket 服务） |
| 日志 | loguru |
| 配置 | python-dotenv（优先读 quant/.env，回退 web-admin/.env） |
| 报告 | openpyxl（Excel 输出） |

## 目录结构

```
quant/                          ← 与 web-admin/ 同级
├── config/settings.py          配置加载（共享 DB 连接）
├── db/
│   ├── base.py                 共享 web-admin 的 DeclarativeBase
│   ├── session.py              独立 engine（指向同库）
│   └── models.py               7 张 quant_ 前缀 ORM 表
├── collector/
│   ├── stock_collector.py      A股日线采集
│   ├── etf_collector.py        ETF日线采集
│   ├── minute_collector.py     分钟级数据采集
│   └── realtime.py             实时行情 WebSocket 推送
├── factor/
│   ├── registry.py             因子注册表
│   ├── basic_factors.py        基础因子（MA/收益率/波动率）
│   └── multi_factor.py         多因子选股模型
├── strategy/
│   ├── base.py                 策略基类
│   ├── ma_cross.py             MA均线交叉策略
│   └── multi_factor_strategy.py 多因子选股策略
├── backtest/engine.py          回测引擎
├── report/daily_report.py      每日报告（Excel + 日志）
├── utils/logger.py             loguru 统一配置
└── scripts/                    独立可运行脚本
    ├── init_db.py              建 quant_ 表 + 初始化资产池
    ├── collect_daily.py        日线采集
    ├── collect_minute.py       分钟级采集
    ├── compute_factors.py      因子计算
    ├── run_strategy.py         策略信号生成
    ├── run_multi_factor.py     多因子选股
    ├── run_backtest.py         回测
    ├── start_realtime.py       实时推送服务
    └── daily_pipeline.py       全流程一键运行
```

## 数据库（7 张表，quant_ 前缀）

| 表 | 用途 |
|---|---|
| `quant_daily_price` | 日线行情（OHLCV + 换手率） |
| `quant_minute_price` | 分钟级行情（1m/5m/15m/30m/60m） |
| `quant_asset_pool` | 资产池（股票/ETF 代码管理） |
| `quant_factor_value` | 基础因子值 |
| `quant_factor_score` | 多因子评分（标准化 + 加权合成） |
| `quant_trading_signal` | 交易信号（buy/sell/hold） |
| `quant_backtest_result` | 回测结果（收益率/回撤/夏普等） |

## 快速开始

```powershell
cd G:\py\aiweb\quant

# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置（如果 web-admin/.env 已有 DATABASE_URL 可跳过）
copy .env.example .env
# 编辑 .env 中的 QUANT_DB_URI

# 3. 建表（仅建 quant_ 前缀表，不影响 web-admin 表）
python scripts/init_db.py

# 4. 采集数据
python scripts/collect_daily.py

# 5. 全流程运行
python scripts/daily_pipeline.py
```

## 开发阶段

| 阶段 | 内容 | 状态 |
|---|---|---|
| 1 | 基础设施 + 日线数据采集 | 进行中 |
| 2 | 因子计算 + MA交叉信号 | 待开发 |
| 3 | 回测引擎 | 待开发 |
| 4 | 报告 + 全流程编排 | 待开发 |
| 5 | 分钟级数据 + 实时行情推送 | 待开发 |
| 6 | 多因子选股模型 | 待开发 |

## 与 web-admin 的集成

```
web-admin/backend/app/
  apis/quant.py              ← 后续新增：Flask-RESTX 路由
  service/quant_service.py   ← 后续新增：调用 quant/ 的业务逻辑
```

quant API 端点将使用 web-admin 的 `@jwt_required()` 和 `@require_permission()` 装饰器，
实现账号管理和权限控制。
