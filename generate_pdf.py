#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器 - 支持PDF和HTML格式
推荐使用HTML格式（中文显示最佳）

使用方法：
  python3 generate_pdf.py report.md              # 生成PDF
  python3 generate_pdf.py report.md --html       # 生成HTML（推荐）⭐
  python3 generate_pdf.py report.md --both       # 同时生成两种格式
  python3 generate_pdf.py --html                  # 批量生成HTML
"""

import os
import re
import sys

# 尝试导入reportlab
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
except ImportError:
    import subprocess
    print("正在安装reportlab...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch

# 中文字体路径
FONT_PATHS = [
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
]

def get_available_font():
    """获取可用的中文字体"""
    for path in FONT_PATHS:
        if os.path.exists(path):
            return path
    return None


# ==================== PDF生成相关函数 ====================

def create_pdf_with_chinese(md_file_path, output_path=None):
    """从Markdown文件生成PDF（支持中文）"""
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    elements = parse_markdown_for_pdf(content)

    if output_path is None:
        output_path = md_file_path.replace('.md', '.pdf')

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72, leftMargin=72,
        topMargin=72, bottomMargin=72
    )
    doc.build(elements)
    print(f"PDF已生成: {output_path}")
    return output_path


def parse_markdown_for_pdf(content):
    """解析Markdown为PDF元素"""
    elements = []
    lines = content.split('\n')

    font_path = get_available_font()
    if font_path is None:
        raise FileNotFoundError("未找到中文字体")

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ChineseTitle', parent=styles['Title'], fontName='ChineseFont', fontSize=18, spaceAfter=20))
    styles.add(ParagraphStyle(name='ChineseHeading', parent=styles['Heading1'], fontName='ChineseFont', fontSize=14, spaceAfter=12))
    styles.add(ParagraphStyle(name='ChineseBody', parent=styles['Normal'], fontName='ChineseFont', fontSize=10, leading=14))

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('# '):
            elements.append(Paragraph(line[2:], styles['ChineseTitle']))
        elif line.startswith('## '):
            elements.append(Paragraph(line[3:], styles['ChineseHeading']))
        elif line.startswith('### '):
            elements.append(Paragraph(line[4:], styles['ChineseHeading']))
        elif line.startswith('**') and line.endswith('**'):
            elements.append(Paragraph(line.strip('**'), styles['ChineseBody']))
        elif line.startswith('|') and '|' in line[1:]:
            table_data = []
            while line.startswith('|'):
                row = [cell.strip() for cell in line.strip('|').split('|')]
                table_data.append(row)
                if lines and lines[0].strip().startswith('|'):
                    line = lines.pop(0).strip()
                else:
                    break
            if table_data:
                col_widths = [2.5 * inch] * len(table_data[0])
                t = Table(table_data, colWidths=col_widths)
                t.setStyle(TableStyle([
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ]))
                elements.append(t)
                elements.append(Spacer(1, 12))
        else:
            clean_text = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
            elements.append(Paragraph(clean_text, styles['ChineseBody']))
            elements.append(Spacer(1, 6))

    return elements


# ==================== HTML生成相关函数 ====================

def create_html_report(md_file_path, output_path=None):
    """从Markdown文件生成HTML报告（推荐）"""
    with open(md_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    title = "销售分析报告"
    for line in content.split('\n'):
        if line.startswith('# '):
            title = line[2:].strip()
            break

    html_content = parse_markdown_to_html(content)

    html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: "Arial Unicode MS", "PingFang SC", "Microsoft YaHei", sans-serif; margin: 40px; line-height: 1.8; background: #f5f6fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 15px; }}
        h2 {{ color: #34495e; margin-top: 35px; border-left: 4px solid #3498db; padding-left: 15px; }}
        h3 {{ color: #7f8c8d; margin-top: 25px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 25px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        th, td {{ border: 1px solid #bdc3c7; padding: 12px 15px; text-align: center; }}
        th {{ background-color: #3498db; color: white; font-weight: bold; }}
        tr:hover {{ background-color: #f1f1f1; }}
        strong {{ color: #e74c3c; }}
        .positive {{ color: #27ae60; font-weight: bold; }}
        .negative {{ color: #e74c3c; font-weight: bold; }}
        .metric {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 25px; margin: 8px; border-radius: 8px; text-align: center; min-width: 120px; }}
        .metric-value {{ font-size: 28px; font-weight: bold; }}
        .metric-label {{ font-size: 12px; opacity: 0.9; margin-top: 5px; }}
    </style>
</head>
<body>
    <div class="container">
{content}
    </div>
</body>
</html>'''

    full_html = html_template.format(title=title, content=html_content)

    if output_path is None:
        output_path = md_file_path.replace('.md', '.html')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"HTML报告已生成: {output_path}")
    return output_path


def parse_markdown_to_html(content):
    """解析Markdown为HTML"""
    lines = content.split('\n')
    html_lines = []
    table_data = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith('|'):
            table_data.append(line)
            continue
        elif table_data:
            html_lines.append(process_table_html(table_data))
            table_data = []

        if line.startswith('# '):
            html_lines.append(f'<h1>{escape_html(line[2:])}</h1>')
        elif line.startswith('## '):
            html_lines.append(f'<h2>{escape_html(line[3:])}</h2>')
        elif line.startswith('### '):
            html_lines.append(f'<h3>{escape_html(line[4:])}</h3>')
        elif line.startswith('**') and line.endswith('**'):
            text = line.strip('**')
            if '↑' in text or '+' in text:
                html_lines.append(f'<p class="positive"><strong>{escape_html(text)}</strong></p>')
            elif '↓' in text or '-' in text:
                html_lines.append(f'<p class="negative"><strong>{escape_html(text)}</strong></p>')
            else:
                html_lines.append(f'<p><strong>{escape_html(text)}</strong></p>')
        elif line.startswith('- '):
            html_lines.append(f'<li>{escape_html(line[2:])}</li>')
        else:
            # 处理粗体并转义其他内容
            parts = re.split(r'(\*\*.+?\*\*)', line)
            html_parts = []
            for part in parts:
                if part.startswith('**') and part.endswith('**'):
                    html_parts.append(f'<strong>{escape_html(part[2:-2])}</strong>')
                else:
                    html_parts.append(escape_html(part))
            html_lines.append(f'<p>{"".join(html_parts)}</p>')

    if table_data:
        html_lines.append(process_table_html(table_data))

    return '\n'.join(html_lines)


def process_table_html(table_lines):
    """处理Markdown表格为HTML"""
    rows = [line.strip('|').split('|') for line in table_lines]
    rows = [[cell.strip() for cell in row] for row in rows]

    if not rows:
        return ''

    html = '<table>\n  <thead><tr>\n'
    for cell in rows[0]:
        html += f'    <th>{escape_html(cell)}</th>\n'
    html += '  </tr></thead>\n  <tbody>\n'

    for row in rows[1:]:
        html += '  <tr>\n'
        for i, cell in enumerate(row):
            if i > 0 and '%' in cell and '+' in cell:
                html += f'    <td class="positive">{escape_html(cell)}</td>\n'
            elif i > 0 and '%' in cell and '-' in cell:
                html += f'    <td class="negative">{escape_html(cell)}</td>\n'
            else:
                html += f'    <td>{escape_html(cell)}</td>\n'
        html += '  </tr>\n'
    html += '  </tbody>\n</table>'
    return html


def escape_html(text):
    """HTML转义"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


# ==================== 批量转换 ====================

def convert_all_reports(format_type='pdf'):
    """批量转换所有报告"""
    report_dir = "/Users/zhangzhenhua/Library/Mobile Documents/com~apple~CloudDocs/共享/报告/"

    if not os.path.exists(report_dir):
        print(f"目录不存在: {report_dir}")
        return

    for filename in os.listdir(report_dir):
        if filename.endswith('.md'):
            md_path = os.path.join(report_dir, filename)
            print(f"\n正在转换: {filename}")
            try:
                if format_type == 'html':
                    create_html_report(md_path)
                else:
                    create_pdf_with_chinese(md_path)
            except Exception as e:
                print(f"转换失败: {e}")


# ==================== 主入口 ====================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--html':
            convert_all_reports('html')
        else:
            md_file = sys.argv[1]
            format_type = sys.argv[2] if len(sys.argv) > 2 else None

            if not os.path.exists(md_file):
                print(f"文件不存在: {md_file}")
                sys.exit(1)

            if format_type == '--html':
                create_html_report(md_file)
            elif format_type == '--both':
                create_pdf_with_chinese(md_file)
                create_html_report(md_file)
            else:
                create_pdf_with_chinese(md_file)
    else:
        print("使用方法:")
        print("  python3 generate_pdf.py report.md              # 生成PDF")
        print("  python3 generate_pdf.py report.md --html       # 生成HTML（推荐）")
        print("  python3 generate_pdf.py report.md --both       # 同时生成两种格式")
        print("  python3 generate_pdf.py --html                  # 批量生成HTML")
