"""Environment configuration management for RedTunnel.

This module provides multi-environment support with configuration
loading, validation, and environment-specific settings.
"""

import os
import yaml
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional


class Environment(Enum):
    """Supported environment types."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class EnvironmentConfig:
    """Environment configuration manager."""
    
    DEFAULT_CONFIG = {
        "environment": "development",
        "debug": True,
        "log_level": "DEBUG",
        "cloudflare": {
            "api_token": "",
            "account_id": "",
            "zone_id": "",
        },
        "simulation": {
            "max_requests": 100,
            "timeout": 30,
            "delay_between_requests": 1.0,
        },
        "ui": {
            "use_nerdfont": True,
            "use_color": True,
            "use_unicode": True,
            "theme": "default",
        },
    }
    
    def __init__(self, config_path: Optional[str] = None, environment: Optional[str] = None):
        """Initialize environment configuration.
        
        Args:
            config_path: Path to configuration file
            environment: Environment to use (overrides config file)
        """
        self.config_path = config_path or self._find_config_path()
        self.environment = environment
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _find_config_path(self) -> str:
        """Find the configuration file."""
        # Check multiple possible locations
        possible_paths = [
            "config/settings.yml",
            "config/settings.yaml",
            os.path.expanduser("~/.redtunnel/config.yml"),
            os.path.expanduser("~/.redtunnel/config.yaml"),
            "/etc/redtunnel/config.yml",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        # Return default path if none found
        return "config/settings.yml"
    
    def _load_config(self) -> None:
        """Load configuration from file and environment variables."""
        # Start with defaults
        self._config = self.DEFAULT_CONFIG.copy()
        
        # Load from file if exists
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    file_config = yaml.safe_load(f)
                    if file_config:
                        self._deep_merge(self._config, file_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        # Override with environment-specific config
        env = self.get_environment()
        env_config_path = f"config/environments/{env.value}.yml"
        if os.path.exists(env_config_path):
            try:
                with open(env_config_path, "r") as f:
                    env_config = yaml.safe_load(f)
                    if env_config:
                        self._deep_merge(self._config, env_config)
            except Exception as e:
                print(f"Warning: Could not load environment config: {e}")
        
        # Override with command-line environment parameter
        if self.environment:
            self._config["environment"] = self.environment
        
        # Override with environment variables
        self._load_env_overrides()
    
    def _deep_merge(self, base: Dict, override: Dict) -> None:
        """Deep merge override dict into base dict."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def _load_env_overrides(self) -> None:
        """Load configuration overrides from environment variables."""
        env_mapping = {
            "REDTUNNEL_ENV": ("environment", str),
            "REDTUNNEL_DEBUG": ("debug", bool),
            "REDTUNNEL_LOG_LEVEL": ("log_level", str),
            "REDTUNNEL_CF_API_TOKEN": ("cloudflare.api_token", str),
            "REDTUNNEL_CF_ACCOUNT_ID": ("cloudflare.account_id", str),
            "REDTUNNEL_CF_ZONE_ID": ("cloudflare.zone_id", str),
            "REDTUNNEL_MAX_REQUESTS": ("simulation.max_requests", int),
            "REDTUNNEL_TIMEOUT": ("simulation.timeout", int),
        }
        
        for env_var, (config_key, config_type) in env_mapping.items():
            value = os.environ.get(env_var)
            if value is not None:
                # Convert string to appropriate type
                if config_type == bool:
                    value = value.lower() in ("true", "1", "yes")
                elif config_type == int:
                    value = int(value)
                
                # Set nested config value
                keys = config_key.split(".")
                target = self._config
                for key in keys[:-1]:
                    if key not in target:
                        target[key] = {}
                    target = target[key]
                target[keys[-1]] = value
    
    def get_environment(self) -> Environment:
        """Get the current environment."""
        env_name = self._config.get("environment", "development")
        try:
            return Environment(env_name.lower())
        except ValueError:
            return Environment.DEVELOPMENT
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key (supports dot notation)."""
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value by key (supports dot notation)."""
        keys = key.split(".")
        target = self._config
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
    
    def save(self, path: Optional[str] = None) -> None:
        """Save current configuration to file."""
        save_path = path or self.config_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, "w") as f:
            yaml.dump(self._config, f, default_flow_style=False)
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.get_environment() == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.get_environment() == Environment.DEVELOPMENT
    
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.get_environment() == Environment.TESTING
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the full configuration dictionary."""
        return self._config.copy()


# Global config instance
_config: Optional[EnvironmentConfig] = None


def get_config(config_path: Optional[str] = None, environment: Optional[str] = None) -> EnvironmentConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = EnvironmentConfig(config_path, environment)
    return _config


def reset_config() -> None:
    """Reset the global configuration instance (useful for testing)."""
    global _config
    _config = None