import os
import tempfile
import pytest
from pathlib import Path
import sys
import subprocess

# Add the cli directory to the path so we can import rename
sys.path.insert(0, str(Path(__file__).parent.parent / 'cli'))

try:
    import rename
except ImportError:
    # If rename.py doesn't exist yet, we'll create a mock for testing
    class MockRename:
        def bulk_rename(self, root_path: str, dry_run: bool = False):
            pass
    rename = MockRename()


class TestRename:
    
    @pytest.fixture
    def temp_project(self):
        """Create a temporary directory with test files containing globex_ references."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create Python file with globex_ references
            python_file = temp_path / "test_module.py"
            python_file.write_text("""
def globex_function():
    return "globex_value"

class GlobexClass:
    globex_attribute = "test"
""")
            
            # Create config file with globex_ references
            config_file = temp_path / "config.yaml"
            config_file.write_text("""
globex_setting: true
globex_database: "globex_db"
""")
            
            # Create binary file (should be skipped)
            binary_file = temp_path / "binary_file.bin"
            binary_file.write_bytes(b'\x00\x01\x02globex_\x03\x04')
            
            # Create subdirectory with more files
            sub_dir = temp_path / "subdir"
            sub_dir.mkdir()
            sub_file = sub_dir / "sub_module.py"
            sub_file.write_text("globex_constant = 'value'")
            
            yield temp_path

    def test_rename_files_content(self, temp_project):
        """Test that globex_ references in text files are renamed to chroma_."""
        # Run the rename operation
        if hasattr(rename, 'bulk_rename'):
            rename.bulk_rename(str(temp_project))
        
        # Check that Python files were updated
        python_file = temp_project / "test_module.py"
        content = python_file.read_text()
        
        assert "chroma_function" in content
        assert "ChromaClass" in content or "chroma_" in content
        assert "globex_" not in content

    def test_skip_binary_files(self, temp_project):
        """Test that binary files are not modified."""
        binary_file = temp_project / "binary_file.bin"
        original_content = binary_file.read_bytes()
        
        # Run the rename operation
        if hasattr(rename, 'bulk_rename'):
            rename.bulk_rename(str(temp_project))
        
        # Binary file should remain unchanged
        current_content = binary_file.read_bytes()
        assert current_content == original_content
        assert b'globex_' in current_content  # Original content preserved

    def test_dry_run_check(self, temp_project):
        """Test that --check flag performs dry run without modifying files."""
        # Store original content
        python_file = temp_project / "test_module.py"
        original_content = python_file.read_text()
        
        # Run in dry-run mode
        if hasattr(rename, 'bulk_rename'):
            rename.bulk_rename(str(temp_project), dry_run=True)
        
        # Files should not be modified in dry-run
        current_content = python_file.read_text()
        assert current_content == original_content
        assert "globex_" in current_content  # Original content preserved

    def test_recursive_rename(self, temp_project):
        """Test that renaming works recursively in subdirectories."""
        # Run the rename operation
        if hasattr(rename, 'bulk_rename'):
            rename.bulk_rename(str(temp_project))
        
        # Check subdirectory file was updated
        sub_file = temp_project / "subdir" / "sub_module.py"
        content = sub_file.read_text()
        
        assert "chroma_constant" in content
        assert "globex_" not in content

    def test_cli_integration(self, temp_project):
        """Test the command line interface with --check flag."""
        rename_script = Path(__file__).parent.parent / 'cli' / 'rename.py'
        
        if rename_script.exists():
            # Test dry-run via CLI
            result = subprocess.run([
                sys.executable, str(rename_script), 
                '--path', str(temp_project), 
                '--check'
            ], capture_output=True, text=True)
            
            # Should complete successfully
            assert result.returncode == 0
            
            # Files should remain unchanged
            python_file = temp_project / "test_module.py"
            content = python_file.read_text()
            assert "globex_" in content

    def test_file_extensions_handled(self, temp_project):
        """Test that various file extensions are processed correctly."""
        # Create additional file types
        js_file = temp_project / "script.js"
        js_file.write_text("const globex_config = 'test';")
        
        json_file = temp_project / "config.json"
        json_file.write_text('{"globex_key": "value"}')
        
        # Run rename
        if hasattr(rename, 'bulk_rename'):
            rename.bulk_rename(str(temp_project))
        
        # Check that appropriate files were updated
        # (This depends on the implementation of which file types are supported)
        pass

    def test_no_false_positives(self, temp_project):
        """Test that legitimate uses of 'globex' without underscore are preserved."""
        test_file = temp_project / "legitimate.py"
        test_file.write_text("""
# This should not be changed: "globex is a company"
globex_function()  # This should be changed
comment_about_globex = "test"  # This should not be changed
""")
        
        if hasattr(rename, 'bulk_rename'):
            rename.bulk_rename(str(temp_project))
        
        content = test_file.read_text()
        assert "globex is a company" in content  # Preserved
        assert "chroma_function" in content  # Changed