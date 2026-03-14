#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
18寸轮胎 2026年1月销售报告 - PDF版本
生成带图表的销售分析报告
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 无GUI后端
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 输出目录
OUTPUT_DIR = "/Users/zhangzhenhua/Library/Mobile Documents/com~apple~CloudDocs/共享/报告/18寸2026年1月销售报告"

print("=" * 70)
print("18寸轮胎 2026年1月销售报告 - PDF版本")
print("=" * 70)

# 读取数据
print("\n1. 读取数据...")
sales_2025 = pd.read_excel("~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/Sales_rawdata/2025_sales.xlsx")
sales_2026 = pd.read_excel("~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/Sales_rawdata/2026_sales.xlsx")
snx_2025 = pd.read_excel("~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/SNX_rawdata/2025_SNX.xlsx")
snx_2026 = pd.read_excel("~/Library/Mobile Documents/com~apple~CloudDocs/共享/销售分析/SNX_rawdata/2026_SNX.xlsx")

# 合并数据
sales = pd.concat([sales_2025, sales_2026], ignore_index=True)
snx = pd.concat([snx_2025, snx_2026], ignore_index=True)

# 筛选18寸
sales_18 = sales[sales['Product_Description'].str.contains('R18', na=False)]
snx_18 = snx[snx['Product_Description'].str.contains('R18', na=False)]

# 2025年1月 vs 2026年1月
s_2025 = sales_18[sales_18['ID_Month_Key'] == 202501]['具体客户购买数'].sum()
s_2026 = sales_18[sales_18['ID_Month_Key'] == 202601]['具体客户购买数'].sum()

# SNX值需要正确提取
snx_2025_val = int(snx_18[(snx_18['ID_Month_Key'] == 202501)]['SNX'].sum())
snx_2026_val = int(snx_18[(snx_18['ID_Month_Key'] == 202601)]['SNX'].sum())

# 提取规格
sales_18['规格'] = sales_18['Product_Description'].str.extract(r'(\d+)/(\d+)\s*[RZ]?\s*(\d+)')[0] + '/' + \
                   sales_18['Product_Description'].str.extract(r'(\d+)/(\d+)\s*[RZ]?\s*(\d+)')[1] + 'R' + \
                   sales_18['Product_Description'].str.extract(r'(\d+)/(\d+)\s*[RZ]?\s*(\d+)')[2]

# 2025年1月 vs 2026年1月
s_2025_jan = sales_18[sales_18['ID_Month_Key'] == 202501]
s_2026_jan = sales_18[sales_18['ID_Month_Key'] == 202601]

# 生成图表
print("\n2. 生成图表...")

# 图1：核心指标对比
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# 销量对比
labels = ['2025年1月', '2026年1月']
sales_values = [s_2025, s_2026]
colors_sales = ['#3498db', '#e74c3c']
bars1 = axes[0].bar(labels, sales_values, color=colors_sales)
axes[0].set_title('渠道销量对比', fontsize=14, fontweight='bold')
axes[0].set_ylabel('销量（条）')
for bar, val in zip(bars1, sales_values):
    axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100, 
                  f'{val:,}', ha='center', va='bottom', fontsize=11)

# SNX对比
snx_values = [snx_2025_val, snx_2026_val]
bars2 = axes[1].bar(labels, snx_values, color=['#2ecc71', '#f39c12'])
axes[1].set_title('SNX注册对比', fontsize=14, fontweight='bold')
axes[1].set_ylabel('SNX数量')
for bar, val in zip(bars2, snx_values):
    axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, 
                  f'{val:,}', ha='center', va='bottom', fontsize=11)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/图1-核心指标对比.png", dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 图1-核心指标对比.png")

# 图2：渠道对比
s_prog_2025 = s_2025_jan.groupby('Program_Type')['具体客户购买数'].sum()
s_prog_2026 = s_2026_jan.groupby('Program_Type')['具体客户购买数'].sum()

snx_2025_jan = snx_18[snx_18['ID_Month_Key'] == 202501]
snx_2026_jan = snx_18[snx_18['ID_Month_Key'] == 202601]
snx_prog_2025 = snx_2025_jan.groupby('Program_Type')['SNX'].sum()
snx_prog_2026 = snx_2026_jan.groupby('Program_Type')['SNX'].sum()

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 渠道销量
channels = sorted(set(s_prog_2025.index) | set(s_prog_2026.index))
x = range(len(channels))
width = 0.35
vals_2025 = [s_prog_2025.get(c, 0) for c in channels]
vals_2026 = [s_prog_2026.get(c, 0) for c in channels]

bars1 = axes[0].bar([i - width/2 for i in x], vals_2025, width, label='2025年1月', color='#3498db')
bars2 = axes[0].bar([i + width/2 for i in x], vals_2026, width, label='2026年1月', color='#e74c3c')
axes[0].set_xticks(x)
axes[0].set_xticklabels(channels, rotation=45, ha='right')
axes[0].set_title('渠道销量对比', fontsize=14, fontweight='bold')
axes[0].legend()
axes[0].set_ylabel('销量（条）')

# SNX
snx_vals_2025 = [snx_prog_2025.get(c, 0) for c in channels]
snx_vals_2026 = [snx_prog_2026.get(c, 0) for c in channels]

bars3 = axes[1].bar([i - width/2 for i in x], snx_vals_2025, width, label='2025年1月', color='#2ecc71')
bars4 = axes[1].bar([i + width/2 for i in x], snx_vals_2026, width, label='2026年1月', color='#f39c12')
axes[1].set_xticks(x)
axes[1].set_xticklabels(channels, rotation=45, ha='right')
axes[1].set_title('SNX注册对比', fontsize=14, fontweight='bold')
axes[1].legend()
axes[1].set_ylabel('SNX数量')

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/图2-渠道对比.png", dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 图2-渠道对比.png")

# 图3：规格分析
spec_2025 = s_2025_jan.groupby('规格')['具体客户购买数'].sum()
spec_2026 = s_2026_jan.groupby('规格')['具体客户购买数'].sum()

spec_comp = pd.DataFrame({
    '2025': spec_2025,
    '2026': spec_2026
}).fillna(0)
spec_comp['变化'] = spec_comp['2026'] - spec_comp['2025']
spec_comp = spec_comp.sort_values('变化')

# 取TOP 10下降和上升
spec_top10 = pd.concat([spec_comp.head(5), spec_comp.tail(5)])

fig, ax = plt.subplots(figsize=(12, 6))
colors = ['#e74c3c' if x < 0 else '#2ecc71' for x in spec_top10['变化']]
bars = ax.barh(range(len(spec_top10)), spec_top10['变化'], color=colors)
ax.set_yticks(range(len(spec_top10)))
ax.set_yticklabels(spec_top10.index)
ax.set_title('规格销量变化 (2026年1月 vs 2025年1月)', fontsize=14, fontweight='bold')
ax.set_xlabel('销量变化（条）')
ax.axvline(x=0, color='black', linewidth=0.5)

plt.tight_layout()
plt.savefig(f"{OUTPUT_DIR}/图3-规格变化.png", dpi=150, bbox_inches='tight')
plt.close()
print(f"  ✓ 图3-规格变化.png")

print("\n3. 生成PDF报告...")

# 创建PDF
c = canvas.Canvas(f"{OUTPUT_DIR}/18寸2026年1月销售报告.pdf", pagesize=A4)
width, height = A4

# 标题
c.setFont("Helvetica-Bold", 24)
c.drawCentredString(width/2, height - 80, "18寸轮胎 2026年1月销售报告")

# 副标题
c.setFont("Helvetica", 12)
c.drawCentredString(width/2, height - 110, f"报告日期: 2026年2月13日")

# 核心指标
y = height - 160
c.setFont("Helvetica-Bold", 16)
c.drawString(50, y, "一、核心指标")
y -= 30

c.setFont("Helvetica", 11)
c.drawString(50, y, f"• 渠道销量：2025年1月 {s_2025:,} 条 → 2026年1月 {s_2026:,} 条 ({(s_2026-s_2025)/s_2025*100:+.1f}%)")
y -= 20
c.drawString(50, y, f"• SNX注册：2025年1月 {snx_2025_val:,} 条 → 2026年1月 {snx_2026_val:,} 条 ({(snx_2026_val-snx_2025_val)/snx_2025_val*100:+.1f}%)")
y -= 40

# 核心洞察
c.setFont("Helvetica-Bold", 14)
c.drawString(50, y, "核心洞察：")
y -= 25
c.setFont("Helvetica", 11)
c.drawString(70, y, "• 渠道出货下降 8.6%，但终端零售 SNX 上涨 20.1%")
y -= 18
c.drawString(70, y, "• 说明：渠道在消化库存，终端需求依然强劲")
y -= 40

# 插入图表
c.drawImage(f"{OUTPUT_DIR}/图1-核心指标对比.png", 50, y-200, width=400, height=200)
y -= 250

# 渠道分析
c.setFont("Helvetica-Bold", 16)
c.drawString(50, y, "二、渠道维度分析")
y -= 30

c.setFont("Helvetica", 11)
for prog in ['MCR', 'MLD', 'TYREPLUS', 'FDD', 'MARPlus']:
    s5 = s_prog_2025.get(prog, 0)
    s6 = s_prog_2026.get(prog, 0)
    n5 = snx_prog_2025.get(prog, 0)
    n6 = snx_prog_2026.get(prog, 0)
    change_s = (s6-s5)/s5*100 if s5 > 0 else 0
    change_n = (n6-n5)/n5*100 if n5 > 0 else 0
    c.drawString(50, y, f"• {prog}: 销量 {change_s:+.1f}% / SNX {change_n:+.1f}%")
    y -= 18

y -= 20
c.drawImage(f"{OUTPUT_DIR}/图2-渠道对比.png", 50, y-180, width=450, height=180)
y -= 220

# 规格分析
c.setFont("Helvetica-Bold", 16)
c.drawString(50, y, "三、规格维度分析")
y -= 30

c.setFont("Helvetica", 11)
c.drawString(50, y, "销量下降规格 TOP 5:")
y -= 18
for spec, row in spec_comp.head(5).iterrows():
    c.drawString(70, y, f"  • {spec}: {int(row['2025']):,} → {int(row['2026']):,} ({int(row['变化']):+,})")
    y -= 15

y -= 15
c.drawImage(f"{OUTPUT_DIR}/图3-规格变化.png", 50, y-180, width=450, height=180)

c.save()
print(f"  ✓ 18寸2026年1月销售报告.pdf")

# 生成Markdown版本
print("\n4. 生成Markdown报告...")
with open(f"{OUTPUT_DIR}/18寸2026年1月销售报告.md", "w", encoding='utf-8') as f:
    f.write("# 18寸轮胎 2026年1月销售报告\n\n")
    f.write("**报告日期：2026年2月13日**\n\n")
    f.write("## 一、核心指标\n\n")
    f.write("| 指标 | 2025年1月 | 2026年1月 | 变化 |\n")
    f.write("|------|------------|------------|------|\n")
    f.write(f"| 渠道销量 | {s_2025:,} 条 | {s_2026:,} 条 | {(s_2026-s_2025)/s_2025*100:+.1f}% |\n")
    f.write(f"| SNX注册 | {snx_2025_val:,} 条 | {snx_2026_val:,} 条 | {(snx_2026_val-snx_2025_val)/snx_2025_val*100:+.1f}% |\n\n")
    f.write("### 核心洞察\n")
    f.write("- 渠道出货下降 8.6%，但终端零售 SNX 上涨 20.1%\n")
    f.write("- 说明：**渠道在消化库存，终端需求依然强劲**\n\n")
    f.write("![核心指标对比](./图1-核心指标对比.png)\n\n")
    f.write("## 二、渠道维度分析\n\n")
    f.write("| 渠道 | 销量变化 | SNX变化 | 解读 |\n")
    f.write("|------|----------|---------|------|\n")
    for prog in ['MCR', 'MLD', 'TYREPLUS', 'FDD', 'MARPlus']:
        s5 = s_prog_2025.get(prog, 0)
        s6 = s_prog_2026.get(prog, 0)
        n5 = snx_prog_2025.get(prog, 0)
        n6 = snx_prog_2026.get(prog, 0)
        change_s = (s6-s5)/s5*100 if s5 > 0 else 0
        change_n = (n6-n5)/n5*100 if n5 > 0 else 0
        f.write(f"| {prog} | {change_s:+.1f}% | {change_n:+.1f}% | - |\n")
    f.write("\n![渠道对比](./图2-渠道对比.png)\n\n")
    f.write("## 三、规格维度分析\n\n")
    f.write("### 销量下降规格 TOP 5\n\n")
    for spec, row in spec_comp.head(5).iterrows():
        f.write(f"- {spec}: {int(row['2025']):,} → {int(row['2026']):,} ({int(row['变化']):+,})\n")
    f.write("\n![规格变化](./图3-规格变化.png)\n\n")
    f.write("---\n\n")
    f.write("*报告由 ZZH-EC 自动生成*\n")

print(f"  ✓ 18寸2026年1月销售报告.md")

print("\n" + "=" * 70)
print("报告生成完成！")
print("=" * 70)
print(f"\n输出目录: {OUTPUT_DIR}")
print("\n生成的文件:")
print("  1. 18寸2026年1月销售报告.pdf")
print("  2. 18寸2026年1月销售报告.md")
print("  3. 图1-核心指标对比.png")
print("  4. 图2-渠道对比.png")
print("  5. 图3-规格变化.png")
