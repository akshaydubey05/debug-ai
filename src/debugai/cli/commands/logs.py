"""
Logs Command - Manage log sources
"""

from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from debugai.ui import get_ui
from debugai.cli.help_theme import show_command_help

console = Console()
ui = get_ui()
app = typer.Typer(name="logs", help="Manage log sources", no_args_is_help=False)


@app.callback(invoke_without_command=True)
def logs_callback(
    ctx: typer.Context,
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """Manage log sources for DebugAI analysis."""
    if help_flag or ctx.invoked_subcommand is None:
        show_command_help(
            command_name="debugai logs",
            description="Manage log sources for DebugAI analysis. Add, remove, list, and watch log sources for real-time monitoring.",
            subcommands=[
                ("add", "Add a new log source (file or directory)"),
                ("list", "List all configured log sources"),
                ("remove", "Remove a log source by name"),
                ("watch", "Watch log sources for new entries in real-time"),
            ],
            examples=[
                "debugai logs add ./logs --name app-logs",
                "debugai logs list",
                "debugai logs remove app-logs",
                "debugai logs watch",
            ]
        )
        raise typer.Exit(0)


@app.command("add")
def add_source(
    path: Path = typer.Argument(..., help="Path to log file or directory"),
    name: str = typer.Option(None, "--name", "-n", help="Name for this source"),
    pattern: str = typer.Option("*.log", "--pattern", "-p", help="File pattern"),
    service: str = typer.Option(None, "--service", "-s", help="Service name"),
) -> None:
    """Add a log source."""
    from debugai.storage.database import Database
    
    primary = ui.theme.primary
    text_color = ui.theme.text
    success_color = ui.theme.success
    error_color = ui.theme.error
    
    try:
        db = Database()
        source_name = name or path.name
        
        db.add_log_source(
            name=source_name,
            path=str(path.absolute()),
            pattern=pattern,
            service=service
        )
        
        console.print(f"[{success_color}]Added log source: {source_name}[/]")
        console.print(f"   [{text_color}]Path: {path.absolute()}[/]")
    
    except Exception as e:
        console.print(f"[{error_color}]Failed: {e}[/]")
        raise typer.Exit(1)


@app.command("list")
def list_sources() -> None:
    """List all log sources."""
    from debugai.storage.database import Database
    
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    warning_color = ui.theme.warning
    error_color = ui.theme.error
    
    try:
        db = Database()
        sources = db.get_log_sources()
        
        if not sources:
            console.print(f"[{warning_color}]No log sources configured[/]")
            console.print(f"[{dim_color}]Use 'debugai logs add ./path' to add one[/]")
            return
        
        table = Table(show_header=True, header_style=f"bold {primary}")
        table.add_column("Name", style=primary)
        table.add_column("Path", style=text_color)
        table.add_column("Pattern", style=dim_color)
        table.add_column("Service", style=text_color)
        
        for source in sources:
            table.add_row(
                source["name"],
                source["path"],
                source["pattern"],
                source.get("service", "-")
            )
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[{error_color}]Failed: {e}[/]")
        raise typer.Exit(1)


@app.command("remove")
def remove_source(
    name: str = typer.Argument(..., help="Name of source to remove"),
) -> None:
    """Remove a log source."""
    from debugai.storage.database import Database
    
    success_color = ui.theme.success
    error_color = ui.theme.error
    
    try:
        db = Database()
        db.remove_log_source(name)
        console.print(f"[{success_color}]Removed: {name}[/]")
    
    except Exception as e:
        console.print(f"[{error_color}]Failed: {e}[/]")
        raise typer.Exit(1)


@app.command("watch")
def watch_sources(
    name: Optional[str] = typer.Argument(None, help="Source name to watch (all if omitted)"),
) -> None:
    """Watch log sources for new entries."""
    primary = ui.theme.primary
    text_color = ui.theme.text
    warning_color = ui.theme.warning
    error_color = ui.theme.error
    
    console.print(f"[{primary}]Watching logs... (Ctrl+C to stop)[/]\n")
    
    try:
        from debugai.ingestion.stream_ingester import StreamIngester
        
        ingester = StreamIngester()
        for entry in ingester.watch(name):
            level = entry.get("level", "info")
            if level == "error":
                level_color = error_color
            elif level == "warn":
                level_color = warning_color
            else:
                level_color = text_color
            console.print(f"[{level_color}]{entry['message']}[/]")
    
    except KeyboardInterrupt:
        console.print(f"\n[{warning_color}]Stopped watching[/]")
