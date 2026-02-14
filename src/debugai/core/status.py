"""
Status - Check DebugAI status and health
"""

from typing import Dict, Any
from pathlib import Path
import os


def get_status() -> Dict[str, Dict[str, Any]]:
    """Get status of all DebugAI components."""
    status = {}
    
    # Check configuration
    status["Configuration"] = _check_configuration()
    
    # Check API key
    status["Gemini API"] = _check_api_key()
    
    # Check database
    status["Database"] = _check_database()
    
    # Check log sources
    status["Log Sources"] = _check_log_sources()
    
    return status


def _check_configuration() -> Dict[str, Any]:
    """Check if DebugAI is configured."""
    config_path = Path.cwd() / ".debugai" / "config.yaml"
    
    if config_path.exists():
        return {
            "healthy": True,
            "status": "Configured",
            "details": str(config_path)
        }
    return {
        "healthy": False,
        "status": "Not initialized",
        "details": "Run 'debugai init' to initialize"
    }


def _check_api_key() -> Dict[str, Any]:
    """Check if Gemini API key is configured."""
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if api_key:
        return {
            "healthy": True,
            "status": "Configured",
            "details": f"Key: {api_key[:8]}..."
        }
    
    # Check config file
    from debugai.config.settings import Settings
    try:
        settings = Settings()
        if settings.get("api-key"):
            return {
                "healthy": True,
                "status": "Configured",
                "details": "From config file"
            }
    except:
        pass
    
    return {
        "healthy": False,
        "status": "Not configured",
        "details": "Set GEMINI_API_KEY or run 'debugai config set api-key YOUR_KEY'"
    }


def _check_database() -> Dict[str, Any]:
    """Check database status."""
    db_path = Path.cwd() / ".debugai" / "debugai.db"
    
    if db_path.exists():
        size_mb = db_path.stat().st_size / (1024 * 1024)
        return {
            "healthy": True,
            "status": "Connected",
            "details": f"Size: {size_mb:.2f} MB"
        }
    return {
        "healthy": True,
        "status": "Ready",
        "details": "Will be created on first use"
    }


def _check_log_sources() -> Dict[str, Any]:
    """Check configured log sources."""
    try:
        from debugai.storage.database import Database
        db = Database()
        sources = db.get_log_sources()
        
        if sources:
            return {
                "healthy": True,
                "status": f"{len(sources)} configured",
                "details": ", ".join(s["name"] for s in sources[:3])
            }
    except:
        pass
    
    return {
        "healthy": True,
        "status": "None configured",
        "details": "Use 'debugai logs add' to add sources"
    }
