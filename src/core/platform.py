"""Platform detection and compatibility module for RedTunnel.

This module provides cross-platform detection and compatibility checks,
including support for Termux on Android and other less common platforms.
"""

import os
import sys
import platform
from enum import Enum
from typing import Optional


class PlatformType(Enum):
    """Supported platform types."""
    LINUX = "linux"
    DARWIN = "darwin"
    WINDOWS = "windows"
    ANDROID_TERMUX = "android_termux"
    UNKNOWN = "unknown"


class PlatformInfo:
    """Platform information and compatibility detection."""
    
    def __init__(self):
        self._platform_type = self._detect_platform()
        self._termux_detected = self._detect_termux()
        self._nerdfont_available = self._detect_nerdfont()
        
    def _detect_platform(self) -> PlatformType:
        """Detect the current platform type."""
        system = platform.system().lower()
        
        # Check for Termux first (it may report as different systems)
        if self._detect_termux():
            return PlatformType.ANDROID_TERMUX
        
        if system == "linux":
            return PlatformType.LINUX
        elif system == "darwin":
            return PlatformType.DARWIN
        elif system == "windows":
            return PlatformType.WINDOWS
        else:
            # If we detected Termux but system is unknown, still return Termux
            if self._detect_termux():
                return PlatformType.ANDROID_TERMUX
            return PlatformType.UNKNOWN
    
    def _detect_termux(self) -> bool:
        """Detect if running under Termux on Android."""
        # Termux sets specific environment variables
        return (
            "TERMUX_VERSION" in os.environ or
            "TERMUX_APP__PACKAGE_NAME" in os.environ or
            os.path.exists("/data/data/com.termux")
        )
    
    def _detect_nerdfont(self) -> bool:
        """Detect if NerdFont is available in the terminal."""
        try:
            # Check if we can import and use nerdfont package
            import nerdfont
            return True
        except ImportError:
            return False
    
    @property
    def platform_type(self) -> PlatformType:
        """Get the detected platform type."""
        return self._platform_type
    
    @property
    def is_termux(self) -> bool:
        """Check if running under Termux."""
        return self._termux_detected
    
    @property
    def is_android(self) -> bool:
        """Check if running on Android."""
        return self._termux_detected
    
    @property
    def has_nerdfont(self) -> bool:
        """Check if NerdFont is available."""
        return self._nerdfont_available
    
    @property
    def is_mobile(self) -> bool:
        """Check if running on a mobile platform."""
        return self._termux_detected
    
    @property
    def python_version(self) -> tuple:
        """Get Python version as tuple."""
        return sys.version_info[:3]
    
    @property
    def supports_color(self) -> bool:
        """Check if terminal supports color."""
        # Check if we're in a terminal that supports color
        if sys.stdout.isatty():
            # Check TERM environment variable
            term = os.environ.get("TERM", "")
            if term and term != "dumb":
                return True
        return False
    
    @property
    def supports_unicode(self) -> bool:
        """Check if terminal supports Unicode."""
        # Most modern terminals support Unicode
        # This is a basic check - could be enhanced
        encoding = sys.stdout.encoding or ""
        return "utf" in encoding.lower()
    
    def get_platform_name(self) -> str:
        """Get human-readable platform name."""
        if self._platform_type == PlatformType.ANDROID_TERMUX:
            return "Android (Termux)"
        elif self._platform_type == PlatformType.LINUX:
            return "Linux"
        elif self._platform_type == PlatformType.DARWIN:
            return "macOS"
        elif self._platform_type == PlatformType.WINDOWS:
            return "Windows"
        else:
            return "Unknown"
    
    def get_recommended_config(self) -> dict:
        """Get recommended configuration for current platform."""
        config = {
            "use_nerdfont": self._nerdfont_available,
            "use_color": self.supports_color,
            "use_unicode": self.supports_unicode,
            "termux_mode": self._termux_detected,
        }
        
        # Platform-specific recommendations
        if self._termux_detected:
            config.update({
                "max_workers": 2,  # Limited resources on mobile
                "cache_enabled": True,  # Reduce network calls
                "log_level": "INFO",  # Reduce verbosity
            })
        elif self._platform_type == PlatformType.WINDOWS:
            config.update({
                "use_windows_ansi": True,
            })
        
        return config


# Global platform instance
_platform_info: Optional[PlatformInfo] = None


def get_platform_info() -> PlatformInfo:
    """Get the global platform info instance."""
    global _platform_info
    if _platform_info is None:
        _platform_info = PlatformInfo()
    return _platform_info