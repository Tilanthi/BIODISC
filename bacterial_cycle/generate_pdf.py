#!/usr/bin/env python3
"""Generate PDF from the bacterial cell cycle review markdown file."""

import sys
sys.path.insert(0, '/Users/gjw255/astrodata/SWARM/BIODISC')

from biodisc_core.utils.pdf_generator import ASTRAPDFGenerator
import re
import os

# Read the markdown file
manuscript_path = '/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/bacterial_cell_cycle_review_PUBLICATION_READY.md'
output_path = '/Users/gjw255/astrodata/SWARM/BIODISC/bacterial_cycle/bacterial_cell_cycle_review_COMPREHENSIVE_REVISION_FULL.pdf'

with open(manuscript_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Create PDF generator
pdf = ASTRAPDFGenerator(output_path)

# Track what's being added
headings_added = 0
paragraphs_added = 0
references_added = 0
tables_added = 0
lists_added = 0

# Parse and add content
lines = content.split('\n')
i = 0
title = None
in_references = False
abstract_lines = []
subtitle = None

print(f"Processing {len(lines)} lines of markdown...")

# First pass: extract title and subtitle
for i, line in enumerate(lines):
    if line.startswith('# ') and not line.startswith('##'):
        if title is None:
            title = line[2:].strip()
    elif line.startswith('## ') and i < 50:
        if subtitle is None:
            subtitle = line[3:].strip()
    if title and subtitle:
        break

# Reset and start full processing
i = 0

while i < len(lines):
    line = lines[i].rstrip()

    # Skip empty lines
    if not line:
        if abstract_lines:
            # We have accumulated abstract content
            abstract_text = ' '.join(abstract_lines)
            pdf.add_abstract(abstract_text)
            abstract_lines = []
        i += 1
        continue

    # Title (# but not ##)
    if line.startswith('# ') and not line.startswith('##'):
        if title is None:
            title = line[2:].strip()
        if title and not subtitle:
            pdf.add_title(title)
        elif title and subtitle:
            pdf.add_title(title)
            # Add subtitle as regular text
            pdf.add_paragraph(subtitle)
            paragraphs_added += 1
        i += 1

    # Abstract section heading
    elif line.startswith('### Abstract') or line.strip() == '### Abstract':
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith('#'):
            abstract_lines.append(lines[i].strip())
            i += 1
        if abstract_lines:
            pdf.add_abstract(' '.join(abstract_lines))

    # Headings (including References)
    elif line.startswith('##'):
        level = len(line) - len(line.lstrip('#'))
        heading_text = line.lstrip('#').strip()

        # Check if this is the References section
        if 'References' in heading_text:
            in_references = True
            pdf.add_heading('References', 2)
            headings_added += 1
        else:
            pdf.add_heading(heading_text, min(level, 3))
            headings_added += 1
        i += 1

    # Subsection headings (###)
    elif line.startswith('###'):
        subsection_text = line[3:].strip()
        pdf.add_heading(subsection_text, 3)
        headings_added += 1
        i += 1

    # Tables
    elif '|' in line and i + 1 < len(lines) and ('|-' in lines[i + 1] or '|' in lines[i + 1]):
        headers = [h.strip() for h in line.split('|')[1:-1] if h.strip()]
        i += 2  # Skip separator
        rows = []
        while i < len(lines) and '|' in lines[i] and lines[i].strip() and not lines[i].startswith('#'):
            row = [c.strip() for c in lines[i].split('|')[1:-1] if c.strip()]
            if row:
                rows.append(row)
            i += 1
        if headers and rows:
            try:
                pdf.add_table(headers, rows)
                tables_added += 1
            except Exception as e:
                print(f"Warning: Could not add table: {e}")

    # Bullet lists
    elif line.strip().startswith(('- ', '* ')):
        items = []
        while i < len(lines):
            next_line = lines[i].strip()
            if not next_line:
                break
            if next_line.startswith(('- ', '* ')):
                items.append(next_line[2:])
                i += 1
            elif next_line.startswith('   ') or next_line.startswith('\t'):
                # Sub-list item, add to previous with indentation
                if items:
                    items[-1] += ' ' + next_line.strip()
                i += 1
            else:
                break
        if items:
            pdf.add_bullet_list(items)
            lists_added += 1

    # References section - each line is a reference
    elif in_references and line.strip() and not line.startswith('#'):
        # Each reference line in references is a separate entry
        ref_text = line.strip()
        pdf.add_reference(ref_text)
        references_added += 1
        i += 1

    # Code blocks (skip content but track)
    elif line.strip().startswith('```'):
        i += 1
        while i < len(lines) and not lines[i].strip().startswith('```'):
            i += 1
        i += 1

    # Regular paragraph
    else:
        para_text = line
        i += 1
        # Combine consecutive non-empty lines that are part of the same paragraph
        while i < len(lines):
            next_line = lines[i].strip()
            if not next_line or next_line.startswith(('#', '-', '*', '|', '```', '![')):
                break
            # In references section, each line is a separate reference
            if in_references:
                break
            para_text += ' ' + next_line
            i += 1

        # Check if this looks like a reference entry
        # References typically start with "Author. Year." or just "Author, A."
        if not in_references and re.match(r'^[A-Z][a-z]+, [A-Z]\.', para_text):
            # This might be a reference appearing before the References section
            pdf.add_reference(para_text)
            references_added += 1
        else:
            pdf.add_paragraph(para_text)
            paragraphs_added += 1

# Build the PDF
print("Building PDF...")
print(f"Summary: {headings_added} headings, {paragraphs_added} paragraphs, {references_added} references, {tables_added} tables, {lists_added} lists")
result_path = pdf.build()
print(f'PDF built successfully: {result_path}')
print(f'File size: {os.path.getsize(result_path) / (1024*1024):.2f} MB')
