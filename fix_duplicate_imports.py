#!/usr/bin/env python3
"""
Fix Duplicate Imports in BIODISC Codebase

Automatically removes duplicate import statements from Python files.
Handles multiple patterns:
1. Consecutive repeated import blocks
2. Scattered duplicate imports within functions
3. Multiple types of imports (import, from...import)

Usage:
    python fix_duplicate_imports.py --dry-run  # Preview changes
    python fix_duplicate_imports.py            # Apply fixes
    python fix_duplicate_imports.py --file path/to/file.py  # Fix specific file
"""

import os
import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import shutil


class DuplicateImportFixer:
    """Fix duplicate imports in Python files."""

    def __init__(self, dry_run: bool = False, backup: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.stats = defaultdict(lambda: {'removed': 0, 'kept': 0, 'files': 0})

    # Import pattern matching
    IMPORT_PATTERNS = [
        # Standard import: import X
        r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*(\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)',
        # From import: from X import Y
        r'^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import\s+(.+)',
        # Import with alias: import X as Y
        r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+as\s+[a-zA-Z_][a-zA-Z0-9_]*',
        # From import with aliases: from X import Y as Z
        r'^from\s+([a-zA-Z_][a-zA-Z0-9_.]*)\s+import\s+([a-zA-Z_][a-zA-Z0-9_]*(\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)\s+as\s+[a-zA-Z_][a-zA-Z0-9_]*',
    ]

    def extract_import_key(self, line: str) -> str:
        """Extract a normalized key for an import statement."""
        line = line.strip()

        # Skip comments and non-imports
        if not line or line.startswith('#'):
            return None

        for pattern in self.IMPORT_PATTERNS:
            match = re.match(pattern, line)
            if match:
                # Return the full line as the key for exact matching
                # This preserves differences like "import numpy as np" vs "import numpy"
                return line

        return None

    def fix_file(self, filepath: Path) -> bool:
        """Fix duplicate imports in a single file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            if not lines:
                return False

            original_lines = lines.copy()
            removed_count = 0
            kept_imports: Set[str] = set()

            # Track which imports have been seen (including their line position)
            import_occurrences: Dict[str, List[int]] = defaultdict(list)

            # First pass: find all import statements
            for i, line in enumerate(lines):
                import_key = self.extract_import_key(line)
                if import_key:
                    import_occurrences[import_key].append(i)

            # Second pass: remove duplicates
            # Keep the first occurrence, remove subsequent ones
            imports_to_remove = set()
            for import_stmt, positions in import_occurrences.items():
                if len(positions) > 1:
                    # Keep first occurrence, mark rest for removal
                    for pos in positions[1:]:
                        imports_to_remove.add(pos)

            # Remove duplicate imports (in reverse order to preserve line numbers)
            for pos in sorted(imports_to_remove, reverse=True):
                line = lines[pos].strip()

                # Check if it's inside a function body
                is_inside_function = self._is_inside_function(lines, pos)

                # Special handling for imports inside functions:
                # If the same import exists at module level, remove the one inside function
                module_level_imports = [p for p in import_occurrences[self.extract_import_key(lines[pos])]
                                       if p < pos and not self._is_inside_function(lines, p)]

                if is_inside_function and module_level_imports:
                    # Safe to remove - module-level import exists
                    lines.pop(pos)
                    removed_count += 1
                elif not is_inside_function:
                    # Module-level duplicate - safe to remove
                    # Also remove any trailing blank lines to clean up
                    lines.pop(pos)
                    while pos < len(lines) and lines[pos].strip() == '':
                        lines.pop(pos)
                    removed_count += 1
                else:
                    # Import inside function with no module-level equivalent
                    # Keep it to avoid breaking function scope
                    kept_imports.add(self.extract_import_key(lines[pos]))

            # Clean up consecutive blank lines that may result
            lines = self._cleanup_blank_lines(lines)

            # Check if anything changed
            if lines != original_lines:
                if self.backup and not self.dry_run:
                    backup_path = filepath.with_suffix(filepath.suffix + '.bak')
                    shutil.copy2(filepath, backup_path)

                if not self.dry_run:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.writelines(lines)

                print(f"{'[DRY RUN] ' if self.dry_run else ''}Fixed {filepath}: removed {removed_count} duplicate imports")
                return True

            return False

        except Exception as e:
            print(f"Error processing {filepath}: {e}", file=sys.stderr)
            return False

    def _is_inside_function(self, lines: List[str], pos: int) -> bool:
        """Check if line at pos is inside a function definition."""
        # Look backwards for a function definition
        indent_level = len(lines[pos]) - len(lines[pos].lstrip())

        for i in range(pos - 1, -1, -1):
            line = lines[i].rstrip()

            # Stop if we hit a class or module-level definition with less or equal indent
            if line.strip() and not line.strip().startswith('#'):
                line_indent = len(line) - len(line.lstrip())
                if line_indent < indent_level:
                    if re.match(r'^\s*(def|class|async def)\s+', line):
                        return True
                    # If we hit something at module level, we're not in a function
                    if line_indent == 0:
                        return False

        return False

    def _cleanup_blank_lines(self, lines: List[str]) -> List[str]:
        """Remove excessive consecutive blank lines (max 2)."""
        result = []
        blank_count = 0

        for line in lines:
            if line.strip() == '':
                blank_count += 1
                if blank_count <= 2:
                    result.append(line)
            else:
                blank_count = 0
                result.append(line)

        return result

    def fix_directory(self, directory: Path, pattern: str = '*.py') -> Dict[str, any]:
        """Fix all Python files in a directory recursively."""
        results = {
            'fixed': [],
            'skipped': [],
            'errors': [],
            'total_removed': 0
        }

        for filepath in directory.rglob(pattern):
            if filepath.is_file():
                if self.fix_file(filepath):
                    results['fixed'].append(filepath)
                    results['total_removed'] += self._count_removed_imports(filepath)
                else:
                    results['skipped'].append(filepath)

        return results

    def _count_removed_imports(self, filepath: Path) -> int:
        """Count imports that would be removed from a file."""
        # This is a rough estimate based on the fix
        return 0


def analyze_duplicates(directory: Path) -> Dict[str, Dict]:
    """Analyze files for duplicate imports without modifying them."""
    fixer = DuplicateImportFixer(dry_run=True)
    analysis = defaultdict(lambda: {
        'file': str(directory.relative_to(Path.cwd())),
        'duplicate_imports': defaultdict(list),
        'total_duplicates': 0
    })

    import_pattern = re.compile(r'^(import|from)\s+')

    for filepath in directory.rglob('*.py'):
        if not filepath.is_file():
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            import_positions: Dict[str, List[int]] = defaultdict(list)

            for i, line in enumerate(lines):
                if import_pattern.match(line.strip()):
                    import_stmt = line.strip()
                    import_positions[import_stmt].append(i)

            # Count duplicates
            file_duplicates = defaultdict(list)
            total = 0
            for import_stmt, positions in import_positions.items():
                if len(positions) > 1:
                    file_duplicates[import_stmt] = positions
                    total += len(positions) - 1  # Subtract 1 to keep first

            if total > 0:
                rel_path = str(filepath.relative_to(directory))
                analysis[rel_path] = {
                    'file': rel_path,
                    'duplicate_imports': dict(file_duplicates),
                    'total_duplicates': total
                }

        except Exception as e:
            print(f"Error analyzing {filepath}: {e}", file=sys.stderr)

    return analysis


def main():
    parser = argparse.ArgumentParser(
        description='Fix duplicate imports in BIODISC codebase'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Do not create backup files'
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Fix a specific file instead of scanning directory'
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze and report duplicates without fixing'
    )
    parser.add_argument(
        '--dir',
        type=str,
        default='biodisc_core',
        help='Directory to scan (default: biodisc_core)'
    )

    args = parser.parse_args()

    # Set up directory
    base_dir = Path(args.dir)
    if not base_dir.exists():
        print(f"Error: Directory {base_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    # Analysis mode
    if args.analyze:
        print("Analyzing duplicate imports...\n")
        analysis = analyze_duplicates(base_dir)

        # Sort by severity (total duplicates)
        sorted_files = sorted(
            analysis.items(),
            key=lambda x: x[1]['total_duplicates'],
            reverse=True
        )

        for filepath, info in sorted_files:
            print(f"\n{filepath}")
            print(f"  Total duplicates: {info['total_duplicates']}")
            print(f"  Types of duplicated imports:")

            for import_stmt, positions in info['duplicate_imports'].items():
                print(f"    - {import_stmt[:80]}... ({len(positions)} occurrences)")

        total_duplicates = sum(info['total_duplicates'] for info in analysis.values())
        print(f"\n{'='*60}")
        print(f"Total files with duplicates: {len(analysis)}")
        print(f"Total duplicate imports: {total_duplicates}")

        return

    # Fix mode
    fixer = DuplicateImportFixer(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )

    if args.file:
        # Fix single file
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Error: File {filepath} does not exist", file=sys.stderr)
            sys.exit(1)

        success = fixer.fix_file(filepath)
        sys.exit(0 if success else 1)
    else:
        # Fix directory
        print(f"Scanning {base_dir} for duplicate imports...")
        if args.dry_run:
            print("DRY RUN MODE - No files will be modified\n")

        results = fixer.fix_directory(base_dir)

        print(f"\n{'='*60}")
        print(f"Results:")
        print(f"  Files fixed: {len(results['fixed'])}")
        print(f"  Files skipped: {len(results['skipped'])}")
        print(f"  Errors: {len(results['errors'])}")

        if results['fixed']:
            print(f"\nFixed files:")
            for f in results['fixed']:
                print(f"  - {f}")


if __name__ == '__main__':
    main()
