"""
Doctor - Diagnose and fix common issues
"""

from typing import List, Dict, Any
from pathlib import Path
import os
import sys


def run_diagnostics() -> List[Dict[str, Any]]:
    """Run all diagnostic checks."""
    checks = [
        _check_python_version(),
        _check_dependencies(),
        _check_initialization(),
        _check_api_key(),
        _check_permissions(),
        _check_disk_space(),
    ]
    return checks


def _check_python_version() -> Dict[str, Any]:
    """Check Python version."""
    version = sys.version_info
    if version >= (3, 11):
        return {
            "name": "Python Version",
            "passed": True,
            "details": f"Python {version.major}.{version.minor}.{version.micro}"
        }
    return {
        "name": "Python Version",
        "passed": False,
        "fix": f"Upgrade to Python 3.11+ (current: {version.major}.{version.minor})"
    }


def _check_dependencies() -> Dict[str, Any]:
    """Check if required dependencies are installed."""
    required = {
        "typer": "typer",
        "rich": "rich", 
        "google-generativeai": "google.generativeai"
    }
    missing = []
    
    for pkg_name, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg_name)
    
    if not missing:
        return {
            "name": "Dependencies",
            "passed": True,
            "details": "All required packages installed"
        }
    return {
        "name": "Dependencies",
        "passed": False,
        "fix": f"pip install {' '.join(missing)}"
    }


def _check_initialization() -> Dict[str, Any]:
    """Check if DebugAI is initialized."""
    debugai_dir = Path.cwd() / ".debugai"
    
    if debugai_dir.exists():
        return {
            "name": "Initialization",
            "passed": True,
            "details": f"Initialized at {debugai_dir}"
        }
    return {
        "name": "Initialization",
        "passed": False,
        "fix": "Run 'debugai init' to initialize"
    }


def _check_api_key() -> Dict[str, Any]:
    """Check if API key is configured."""
    if os.environ.get("GEMINI_API_KEY"):
        return {
            "name": "API Key",
            "passed": True,
            "details": "GEMINI_API_KEY environment variable set"
        }
    
    # Check config
    config_path = Path.cwd() / ".debugai" / "config.yaml"
    if config_path.exists():
        content = config_path.read_text()
        if "api_key:" in content and "YOUR_API_KEY" not in content:
            return {
                "name": "API Key",
                "passed": True,
                "details": "API key found in config"
            }
    
    return {
        "name": "API Key",
        "passed": False,
        "fix": "Set GEMINI_API_KEY environment variable or run 'debugai config set api-key YOUR_KEY'"
    }


def _check_permissions() -> Dict[str, Any]:
    """Check file permissions."""
    debugai_dir = Path.cwd() / ".debugai"
    
    try:
        if debugai_dir.exists():
            # Try to write a test file
            test_file = debugai_dir / ".permission_test"
            test_file.write_text("test")
            test_file.unlink()
        
        return {
            "name": "Permissions",
            "passed": True,
            "details": "Read/write access OK"
        }
    except PermissionError:
        return {
            "name": "Permissions",
            "passed": False,
            "fix": f"Grant write permissions to {debugai_dir}"
        }


def _check_disk_space() -> Dict[str, Any]:
    """Check available disk space."""
    import shutil
    
    try:
        total, used, free = shutil.disk_usage(Path.cwd())
        free_gb = free / (1024 ** 3)
        
        if free_gb > 1:
            return {
                "name": "Disk Space",
                "passed": True,
                "details": f"{free_gb:.1f} GB available"
            }
        return {
            "name": "Disk Space",
            "passed": False,
            "fix": f"Free up disk space (only {free_gb:.2f} GB available)"
        }
    except:
        return {
            "name": "Disk Space",
            "passed": True,
            "details": "Could not check (assuming OK)"
        }
