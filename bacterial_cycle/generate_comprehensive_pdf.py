#!/usr/bin/env python3
"""
Generate PDF from COMPREHENSIVE_REVIEW_WITH_DISCOVERY_ANALYSIS.md
Includes Phase 2 figures for discovery analysis section
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import re

# Paths
MANUSCRIPT_PATH = "/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/COMPREHENSIVE_REVIEW_WITH_DISCOVERY_ANALYSIS.md"
PDF_OUTPUT = "/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/Physical_Molecular_Integration_Comprehensive_Review.pdf"
FIGURES_DIR = "/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/figures"

def markdown_to_pdf_elements(md_text, figures_dir):
    """Convert markdown text to PDF elements"""
    styles = getSampleStyleSheet()

    # Custom styles with unique names to avoid conflicts
    title_style = ParagraphStyle(
        'ComprehensiveTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.darkblue,
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading1_style = ParagraphStyle(
        'CompHeading1',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.darkblue,
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )

    heading2_style = ParagraphStyle(
        'CompHeading2',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.darkblue,
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )

    heading3_style = ParagraphStyle(
        'CompHeading3',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.darkblue,
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CompBody',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName='Times-Roman'
    )

    abstract_style = ParagraphStyle(
        'CompAbstract',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
        leftIndent=20,
        rightIndent=20,
        fontName='Times-Roman',
        textColor=colors.darkgray
    )

    caption_style = ParagraphStyle(
        'CompCaption',
        parent=body_style,
        fontSize=9,
        alignment=TA_CENTER,
        italic=True,
        spaceAfter=15
    )

    elements = []
    lines = md_text.split('\n')

    # State tracking
    in_abstract = False
    in_table = False
    table_lines = []
    in_code_block = False
    code_lines = []

    # Track which figures we've inserted
    figures_inserted = set()

    for i, line in enumerate(lines):
        # Skip empty lines
        if not line.strip():
            if in_code_block:
                code_lines.append('')
            continue

        # Code blocks
        if line.strip().startswith('```'):
            if in_code_block:
                # End code block
                code_text = '\n'.join(code_lines)
                # Add as preformatted text
                code_style = ParagraphStyle(
                    f'Code{i}',
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
                in_code_block = False
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
            text = line[2:].strip()
            text = escape_html(text)
            elements.append(Paragraph(text, title_style))
            continue

        if line.startswith('## '):
            text = line[3:].strip()
            text = escape_html(text)
            elements.append(Paragraph(text, heading1_style))
            continue

        if line.startswith('### '):
            text = line[4:].strip()
            text = escape_html(text)
            elements.append(Paragraph(text, heading2_style))
            continue

        if line.startswith('#### '):
            text = line[5:].strip()
            text = escape_html(text)
            elements.append(Paragraph(text, heading3_style))
            continue

        # Tables
        if line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_lines = []
            table_lines.append(line)
            # Check if table ends
            if i == len(lines) - 1 or (not lines[i+1].strip().startswith('|')):
                in_table = False
                table = parse_table(table_lines)
                if table:
                    elements.append(table)
                table_lines = []
            continue

        # Strategic figure insertions for discovery analysis section
        if '**Figure 1**' in line and 'fig1' not in figures_inserted:
            fig_path = os.path.join(figures_dir, 'fig1_complexity_vs_variability_n13.png')
            if os.path.exists(fig_path):
                elements.append(Spacer(0.1*inch, 0.2*inch))
                img = Image(fig_path, width=6*inch, height=4*inch)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Paragraph('<b>Figure 1:</b> Complexity vs Variability scatter plot showing negative correlation (Spearman rho = -0.89)', caption_style))
                figures_inserted.add('fig1')
            continue

        if '**Figure 2**' in line and 'fig2' not in figures_inserted:
            fig_path = os.path.join(figures_dir, 'fig2_string_vs_manual_complexity.png')
            if os.path.exists(fig_path):
                elements.append(Spacer(0.1*inch, 0.2*inch))
                img = Image(fig_path, width=6*inch, height=4*inch)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Paragraph('<b>Figure 2:</b> Cross-validation of manual and STRING database complexity scores', caption_style))
                figures_inserted.add('fig2')
            continue

        if '**Figure 3**' in line and 'fig3' not in figures_inserted:
            fig_path = os.path.join(figures_dir, 'fig3_matrix_occupancy_ecoli.png')
            if os.path.exists(fig_path):
                elements.append(Spacer(0.1*inch, 0.2*inch))
                img = Image(fig_path, width=6*inch, height=4.5*inch)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Paragraph('<b>Figure 3:</b> Matrix occupancy heatmap for E. coli showing quantitative interaction scores', caption_style))
                figures_inserted.add('fig3')
            continue

        if '**Table 4**' in line and 'heatmap' not in figures_inserted:
            # Insert matrix occupancy heatmap after Table 4
            fig_path = os.path.join(figures_dir, 'fig3_matrix_occupancy_ecoli.png')
            if os.path.exists(fig_path) and 'fig3' not in figures_inserted:
                elements.append(Spacer(0.1*inch, 0.2*inch))
                img = Image(fig_path, width=6*inch, height=4.5*inch)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Paragraph('<b>Matrix Occupancy Heatmap:</b> Visual representation of E. coli matrix cell occupancy scores', caption_style))
                figures_inserted.add('fig3')
            continue

        # Regular text
        text = escape_html(line)

        # Handle bold formatting ONLY - DO NOT convert single asterisks to italic
        # This prevents corruption of mathematical expressions like "dyn*cm^2/g^2"
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

        # Handle inline code
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
        if '---' in line:  # Skip separator line
            continue
        cells = [cell.strip() for cell in line.split('|')[1:-1]]
        data.append(cells)

    if not data:
        return None

    # Calculate column widths based on content
    num_cols = len(data[0])
    col_widths = []
    for col_idx in range(num_cols):
        max_len = max([len(data[row][col_idx]) if col_idx < len(data[row]) else 0 for row in range(len(data))])
        # Scale width: minimum 1 inch, maximum 3 inches
        width = min(3.0, max(1.0, max_len * 0.08))
        col_widths.append(width * inch)

    # Create table
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))

    return t

def main():
    """Generate PDF"""
    print(f"Reading manuscript from: {MANUSCRIPT_PATH}")

    with open(MANUSCRIPT_PATH, 'r', encoding='utf-8') as f:
        md_content = f.read()

    print("Converting markdown to PDF elements...")
    print(f"Manuscript length: {len(md_content)} characters")

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

    # Get file size
    file_size = os.path.getsize(PDF_OUTPUT)
    print(f"\nPDF generated successfully!")
    print(f"Output: {PDF_OUTPUT}")
    print(f"File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

    # List available figures
    print("\nAvailable figures in directory:")
    for fig_file in sorted(os.listdir(FIGURES_DIR)):
        if fig_file.endswith('.png') or fig_file.endswith('.pdf'):
            print(f"  {fig_file}")

if __name__ == '__main__':
    main()
