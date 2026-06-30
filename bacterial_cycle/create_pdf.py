#!/usr/bin/env python3
"""
Simple Markdown to HTML converter for PDF generation
Usage: python3 create_pdf.py
Output: INTEGRATED_DISCOVERY_PAPER.html
Then open in browser and print to PDF
"""

import re
from pathlib import Path

def markdown_to_html(md_content):
    """Convert basic markdown to HTML"""
    html = md_content
    
    # Escape HTML special characters (except for markdown)
    html = html.replace('&', '&amp;')
    html = html.replace('<', '&lt;')
    html = html.replace('>', '&gt;')
    
    # Headers
    html = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Bold
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    
    # Italic - only if not part of a word (to avoid breaking *E. coli*)
    html = re.sub(r'(?<!\w)\*([^*]+?)\*(?!\w)', r'<em>\1</em>', html)
    
    # Code
    html = re.sub(r'`([^`]+?)`', r'<code>\1</code>', html)
    
    # Links
    html = re.sub(r'\[([^\]]+?)\]\(([^\)]+?)\)', r'<a href="\2">\1</a>', html)
    
    # Images
    html = re.sub(r'!\[([^\]]*?)\]\(([^\)]+?)\)', r'<img src="\2" alt="\1">', html)
    
    # Tables (basic)
    lines = html.split('\n')
    in_table = False
    table_rows = []
    result_lines = []
    
    for line in lines:
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append(line)
        else:
            if in_table:
                # Convert table to HTML
                result_lines.append('<table>')
                for i, row in enumerate(table_rows):
                    if '---' in row:
                        continue  # Skip separator row
                    cells = [cell.strip() for cell in row.split('|')[1:-1]]
                    tag = 'th' if i == 0 or i == 1 else 'td'
                    result_lines.append('<tr>')
                    for cell in cells:
                        result_lines.append(f'<{tag}>{cell}</{tag}>')
                    result_lines.append('</tr>')
                result_lines.append('</table>')
                table_rows = []
                in_table = False
            result_lines.append(line)
    
    # Handle table at end of file
    if in_table:
        result_lines.append('<table>')
        for i, row in enumerate(table_rows):
            if '---' in row:
                continue
            cells = [cell.strip() for cell in row.split('|')[1:-1]]
            tag = 'th' if i == 0 else 'td'
            result_lines.append('<tr>')
            for cell in cells:
                result_lines.append(f'<{tag}>{cell}</{tag}>')
            result_lines.append('</tr>')
        result_lines.append('</table>')
    
    html = '\n'.join(result_lines)
    
    # Paragraphs (simple - consecutive lines become paragraphs)
    paragraphs = html.split('\n\n')
    result_paragraphs = []
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if para.startswith('<h') or para.startswith('<table') or para.startswith('<ul') or para.startswith('<ol') or para.startswith('<img'):
            result_paragraphs.append(para)
        else:
            # Replace single newlines with spaces within paragraphs
            para = para.replace('\n', ' ')
            result_paragraphs.append(f'<p>{para}</p>')
    
    return '\n\n'.join(result_paragraphs)

# Read markdown file
md_file = Path('INTEGRATED_DISCOVERY_PAPER.md')
with open(md_file, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Convert to HTML
html_body = markdown_to_html(md_content)

# Create full HTML document
html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Physical-Molecular Integration in Bacterial Cell Cycle Regulation</title>
    <style>
        @page {{
            margin: 2cm;
            size: A4;
        }}
        body {{
            font-family: 'Times New Roman', Georgia, serif;
            font-size: 11pt;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3, h4 {{
            color: #222;
            margin-top: 1.8em;
            margin-bottom: 0.8em;
            font-weight: 600;
        }}
        h1 {{
            font-size: 18pt;
            border-bottom: 2px solid #333;
            padding-bottom: 0.3em;
        }}
        h2 {{
            font-size: 14pt;
            border-bottom: 1px solid #666;
            padding-bottom: 0.2em;
        }}
        h3 {{
            font-size: 12pt;
            border-bottom: none;
        }}
        h4 {{
            font-size: 11pt;
        }}
        p {{
            margin-bottom: 1em;
            text-align: justify;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1.5em 0;
            font-size: 9pt;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 6px 8px;
            text-align: left;
        }}
        th {{
            background-color: #f2f2f2;
            font-weight: 600;
        }}
        code {{
            font-family: 'Courier New', 'Monaco', monospace;
            background-color: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-size: 0.9em;
        }}
        pre {{
            background-color: #f4f4f4;
            padding: 12px;
            border-radius: 5px;
            overflow-x: auto;
            font-size: 0.9em;
            border-left: 3px solid #ccc;
        }}
        strong {{
            font-weight: 600;
        }}
        em {{
            font-style: italic;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5em auto;
            border: 1px solid #ddd;
            padding: 5px;
            background: #fff;
        }}
        blockquote {{
            margin: 1.5em 0;
            padding: 0.5em 1.5em;
            border-left: 4px solid #ccc;
            color: #555;
            background-color: #f9f9f9;
        }}
        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 2em 0;
        }}
        @media print {{
            body {{
                max-width: 100%;
                padding: 0;
            }}
            h1, h2, h3, h4 {{
                page-break-after: avoid;
            }}
            table, img, blockquote {{
                page-break-inside: avoid;
            }}
            a {{
                color: #000;
                text-decoration: underline;
            }}
        }}
    </style>
</head>
<body>
{html_body}
</body>
</html>'''

# Write HTML file
html_file = Path('INTEGRATED_DISCOVERY_PAPER.html')
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f"HTML file created: {html_file}")
print(f"File size: {html_file.stat().st_size} bytes")
print()
print("=" * 60)
print("TO CREATE PDF:")
print("=" * 60)
print("1. Open INTEGRATED_DISCOVERY_PAPER.html in your web browser")
print("2. Press Cmd+P (Mac) or Ctrl+P (Windows/Linux)")
print('3. Select "Save as PDF" or "Microsoft Print to PDF"')
print("4. Click Save/Print")
print()
print("Alternatively, if you have pandoc installed:")
print("  pandoc INTEGRATED_DISCOVERY_PAPER.md -o INTEGRATED_DISCOVERY_PAPER.pdf")
print("=" * 60)
