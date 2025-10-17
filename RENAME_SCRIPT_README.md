# Globex to Chroma Renamer

This Python script recursively renames files and symbols from `globex_` to `chroma_` throughout a directory tree.

## Features

- **File Renaming**: Renames any files that start with `globex_` to `chroma_`
- **Symbol Renaming**: Updates `globex_` identifiers in code files to `chroma_`
- **Smart Skipping**: Automatically skips `.git`, `node_modules`, and other common directories
- **Summary Table**: Provides a detailed summary of all changes made
- **Dry Run Mode**: Preview changes without making modifications

## Usage

### Basic Usage
```bash
# Rename in current directory
python3 rename_globex_to_chroma.py

# Rename in specific directory
python3 rename_globex_to_chroma.py /path/to/project
```

### Dry Run (Preview Mode)
```bash
# Preview what would be changed without making modifications
python3 rename_globex_to_chroma.py --dry-run
```

## Supported File Types

The script processes symbols in the following file types:
- Python (`.py`)
- JavaScript/TypeScript (`.js`, `.ts`, `.jsx`, `.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`, `.hpp`)
- Configuration files (`.yaml`, `.yml`, `.json`, `.xml`)
- Documentation (`.md`, `.rst`, `.txt`)
- And many more...

## Example Output

```
Starting globex_ to chroma_ renaming in: /workspaces/copilot-fundamentals-training
Skipping directories: .git, __pycache__, .pytest_cache, node_modules
----------------------------------------------------------------
Updated symbols in: demos/copilot-features/app/globex_service.py (15 changes)
Renamed file: demos/copilot-features/app/globex_service.py -> demos/copilot-features/app/chroma_service.py
Updated symbols in: demos/copilot-features/cli/globex_cli.py (8 changes)
Renamed file: demos/copilot-features/cli/globex_cli.py -> demos/copilot-features/cli/chroma_cli.py

================================================================================
SUMMARY OF CHANGES
================================================================================

📁 FILE RENAMES (8 files):
------------------------------------------------------------
  globex_service.py → chroma_service.py
  globex_cli.py → chroma_cli.py
  globex_utils.py → chroma_utils.py
  globex_refactor.py → chroma_refactor.py
  globex_logging.yaml → chroma_logging.yaml
  globex_settings.yaml → chroma_settings.yaml
  globex_api.md → chroma_api.md
  globex_architecture.md → chroma_architecture.md

🔧 SYMBOL CHANGES (45 symbols in 6 files):

  📄 demos/copilot-features/app/chroma_service.py:
    Line   10: GlobexService → ChromaService
    Line   16: globex_add_item → chroma_add_item
    Line   25: globex_get_items → chroma_get_items
    Line   32: globex_clear → chroma_clear

  📄 demos/copilot-features/cli/chroma_cli.py:
    Line    8: globex_main → chroma_main
    Line   15: globex_process → chroma_process

📊 TOTAL SUMMARY:
  • Files renamed: 8
  • Files with symbol changes: 6
  • Total symbol changes: 45
================================================================================
```

## Safety Features

- **Backup Recommendation**: Always backup your code before running the script
- **Git Integration**: The script skips `.git` directories to preserve version control
- **Error Handling**: Graceful handling of permission errors and file access issues
- **Dry Run Mode**: Test the script without making changes first

## Running in Your Workspace

To run this script on your workspace:

1. **Dry run first** (recommended):
   ```bash
   python3 rename_globex_to_chroma.py --dry-run
   ```

2. **Run the actual renaming**:
   ```bash
   python3 rename_globex_to_chroma.py
   ```

3. **Target specific directory**:
   ```bash
   python3 rename_globex_to_chroma.py demos/copilot-features/
   ```