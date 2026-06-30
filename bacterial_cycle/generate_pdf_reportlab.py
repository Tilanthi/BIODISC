#!/usr/bin/env python3
"""
Generate PDF from markdown using ReportLab
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib.fonts import tt2ps
import re
import os

def clean_markdown_text(text):
    """Convert markdown to reportlab-compatible HTML

    CRITICAL: NEVER convert single asterisks to italic because they're used
    in mathematical expressions (e.g., dyn*cm^2/g^2). Only convert bold.
    """
    # Step 1: Protect bold tags with placeholders
    text = re.sub(r'\*\*([^*]+?)\*\*', r'%%BOLD_START%%\1%%BOLD_END%%', text)

    # Step 2: Escape ALL HTML special characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')

    # Step 3: Restore protected bold tags
    text = text.replace('%%BOLD_START%%', '<b>')
    text = text.replace('%%BOLD_END%%', '</b>')

    # Convert links [text](url) - remove links for now, keep text only
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    return text

def generate_pdf():
    # Read the markdown file
    md_file = '/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/Origins_regulation_bacterial_cellcycle.md'
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create PDF
    output_file = '/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/Origins_regulation_bacterial_cellcycle.pdf'
    doc = SimpleDocTemplate(output_file,
                            pagesize=letter,
                            leftMargin=inch,
                            rightMargin=inch,
                            topMargin=inch,
                            bottomMargin=inch)

    # Create styles
    styles = getSampleStyleSheet()
    # Modify existing styles
    if 'Title' in styles:
        styles['Title'].fontName = 'Times-Roman'
        styles['Title'].fontSize = 16
        styles['Title'].leading = 20
        styles['Title'].spaceAfter = 12
        styles['Title'].alignment = TA_CENTER
    if 'Heading1' in styles:
        styles['Heading1'].fontName = 'Times-Bold'
        styles['Heading1'].fontSize = 14
        styles['Heading1'].leading = 18
        styles['Heading1'].spaceAfter = 10
        styles['Heading1'].spaceBefore = 12
    if 'Heading2' in styles:
        styles['Heading2'].fontName = 'Times-Bold'
        styles['Heading2'].fontSize = 12
        styles['Heading2'].leading = 15
        styles['Heading2'].spaceAfter = 8
        styles['Heading2'].spaceBefore = 10
    if 'Heading3' in styles:
        styles['Heading3'].fontName = 'Times-Bold'
        styles['Heading3'].fontSize = 11
        styles['Heading3'].leading = 14
        styles['Heading3'].spaceAfter = 6
        styles['Heading3'].spaceBefore = 8
    if 'BodyText' in styles:
        styles['BodyText'].fontName = 'Times-Roman'
        styles['BodyText'].fontSize = 11
        styles['BodyText'].leading = 14
        styles['BodyText'].spaceAfter = 10
        styles['BodyText'].alignment = TA_JUSTIFY
    # Add new styles
    if 'Caption' not in styles:
        styles.add(ParagraphStyle(name='Caption', fontName='Times-Italic', fontSize=10, leading=12, spaceAfter=10, alignment=TA_CENTER))
    if 'Abstract' not in styles:
        styles.add(ParagraphStyle(name='Abstract', fontName='Times-Roman', fontSize=11, leading=14, spaceAfter=10, alignment=TA_JUSTIFY, leftIndent=0.5*inch, rightIndent=0.5*inch))

    # Build the story
    story = []

    # Process content line by line
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line:
            story.append(Spacer(1, 0.1*inch))
            i += 1
            continue

        # Handle headers
        if line.startswith('# '):
            text = clean_markdown_text(line[2:].strip())
            p = Paragraph(text, styles['Title'])
            story.append(p)
        elif line.startswith('## '):
            text = clean_markdown_text(line[3:].strip())
            p = Paragraph(text, styles['Heading1'])
            story.append(p)
        elif line.startswith('### '):
            text = clean_markdown_text(line[4:].strip())
            p = Paragraph(text, styles['Heading2'])
            story.append(p)
        elif line.startswith('#### '):
            text = clean_markdown_text(line[5:].strip())
            p = Paragraph(text, styles['Heading3'])
            story.append(p)
        elif line.startswith('**Abstract**'):
            # Abstract section - indent
            story.append(Paragraph('<b>Abstract</b>', styles['Heading1']))
            story.append(Spacer(1, 0.1*inch))
            # Collect abstract paragraphs
            abstract_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('#'):
                if lines[i].strip():
                    abstract_lines.append(clean_markdown_text(lines[i].strip()))
                i += 1
            for abs_line in abstract_lines:
                story.append(Paragraph(abs_line, styles['Abstract']))
            continue
        elif line.startswith('**Figure') or line.startswith('![Figure'):
            # Figure caption
            text = clean_markdown_text(line)
            p = Paragraph(text, styles['Caption'])
            story.append(p)
        elif line.startswith('!['):
            # Image - try to include if file exists
            img_match = re.match(r'!\[([^\]]*)\]\(([^\)]+)\)', line)
            if img_match:
                img_path = img_match.group(2)
                full_path = os.path.join(os.path.dirname(md_file), img_path)
                if os.path.exists(full_path):
                    try:
                        img = Image(full_path, width=5*inch, height=3*inch)
                        story.append(img)
                    except:
                        story.append(Paragraph(f'[Image: {img_path}]', styles['BodyText']))
                else:
                    story.append(Paragraph(f'[Image: {img_path}]', styles['BodyText']))
            i += 1
            continue
        elif line.startswith('|'):
            # Table - collect table rows
            table_lines = [line]
            i += 1
            while i < len(lines) and lines[i].startswith('|'):
                table_lines.append(lines[i])
                i += 1
            # Simple table handling
            if table_lines:
                rows = []
                for tl in table_lines:
                    cells = [c.strip() for c in tl.split('|')[1:-1]]
                    rows.append([clean_markdown_text(c) for c in cells])
                if rows:
                    t = Table(rows)
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(t)
            continue
        elif line.startswith('---') or line.startswith('***'):
            story.append(Spacer(1, 0.2*inch))
        elif line.startswith('**') and line.endswith('**') and not line.startswith('**Figure'):
            # Bold line (like a section heading in all caps)
            text = clean_markdown_text(line)
            p = Paragraph(text, styles['Heading3'])
            story.append(p)
        else:
            # Regular text
            text = clean_markdown_text(line)
            if text:
                try:
                    p = Paragraph(text, styles['BodyText'])
                    story.append(p)
                except:
                    # If paragraph fails, add as plain text
                    story.append(Spacer(1, 0.1*inch))

        i += 1

    # Build PDF
    doc.build(story)
    print(f'PDF successfully generated: {output_file}')
    return output_file

if __name__ == '__main__':
    generate_pdf()
