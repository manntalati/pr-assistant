import pytest
from typer.testing import CliRunner
from unittest.mock import MagicMock
from pr_assistant.main import app

runner = CliRunner()

@pytest.fixture
def mock_deps(monkeypatch):
    # Mock everything main.py uses
    mock_conf = MagicMock()
    mock_conf.exists.return_value = False
    monkeypatch.setattr("pr_assistant.main.ConfigManager", lambda: mock_conf)
    
    mock_agent = MagicMock()
    monkeypatch.setattr("pr_assistant.main.Agent", lambda *args: mock_agent)
    
    mock_gh = MagicMock()
    monkeypatch.setattr("pr_assistant.main.GitHubClient", lambda *args: mock_gh)
    
    return mock_conf, mock_agent, mock_gh

def test_init_command(mock_deps):
    mock_conf, _, _ = mock_deps
    mock_conf.global_config_path.exists.return_value = False

    inputs = "token\n\nkey\ny\nowner/repo\n"
    result = runner.invoke(app, ["init"], input=inputs)
    
    assert result.exit_code == 0
    assert "Global configuration saved!" in result.stdout
    assert "Project configuration saved" in result.stdout

    assert mock_conf.set.call_count >= 3

def test_create_command(mock_deps):
    _, mock_agent, mock_gh = mock_deps
    
    # Mock agent returning PRs
    mock_agent.propose_prs.return_value = [{
        "title": "Test PR",
        "body": "Body",
        "branch": "branch",
        "files": [{"path": "f.py", "content": "c"}]
    }]
    
    mock_gh.create_pr.return_value = "http://url"
    
    result = runner.invoke(app, ["create", "1"])
    
    assert result.exit_code == 0
    assert "PR Created: http://url" in result.stdout
    mock_agent.propose_prs.assert_called_with("Improve code quality", 1)
    mock_gh.create_branch.assert_called()
    mock_gh.create_file.assert_called()
    mock_gh.create_pr.assert_called()

def test_list_prs_command(mock_deps):
    _, _, mock_gh = mock_deps
    
    mock_gh.list_prs.return_value = [
        {"number": 1, "title": "PR 1", "user": "user", "url": "url"}
    ]
    
    result = runner.invoke(app, ["list-prs"])
    
    assert result.exit_code == 0
    assert "PR 1" in result.stdout
    assert "Listing open PRs" in result.stdout

def test_review_pr_command(mock_deps):
    _, mock_agent, mock_gh = mock_deps
    
    mock_gh.get_pr_details.return_value = {"title": "Test PR", "body": "Description"}
    mock_gh.get_pr_diff.return_value = "diff content"
    
    mock_agent.review_pr.return_value = "LGTM"
    
    result = runner.invoke(app, ["review-pr", "123"])
    
    assert result.exit_code == 0
    assert "Reviewing PR #123" in result.stdout
    assert "Review Generated!" in result.stdout
    assert "LGTM" in result.stdout
    assert "Review posted successfully" in result.stdout
    
    mock_gh.get_pr_details.assert_called_with(123)
    mock_gh.get_pr_diff.assert_called_with(123)
    mock_agent.review_pr.assert_called()
    mock_gh.post_comment.assert_called()
