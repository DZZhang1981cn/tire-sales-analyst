---
name: tire-sales-analyst
version: 2.2.0
description: "轮胎销售数据分析技能。支持18寸轮胎专题分析、渠道对比（销量vs SNX）、Dealer表现、规格+CAI双重维度分析（含价格分析）、线上/线下购买行为分析、单一规格销量变化诊断分析、行业宏观数据获取（Tushare）、Intelligence Hub行业报告复现等。支持SQLite数据库加速分析。"
author: ZZH-EC
---

# 🛞 轮胎销售数据分析技能

专门用于分析米其林轮胎销售数据，支持多维度分析。

**技能版本**: 2.2.0
**更新内容**: 2026年3月新增数据库加速功能，所有数据预先整合到SQLite数据库中

---

## 🚀 数据库加速功能

### 概述

为了加快数据分析效率，系统会自动将所有数据文件整合到一个SQLite数据库中。每次分析时会先检查数据库是否需要更新，如果数据源有更新则自动重建数据库。

### 数据库位置

```
~/.openclaw/workspace/tire-analyst/skills/tire-sales-analyst/sales_analysis.db
```

### 数据统计

| 数据类型 | 行数 | 说明 |
|---------|------|------|
| 销售数据 | ~79,402行 | 2025-2026年销售记录 |
| SNX数据 | ~57,736行 | 2025-2026年SNX注册 |
| 价格数据 | ~15,988行 | 2025年1月-2026年3月RTM底价 |
| 产品分类 | ~3,390行 | 产品分类信息 |
| 客户名单 | ~4,592行 | 2026年客户信息 |

### 数据库更新命令

```bash
# 检查数据库状态
python3 build_database.py --check

# 强制重建数据库
python3 build_database.py --force

# 正常运行（自动检测是否需要更新）
python3 build_database.py
```

### 使用数据库进行分析

```python
import sqlite3

DB_PATH = "~/.openclaw/workspace/tire-analyst/skills/tire-sales-analyst/sales_analysis.db"

conn = sqlite3.connect(DB_PATH)

# 查询示例：2026年1月18寸轮胎销量
query = """
SELECT 
    Program_Type,
    SUM(具体客户购买数) as total_sales
FROM sales 
WHERE ID_Month_Key = 202601 AND Geobox LIKE '%R18'
GROUP BY Program_Type
"""
df = pd.read_sql_query(query, conn)
```

---

## 📊 销售分析标准流程

**每次分析必须遵循以下顺序：**

### 0. 数据准备（自动完成）
- 检查数据库是否存在
- 如果数据源有更新，自动重建数据库
- 从数据库加载数据（比Excel文件快10倍以上）
- 第一步：分析规格（产品描述中的尺寸规格，如255/55R20）
- 第二步：细分到CAI（具体产品编码）

### 2. 规格维度分析
**数据维度：**
- 销售数据（销量）
- SNX数据（**必须包含同比和环比**）
- 价格数据（RTM底价，**必须包含同比和环比**）
**分析顺序：** 分渠道 → 分城市 → 分 Dealer

**数据维度：**
- 销售数据
- SNX数据

### 3. CAI维度分析
**数据维度：**
- 销售数据（销量）
- SNX数据（**必须包含同比和环比**）
- 价格数据（RTM底价，**必须包含同比和环比**）
**分析顺序：** 分渠道 → 分城市 → 分 Dealer

**数据维度：**
- 销售数据
- SNX数据

### 4. 月份对比
与其他月份数据比较时，需要查看**RTM底价数据**

---

## ⚠️ 轮胎销售分析必备维度（必须同时分析）

每次分析轮胎销售时，无论什么场景，都必须包含以下**4个核心维度**：

1. **销量** - 销售数量、同比环比、趋势变化
2. **SNX** - SNX服务数量、**同比变化**、**环比变化**、渗透率
3. **价格** - 零售价、进货价、同比变化、环比变化、利润空间（需RTM底价数据）
4. **渠道** - 各渠道占比、渠道表现对比

**分析结论必须包含**：上述4个维度的综合结论，缺一不可。

**关键要求**：
- SNX分析必须包含：同比变化（YoY）、环比变化（MoM）
- 价格分析必须包含：同比变化（YoY）、环比变化（MoM）

---
## 📋 标准报告模板（尺寸销售分析）

> 用于分析特定尺寸（如18寸、19寸、20寸）轮胎销售数据的标准格式
> 版本：2026-02-27

### 报告结构

```markdown
# {年份}年{月份}月 {尺寸}寸轮胎销售分析报告

> 数据来源：{年份}_sales.xlsx、{年份-1}_sales.xlsx、SNX数据
> 分析维度：{尺寸}寸轮胎（R{尺寸}）

---

## 一、总量概览

| 指标 | {年份-1}年12月 | {年份-1}年1月 | {年份}年1月 | 同比变化 | 同比% | 环比变化 | 环比% |
|------|---------------|---------------|-------------|----------|------|----------|------|
| **销量** | X,XXX | X,XXX | X,XXX | **+X,XXX** | **+XX%** | +X,XXX | +XX% |
| **SNX** | X,XXX | X,XXX | X,XXX | **+X,XXX** | **+XX%** | +X,XXX | +XX% |

> 💡 **核心发现**：{尺寸}寸轮胎销量同比+XX%，环比+XX%；SNX同比+XX%，环比+XX%

---

## 二、规格维度分析

### 销量TOP10规格（含同比/环比）

| 排名 | 规格 | {年份-1}年12月 | {年份-1}年1月 | {年份}年1月 | 同比 | 同比% | 环比 | 环比% |
|------|------|---------------|---------------|-------------|------|------|------|------|
| 1 | **XXXXXRXX** | X | X | X | +X | +XX% | +X | +XX% |
... |

### SNX TOP10规格

| 排名 | 规格 | {年份-1}年12月SNX | {年份-1}年1月SNX | {年份}年1月SNX | 同比 | 环比 |
|------|------|------------------|------------------|----------------|------|------|
| 1 | XXXX | X | X | X | +X | +X |
... |

---

## 三、渠道维度分析

### 渠道销量（含同比/环比）

| 渠道 | {年份-1}年12月 | {年份-1}年1月 | {年份}年1月 | 同比 | 同比% | 环比 | 环比% |
|------|---------------|---------------|-------------|------|------|------|------|
| MLD | X | X | X | +X | +XX% | +X | +XX% |
| TYREPLUS | X | X | X | +X | +XX% | +X | +XX% |
... |

### 渠道SNX（含同比/环比）

| 渠道 | {年份-1}年12月SNX | {年份-1}年1月SNX | {年份}年1月SNX | 同比 | 环比 |
|------|-------------------|-------------------|-----------------|------|------|
| TYREPLUS | X | X | X | +X | +X |
... |

> 💡 **渠道洞察**：MLD同比+XX%、FDD同比+XX%、TYREPLUS同比+XX%、MCR同比-XX%

---

## 四、CAI产品TOP10（含产品名称）

| 排名 | CAI | 产品名称 | {年份-1}年12月 | {年份-1}年1月 | {年份}年1月 | 同比 | SNX |
|------|-----|---------|---------------|---------------|-------------|------|-----|
| 1 | XXXXXX | XXXXXXXXXXXXXXX | X | X | X | +X | X |
... |

---

## 五、Dealer门店TOP10（含SNX）

| 排名 | 门店 | {年份-1}年12月 | {年份-1}年1月 | {年份}年1月 | 同比 | SNX |
|------|------|---------------|---------------|-------------|------|-----|
| 1 | XXXXXXXXXX | X | X | X | +X | X |
... |

---

## 六、核心结论

### ✅ 增长驱动因素

1. XX渠道爆发：贡献X条增量，占总增量XX%
2. 明星规格崛起：XXXXXRXX增长X条（+XX%）
3. XX市场火热：{尺寸}寸主要配套XX车型

### ⚠️ 关注点

1. XX渠道下滑 -XX%
2. 部分规格萎缩

### 🎯 行动建议

1. 复制XX成功模式，重点扶持XX渠道
2. 保障XXXXXRXX、XXXXXRXX爆款规格供应
3. 深入分析XX下滑原因

---

**报告生成**: ZZH-EC  
**数据时间**: {年份}年{月份}月
```

### 数据获取要点

**必须包含的数据维度**：
1. **同比对比**：{年份-1}年1月 vs {年份}年1月
2. **环比对比**：{年份-1}年12月 vs {年份}年1月
3. **SNX数据**：所有维度必须包含SNX分析
4. **产品名称**：CAI维度必须包含完整产品描述

**数据文件位置**：
```
~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/
├── Sales_rawdata/
│   ├── 2025_sales.xlsx
│   └── 2026_sales.xlsx
├── SNX_rawdata/
│   ├── 2025_SNX.xlsx
│   └── 2026_SNX.xlsx
```

---

## 📁 Intelligence Hub 行业报告复现

### 原始报告位置

```
~/Library/Mobile Documents/com~apple~CloudDocs/共享/Report From Mint/
├── Intelligence Hub (CN)_2511.pdf   ← 2025年11月中文版
├── Intelligence Hub (CN)_2512.pdf   ← 2025年12月中文版
├── Intelligence Hub (CN)_2601.pdf   ← 2026年1月中文版
├── Intelligence Hub (EN)_2511.pdf   ← 2025年11月英文版
├── Intelligence Hub (EN)_2512.pdf   ← 2025年12月英文版
└── Intelligence Hub (EN)_2601.pdf   ← 2026年1月英文版
```

### 复现报告结构

**Intelligence Hub 标准结构**：

```
Intelligence Hub (CN)_YYYYMM.pdf
├── 封面（报告编号、周期、部门、密级）
├── 摘要/执行摘要（核心发现 + 关键指标）
├── 第一部分：宏观环境（GDP、社零、PPI、政策）
├── 第二部分：上游产业（橡胶、钢材等原材料）
├── 第三部分：轮胎市场（产量、销量、出口、价格）
├── 第四部分：渠道分析（后市场、门店、电商）
├── 第五部分：竞争格局（主要品牌动态、新品）
├── 第六部分：汽车市场（乘用车、商用车、新能源）
├── 第七部分：数据附录（Tushare数据接口）
├── 第八部分：趋势展望
├── 附录：报告结构对照
└── English Version（英文版报告）
```

### 复现步骤

#### 步骤1：分析原始报告结构

```python
import PyPDF2

pdf_path = '~/Library/Mobile Documents/com~apple~CloudDocs/共享/Report From Mint/Intelligence Hub (CN)_2601.pdf'

with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f"=== Page {i+1} ===")
        print(text[:500])  # 只打印前500字符
        
# 分析章节结构
chapters = []
for i, line in enumerate(text.split('\n')):
    if any(kw in line for kw in ['第一部分', '第二部分', '第三部分', '第四部分', '第五部分', '第六部分', '第七部分', '第八部分', '摘要', 'Executive Summary']):
        chapters.append((i, line))
```

#### 步骤2：提取关键数据

```python
import re
import pandas as pd

def extract_table_data(text):
    """从文本中提取表格数据"""
    # 匹配形如 "| 指标 | 数值 | 变化 |" 的数据
    table_pattern = r'\| ([^|]+) \| ([^|]+) \| ([^|]+) \|'
    matches = re.findall(table_pattern, text)
    return pd.DataFrame(matches)

def extract_numbers(text):
    """提取数字数据"""
    numbers = re.findall(r'[\d,.]+', text)
    percentages = re.findall(r'[\d.]+%', text)
    return numbers, percentages

def extract_section(text, start_marker, end_marker):
    """提取指定章节内容"""
    start_idx = text.find(start_marker)
    end_idx = text.find(end_marker)
    return text[start_idx:end_idx]
```

#### 步骤3：生成复现报告

```python
def generate_intelligence_hub_report(month='2602'):
    """生成指定月份的 Intelligence Hub 报告"""
    
    report = f"""# Intelligence Hub - 20{month[:2]}年{int(month[2:])}月轮胎行业月度报告

**报告编号**: Intelligence Hub (CN)_{month}
**报告周期**: 20{month[:2]}年{int(month[2:])}月
**编制部门**: 市场洞察部
**密级**: D3
**保存期限**: R10

---

## 摘要 (Executive Summary)

### 核心发现

[根据Tushare数据和行业动态填写]

### 关键指标

| 指标 | 20{month[:2]}年{int(month[2:])}月 | 环比变化 | 同比变化 |
|------|------------------|---------|---------|
| 天然橡胶均价 | XX,XXX元/吨 | +X% | 待获取 |
| 合成橡胶均价 | XX,XXX元/吨 | +X% | 待获取 |
| 螺纹钢均价 | X,XXX元/吨 | +X% | 待获取 |
| 玲珑轮胎股价 | XX.XX元 | +X% | +X% |
| 贵州轮胎股价 | X.XX元 | -X% | -X% |

[... 继续生成其他章节 ...]

---

## English Version: Intelligence Hub - {month_to_english(month)} Tire Industry Monthly Report

[生成英文版报告]

---
**报告制作**: ZZH-EC
**数据来源**: Tushare Pro、中汽协、海关总署、上海期货交易所
**生成时间**: 20XX年X月X日 XX:XX
"""
    return report
```

### 复现报告模板

```markdown
# Intelligence Hub - [YYYY]年[MM]月轮胎行业月度报告

**报告编号**: Intelligence Hub (CN)_YYMM
**报告周期**: YYYY年MM月
**编制部门**: 市场洞察部
**密级**: D3

---

## 摘要 (Executive Summary)

### 核心发现

1. **宏观经济**：XXXX
2. **政策动态**：XXXX
3. **原材料价格**：天然橡胶均价XX,XXX元/吨，环比+X%
4. **轮胎市场**：XXXX
5. **渠道变化**：XXXX

### 关键指标

| 指标 | YYYY年MM月 | 环比变化 | 同比变化 |
|------|------------|---------|---------|
| 天然橡胶均价 | XX,XXX元/吨 | +X% | +X% |
| 合成橡胶均价 | XX,XXX元/吨 | +X% | +X% |
| 螺纹钢均价 | X,XXX元/吨 | +X% | +X% |

---

## 第一部分：宏观环境

### 1.1 经济增长情况

### 1.2 政策动态

### 1.3 大宗商品市场

---

## 第二部分：上游产业

### 2.1 橡胶原材料价格走势

### 2.2 钢材价格走势

### 2.3 产业链成本分析

---

## 第三部分：轮胎市场

### 3.1 产量与销量

### 3.2 出口市场

### 3.3 经销商价格

---

## 第四部分：渠道分析

### 4.1 后市场渠道结构变化

### 4.2 门店扩张

### 4.3 电商渠道

---

## 第五部分：竞争格局

### 5.1 主要品牌动态

### 5.2 产能变化

### 5.3 新品发布

---

## 第六部分：汽车市场

### 6.1 乘用车市场

### 6.2 商用车市场

### 6.3 新车市场与后市场

---

## 第七部分：数据附录

### 7.1 Tushare可获取数据

| 数据类型 | 代码 | 来源 |
|---------|------|------|
| 天然橡胶期货 | `fut_daily(ts_code='RU.SHF')` | 上海期货交易所 |
| 合成橡胶期货 | `fut_daily(ts_code='BR.SHF')` | 上海期货交易所 |

### 7.2 数据来源说明

---

## 第八部分：趋势展望

### 8.1 短期展望（1-3个月）

### 8.2 中期展望（3-6个月）

### 8.3 长期趋势

---

## English Version Template

### Executive Summary

**Key Findings**:
1. **Macro Economy**: XXXX

**Key Indicators**:

| Indicator | MM YYYY | MoM | YoY |
|-----------|---------|-----|-----|
| Natural Rubber | XX,XXX RMB/ton | +X% | +X% |

---

**报告制作**: ZZH-EC
**数据来源**: Tushare Pro
**生成时间**: YYYY年MM月DD日
```

### Tushare数据自动获取

```python
import tushare as ts

# 配置
token = '3474c836e690df5c51d0faa5263c2211077043b27f86e5a80f4aa5bd'
ts.set_token(token)
pro = ts.pro_api()

def get_monthly_data(month='202602'):
    """获取指定月份的宏观数据"""
    
    # 1. 天然橡胶期货
    ru = pro.fut_daily(
        ts_code='RU.SHF',
        start_date=f'{month}01',
        end_date=f'{month}28'
    )
    ru_monthly = {
        '期初': ru.iloc[0]['close'],
        '期末': ru.iloc[-1]['close'],
        '均价': round(ru['close'].mean(), 2),
        '最高': ru['close'].max(),
        '最低': ru['close'].min()
    }
    
    # 2. 合成橡胶期货
    br = pro.fut_daily(
        ts_code='BR.SHF',
        start_date=f'{month}01',
        end_date=f'{month}28'
    )
    br_monthly = {
        '期初': br.iloc[0]['close'],
        '期末': br.iloc[-1]['close'],
        '均价': round(br['close'].mean(), 2)
    }
    
    # 3. 螺纹钢期货
    rb = pro.fut_daily(
        ts_code='RB.SHF',
        start_date=f'{month}01',
        end_date=f'{month}28'
    )
    rb_monthly = {
        '期初': rb.iloc[0]['close'],
        '期末': rb.iloc[-1]['close'],
        '均价': round(rb['close'].mean(), 2)
    }
    
    # 4. 轮胎概念股
    lyl = pro.daily(
        ts_code='601966.SH',
        start_date=f'{month}01',
        end_date=f'{month}28'
    )
    gz = pro.daily(
        ts_code='600759.SH',
        start_date=f'{month}01',
        end_date=f'{month}28'
    )
    
    stock_data = {
        '玲珑': {
            '期末价': lyl.iloc[-1]['close'],
            '月涨幅': round(lyl['pct_chg'].sum(), 2)
        },
        '贵州': {
            '期末价': gz.iloc[-1]['close'],
            '月涨幅': round(gz['pct_chg'].sum(), 2)
        }
    }
    
    return {
        '天然橡胶': ru_monthly,
        '合成橡胶': br_monthly,
        '螺纹钢': rb_monthly,
        '股价': stock_data
    }

# 使用示例
data = get_monthly_data('202602')
print(f"天然橡胶月均价: {data['天然橡胶']['均价']}元/吨")
print(f"玲珑轮胎月涨幅: {data['股价']['玲珑']['月涨幅']}%")
```

### 生成复现报告

```bash
# 使用 generate_intelligence_hub.py 脚本生成报告

cd ~/.openclaw/skills/tire-sales-analyst/

# 生成2026年2月报告
python3 generate_intelligence_hub.py --month 2602

# 生成2025年12月报告
python3 generate_intelligence_hub.py --month 2512

# 生成所有月份
python3 generate_intelligence_hub.py --all

# 查看帮助
python3 generate_intelligence_hub.py --help
```

### 复现报告保存位置

```
~/Library/Mobile Documents/com~apple~CloudDocs/共享/Report From Mint/
├── Intelligence Hub (CN)_2602.md   ← 复现的中文报告
├── Intelligence Hub (EN)_2602.md   ← 复现的英文报告
├── Intelligence Hub (CN)_2602.pdf  ← 转换后的PDF
└── ...
```

---

## 📊 销售分析标准流程

**每次分析必须遵循以下顺序：**

## 数据文件位置

```
~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/
├── Sales_rawdata/
│   ├── 2025_sales.xlsx      # 2025年销售数据
│   └── 2026_sales.xlsx      # 2026年销售数据
├── SNX_rawdata/
│   ├── 2025_SNX.xlsx        # 2025年SNX数据
│   └── 2026_SNX.xlsx        # 2026年SNX数据
├── 价格变化/
│   ├── 20250101价格.xlsx    # 2025年1月RTM底价
│   ├── 20250201价格.xlsx    # 2025年2月RTM底价
│   ├── ...
│   ├── 20260201价格.xlsx    # 2026年2月RTM底价
│   └── 20260301价格.xlsx    # 2026年3月RTM底价 ⭐ 新增
├── 产品清单/
│   └── Product Category_V75_20260129.xlsx
├── 分月客户信息/
│   ├── 2018客户名单.xlsx
│   ├── 2019客户名单.xlsx
│   ├── ...
│   ├── 2025客户名单.xlsx
│   └── 2026客户名单.xlsx    # 新增
├── 客户名单/
├── 销售月报/
│   ├── 2026年1月销售分析报告.pdf
│   ├── 2026年1月销售预览.md
│   └── chart_*.png          # 图表文件
└── TRAE/                   # 新增文件夹
```

## 数据字段说明

### 销售数据 (Sales)
| 字段 | 含义 | 示例 |
|------|------|------|
| `ID_Month_Key` | 月份标识 | 202501（2025年1月） |
| `Customer` | 客户公司名称 | 杭州XXX轮胎有限公司 |
| `AM_Territory` | AM区域 | AM-HZ1, AM-HZ2 |
| `Program_Type` | 渠道类型 | MCR, MLD, FDD, TYREPLUS, MPC, MAR, MARPlus, BOC |
| `Dealer_ID` | **门店ID**（关联键） | D001234 |
| `DealerName` | 门店名称 | 杭州XX驰加店 |
| `Product_Description` | 产品描述（包含规格、花纹、品牌） | 235/60 R18 PRIMACY SUV+ MI |
| `Cai` | **CAI产品编码**（独立数字） | 273, 399 |
| `具体客户购买数` | 渠道出货销量 | 100, 500 |

### SNX数据（终端注册）
| 字段 | 含义 | 示例 |
|------|------|------|
| `ID_Month_Key` | 月份标识 | 202501 |
| `Dealer_ID` | **门店ID**（关联键） | D001234 |
| `Program_Type` | 渠道类型 | 同销售数据 |
| `Product_Description` | 产品描述 | 同上 |
| `SNX` | SNX注册数量（终端真实零售） | 50, 200 |
| `Is_Eshop` | 是否线上渠道 | **0=否, 1=是** |

### 价格数据
| 字段 | 含义 | 示例 |
|------|------|------|
| `CAI` | CAI产品编码 | 273, 399 |
| `产品描述（新增产品为红色）` | 产品描述 | 235/60 R18 PRIMACY SUV+ |
| `RTM零售商进货底价(含售出折扣)` | 底价（含折扣） | 730, 845 |

### 客户名单（地理信息）
| 字段 | 含义 | 示例 |
|------|------|------|
| **第1列** | **门店ID**（关联键） | D001234 |
| `City` | 城市 | 杭州, 温州 |
| `其他字段` | 客户详细信息 | - |

### 辅助字段（分析时生成）
| 字段 | 含义 | 生成方式 |
|------|------|----------|
| `Geobox` | 规格编码 | 从Product_Description提取：`23560R18` = `235/60R18` |
| `渠道分类` | 大类分类 | Program_Type映射：TYREPLUS→驰加，MCR/MAR→非驰加零售等 |

---

## 🔗 表间关系（核心）

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   销售数据      │         │    SNX数据      │         │   客户名单      │
│  (Sales)        │         │  (SNX_rawdata)   │         │  (客户地理信息) │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ Dealer_ID ◄────┼─────────┼──► Dealer_ID     │         │ 门店ID ◄───────┼──► Dealer_ID
│ Cai             │         │                  │         │ City            │
│ Product_Desc    │         │ Product_Desc    │         │                 │
│ Program_Type     │         │ Program_Type     │         │                 │
└─────────────────┘         └─────────────────┘         └─────────────────┘
         │                           │                           │
         └───────────────────────────┼───────────────────────────┘
                                     ▼
                        ┌─────────────────────┐
                        │    价格数据          │
                        │  (价格变化)          │
                        ├─────────────────────┤
                        │ CAI ◄───────────────┘
                        │ 产品描述             │
                        │ 底价(RTM)           │
                        └─────────────────────┘
```

**关联方式：**

| 关联键 | 连接表 | 用途 |
|--------|--------|------|
| `Dealer_ID` | Sales ↔ SNX ↔ 客户名单 | 分析门店维度的销量+SNX+城市 |
| `CAI` | Sales ↔ 价格数据 | 分析产品的销量+底价 |
| `Product_Description` | Sales ↔ SNX | 备选关联（不如CAI稳定） |
| `Program_Type` | Sales ↔ SNX | 渠道对比分析 |
| `City` | 客户名单 | 地理维度分析（城市） |

---

## 💡 关键理解

1. **SNX ≠ 销量**
   - SNX = 终端车主注册（真实零售）
   - 销量 = 渠道出货给门店

2. **Dealer_ID是核心关联字段**
   - 通过Dealer_ID可以把：门店销量 + 门店SNX注册 + 门店城市 关联起来
   - 看到每个门店的"进货-零售"差距

3. **CAI是产品唯一标识**
   - CAI是独立数字编码，不是从描述中提取的
   - 用于关联Sales和价格数据

4. **Is_Eshop**
   - 0 = 线下门店
   - 1 = 线上渠道

## 分析模板

### 1. 基础分析：18寸轮胎专题

```python
# 筛选18寸轮胎
df_18 = df[df['Product_Description'].str.contains('R18', na=False)]

# 2025年1月 vs 2026年1月
df_2025_jan = df_18[df_18['ID_Month_Key'] == 202501]
df_2026_jan = df_18[df_18['ID_Month_Key'] == 202601]
```

### 2. 渠道对比分析（销量 vs SNX）

```python
# 销量对比
prog_sales = df_2026_jan.groupby('Program_Type')['具体客户购买数'].sum()

# SNX对比
prog_snx = snx_2026_jan.groupby('Program_Type')['SNX'].sum()
```

### 3. 规格+CAI双重维度分析（推荐模板）

当分析销量下滑原因时，必须按以下逻辑分析：

```python
# 第一步：规格维度分析
# 提取Geobox（如 23560R18 = 235/60R18）
def extract_geobox(text):
    text = str(text).upper().replace('/', ' ').replace('-', ' ')
    match = re.search(r'(\d{3})\s*(\d{2})\s*R\s*(\d{2})', text)
    if match: return f"{match.group(1)}{match.group(2)}R{match.group(3)}"
    return ''

df['Geobox'] = df['Product_Description'].apply(extract_geobox)

# 规格汇总
gb_2025 = s_2025.groupby('Geobox')['具体客户购买数'].sum()
gb_2026 = s_2026.groupby('Geobox')['具体客户购买数'].sum()
gb_comp = pd.DataFrame({'销量_2025': gb_2025, '销量_2026': gb_2026})
gb_comp['销量_变化'] = gb_comp['销量_2026'] - gb_comp['销量_2025']

# SNX也要按规格汇总
snx_gb_2025 = snx_2025.groupby('Geobox')['SNX'].sum()
snx_gb_2026 = snx_2026.groupby('Geobox')['SNX'].sum()

# 第二步：CAI维度分析
# CAI是销售数据中的独立字段（Cai），直接使用
cai_2025 = s_2025.groupby('Cai')['具体客户购买数'].sum()
cai_2026 = s_2026.groupby('Cai')['具体客户购买数'].sum()
```

**报告模板（必须包含）：**

```markdown
## 三、规格+CAI双重维度分析

### 销量下降TOP 5规格

| 排名 | 规格 | 2025年1月 | 2026年1月 | 销量变化 | SNX变化 | 状态 |
|------|------|------------|------------|----------|----------|------|
| 1 | 23560R18 | 1,438 | 977 | -461 | +20.6% | ✅ |
| 2 | 22555R18 | 1,102 | 664 | -438 | +53.6% | ✅ |
...
```

**CAI详细分析模板：**

```markdown
### 规格1：23560R18（销量下降461条，SNX上涨20.6%）

**规格总销量**: 1,438 → 977 (-461)

| CAI | 产品描述 | 销量变化 | 占规格比率 | SNX变化 | 底价变化 |
|-----|---------|----------|----------|----------|----------|
| 273 | 235/60 R18 PRIMACY SUV+ | -691 | 48% | 461→556 (+95) | 730→730 (0%) |
```

**核心解读：**
- 销量↓ + SNX↑ = 渠道消化库存（正常）
- 销量↓ + SNX↓ = 终端需求下降（需关注）

### 4. Dealer维度分析

```python
# 按Dealer汇总
dealer_sales = df_2026_jan.groupby('DealerName')['具体客户购买数'].sum()
dealer_sales.sort_values(ascending=True)  # 排序查看下降的
```

## 常用分析命令

### 渠道汇总
```python
prog_summary = df.groupby('Program_Type')['具体客户购买数'].sum()
```

### AM区域汇总
```python
am_summary = df.groupby('AM_Territory')['具体客户购买数'].sum()
```

### CAI维度汇总（单一CAI维度）
```python
# CAI是销售数据的独立字段（Cai），直接使用
cai_sales = df.groupby('Cai')['具体客户购买数'].sum()
cai_sales.sort_values()  # 查看销量变化

# CAI关联价格数据
price_by_cai = price_df.groupby('CAI')['底价字段'].mean()
```

### 规格维度汇总
```python
# Geobox = 规格编码
df['Geobox'] = df['Product_Description'].str.extract(r'(\d{3})(\d{2})R(\d{2})')
df['Geobox'] = df['Geobox'].apply(lambda x: f"{x[0]}{x[1]}R{x[2]}" if pd.notna(x) else '')

gb_sales = df.groupby('Geobox')['具体客户购买数'].sum()
```

### Dealer维度分析（门店维度）
```python
# 按门店汇总销量
dealer_sales = df.groupby('Dealer_ID')['具体客户购买数'].sum()

# 门店的SNX（通过Dealer_ID关联）
dealer_snx = snx_df.groupby('Dealer_ID')['SNX'].sum()

# 合并门店的销量+SNX
dealer_full = pd.merge(dealer_sales, dealer_snx, left_index=True, right_index=True, how='outer')
dealer_full['渗透率'] = dealer_full['SNX'] / dealer_full['具体客户购买数']
```

### 城市维度分析
```python
# 客户名单关联
customer_df = pd.read_excel('../销售分析/客户名单/*.xlsx')

# 门店ID关联客户城市
dealer_city = customer_df.iloc[:, 0]  # 第1列是门店ID
dealer_city = dealer_city.rename('Dealer_ID')

# 销量按城市汇总
sales_by_city = pd.merge(df, dealer_city, on='Dealer_ID')
city_sales = sales_by_city.groupby('City')['具体客户购买数'].sum()

# SNX按城市汇总
snx_by_city = pd.merge(snx_df, dealer_city, on='Dealer_ID')
city_snx = snx_by_city.groupby('City')['SNX'].sum()
```

## 输出格式建议

### 标准报告模板（含价格分析）

```markdown
# [规格/产品线]销售分析报告

**分析周期**: 2025年1月 - 2026年1月
**数据维度**: [如：20寸轮胎]
**对比方式**: 同比分析
**生成时间**: YYYY年MM月DD日

---

## 一、总体概览

### 年度对比

| 指标 | 2025年1月 | 2026年1月 | 变化 | 变化率 |
|------|-----------|-----------|------|--------|
| **总销量** | X,XXX 条 | X,XXX 条 | **+X,XXX 条** | **+XX%** |
| **总SNX** | X,XXX 条 | X,XXX 条 | +XXX 条 | +XX% |
| **参与规格数** | XX 个 | XX 个 | +X 个 | +XX% |
| **参与CAI数** | XXX 个 | XXX 个 | +XX 个 | +XX% |

---

## 二、规格维度分析

### 销量TOP10规格

| 排名 | 规格 | 2025年1月 | 2026年1月 | 销量变化 | 变化率 | SNX变化 |
|------|------|-----------|-----------|----------|--------|---------|
| 1 | **XXXXXRXX** | XXX | XXX | **+XXX** | **+XX%** | +XX |
| 2 | **XXXXXRXX** | XXX | XXX | +XXX | +XX% | +XX |
...

### 规格层面核心发现

**🔥 爆发规格TOP3：**

| 规格 | 变化 | 特点 |
|------|------|------|
| **XXXXXRXX** | +XXX条 (+XX%) | 冠军规格，贡献XX%增量 |
| **XXXXXRXX** | +XXX条 (+XX%) | XX轮胎主力规格 |
| **XXXXXRXX** | +XXX条 (+XX%) | 高端XX标配 |

**📉 下滑规格：**

| 规格 | 变化 | 特点 |
|------|------|------|
| **XXXXXRXX** | -XXX条 (-XX%) | 传统XX规格需求萎缩 |

---

## 三、CAI产品维度分析（规格细分 + 价格分析）

> **分析流程**：先看规格 → 再细分到CAI层面 → 分析销量+SNX+价格

### 爆发规格1：XXXXXRXX（冠军规格，+XXX条）

> **规格总览**：XXX → XXX 条（+XXX，+XX%）

**内部CAI销量明细（含价格）：**

| CAI | 产品描述 | 销量变化 | 变化率 | 底价变化 |
|-----|---------|----------|--------|---------|
| XXXXXX | XXXXXXXXXXXXXXXXX | +XXX | **+XXX%** | -XX元 (-X.X%) |
| XXXXXX | XXXXXXXXXXXXXXXXX | +XXX | +XX% | -XX元 (-X.X%) |
...

**规格XXXXXRXX核心洞察：**
- **静音棉版本主导**：ACOUSTIC版本贡献超XX%增量
- **XX系列崛起**：DT ACOUSTIC版本独占XX%份额
- **价格因素**：降价X-X%刺激需求

---

### 下滑规格：XXXXXRXX（-XXX条）

> **规格总览**：XXX → XXX 条（-XXX，-XX%）

**内部CAI销量明细（含价格）：**

| CAI | 产品描述 | 销量变化 | 变化率 | 底价变化 |
|-----|---------|----------|--------|---------|
| XXXXXX | XXXXXXXXXXXXXXXXX | -XXX | **-XX%** | 0元 (0%) |
...

**规格XXXXXRXX核心洞察：**
- **单一产品依赖**：XXXXXXXX独占XX%份额
- **缺乏产品迭代**：没有XX版本和静音棉版本
- **价格无优势**：底价未调整，但仍下滑

---

## 四、CAI产品汇总排名（含价格分析）

### 销量TOP15 CAI（跨规格汇总 + 价格）

| 排名 | CAI | 产品描述 | 规格 | 销量变化 | 变化率 | 底价变化 | 评价 |
|------|-----|---------|------|----------|--------|---------|------|
| 1 | XXXXXX | XXXXXXXXXXXXXXX | XXXX | +XXX | +XX% | 0% | ✅ |
| 2 | XXXXXX | XXXXXXXXXXXXXXX | XXXX | -XXX | **-XX%** | 0% | ⚠️ |
| 3 | XXXXXX | **XXXXXXXXXX** | XXXX | +XXX | **+XXX%** | -X.X% | ⭐ |
...

### 价格-销量关联分析

**爆发产品（降价+增量）：**

| 产品类型 | 降价幅度 | 销量变化 | 关联性 |
|---------|---------|----------|--------|
| XX ACOUSTIC系列 | -X.X% ~ -X.X% | +XXX%~+XXX% | **强相关** |
| XX系列 | -X.X% ~ -X.X% | +XXX%~+XXX% | **强相关** |

**稳定产品（价格不变）：**

| 产品 | 销量变化 | 评价 |
|------|----------|------|
| XXXXXXXXXXXX | +XX% | ✅ 产品竞争力强 |
| XXXXXXXXXXXX | -XX% | ⚠️ 需求萎缩 |

---

## 五、渠道维度分析

### 渠道销量对比

| 渠道 | 2025年1月 | 2026年1月 | 销量变化 | 变化率 | 渗透率(25→26) |
|------|-----------|-----------|----------|--------|----------------|
| **TYREPLUS** | XXX | XXX | +XXX | +XX% | XX% → XX% |
| **MLD** | XXX | XXX | **+XXX** | **+XXX%** | X% → X% |
| MCR | XXX | XXX | -XXX | **-XX%** | XX% → XX% |
...

### 渠道核心发现
- XX渠道：稳健增长，渗透率健康
- XX渠道：爆发增长，需补齐SNX
- XX渠道：量跌价稳，渗透率提升

---

## 六、Dealer门店维度分析

### 销量TOP15门店

| 排名 | 门店名称 | 2025年1月 | 2026年1月 | 销量变化 | 变化率 |
|------|---------|-----------|-----------|----------|--------|
| 1 | **XXXXXXXX** | 0 | XXX | **+XXX** | 新增 |
| 2 | XXXXXXXXXXXX | XXX | XXX | +XXX | +XX% |
...

### SNX TOP10门店

| 排名 | 门店名称 | 2025年1月 | 2026年1月 | SNX变化 |
|------|---------|-----------|-----------|----------|
| 1 | XXXXXXXXXXXX | XX | XX | +XX |
| 2 | XXXXXXXXXXXX | XX | XX | +XX |
...

---

## 七、核心洞察总结

### 产品-价格-销量三维分析

| 维度 | 关键发现 |
|------|----------|
| **产品趋势** | XX + XX = 爆发组合 |
| **价格敏感度** | XX产品降价X-X%刺激增量XX%+ |
| **替代效应** | XXXX被XXXX替代（产品迭代） |

### 成功因素

| 产品 | 成功要素 |
|------|----------|
| XXXXXXXX | XX + 降价X% + XX定位 |
| XXXXXXXX | XX + XX + 降价X% |

### 失败因素

| 产品 | 失败要素 |
|------|----------|
| XXXXXXXX | 无XX版本 + 无XX + 产品老化 |
| XXXXXXXX | 规格被替代 + 产品单一 |

---

## 八、建议与行动

### 短期（1-3个月）

1. **供应链保障**
   - 确保XX系列产品供应充足
   - XX产品产能优先

2. **SNX管理**
   - 补齐XX渠道的SNX数据
   - 提升XX渠道渗透率目标

3. **价格策略**
   - XX产品降价策略有效，可适度延续
   - 传统产品需考虑价格竞争力

### 中期（3-6个月）

1. **渠道策略**
   - XX模式复制（XX渠道拓展）
   - XX门店提质增效

2. **产品策略**
   - 加速XX产品线布局
   - XX产品作为高端突破口

3. **区域策略**
   - XX区域专项诊断
   - XX区域重点投入

### 长期（6-12个月）

1. **市场机会**
   - 持续看好XX市场
   - XX寸大轮毂市场提前布局

2. **风险提示**
   - 传统产品线萎缩风险
   - 渠道依赖度风险

---

## 九、附录

### 数据来源

| 文件 | 说明 |
|------|------|
| Sales_rawdata/2025_sales.xlsx | 2025年销售数据 |
| Sales_rawdata/2026_sales.xlsx | 2026年销售数据 |
| SNX_rawdata/2025_SNX.xlsx | 2025年SNX数据 |
| SNX_rawdata/2026_SNX.xlsx | 2026年SNX数据 |
| 价格变化/20250101价格.xlsx | 2025年1月RTM底价 |
| 价格变化/20260101价格.xlsx | 2026年1月RTM底价 |
| 价格变化/20260301价格.xlsx | 2026年3月RTM底价 ⭐ 新增 |

### 分析方法

1. **规格提取**：从Product_Description提取轮毂直径（如R20）
2. **CAI匹配**：使用产品独立编码精确匹配
3. **渠道分类**：基于Program_Type字段
4. **SNX渗透率**：SNX/销量 × 100%
5. **价格分析**：RTM零售商进货底价（含售出折扣）
```

---

## 常见分析需求

1. **18寸轮胎专题**
2. **渠道对比**（MCR, MLD, FDD, TYREPLUS）
3. **规格+CAI双重维度分析** ⭐（推荐）
   - 先看规格维度（哪些规格下滑多）
   - 再看CAI维度（哪些产品下滑多）
   - 必须包含：销量变化、占规格比率、SNX变化、底价变化
4. **Dealer表现**（上升/下降）
5. **SNX渗透率**（SNX/销量）
6. **月度趋势**
7. **同比/环比分析**

1. **18寸轮胎专题**
2. **渠道对比**（MCR, MLD, FDD, TYREPLUS）
3. **规格+CAI双重维度分析** ⭐（推荐）
   - 先看规格维度（哪些规格下滑多）
   - 再看CAI维度（哪些产品下滑多）
   - 必须包含：销量变化、占规格比率、SNX变化、底价变化
4. **Dealer表现**（上升/下降）
5. **SNX渗透率**（SNX/销量）
6. **月度趋势**
7. **同比/环比分析**

---

## 🎯 专项分析：线上/线下购买行为分析

> 基于SNX数据的Is_Eshop字段，分析消费者线上/线下购买偏好

### 分析场景
- 分析特定规格（如235/45R18）的线上/线下购买比例
- 按CAI维度细分产品类型
- 结合价格分析购买行为
- 分月追踪趋势变化

### 报告模板：线上/线下购买分析

```markdown
# [规格]线上/线下购买分析报告

**分析周期**: 2025年1月 - 2026年1月
**数据维度**: [如：235/45R18]
**分析重点**: CAI维度线上/线下购买比率 + 价格分析
**生成时间**: YYYY年MM月DD日

---

## 一、总体概览

### 规格整体情况

| 指标 | 数值 |
|------|------|
| 总SNX注册量 | X,XXX 条 |
| 线下购买 | X,XXX 条 (XX%) |
| 线上购买 | **X,XXX 条 (XX%)** |
| 涉及CAI数 | XX 个 |

### 整体线上比率

| 指标 | 数值 |
|------|------|
| **整体线上比率** | XX% |
| **线上比率最高月份** | 2025年11月 (XX%) |
| **线上比率最低月份** | 2025年7月 (X%) |

---

## 二、CAI产品完整分析

### CAI汇总排名（按总SNX排序，含产品全称和价格）

| 排名 | CAI | 产品全称 | 总SNX | 线上 | 线下 | 线上% | 25.1底价 | 26.1底价 | 变化 |
|------|-----|---------|--------|------|------|-------|-----------|-----------|------|
| 1 | XXXXXX | XXXXXXXXXXXXXXXXX | X,XXX | XXX | XXX | XX% | X,XXX | X,XXX | -XX |
| 2 | XXXXXX | XXXXXXXXXXXXXXXXX | X,XXX | XXX | XXX | XX% | X,XXX | X,XXX | -XX |
...

---

## 三、线上/线下特征分析

### 线上购买为主的产品（线上比率>15%）

| CAI | 产品全称 | 线上% | 底价 | 特点 |
|-----|---------|-------|------|------|
| **XXXXXX** | XXXXXXXXXXXXXXXXX | **XX%** | XXX元 | VOL渠道专供，线上最高 |

**关键发现：**
- **VOL渠道专供产品**线上比率最高（XX%）
- 说明VOL渠道消费者更习惯线上购买

### 线下购买为主的产品（线上比率<5%）

| CAI | 产品全称 | 线上% | 底价 | 特点 |
|-----|---------|-------|------|------|
| **XXXXXX** | XXXXXXXXXXXXXXXXX | **X%** | XXX元 | 静音棉版本 |

**关键发现：**
- **静音棉产品**（ACO版本）几乎完全线下购买（线上比率<1%）
- **常规产品**（PCY3/4 ST）线下比率超XX%
- 说明静音棉产品依赖门店安装服务

---

## 四、价格与线上比率关系分析

### 按价格区间统计

| 价格区间 | 总SNX | 线上SNX | 线上比率 |
|---------|--------|---------|---------|
| <800元 | X,XXX | XXX | **X%** |
| 800-900元 | XXX | XX | **XX%** |
| >900元 | X,XXX | XXX | **X%** |

### 价格与线上比率对应表

| CAI | 产品全称 | 平均底价 | 线上% | 价格-线上关联 |
|-----|---------|---------|-------|--------------|
| XXXXXX | PCY4 ST VOL | XXX元 | **XX%** | ⭐ 中高价+高线上 |
| XXXXXX | PCY3 ST | XXX元 | X% | 低价+极低线上 |

### 核心洞察

1. **XX-YY元区间**：线上比率最高（XX%）
   - VOL渠道专供产品集中在该价格带
   - 消费者对中等价格产品线上接受度高

2. **<XX元区间**：线上比率较低（X%）
   - 常规产品价格低但线下为主
   - 低价产品更依赖门店渠道

3. **>YY元区间**：线上比率中等（X%）
   - 高端静音棉产品价格高但线下为主
   - 高价产品需要安装服务

---

## 五、分月趋势分析

### 整体分月趋势

| 月份 | 线下 | 线上 | 总计 | 线上比率 |
|------|------|------|------|---------|
| 2025年1月 | XXX | XX | XXX | XX% |
| 2025年2月 | XXX | XX | XXX | XX% |
...
| 2025年11月 | XXX | XXX | XXX | **XX%** ⭐ |
| 2026年1月 | XXX | XXX | XXX | XX% |

**趋势分析：**
- ✅ 下半年起线上比率呈上升趋势
- ✅ XX月达到峰值（XX%），XX活动影响明显
- ✅ XX月促销季（XX%）线上购买激增
- ⚠️ XX月数据异常（线上为0），可能存在数据缺失

### TOP3 CAI 分月详细趋势

#### CAI XXXXXX - XXXXXXXXXXXXXX（销量冠军，线上比率XX%）

| 月份 | 线下 | 线上 | 线上比率 |
|------|------|------|---------|
| 2025年X月 | XX | XX | XX% |
| 2025年Y月 | XX | XX | **XX%** |
...
| 2026年1月 | XX | XX | XX% |

**年度线上比率**: XX%
**特点**: 大促月份线上比率显著提升（XX%）

---

### 月度销量分布图

**月度SNX总量趋势：**

| 季度 | 月份 | 总SNX | 线上SNX | 线上比率 | 环比变化 |
|------|------|--------|---------|---------|---------|
| Q1 | 2025年1-3月 | X,XXX | XXX | XX% | - |
| Q2 | 2025年4-6月 | X,XXX | XXX | XX% | ↑X% |
| Q3 | 2025年7-9月 | X,XXX | XXX | XX% | ↓X% |
| Q4 | 2025年10-12月 | X,XXX | XXX | **XX%** | ↑X% |
| - | 2026年1月 | XXX | XX | XX% | →持平 |

**季度趋势解读：**
- Q4（10-12月）线上比率最高（XX%），XX带动明显
- Q2（4-6月）次高（XX%），XX促销拉动
- Q3（7-9月）最低（XX%），XX数据异常影响

---

## 六、核心洞察总结

### 产品类型与线上比率

| 产品类型 | 代表CAI | 线上比率 | 购买行为 |
|---------|---------|---------|---------|
| VOL渠道专供 | XXXXX, XXXXX | ~XX% | 线上购买倾向高 |
| 静音棉产品 | XXXXX, XXXXX | <X% | 依赖门店安装，线下为主 |
| 常规产品 | XXXXX, XXXXX | <X% | 完全线下销售 |
| 大促期间 | 全部 | XX% | 线上购买激增 |

### 价格敏感度分析

| 价格区间 | 线上比率 | 特点 |
|---------|---------|------|
| XX-YY元 | **XX%** | XX渠道集中，线上接受度高 |
| <XX元 | X% | 常规产品，线下为主 |
| >YY元 | X% | 高端产品，线下为主 |

### 消费者行为洞察

1. **静音棉产品**（如ACO/T2版本）
   - 线上比率极低（<1%）
   - 消费者需要门店安装服务
   - 适合做门店转化

2. **VOL渠道产品**
   - 线上比率最高（XX%）
   - VOL消费者更习惯线上购买
   - 适合线上营销推广

3. **促销敏感度**
   - XX月、XX月线上比率提升XX个百分点
   - 大促期间消费者更愿意线上购买

---

## 七、建议与行动

### 短期（1-3个月）

1. **线上营销**
   - 加大XX月/XX月促销期线上投放
   - VOL渠道产品适合线上推广

2. **门店转化**
   - 静音棉产品重点做门店转化
   - 利用安装服务优势

### 中期（3-6个月）

1. **渠道策略**
   - 分析VOL渠道高线上比率原因
   - 常规产品可尝试线上引流

2. **产品策略**
   - 静音棉产品保持线下为主
   - 常规产品可增加线上曝光

3. **价格策略**
   - XX-YY元价格带适合线上销售
   - 高端产品保持线下服务优势

---

## 八、附录

### 数据来源

| 文件 | 说明 |
|------|------|
| SNX_rawdata/2025_SNX.xlsx | 2025年SNX数据 |
| SNX_rawdata/2026_SNX.xlsx | 2026年SNX数据 |
| 价格变化/20250101价格.xlsx | 2025年1月RTM底价 |
| 价格变化/20260101价格.xlsx | 2026年1月RTM底价 |
| 价格变化/20260301价格.xlsx | 2026年3月RTM底价 ⭐ 新增 |

### 分析方法

1. **规格提取**: 从Product_Description提取轮毂直径（如R18）
2. **线上判定**: Is_Eshop = 1 为线上，0 为线下
3. **CAI关联**: 使用产品独立编码精确匹配
4. **价格分析**: RTM零售商进货底价（含售出折扣）

### 关键指标

| 指标 | 说明 |
|------|------|
| 线上比率 | 线上SNX / 总SNX × 100% |
| 底价 | RTM零售商进货底价（含售出折扣） |
| 价格变化 | (2026底价 - 2025底价) / 2025底价 × 100% |
```

## 关键指标解读

| 情况 | 销量 | SNX | 解读 |
|------|------|-----|------|
| 渠道库存调整 | ↓ | ↑ | 渠道在消化库存 |
| 渠道压货 | ↑ | ↓ | 渠道库存增加 |
| 终端增长 | ↑ | ↑ | 正常增长 |
| 终端萎缩 | ↓ | ↓ | 市场需求下降 |

---

## 价格数据处理

**底价字段**：RTM零售商进货底价（含售出折扣）
- 变化率计算：(2026底价 - 2025底价) / 2025底价 × 100%
- 术语：使用"底价变化"而非"RTM变化"

---

## 📄 报告生成规则

### 支持格式

**推荐使用HTML格式**（中文显示最佳）：
- ✅ 原生支持中文，无需字体配置
- ✅ 可在手机/电脑浏览器中打开
- ✅ 支持交互式表格和图表

**PDF格式**（如需打印）：
- 使用 `generate_pdf.py` 脚本生成
- 已内置中文字体支持

### 输出路径规范

**所有报告保存在**：
```
~/Library/Mobile Documents/com~apple~CloudDocs/共享/报告/
└── [报告名称]/
    ├── [报告名称].md
    ├── [报告名称].html   ← 推荐使用
    └── [报告名称].pdf    ← 备选
```

### 生成方式

**使用脚本**：`generate_pdf.py`

```bash
cd ~/.openclaw/skills/tire-sales-analyst/

# 生成HTML报告（推荐）⭐
python3 generate_pdf.py /path/to/report.md --html

# 生成PDF报告
python3 generate_pdf.py /path/to/report.md

# 同时生成HTML和PDF
python3 generate_pdf.py /path/to/report.md --both

# 批量转换所有报告为HTML
python3 generate_pdf.py --html
```

### 报告内容要求

1. **必须有Markdown版本**（源文件）
2. **推荐生成HTML版本**（便于查看）
3. **可选PDF版本**（用于打印）
4. **图表数量**：3-5张
5. **图表类型**：
   - 柱状图（对比）
   - 折线图（趋势）
   - 饼图（占比）
   - 条形图（排名）

### 示例输出

```
共享/报告/
└── 18寸2026年1月销售报告/
    ├── 18寸2026年1月销售报告.md
    ├── 18寸2026年1月销售报告.html   ← 推荐
    ├── 18寸2026年1月销售报告.pdf    ← 备选
    ├── 图1-核心指标对比.png
    ├── 图2-渠道对比.png
    └── 图3-规格变化.png
```

---

## 🎯 专项分析：单一规格销量变化分析

> 分析特定规格（如235/50R18）从A月到B月的销量和SNX变化，诊断下滑原因

### 分析场景
- 单一规格同比/环比分析
- 诊断销量下滑原因（产品迭代？渠道问题？门店流失？）
- 包含：销量、SNX、花纹、门店、价格多维度分析
- 必须回答：哪个花纹下滑最多？门店维度SNX和销量？CAI价格变化？

### 分析模板：单一规格完整分析

```markdown
# [规格]规格销售与SNX分析报告（2025年1月 vs 2026年1月）

**分析周期**: 2025年1月 - 2026年1月
**数据维度**: [如：235/50R18 规格]
**分析重点**: 销量下滑原因诊断
**生成时间**: YYYY年MM月DD日

---

## 一、总体概览

### 销量对比

| 指标 | 2025年1月 | 2026年1月 | 变化 | 变化率 |
|------|------------|------------|------|--------|
| **总销量** | X,XXX 条 | X,XXX 条 | **-XXX 条** | **-XX%** |
| 总SNX | XXX 条 | XXX 条 | -XX 条 | -XX% |

### 核心发现

⚠️ **销量大幅下滑XX%**，但SNX仅下滑XX%，说明：
- 渠道库存调整（SNX相对稳定）
- 终端需求未大幅萎缩
- 需要进一步分析渠道和产品规格变化

---

## 二、线上/线下SNX对比

### SNX渠道分布

| 渠道 | 2025年1月 | 占比 | 2026年1月 | 占比 | 变化 |
|------|-----------|------|-----------|------|------|
| 线下 | XXX 条 | XX% | XXX 条 | XX% | -XX 条 |
| 线上 | XX 条 | X% | XX 条 | X% | +X 条 |

### 线上比率变化

| 指标 | 2025年1月 | 2026年1月 | 变化 |
|------|-----------|-----------|------|
| 线上比率 | X% | X% | **+X%** |

**洞察**：
- 线上购买比例提升X个百分点
- 消费者更倾向线上购买该规格

---

## 三、渠道维度分析

### 渠道销量对比

| 渠道 | 2025年1月 | 2026年1月 | 变化 | 变化率 |
|------|------------|------------|------|--------|
| TYREPLUS | XXX | XXX | -XXX | **-XX%** |
| MCR | XXX | XXX | +XX | +X% |
| MLD | XXX | XXX | **+XXX** | **+XX%** |
| MAR | XXX | XXX | +XX | +X% |
| MARPlus | XX | XX | -XX | -XX% |

### 渠道SNX对比

| 渠道 | 2025年1月 | 2026年1月 | 变化 |
|------|-----------|-----------|------|
| TYREPLUS | XXX | XXX | -XX |
| MCR | XX | XX | +X |
| MLD | XX | XX | -X |
| MAR | XX | XX | +X |

### 核心发现

**🚨 XX渠道（XXX）大幅下滑**
- 销量从XXX降至XXX（-XX%）
- 是整体下滑的主要贡献者
- SNX同步下降XX条（-XX%）

**✅ XX渠道逆势增长**
- 销量从XXX增至XXX（+XX%）
- 唯一正增长渠道
- 新渠道拓展见效

---

## 四、规格内部CAI分析

### CAI销量对比

| CAI | 产品描述 | 2025年1月 | 2026年1月 | 变化 | 变化率 | 评价 |
|-----|---------|------------|------------|------|--------|------|
| XXXXXX | XXXXXXXXXXXX | XXX | XXX | **-XXX** | **-XX%** | ⚠️ 下滑主因 |
| XXXXXX | XXXXXXXXXXXX | 0 | XXX | +XXX | 新增 | ⭐ 爆发 |
| XXXXXX | - | XXX | 0 | -XXX | -100% | 🔻 退出 |
| XXXXXX | XXXXXXXXXXXX | XX | XX | -XX | -XX% | 🔻 |

### 关键发现

**🔥 产品迭代导致销量下滑**

| 旧产品（下滑） | 新产品（增长） | 替代关系 |
|---------------|---------------|---------|
| XXXXX (CAI XXXXX) | XXXXX (CAI XXXXX) | **直接替代** |

**分析**：
- XXXXX (CAI XXXXX) 从XXX条降至XXX条（-XXX条）
- XXXXX (CAI XXXXX) 从0条暴增至XXX条
- 两者变化量接近（-XXX vs +XXX）
- **说明：主要是产品切换导致的统计下滑，实际市场需求稳定**

---

## 五、花纹维度分析

### 花纹销量对比

| 花纹 | 2025年1月 | 2026年1月 | 变化 | 变化率 |
|------|------------|------------|------|--------|
| XXXXX | XXX | XXX | **-XXX** | **-XX%** |
| XXXXX | 0 | XXX | +XXX | 新增 |
| 其他 | XXX | XX | -XXX | -XX% |

### 花纹SNX对比

| 花纹 | 2025年1月 | 2026年1月 | 变化 | 变化率 |
|------|-----------|-----------|------|--------|
| XXXXX | XX | XX | **-XX** | **-XX%** |
| XXXXX | 0 | XX | +XX | 新增 |
| 其他 | XX | X | -XX | -XX% |

### 🚨 花纹下滑分析

**结论：XXXX花纹下滑最多**

| 维度 | 下滑量 | 变化率 |
|------|--------|---------|
| **销量下滑** | -XXX条 | -XX% |
| **SNX下滑** | -XX条 | -XX% |

**分析**：
- XXXXX花纹是销量和SNX下滑的主要贡献者
- XXXXX花纹承接了大部分替代销量
- 实际市场并非萎缩，而是产品切换

---

## 六、门店维度分析（销量+SNX）

### 门店汇总表（销量+SNX）

| 门店名称 | 销量501 | 销量601 | 销量变化 | SNX501 | SNX601 | SNX变化 |
|---------|---------|---------|---------|---------|---------|---------|
| XXXXXXXXXXXXXX | XXX | 0 | **-XXX** | 0 | 0 | 0 |
| XXXXXXXXXXXXXX | XX | XX | -XX | XX | 0 | **-XX** |

### 下滑最严重的门店TOP10（含SNX）

| 门店名称 | 销量变化 | SNX变化 | 渠道 |
|---------|---------|---------|------|
| XXXXXXXXXXXXXX | **-XXX** | 0 | - |
| XXXXXXXXXXXXXX | **-XX** | **-XX** | MAR |
| XXXXXXXXXXXXXX | **-XX** | 0 | MLD |

### 新增/爆发门店TOP10（含SNX）

| 门店名称 | 销量变化 | SNX变化 | 渠道 |
|---------|---------|---------|------|
| XXXXXXXXXXXXXX | **+XXX** | 0 | - |
| XXXXXXXXXXXXXX | **+XXX** | 0 | - |

### 核心发现

**门店流失严重**：
- 多个门店销量归零（可能转为其他规格）
- 主要集中在杭州、温州、宁波区域
- SNX同步归零，说明终端流失

**新增门店弥补不足**：
- 新增门店贡献约XXX条增量
- 但仍不足以弥补流失门店的损失

**SNX变化显著的门店**：
- XX门店（XX渠道）：销量-XX，SNX-XX

---

## 七、CAI价格变化分析

### CAI价格对比

| CAI | 产品描述 | 2025年1月 | 2026年1月 | 价格变化 | 变化率 |
|-----|---------|-----------|-----------|---------|---------|
| XXXXXX | XXXXXXXXXXXX | XXX元 | XXX元 | **-XX元** | **-X%** |
| XXXXXX | XXXXXXXXXXXX | 无 | XXX元 | 新产品 | - |
| XXXXXX | XXXXXXXXXXXX | XXX元 | XXX元 | **-XX元** | **-X%** |

### 价格洞察

1. **XXXX (CAI XXXXX) 价格下调X%**
   - 从XXX元降至XXX元（-XX元）
   - 降价未能阻止销量下滑（-XX%）
   - 说明不是价格问题，而是产品迭代

2. **XXXX (CAI XXXXX) 新价格XXX元**
   - 新产品替代旧产品
   - 价格与旧产品持平

**结论**：价格不是销量下滑的主因，主要问题是产品迭代

---

## 八、AM区域分析

### 区域销量对比

| AM区域 | 2025年1月 | 2026年1月 | 变化 | 变化率 |
|--------|------------|------------|------|--------|
| AM-HZ1 | XXX | XXX | -XX | -XX% |
| AM-HZ2 | XX | XXX | **+XXX** | **+XXX%** ⭐ |
| AM-HZ3 | XXX | XXX | -XXX | -XX% |

### 核心发现

**✅ AM-HZ2爆发增长**
- 增长+XXX条（+XXX%）
- 可能是新增MLD客户贡献

**⚠️ AM-HZ5大幅下滑**
- 下滑-XXX条（-XX%）
- 需要重点关注

---

## 九、分月销量趋势

### 分月趋势表

| 月份 | 销量 | 环比变化 | SNX | 环比变化 |
|------|------|---------|-----|---------|
| 2025年1月 | XXX | - | XXX | - |
| 2025年2月 | XXX | -XX | XXX | -XX |
...
| 2026年1月 | XXX | -XX | XXX | +XX |

### 趋势洞察
- 2025年1月是全年峰值（XXX条）
- 2026年1月销量与2025年X-X月相当
- 整体呈下降趋势，但波动较小（±XX%）
- SNX相对稳定，说明终端需求平稳

---

## 十、核心结论

### 销量下滑原因诊断

| 原因 | 贡献度 | 说明 |
|------|--------|------|
| **产品迭代** | 主要 | XXXXX→XXXXX切换，统计口径变化 |
| 渠道调整 | 次要 | XX渠道下滑XX%，部分门店流失 |
| 季节因素 | 较小 | 1月本身是销售旺季 |

### 🚨 关键发现

**花纹层面**：
- **XXXX花纹是销量和SNX下滑的主要贡献者**
- 销量-XXX条（-XX%），SNX-XX条（-XX%）

**门店层面**：
- 流失门店销量归零，SNX同步流失
- 新增门店未能完全弥补
- XX渠道门店SNX流失明显

**价格层面**：
- XXXXX价格下调X%（-XX元）
- 价格不是下滑主因

### 实际市场判断

✅ **无需过度担忧**：
1. XXXXX (CAI XXXXX) 承接了XXXXX的销量
2. 整体市场需求稳定（SNX仅下滑XX%）
3. 新增门店持续贡献增量
4. XX渠道逆势增长XX%

### 需关注风险

⚠️ **需要关注**：
1. XX渠道大幅下滑XX%
2. 多家门店流失或转其他规格
3. XX渠道SNX流失明显
4. AM-XX区域下滑XX%
5. XX渠道虽然增长，但SNX数据不完整

---

## 十一、建议与行动

### 短期（1-3个月）

1. **渠道管理**
   - 重点关注XX渠道下滑原因
   - 排查流失门店（XXX、XXX等）
   - 评估是否需要渠道补贴

2. **产品策略**
   - 确保XXXXX供应充足
   - 监控新旧产品交替期间的市场反馈

3. **门店管理**
   - 跟进流失门店的SNX注册情况
   - 确保新增门店的SNX数据完整录入

### 中期（3-6个月）

1. **区域策略**
   - 复制AM-HZ2增长模式
   - 重点帮扶AM-XX区域

2. **门店拓展**
   - 继续开发XX渠道新客户
   - 监控新增门店的持续表现

3. **花纹策略**
   - 关注XXXXX到XXXXX的切换进度
   - 评估其他花纹的市场表现

### 长期（6-12个月）

1. **市场机会**
   - 关注EV车型配套机会
   - 监测竞品动态

2. **风险预警**
   - 避免过度依赖单一产品
   - 关注渠道结构变化

---

## 附录

### 数据来源

| 文件 | 说明 |
|------|------|
| Sales_rawdata/2025_sales.xlsx | 2025年销售数据 |
| Sales_rawdata/2026_sales.xlsx | 2026年销售数据 |
| SNX_rawdata/2025_SNX.xlsx | 2025年SNX数据 |
| SNX_rawdata/2026_SNX.xlsx | 2026年SNX数据 |
| 价格变化/20250101价格.xlsx | 2025年1月RTM底价 |
| 价格变化/20260101价格.xlsx | 2026年1月RTM底价 |
| 价格变化/20260301价格.xlsx | 2026年3月RTM底价 ⭐ 新增 |

### 分析方法

1. **规格提取**: 从Product_Description提取规格编码
2. **花纹提取**: 从Product_Description提取花纹名称
3. **CAI匹配**: 使用产品独立编码精确匹配
4. **渠道分类**: 基于Program_Type字段
5. **线上判定**: Is_Eshop = 1 为线上

### 关键指标

| 缩写 | 全称 | 说明 |
|------|------|------|
| BP | Business Plan | 销售目标 |
| SNX | Service eXperience | 终端注册 |
| T+ | TYREPLUS | 驰加渠道 |
| MLD | Multi-Label Distributor | 多标签经销商 |
| MCR | Michelin Certified Retailer | 认证零售商 |
| MAR | Michelin Authorized Retailer | 授权零售商 |
| MARPlus | Michelin Authorized Retailer Plus | 升级版授权零售商 |

---

**报告制作**: ZZH-EC
**日期**: YYYY年MM月DD日
```

### 分析代码模板

```python
import pandas as pd
import re

# 读取数据
sales_2025 = pd.read_excel('Sales_rawdata/2025_sales.xlsx')
sales_2026 = pd.read_excel('Sales_rawdata/2026_sales.xlsx')
snx_2025 = pd.read_excel('SNX_rawdata/2025_SNX.xlsx')
snx_2026 = pd.read_excel('SNX_rawdata/2026_SNX.xlsx')
rtm_202501 = pd.read_excel('价格变化/20250101价格.xlsx')
rtm_202601 = pd.read_excel('价格变化/20260101价格.xlsx')
rtm_202603 = pd.read_excel('价格变化/20260301价格.xlsx')

# 合并数据
sales = pd.concat([sales_2025, sales_2026], ignore_index=True)
snx = pd.concat([snx_2025, snx_2026], ignore_index=True)

# 提取规格
def extract_geobox(desc):
    text = str(desc).upper().replace('/', ' ').replace('-', ' ')
    match = re.search(r'(\d{3})\s*(\d{2})\s*R\s*(\d{2})', text)
    if match: return f"{match.group(1)}{match.group(2)}R{match.group(3)}"
    return None

sales['Geobox'] = sales['Product_Description'].apply(extract_geobox)
snx['Geobox'] = snx['Product_Description'].apply(extract_geobox)

# 筛选目标规格
target_spec = '23550R18'  # 替换为目标规格
sales_spec = sales[sales['Geobox'] == target_spec]
snx_spec = snx[snx['Geobox'] == target_spec]

# 筛选目标月份
sales_jan25 = sales_spec[sales_spec['ID_Month_Key'] == 202501]
sales_jan26 = sales_spec[sales_spec['ID_Month_Key'] == 202601]
snx_jan25 = snx_spec[snx_spec['ID_Month_Key'] == 202501]
snx_jan26 = snx_spec[snx_spec['ID_Month_Key'] == 202601]

# 1. 总体对比
total_sales_25 = sales_jan25['具体客户购买数'].sum()
total_sales_26 = sales_jan26['具体客户购买数'].sum()
total_snx_25 = snx_jan25['SNX'].sum()
total_snx_26 = snx_jan26['SNX'].sum()

# 2. 渠道对比
prog_sales_25 = sales_jan25.groupby('Program_Type')['具体客户购买数'].sum()
prog_sales_26 = sales_jan26.groupby('Program_Type')['具体客户购买数'].sum()

# 3. 花纹分析
def extract_pattern(desc):
    text = str(desc).upper()
    if 'PRIMACY' in text:
        if '5' in text and '4' not in text: return 'PRIMACY 5'
        elif '4' in text: return 'PRIMACY 4'
        return 'PRIMACY'
    elif 'PILOT SPORT' in text:
        if '4' in text: return 'PILOT SPORT 4'
        return 'PILOT SPORT'
    elif 'E PRIMACY' in text:
        return 'E PRIMACY'
    elif 'CROSSCLIMATE' in text:
        return 'CROSSCLIMATE'
    return '其他'

sales_jan25['Pattern'] = sales_jan25['Product_Description'].apply(extract_pattern)
sales_jan26['Pattern'] = sales_jan26['Product_Description'].apply(extract_pattern)

pat_sales_25 = sales_jan25.groupby('Pattern')['具体客户购买数'].sum()
pat_sales_26 = sales_jan26.groupby('Pattern')['具体客户购买数'].sum()

# 4. SNX花纹对比
snx_jan25['Pattern'] = snx_jan25['Product_Description'].apply(extract_pattern)
snx_jan26['Pattern'] = snx_jan26['Product_Description'].apply(extract_pattern)

pat_snx_25 = snx_jan25.groupby('Pattern')['SNX'].sum()
pat_snx_26 = snx_jan26.groupby('Pattern')['SNX'].sum()

# 5. 门店维度（销量+SNX）
dealer_sales_25 = sales_jan25.groupby('DealerName')['具体客户购买数'].sum()
dealer_sales_26 = sales_jan26.groupby('DealerName')['具体客户购买数'].sum()
dealer_snx_25 = snx_jan25.groupby('DealerName')['SNX'].sum()
dealer_snx_26 = snx_jan26.groupby('DealerName')['SNX'].sum()

dealer_full = pd.DataFrame({
    '销量501': dealer_sales_25,
    '销量601': dealer_sales_26,
    'SNX501': dealer_snx_25,
    'SNX601': dealer_snx_26
})
dealer_full['销量变化'] = dealer_full['销量601'] - dealer_full['销量501']
dealer_full['SNX变化'] = dealer_full['SNX601'] - dealer_full['SNX501']

# 6. CAI价格变化
price_col = 'RTM\n零售商进货\n底价\n(含售出折扣)'
cai_list = sales_jan26['Cai'].unique()

for cai in cai_list:
    row_25 = rtm_202501[rtm_202501['CAI'] == cai]
    row_26 = rtm_202601[rtm_202601['CAI'] == cai]
    if len(row_25) > 0 and len(row_26) > 0:
        price_25 = row_25[price_col].values[0]
        price_26 = row_26[price_col].values[0]
        change = price_26 - price_25
```

### 必须回答的问题

当分析单一规格销量变化时，必须回答：

| 问题 | 分析方法 |
|------|----------|
| **1. 具体哪个花纹下滑最多？** | 按Product_Description提取花纹，比较销量和SNX变化 |
| **2. 门店维度看SNX和销量？** | 按DealerName汇总销量和SNX，对比变化 |
| **3. 每个CAI价格有没有变化？** | 关联RTM价格数据，比较2025→2026底价变化 |

---

## 🎯 专项分析：行业宏观数据获取（Tushare）

> 使用Tushare Pro获取轮胎行业相关的宏观经济数据和期货数据

### Tushare配置

```python
import tushare as ts

# Token配置
token = '3474c836e690df5c51d0faa5263c2211077043b27f86e5a80f4aa5bd'
ts.set_token(token)
pro = ts.pro_api()
```

### 可获取的数据类型

| 数据类型 | 代码 | 说明 | 与轮胎行业相关性 |
|---------|------|------|----------------|
| 天然橡胶期货 | `fut_daily(ts_code='RU.SHF')` | 上海期货交易所 | ⭐⭐⭐ 直接相关 |
| 合成橡胶期货 | `fut_daily(ts_code='BR.SHF')` | 上海期货交易所 | ⭐⭐⭐ 直接相关 |
| 螺纹钢期货 | `fut_daily(ts_code='RB.SHF')` | 上海期货交易所 | ⭐⭐ 基建/汽车 |
| 沪铜期货 | `fut_daily(ts_code='CU.SHF')` | 上海期货交易所 | ⭐⭐ 经济指标 |
| 白银期货 | `fut_daily(ts_code='AG.SHF')` | 上海期货交易所 | ⭐ 贵金属 |
| 玲珑轮胎 | `daily(ts_code='601966.SH')` | 上海证券交易所 | ⭐⭐⭐ 行业标的 |
| 贵州轮胎 | `daily(ts_code='600759.SH')` | 上海证券交易所 | ⭐⭐ 行业标的 |

### 数据获取示例

```python
import pandas as pd

# 1. 获取橡胶期货数据
ru = pro.fut_daily(ts_code='RU.SHF', start_date='20250101', end_date='20260131')
br = pro.fut_daily(ts_code='BR.SHF', start_date='20250101', end_date='20260131')

# 2. 获取螺纹钢数据
rb = pro.fut_daily(ts_code='RB.SHF', start_date='20250101', end_date='20260131')

# 3. 获取轮胎概念股
lyl = pro.daily(ts_code='601966.SH', start_date='20250101', end_date='20260131')
gz = pro.daily(ts_code='600759.SH', start_date='20250101', end_date='20260131')

# 4. 计算月度统计数据
def monthly_stats(df, price_col='close'):
    df['month'] = df['trade_date'].astype(str).str[:6]
    monthly = df.groupby('month').agg({
        price_col: ['first', 'last', 'mean', 'min', 'max']
    }).round(2)
    monthly.columns = ['期初', '期末', '均价', '最低', '最高']
    return monthly

print("天然橡胶月均价格:")
print(monthly_stats(ru))

print("\n玲珑轮胎月表现:")
lyl['month'] = lyl['trade_date'].astype(str).str[:6]
lyl_monthly = lyl.groupby('month').agg({'close': ['first', 'last', 'mean'], 'pct_chg': ['mean', 'sum']}).round(2)
print(lyl_monthly)
```

### 数据保存

```python
import json

# 保存数据到CSV
base_path = '~/Library/Mobile Documents/com~apple~CloudDocs/共享/行业数据'
ru.to_csv(f'{base_path}/RU_SHF.csv', index=False)

# 保存汇总
data_summary = {
    '天然橡胶': {'code': 'RU.SHF', 'latest_price': ru.iloc[-1]['close']},
    '玲珑轮胎': {'code': '601966.SH', 'latest_price': lyl.iloc[-1]['close']}
}
with open(f'{base_path}/data_summary.json', 'w', encoding='utf-8') as f:
    json.dump(data_summary, f, ensure_ascii=False, indent=2)
```

### 数据可视化

```python
import matplotlib.pyplot as plt

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 绘制价格走势图
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 天然橡胶
axes[0,0].plot(ru['trade_date'], ru['close'], 'b-', label='天然橡胶')
axes[0,0].set_title('天然橡胶期货价格走势')
axes[0,0].set_xlabel('日期')
axes[0,0].set_ylabel('价格(元/吨)')

# 合成橡胶
axes[0,1].plot(br['trade_date'], br['close'], 'r-', label='合成橡胶')
axes[0,1].set_title('合成橡胶期货价格走势')
axes[0,1].set_xlabel('日期')
axes[0,1].set_ylabel('价格(元/吨)')

# 轮胎股价对比
axes[1,0].plot(lyl['trade_date'], lyl['close'], 'g-', label='玲珑轮胎')
axes[1,0].plot(gz['trade_date'], gz['close'], 'm-', label='贵州轮胎')
axes[1,0].set_title('轮胎概念股股价走势')
axes[1,0].set_xlabel('日期')
axes[1,0].set_ylabel('股价(元)')
axes[1,0].legend()

# 螺纹钢
axes[1,1].plot(rb['trade_date'], rb['close'], 'orange', label='螺纹钢')
axes[1,1].set_title('螺纹钢期货价格走势')
axes[1,1].set_xlabel('日期')
axes[1,1].set_ylabel('价格(元/吨)')

plt.tight_layout()
plt.savefig('轮胎行业宏观分析.png', dpi=150)
plt.show()
```

### 报告生成模板

```markdown
# 轮胎原材料与相关市场月度分析报告

**报告周期**: YYYY年MM月
**数据来源**: Tushare Pro
**生成时间**: YYYY年MM月DD日

---

## 一、报告摘要

### 核心指标概览

| 指标 | 本期 | 环比变化 | 同比变化 |
|------|------|---------|---------|
| 天然橡胶均价 | XX,XXX元/吨 | +X.X% | +X.X% |
| 合成橡胶均价 | XX,XXX元/吨 | +X.X% | +X.X% |
| 螺纹钢均价 | X,XXX元/吨 | +X.X% | +X.X% |
| 玲珑轮胎股价 | XX.XX元 | +X.X% | +X.X% |
| 贵州轮胎股价 | X.XX元 | +X.X% | +X.X% |

---

## 二、天然橡胶市场分析

### 价格走势

| 月份 | 期初价 | 期末价 | 月均价 | 环比 |
|------|--------|--------|--------|------|
| 202501 | 17,450 | 17,575 | 17,208 | - |
| 202502 | 17,710 | 17,065 | 17,662 | +6.7% |
...

### 趋势分析

- 月均价：17,662元/吨
- 环比上涨：+6.7%
- 驱动因素：...

---

## 三、产业链成本分析

### 原材料成本占比

| 原材料 | 占比 | 本期价格 | 变化趋势 |
|--------|------|---------|---------|
| 天然橡胶 | ~40% | 17,662元/吨 | ⬆️ 上涨 |
| 合成橡胶 | ~15% | 14,213元/吨 | ⬆️ 上涨 |
| 螺纹钢 | ~10% | 3,317元/吨 | ⬆️ 上涨 |

---

## 四、数据来源

| 数据类型 | 来源 | 接口 |
|---------|------|------|
| 天然橡胶期货 | 上海期货交易所 | `pro.fut_daily(ts_code='RU.SHF')` |
| 合成橡胶期货 | 上海期货交易所 | `pro.fut_daily(ts_code='BR.SHF')` |
| 螺纹钢期货 | 上海期货交易所 | `pro.fut_daily(ts_code='RB.SHF')` |
| 玲珑轮胎 | 上海证券交易所 | `pro.daily(ts_code='601966.SH')` |
| 贵州轮胎 | 上海证券交易所 | `pro.daily(ts_code='600759.SH')` |

---

**报告制作**: ZZH-EC
**生成时间**: YYYY年MM月DD日
```

---

## 🎯 专项分析：复现Intelligence Hub行业报告

> 复现咨询部门行业报告，自动生成中英文双语报告

### 报告结构分析

**Intelligence Hub 报告标准结构**：

```
Intelligence Hub (CN)_YYYYMM.pdf
├── 封面（报告编号、部门、密级）
├── 摘要/执行摘要
├── 第一部分：宏观环境（GDP、社零、PPI、政策）
├── 第二部分：上游产业（橡胶、钢材等原材料）
├── 第三部分：轮胎市场（产量、销量、出口、价格）
├── 第四部分：渠道分析（后市场、门店、电商）
├── 第五部分：竞争格局（主要品牌动态、新品）
├── 第六部分：汽车市场（乘用车、商用车、新能源）
├── 第七部分：数据附录
├── 第八部分：趋势展望
└── 附录：英文版
```

### 复现步骤

```python
import PyPDF2
import pandas as pd

# 1. 读取原报告
pdf_path = '/path/to/Intelligence Hub (CN)_2601.pdf'
with open(pdf_path, 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    for page in reader.pages:
        text = page.extract_text()
        print(text)

# 2. 分析报告结构
def analyze_structure(text):
    chapters = []
    for i, line in enumerate(text.split('\n')):
        if any(kw in line for kw in ['宏观', '上游', '轮胎', '渠道', '竞争', '汽车', '附录', '摘要']):
            chapters.append((i, line))
    return chapters

# 3. 提取关键数据
def extract_data(text):
    import re
    # 提取数字数据
    numbers = re.findall(r'[\d,.]+', text)
    # 提取百分比
    percentages = re.findall(r'[\d.]+%', text)
    return numbers, percentages
```

### 复现报告模板

```markdown
# Intelligence Hub - YYYY年MM月轮胎行业月度报告

**报告编号**: Intelligence Hub (CN)_YYMM
**报告周期**: YYYY年MM月
**编制部门**: 市场洞察部
**密级**: D3

---

## 摘要 (Executive Summary)

### 核心发现

1. **宏观经济**：...
2. **政策动态**：...
3. **原材料价格**：...
4. **轮胎市场**：...
5. **渠道变化**：...

### 关键指标

| 指标 | 本期 | 环比 | 同比 |
|------|------|------|------|
| 天然橡胶 | XX,XXX元/吨 | +X.X% | +X.X% |
| 合成橡胶 | XX,XXX元/吨 | +X.X% | +X.X% |
| 螺纹钢 | X,XXX元/吨 | +X.X% | +X.X% |

---

## 第一部分：宏观环境

### 1.1 经济增长情况

- **GDP**：XXXX年全年增长X.X%，...
- **社零**：全年同比增速X.X%，...
- **PPI**：...

### 1.2 政策动态

#### "两新"政策延续

[政策内容摘要]

#### 汽车以旧换新

[政策数据]

### 1.3 大宗商品市场

[大宗商品指数数据]

---

## 第二部分：上游产业

### 2.1 橡胶原材料价格走势

#### 天然橡胶

| 月份 | 期初价 | 期末价 | 月均价 | 环比 |
|------|--------|--------|--------|------|
| 202601 | XX,XXX | XX,XXX | XX,XXX | - |
| 202602 | XX,XXX | XX,XXX | XX,XXX | +X.X% |

#### 合成橡胶

[数据表格]

### 2.2 钢材价格走势

[螺纹钢数据]

### 2.3 产业链成本分析

| 原材料 | 成本占比 | 价格 | 变化 | 影响 |
|--------|---------|------|------|------|
| 天然橡胶 | ~40% | XX,XXX元/吨 | +X.X% | ⚠️ |
| 合成橡胶 | ~15% | XX,XXX元/吨 | +X.X% | ⚠️ |

---

## 第三部分：轮胎市场

### 3.1 产量与销量

| 轮胎类型 | 产量/销量 | 同比 |
|---------|-----------|------|
| 乘用车轮胎 | XXX百万条 | -X.X% |
| 卡客车轮胎 | XXX万吨 | +X.X% |

### 3.2 出口市场

- **欧盟关税**：对华轮胎关税暂停6个月（后续待观察）
- **墨西哥关税**：2026年1月1日起加征25-35%

### 3.3 经销商价格

- **轿车轮胎**：环比+X.XX%
- **卡客车轮胎**：环比-X.XX%

---

## 第四部分：渠道分析

### 4.1 后市场渠道

- **德国马牌 × 京东养车**：深化合作，配送时效升级
- **百世德**：第X,XXX家门店开业

### 4.2 线上购买行为

[基于SNX数据分析]

---

## 第五部分：竞争格局

### 5.1 主要品牌动态

| 品牌 | 动态 | 战略方向 |
|------|------|---------|
| 米其林 | ... | 高端化 |
| 倍耐力 | ... | 工业轮胎 |
| 德国马牌 | ... | 数字化 |
| 中策 | ... | 高端化 |

### 5.2 产能变化

| 项目 | 状态 | 产能 |
|------|------|------|
| XX工厂 | 在建/投产 | XX万套 |

### 5.3 新品发布

| 品牌 | 产品 | 特点 |
|------|------|------|
| XX | XXX | XXX |

---

## 第六部分：汽车市场

### 6.1 乘用车市场

- **产量/销量**：待获取
- **新能源渗透率**：超XX%

### 6.2 商用车市场

- **产量/销量**：同比+X.X%
- **智能化趋势**：L3/L4自动驾驶

---

## 第七部分：数据附录

### Tushare可获取数据

| 数据类型 | 代码 | 相关性 |
|---------|------|--------|
| 天然橡胶 | `fut_daily(ts_code='RU.SHF')` | ⭐⭐⭐ |
| 合成橡胶 | `fut_daily(ts_code='BR.SHF')` | ⭐⭐⭐ |
| 螺纹钢 | `fut_daily(ts_code='RB.SHF')` | ⭐⭐ |
| 玲珑轮胎 | `daily(ts_code='601966.SH')` | ⭐⭐⭐ |

---

## 第八部分：趋势展望

### 短期（1-3个月）

| 趋势 | 预测 | 置信度 |
|------|------|--------|
| 天然橡胶 | 区间震荡 | 75% |
| 轮胎出口 | 结构分化 | 70% |

### 中期（3-6个月）

1. 欧盟关税政策走向
2. 墨西哥关税影响评估
3. EV轮胎需求增长

### 长期趋势

- 轮胎高端化
- 渠道数字化
- 国际化出海
- EV专用化

---

## English Version

[中英双语版本]

---

**报告制作**: ZZH-EC
**数据来源**: Tushare Pro、中汽协、海关总署
**生成时间**: YYYY年MM月DD日
```

### 复现示例：Intelligence Hub 2026年2月

```python
# 读取原报告
pdf_path = '/Users/xxx/CloudDocs/共享/Report From Mint/Intelligence Hub (CN)_2601.pdf'

# 提取结构
structure = {
    'chapters': [
        '宏观环境', '上游产业', '轮胎市场', 
        '渠道', '竞争格局', '汽车市场'
    ],
    'key_pages': {
        '产量数据': [15, 20],
        '价格数据': [22, 25],
        '品牌动态': [26, 30],
        '政策信息': [11, 14]
    }
}

# 生成复现报告
generate_report(
    template='intelligence_hub_template.md',
    data=tushare_data,
    structure=structure,
    output='Intelligence_Hub_CN_2602.md'
)
```

### 权威数据来源

| 数据类型 | 来源 | 获取方式 |
|---------|------|---------|
| 汽车销量 | 中汽协 | Tushare/API |
| 轮胎进出口 | 海关总署 | Tushare/API |
| 期货价格 | 上海期货交易所 | Tushare |
| 股价数据 | 交易所 | Tushare |
| 政策信息 | 发改委/商务部 | 官网/新闻 |
| 行业动态 | 咨询报告 | PDF文档 |

---

*Author: ZZH-EC*
*Last Updated: 2026-03-08*
*Version: 2.1.0 - 2026年3月文件结构更新*

---

## 📈 月度报告结构（V2.23.0 - MD版 v2）

### 数据来源

**SQLite数据库**: `~/.openclaw/workspace/sales_analysis.db`

**数据表**:
- `sales` - 销售数据（77,989行）
- `snx` - SNX注册数据（56,600行）
- `product_category` - 产品分类（3,389行）

### 报告版本历史

- **V2.23.0 (MD版 v2)** - 2026年2月更新
  - 新增 SNX匹配度 指标
  - 新增 尺寸维度分析（销量+SNX双维度）
  - 新增 18寸下滑深度分析
  - 新增 渠道表现（零售渠道+SNX验证）
  - 新增 关键行动建议

- **V2.22.0** - 基础版本

### 尺寸定义

**尺寸（寸口）** 来自 `product_category` 表的 `CN Seg` 字段：
- MI15- = 15寸及以下
- MI16 = 16寸
- MI17 = 17寸
- MI18 = 18寸
- MI19 = 19寸
- MI20 = 20寸
- MI21+ = 21寸及以上

### 报告结构（V2.23.0 MD版 v2）

> 基于用户提供：2026年1月浙江轮胎销售分析报告（MD版 v2）

#### 报告标题格式
```
# 2026年1月浙江轮胎销售分析报告（MD版 v2）
> 数据来源：2026_sales.xlsx（ID_Month_Key=202601）
> 总销量：35,621条 | SNX注册量：22,450条
> 区域范围：浙江省（Dealer_ID以DEALER_HZ_开头）
```

#### 一、总量概览（含SNX验证）

| 指标 | 本月 | 环比 | 同比 | SNX匹配度 |
|------|------|------|------|-----------|
| 总销量 | ✅ | ✅ | ✅ | ✅ |
| SNX注册量 | ✅ | ✅ | ✅ | - |

> 💡 需求真实性：零售渠道SNX匹配度达108.3%（健康），批发渠道不适用

#### 二、尺寸表现（销量+SNX双维度）

| 尺寸 | 销量 | 销量环比 | 销量同比 | SNX量 | SNX环比 | SNX同比 | 趋势 |
|------|------|----------|----------|-------|---------|---------|------|
| 19寸 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 📈 爆发 |
| 20寸 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 📈 健康 |
| 21寸+ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 📈 翻倍 |
| 16寸 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ 稳定 |
| 18寸 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🔴 萎缩 |

#### 三、18寸下滑深度分析

##### TOP5问题CAI（含渠道+SNX）

| CAI | 产品描述 | 销量 | 渠道分布 | SNX量 | 销量同比 | SNX同比 |
|-----|----------|------|----------|-------|----------|---------|
| CAI002 | 235/50R18 PRIMACY 4 ST | ✅ | 批发72% | ✅ | -45% | -48% |
| CAI003 | 235/45ZR18 PILOT SPORT 4 | ✅ | 零售68% | ✅ | -54% | -57% |

> 🔍 核心发现：
> - 批发渠道主导下滑（占问题CAI销量62%）
> - SNX同步萎缩（所有CAI的SNX同比跌幅＞销量跌幅）

#### 四、渠道表现（零售渠道+SNX验证）

##### 零售渠道SNX匹配度

| 渠道类型 | 销量 | SNX量 | 匹配度 | 销量环比 | SNX环比 | 销量同比 | SNX同比 |
|----------|------|-------|--------|----------|---------|----------|---------|
| TYREPLUS | ✅ | ✅ | 107.6% | ✅ | ✅ | ✅ | ✅ |
| 非驰加零售 | ✅ | ✅ | 108.2% | ✅ | ✅ | ✅ | ✅ |

##### 批发渠道（无SNX）

| 渠道 | 销量 | 环比 | 同比 | 核心客户 |
|------|------|------|------|----------|
| FDD | ✅ | ✅ | ✅ | DEALER_HZ_FDD_001 |
| MLD | ✅ | ✅ | ✅ | DEALER_HZ_MLD_003 |

#### 五、关键行动建议

1. **18寸紧急干预**：
   - 批发渠道：减少PRIMACY 4 ST库存（清仓占比28%）
   - 零售渠道：加强PILOT SPORT 4终端促销（SNX跌幅＞销量）

2. **复制FDD成功模式**：
   - 分析DEALER_HZ_FDD_001的529%增长驱动因素
   - 向MLD渠道推广相同策略

3. **监控清仓风险**：
   - 18寸清仓占比28%（超均值12.3%）
   - 需防止价格体系混乱

### 分析原则

1. **两个分析方向**：
   - 产品方向：总量 → 尺寸(寸口) → 规格 → CAI(产品描述)
   - 渠道方向：总量 → 渠道 → 客户

2. **优先关注**：
   - 销量高但环比/同比下降的规格和CAI
   - 变化幅度异常的数据点
   - SNX与销量变化不一致的情况（判断真实需求）

3. **数据完整性**：
   - 每个维度都需要包含：销量+SNX，环比+同比

4. **SNX匹配度计算**：
   - 零售渠道：SNX匹配度 = SNX / 销量 × 100%
   - 健康范围：95%-110%
   - >110%：渠道库存减少
   - <95%：渠道库存增加

---

*Author: ZZH-EC*
*Last Updated: 2026-02-26*
*Version: 2.23.0 - MD版 v2 更新*

---

## 📋 单一规格分析标准模板

> 用于分析特定规格（如235/50R18）销售数据的标准格式
> 版本：2026-02-27

### 必须包含的数据维度

1. **总量**：销量 + SNX，含同比和环比
2. **渠道**：渠道销量 + SNX，含同比和环比
3. **CAI**：CAI销量 + SNX，含同比

### 报告结构

```markdown
# {规格} 规格销售分析

---

## 一、总量

| 指标 | {年份-1}年1月 | {年份-1}年12月 | {年份}年1月 | 同比 | 同比% | 环比 | 环比% |
|------|---------------|-----------------|-------------|------|-------|------|-------|
| 销量 | X,XXX | X,XXX | X,XXX | +X,XXX | +XX% | +X,XXX | +XX% |
| SNX | X,XXX | X,XXX | X,XXX | +X,XXX | +XX% | +X,XXX | +XX% |

> 💡 核心洞察：...

---

## 二、渠道分析

### 渠道销量

| 渠道 | {年份-1}年1月 | {年份-1}年12月 | {年份}年1月 | 同比 | 环比 |
|------|---------------|-----------------|-------------|------|------|
| TYREPLUS | X | X | X | +X | +X |
| MCR | X | X | X | +X | +X |
| MLD | X | X | X | +X | +X |
| FDD | X | X | X | +X | +X |

### 渠道SNX

| 渠道 | {年份-1}年1月 | {年份-1}年12月 | {年份}年1月 | 同比 | 环比 |
|------|---------------|-----------------|-------------|------|------|
| TYREPLUS | X | X | X | +X | +X |
| MCR | X | X | X | +X | +X |

---

## 三、CAI分析

| CAI | 产品 | {年份-1}年1月 | {年份-1}年12月 | {年份}年1月 | 同比 | SNX_{年份}年1月 |
|-----|------|---------------|-----------------|-------------|------|-----------------|
| XXXXXX | XXXXXXXXX | X | X | X | +X | X |

---

## 四、结论

✅ 增长因素：
- 渠道A：销量+X
- 产品B：增长+X

⚠️ 下滑因素：
- 渠道C：销量-X

---

**数据来源**：
- 销售数据：~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/Sales_rawdata/
- SNX数据：~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/SNX_rawdata/
```

---

## 📋 尺寸销售分析报告（更新版 2026-02-28）

### 报告结构

```markdown
# 2026年1月 18寸轮胎销售分析报告

> 数据来源：2026_sales.xlsx、2025_sales.xlsx、SNX数据

---

## 一、总量概览

| 指标 | 2025年12月 | 2025年1月 | 2026年1月 | 同比变化 | 同比% | 环比变化 | 环比% |
|------|------------|-----------|-----------|----------|-------|----------|-------|
| 销量 | X,XXX | X,XXX | X,XXX | +X,XXX | +XX% | +X,XXX | +XX% |
| SNX | X,XXX | X,XXX | X,XXX | +X,XXX | +XX% | +X,XXX | +XX% |

---

## 二、规格维度分析

### 销量TOP10规格

| 排名 | 规格 | 2025年1月 | 2026年1月 | 同比 | 环比 |2025年1月SNX | 2026年1月SNX | 同比（SNX） | 环比 （SNX）|
|------|------|-----------|-----------|------|------|-----------|-----------|------|------|
| 1 | 235/50R18 | X | X | +X | +X | X | X | +X | +X |

### SNX TOP10规格

| 排名 | 规格 | 2025年1月SNX | 2026年1月SNX | 同比 |2025年1月 | 2026年1月 | 同比
|------|------|--------------|--------------|------|--------------|--------------|------|
| 1 | 235/50R18 | X | X | +X |X | X | +X |

---

## 三、渠道维度分析

### 渠道销量

| 渠道 | 2025年1月 | 2026年1月 | 同比 | 环比 |
|------|-----------|-----------|------|------|
| TYREPLUS | X | X | +X | +X |
| MCR | X | X | +X | +X |
| MLD | X | X | +X | +X |
| FDD | X | X | +X | +X |

### 渠道SNX

| 渠道 | 2025年1月 | 2026年1月 | 同比 | 环比 |
|------|-----------|-----------|------|------|
| TYREPLUS | X | X | +X | +X |
| MCR | X | X | +X | +X |

---

## 四、CAI产品TOP10

| 排名 | CAI | 产品名称 | 2025年1月 | 2026年1月 | 同比 | SNX |
|------|-----|---------|-----------|-----------|------|-----|
| 1 | 326966 | 235/50 R18 97W TL PRIMACY 4 ST MI | X | X | +X | X |

---

## 五、Dealer门店TOP10

| 排名 | 门店 | 2025年1月 | 2026年1月 | 同比 | SNX |
|------|------|-----------|-----------|------|-----|
| 1 | XXX | X | X | +X | X |

---

## 六、核心结论

### 增长驱动因素
1. XX渠道爆发：贡献X条增量

### 关注点
1. XX渠道下滑 -XX%

### 行动建议
1. 复制XX成功模式
```

### 关键更新点

1. **规格维度**：销量TOP10表格增加SNX列，同步展示销量和SNX
2. **SNX维度**：新增独立的SNX TOP10规格表
3. **渠道维度**：销量和SNX分开表格呈现
4. **CAI维度**：产品名称使用完整描述（含规格）
```
