import pytest
from unittest.mock import MagicMock
from pr_assistant.agent import Agent

@pytest.fixture
def mock_genai(monkeypatch):
    mock_genai = MagicMock()
    monkeypatch.setattr("pr_assistant.agent.genai", mock_genai)
    return mock_genai

@pytest.fixture
def mock_config(monkeypatch):
    mock_conf = MagicMock()
    mock_conf.get.return_value = "dummy_key"
    monkeypatch.setattr("pr_assistant.agent.ConfigManager", lambda: mock_conf)
    return mock_conf

@pytest.fixture
def mock_codebase(monkeypatch):
    mock_cb = MagicMock()
    mock_cb.get_file_structure.return_value = "file structure"
    monkeypatch.setattr("pr_assistant.agent.CodebaseReader", lambda: mock_cb)
    return mock_cb

@pytest.fixture
def mock_rate_limiter(monkeypatch):
    mock_rl = MagicMock()
    mock_rl.check_limit.return_value = True
    monkeypatch.setattr("pr_assistant.agent.RateLimiter", lambda: mock_rl)
    return mock_rl

def test_agent_init(mock_genai, mock_config, mock_codebase, mock_rate_limiter):
    agent = Agent()
    mock_genai.configure.assert_called_with(api_key="dummy_key")
    mock_genai.GenerativeModel.assert_called_with('gemini-flash-latest')

def test_propose_prs_success(mock_genai, mock_config, mock_codebase, mock_rate_limiter):
    agent = Agent()
    mock_model = mock_genai.GenerativeModel.return_value
    
    # Mock response
    mock_response = MagicMock()
    mock_response.text = '{"prs": [{"title": "Test PR"}]}'
    mock_model.generate_content.return_value = mock_response
    
    prs = agent.propose_prs("instruction")
    
    assert len(prs) == 1
    assert prs[0]["title"] == "Test PR"
    mock_rate_limiter.check_limit.assert_called()

def test_propose_prs_rate_limited(mock_genai, mock_config, mock_codebase, mock_rate_limiter):
    mock_rate_limiter.check_limit.return_value = False
    agent = Agent()
    
    with pytest.raises(RuntimeError, match="Rate limit exceeded"):
        agent.propose_prs("instruction")

def test_propose_prs_json_error(mock_genai, mock_config, mock_codebase, mock_rate_limiter):
    agent = Agent()
    mock_model = mock_genai.GenerativeModel.return_value
    
    mock_response = MagicMock()
    mock_response.text = "Not JSON"
    mock_model.generate_content.return_value = mock_response
    
    prs = agent.propose_prs("instruction")
    assert prs == []
