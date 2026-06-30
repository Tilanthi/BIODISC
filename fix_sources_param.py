#!/usr/bin/env python3
"""Fix sources parameter in domain modules"""
import re
import os

domains = [
    "biochemistry",
    "genetics",
    "cell_biology",
    "biophysics",
    "bioinformatics",
    "computational_biology",
    "genomics",
    "proteomics",
    "systems_biology"
]

base_path = "/Users/gjw255/astrodata/SWARM/BIODISC/biodisc_core/domains"

for domain in domains:
    init_file = os.path.join(base_path, domain, "__init__.py")
    if not os.path.exists(init_file):
        print(f"Skipping {domain}: file not found")
        continue

    with open(init_file, 'r') as f:
        content = f.read()

    # Pattern to match sources= lines in DomainQueryResult calls
    # We need to extract the sources list and move it to metadata
    pattern = r'sources=\[([^\]]+)\]'
    matches = list(re.finditer(pattern, content))

    if not matches:
        print(f"No sources found in {domain}")
        continue

    # Process in reverse order to maintain positions
    for match in reversed(matches):
        sources_content = match.group(1)
        # Find the metadata line and add sources to it
        # Look for metadata= line after this sources line
        lines = content.split('\n')
        modified_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            modified_lines.append(line)

            # Check if this line contains sources=
            if 'sources=' in line and 'DomainQueryResult' in '\n'.join(lines[max(0, i-5):i]):
                # Skip this line (don't add to modified)
                modified_lines.pop()  # Remove the line we just added
                # Look ahead for metadata= line
                j = i + 1
                while j < len(lines) and 'metadata=' not in lines[j]:
                    if 'confidence=' in lines[j]:
                        modified_lines.append(lines[j])
                    i += 1
                    j += 1

                # When we find metadata=, modify it to include sources
                if j < len(lines) and 'metadata=' in lines[j]:
                    metadata_line = lines[j]
                    # Add sources to metadata
                    if '{' in metadata_line:
                        # Insert sources before the closing brace
                        modified_metadata = metadata_line.replace(
                            '}',
                            f', "sources": [{sources_content}]}}'
                        )
                        modified_lines.append(modified_metadata)
                    else:
                        # Simple case: metadata={"topic": "xxx"}
                        # Need to reconstruct
                        modified_metadata = metadata_line.replace(
                            '"topic":',
                            f'"sources": [{sources_content}], "topic":'
                        )
                        modified_lines.append(modified_metadata)
                    i = j
            i += 1

        content = '\n'.join(modified_lines)

    # Clean up any remaining lines that just have sources=
    lines = content.split('\n')
    cleaned_lines = [line for line in lines if not line.strip().startswith('sources=') or 'metadata=' in line]
    content = '\n'.join(cleaned_lines)

    # Also fix indentation - ensure proper formatting
    # Replace lines that are just sources=[...] with nothing
    content = re.sub(r'\s+sources=\[[^\]]+\]\n', '\n', content)

    with open(init_file, 'w') as f:
        f.write(content)

    print(f"Fixed {domain}")

print("All domain modules fixed!")
