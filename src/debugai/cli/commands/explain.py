"""
Explain Command - Get plain English explanations for errors
"""

from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import box

from debugai.ui import get_ui
from debugai.cli.help_theme import show_command_help

console = Console()
ui = get_ui()
app = typer.Typer(name="explain", help="Explain errors in plain English", no_args_is_help=False)


@app.callback(invoke_without_command=True)
def explain_callback(
    ctx: typer.Context,
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """Explain errors in plain English with AI assistance."""
    if help_flag or ctx.invoked_subcommand is None:
        show_command_help(
            command_name="debugai explain",
            description="Get plain English explanations for errors using AI. Understand what went wrong and why it happened.",
            subcommands=[
                ("error", "Explain a specific error by ID or hash"),
                ("trace", "Explain a full stack trace"),
                ("message", "Explain any error message directly"),
            ],
            examples=[
                "debugai explain error err_12345",
                "debugai explain error err_12345 --verbose",
                "debugai explain trace ./stacktrace.txt",
                'debugai explain message "NullPointerException"',
            ]
        )
        raise typer.Exit(0)


@app.command("error")
def explain_error(
    error_id: str = typer.Argument(..., help="Error ID or hash to explain"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed explanation"),
    show_code: bool = typer.Option(True, "--code/--no-code", help="Show relevant code"),
) -> None:
    """Explain a specific error in plain English."""
    from debugai.core.engine import DebugEngine
    from debugai.ai.gemini_client import GeminiClient
    
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    error_color = ui.theme.error
    warning_color = ui.theme.warning
    success_color = ui.theme.success
    
    console.print(f"\n[{primary}]Looking up error: {error_id}[/]\n")
    
    try:
        engine = DebugEngine()
        ai = GeminiClient()
        
        error = engine.get_error_by_id(error_id)
        if not error:
            console.print(f"[{error_color}]Error not found: {error_id}[/]")
            raise typer.Exit(1)
        
        with console.status(f"[bold {primary}]Generating explanation..."):
            explanation = ai.explain_error(error, verbose=verbose)
        
        console.print(Panel(
            Markdown(explanation["summary"]),
            title=f"[{primary}]What Happened[/]",
            border_style=border
        ))
        
        if verbose and explanation.get("technical_details"):
            console.print(Panel(
                explanation["technical_details"],
                title=f"[{primary}]Technical Details[/]",
                border_style=border
            ))
        
        if explanation.get("similar_issues"):
            console.print(f"\n[bold {text_color}]Similar Issues:[/]")
            for issue in explanation["similar_issues"][:3]:
                console.print(f"  - [{text_color}]{issue['title']}[/] - [{dim_color}]{issue['url']}[/]")
    
    except Exception as e:
        console.print(f"[{error_color}]Failed to explain error: {e}[/]")
        raise typer.Exit(1)


@app.command("text")
def explain_text(
    error_text: str = typer.Argument(..., help="Error message or stack trace to explain"),
) -> None:
    """Explain any error text directly."""
    from debugai.ai.gemini_client import GeminiClient
    
    primary = ui.theme.primary
    border = ui.theme.border
    error_color = ui.theme.error
    
    console.print(f"\n[{primary}]Analyzing error text...[/]\n")
    
    try:
        ai = GeminiClient()
        
        with console.status(f"[bold {primary}]Generating explanation..."):
            explanation = ai.explain_text(error_text)
        
        console.print(Panel(
            Markdown(explanation),
            title=f"[{primary}]Explanation[/]",
            border_style=border
        ))
    
    except Exception as e:
        console.print(f"[{error_color}]Failed to explain: {e}[/]")
        raise typer.Exit(1)
