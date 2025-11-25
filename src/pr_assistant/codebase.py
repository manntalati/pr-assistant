import os
import fnmatch
from typing import List, Dict

class CodebaseReader:
    def __init__(self, root_dir: str = "."):
        self.root_dir = os.path.abspath(root_dir)
        self.ignore_patterns = self._load_gitignore()

    def _load_gitignore(self) -> List[str]:
        ignore_path = os.path.join(self.root_dir, ".gitignore")
        patterns = [".git", "__pycache__", "*.pyc", ".DS_Store", "venv", ".env"]
        if os.path.exists(ignore_path):
            with open(ignore_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        return patterns

    def _is_ignored(self, path: str) -> bool:
        rel_path = os.path.relpath(path, self.root_dir)
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
            if pattern.endswith("/") and rel_path.startswith(pattern.rstrip("/")):
                return True
        return False

    def get_file_structure(self) -> str:
        """Returns a string representation of the file tree."""
        structure = []
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d))]
            
            level = root.replace(self.root_dir, '').count(os.sep)
            indent = ' ' * 4 * (level)
            structure.append(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                if not self._is_ignored(os.path.join(root, f)):
                    structure.append(f"{subindent}{f}")
        return "\n".join(structure)

    def read_files(self, extensions: List[str] = None) -> Dict[str, str]:
        """Reads all non-ignored files, optionally filtering by extension."""
        files_content = {}
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if not self._is_ignored(os.path.join(root, d))]
            
            for f in files:
                if self._is_ignored(os.path.join(root, f)):
                    continue
                
                if extensions and not any(f.endswith(ext) for ext in extensions):
                    continue

                full_path = os.path.join(root, f)
                try:
                    with open(full_path, "r", encoding="utf-8") as file_obj:
                        relative_path = os.path.relpath(full_path, self.root_dir).replace("\\", "/")
                        files_content[relative_path] = file_obj.read()
                except UnicodeDecodeError:
                    pass
        return files_content
