#!/usr/bin/env python3
"""
Generate Discovery-First PDF manuscript
Restructured to emphasize discovery and framework predictive power
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
import os
import re

# Paths
MANUSCRIPT_PATH = "/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/Origins_regulation_bacterial_cellcycle_RESTRUCTURED.md"
PDF_OUTPUT = "/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/Origins_regulation_bacterial_cellcycle_DISCOVERY_FIRST.pdf"
FIGURES_DIR = "/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/figures"

def markdown_to_pdf_elements(md_text, figures_dir):
    """Convert markdown text to PDF elements"""
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.darkblue,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.darkblue,
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )

    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.darkblue,
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )

    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.darkblue,
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Times-Roman'
    )

    abstract_style = ParagraphStyle(
        'CustomAbstract',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        leftIndent=20,
        rightIndent=20,
        fontName='Times-Roman',
        textColor=colors.darkgray
    )

    elements = []
    lines = md_text.split('\n')

    # State tracking
    in_abstract = False
    in_table = False
    table_lines = []
    in_code_block = False
    code_lines = []

    for i, line in enumerate(lines):
        if not line.strip():
            if in_code_block:
                code_lines.append('')
            continue

        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                in_code_block = False
                code_text = '\n'.join(code_lines)
                code_style = ParagraphStyle(
                    'Code',
                    parent=body_style,
                    fontName='Courier',
                    fontSize=8,
                    leftIndent=20,
                    backColor=colors.lightgrey
                )
                elements.append(Spacer(0.1*inch, 0.1*inch))
                code_text = code_text.replace('<', '&lt;').replace('>', '&gt;')
                elements.append(Paragraph(code_text, code_style))
                elements.append(Spacer(0.1*inch, 0.1*inch))
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            continue

        if in_code_block:
            code_lines.append(line)
            continue

        # Abstract detection
        if '## Abstract' in line or line.startswith('Abstract'):
            in_abstract = True
            elements.append(Spacer(0.1*inch, 0.1*inch))
            elements.append(Paragraph('<b>Abstract</b>', heading1_style))
            continue

        if in_abstract and line.startswith('##') and 'Abstract' not in line:
            in_abstract = False

        # Headings
        if line.startswith('# '):
            text = escape_html(line[2:].strip())
            elements.append(Paragraph(text, title_style))
            continue

        if line.startswith('## '):
            text = escape_html(line[3:].strip())
            elements.append(Paragraph(text, heading1_style))
            continue

        if line.startswith('### '):
            text = escape_html(line[4:].strip())
            elements.append(Paragraph(text, heading2_style))
            continue

        if line.startswith('#### '):
            text = escape_html(line[5:].strip())
            elements.append(Paragraph(text, heading3_style))
            continue

        # Tables
        if line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
            if i == len(lines) - 1 or (not lines[i+1].strip().startswith('|')):
                in_table = False
                table = parse_table(table_lines)
                if table:
                    elements.append(table)
                table_lines = []
            continue

        # Figures
        if '![' in line:
            match = re.search(r'!\[.*?\]\((.*?)\)', line)
            if match:
                fig_path = match.group(1)
                full_path = os.path.join(figures_dir, os.path.basename(fig_path))

                if os.path.exists(full_path):
                    elements.append(Spacer(0.1*inch, 0.2*inch))
                    img = Image(full_path, width=5*inch, height=3.5*inch)
                    img.hAlign = 'CENTER'
                    elements.append(img)

                    alt_match = re.search(r'!\[(.*?)\]', line)
                    if alt_match:
                        caption = alt_match.group(1)
                        caption = escape_html(caption)
                        caption_style = ParagraphStyle(
                            'FigureCaption',
                            parent=body_style,
                            fontSize=9,
                            alignment=TA_CENTER,
                            italic=True,
                            spaceAfter=15
                        )
                        elements.append(Paragraph(caption, caption_style))
                    elements.append(Spacer(0.1*inch, 0.2*inch))
            continue

        # Regular text
        text = escape_html(line)
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
        text = re.sub(r'\*([a-zA-Z][a-zA-Z\s]{2,}?)\*', r'<i>\1</i>', text)
        text = re.sub(r'`([^`]+)`', r'<font face="Courier"><i>\1</i></font>', text)

        if in_abstract:
            elements.append(Paragraph(text, abstract_style))
        else:
            elements.append(Paragraph(text, body_style))

    return elements

def escape_html(text):
    """Escape HTML special characters"""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def parse_table(lines):
    """Parse markdown table and return reportlab Table"""
    if len(lines) < 2:
        return None

    data = []
    for line in lines:
        if '---' in line:
            continue
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        data.append(cells)

    if not data:
        return None

    # Calculate column widths based on content
    max_cols = max(len(row) for row in data)
    col_widths = []
    for col_idx in range(max_cols):
        max_len = max(len(row[col_idx]) if col_idx < len(row) else 0 for row in data)
        col_widths.append(max(1*inch, min(max_len * 0.1 * inch, 2.5*inch)))

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    return t

def main():
    """Generate PDF"""
    print(f"Reading manuscript from: {MANUSCRIPT_PATH}")

    with open(MANUSCRIPT_PATH, 'r', encoding='utf-8') as f:
        md_content = f.read()

    print("Converting markdown to PDF elements...")
    elements = markdown_to_pdf_elements(md_content, FIGURES_DIR)

    print(f"Generating PDF: {PDF_OUTPUT}")
    doc = SimpleDocTemplate(
        PDF_OUTPUT,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )

    doc.build(elements)

    file_size = os.path.getsize(PDF_OUTPUT)
    print(f"\nPDF generated successfully!")
    print(f"Output: {PDF_OUTPUT}")
    print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

    print("\nRestructuring highlights:")
    print("  ✓ Two-dimensional matrix framework moved to Section 2 (discovery-first)")
    print("  ✓ Discovery analyses D1-D5 prominent in Section 4")
    print("  ✓ Background condensed to Section 5 (preserving depth)")
    print("  ✓ Emphasis on what the framework enables for taking research forward")
    print("  ✓ Original question retained throughout")

if __name__ == '__main__':
    main()
