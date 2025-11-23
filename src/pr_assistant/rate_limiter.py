import time
import json
from pathlib import Path
from typing import Dict
from datetime import datetime, timedelta

class RateLimiter:
    """
    Simple client-side rate limiter to prevent abuse.
    Tracks usage in a local JSON file.
    """
    def __init__(self, max_requests_per_hour: int = 50):
        self.max_requests = max_requests_per_hour
        self.storage_path = Path.home() / ".pr_assistant" / "usage.json"
        self._ensure_storage()

    def _ensure_storage(self):
        if not self.storage_path.parent.exists():
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._save_usage({})

    def _load_usage(self) -> Dict[str, float]:
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_usage(self, usage: Dict[str, float]):
        with open(self.storage_path, 'w') as f:
            json.dump(usage, f)

    def _cleanup_old_requests(self, usage: Dict[str, float]) -> Dict[str, float]:
        cutoff = time.time() - 3600
        return {k: v for k, v in usage.items() if v > cutoff}

    def check_limit(self) -> bool:
        """
        Returns True if request is allowed, False otherwise.
        """
        usage = self._load_usage()
        usage = self._cleanup_old_requests(usage)
        
        if len(usage) >= self.max_requests:
            return False
        
        request_id = str(time.time())
        usage[request_id] = time.time()
        self._save_usage(usage)
        return True

    def get_remaining(self) -> int:
        usage = self._load_usage()
        usage = self._cleanup_old_requests(usage)
        return max(0, self.max_requests - len(usage))
