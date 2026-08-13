"""Theme management for the TUI.

This module provides color themes and styling options with
automatic fallback for terminals that don't support color.
"""

from enum import Enum
from typing import Dict, Optional


class Color(Enum):
    """ANSI color codes."""
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    BRIGHT_BLACK = 90
    BRIGHT_RED = 91
    BRIGHT_GREEN = 92
    BRIGHT_YELLOW = 93
    BRIGHT_BLUE = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN = 96
    BRIGHT_WHITE = 97
    RESET = 0


class Style:
    """Text styling with ANSI codes."""
    
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    RESET = "\033[0m"
    
    @staticmethod
    def color(text: str, color: Color) -> str:
        """Apply color to text."""
        return f"\033[{color.value}m{text}\033[{Color.RESET.value}m"
    
    @staticmethod
    def bold(text: str) -> str:
        """Apply bold styling."""
        return f"{Style.BOLD}{text}{Style.RESET}"
    
    @staticmethod
    def dim(text: str) -> str:
        """Apply dim styling."""
        return f"{Style.DIM}{text}{Style.RESET}"
    
    @staticmethod
    def underline(text: str) -> str:
        """Apply underline styling."""
        return f"{Style.UNDERLINE}{text}{Style.RESET}"


class Theme:
    """Theme configuration for TUI."""
    
    THEMES = {
        "default": {
            "primary": Color.BLUE,
            "secondary": Color.CYAN,
            "success": Color.GREEN,
            "warning": Color.YELLOW,
            "error": Color.RED,
            "info": Color.BRIGHT_BLUE,
            "muted": Color.BRIGHT_BLACK,
            "border": Color.BRIGHT_BLACK,
        },
        "dark": {
            "primary": Color.BRIGHT_BLUE,
            "secondary": Color.BRIGHT_CYAN,
            "success": Color.BRIGHT_GREEN,
            "warning": Color.BRIGHT_YELLOW,
            "error": Color.BRIGHT_RED,
            "info": Color.CYAN,
            "muted": Color.WHITE,
            "border": Color.WHITE,
        },
        "light": {
            "primary": Color.BLUE,
            "secondary": Color.CYAN,
            "success": Color.GREEN,
            "warning": Color.YELLOW,
            "error": Color.RED,
            "info": Color.BRIGHT_BLUE,
            "muted": Color.BLACK,
            "border": Color.BLACK,
        },
        "minimal": {
            "primary": Color.WHITE,
            "secondary": Color.WHITE,
            "success": Color.WHITE,
            "warning": Color.WHITE,
            "error": Color.WHITE,
            "info": Color.WHITE,
            "muted": Color.BRIGHT_BLACK,
            "border": Color.BRIGHT_BLACK,
        },
    }
    
    def __init__(self, theme_name: str = "default", use_color: bool = True):
        """Initialize theme.
        
        Args:
            theme_name: Name of the theme to use
            use_color: Whether to use colors (fallback to plain text)
        """
        self.theme_name = theme_name
        self.use_color = use_color
        self._colors = self.THEMES.get(theme_name, self.THEMES["default"])
    
    def get_color(self, role: str) -> Color:
        """Get color for a specific role.
        
        Args:
            role: Color role (primary, secondary, success, etc.)
            
        Returns:
            Color enum value
        """
        return self._colors.get(role, Color.WHITE)
    
    def style(self, text: str, role: str = "primary", bold: bool = False) -> str:
        """Apply theme styling to text.
        
        Args:
            text: Text to style
            role: Color role to apply
            bold: Whether to make text bold
            
        Returns:
            Styled text (or plain text if color disabled)
        """
        if not self.use_color:
            return text
        
        color = self.get_color(role)
        styled = Style.color(text, color)
        
        if bold:
            styled = Style.bold(styled)
        
        return styled
    
    def success(self, text: str) -> str:
        """Style text as success message."""
        return self.style(text, "success")
    
    def error(self, text: str) -> str:
        """Style text as error message."""
        return self.style(text, "error")
    
    def warning(self, text: str) -> str:
        """Style text as warning message."""
        return self.style(text, "warning")
    
    def info(self, text: str) -> str:
        """Style text as info message."""
        return self.style(text, "info")
    
    def muted(self, text: str) -> str:
        """Style text as muted."""
        return self.style(text, "muted")
    
    def primary(self, text: str) -> str:
        """Style text with primary color."""
        return self.style(text, "primary")
    
    def secondary(self, text: str) -> str:
        """Style text with secondary color."""
        return self.style(text, "secondary")
    
    def set_theme(self, theme_name: str) -> None:
        """Change the current theme."""
        self.theme_name = theme_name
        self._colors = self.THEMES.get(theme_name, self.THEMES["default"])
    
    def set_use_color(self, use_color: bool) -> None:
        """Enable or disable color output."""
        self.use_color = use_color


# Global theme instance
_theme: Optional[Theme] = None


def get_theme(theme_name: Optional[str] = None, use_color: Optional[bool] = None) -> Theme:
    """Get the global theme instance.
    
    Args:
        theme_name: Override theme name
        use_color: Override color usage setting
        
    Returns:
        Theme instance
    """
    global _theme
    if _theme is None or theme_name is not None or use_color is not None:
        _theme = Theme(
            theme_name if theme_name is not None else "default",
            use_color if use_color is not None else True
        )
    return _theme