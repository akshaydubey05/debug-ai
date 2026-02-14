"""
Interactive Command - Interactive debugging session
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from debugai.ui import get_ui
from debugai.cli.help_theme import show_command_help

console = Console()
ui = get_ui()
app = typer.Typer(name="interactive", help="Interactive debugging session", no_args_is_help=False)


@app.callback(invoke_without_command=True)
def interactive_callback(
    ctx: typer.Context,
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """Interactive debugging session."""
    if help_flag or ctx.invoked_subcommand is None:
        show_command_help(
            command_name="debugai interactive",
            description="Start an interactive debugging session. Chat with AI to analyze logs and debug issues in real-time.",
            subcommands=[
                ("start", "Start an interactive debugging session"),
            ],
            examples=[
                "debugai interactive start",
            ]
        )
        raise typer.Exit(0)


@app.command("start")
def start_session() -> None:
    """Start an interactive debugging session."""
    from debugai.core.engine import DebugEngine
    from debugai.ai.gemini_client import GeminiClient
    
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    error_color = ui.theme.error
    warning_color = ui.theme.warning
    success_color = ui.theme.success
    
    console.print(Panel.fit(
        f"[bold {primary}]Interactive Debug Session[/]\n\n"
        f"[{text_color}]Commands:[/]\n"
        f"  [{primary}]analyze <path>[/] - Analyze log file\n"
        f"  [{primary}]explain <text>[/] - Explain an error\n"
        f"  [{primary}]suggest <text>[/] - Get fix suggestions\n"
        f"  [{primary}]history[/]        - Show session history\n"
        f"  [{primary}]clear[/]          - Clear screen\n"
        f"  [{primary}]exit[/]           - Exit session\n",
        border_style=border
    ))
    
    engine = DebugEngine()
    ai = GeminiClient()
    history = []
    
    while True:
        try:
            command = Prompt.ask(f"\n[bold {primary}]debugai>[/]")
            
            if not command.strip():
                continue
            
            parts = command.strip().split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            if cmd == "exit" or cmd == "quit":
                console.print(f"[{warning_color}]Goodbye![/]")
                break
            
            elif cmd == "clear":
                console.clear()
            
            elif cmd == "history":
                if history:
                    for i, h in enumerate(history[-10:], 1):
                        console.print(f"  [{text_color}]{i}. {h}[/]")
                else:
                    console.print(f"[{dim_color}]No history yet[/]")
            
            elif cmd == "analyze":
                if not args:
                    console.print(f"[{error_color}]Usage: analyze <path>[/]")
                else:
                    with console.status(f"[{primary}]Analyzing..."):
                        # Quick analysis
                        result = engine.quick_analyze(args)
                    console.print(f"[{text_color}]Found {result['error_count']} errors[/]")
            
            elif cmd == "explain":
                if not args:
                    console.print(f"[{error_color}]Usage: explain <error text>[/]")
                else:
                    with console.status(f"[{primary}]Explaining..."):
                        explanation = ai.explain_text(args)
                    console.print(Panel(explanation, title=f"[{primary}]Explanation[/]", border_style=border))
            
            elif cmd == "suggest":
                if not args:
                    console.print(f"[{error_color}]Usage: suggest <error text>[/]")
                else:
                    with console.status(f"[{primary}]Generating suggestions..."):
                        suggestions = ai.suggest_for_text(args)
                    for s in suggestions:
                        console.print(f"[bold {text_color}]{s['title']}[/]: [{text_color}]{s['description']}[/]")
            
            else:
                console.print(f"[{error_color}]Unknown command: {cmd}[/]")
            
            history.append(command)
        
        except KeyboardInterrupt:
            console.print(f"\n[{warning_color}]Use 'exit' to quit[/]")
        except Exception as e:
            console.print(f"[{error_color}]Error: {e}[/]")
