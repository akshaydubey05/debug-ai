"""
Settings - Configuration management for DebugAI
"""

from typing import Any, Optional, Dict, List
from pathlib import Path
import os
import yaml


class Settings:
    """
    Manages DebugAI configuration from multiple sources:
    - Environment variables
    - Config file (.debugai/config.yaml)
    - User home directory (~/.debugai/config.yaml)
    - Default values
    """
    
    # Configuration key mappings
    KEY_MAPPINGS = {
        "api-key": ("ai", "api_key"),
        "model": ("ai", "model"),
        "provider": ("ai", "provider"),
        "format": ("output", "format"),
        "theme": ("output", "theme"),
        "correlation": ("analysis", "correlation"),
        "max-errors": ("analysis", "max_errors"),
    }
    
    # Environment variable mappings
    ENV_MAPPINGS = {
        "GEMINI_API_KEY": "api-key",
        "DEBUGAI_MODEL": "model",
        "DEBUGAI_FORMAT": "format",
    }
    
    DEFAULTS = {
        "ai": {
            "provider": "gemini",
            "model": "gemini-1.5-flash",
            "api_key": None,
            "max_tokens": 4096,
            "temperature": 0.3,
        },
        "parsing": {
            "format": "auto",
            "timestamp_formats": [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
            ],
        },
        "analysis": {
            "correlation": True,
            "max_errors": 100,
            "correlation_window": 60,
            "pattern_detection": True,
        },
        "output": {
            "format": "rich",
            "theme": "auto",
            "timestamps": True,
        },
        "storage": {
            "database": ".debugai/debugai.db",
            "cache_ttl": 24,
            "max_cache_size": 100,
        },
    }
    
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._config_path: Optional[Path] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from all sources."""
        # Start with defaults
        self._config = self._deep_copy(self.DEFAULTS)
        
        # Load from home directory
        home_config = Path.home() / ".debugai" / "config.yaml"
        if home_config.exists():
            self._merge_config(self._load_yaml(home_config))
        
        # Load from project directory
        project_config = Path.cwd() / ".debugai" / "config.yaml"
        if project_config.exists():
            self._config_path = project_config
            self._merge_config(self._load_yaml(project_config))
        
        # Override with environment variables
        self._load_env_vars()
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML config file."""
        try:
            with open(path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}
    
    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        for env_var, key in self.ENV_MAPPINGS.items():
            value = os.environ.get(env_var)
            if value:
                self.set(key, value, save=False)
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration into existing."""
        for key, value in new_config.items():
            if key in self._config and isinstance(self._config[key], dict) and isinstance(value, dict):
                self._config[key].update(value)
            else:
                self._config[key] = value
    
    def _deep_copy(self, obj: Any) -> Any:
        """Deep copy a dictionary."""
        if isinstance(obj, dict):
            return {k: self._deep_copy(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        return obj
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key (e.g., "api-key", "model")
            default: Default value if not found
        
        Returns:
            Configuration value
        """
        # Check if it's a mapped key
        if key in self.KEY_MAPPINGS:
            section, subkey = self.KEY_MAPPINGS[key]
            return self._config.get(section, {}).get(subkey, default)
        
        # Check if it's a dotted path (e.g., "ai.model")
        if "." in key:
            parts = key.split(".")
            value = self._config
            for part in parts:
                if isinstance(value, dict):
                    value = value.get(part)
                else:
                    return default
            return value if value is not None else default
        
        # Check top-level
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
            save: Whether to save to config file
        """
        # Check if it's a mapped key
        if key in self.KEY_MAPPINGS:
            section, subkey = self.KEY_MAPPINGS[key]
            if section not in self._config:
                self._config[section] = {}
            self._config[section][subkey] = value
        elif "." in key:
            parts = key.split(".")
            config = self._config
            for part in parts[:-1]:
                if part not in config:
                    config[part] = {}
                config = config[part]
            config[parts[-1]] = value
        else:
            self._config[key] = value
        
        if save:
            self._save_config()
    
    def list_all(self) -> List[Dict[str, Any]]:
        """List all configuration values."""
        items = []
        
        # Add mapped keys
        for key, (section, subkey) in self.KEY_MAPPINGS.items():
            value = self._config.get(section, {}).get(subkey)
            source = "config" if self._config_path else "default"
            
            # Check if from environment
            for env_var, mapped_key in self.ENV_MAPPINGS.items():
                if mapped_key == key and os.environ.get(env_var):
                    source = "environment"
                    break
            
            items.append({
                "key": key,
                "value": value,
                "source": source
            })
        
        return items
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self._config = self._deep_copy(self.DEFAULTS)
        self._save_config()
    
    def _save_config(self) -> None:
        """Save configuration to file."""
        if self._config_path is None:
            self._config_path = Path.cwd() / ".debugai" / "config.yaml"
            self._config_path.parent.mkdir(exist_ok=True)
        
        # Don't save API keys to file
        save_config = self._deep_copy(self._config)
        if "ai" in save_config and "api_key" in save_config["ai"]:
            if save_config["ai"]["api_key"]:
                save_config["ai"]["api_key"] = "***"  # Mask
        
        with open(self._config_path, "w") as f:
            yaml.dump(save_config, f, default_flow_style=False)
    
    @property
    def config_path(self) -> Optional[Path]:
        """Get current config file path."""
        return self._config_path
