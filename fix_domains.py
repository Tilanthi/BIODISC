#!/usr/bin/env python3
# Copyright 2026 Tilanthi
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
