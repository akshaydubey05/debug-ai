"""
Timeline Command - Generate event timeline
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
app = typer.Typer(name="timeline", help="Generate event timeline", no_args_is_help=False)


@app.callback(invoke_without_command=True)
def timeline_callback(
    ctx: typer.Context,
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """Generate and display event timelines."""
    if help_flag or ctx.invoked_subcommand is None:
        show_command_help(
            command_name="debugai timeline",
            description="Generate and display event timelines. Visualize log events chronologically to understand incident flow.",
            subcommands=[
                ("show", "Show timeline of events with filtering options"),
            ],
            examples=[
                "debugai timeline show",
                "debugai timeline show --last 1h",
                "debugai timeline show --filter errors",
                "debugai timeline show --service api --limit 100",
            ]
        )
        raise typer.Exit(0)


@app.command("show")
def show_timeline(
    last: str = typer.Option("5m", "--last", "-l", help="Time range (e.g., 5m, 1h, 1d)"),
    filter_level: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter: errors, warnings, all"),
    service: Optional[str] = typer.Option(None, "--service", "-s", help="Filter by service"),
    limit: int = typer.Option(50, "--limit", "-n", help="Max events to show"),
) -> None:
    """Show timeline of events."""
    from debugai.core.engine import DebugEngine
    from debugai.analysis.timeline_builder import TimelineBuilder
    
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    error_color = ui.theme.error
    warning_color = ui.theme.warning
    
    console.print(f"\n[{primary}]Timeline (last {last})[/]\n")
    
    try:
        engine = DebugEngine()
        builder = TimelineBuilder()
        
        with console.status(f"[bold {primary}]Building timeline..."):
            events = builder.build(
                time_range=last,
                filter_level=filter_level,
                service=service,
                limit=limit
            )
        
        if not events:
            console.print(f"[{warning_color}]No events found in the specified range[/]")
            return
        
        table = Table(show_header=True, header_style=f"bold {primary}")
        table.add_column("Time", style=primary, width=20)
        table.add_column("Level", width=8)
        table.add_column("Service", style=text_color, width=15)
        table.add_column("Event", style=text_color)
        
        for event in events:
            level = event["level"]
            if level == "error":
                level_color = error_color
            elif level == "warn":
                level_color = warning_color
            else:
                level_color = dim_color
            table.add_row(
                event["timestamp"],
                f"[{level_color}]{level.upper()}[/]",
                event.get("service", "-"),
                event["message"][:60] + ("..." if len(event["message"]) > 60 else "")
            )
        
        console.print(table)
        console.print(f"\n[{dim_color}]Showing {len(events)} events[/]")
    
    except Exception as e:
        console.print(f"[{error_color}]Failed: {e}[/]")
        raise typer.Exit(1)


@app.command("crash")
def crash_timeline(
    error_id: str = typer.Argument(..., help="Error ID to trace"),
    before: str = typer.Option("5m", "--before", "-b", help="Time before crash to show"),
) -> None:
    """Show events leading to a crash."""
    from debugai.core.engine import DebugEngine
    from debugai.analysis.timeline_builder import TimelineBuilder
    
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    error_color = ui.theme.error
    warning_color = ui.theme.warning
    
    console.print(f"\n[{primary}]Crash Timeline for: {error_id}[/]\n")
    
    try:
        engine = DebugEngine()
        builder = TimelineBuilder()
        
        error = engine.get_error_by_id(error_id)
        if not error:
            console.print(f"[{error_color}]Error not found: {error_id}[/]")
            raise typer.Exit(1)
        
        with console.status(f"[bold {primary}]Tracing events..."):
            events = builder.trace_crash(error, before=before)
        
        console.print(Panel(
            f"[bold {error_color}]CRASH[/]: [{text_color}]{error['message']}[/]\n"
            f"[{dim_color}]Time: {error['timestamp']} | Service: {error.get('service', 'Unknown')}[/]",
            border_style=border
        ))
        
        console.print(f"\n[bold {text_color}]Events leading to crash:[/]\n")
        
        for i, event in enumerate(events):
            prefix = "├──" if i < len(events) - 1 else "└──"
            level = event["level"]
            if level == "error":
                level_color = error_color
            elif level == "warn":
                level_color = warning_color
            else:
                level_color = dim_color
            console.print(f"  {prefix} [{level_color}]{event['timestamp']}[/] [{text_color}]{event['message']}[/]")
    
    except Exception as e:
        console.print(f"[{error_color}]Failed: {e}[/]")
        raise typer.Exit(1)
