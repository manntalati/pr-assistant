import pytest
from unittest.mock import MagicMock, patch
from pr_assistant.github_client import GitHubClient

@pytest.fixture
def mock_github(monkeypatch):
    mock_gh = MagicMock()
    mock_auth = MagicMock()
    
    monkeypatch.setattr("pr_assistant.github_client.Github", mock_gh)
    monkeypatch.setattr("pr_assistant.github_client.Auth.Token", mock_auth)
    
    return mock_gh

@pytest.fixture
def mock_config(monkeypatch):
    mock_conf = MagicMock()
    mock_conf.get.side_effect = lambda k: "dummy_token" if k == "github_token" else "owner/repo"
    monkeypatch.setattr("pr_assistant.github_client.ConfigManager", lambda: mock_conf)
    return mock_conf

def test_github_client_init(mock_github, mock_config):
    client = GitHubClient()
    mock_github.assert_called_once()
    mock_github.return_value.get_repo.assert_called_with("owner/repo")

def test_create_pr(mock_github, mock_config):
    client = GitHubClient()
    repo = mock_github.return_value.get_repo.return_value
    repo.create_pull.return_value.html_url = "http://github.com/pr/1"
    
    url = client.create_pr("Title", "Body", "feature-branch")
    
    repo.create_pull.assert_called_with(
        title="Title", body="Body", head="feature-branch", base="main"
    )
    assert url == "http://github.com/pr/1"

def test_create_branch(mock_github, mock_config):
    client = GitHubClient()
    repo = mock_github.return_value.get_repo.return_value
    repo.get_branch.return_value.commit.sha = "sha123"
    
    client.create_branch("new-branch")
    
    repo.get_branch.assert_called_with("main")
    repo.create_git_ref.assert_called_with(ref="refs/heads/new-branch", sha="sha123")

def test_create_file_new(mock_github, mock_config):
    client = GitHubClient()
    repo = mock_github.return_value.get_repo.return_value
    # Simulate file not found (create new)
    repo.get_contents.side_effect = Exception("Not found")
    
    client.create_file("path/file.txt", "msg", "content", "branch")
    
    repo.create_file.assert_called_with("path/file.txt", "msg", "content", branch="branch")

def test_create_file_update(mock_github, mock_config):
    client = GitHubClient()
    repo = mock_github.return_value.get_repo.return_value
    # Simulate file found (update)
    repo.get_contents.return_value.sha = "old_sha"
    repo.get_contents.return_value.path = "path/file.txt"
    
    client.create_file("path/file.txt", "msg", "content", "branch")
    
    repo.update_file.assert_called_with("path/file.txt", "msg", "content", "old_sha", branch="branch")
