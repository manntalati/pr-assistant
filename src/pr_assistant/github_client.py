from github import Github, Auth
from typing import List, Optional
from pr_assistant.config import ConfigManager

class GitHubClient:
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config = config_manager or ConfigManager()
        self.token = self.config.get("bot_github_token") or self.config.get("github_token")
        if not self.token:
            raise ValueError("GitHub token not found. Run 'pr-assistant init' first.")
        
        auth = Auth.Token(self.token)
        self.gh = Github(auth=auth)
        self.repo_name = self.config.get("repo_name")
        if not self.repo_name:
             raise ValueError("Repository name not configured. Run 'pr-assistant init' first.")
        
        self.repo = self.gh.get_repo(self.repo_name)

    def create_pr(self, title: str, body: str, head: str, base: str = "main") -> str:
        """Creates a PR and returns the HTML URL."""
        pr = self.repo.create_pull(title=title, body=body, head=head, base=base)
        return pr.html_url

    def list_prs(self, state: str = "open") -> List[dict]:
        """Lists PRs and returns a simplified list of dicts."""
        prs = self.repo.get_pulls(state=state)
        return [
            {
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
                "user": pr.user.login,
                "created_at": pr.created_at.isoformat()
            }
            for pr in prs
        ]

    def create_branch(self, branch_name: str, source_branch: str = "main"):
        """Creates a new branch from the source branch."""
        source = self.repo.get_branch(source_branch)
        self.repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=source.commit.sha)

    def create_file(self, path: str, message: str, content: str, branch: str):
        """Creates or updates a file in the repository."""
        try:
            contents = self.repo.get_contents(path, ref=branch)
            self.repo.update_file(contents.path, message, content, contents.sha, branch=branch)
        except:
            self.repo.create_file(path, message, content, branch=branch)

    def get_pr_details(self, pr_number: int) -> dict:
        """Fetches PR title and body."""
        pr = self.repo.get_pull(pr_number)
        return {
            "title": pr.title,
            "body": pr.body,
            "url": pr.html_url,
            "user": pr.user.login
        }

    def get_pr_diff(self, pr_number: int) -> str:
        """Fetches the diff of the PR."""
        pr = self.repo.get_pull(pr_number)
        files_data = []
        for file in pr.get_files():
            files_data.append(f"File: {file.filename}\nStatus: {file.status}\nChanges: +{file.additions} -{file.deletions}\n\nPatch:\n{file.patch}")
        
        return "\n\n---\n\n".join(files_data)

    def post_comment(self, pr_number: int, body: str):
        """Posts a comment on the PR."""
        pr = self.repo.get_pull(pr_number)
        pr.create_issue_comment(body)
