"""
Config Command - Manage DebugAI settings
"""

from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from debugai.ui import get_ui
from debugai.cli.help_theme import show_command_help

console = Console()
ui = get_ui()
app = typer.Typer(name="config", help="Configure DebugAI settings", no_args_is_help=False)


@app.callback(invoke_without_command=True)
def config_callback(
    ctx: typer.Context,
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """Configure DebugAI settings."""
    if help_flag or ctx.invoked_subcommand is None:
        show_command_help(
            command_name="debugai config",
            description="Configure DebugAI settings. Manage API keys, models, and preferences.",
            subcommands=[
                ("set", "Set a configuration value"),
                ("get", "Get a configuration value"),
                ("list", "List all configuration values"),
            ],
            examples=[
                "debugai config set api-key YOUR_API_KEY",
                "debugai config set model gemini-2.0-flash",
                "debugai config get api-key",
                "debugai config list",
            ]
        )
        raise typer.Exit(0)


@app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Configuration key (e.g., api-key, model)"),
    value: str = typer.Argument(..., help="Configuration value"),
) -> None:
    """Set a configuration value."""
    from debugai.config.settings import Settings
    
    primary = ui.theme.primary
    error_color = ui.theme.error
    success_color = ui.theme.success
    
    try:
        settings = Settings()
        settings.set(key, value)
        
        # Mask sensitive values
        display_value = "***" if "key" in key.lower() else value
        console.print(f"[{success_color}]Set {key} = {display_value}[/]")
    
    except Exception as e:
        console.print(f"[{error_color}]Failed: {e}[/]")
        raise typer.Exit(1)


@app.command("get")
def config_get(
    key: str = typer.Argument(..., help="Configuration key to get"),
) -> None:
    """Get a configuration value."""
    from debugai.config.settings import Settings
    
    primary = ui.theme.primary
    text_color = ui.theme.text
    warning_color = ui.theme.warning
    error_color = ui.theme.error
    
    try:
        settings = Settings()
        value = settings.get(key)
        
        if value is None:
            console.print(f"[{warning_color}]Key '{key}' not set[/]")
        else:
            display_value = "***" if "key" in key.lower() else value
            console.print(f"[{primary}]{key}[/] = [{text_color}]{display_value}[/]")
    
    except Exception as e:
        console.print(f"[{error_color}]Failed: {e}[/]")
        raise typer.Exit(1)


@app.command("list")
def config_list() -> None:
    """List all configuration values."""
    from debugai.config.settings import Settings
    
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    error_color = ui.theme.error
    
    try:
        settings = Settings()
        all_config = settings.list_all()
        
        table = Table(show_header=True, header_style=f"bold {primary}")
        table.add_column("Key", style=primary)
        table.add_column("Value", style=text_color)
        table.add_column("Source", style=dim_color)
        
        for item in all_config:
            value = "***" if "key" in item["key"].lower() else item["value"]
            table.add_row(item["key"], str(value), item["source"])
        
        console.print(table)
    
    except Exception as e:
        console.print(f"[{error_color}]Failed: {e}[/]")
        raise typer.Exit(1)


@app.command("reset")
def config_reset(
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
) -> None:
    """Reset all configuration to defaults."""
    from debugai.config.settings import Settings
    
    success_color = ui.theme.success
    warning_color = ui.theme.warning
    
    if not confirm:
        confirm = typer.confirm("Reset all configuration?")
    
    if confirm:
        settings = Settings()
        settings.reset()
        console.print(f"[{success_color}]Configuration reset to defaults[/]")
    else:
        console.print(f"[{warning_color}]Cancelled[/]")
