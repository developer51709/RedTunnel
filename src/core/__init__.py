"""Core functionality for RedTunnel."""

from .platform import PlatformInfo, PlatformType, get_platform_info
from .environment import EnvironmentConfig, Environment, get_config, reset_config

__all__ = [
    "PlatformInfo",
    "PlatformType", 
    "get_platform_info",
    "EnvironmentConfig",
    "Environment",
    "get_config",
    "reset_config",
]