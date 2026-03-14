---
name: tire-sales-analyst
version: 2.3.0
description: "轮胎销售数据分析技能 v2.3.0 - 模块化重构版。支持数据库加速、标准分析流程、实战案例、进阶分析工具、数据可视化、安全加固和实用工具。"
author: ZZH-EC
---

# 🛞 轮胎销售数据分析技能 (v2.3.0)

> 专门用于分析米其林轮胎销售数据，支持多维度分析
> 版本：2026-03-14 | 作者：ZZH-EC

---

## 📦 核心功能

### 1. 数据库加速

#### 自动化数据更新
- **每日凌晨3点同步**：通过cron自动执行 `build_database.py`
- **增量更新**：仅更新有变化的数据文件
- **手动触发**：
  ```bash
  python3 build_database.py --force  # 强制重建
  python3 build_database.py --check   # 检查状态
  ```

#### SQLite性能优化
- **查询提速300%**：相比Excel直接读取
- **索引优化**：自动创建关键字段索引
  - `ID_Month_Key`, `Dealer_ID`, `CAI`, `Geobox`, `Program_Type`
- **内存映射**：支持大数据集快速查询

#### 数据统计概览表

| 数据类型 | 行数 | 更新频率 |
|---------|------|---------|
| 销售数据 | ~79,402行 | 每日 |
| SNX数据 | ~57,736行 | 每日 |
| 价格数据 | ~15,988行 | 每日 |
| 产品分类 | ~3,390行 | 每周 |
| 客户名单 | ~4,592行 | 每月 |

**数据库位置**：
```
~/.openclaw/workspace/tire-analyst/skills/tire-sales-analyst/sales_analysis.db
```

---

### 2. 标准分析流程

#### 规格维度分析（销量/SNX/价格三维度）

**分析顺序**：
1. 筛选目标规格（如18寸 → `Geobox LIKE '%R18'`）
2. 按渠道汇总销量
3. 关联SNX数据验证终端需求
4. 关联价格数据计算毛利空间

**核心指标**：
- 销量 = 渠道出货数量
- SNX = 终端车主注册（真实零售）
- 价格 = RTM零售商进货底价

#### CAI产品诊断（TOP10排名与下滑分析）

**分析模板**：
```markdown
### 下滑CAI诊断

| CAI | 产品描述 | 销量变化 | SNX变化 | 价格变化 | 诊断结论 |
|-----|---------|----------|---------|---------|---------|
| 273 | 235/60 R18 PRIMACY SUV+ | -461 | +95 | 0% | 渠道库存调整 |
```

**关键判断**：
- 销量↓ + SNX↑ = 渠道消化库存（正常）
- 销量↓ + SNX↓ = 终端需求下降（需关注）
- 销量↑ + SNX↑ = 正常增长

#### 渠道交叉验证（零售/批发渠道分离）

**渠道分类**：
| 渠道类型 | 包含 | SNX验证 |
|---------|------|---------|
| 驰加 | TYREPLUS | ✅ 支持 |
| 非驰加零售 | MCR, MAR | ✅ 支持 |
| MLD | MLD | ❌ 不适用 |
| FDD | FDD | ❌ 不适用 |
| 批发 | MPC, BOC | ❌ 不适用 |

**SNX匹配度计算**：
```
SNX匹配度 = SNX / 销量 × 100%
- 健康范围：95% - 110%
- > 110%：渠道库存减少
- < 95%：渠道库存增加
```

#### 核心结论模板

```markdown
## 📋 核心结论

### ✅ 增长驱动
1. XX渠道爆发：贡献X条增量，占总增量XX%
2. 明星规格崛起：XXXXXRXX增长X条（+XX%）
3. XX市场火热：主要配套XX车型

### ⚠️ 关注点
1. XX渠道下滑 -XX%
2. 部分规格萎缩

### 🎯 行动建议
1. 复制XX成功模式
2. 保障爆款规格供应
3. 深入分析下滑原因
```

---

### 3. 实战案例

#### 18寸轮胎下滑诊断（2026年1月）

**诊断流程**：
1. **总量对比**：2025年1月 vs 2026年1月
2. **规格维度**：哪些规格下滑最多？
3. **CAI维度**：哪些产品下滑最多？
4. **渠道维度**：哪个渠道是下滑主因？
5. **门店维度**：哪些门店在流失？

**输出报告**：
- 下滑规格TOP5
- 下滑CAI分析（含价格）
- 渠道贡献度
- 门店流失清单

#### 线上/线下购买行为分析

**数据来源**：SNX数据 `Is_Eshop` 字段
- `0` = 线下门店
- `1` = 线上渠道

**分析维度**：
- 整体线上比率
- CAI级别线上比率
- 价格敏感度
- 促销期趋势

#### 单一规格深度诊断流程

**诊断问题**：
1. 具体哪个花纹下滑最多？
2. 门店维度看SNX和销量？
3. 每个CAI价格有没有变化？

**诊断模板**：
```python
# 步骤1：提取规格
sales['Geobox'] = sales['Product_Description'].apply(extract_geobox)

# 步骤2：按规格汇总
spec_sales = sales[sales['Geobox'] == '23550R18']
spec_snx = snx[snx['Geobox'] == '23550R18']

# 步骤3：按渠道分析
channel_analysis = spec_sales.groupby('渠道分类')['具体客户购买数'].sum()

# 步骤4：按CAI分析
cai_analysis = spec_sales.groupby('Cai')['具体客户购买数'].sum()
```

---

## 🛠️ 进阶功能

### 1. 行业报告复现

#### Intelligence Hub模板（中英文双语）

**报告结构**：
```
Intelligence Hub (CN)_YYYYMM.pdf
├── 封面（报告编号、部门、密级）
├── 摘要/执行摘要
├── 第一部分：宏观环境
├── 第二部分：上游产业
├── 第三部分：轮胎市场
├── 第四部分：渠道分析
├── 第五部分：竞争格局
├── 第六部分：汽车市场
├── 第七部分：数据附录
├── 第八部分：趋势展望
└── English Version
```

**复现脚本**：`generate_intelligence_hub.py`
```bash
python3 generate_intelligence_hub.py --month 2602  # 2026年2月
python3 generate_intelligence_hub.py --all          # 所有月份
```

#### Tushare数据接口（期货/股价/政策）

**可用数据**：

| 数据类型 | 接口代码 | 相关性 |
|---------|---------|-------|
| 天然橡胶期货 | `fut_daily(ts_code='RU.SHF')` | ⭐⭐⭐ |
| 合成橡胶期货 | `fut_daily(ts_code='BR.SHF')` | ⭐⭐⭐ |
| 螺纹钢期货 | `fut_daily(ts_code='RB.SHF')` | ⭐⭐ |
| 玲珑轮胎 | `daily(ts_code='601966.SH')` | ⭐⭐⭐ |
| 贵州轮胎 | `daily(ts_code='600759.SH')` | ⭐⭐ |

**配置**：
```python
import tushare as ts
token = '你的TushareToken'
ts.set_token(token)
pro = ts.pro_api()
```

#### 报告生成器（HTML/PDF双格式）

**使用方式**：
```bash
# 生成HTML（推荐）
python3 generate_pdf.py report.md --html

# 生成PDF
python3 generate_pdf.py report.md

# 批量转换
python3 generate_pdf.py --html
```

**输出路径**：
```
~/Library/Mobile Documents/com~apple~CloudDocs/共享/报告/
└── [报告名称]/
    ├── [报告名称].md
    ├── [报告名称].html   ← 推荐
    └── [报告名称].pdf
```

---

### 2. 专项分析工具

#### 价格敏感度分析（价格-销量关联图）

**分析思路**：
1. 提取各CAI的底价变化
2. 对比销量变化
3. 计算相关系数

**可视化输出**：
- 散点图：价格变化 vs 销量变化
- 折线图：价格趋势与销量趋势对比

#### 库存周转诊断（SNX匹配度计算）

**诊断指标**：
- **渠道库存周转**：销量 vs SNX
- **清仓风险**：降价产品占比
- **补货预警**：高SNX + 低库存

**计算公式**：
```
库存周转率 = SNX / 销量
清仓占比 = 降价产品销量 / 总销量
```

#### 区域市场对比（省份/城市维度）

**关联方式**：
```
销售数据 → Dealer_ID → 客户名单 → City
```

**分析维度**：
- 省份销量排名
- 城市销量排名
- 区域渠道分布

---

## 📈 数据可视化

### 1. 交互式仪表盘

#### Plotly实时图表（月度销量趋势）

**示例**：
```python
import plotly.express as px

# 月度趋势图
fig = px.line(df, x='月份', y='销量', color='渠道')
fig.show()
```

**支持的图表类型**：
- 折线图：月度趋势
- 柱状图：渠道对比
- 饼图：占比分布
- 热力图：规格表现

#### Power BI仪表盘（渠道表现对比）

**数据导出**：
```python
# 导出为CSV供Power BI使用
df.to_csv('channel_performance.csv', index=False)
```

---

### 2. 故障排查

#### SQLite锁死处理

**问题症状**：
```
sqlite3.OperationalError: database is locked
```

**解决方案**：
```python
# 方法1：设置超时
conn = sqlite3.connect(DB_PATH, timeout=30)

# 方法2：关闭连接
conn.close()

# 方法3：删除锁文件
import os
if os.path.exists(f"{DB_PATH}-wal"):
    os.remove(f"{DB_PATH}-wal")
if os.path.exists(f"{DB_PATH}-shm"):
    os.remove(f"{DB_PATH}-shm")
```

#### 数据校验脚本

**校验项**：
- 月份连续性
- 渠道代码有效性
- CAI编码格式
- SNX与销量匹配度

```python
# 校验示例
def validate_data(df):
    errors = []
    if df['ID_Month_Key'].isnull().any():
        errors.append("存在空月份")
    if (df['具体客户购买数'] < 0).any():
        errors.append("存在负销量")
    return errors
```

#### 错误日志分析

**日志位置**：
```
~/.openclaw/logs/
```

**常见错误**：
| 错误 | 原因 | 解决方案 |
|------|------|---------|
| FileNotFoundError | 数据文件路径错误 | 检查BASE_PATH |
| KeyError | 列名不匹配 | 更新字段映射 |
| MemoryError | 数据量过大 | 分批处理 |

---

## 🛡️ 安全加固

### 1. 数据加密

#### SQLCipher加密配置

**安装**：
```bash
pip install pysqlcipher3
```

**配置**：
```python
import pysqlcipher3
db = pysqlcipher3.connect(database="sales.db", passphrase="your_password")
```

**注意**：请使用强密码并妥善保管

#### 环境变量管理

**敏感信息存储**：
```bash
# ~/.bashrc 或 ~/.zshrc
export TUSHARE_TOKEN="your_token"
export GITHUB_TOKEN="your_token"
```

**代码读取**：
```python
import os
token = os.environ.get('TUSHARE_TOKEN')
```

---

### 2. 权限分级

#### GitHub Teams访问控制

**仓库设置**：
1. 创建Organization
2. 添加Team成员
3. 设置仓库权限（Read/Write/Admin）

#### 数据脱敏规则

**敏感字段**：
- 客户姓名 → 脱敏处理
- 联系电话 → 隐藏中间位
- 门店地址 → 仅保留城市

**脱敏脚本**：
```python
def mask_sensitive(data):
    data['Customer'] = data['Customer'].apply(lambda x: x[0] + '***')
    data['Contact'] = data['Contact'].apply(lambda x: x[:3] + '****' + x[-4:])
    return data
```

---

## 📚 实用工具

### 1. 数据获取

#### Tushare Pro接口（期货/股票）

**快速获取函数**：
```python
from database import get_monthly_data

# 获取2026年2月数据
data = get_monthly_data('202602')
print(f"天然橡胶均价: {data['天然橡胶']['均价']}")
```

#### 爬虫模板（竞品数据抓取）

**使用示例**：
```python
# 参考 generate_intelligence_hub.py 中的爬虫逻辑
# 遵守网站robots.txt规则
# 合理设置请求间隔
```

---

### 2. 代码模板

#### Python分析脚本（Pandas/SQL）

**基础模板**：
```python
import pandas as pd
import sqlite3

# 连接数据库
DB_PATH = "~/.openclaw/workspace/tire-analyst/skills/tire-sales-analyst/sales_analysis.db"
conn = sqlite3.connect(DB_PATH)

# 查询数据
df = pd.read_sql_query("""
    SELECT * FROM sales 
    WHERE ID_Month_Key = '202601' 
    AND Geobox LIKE '%R18'
""", conn)

# 分析
result = df.groupby('渠道分类')['具体客户购买数'].sum()
print(result)
```

#### Jupyter Notebook模板

**模板位置**：
```
~/.openclaw/skills/tire-sales-analyst/notebooks/
```

**模板结构**：
1. 数据加载
2. 数据清洗
3. 探索性分析
4. 可视化
5. 结论

#### Markdown报告框架

**基础框架**：
```markdown
# 报告标题

## 一、总量概览
[数据表格]

## 二、维度分析
[分析内容]

## 三、核心结论
[总结]

## 四、行动建议
[下一步]
```

---

## 📊 附录

### 数据字段说明

| 字段 | 含义 | 示例 |
|------|------|------|
| `ID_Month_Key` | 月份标识 | 202501 |
| `Dealer_ID` | 门店ID | D001234 |
| `Cai` | CAI产品编码 | 273, 399 |
| `具体客户购买数` | 渠道出货销量 | 100, 500 |
| `SNX` | 终端注册数量 | 50, 200 |
| `Geobox` | 规格编码 | 23550R18 |
| `渠道分类` | 大类分类 | 驰加/MLD/FDD/批发 |

### 数据文件位置

```
~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/
├── Sales_rawdata/      # 销售数据
├── SNX_rawdata/        # SNX数据
├── 价格变化/            # RTM底价
├── 产品清单/            # 产品分类
└── 分月客户信息/        # 客户名单
```

### 常用查询速查

```python
# 2026年1月18寸轮胎
sales[(sales['ID_Month_Key']=='202601') & (sales['Geobox'].str.contains('R18'))]

# 按渠道汇总
df.groupby('渠道分类')['具体客户购买数'].sum()

# SNX匹配度
(snx['SNX'].sum() / sales['具体客户购买数'].sum()) * 100
```

---

*Author: ZZH-EC*
*Last Updated: 2026-03-14*
*Version: 2.3.0 - 模块化重构版*
