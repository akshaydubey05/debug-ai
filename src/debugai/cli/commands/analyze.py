"""
Analyze Command - Core log analysis functionality

Commands:
  debugai analyze ./logs --service api,db,redis
  debugai analyze --docker container_name
  debugai analyze --stdin
"""

from pathlib import Path
from typing import Optional, List
from enum import Enum

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.syntax import Syntax
from rich import box

from debugai.ui import get_ui
from debugai.cli.help_theme import show_command_help

console = Console()
ui = get_ui()

app = typer.Typer(
    name="analyze",
    help="Analyze logs from multiple sources with AI-powered insights",
    no_args_is_help=False,
)


@app.callback(invoke_without_command=True)
def analyze_callback(
    ctx: typer.Context,
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """Analyze logs from multiple sources with AI-powered insights."""
    if help_flag or ctx.invoked_subcommand is None:
        show_command_help(
            command_name="debugai analyze",
            description="Analyze logs from multiple sources with AI-powered insights. Supports file paths, Docker containers, Kubernetes pods, and stdin.",
            subcommands=[
                ("path", "Analyze logs from file or directory"),
                ("docker", "Analyze Docker container logs"),
                ("k8s", "Analyze Kubernetes pod logs"),
                ("stdin", "Analyze logs from standard input"),
            ],
            examples=[
                "debugai analyze path ./logs",
                "debugai analyze path ./logs --service api,db",
                "debugai analyze docker my-container",
                "cat app.log | debugai analyze stdin",
            ]
        )
        raise typer.Exit(0)


class OutputFormat(str, Enum):
    """Output format options"""
    RICH = "rich"
    JSON = "json"
    MARKDOWN = "markdown"
    PLAIN = "plain"


class LogSource(str, Enum):
    """Log source types"""
    FILE = "file"
    DOCKER = "docker"
    KUBERNETES = "kubernetes"
    STDIN = "stdin"
    JOURNALD = "journald"


@app.command("path")
def analyze_path(
    paths: List[Path] = typer.Argument(
        ...,
        help="Path(s) to log files or directories",
        exists=True,
    ),
    service: Optional[str] = typer.Option(
        None,
        "--service", "-s",
        help="Filter by service names (comma-separated: api,db,redis)",
    ),
    level: Optional[str] = typer.Option(
        None,
        "--level", "-l",
        help="Filter by log level (error,warn,info,debug)",
    ),
    since: Optional[str] = typer.Option(
        None,
        "--since",
        help="Analyze logs since time (e.g., '1h', '30m', '2024-01-01')",
    ),
    until: Optional[str] = typer.Option(
        None,
        "--until",
        help="Analyze logs until time",
    ),
    pattern: Optional[str] = typer.Option(
        None,
        "--pattern", "-p",
        help="Custom regex pattern to match",
    ),
    correlate: bool = typer.Option(
        True,
        "--correlate/--no-correlate",
        help="Enable cross-service error correlation",
    ),
    ai_analysis: bool = typer.Option(
        True,
        "--ai/--no-ai",
        help="Enable AI-powered analysis",
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.RICH,
        "--format", "-f",
        help="Output format",
    ),
    max_errors: int = typer.Option(
        50,
        "--max-errors",
        help="Maximum number of errors to analyze in detail",
    ),
    save_report: Optional[Path] = typer.Option(
        None,
        "--save", "-o",
        help="Save analysis report to file",
    ),
) -> None:
    """
    Analyze log files or directories.
    
    Examples:
        debugai analyze path ./logs
        debugai analyze path ./logs --service api,db
        debugai analyze path ./app.log ./error.log --level error
        debugai analyze path ./logs --since 1h --correlate
    """
    from debugai.core.engine import DebugEngine
    from debugai.ingestion.file_ingester import FileIngester
    from debugai.analysis.correlator import ErrorCorrelator
    
    # Get theme colors
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    
    console.print(Panel.fit(
        f"[bold {primary}]DebugAI Log Analysis[/bold {primary}]",
        border_style=border
    ))
    
    # Parse service filter
    services = service.split(",") if service else None
    levels = level.split(",") if level else None
    
    # Show configuration
    config_table = Table(show_header=False, box=None, padding=(0, 2))
    config_table.add_column("Key", style=primary)
    config_table.add_column("Value", style=text_color)
    
    config_table.add_row("Paths", ", ".join(str(p) for p in paths))
    if services:
        config_table.add_row("Services", ", ".join(services))
    if levels:
        config_table.add_row("Levels", ", ".join(levels))
    if since:
        config_table.add_row("Since", since)
    config_table.add_row("AI Analysis", "Enabled" if ai_analysis else "Disabled")
    config_table.add_row("Correlation", "Enabled" if correlate else "Disabled")
    
    console.print(config_table)
    console.print()
    
    # Run analysis with progress
    with Progress(
        SpinnerColumn(style=primary),
        TextColumn(f"[{text_color}]" + "{task.description}" + f"[/{text_color}]"),
        BarColumn(complete_style=primary, finished_style=primary),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        # Step 1: Ingest logs
        ingest_task = progress.add_task(f"[{primary}]Ingesting logs...", total=100)
        
        try:
            engine = DebugEngine()
            ingester = FileIngester()
            
            # Ingest all paths
            all_logs = []
            for path in paths:
                logs = ingester.ingest(
                    path=path,
                    services=services,
                    levels=levels,
                    since=since,
                    until=until,
                )
                all_logs.extend(logs)
            
            progress.update(ingest_task, completed=100)
            
            # Step 2: Parse and structure
            parse_task = progress.add_task(f"[{primary}]Parsing log entries...", total=100)
            parsed_logs = engine.parse_logs(all_logs)
            progress.update(parse_task, completed=100)
            
            # Step 3: Identify errors
            error_task = progress.add_task(f"[{primary}]Identifying errors...", total=100)
            errors = engine.identify_errors(parsed_logs)
            progress.update(error_task, completed=100)
            
            # Step 4: Correlate errors (if enabled)
            if correlate and len(errors) > 0:
                correlate_task = progress.add_task(f"[{primary}]Correlating errors across services...", total=100)
                correlator = ErrorCorrelator()
                correlated = correlator.correlate(errors)
                progress.update(correlate_task, completed=100)
            else:
                correlated = errors
            
            # Step 5: AI Analysis (if enabled)
            if ai_analysis and len(correlated) > 0:
                ai_task = progress.add_task(f"[{primary}]Running AI analysis...", total=100)
                analysis_results = engine.ai_analyze(
                    errors=correlated[:max_errors],
                    context=parsed_logs,
                )
                progress.update(ai_task, completed=100)
            else:
                analysis_results = None
        
        except Exception as e:
            console.print(f"\n[{ui.theme.error}]Analysis failed: {e}[/]")
            raise typer.Exit(1)
    
    # Display results
    console.print()
    _display_analysis_results(
        parsed_logs=parsed_logs,
        errors=correlated,
        analysis=analysis_results,
        output_format=output_format,
    )
    
    # Save report if requested
    if save_report:
        _save_report(save_report, parsed_logs, correlated, analysis_results)
        console.print(f"\n[{ui.theme.success}]Report saved to {save_report}[/]")


@app.command("docker")
def analyze_docker(
    containers: List[str] = typer.Argument(
        ...,
        help="Docker container names or IDs",
    ),
    follow: bool = typer.Option(
        False,
        "--follow", "-f",
        help="Follow log output (live analysis)",
    ),
    tail: int = typer.Option(
        1000,
        "--tail", "-n",
        help="Number of lines to analyze from end",
    ),
    since: Optional[str] = typer.Option(
        None,
        "--since",
        help="Show logs since timestamp or relative time",
    ),
    ai_analysis: bool = typer.Option(
        True,
        "--ai/--no-ai",
        help="Enable AI-powered analysis",
    ),
) -> None:
    """
    Analyze Docker container logs.
    
    Examples:
        debugai analyze docker my-api
        debugai analyze docker api db redis --tail 500
        debugai analyze docker my-app --follow
    """
    from debugai.ingestion.docker_ingester import DockerIngester
    from debugai.core.engine import DebugEngine
    
    # Get theme colors
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    
    console.print(Panel.fit(
        f"[bold {primary}]Docker Log Analysis[/]\n"
        f"[{dim_color}]Containers: {', '.join(containers)}[/]",
        border_style=border
    ))
    
    try:
        ingester = DockerIngester()
        engine = DebugEngine()
        
        with Progress(
            SpinnerColumn(style=primary),
            TextColumn(f"[{text_color}]" + "{task.description}" + f"[/{text_color}]"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[{primary}]Fetching Docker logs...", total=None)
            
            all_logs = []
            for container in containers:
                logs = ingester.ingest(
                    container=container,
                    tail=tail,
                    since=since,
                )
                all_logs.extend(logs)
            
            progress.update(task, description=f"[{primary}]Analyzing...")
            
            parsed = engine.parse_logs(all_logs)
            errors = engine.identify_errors(parsed)
            
            if ai_analysis and errors:
                analysis = engine.ai_analyze(errors, parsed)
            else:
                analysis = None
        
        _display_analysis_results(parsed, errors, analysis, OutputFormat.RICH)
        
    except Exception as e:
        console.print(f"[{ui.theme.error}]Docker analysis failed: {e}[/]")
        raise typer.Exit(1)


@app.command("stream")
def analyze_stream(
    source: str = typer.Argument(
        ...,
        help="Stream source (stdin, file path, or URL)",
    ),
    buffer_size: int = typer.Option(
        100,
        "--buffer",
        help="Number of lines to buffer before analysis",
    ),
    alert_level: str = typer.Option(
        "error",
        "--alert",
        help="Alert threshold level (error, warn, info)",
    ),
) -> None:
    """
    Analyze streaming logs in real-time.
    
    Examples:
        tail -f /var/log/app.log | debugai analyze stream stdin
        debugai analyze stream /var/log/app.log --buffer 50
    """
    from debugai.ingestion.stream_ingester import StreamIngester
    from debugai.core.engine import DebugEngine
    
    # Get theme colors
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    warning_color = ui.theme.warning
    
    console.print(Panel.fit(
        f"[bold {primary}]Live Log Analysis[/]\n"
        f"[{dim_color}]Source: {source} | Buffer: {buffer_size} | Alert: {alert_level}[/]",
        border_style=border
    ))
    console.print(f"[{warning_color}]Press Ctrl+C to stop[/]\n")
    
    try:
        ingester = StreamIngester()
        engine = DebugEngine()
        
        for batch in ingester.stream(source, buffer_size):
            parsed = engine.parse_logs(batch)
            errors = engine.identify_errors(parsed)
            
            for error in errors:
                if _should_alert(error, alert_level):
                    _display_live_error(error)
    
    except KeyboardInterrupt:
        console.print(f"\n[{warning_color}]Stream analysis stopped[/]")


def _display_analysis_results(
    parsed_logs: list,
    errors: list,
    analysis: Optional[dict],
    output_format: OutputFormat,
) -> None:
    """Display analysis results in the specified format."""
    
    # Get theme colors
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    error_color = ui.theme.error
    warning_color = ui.theme.warning
    success_color = ui.theme.success
    
    # Summary panel
    summary = Table(show_header=False, box=None, padding=(0, 2))
    summary.add_column("Metric", style=primary)
    summary.add_column("Value", style=f"bold {text_color}")
    
    summary.add_row("Total Log Entries", str(len(parsed_logs)))
    summary.add_row("Errors Found", f"[{error_color}]{len([e for e in errors if e.get('level') == 'error'])}[/]")
    summary.add_row("Warnings Found", f"[{warning_color}]{len([e for e in errors if e.get('level') == 'warn'])}[/]")
    
    if analysis:
        summary.add_row("Root Causes Identified", str(len(analysis.get('root_causes', []))))
        summary.add_row("Suggestions Generated", str(len(analysis.get('suggestions', []))))
    
    console.print(Panel(summary, title=f"[{primary}]Analysis Summary[/]", border_style=border))
    
    # Error details
    if errors:
        console.print(f"\n[bold {primary}]Errors Detected[/]\n")
        
        error_table = Table(show_header=True, header_style=f"bold {primary}")
        error_table.add_column("#", style=dim_color, width=4)
        error_table.add_column("Time", style=primary, width=20)
        error_table.add_column("Service", style=text_color, width=15)
        error_table.add_column("Error", style=error_color)
        
        for i, error in enumerate(errors[:10], 1):
            error_table.add_row(
                str(i),
                error.get("timestamp", "Unknown"),
                error.get("service", "Unknown"),
                error.get("message", "Unknown error")[:60] + "..."
            )
        
        console.print(error_table)
        
        if len(errors) > 10:
            console.print(f"\n[{dim_color}]... and {len(errors) - 10} more errors[/]")
    
    # AI Analysis results
    if analysis:
        console.print(f"\n[bold {primary}]AI Analysis[/]\n")
        
        # Root causes
        if analysis.get('root_causes'):
            console.print(f"[bold {text_color}]Root Cause Analysis:[/]")
            for i, cause in enumerate(analysis['root_causes'], 1):
                console.print(Panel(
                    f"[bold {text_color}]{cause['title']}[/]\n\n"
                    f"[{text_color}]{cause['explanation']}[/]\n\n"
                    f"[{dim_color}]Confidence: {cause['confidence']}%[/]",
                    title=f"[{primary}]Root Cause #{i}[/]",
                    border_style=border
                ))
        
        # Suggestions
        if analysis.get('suggestions'):
            console.print(f"\n[bold {text_color}]Suggested Fixes:[/]")
            for i, suggestion in enumerate(analysis['suggestions'], 1):
                console.print(f"\n  [{primary}]{i}.[/] [{text_color}]{suggestion['title']}[/]")
                console.print(f"     [{dim_color}]{suggestion['description']}[/]")
                
                if suggestion.get('code'):
                    console.print()
                    console.print(Syntax(
                        suggestion['code'],
                        suggestion.get('language', 'python'),
                        theme="monokai",
                        line_numbers=True,
                        word_wrap=True,
                    ))
        
        # Plain English summary
        if analysis.get('summary'):
            console.print(Panel(
                f"[{text_color}]{analysis['summary']}[/]",
                title=f"[{primary}]What Happened (Plain English)[/]",
                border_style=border
            ))


def _save_report(path: Path, logs: list, errors: list, analysis: Optional[dict]) -> None:
    """Save analysis report to file."""
    import json
    
    report = {
        "generated_at": str(Path),
        "total_logs": len(logs),
        "total_errors": len(errors),
        "errors": errors,
        "analysis": analysis,
    }
    
    with open(path, "w") as f:
        json.dump(report, f, indent=2, default=str)


def _should_alert(error: dict, threshold: str) -> bool:
    """Check if error meets alert threshold."""
    levels = {"debug": 0, "info": 1, "warn": 2, "error": 3, "critical": 4}
    error_level = levels.get(error.get("level", "info"), 1)
    threshold_level = levels.get(threshold, 2)
    return error_level >= threshold_level


def _display_live_error(error: dict) -> None:
    """Display error in live streaming mode."""
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    error_color = ui.theme.error
    
    console.print(Panel(
        f"[bold {error_color}]{error.get('message', 'Unknown error')}[/]\n"
        f"[{dim_color}]Service: {error.get('service', 'Unknown')} | "
        f"Time: {error.get('timestamp', 'Unknown')}[/]",
        border_style=border
    ))
