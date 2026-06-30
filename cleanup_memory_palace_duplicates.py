#!/usr/bin/env python3
"""
Clean up duplicate discovery entries in GraphPalace (Memory Palace).

This script removes duplicate discovery files that were created due to the
deduplication bug, keeping only the most recent version of each discovery.
"""

import os
import re
from datetime import datetime
from collections import defaultdict
import glob

# Memory palace path
MEMORY_PALACE_PATH = "/Users/gjw255/.claude/projects/-Users-gjw255-astrodata-SWARM-BIODISC/memory/"

def extract_discovery_id(filename):
    """Extract discovery ID from filename"""
    match = re.match(r'discovery_discovery_([a-f0-9]+)_[0-9]+_[0-9]+\.md', filename)
    if match:
        return match.group(1)
    return None

def extract_timestamp(filename):
    """Extract timestamp from filename for sorting"""
    match = re.match(r'discovery_discovery_[a-f0-9]+_([0-9]+)_([0-9]+)\.md', filename)
    if match:
        date_part = match.group(1)
        time_part = match.group(2)
        return int(f"{date_part}{time_part}")
    return 0

def find_duplicate_discoveries():
    """Find all duplicate discovery files"""
    os.chdir(MEMORY_PALACE_PATH)

    # Find all discovery files
    discovery_files = glob.glob("discovery_discovery_*_[0-9]*_[0-9]*.md")

    # Group by discovery ID
    discovery_groups = defaultdict(list)
    for filename in discovery_files:
        discovery_id = extract_discovery_id(filename)
        if discovery_id:
            discovery_groups[discovery_id].append(filename)

    # Find duplicates (groups with more than 1 file)
    duplicates = {k: v for k, v in discovery_groups.items() if len(v) > 1}

    return duplicates

def cleanup_duplicates(duplicates, dry_run=True):
    """Remove duplicate files, keeping only the most recent"""
    removed_count = 0
    kept_count = 0

    print(f"{'DRY RUN' if dry_run else 'CLEANUP MODE'}")
    print(f"Found {len(duplicates)} discoveries with duplicates\n")

    for discovery_id, files in duplicates.items():
        # Sort by timestamp (most recent last)
        files_sorted = sorted(files, key=extract_timestamp)

        # Keep the most recent, remove the rest
        to_keep = files_sorted[-1]
        to_remove = files_sorted[:-1]

        print(f"Discovery {discovery_id}:")
        print(f"  Keeping: {to_keep} (most recent)")

        for file_to_remove in to_remove:
            if dry_run:
                print(f"  Would remove: {file_to_remove}")
            else:
                os.remove(file_to_remove)
                print(f"  Removed: {file_to_remove}")
            removed_count += 1

        kept_count += 1
        print()

    print(f"Summary:")
    print(f"  Discoveries cleaned: {kept_count}")
    print(f"  Files removed: {removed_count}")
    print(f"  Files kept: {kept_count}")

    return removed_count

def update_memory_index():
    """Update MEMORY.md to remove references to deleted files"""
    memory_index_path = os.path.join(MEMORY_PALACE_PATH, "MEMORY.md")

    if not os.path.exists(memory_index_path):
        print("MEMORY.md not found, skipping index update")
        return

    print("Updating MEMORY.md index...")

    # Read current index
    with open(memory_index_path, 'r') as f:
        content = f.read()

    # Remove duplicate entries (keeping references to existing files only)
    lines = content.split('\n')
    unique_lines = []
    seen_discoveries = set()

    for line in lines:
        # Check if this is a discovery reference line
        if 'discovery_discovery_' in line and '.md' in line:
            # Extract discovery ID
            match = re.search(r'discovery_discovery_([a-f0-9]+)_[0-9]+_[0-9]+\.md', line)
            if match:
                discovery_id = match.group(1)
                if discovery_id not in seen_discoveries:
                    seen_discoveries.add(discovery_id)
                    unique_lines.append(line)
                else:
                    print(f"  Removing duplicate index entry for {discovery_id}")
            else:
                unique_lines.append(line)
        else:
            unique_lines.append(line)

    # Write cleaned index
    with open(memory_index_path, 'w') as f:
        f.write('\n'.join(unique_lines))

    print("MEMORY.md index updated")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Clean up duplicate discoveries in memory palace')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without making changes')
    parser.add_argument('--execute', action='store_true', help='Actually remove duplicate files')

    args = parser.parse_args()

    if args.execute:
        dry_run = False
        print("🧹 CLEANUP MODE - Will actually delete files!")
    else:
        dry_run = True
        print("🔍 DRY RUN MODE - No files will be deleted")

    # Find duplicates
    duplicates = find_duplicate_discoveries()

    if not duplicates:
        print("✅ No duplicate discoveries found!")
    else:
        # Clean up duplicates
        cleanup_duplicates(duplicates, dry_run=dry_run)

        if not dry_run:
            # Update memory index
            update_memory_index()
            print("\n✅ Memory palace cleanup complete!")
        else:
            print("\n💡 Run with --execute to actually remove duplicates")