import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    APP_NAME = "pr-assistant"
    CONFIG_FILE = "config.json"

    def __init__(self):
        # Global config (User home)
        self.global_config_dir = Path(typer.get_app_dir(self.APP_NAME)) if 'typer' in globals() else Path.home() / f".{self.APP_NAME}"
        self.global_config_path = self.global_config_dir / self.CONFIG_FILE
        self._ensure_global_config_dir()

        # Local config (Current working directory)
        self.local_config_path = Path.cwd() / f".{self.APP_NAME}.json"

    def _ensure_global_config_dir(self):
        self.global_config_dir.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return self.global_config_path.exists() or self.local_config_path.exists()

    def load(self) -> Dict[str, Any]:
        config = {}
        
        # Load Global
        if self.global_config_path.exists():
            try:
                with open(self.global_config_path, 'r') as f:
                    config.update(json.load(f))
            except json.JSONDecodeError:
                pass

        # Load Local (Overrides Global)
        if self.local_config_path.exists():
            try:
                with open(self.local_config_path, 'r') as f:
                    config.update(json.load(f))
            except json.JSONDecodeError:
                pass
                
        return config

    def save(self, config: Dict[str, Any], local: bool = False):
        target_path = self.local_config_path if local else self.global_config_path
        
        # If saving locally, we might want to only save the diff, but for simplicity
        # we'll just save what's passed if it's explicitly a local save.
        # However, the current usage of 'save' in main.py passes the WHOLE config.
        # We should probably update 'save' to take specific keys or just dump everything.
        # For now, let's keep it simple: 'save' writes to global by default unless specified.
        
        with open(target_path, 'w') as f:
            json.dump(config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        config = self.load()
        return config.get(key, default)

    def set(self, key: str, value: Any, local: bool = False):
        # This is a bit tricky because 'load' returns merged.
        # If we want to set a value, we need to know WHERE to set it.
        # For simplicity, 'set' will read the specific file, update it, and write it back.
        
        target_path = self.local_config_path if local else self.global_config_path
        
        current_file_config = {}
        if target_path.exists():
            try:
                with open(target_path, 'r') as f:
                    current_file_config = json.load(f)
            except json.JSONDecodeError:
                pass
        
        current_file_config[key] = value
        
        with open(target_path, 'w') as f:
            json.dump(current_file_config, f, indent=4)
