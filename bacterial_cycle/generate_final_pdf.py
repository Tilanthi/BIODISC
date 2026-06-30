#!/usr/bin/env python3
"""
Generate final PDF manuscript with embedded figures
Includes Figures 4, 5, 6 created for strategic enhancement
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
MANUSCRIPT_PATH = "/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/bacterial_cell_cycle_review_PUBLICATION_READY.md"
PDF_OUTPUT = "/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/bacterial_cell_cycle_review_ROUND_13_FINAL_COMPLETE.pdf"
FIGURES_DIR = "/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/figures"

# Figure placements (strategic locations in manuscript)
FIGURE_PLACEMENTS = {
    'fig1_hierarchical_framework.png': 'Introduction',
    'fig2_min_system.png': 'Min System section',
    'fig3_nucleoid_occlusion.png': 'Nucleoid Occlusion section',
    'fig4_asi_measurement_protocol.png': 'AsI Measurement Protocol section',
    'fig5_sos_pilot_estimate.png': 'SOS Pilot Estimate section',
    'fig6_molecular_complexity_threshold.png': 'Molecular Complexity Threshold section'
}

def markdown_to_pdf_elements(md_text, figures_dir):
    """Convert markdown text to PDF elements"""
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
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

        # Figures
        if '![' in line:
            # Extract figure path
            match = re.search(r'!\[.*?\]\((.*?)\)', line)
            if match:
                fig_path = match.group(1)
                full_path = os.path.join(figures_dir, os.path.basename(fig_path))

                if os.path.exists(full_path):
                    # Add figure
                    img = Image(full_path, width=5*inch, height=3.5*inch)
                    img.hAlign = 'CENTER'
                    elements.append(Spacer(0.1*inch, 0.2*inch))
                    elements.append(img)

                    # Extract caption if present
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
                else:
                    # Figure not found, add placeholder
                    elements.append(Spacer(0.1*inch, 0.1*inch))
                    elements.append(Paragraph(f'[Figure: {os.path.basename(fig_path)}]', body_style))
            continue

        # Strategic figure insertions based on content
        if '**AsI Measurement Protocol**' in line or '**Cross-Domain Measurement**' in line:
            fig4_path = os.path.join(figures_dir, 'fig4_asi_measurement_protocol.png')
            if os.path.exists(fig4_path):
                elements.append(Spacer(0.1*inch, 0.2*inch))
                elements.append(Paragraph('<b>Figure 4:</b> Asymmetry Index (AsI) Cross-Domain Measurement Protocol', heading3_style))
                img = Image(fig4_path, width=6*inch, height=4*inch)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(0.1*inch, 0.3*inch))
            continue

        if '**Bayesian Credibility Analysis**' in line:
            fig5_path = os.path.join(figures_dir, 'fig5_sos_pilot_estimate.png')
            if os.path.exists(fig5_path):
                elements.append(Spacer(0.1*inch, 0.2*inch))
                elements.append(Paragraph('<b>Figure 5:</b> SOS Checkpoint Pilot Estimate with Bayesian Credibility Analysis', heading3_style))
                img = Image(fig5_path, width=6*inch, height=3*inch)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(0.1*inch, 0.3*inch))
            continue

        if '**Prediction C: Molecular Complexity and Division Timing Variability**' in line:
            fig6_path = os.path.join(figures_dir, 'fig6_molecular_complexity_threshold.png')
            if os.path.exists(fig6_path):
                elements.append(Spacer(0.1*inch, 0.2*inch))
                elements.append(Paragraph('<b>Figure 6:</b> Molecular Complexity Threshold Hypothesis - Current Data and Testable Predictions', heading3_style))
                img = Image(fig6_path, width=6*inch, height=3.5*inch)
                img.hAlign = 'CENTER'
                elements.append(img)
                elements.append(Spacer(0.1*inch, 0.3*inch))
            continue

        # Regular text
        text = escape_html(line)

        # Handle bold formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)

        # Handle italic formatting - but be careful with mathematical expressions
        # Only convert *text* to <i> if it doesn't look like math
        text = re.sub(r'\*([a-zA-Z][a-zA-Z\s]{2,}?)\*', r'<i>\1</i>', text)

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

    # Create table
    t = Table(data, colWidths=[1.5*inch]*len(data[0]))
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
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

    # Get file size
    file_size = os.path.getsize(PDF_OUTPUT)
    print(f"\nPDF generated successfully!")
    print(f"Output: {PDF_OUTPUT}")
    print(f"File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")

    # Check figures were embedded
    print("\nEmbedded figures:")
    for fig_name in FIGURE_PLACEMENTS.keys():
        fig_path = os.path.join(FIGURES_DIR, fig_name)
        if os.path.exists(fig_path):
            print(f"  ✓ {fig_name} ({os.path.getsize(fig_path)/1024:.1f} KB)")

if __name__ == '__main__':
    main()
