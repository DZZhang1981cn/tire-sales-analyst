# 🛞 轮胎销售数据分析技能 - 使用指南

**创建日期：2026年02月13日**
**作者：ZZH-EC**

---

## 一、技能概述

这是一个专门用于分析米其林轮胎销售数据的技能，支持：
- ✅ 销售数据分析（销量、出货）
- ✅ SNX注册分析（终端零售）
- ✅ 多维度分析（渠道、规格、Dealer、AM区域）
- ✅ 自动生成PDF报告（带图表）

---

## 二、文件结构

```
tire-sales-analyst/
├── SKILL.md              # 技能说明和使用模板
├── generate_report.py    # PDF报告生成脚本
└── README.md            # 使用指南（本文档）
```

**报告输出目录：**
```
~/Library/Mobile Documents/com~apple~CloudDocs/共享/报告/
└── [报告名称]/
    ├── [报告名称].pdf           # PDF版本（带图表）
    ├── [报告名称].md           # Markdown版本
    ├── 图1-xxx.png            # 图表1
    ├── 图2-xxx.png            # 图表2
    └── 图3-xxx.png            # 图表3
```

---

## 三、快速开始

### 方式1：自然语言分析

直接用自然语言告诉我你的分析需求，例如：
- "分析18寸轮胎2026年1月销售情况"
- "对比MCR和TYREPLUS渠道的SNX变化"
- "查看规格235/45R18的销量趋势"

### 方式2：生成完整PDF报告

```bash
# 终端执行
cd ~/.openclaw/skills/tire-sales-analyst/
python3 generate_report.py
```

---

## 四、数据文件位置

```
~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/
├── Sales_rawdata/
│   ├── 2025_sales.xlsx   # 2025年销售出货数据
│   └── 2026_sales.xlsx   # 2026年销售出货数据
└── SNX_rawdata/
    ├── 2025_SNX.xlsx     # 2025年SNX注册数据
    └── 2026_SNX.xlsx     # 2026年SNX注册数据
```

---

## 五、常用分析命令

### 1. 基础分析（18寸轮胎专题）

```python
import pandas as pd

# 读取数据
sales = pd.read_excel("~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/Sales_rawdata/2026_sales.xlsx")

# 筛选18寸轮胎
df_18 = sales[sales['Product_Description'].str.contains('R18', na=False)]

# 2026年1月数据
jan_2026 = df_18[df_18['ID_Month_Key'] == 202601]
```

### 2. 渠道对比

```python
# 按渠道汇总
prog_summary = jan_2026.groupby('Program_Type')['具体客户购买数'].sum()

# 支持的渠道：
# MCR, MLD, FDD, TYREPLUS, MPC, MAR, MARPlus, BOC
```

### 3. SNX分析

```python
snx = pd.read_excel("~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/SNX_rawdata/2026_SNX.xlsx")
snx_18 = snx[snx['Product_Description'].str.contains('R18', na=False)]

# SNX代表终端真实零售
snx_summary = snx_18.groupby('Program_Type')['SNX'].sum()
```

### 4. 规格维度

```python
# 提取规格（如 235/45R18）
df['规格'] = df['Product_Description'].str.extract(
    r'(\d+)/(\d+)\s*[RZ]?\s*(\d+)'
)[0] + '/' + df['Product_Description'].str.extract(
    r'(\d+)/(\d+)\s*[RZ]?\s*(\d+)'
)[1] + 'R' + df['Product_Description'].str.extract(
    r'(\d+)/(\d+)\s*[RZ]?\s*(\d+)'
)[2]

# 按规格汇总
spec_summary = jan_2026.groupby('规格')['具体客户购买数'].sum()
```

### 5. Dealer分析

```python
# 按Dealer汇总
dealer_summary = jan_2026.groupby('DealerName')['具体客户购买数'].sum()

# 查看下降的Dealer
dealer_summary.sort_values(ascending=True).head(20)
```

---

## 六、PDF报告模板

### 标准报告结构

```markdown
# [报告标题]

**日期**: YYYY年MM月DD日

## 一、核心指标
| 指标 | 数值 | 变化 |
|------|------|------|

## 二、渠道/规格/Dealer维度分析
（图表 + 数据）

## 三、关键发现
1. 发现1
2. 发现2

## 四、建议
1. 建议1
```

### 图表类型

| 图表 | 用途 | 示例 |
|------|------|------|
| 柱状图 | 对比两组数据 | 2025 vs 2026 销量对比 |
| 折线图 | 趋势变化 | 月度销量趋势 |
| 饼图 | 占比分析 | 渠道销量占比 |
| 条形图 | 排名分析 | TOP 10规格 |

---

## 七、示例：生成完整报告

### 1. 创建报告目录

```bash
mkdir -p "/Users/你的用户名/Library/Mobile Documents/com~apple~CloudDocs/共享/报告/18寸2026年1月销售报告"
```

### 2. 运行报告生成脚本

```bash
cd ~/.openclaw/skills/tire-sales-analyst/
python3 generate_report.py
```

### 3. 生成的报告包含

```
18寸2026年1月销售报告/
├── 18寸2026年1月销售报告.pdf      # 207KB（完整版）
├── 18寸2026年1月销售报告.md       # 1.1KB
├── 图1-核心指标对比.png            # 49KB
├── 图2-渠道对比.png               # 61KB
└── 图3-规格变化.png               # 61KB
```

---

## 八、关键洞察要点

### 销量 vs SNX 的解读

| 情况 | 解读 |
|------|------|
| 销量↓ + SNX↑ | **渠道在消化库存**，终端需求好 |
| 销量↑ + SNX↑ | **健康增长**，渠道补货+终端需求 |
| 销量↑ + SNX↓ | **渠道压货**，终端需求弱 |
| 销量↓ + SNX↓ | **双重下降**，需警惕 |

---

## 九、常见问题

### Q1: 如何分析其他月份？
```python
# 将 ID_Month_Key 改为对应月份
df[df['ID_Month_Key'] == 202602]  # 2026年2月
df[df['ID_Month_Key'] == 202505]  # 2025年5月
```

### Q2: 如何分析非18寸轮胎？
```python
# 移除筛选条件
df_all = sales  # 所有轮胎
# 或筛选其他尺寸
df_17 = sales[sales['Product_Description'].str.contains('R17', na=False)]
```

### Q3: 报告生成失败怎么办？
```bash
# 1. 检查数据文件是否存在
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/共享/销售分析/Sales_rawdata/

# 2. 重新运行
python3 generate_report.py
```

---

## 十、快捷指令

在飞书中直接发消息：

| 需求 | 消息内容 |
|------|----------|
| 生成18寸分析报告 | "生成18寸2026年1月销售报告" |
| 查看MCR渠道 | "分析MCR渠道销量" |
| 查看规格排名 | "查看规格销量TOP10" |
| 查看Dealer下降 | "查看销量下降的Dealer" |

---

## 十一、更新日志

| 日期 | 更新内容 |
|------|----------|
| 2026-02-13 | 初始版本，支持18寸分析、PDF报告生成 |

---

## 十二、注意事项

1. **SNX代表终端零售**，销量代表渠道出货
2. **iCloud同步**：报告生成在本地，需要等iCloud同步后才能在手机端看到
3. **Python库**：需要安装 pandas、matplotlib、reportlab

### 安装Python库
```bash
pip3 install pandas matplotlib reportlab
```

---

*最后更新：2026年02月13日*
*技能版本：1.0.0*
