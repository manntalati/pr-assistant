import pytest
import os
from pr_assistant.codebase import CodebaseReader

@pytest.fixture
def mock_repo(tmp_path):
    """
    Creates a mock repository structure.
    """
    # Create files
    (tmp_path / "main.py").write_text("print('hello')")
    (tmp_path / "utils.py").write_text("def util(): pass")
    (tmp_path / ".gitignore").write_text("*.log\nignored_dir/")
    
    # Create ignored stuff
    (tmp_path / "test.log").write_text("log content")
    
    ignored_dir = tmp_path / "ignored_dir"
    ignored_dir.mkdir()
    (ignored_dir / "secret.py").write_text("secret")
    
    # Create nested dir
    nested = tmp_path / "src"
    nested.mkdir()
    (nested / "app.py").write_text("app code")
    
    return tmp_path

def test_codebase_reader_init(mock_repo):
    reader = CodebaseReader(root_dir=str(mock_repo))
    assert "*.log" in reader.ignore_patterns
    assert "ignored_dir/" in reader.ignore_patterns
    assert ".git" in reader.ignore_patterns # Default

def test_codebase_reader_structure(mock_repo):
    reader = CodebaseReader(root_dir=str(mock_repo))
    structure = reader.get_file_structure()
    
    assert "main.py" in structure
    assert "src/" in structure
    assert "app.py" in structure
    
    # Ignored files shouldn't be there
    assert "test.log" not in structure
    assert "ignored_dir/" not in structure
    assert "secret.py" not in structure

def test_codebase_reader_content(mock_repo):
    reader = CodebaseReader(root_dir=str(mock_repo))
    content = reader.read_files()
    
    assert "main.py" in content
    assert content["main.py"] == "print('hello')"
    assert "src/app.py" in content
    
    assert "test.log" not in content
    assert "ignored_dir/secret.py" not in content
