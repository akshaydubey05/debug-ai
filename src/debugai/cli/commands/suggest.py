"""
Suggest-Fix Command - AI-powered fix suggestions
"""

from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box

from debugai.ui import get_ui
from debugai.cli.help_theme import show_command_help

console = Console()
ui = get_ui()
app = typer.Typer(name="suggest-fix", help="Get AI-powered fix suggestions", no_args_is_help=False)


@app.callback(invoke_without_command=True)
def suggest_callback(
    ctx: typer.Context,
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """Get AI-powered fix suggestions for errors."""
    if help_flag or ctx.invoked_subcommand is None:
        show_command_help(
            command_name="debugai suggest-fix",
            description="Get AI-powered fix suggestions for errors and issues. Receive actionable code fixes with confidence scores.",
            subcommands=[
                ("error", "Get fix suggestions for a specific error"),
                ("message", "Get suggestions for any error message"),
                ("pattern", "Get suggestions for recurring error patterns"),
            ],
            examples=[
                "debugai suggest-fix error err_12345",
                "debugai suggest-fix error err_12345 --max 5",
                'debugai suggest-fix message "OutOfMemoryError"',
                "debugai suggest-fix pattern null_pointer",
            ]
        )
        raise typer.Exit(0)


@app.command("error")
def suggest_for_error(
    error_id: str = typer.Argument(..., help="Error ID to get suggestions for"),
    max_suggestions: int = typer.Option(3, "--max", "-m", help="Maximum suggestions"),
) -> None:
    """Get fix suggestions for a specific error."""
    from debugai.core.engine import DebugEngine
    from debugai.ai.gemini_client import GeminiClient
    
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    error_color = ui.theme.error
    success_color = ui.theme.success
    
    console.print(f"\n[{primary}]Getting suggestions for: {error_id}[/]\n")
    
    try:
        engine = DebugEngine()
        ai = GeminiClient()
        
        error = engine.get_error_by_id(error_id)
        if not error:
            console.print(f"[{error_color}]Error not found: {error_id}[/]")
            raise typer.Exit(1)
        
        with console.status(f"[bold {primary}]Generating suggestions..."):
            suggestions = ai.suggest_fixes(error, max_suggestions=max_suggestions)
        
        for i, suggestion in enumerate(suggestions, 1):
            console.print(Panel(
                f"[bold {text_color}]{suggestion['title']}[/]\n\n"
                f"[{text_color}]{suggestion['description']}[/]\n\n"
                f"[{dim_color}]Confidence: {suggestion['confidence']}%[/]",
                title=f"[{primary}]Suggestion #{i}[/]",
                border_style=border
            ))
            
            if suggestion.get("code"):
                console.print(Syntax(
                    suggestion["code"],
                    suggestion.get("language", "python"),
                    theme="monokai",
                    line_numbers=True
                ))
            console.print()
    
    except Exception as e:
        console.print(f"[{error_color}]Failed: {e}[/]")
        raise typer.Exit(1)


@app.command("text")
def suggest_for_text(
    error_text: str = typer.Argument(..., help="Error message to get suggestions for"),
    language: str = typer.Option("python", "--lang", "-l", help="Programming language"),
) -> None:
    """Get fix suggestions for any error text."""
    from debugai.ai.gemini_client import GeminiClient
    
    primary = ui.theme.primary
    text_color = ui.theme.text
    border = ui.theme.border
    error_color = ui.theme.error
    
    console.print(f"\n[{primary}]Analyzing: {error_text[:50]}...[/]\n")
    
    try:
        ai = GeminiClient()
        
        with console.status(f"[bold {primary}]Generating suggestions..."):
            suggestions = ai.suggest_for_text(error_text, language=language)
        
        for i, suggestion in enumerate(suggestions, 1):
            console.print(Panel(
                f"[bold {text_color}]{suggestion['title']}[/]\n\n[{text_color}]{suggestion['description']}[/]",
                title=f"[{primary}]Suggestion #{i}[/]",
                border_style=border
            ))
            
            if suggestion.get("code"):
                console.print(Syntax(
                    suggestion["code"], language, theme="monokai", line_numbers=True
                ))
            console.print()
    
    except Exception as e:
        console.print(f"[{error_color}]Failed: {e}[/]")
        raise typer.Exit(1)
