"""
DebugAI UI Module - Themes and Animations
"""

import time
import random
import sys
import os
from pathlib import Path
from typing import Optional, List, Callable
from enum import Enum
from dataclasses import dataclass
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.style import Style
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


# Theme config file path
THEME_CONFIG_PATH = Path.home() / ".debugai_theme"


def save_theme_preference(theme_name: str) -> None:
    """Save theme preference to config file."""
    try:
        THEME_CONFIG_PATH.write_text(theme_name.lower())
    except Exception:
        pass  # Silently fail if can't save


def load_theme_preference() -> Optional[str]:
    """Load saved theme preference."""
    try:
        if THEME_CONFIG_PATH.exists():
            return THEME_CONFIG_PATH.read_text().strip().lower()
    except Exception:
        pass
    return None


@dataclass
class Theme:
    """Color theme definition"""
    name: str
    primary: str       # Main accent color
    secondary: str     # Dimmed/muted version
    text: str          # Primary text (usually white)
    dim: str           # Dimmed text
    success: str       # Success messages
    error: str         # Error messages
    warning: str       # Warning messages
    border: str        # Panel borders


class Themes(Enum):
    """Available themes"""
    CYAN = Theme(
        name="Cyan",
        primary="cyan",
        secondary="dark_cyan",
        text="white",
        dim="grey70",
        success="green",
        error="red",
        warning="yellow",
        border="cyan"
    )
    GREEN = Theme(
        name="Green",
        primary="green",
        secondary="dark_green",
        text="white",
        dim="grey70",
        success="bright_green",
        error="red",
        warning="yellow",
        border="green"
    )
    RED = Theme(
        name="Red",
        primary="red",
        secondary="dark_red",
        text="white",
        dim="grey70",
        success="green",
        error="bright_red",
        warning="yellow",
        border="red"
    )
    PURPLE = Theme(
        name="Purple",
        primary="magenta",
        secondary="dark_magenta",
        text="white",
        dim="grey70",
        success="green",
        error="red",
        warning="yellow",
        border="magenta"
    )
    ORANGE = Theme(
        name="Orange",
        primary="dark_orange",
        secondary="orange4",
        text="white",
        dim="grey70",
        success="green",
        error="red",
        warning="yellow",
        border="dark_orange"
    )
    BLUE = Theme(
        name="Blue",
        primary="blue",
        secondary="dark_blue",
        text="white",
        dim="grey70",
        success="green",
        error="red",
        warning="yellow",
        border="blue"
    )
    MATRIX = Theme(
        name="Matrix",
        primary="bright_green",
        secondary="green",
        text="bright_green",
        dim="dark_green",
        success="bright_green",
        error="red",
        warning="yellow",
        border="green"
    )
    HACKER = Theme(
        name="Hacker",
        primary="bright_green",
        secondary="dark_green",
        text="grey93",
        dim="grey50",
        success="bright_green",
        error="bright_red",
        warning="bright_yellow",
        border="bright_green"
    )


class UIEffects:
    """Animation and visual effects for CLI"""
    
    GLITCH_CHARS = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
    
    def __init__(self, console: Optional[Console] = None, theme: Themes = Themes.CYAN):
        self.console = console or Console()
        self.theme = theme.value
        self.animations_enabled = True
    
    def set_theme(self, theme: Themes, save: bool = True) -> None:
        """Change the current theme and optionally save preference"""
        self.theme = theme.value
        if save:
            save_theme_preference(theme.name.lower())
    
    def disable_animations(self) -> None:
        """Disable animations for non-interactive use"""
        self.animations_enabled = False
    
    def enable_animations(self) -> None:
        """Enable animations"""
        self.animations_enabled = True
    
    # ============= TEXT ANIMATIONS =============
    
    def glitch_text(self, text: str, duration: float = 0.5, final_color: Optional[str] = None) -> None:
        """Display text with glitch animation effect"""
        if not self.animations_enabled:
            self.console.print(f"[{final_color or self.theme.primary}]{text}[/]")
            return
        
        color = final_color or self.theme.primary
        iterations = int(duration * 20)
        text_len = len(text)
        
        for i in range(iterations):
            glitched = ""
            glitch_intensity = 1 - (i / iterations)  # Decreases over time
            
            for char in text:
                if char == " ":
                    glitched += " "
                elif random.random() < glitch_intensity * 0.7:
                    glitched += random.choice(self.GLITCH_CHARS)
                else:
                    glitched += char
            
            # Random color flicker during glitch
            if random.random() < glitch_intensity * 0.3:
                display_color = random.choice(["red", "green", "blue", "yellow", "magenta"])
            else:
                display_color = color
            
            # Clear line and print (works better in Windows)
            padding = " " * 5  # Extra padding to clear
            sys.stdout.write(f"\r\033[K")  # Clear line
            self.console.print(f"[{display_color}]{glitched}[/{display_color}]{padding}", end="")
            sys.stdout.flush()
            time.sleep(0.025)
        
        # Final clean text on new line
        sys.stdout.write(f"\r\033[K")  # Clear line
        self.console.print(f"[{color}]{text}[/{color}]")
    
    def typewriter(self, text: str, speed: float = 0.03, color: Optional[str] = None) -> None:
        """Display text with typewriter effect"""
        if not self.animations_enabled:
            self.console.print(f"[{color or self.theme.text}]{text}[/]")
            return
        
        color = color or self.theme.text
        for i, char in enumerate(text):
            self.console.print(f"[{color}]{char}[/]", end="")
            
            # Variable speed for natural feel
            if char in ".!?":
                time.sleep(speed * 5)
            elif char == ",":
                time.sleep(speed * 2)
            elif char == " ":
                time.sleep(speed * 0.5)
            else:
                time.sleep(speed)
        
        self.console.print()  # Newline at end
    
    def reveal_text(self, text: str, duration: float = 0.3, color: Optional[str] = None) -> None:
        """Reveal text character by character with fade effect"""
        if not self.animations_enabled:
            self.console.print(f"[{color or self.theme.text}]{text}[/]")
            return
        
        color = color or self.theme.text
        delay = duration / len(text) if text else 0
        
        for i in range(len(text) + 1):
            visible = text[:i]
            hidden = "░" * (len(text) - i)
            sys.stdout.write(f"\r\033[K")  # Clear line
            self.console.print(f"[{color}]{visible}[/][{self.theme.dim}]{hidden}[/]", end="")
            sys.stdout.flush()
            time.sleep(delay)
        
        sys.stdout.write(f"\r\033[K")
        self.console.print(f"[{color}]{text}[/]")
    
    def scramble_reveal(self, text: str, duration: float = 0.5, color: Optional[str] = None) -> None:
        """Reveal text with scrambling effect (like hacking scenes)"""
        if not self.animations_enabled:
            self.console.print(f"[{color or self.theme.primary}]{text}[/]")
            return
        
        color = color or self.theme.primary
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        iterations = int(duration * 30)
        revealed = [False] * len(text)
        
        for iteration in range(iterations):
            output = ""
            # Reveal more characters as we progress
            reveal_chance = iteration / iterations
            
            for i, char in enumerate(text):
                if revealed[i]:
                    output += char
                elif char == " ":
                    output += " "
                    revealed[i] = True
                elif random.random() < reveal_chance * 0.3:
                    output += char
                    revealed[i] = True
                else:
                    output += random.choice(chars)
            
            sys.stdout.write(f"\r\033[K")  # Clear line
            self.console.print(f"[{color}]{output}[/]", end="")
            sys.stdout.flush()
            time.sleep(duration / iterations)
        
        # Final clean text
        sys.stdout.write(f"\r\033[K")
        self.console.print(f"[{color}]{text}[/]")
    
    # ============= STYLED COMPONENTS =============
    
    def header(self, text: str, animate: bool = True) -> None:
        """Display animated header"""
        border = "═" * (len(text) + 4)
        
        if animate and self.animations_enabled:
            self.glitch_text(f"╔{border}╗", duration=0.2, final_color=self.theme.border)
            self.glitch_text(f"║  {text}  ║", duration=0.3, final_color=self.theme.primary)
            self.glitch_text(f"╚{border}╝", duration=0.2, final_color=self.theme.border)
        else:
            self.console.print(f"[{self.theme.border}]╔{border}╗[/]")
            self.console.print(f"[{self.theme.border}]║[/]  [{self.theme.primary}]{text}[/]  [{self.theme.border}]║[/]")
            self.console.print(f"[{self.theme.border}]╚{border}╝[/]")
    
    def subheader(self, text: str) -> None:
        """Display subheader with line"""
        line = "─" * 40
        self.console.print(f"\n[{self.theme.primary}]┌─ {text}[/]")
        self.console.print(f"[{self.theme.dim}]{line}[/]")
    
    def success(self, text: str, animate: bool = False) -> None:
        """Display success message"""
        self.console.print(f"[{self.theme.success}][OK] {text}[/]")
    
    def error(self, text: str, animate: bool = False) -> None:
        """Display error message"""
        self.console.print(f"[{self.theme.error}][ERROR] {text}[/]")
    
    def warning(self, text: str) -> None:
        """Display warning message"""
        self.console.print(f"[{self.theme.warning}][WARN] {text}[/]")
    
    def info(self, text: str, animate: bool = False) -> None:
        """Display info message"""
        self.console.print(f"[{self.theme.text}][INFO] {text}[/]")
    
    def dim(self, text: str) -> None:
        """Display dimmed text"""
        self.console.print(f"[{self.theme.dim}]{text}[/]")
    
    def panel(self, content: str, title: str = "", border_style: Optional[str] = None) -> None:
        """Display a themed panel"""
        style = border_style or self.theme.border
        self.console.print(Panel(
            content,
            title=f"[bold {self.theme.primary}]{title}[/]" if title else None,
            border_style=style,
            padding=(1, 2)
        ))
    
    def table(self, headers: List[str], rows: List[List[str]], title: str = "") -> None:
        """Display a themed table"""
        table = Table(
            title=f"[bold {self.theme.primary}]{title}[/]" if title else None,
            header_style=f"bold {self.theme.primary}",
            border_style=self.theme.border,
            show_header=True
        )
        
        for header in headers:
            table.add_column(header)
        
        for row in rows:
            styled_row = [f"[{self.theme.text}]{cell}[/]" for cell in row]
            table.add_row(*styled_row)
        
        self.console.print(table)
    
    def progress_bar(self, description: str = "Processing") -> Progress:
        """Get a themed progress bar"""
        return Progress(
            SpinnerColumn(style=self.theme.primary),
            TextColumn(f"[{self.theme.text}]{description}...[/]"),
            console=self.console
        )
    
    def divider(self, char: str = "─", width: int = 50) -> None:
        """Display a divider line"""
        self.console.print(f"[{self.theme.dim}]{char * width}[/]")
    
    # ============= SPECIAL EFFECTS =============
    
    def loading_animation(self, text: str = "Loading", duration: float = 2.0) -> None:
        """Display loading animation"""
        if not self.animations_enabled:
            self.console.print(f"[{self.theme.primary}]{text}...[/]")
            return
        
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end_time = time.time() + duration
        i = 0
        
        while time.time() < end_time:
            frame = frames[i % len(frames)]
            sys.stdout.write(f"\r\033[K")  # Clear line
            self.console.print(f"[{self.theme.primary}]{frame}[/] [{self.theme.text}]{text}...[/]", end="")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        
        sys.stdout.write(f"\r\033[K")  # Clear line
        self.console.print(f"[{self.theme.success}]✓[/] [{self.theme.text}]{text}[/]")
    
    def banner(self, lines: List[str], animate: bool = True) -> None:
        """Display ASCII art banner with animation"""
        if animate and self.animations_enabled:
            for line in lines:
                self.glitch_text(line, duration=0.1, final_color=self.theme.primary)
                time.sleep(0.05)
        else:
            for line in lines:
                self.console.print(f"[{self.theme.primary}]{line}[/]")
    
    def status_line(self, label: str, value: str, status: str = "ok") -> None:
        """Display a status line with label and value"""
        status_colors = {
            "ok": self.theme.success,
            "error": self.theme.error,
            "warning": self.theme.warning,
            "info": self.theme.primary
        }
        color = status_colors.get(status, self.theme.text)
        
        dots = "." * (40 - len(label) - len(value))
        self.console.print(
            f"[{self.theme.text}]{label}[/]"
            f"[{self.theme.dim}]{dots}[/]"
            f"[{color}]{value}[/]"
        )
    
    def code_block(self, code: str, language: str = "python") -> None:
        """Display syntax-highlighted code block"""
        from rich.syntax import Syntax
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        self.console.print(Panel(syntax, border_style=self.theme.border))
    
    def bullet_list(self, items: List[str], bullet: str = "•") -> None:
        """Display a bullet list"""
        for item in items:
            self.console.print(f"  [{self.theme.primary}]{bullet}[/] [{self.theme.text}]{item}[/]")
    
    def numbered_list(self, items: List[str]) -> None:
        """Display a numbered list"""
        for i, item in enumerate(items, 1):
            self.console.print(f"  [{self.theme.primary}]{i}.[/] [{self.theme.text}]{item}[/]")


# Theme name to enum mapping
THEME_MAP = {
    "cyan": Themes.CYAN,
    "green": Themes.GREEN,
    "red": Themes.RED,
    "purple": Themes.PURPLE,
    "orange": Themes.ORANGE,
    "blue": Themes.BLUE,
    "matrix": Themes.MATRIX,
    "hacker": Themes.HACKER,
}


def get_saved_theme() -> Themes:
    """Get the saved theme or default to CYAN"""
    saved = load_theme_preference()
    if saved and saved in THEME_MAP:
        return THEME_MAP[saved]
    return Themes.CYAN


# Global UI instance
_ui: Optional[UIEffects] = None


def get_ui(theme: Optional[Themes] = None) -> UIEffects:
    """Get or create the global UI instance.
    
    If theme is provided, uses that theme.
    Otherwise, loads from saved preference or defaults to CYAN.
    """
    global _ui
    if _ui is None:
        # Use provided theme, or load saved, or default to CYAN
        actual_theme = theme if theme is not None else get_saved_theme()
        _ui = UIEffects(theme=actual_theme)
    return _ui


def set_theme(theme: Themes) -> None:
    """Set the global theme"""
    get_ui().set_theme(theme)


# ASCII Art Banners
DEBUGAI_BANNER = [
    "╔══════════════════════════════════════════════════════════╗",
    "║  ____       _                      _    ___              ║",
    "║ |  _ \\  ___| |__  _   _  __ _     / \\  |_ _|             ║",
    "║ | | | |/ _ \\ '_ \\| | | |/ _` |   / _ \\  | |              ║",
    "║ | |_| |  __/ |_) | |_| | (_| |  / ___ \\ | |              ║",
    "║ |____/ \\___|_.__/ \\__,_|\\__, | /_/   \\_\\___|             ║",
    "║                         |___/                            ║",
    "║              AI-Powered Log Analysis                     ║",
    "╚══════════════════════════════════════════════════════════╝",
]

DEBUGAI_BANNER_SMALL = [
    "┌─────────────────────────┐",
    "│  DebugAI v1.0.0        │",
    "│  AI-Powered Debugging  │",
    "└─────────────────────────┘",
]
