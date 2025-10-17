#!/usr/bin/env python3
"""
Recursively rename files and symbols from 'globex_' to 'chroma_'
Skips .git and node_modules directories
Provides a summary table of changes made
"""

import os
import re
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

class GlobexToChromaRenamer:
    def __init__(self, root_path: str = ".", dry_run: bool = False):
        self.root_path = Path(root_path).resolve()
        self.dry_run = dry_run
        self.skip_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', 'node_modules'}
        self.skip_extensions = {'.pyc', '.pyo', '.pyd', '__pycache__'}
        self.logger = logging.getLogger(__name__)
        
        # Track changes for summary
        self.file_renames = []  # (old_path, new_path)
        self.symbol_changes = defaultdict(list)  # file_path: [(old_symbol, new_symbol, line_num)]
        
        # File extensions that commonly contain code symbols
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
            '.cs', '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.clj',
            '.sql', '.yaml', '.yml', '.json', '.xml', '.html', '.css', '.scss',
            '.less', '.md', '.rst', '.txt', '.sh', '.bash', '.zsh', '.fish'
        }

    def should_skip_path(self, path: Path) -> bool:
        """Check if path should be skipped"""
        parts = path.parts
        for part in parts:
            if part in self.skip_dirs:
                return True
        return path.suffix in self.skip_extensions

    def rename_file(self, file_path: Path) -> Path:
        """Rename a file if it starts with 'globex_'"""
        if file_path.name.startswith('globex_'):
            new_name = file_path.name.replace('globex_', 'chroma_', 1)
            new_path = file_path.parent / new_name
            
            if self.dry_run:
                self.file_renames.append((str(file_path), str(new_path)))
                self.logger.info(f"[DRY RUN] Would rename file: {file_path} -> {new_path}")
                return file_path
            
            try:
                file_path.rename(new_path)
                self.file_renames.append((str(file_path), str(new_path)))
                self.logger.info(f"Renamed file: {file_path} -> {new_path}")
                return new_path
            except Exception as e:
                self.logger.error(f"Error renaming file {file_path}: {e}")
                return file_path
        return file_path

    def rename_symbols_in_file(self, file_path: Path) -> None:
        """Replace 'globex_' symbols in file content"""
        if file_path.suffix not in self.code_extensions:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return

        # Pattern to match globex_ symbols (identifiers)
        # This matches globex_ followed by word characters, but not if it's part of a larger word
        pattern = r'\bglobex_\w+'
        
        changes_made = []
        new_content = content
        
        # Find all matches and their positions
        for match in re.finditer(pattern, content):
            old_symbol = match.group()
            new_symbol = old_symbol.replace('globex_', 'chroma_', 1)
            
            # Calculate line number
            line_num = content[:match.start()].count('\n') + 1
            changes_made.append((old_symbol, new_symbol, line_num))

        if changes_made:
            self.symbol_changes[str(file_path)] = changes_made
            
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would update symbols in: {file_path} ({len(changes_made)} changes)")
                return
            
            # Replace all occurrences
            new_content = re.sub(pattern, lambda m: m.group().replace('globex_', 'chroma_', 1), content)
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                self.logger.info(f"Updated symbols in: {file_path} ({len(changes_made)} changes)")
            except Exception as e:
                self.logger.error(f"Error writing file {file_path}: {e}")

    def process_directory(self, directory: Path) -> None:
        """Recursively process directory"""
        if self.should_skip_path(directory):
            return
            
        try:
            # Process files in current directory
            for item in directory.iterdir():
                if item.is_file():
                    if not self.should_skip_path(item):
                        # First rename symbols in the file
                        self.rename_symbols_in_file(item)
                        # Then rename the file itself (returns new path if renamed)
                        self.rename_file(item)
                        
                elif item.is_dir():
                    # Recursively process subdirectories
                    self.process_directory(item)
                    
        except PermissionError:
            self.logger.warning(f"Permission denied: {directory}")
        except Exception as e:
            self.logger.error(f"Error processing directory {directory}: {e}")

    def print_summary_table(self) -> None:
        """Print a summary table of all changes made"""
        self.logger.info("\n" + "="*80)
        self.logger.info("SUMMARY OF CHANGES")
        self.logger.info("="*80)
        
        # File renames summary
        if self.file_renames:
            self.logger.info(f"\n📁 FILE RENAMES ({len(self.file_renames)} files):")
            self.logger.info("-" * 60)
            for old_path, new_path in self.file_renames:
                old_name = Path(old_path).name
                new_name = Path(new_path).name
                self.logger.info(f"  {old_name} → {new_name}")
        else:
            self.logger.info("\n📁 FILE RENAMES: None")
        
        # Symbol changes summary
        total_symbol_changes = sum(len(changes) for changes in self.symbol_changes.values())
        if total_symbol_changes > 0:
            self.logger.info(f"\n🔧 SYMBOL CHANGES ({total_symbol_changes} symbols in {len(self.symbol_changes)} files):")
            self.logger.info("-" * 60)
            
            for file_path, changes in self.symbol_changes.items():
                rel_path = os.path.relpath(file_path, self.root_path)
                self.logger.info(f"\n  📄 {rel_path}:")
                for old_symbol, new_symbol, line_num in changes:
                    self.logger.info(f"    Line {line_num:4d}: {old_symbol} → {new_symbol}")
        else:
            self.logger.info("\n🔧 SYMBOL CHANGES: None")
        
        # Overall summary
        self.logger.info(f"\n📊 TOTAL SUMMARY:")
        self.logger.info(f"  • Files renamed: {len(self.file_renames)}")
        self.logger.info(f"  • Files with symbol changes: {len(self.symbol_changes)}")
        self.logger.info(f"  • Total symbol changes: {total_symbol_changes}")
        self.logger.info("="*80)

    def run(self) -> None:
        """Run the renaming process"""
        mode = "[DRY RUN] " if self.dry_run else ""
        self.logger.info(f"{mode}Starting globex_ to chroma_ renaming in: {self.root_path}")
        self.logger.info(f"Skipping directories: {', '.join(sorted(self.skip_dirs))}")
        if self.dry_run:
            self.logger.info("🔍 DRY RUN MODE - No actual changes will be made")
        self.logger.info("-" * 60)
        
        self.process_directory(self.root_path)
        self.print_summary_table()

def bulk_rename(root_path: str, dry_run: bool = False) -> None:
    """
    Convenience function for bulk renaming operations.
    This function is used by tests for compatibility.
    """
    renamer = GlobexToChromaRenamer(root_path, dry_run=dry_run)
    renamer.run()

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Recursively rename files and symbols from 'globex_' to 'chroma_'"
    )
    parser.add_argument(
        '--path',
        default='.',
        help='Root path to start renaming (default: current directory)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be renamed without making changes'
    )
    parser.add_argument(
        '--check',
        action='store_true',
        help='Alias for --dry-run: show what would be renamed without making changes'
    )
    
    args = parser.parse_args()
    
    # --check is an alias for --dry-run
    dry_run = args.dry_run or args.check
    
    renamer = GlobexToChromaRenamer(args.path, dry_run=dry_run)
    renamer.run()

if __name__ == "__main__":
    main()