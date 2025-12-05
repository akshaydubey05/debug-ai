"""
Project Initializer - Set up DebugAI in a directory
"""

from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class InitResult:
    """Result of initialization."""
    success: bool
    message: str
    path: Optional[Path] = None


def initialize_project(path: Optional[Path] = None) -> InitResult:
    """
    Initialize DebugAI in the specified directory.
    Creates .debugai folder with configuration and cache directories.
    """
    base_path = path or Path.cwd()
    debugai_dir = base_path / ".debugai"
    
    try:
        # Create main directory
        debugai_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (debugai_dir / "cache").mkdir(exist_ok=True)
        (debugai_dir / "patterns").mkdir(exist_ok=True)
        (debugai_dir / "reports").mkdir(exist_ok=True)
        
        # Create default config
        config_path = debugai_dir / "config.yaml"
        if not config_path.exists():
            config_path.write_text(DEFAULT_CONFIG)
        
        # Create .gitignore
        gitignore_path = debugai_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text("cache/\n*.db\n*.log\n")
        
        return InitResult(
            success=True,
            message="DebugAI initialized successfully",
            path=debugai_dir
        )
    
    except Exception as e:
        return InitResult(
            success=False,
            message=str(e)
        )


DEFAULT_CONFIG = """# DebugAI Configuration
# https://debugai.dev/docs/configuration

# AI Settings
ai:
  provider: gemini
  model: gemini-1.5-flash
  # api_key: YOUR_API_KEY  # Or set GEMINI_API_KEY env var
  max_tokens: 4096
  temperature: 0.3

# Log Parsing
parsing:
  # Supported formats: auto, json, apache, nginx, syslog, custom
  format: auto
  
  # Custom timestamp formats
  timestamp_formats:
    - "%Y-%m-%d %H:%M:%S"
    - "%Y-%m-%dT%H:%M:%S"
    - "%d/%b/%Y:%H:%M:%S"
  
  # Log level mapping
  level_mapping:
    error: [error, err, fatal, critical, crit]
    warning: [warning, warn, wrn]
    info: [info, inf, notice]
    debug: [debug, dbg, trace]

# Analysis Settings
analysis:
  # Enable cross-service correlation
  correlation: true
  
  # Maximum errors to analyze in detail
  max_errors: 100
  
  # Time window for correlation (seconds)
  correlation_window: 60
  
  # Enable pattern detection
  pattern_detection: true

# Output Settings
output:
  # Default format: rich, json, markdown, plain
  format: rich
  
  # Color theme: dark, light, auto
  theme: auto
  
  # Show timestamps
  timestamps: true

# Storage Settings
storage:
  # Database location
  database: .debugai/debugai.db
  
  # Cache TTL in hours
  cache_ttl: 24
  
  # Max cache size in MB
  max_cache_size: 100

# Sources
sources: []
"""
