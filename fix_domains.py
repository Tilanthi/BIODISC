#!/usr/bin/env python3
"""Fix DomainQueryResult calls in domain modules"""
import os
import re

domains_dir = "/Users/gjw255/astrodata/SWARM/BIODISC/biodisc_core/domains"

for domain in os.listdir(domains_dir):
    domain_path = os.path.join(domains_dir, domain)
    if not os.path.isdir(domain_path):
        continue

    init_file = os.path.join(domain_path, "__init__.py")
    if not os.path.exists(init_file):
        continue

    with open(init_file, 'r') as f:
        content = f.read()

    # Fix DomainQueryResult calls
    content = re.sub(
        r'DomainQueryResult\(\s*success=([A-Za-z]+),',
        r'DomainQueryResult(\n            domain_name="{}",\n            ' + r'answer=',
        content
    )

    # Remove remaining 'success' lines
    content = re.sub(r',\s*success=([A-Za-z]+),', ',', content)

    # Fix the first parameter to be domain_name
    content = content.replace('DomainQueryResult(\n            domain_name="{}",\n            answer=', 'DomainQueryResult(\n            domain_name="' + domain + '",\n            answer=')

    with open(init_file, 'w') as f:
        f.write(content)

    print(f"Fixed {domain}")

print("All domain modules fixed!")
