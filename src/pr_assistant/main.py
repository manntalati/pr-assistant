import typer
from rich.console import Console
from rich.table import Table
from typing import Optional
from dataclasses import dataclass

from pr_assistant.config import ConfigManager
from pr_assistant.rate_limiter import RateLimiter
from pr_assistant.agent import Agent
from pr_assistant.github_client import GitHubClient
from pr_assistant.logger import setup_logging, get_logger

# Setup logger
logger = get_logger(__name__)

@dataclass
class PRContext:
    config: ConfigManager
    console: Console
    verbose: bool = False

app = typer.Typer(help="PR Assistant CLI - Your AI-powered coding companion.")
console = Console()

@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, help="Enable verbose logging"),
):
    """
    PR Assistant CLI entry point.
    """
    setup_logging(verbose)
    ctx.obj = PRContext(
        config=ConfigManager(),
        console=console,
        verbose=verbose
    )

@app.command()
def init(ctx: typer.Context):
    """
    Initialize the PR Assistant configuration.
    """
    ctx.obj.console.print("[bold blue]PR Assistant Initialization[/bold blue]")
    config_manager = ctx.obj.config
    
    # Check if global config exists
    if config_manager.global_config_path.exists():
        if not typer.confirm("Global configuration already exists. Overwrite?"):
            ctx.obj.console.print("Skipping global config update.")
    
    # Global Config (Secrets)
    github_token = typer.prompt("Enter your GitHub Personal Access Token", hide_input=True)
    gemini_key = typer.prompt("Enter your Gemini API Key", hide_input=True)
    
    config_manager.set("github_token", github_token, local=False)
    config_manager.set("gemini_api_key", gemini_key, local=False)
    
    ctx.obj.console.print("[green]Global configuration saved![/green]")

    # Local Config (Project settings)
    if typer.confirm("Do you want to configure this directory as a project? (Saves repo name locally)"):
        repo_name = typer.prompt("Enter the repository name (e.g., owner/repo)")
        config_manager.set("repo_name", repo_name, local=True)
        ctx.obj.console.print(f"[green]Project configuration saved to {config_manager.local_config_path}![/green]")
    else:
        # Fallback to global if they don't want local
        repo_name = typer.prompt("Enter the repository name (e.g., owner/repo) for global default")
        config_manager.set("repo_name", repo_name, local=False)
        ctx.obj.console.print("[green]Global repository default saved![/green]")

@app.command()
def create(
    ctx: typer.Context,
    count: int = typer.Argument(1, help="Number of PRs to create"),
    instruction: str = typer.Option("Improve code quality", help="High-level instruction for the agent")
):
    """
    Create X number of PRs based on agent analysis.
    """
    console = ctx.obj.console
    console.print(f"[bold green]Creating {count} PRs with instruction: '{instruction}'...[/bold green]")
    
    try:
        # Initialize services with config from context
        agent = Agent(ctx.obj.config)
        gh_client = GitHubClient(ctx.obj.config)
        
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
            logger.info(f"Creating branch: {branch}")
            
            try:
                gh_client.create_branch(branch)
            except Exception as e:
                logger.error(f"Failed to create branch {branch}: {e}")
                console.print(f"[red]Failed to create branch {branch}: {e}[/red]")
                continue

            for file_change in files:
                path = file_change.get("path")
                content = file_change.get("content")
                gh_client.create_file(path, f"feat: {title}", content, branch)
            
            url = gh_client.create_pr(title, body, branch)
            console.print(f"[green]PR Created: {url}[/green]")

    except Exception as e:
        logger.exception("Error in create command")
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def list_prs(ctx: typer.Context, state: str = "open"):
    """
    List active PRs with details.
    """
    console = ctx.obj.console
    console.print(f"[bold blue]Listing {state} PRs...[/bold blue]")
    try:
        gh_client = GitHubClient(ctx.obj.config)
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
        logger.exception("Error listing PRs")
        console.print(f"[bold red]Error:[/bold red] {e}")

if __name__ == "__main__":
    app()
