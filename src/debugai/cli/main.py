"""
DebugAI CLI - Main Entry Point

This module defines the main CLI application with all commands.
"""

import sys
import typer
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint

from debugai.cli.commands import analyze, explain, suggest, timeline, config, logs, interactive
from debugai import __version__
from debugai.ui import UIEffects, Themes, DEBUGAI_BANNER, get_ui, get_saved_theme, THEME_MAP

# Parse theme from command line arguments early (before Typer processes them)
def _get_theme_from_args():
    """Extract theme from command line args before Typer runs.
    
    If --theme is provided in args, use that.
    Otherwise, load from saved preference.
    """
    args = sys.argv[1:]
    
    # Check if theme is explicitly provided in args
    for i, arg in enumerate(args):
        if arg in ("--theme", "-t") and i + 1 < len(args):
            theme_name = args[i + 1].lower()
            return THEME_MAP.get(theme_name, get_saved_theme())
        elif arg.startswith("--theme="):
            theme_name = arg.split("=", 1)[1].lower()
            return THEME_MAP.get(theme_name, get_saved_theme())
    
    # No theme in args, use saved preference
    return get_saved_theme()

# Initialize console and UI with the theme from args or saved preference
console = Console()
_initial_theme = _get_theme_from_args()
ui = get_ui(_initial_theme)

# Get dynamic help text based on current theme
def _get_help_text():
    """Generate help text with current theme colors."""
    primary = ui.theme.primary
    secondary = ui.theme.secondary
    dim = ui.theme.dim
    
    return f"""DebugAI - AI-Powered Log Analysis & Debugging CLI
    
Reduce debugging time by 60-75% with intelligent log analysis,
error correlation, and AI-powered fix suggestions.

[bold {primary}]Quick Start:[/]

  $ debugai init                           # Initialize in current directory
  $ debugai config set api-key YOUR_KEY    # Set Gemini API key
  $ debugai analyze ./logs                 # Analyze log files
  $ debugai explain error_12345            # Explain an error
  $ debugai suggest-fix "NullPointerException"  # Get fix suggestions
  $ debugai timeline --last 5m             # View recent events

[bold {primary}]Examples:[/]

  # Analyze logs from multiple services
  $ debugai analyze ./logs --service api,db,redis
  
  # Get plain English explanation of an error
  $ debugai explain err_abc123 --verbose
  
  # Generate timeline of events leading to crash
  $ debugai timeline --last 10m --filter errors

[{dim}]Run 'debugai COMMAND --help' for more information on a command.[/]"""

# Create main Typer app
app = typer.Typer(
    name="debugai",
    help="AI-Powered Log Analysis & Debugging CLI - Reduce debugging time by 60-75%",
    add_completion=True,
    no_args_is_help=False,  # We handle no-args ourselves for custom output
    rich_markup_mode="rich",
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
)

# Register command groups
app.add_typer(analyze.app, name="analyze", help="Analyze logs from multiple sources")
app.add_typer(explain.app, name="explain", help="Explain errors in plain English")
app.add_typer(suggest.app, name="suggest-fix", help="Get AI-powered fix suggestions")
app.add_typer(timeline.app, name="timeline", help="Generate event timeline")
app.add_typer(config.app, name="config", help="Configure DebugAI settings")
app.add_typer(logs.app, name="logs", help="Manage log sources")
app.add_typer(interactive.app, name="interactive", help="Interactive debugging session")

# Import themed help for single commands
from debugai.cli.help_theme import show_single_command_help


@app.command()
def version(
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """Display DebugAI version and system information."""
    if help_flag:
        show_single_command_help(
            command_name="debugai version",
            description="Display DebugAI version and system information including Python version, platform, and architecture.",
            examples=["debugai version"]
        )
        raise typer.Exit(0)
    
    import platform
    import sys
    
    ui.banner(DEBUGAI_BANNER, animate=True)
    print()
    ui.subheader("System Information")
    print()
    ui.status_line("Version", f"v{__version__}", "ok")
    ui.status_line("Python", sys.version.split()[0], "info")
    ui.status_line("Platform", f"{platform.system()} {platform.release()}", "info")
    ui.status_line("Architecture", platform.machine(), "info")
    print()
    ui.success("Ready to debug!")


@app.command()
def init(
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """Initialize DebugAI in the current directory."""
    if help_flag:
        show_single_command_help(
            command_name="debugai init",
            description="Initialize DebugAI in the current directory. Creates .debugai/ folder with configuration files, patterns directory, and cache.",
            examples=[
                "debugai init",
                "cd my-project && debugai init"
            ]
        )
        raise typer.Exit(0)
    
    from debugai.core.initializer import initialize_project
    
    print()
    ui.glitch_text("Initializing DebugAI...", duration=0.4)
    print()
    
    try:
        result = initialize_project()
        if result.success:
            ui.success("DebugAI initialized successfully!")
            print()
            ui.subheader("Created")
            ui.bullet_list([
                ".debugai/ - Configuration directory",
                ".debugai/config.yaml - Main configuration", 
                ".debugai/patterns/ - Custom log patterns",
                ".debugai/cache/ - Analysis cache"
            ])
            print()
            ui.subheader("Next Steps")
            ui.numbered_list([
                "Configure your Gemini API key: debugai config set api-key YOUR_KEY",
                "Add log sources: debugai logs add ./logs --name app-logs",
                "Start analyzing: debugai analyze path ./logs"
            ])
            print()
        else:
            ui.error(f"Initialization failed: {result.message}")
    except Exception as e:
        ui.error(f"Error during initialization: {e}")
        raise typer.Exit(1)


@app.command()
def status(
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """Check DebugAI status and configuration."""
    if help_flag:
        show_single_command_help(
            command_name="debugai status",
            description="Check DebugAI status and configuration. Shows health status of all components including API connection, database, and log sources.",
            examples=["debugai status"]
        )
        raise typer.Exit(0)
    
    from debugai.core.status import get_status
    
    print()
    ui.glitch_text("DebugAI Status", duration=0.3)
    print()
    
    status_info = get_status()
    
    for component, info in status_info.items():
        status_type = "ok" if info["healthy"] else "error"
        ui.status_line(
            component,
            info['status'],
            status_type
        )
    print()


@app.command()
def doctor(
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """Diagnose and fix common issues."""
    if help_flag:
        show_single_command_help(
            command_name="debugai doctor",
            description="Diagnose and fix common issues. Runs system checks for Python version, dependencies, API key configuration, and database connectivity.",
            examples=["debugai doctor"]
        )
        raise typer.Exit(0)
    
    from debugai.core.doctor import run_diagnostics
    
    print()
    ui.glitch_text("Running diagnostics...", duration=0.4)
    print()
    
    ui.loading_animation("Checking system", duration=1.5)
    
    results = run_diagnostics()
    
    print()
    for check in results:
        if check["passed"]:
            ui.success(check['name'])
        else:
            ui.error(check['name'])
            ui.dim(f"     Fix: {check['fix']}")
    print()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress non-essential output"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
    theme: str = typer.Option(None, "--theme", "-t", help="UI theme: cyan, green, red, purple, orange, blue, matrix, hacker (saves preference)"),
    no_animation: bool = typer.Option(False, "--no-animation", help="Disable animations"),
    help_flag: bool = typer.Option(False, "--help", "-h", help="Show this help message", is_eager=True),
) -> None:
    """
    DebugAI - AI-Powered Log Analysis & Debugging CLI
    """
    # Store global options in context
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["debug"] = debug
    
    # If theme is explicitly provided, update and save it
    if theme is not None:
        if theme.lower() in THEME_MAP:
            ui.set_theme(THEME_MAP[theme.lower()], save=True)
    
    # Handle animation setting
    if no_animation or quiet:
        ui.disable_animations()
    
    # Get theme colors for help
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    
    # If help flag or no command provided, show custom themed help
    if help_flag or ctx.invoked_subcommand is None:
        from rich.box import ROUNDED
        from rich.table import Table
        from rich.live import Live
        from rich.text import Text
        
        # ASCII Art Banner
        banner = [
            "██████╗ ███████╗██████╗ ██╗   ██╗ ██████╗  █████╗ ██╗",
            "██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝ ██╔══██╗██║",
            "██║  ██║█████╗  ██████╔╝██║   ██║██║  ███╗███████║██║",
            "██║  ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║██╔══██║██║",
            "██████╔╝███████╗██████╔╝╚██████╔╝╚██████╔╝██║  ██║██║",
            "╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝",
        ]
        
        console.print()
        
        # Animate the banner (always animate unless --no-animation or --quiet)
        if ui.animations_enabled:
            import time
            import random
            
            glitch_chars = "░▒▓█▄▀▐▌"
            colors = [primary, "red", "green", "yellow", "magenta", "cyan"]
            
            def generate_frame(frame_num, total_frames):
                """Generate a single animation frame."""
                lines = []
                progress = frame_num / total_frames
                
                for line in banner:
                    output = ""
                    for i, char in enumerate(line):
                        char_progress = i / len(line)
                        
                        if char == " ":
                            output += " "
                        elif progress > char_progress:
                            # Revealed - maybe glitch
                            if frame_num < total_frames - 3 and random.random() < 0.15 * (1 - progress):
                                output += random.choice(glitch_chars)
                            else:
                                output += char
                        else:
                            # Not revealed yet
                            if random.random() < 0.6:
                                output += random.choice(glitch_chars)
                            else:
                                output += " "
                    lines.append(output)
                return lines
            
            total_frames = 20
            
            with Live(console=console, refresh_per_second=30, transient=True) as live:
                for frame in range(total_frames + 1):
                    frame_lines = generate_frame(frame, total_frames)
                    
                    # Pick color - more random early, stable at end
                    if frame < total_frames - 2 and random.random() < 0.3 * (1 - frame/total_frames):
                        color = random.choice(colors)
                    else:
                        color = primary
                    
                    # Create rich text
                    display = Text()
                    for line in frame_lines:
                        display.append(line + "\n", style=f"bold {color}")
                    
                    live.update(display)
                    time.sleep(0.04)
            
            # Print final banner (not transient)
            for line in banner:
                console.print(f"[bold {primary}]{line}[/]")
        else:
            # No animation, just print
            for line in banner:
                console.print(f"[bold {primary}]{line}[/]")
        
        console.print()
        console.print(f"[{text_color}]AI-Powered Log Analysis & Debugging CLI[/]")
        console.print(f"[{dim_color}]Reduce debugging time by 60-75%[/]")
        console.print()
        
        # Options panel
        options_table = Table(show_header=False, box=ROUNDED, border_style=border, 
                              title=f"[{primary}]Options[/]", title_justify="left",
                              padding=(0, 1), expand=True)
        options_table.add_column("Option", style=primary, width=20)
        options_table.add_column("Short", style=primary, width=6)
        options_table.add_column("Description", style=text_color)
        
        options_table.add_row("--theme", "-t", "Set UI theme (saves preference)")
        options_table.add_row("--verbose", "-v", "Enable verbose output")
        options_table.add_row("--quiet", "-q", "Suppress non-essential output")
        options_table.add_row("--no-animation", "", "Disable animations")
        options_table.add_row("--help", "-h", "Show this message and exit")
        
        console.print(options_table)
        console.print()
        
        # Commands panel
        commands_table = Table(show_header=False, box=ROUNDED, border_style=border,
                               title=f"[{primary}]Commands[/]", title_justify="left",
                               padding=(0, 1), expand=True)
        commands_table.add_column("Command", style=primary, width=15)
        commands_table.add_column("Description", style=text_color)
        
        commands_table.add_row("analyze", "Analyze logs from multiple sources")
        commands_table.add_row("explain", "Explain errors in plain English")
        commands_table.add_row("suggest-fix", "Get AI-powered fix suggestions")
        commands_table.add_row("timeline", "Generate event timeline")
        commands_table.add_row("config", "Configure DebugAI settings")
        commands_table.add_row("logs", "Manage log sources")
        commands_table.add_row("interactive", "Interactive debugging session")
        commands_table.add_row("init", "Initialize DebugAI in current directory")
        commands_table.add_row("status", "Check DebugAI status and configuration")
        commands_table.add_row("doctor", "Diagnose and fix common issues")
        commands_table.add_row("version", "Display version and system information")
        
        console.print(commands_table)
        console.print()
        
        # Themes panel
        themes_table = Table(show_header=False, box=ROUNDED, border_style=border,
                             title=f"[{primary}]Themes[/]", title_justify="left",
                             padding=(0, 1), expand=True)
        themes_table.add_column("Themes", style=text_color)
        themes_table.add_row("cyan, green, red, purple, orange, blue, matrix, hacker")
        
        console.print(themes_table)
        console.print()
        
        # Quick Start panel
        quick_table = Table(show_header=False, box=ROUNDED, border_style=border,
                            title=f"[{primary}]Quick Start[/]", title_justify="left",
                            padding=(0, 1), expand=True)
        quick_table.add_column("Command", style=text_color)
        quick_table.add_column("Description", style=dim_color)
        
        quick_table.add_row("debugai init", "Initialize DebugAI")
        quick_table.add_row("debugai config set api-key YOUR_KEY", "Set Gemini API key")
        quick_table.add_row("debugai analyze path ./logs", "Analyze log files")
        
        console.print(quick_table)
        console.print()
        
        console.print(f"[{dim_color}]Powered by Google Gemini AI[/]")
        console.print()
        
        raise typer.Exit(0)


if __name__ == "__main__":
    app()
