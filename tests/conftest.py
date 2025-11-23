import pytest
import os
import json
from pathlib import Path
from pr_assistant.config import ConfigManager
from pr_assistant.rate_limiter import RateLimiter

@pytest.fixture
def mock_config_dir(tmp_path):
    """
    Fixture to mock the configuration directory.
    """
    config_dir = tmp_path / ".pr_assistant"
    config_dir.mkdir()
    return config_dir

@pytest.fixture
def mock_config_manager(mock_config_dir, monkeypatch, tmp_path):
    """
    Fixture to mock ConfigManager using a temporary directory.
    """
    monkeypatch.setattr("pr_assistant.config.ConfigManager.APP_NAME", "pr-assistant-test")
    
    # We need to patch where ConfigManager looks for the dir
    # Since ConfigManager uses typer.get_app_dir or home, we'll patch the init logic slightly
    # or just patch the class attribute if possible, but instance attributes are set in __init__.
    # Easiest way is to patch pathlib.Path.home or typer.get_app_dir if used.
    
    # Let's patch the `_ensure_config_dir` or just the path resolution.
    # Actually, ConfigManager uses `typer.get_app_dir` or `Path.home()`.
    # Let's patch `typer.get_app_dir` to return our tmp path.
    
    def mock_get_app_dir(app_name):
        return str(mock_config_dir)
        
    monkeypatch.setattr("typer.get_app_dir", mock_get_app_dir)
    monkeypatch.setattr("pathlib.Path.home", lambda: mock_config_dir)
    
    # Ensure we are in a clean directory for local config tests
    monkeypatch.chdir(tmp_path)
    
    return ConfigManager()

@pytest.fixture
def mock_rate_limiter(mock_config_dir, monkeypatch):
    """
    Fixture to mock RateLimiter using a temporary directory.
    """
    monkeypatch.setattr("pathlib.Path.home", lambda: mock_config_dir)
    return RateLimiter()
