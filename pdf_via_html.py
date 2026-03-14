#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用matplotlib生成图表 + HTML转PDF
"""

import os
import sys
import base64
from datetime import datetime

def md_to_html_with_charts(md_path):
    """将Markdown转换为HTML（嵌入图表）"""
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 读取关联的PNG图片
    img_dir = os.path.dirname(md_path)
    images_html = ""
    
    for f in sorted(os.listdir(img_dir)):
        if f.startswith('图') and f.endswith('.png'):
            img_path = os.path.join(img_dir, f)
            with open(img_path, 'rb') as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode()
            images_html += f'''
            <div class="chart">
                <img src="data:image/png;base64,{img_base64}" />
            </div>
            '''
    
    # HTML模板
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>销售分析报告</title>
    <style>
        body {{
            font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", "Source Han Sans SC", sans-serif;
            font-size: 12pt;
            line-height: 1.6;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
        }}
        h1 {{ font-size: 22pt; color: #1a1a1a; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
        h2 {{ font-size: 16pt; color: #0066cc; margin-top: 30px; }}
        h3 {{ font-size: 14pt; color: #333; margin-top: 20px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            font-size: 10pt;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }}
        th {{ background: #f0f0f0; }}
        .status {{ font-weight: bold; }}
        .status-good {{ color: green; }}
        .status-warning {{ color: orange; }}
        .status-bad {{ color: red; }}
        .chart {{
            margin: 20px 0;
            text-align: center;
        }}
        .chart img {{
            max-width: 100%;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 10pt;
            color: #666;
        }}
    </style>
</head>
<body>
{parse_md_to_html(content)}
    <div class="footer">
        <p>生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
        <p>由 ZZH-EC 自动生成</p>
    </div>
</body>
</html>'''
    
    return html

def parse_md_to_html(md_content):
    """简单Markdown转HTML"""
    import re
    html = ""
    lines = md_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 标题
        if line.startswith('# '):
            html += f'<h1>{line[2:]}</h1>\n'
        elif line.startswith('## '):
            html += f'<h2>{line[3:]}</h2>\n'
        elif line.startswith('### '):
            html += f'<h3>{line[4:]}</h3>\n'
        # 表格
        elif line.startswith('|'):
            # 解析表格
            parts = [p.strip() for p in line.strip('|').split('|')]
            if '---' in line:
                continue
            if '状态' in line or '变化' in line or '指标' in line:
                html += '<table><thead><tr>' + ''.join(f'<th>{p}</th>' for p in parts) + '</tr></thead>\n'
            else:
                # 判断状态
                row_html = '<tr>' + ''.join(f'<td>{p}</td>' for p in parts) + '</tr>\n'
                if '✅' in line:
                    row_html = '<tr>' + ''.join(f'<td class="status status-good">{p}</td>' if p == '✅' else f'<td>{p}</td>' for p in parts) + '</tr>\n'
                elif '⚠️' in line:
                    row_html = '<tr>' + ''.join(f'<td class="status status-warning">{p}</td>' if p == '⚠️' else f'<td>{p}</td>' for p in parts) + '</tr>\n'
                html += row_html
        elif line.startswith('</table>'):
            html += '</table>\n'
        # 列表
        elif line.startswith('- '):
            html += f'<li>{line[2:]}</li>\n'
        elif re.match(r'^\d+\.', line):
            html += f'<p>{line}</p>\n'
        # 普通段落
        else:
            # 清理格式
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            html += f'<p>{text}</p>\n'
    
    return html

def convert_to_pdf_via_html(md_path, output_path=None):
    """通过HTML生成PDF"""
    
    # 生成HTML
    html = md_to_html_with_charts(md_path)
    html_path = md_path.replace('.md', '.html')
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ HTML已生成: {html_path}")
    
    # 尝试使用wkhtmltopdf或系统工具
    pdf_path = output_path or md_path.replace('.md', '.pdf')
    
    # 方法1: 尝试wkhtmltopdf
    try:
        import subprocess
        result = subprocess.run(
            ['wkhtmltopdf', '--enable-local-file-access', html_path, pdf_path],
            capture_output=True, timeout=30
        )
        if result.returncode == 0:
            print(f"✅ PDF已生成: {pdf_path}")
            return pdf_path
    except:
        pass
    
    # 方法2: 使用weasyprint
    try:
        from weasyprint import HTML
        HTML(html_path).write_pdf(pdf_path)
        print(f"✅ PDF已生成: {pdf_path}")
        return pdf_path
    except:
        pass
    
    # 方法3: 保留HTML作为备用
    print(f"⚠️ PDF生成失败，已生成HTML: {html_path}")
    print("请使用浏览器打开HTML文件，然后打印为PDF")
    return html_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        convert_to_pdf_via_html(sys.argv[1])
    else:
        # 转换所有
        report_dir = "/Users/zhangzhenhua/Library/Mobile Documents/com~apple~CloudDocs/共享/报告/"
        for f in sorted(os.listdir(report_dir)):
            if f.endswith('.md') and '完整分析' in f:
                md_path = os.path.join(report_dir, f)
                print(f"\n转换: {f}")
                try:
                    convert_to_pdf_via_html(md_path)
                except Exception as e:
                    print(f"❌ 失败: {e}")
