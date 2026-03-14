#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF生成器 - 支持中文显示
使用 Arial Unicode MS 字体
"""

import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import re

FONT_PATH = "/Library/Fonts/Arial Unicode.ttf"

def create_pdf(md_path, pdf_path=None):
    """从Markdown创建PDF"""
    
    # 注册字体
    try:
        pdfmetrics.registerFont(TTFont('ArialUnicode', FONT_PATH))
        print(f"✅ 字体已注册: {FONT_PATH}")
    except Exception as e:
        print(f"❌ 字体注册失败: {e}")
        return None
    
    # 读取Markdown
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 样式
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='TitleCN',
        parent=styles['Title'],
        fontName='ArialUnicode',
        fontSize=18,
        spaceAfter=20
    ))
    styles.add(ParagraphStyle(
        name='HeadingCN',
        parent=styles['Heading1'],
        fontName='ArialUnicode',
        fontSize=14,
        spaceAfter=12,
        textColor=colors.darkblue
    ))
    styles.add(ParagraphStyle(
        name='BodyCN',
        parent=styles['Normal'],
        fontName='ArialUnicode',
        fontSize=10,
        leading=14
    ))
    
    # 解析
    elements = []
    lines = content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        i += 1
        
        if not line:
            continue
        
        # 标题
        if line.startswith('# '):
            elements.append(Paragraph(line[2:], styles['TitleCN']))
            elements.append(Spacer(1, 15))
        elif line.startswith('## '):
            elements.append(Paragraph(line[3:], styles['HeadingCN']))
        elif line.startswith('### '):
            elements.append(Paragraph(line[4:], styles['HeadingCN']))
        elif line.startswith('|') and '|' in line[1:]:
            # 表格
            table_data = []
            while i <= len(lines) and lines[i-1].strip().startswith('|'):
                row = [cell.strip() for cell in lines[i-1].strip('|').split('|')]
                table_data.append(row)
                if i < len(lines) and not lines[i].strip().startswith('|'):
                    break
                i += 1
            
            if table_data:
                num_cols = len(table_data[0])
                col_widths = [2.0 * inch / num_cols] * num_cols
                
                t = Table(table_data, colWidths=col_widths)
                t.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('FONTNAME', (0, 0), (-1, -1), 'ArialUnicode'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 15))
        else:
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            text = text.replace('|', ' | ')
            elements.append(Paragraph(text, styles['BodyCN']))
            elements.append(Spacer(1, 8))
    
    # 生成PDF
    if pdf_path is None:
        pdf_path = md_path.replace('.md', '.pdf')
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=50, leftMargin=50,
        topMargin=50, bottomMargin=50
    )
    
    doc.build(elements)
    print(f"✅ PDF已生成: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        create_pdf(sys.argv[1])
    else:
        # 转换所有
        report_dir = "/Users/zhangzhenhua/Library/Mobile Documents/com~apple~CloudDocs/共享/报告/"
        for f in sorted(os.listdir(report_dir)):
            if f.endswith('.md'):
                md_path = os.path.join(report_dir, f)
                print(f"\n转换: {f}")
                try:
                    create_pdf(md_path)
                except Exception as e:
                    print(f"❌ 失败: {e}")
