import pytest
from pr_assistant.config import ConfigManager

def test_config_initialization(mock_config_manager):
    assert not mock_config_manager.exists()
    assert mock_config_manager.load() == {}

def test_config_save_and_load(mock_config_manager):
    data = {"key": "value", "number": 123}
    mock_config_manager.save(data)
    
    assert mock_config_manager.exists()
    loaded = mock_config_manager.load()
    assert loaded == data

def test_config_get_set(mock_config_manager):
    mock_config_manager.set("test_key", "test_value")
    assert mock_config_manager.get("test_key") == "test_value"
    assert mock_config_manager.get("non_existent") is None
    assert mock_config_manager.get("non_existent", "default") == "default"

def test_config_persistence(mock_config_manager):
    mock_config_manager.set("persistent", True)
    
    # Reload from disk
    new_manager = ConfigManager()
    assert new_manager.get("persistent") is True
