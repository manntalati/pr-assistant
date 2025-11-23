import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    APP_NAME = "pr-assistant"
    CONFIG_FILE = "config.json"

    def __init__(self):
        self.config_dir = Path(typer.get_app_dir(self.APP_NAME)) if 'typer' in globals() else Path.home() / f".{self.APP_NAME}"
        self.config_path = self.config_dir / self.CONFIG_FILE
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def exists(self) -> bool:
        return self.config_path.exists()

    def load(self) -> Dict[str, Any]:
        if not self.exists():
            return {}
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    def save(self, config: Dict[str, Any]):
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        config = self.load()
        return config.get(key, default)

    def set(self, key: str, value: Any):
        config = self.load()
        config[key] = value
        self.save(config)
