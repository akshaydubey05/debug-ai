"""
Themed Help for Sub-commands and Single Commands
"""

import sys
import time
import random
from typing import List, Tuple, Optional
from rich.console import Console
from rich.box import ROUNDED
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

from debugai.ui import get_ui

console = Console()

# ASCII Art Banner
BANNER = """
 ____  _____ ____  _   _  ____    _    ___ 
|  _ \\| ____| __ )| | | |/ ___|  / \\  |_ _|
| | | |  _| |  _ \\| | | | |  _  / _ \\  | | 
| |_| | |___| |_) | |_| | |_| |/ ___ \\ | | 
|____/|_____|____/ \\___/ \\____/_/   \\_\\___|
"""


def _show_banner_animation(primary: str) -> None:
    """Display ASCII banner with glitch animation."""
    glitch_chars = ['@', '#', '$', '%', '&', '*', '!', '?', '+', '=']
    banner_lines = BANNER.strip().split('\n')
    
    # Glitch animation
    try:
        with Live(console=console, refresh_per_second=30, transient=True) as live:
            # Glitch reveal
            for frame in range(8):
                glitch_text = Text()
                for line in banner_lines:
                    glitch_line = ""
                    for char in line:
                        if char != ' ' and random.random() < (0.7 - frame * 0.1):
                            glitch_line += random.choice(glitch_chars)
                        else:
                            glitch_line += char
                    glitch_text.append(glitch_line + "\n", style=f"bold {primary}")
                live.update(glitch_text)
                time.sleep(0.05)
            
            # Stable banner
            final_text = Text()
            for line in banner_lines:
                final_text.append(line + "\n", style=f"bold {primary}")
            live.update(final_text)
            time.sleep(0.1)
    except Exception:
        pass
    
    # Print stable banner after animation
    for line in banner_lines:
        console.print(f"[bold {primary}]{line}[/]")


def show_command_help(
    command_name: str,
    description: str,
    subcommands: List[Tuple[str, str]],
    examples: Optional[List[str]] = None,
    options: Optional[List[Tuple[str, str, str]]] = None,
) -> None:
    """Display themed help for a command group (no ASCII banner).
    
    Args:
        command_name: Name of the command (e.g., "debugai logs", "debugai analyze")
        description: Description of the command
        subcommands: List of (name, description) tuples for sub-commands
        examples: List of example commands
        options: List of (option, short, description) tuples for options
    """
    ui = get_ui()
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    
    console.print()
    
    # Build help content
    help_parts = []
    
    # Description
    help_parts.append(f"[bold {primary}]DESCRIPTION[/]")
    help_parts.append(f"  {description}")
    help_parts.append("")
    
    # Commands
    if subcommands:
        help_parts.append(f"[bold {primary}]COMMANDS[/]")
        max_cmd_len = max(len(cmd) for cmd, _ in subcommands)
        for cmd, desc in subcommands:
            help_parts.append(f"  [{primary}]{cmd:<{max_cmd_len}}[/]  {desc}")
        help_parts.append("")
    
    # Examples
    if examples:
        help_parts.append(f"[bold {primary}]EXAMPLES[/]")
        for example in examples:
            help_parts.append(f"  [{dim_color}]$[/] {example}")
        help_parts.append("")
    
    # Options
    help_parts.append(f"[bold {primary}]OPTIONS[/]")
    help_parts.append(f"  [{text_color}]-h, --help[/]    Show this help message")
    
    help_text = "\n".join(help_parts)
    
    console.print(Panel(
        help_text,
        title=f"[bold {primary}]{command_name}[/]",
        border_style=border,
        box=ROUNDED,
        padding=(1, 2)
    ))
    console.print()


def show_single_command_help(
    command_name: str,
    description: str,
    options: Optional[List[Tuple[str, str]]] = None,
    examples: Optional[List[str]] = None,
) -> None:
    """Display themed help for a single command (no ASCII banner).
    
    Args:
        command_name: Full command name (e.g., "debugai init")
        description: Description of what the command does
        options: List of (option_flags, description) tuples
        examples: List of example usage strings
    """
    ui = get_ui()
    primary = ui.theme.primary
    text_color = ui.theme.text
    dim_color = ui.theme.dim
    border = ui.theme.border
    
    console.print()
    
    # Build help content
    help_parts = []
    
    # Description
    help_parts.append(f"[bold {primary}]DESCRIPTION[/]")
    help_parts.append(f"  {description}")
    help_parts.append("")
    
    # Usage
    help_parts.append(f"[bold {primary}]USAGE[/]")
    help_parts.append(f"  [{dim_color}]$[/] {command_name} [OPTIONS]")
    help_parts.append("")
    
    # Examples
    if examples:
        help_parts.append(f"[bold {primary}]EXAMPLES[/]")
        for example in examples:
            help_parts.append(f"  [{dim_color}]$[/] {example}")
        help_parts.append("")
    
    # Options
    help_parts.append(f"[bold {primary}]OPTIONS[/]")
    if options:
        max_opt_len = max(len(opt) for opt, _ in options)
        for opt, desc in options:
            help_parts.append(f"  [{text_color}]{opt:<{max_opt_len}}[/]  {desc}")
    help_parts.append(f"  [{text_color}]-h, --help[/]        Show this help message")
    
    help_text = "\n".join(help_parts)
    
    console.print(Panel(
        help_text,
        title=f"[bold {primary}]{command_name}[/]",
        border_style=border,
        box=ROUNDED,
        padding=(1, 2)
    ))
    console.print()


def check_help_flag() -> bool:
    """Check if --help or -h is in the command line arguments."""
    return "--help" in sys.argv or "-h" in sys.argv
