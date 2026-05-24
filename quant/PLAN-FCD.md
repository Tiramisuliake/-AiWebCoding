# quant 阶段 F-C-D 实施计划

> 目标：先验证全链路可跑（F），再扩充标的池（C），最后做因子有效性分析（D）。
> 总体不引入新数据库表（D 阶段除外），不破坏现有 API。

---

## 阶段 F：跑通全流程验证（小工作量）

**目标**：用真实环境跑一遍 `init_db → collect_daily → daily_pipeline`，暴露并修复隐藏 bug。

### F.1 环境准备

| 项 | 内容 |
|---|---|
| `.env` | 复制 `quant/.env.example` → `quant/.env`，填入 `QUANT_DB_URI`（指向 web_admin 库） |
| 依赖 | `pip install -r quant/requirements.txt` |
| 数据库 | 确认 MySQL 运行，web_admin 库存在 |

### F.2 执行顺序 + 验证清单

```
1. python scripts/init_db.py
   验证：MySQL 中出现 7 张 quant_* 表，asset_pool 有 15 条
2. python scripts/collect_daily.py --start-date 20240101
   验证：daily_price 行数 ≈ 15 × 300+ 个交易日，无大量 ERROR
3. python scripts/compute_factors.py
   验证：factor_value 行数 ≈ 15 × 300 × 18 个因子
4. python scripts/run_strategy.py --all-strategies
   验证：trading_signal 至少有 buy/sell 各几条
5. python scripts/run_multi_factor.py --days 5
   验证：factor_score 有数据，multi_factor 信号 ≈ 20 × 5
6. python scripts/run_backtest.py
   验证：backtest_result 每策略 × 每标的一条，指标合理
7. python scripts/daily_pipeline.py
   验证：output/ 目录生成 signals_*.xlsx 和 backtest_*.xlsx
```

### F.3 已知风险点（先准备应对方案）

| 风险 | 表现 | 修复 |
|---|---|---|
| AkShare 列名变动 | `KeyError: '日期'` | 在 collector 加列名容错（'日期'/'date'/'trade_date'） |
| MinutePrice 表 SQLAlchemy 字段未指定类型 | 建表报错 | 显式加 `Numeric(12,4)` |
| `daily_pipeline.py` 引用 `assets` 跨 try 作用域 | NameError | 把 assets 加载提到顶部 |
| AkShare 限流封 IP | 连续 timeout | 已有 `sleep(1)`，必要时调到 2-3 秒 |
| 中文列名 pandas 切片 | 个别 ETF 字段缺失（如换手率） | 已用 `pd.notna(row.get("换手率"))` 兜底 |

### F.4 交付物

- `quant/FCD-F-RESULT.md`：跑通报告（每步耗时、数据量、遇到的 bug）
- 修复任何 bug 的 commit

---

## 阶段 C：资产池扩展（小工作量）

**目标**：从硬编码 15 支扩展到全市场（A 股 5000+、ETF 800+），加行业/概念分类。

### C.1 数据源

| 用途 | AkShare API | 字段 |
|---|---|---|
| 全 A 股清单 | `ak.stock_info_a_code_name()` | code, name |
| 全 ETF 清单 | `ak.fund_etf_category_sina(symbol="ETF基金")` | symbol, name |
| 行业分类 | `ak.stock_board_industry_name_em()` + `ak.stock_board_industry_cons_em(symbol=...)` | 行业名 → 成分股 |
| 概念分类 | `ak.stock_board_concept_name_em()` + `ak.stock_board_concept_cons_em(symbol=...)` | 概念名 → 成分股 |

### C.2 数据库改动（加 2 张表）

```python
# 新增 AssetCategory：行业/概念分类
quant_asset_category
  id, board_type (industry/concept), board_name, code, created_at
  UNIQUE(board_type, board_name, code)
  INDEX(code), INDEX(board_name)
```

`AssetPool` 表加列：

```python
exchange: VARCHAR(10)    # SH / SZ / BJ
list_date: DATE NULL     # 上市日期（已知则填）
delisted: BOOLEAN = FALSE  # 退市标记
```

### C.3 新增脚本

| 文件 | 功能 |
|---|---|
| `scripts/sync_asset_pool.py` | 拉全市场清单写入 asset_pool（增量 upsert，已存在的更新 name/exchange） |
| `scripts/sync_categories.py` | 拉行业 + 概念，写入 asset_category |
| `collector/pool_sync.py` | 上述脚本的核心逻辑（被脚本调用） |

### C.4 资产池筛选机制

新增 `quant_asset_pool.tags` JSON 字段或 `is_active` 配合 `--filter` 命令行：

```powershell
# 默认 is_active = True 才参与采集
python scripts/sync_asset_pool.py            # 全量同步，但全部默认 is_active=False
python scripts/activate_pool.py --board "白酒"  # 激活某个板块的标的
python scripts/activate_pool.py --top-mv 300   # 激活市值前 300（需先采市值）
```

不强制做"启用全部 5000 支"，因为采集量太大（5000 × 1 秒 = 1.4 小时/天）。

### C.5 工作量分解

1. 新增 `AssetCategory` 模型 + 修改 `AssetPool`（加 3 列）→ migration 脚本
2. `collector/pool_sync.py`（核心逻辑，~150 行）
3. 两个入口脚本（每个 ~40 行）
4. `activate_pool.py`（资产池筛选启用工具）

### C.6 交付物

- 沪市/深市/北交所 5000+ A 股、800+ ETF 入库
- 80+ 行业、500+ 概念分类入库
- 仍保留 15 支初始激活清单，全量同步默认不激活

---

## 阶段 D：因子有效性分析（中工作量）

**目标**：用 IC/IR + 分层回测评估每个因子是否真的有预测力。

### D.1 核心概念

| 指标 | 公式 | 解读 |
|---|---|---|
| **IC**（Information Coefficient） | 当日因子值 vs 未来 N 日收益的 Spearman 相关 | \|IC\| > 0.03 视为有效 |
| **IR**（Information Ratio） | IC 均值 / IC 标准差 | IR > 0.5 视为稳定 |
| **IC 胜率** | IC > 0 的日期占比 | > 55% 视为方向一致 |
| **分层回测** | 因子值分 5 组，看 Top vs Bottom 组的收益差 | 多空收益单调 = 有效 |

### D.2 新增数据库表

```python
quant_factor_ic
  id, factor_name, eval_date, horizon (5/10/20 日)
  ic, ic_rank (Spearman/Pearson 取其一)
  sample_size  # 当日有效样本数
  UNIQUE(factor_name, eval_date, horizon)

quant_factor_evaluation
  id, factor_name, period_start, period_end, horizon
  ic_mean, ic_std, ir, ic_positive_rate
  top_return, bottom_return, long_short_return  # 分层回测结果
  group_returns_json  # 5 组各自收益 JSON
  created_at
  UNIQUE(factor_name, period_start, period_end, horizon)
```

### D.3 新增模块结构

```
quant/
├── analysis/
│   ├── __init__.py
│   ├── ic.py              # 计算日度 IC（compute_daily_ic）
│   ├── layered.py         # 分层回测（layered_backtest）
│   └── evaluator.py       # 综合评估（FactorEvaluator）
└── scripts/
    ├── compute_factor_ic.py     # 日度 IC 计算入口
    └── evaluate_factors.py      # 区间评估入口（生成排行报告）
```

### D.4 关键实现

**`analysis/ic.py`**
```python
def compute_daily_ic(factor_name, eval_date, horizon=20):
    """
    1. 取 eval_date 当日所有标的的 factor_value
    2. 取 eval_date+horizon 日的收益率（close_(t+H) / close_t - 1）
    3. Spearman 相关系数 = IC
    4. 写入 factor_ic 表
    """
```

**`analysis/layered.py`**
```python
def layered_backtest(factor_name, start, end, n_groups=5, horizon=20):
    """
    每个 rebalance 日：
    1. 按因子值排序，等分 N 组
    2. 计算各组未来 horizon 日的等权平均收益
    3. 多空组合收益 = top - bottom
    返回：各组累计净值曲线、多空净值、收益差
    """
```

**`analysis/evaluator.py`**
```python
class FactorEvaluator:
    def evaluate(factor_name, start, end, horizons=[5,10,20]):
        """综合输出 IC/IR/胜率/分层收益，写入 factor_evaluation"""
```

### D.5 报告输出

新增 `report/factor_report.py`：
- 因子有效性排行榜 Excel（按 IR 降序）
- 每个因子的 IC 时序图（matplotlib，输出 PNG，可选）
- 分层回测净值曲线图（matplotlib，输出 PNG，可选）

### D.6 用法

```powershell
# 计算单个日期的因子 IC
python scripts/compute_factor_ic.py --date 20260524

# 评估近 6 个月所有因子
python scripts/evaluate_factors.py --start 20251125 --end 20260524 --horizons 5,10,20

# 输出报告
# → output/factor_evaluation_20260524.xlsx
# → output/factor_ic_curves/*.png（可选）
```

### D.7 改进多因子选股

D 阶段产出可反哺阶段 6 的 `multi_factor.py`：

- `MULTI_FACTOR_WEIGHTS` 从配置硬编码 → 按 IR 自动加权（IR 高的因子权重大）
- 剔除 \|IC\| < 0.02 或 IR < 0.3 的无效因子
- 新增 `scripts/auto_tune_weights.py`：根据评估结果自动写回权重配置

---

## 总体时间线

| 阶段 | 文件数 | 代码量 | 数据库改动 |
|---|---|---|---|
| F | 0-3（仅修 bug） | < 50 行 | 无 |
| C | 5-6 个新文件 | ~400 行 | 加 1 表 + 改 1 表 |
| D | 8-10 个新文件 | ~700 行 | 加 2 表 |

预计每阶段独立完成后发版：v2.2.0（F + C）、v2.3.0（D）。

---

## 验收清单

### F 完成标志
- [ ] 7 个脚本无报错跑完
- [ ] 各表数据量在预期范围
- [ ] output/ 有 Excel 报告

### C 完成标志
- [ ] asset_pool 含 5000+ A 股记录
- [ ] asset_category 含行业 + 概念分类
- [ ] `activate_pool.py --board "白酒"` 能激活白酒板块

### D 完成标志
- [ ] 18 个因子都有 IC/IR 评分
- [ ] 因子排行榜可在 Excel 中查看
- [ ] 多因子选股权重可基于评估结果自动调整

---

## 不在 F-C-D 范围内（推迟到后续）

- ❌ Web 集成（API + 前端页面）
- ❌ 实盘交易、券商对接
- ❌ 机器学习因子
- ❌ 高频/Tick 级数据
- ❌ 风控止损
- ❌ 调度自动化（cron/任务计划器）
