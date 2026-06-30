#!/usr/bin/env python3
import re

with open('bacterial_cell_cycle_review_PUBLICATION_READY.md', 'r') as f:
    content = f.read()

sections = re.findall(r'^## ([\d\.]+[^\n]*)', content, re.MULTILINE)
print("Main sections found:")
for i, section in enumerate(sections[:15]):
    print(f"{i+1}. {section}")
