"""
DebugAI - AI-Powered Log Analysis & Debugging CLI

Reduce debugging time by 60-75% with AI-powered log analysis,
error correlation, and intelligent fix suggestions.
"""

import os
from pathlib import Path

__version__ = "1.0.0"
__author__ = "DebugAI Team"
__license__ = "MIT"


def _load_env_file():
    """Load environment variables from .env file if it exists."""
    # Check multiple locations for .env file
    locations = [
        Path.cwd() / ".env",
        Path.cwd() / ".env.example",
        Path(__file__).parent.parent.parent.parent / ".env",
        Path(__file__).parent.parent.parent.parent / ".env.example",
    ]
    
    for env_path in locations:
        if env_path.exists():
            try:
                with open(env_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if not line or line.startswith("#"):
                            continue
                        # Parse KEY=VALUE
                        if "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip()
                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]
                            # Only set if not already set
                            if key and not os.environ.get(key):
                                os.environ[key] = value
                break  # Stop after first .env found
            except Exception:
                pass  # Silently ignore errors


# Auto-load .env on import
_load_env_file()

from debugai.core.analyzer import LogAnalyzer
from debugai.core.engine import DebugEngine

__all__ = [
    "__version__",
    "LogAnalyzer",
    "DebugEngine",
]
