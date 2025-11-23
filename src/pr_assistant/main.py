import typer
from rich.console import Console
from rich.table import Table
from pr_assistant.config import ConfigManager
from pr_assistant.rate_limiter import RateLimiter
from pr_assistant.agent import Agent
from pr_assistant.github_client import GitHubClient

app = typer.Typer(help="PR Assistant CLI - Your AI-powered coding companion.")
console = Console()

@app.command()
def init():
    """
    Initialize the PR Assistant configuration.
    """
    console.print("[bold blue]PR Assistant Initialization[/bold blue]")
    
    config_manager = ConfigManager()
    if config_manager.exists():
        overwrite = typer.confirm("Configuration already exists. Overwrite?")
        if not overwrite:
            console.print("Aborted.")
            return

    github_token = typer.prompt("Enter your GitHub Personal Access Token", hide_input=True)
    repo_name = typer.prompt("Enter the repository name (e.g., owner/repo)")
    gemini_key = typer.prompt("Enter your Gemini API Key", hide_input=True)

    config = {
        "github_token": github_token,
        "repo_name": repo_name,
        "gemini_api_key": gemini_key
    }
    config_manager.save(config)
    console.print("[green]Configuration saved successfully![/green]")

@app.command()
def create(
    count: int = typer.Argument(1, help="Number of PRs to create"),
    instruction: str = typer.Option("Improve code quality", help="High-level instruction for the agent")
):
    """
    Create X number of PRs based on agent analysis.
    """
    console.print(f"[bold green]Creating {count} PRs with instruction: '{instruction}'...[/bold green]")
    
    try:
        agent = Agent()
        gh_client = GitHubClient()
        
        prs = agent.propose_prs(instruction, count)
        
        if not prs:
            console.print("[yellow]No PRs proposed by the agent.[/yellow]")
            return

        for pr_data in prs:
            title = pr_data.get("title")
            body = pr_data.get("body")
            branch = pr_data.get("branch")
            files = pr_data.get("files", [])

            console.print(f"Preparing PR: [bold]{title}[/bold]")
            
            # Create branch
            try:
                gh_client.create_branch(branch)
            except Exception as e:
                console.print(f"[red]Failed to create branch {branch}: {e}[/red]")
                continue

            # Create/Update files
            for file_change in files:
                path = file_change.get("path")
                content = file_change.get("content")
                gh_client.create_file(path, f"feat: {title}", content, branch)
            
            # Open PR
            url = gh_client.create_pr(title, body, branch)
            console.print(f"[green]PR Created: {url}[/green]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def list_prs(state: str = "open"):
    """
    List active PRs with details.
    """
    console.print(f"[bold blue]Listing {state} PRs...[/bold blue]")
    try:
        gh_client = GitHubClient()
        prs = gh_client.list_prs(state)
        
        table = Table(title="Active Pull Requests")
        table.add_column("Number", style="cyan")
        table.add_column("Title", style="magenta")
        table.add_column("Author", style="green")
        table.add_column("URL", style="blue")

        for pr in prs:
            table.add_row(str(pr["number"]), pr["title"], pr["user"], pr["url"])
        
        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
