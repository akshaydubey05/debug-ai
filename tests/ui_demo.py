"""
UI Demo - Test all themes and animations
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from debugai.ui import UIEffects, Themes, DEBUGAI_BANNER, DEBUGAI_BANNER_SMALL


def demo_theme(ui: UIEffects, theme_name: str):
    """Demo a single theme"""
    print("\n")
    ui.divider("═", 60)
    ui.header(f"{theme_name} Theme Demo")
    
    # Text animations
    ui.subheader("Text Animations")
    
    print()
    ui.console.print(f"[{ui.theme.dim}]Glitch Effect:[/]")
    ui.glitch_text("Analyzing system logs...", duration=0.4)
    
    time.sleep(0.3)
    print()
    ui.console.print(f"[{ui.theme.dim}]Typewriter Effect:[/]")
    ui.typewriter("Processing 1,247 log entries. Found 23 errors.", speed=0.02)
    
    time.sleep(0.3)
    print()
    ui.console.print(f"[{ui.theme.dim}]Reveal Effect:[/]")
    ui.reveal_text("Decrypting error patterns...", duration=0.3)
    
    time.sleep(0.3)
    print()
    ui.console.print(f"[{ui.theme.dim}]Scramble Reveal Effect:[/]")
    ui.scramble_reveal("ACCESS GRANTED: Root cause identified", duration=0.5)
    
    # Status messages
    ui.subheader("Status Messages")
    print()
    ui.success("Log analysis completed successfully")
    ui.error("Connection to database failed")
    ui.warning("High memory usage detected")
    ui.info("Processing batch 3 of 5")
    
    # Components
    ui.subheader("UI Components")
    print()
    ui.panel(
        f"[{ui.theme.text}]Error: NullPointerException\n"
        f"[{ui.theme.dim}]Location: UserService.java:142\n"
        f"[{ui.theme.dim}]Time: 2024-01-15 14:32:01[/]",
        title="Error Details"
    )
    
    # Status lines
    print()
    ui.status_line("API Connection", "Online", "ok")
    ui.status_line("Database", "Timeout", "error")
    ui.status_line("Cache", "Degraded", "warning")
    ui.status_line("Log Parser", "Ready", "info")
    
    # Lists
    ui.subheader("Lists")
    print()
    ui.bullet_list([
        "Parse log files from multiple sources",
        "Detect and categorize errors automatically",
        "Generate AI-powered explanations"
    ])
    
    print()
    ui.numbered_list([
        "Connection pool exhausted",
        "Authentication timeout",
        "Memory limit exceeded"
    ])
    
    # Table
    ui.subheader("Table")
    print()
    ui.table(
        headers=["Error ID", "Type", "Count", "Status"],
        rows=[
            ["ERR_001", "Database", "147", "Critical"],
            ["ERR_002", "Network", "89", "Warning"],
            ["ERR_003", "Memory", "23", "Resolved"],
        ],
        title="Error Summary"
    )


def main():
    print("\033[2J\033[H")  # Clear screen
    
    ui = UIEffects()
    
    # Show banner
    ui.banner(DEBUGAI_BANNER, animate=True)
    time.sleep(0.5)
    
    ui.typewriter("\nWelcome to the DebugAI UI Demo!", speed=0.03, color="white")
    ui.typewriter("This demo showcases all available themes and animations.\n", speed=0.02, color="grey70")
    
    time.sleep(0.5)
    
    # List available themes
    ui.console.print(f"\n[bold white]Available Themes:[/]")
    themes = list(Themes)
    for i, theme in enumerate(themes, 1):
        ui.console.print(f"  [{theme.value.primary}]{i}. {theme.value.name}[/]")
    
    ui.console.print(f"\n  [grey70]0. Show ALL themes[/]")
    ui.console.print(f"  [grey70]Q. Quit[/]")
    
    while True:
        try:
            choice = input(f"\n[?] Select theme (0-{len(themes)}, Q to quit): ").strip().upper()
            
            if choice == "Q":
                ui.success("Goodbye!")
                break
            
            if choice == "0":
                # Demo all themes
                for theme in themes:
                    ui.set_theme(theme)
                    demo_theme(ui, theme.value.name)
                    time.sleep(0.5)
            elif choice.isdigit() and 1 <= int(choice) <= len(themes):
                theme = themes[int(choice) - 1]
                ui.set_theme(theme)
                demo_theme(ui, theme.value.name)
            else:
                ui.error("Invalid choice. Try again.")
                
        except KeyboardInterrupt:
            print()
            ui.warning("Interrupted")
            break
        except Exception as e:
            ui.error(f"Error: {e}")
    
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
