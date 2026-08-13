"""Icon management with NerdFont support and fallback.

This module provides icon glyphs with automatic fallback to standard
ASCII characters when NerdFont is not available.
"""

from typing import Dict, Optional


class IconSet:
    """Icon set with NerdFont and fallback support."""
    
    # NerdFont icons (using standard NerdFont glyphs)
    NERDFONT_ICONS = {
        # Navigation
        "home": "",
        "menu": "",
        "back": "",
        "forward": "",
        "up": "",
        "down": "",
        "left": "",
        "right": "",
        
        # Actions
        "play": "",
        "pause": "",
        "stop": "",
        "refresh": "",
        "save": "",
        "load": "",
        "settings": "",
        "help": "",
        "exit": "",
        
        # Status
        "success": "",
        "error": "",
        "warning": "",
        "info": "",
        "loading": "",
        "pending": "",
        
        # Cloud/Network
        "cloud": "",
        "server": "",
        "database": "",
        "network": "",
        "tunnel": "",
        "shield": "",
        "lock": "",
        "unlock": "",
        
        # File operations
        "file": "",
        "folder": "",
        "search": "",
        "filter": "",
        
        # TUI elements
        "checkbox_checked": "",
        "checkbox_unchecked": "",
        "radio_checked": "",
        "radio_unchecked": "",
        "arrow_right": "",
        "arrow_left": "",
        "arrow_up": "",
        "arrow_down": "",
        "bullet": "",
        "dot": "",
        
        # Tools
        "terminal": "",
        "code": "",
        "bug": "",
        "test": "",
        "build": "",
    }
    
    # ASCII fallback icons
    ASCII_ICONS = {
        # Navigation
        "home": "[H]",
        "menu": "[=]",
        "back": "<-",
        "forward": "->",
        "up": "^",
        "down": "v",
        "left": "<",
        "right": ">",
        
        # Actions
        "play": ">",
        "pause": "||",
        "stop": "[]",
        "refresh": "[R]",
        "save": "[S]",
        "load": "[L]",
        "settings": "[*]",
        "help": "[?]",
        "exit": "[X]",
        
        # Status
        "success": "[OK]",
        "error": "[XX]",
        "warning": "[!]",
        "info": "[i]",
        "loading": "...",
        "pending": "[~]",
        
        # Cloud/Network
        "cloud": "[C]",
        "server": "[S]",
        "database": "[D]",
        "network": "[N]",
        "tunnel": "[T]",
        "shield": "[#]",
        "lock": "[L]",
        "unlock": "[U]",
        
        # File operations
        "file": "[F]",
        "folder": "[/]",
        "search": "[?]",
        "filter": "[F]",
        
        # TUI elements
        "checkbox_checked": "[X]",
        "checkbox_unchecked": "[ ]",
        "radio_checked": "(*)",
        "radio_unchecked": "( )",
        "arrow_right": "->",
        "arrow_left": "<-",
        "arrow_up": "^",
        "arrow_down": "v",
        "bullet": "*",
        "dot": ".",
        
        # Tools
        "terminal": "[$]",
        "code": "[{}]",
        "bug": "[B]",
        "test": "[T]",
        "build": "[B]",
    }
    
    def __init__(self, use_nerdfont: bool = True):
        """Initialize icon set.
        
        Args:
            use_nerdfont: Whether to use NerdFont icons if available
        """
        self.use_nerdfont = use_nerdfont
        self._icons = self._select_icon_set()
    
    def _select_icon_set(self) -> Dict[str, str]:
        """Select appropriate icon set based on availability."""
        if self.use_nerdfont:
            try:
                import nerdfont
                # Try to use nerdfont package
                return self.NERDFONT_ICONS
            except ImportError:
                # Fall back to ASCII if nerdfont not installed
                return self.ASCII_ICONS
        return self.ASCII_ICONS
    
    def get(self, key: str, fallback: Optional[str] = None) -> str:
        """Get an icon by key.
        
        Args:
            key: Icon key
            fallback: Fallback string if key not found
            
        Returns:
            Icon character(s) or fallback
        """
        icon = self._icons.get(key)
        if icon is None:
            return fallback or "?"
        return icon
    
    def __getitem__(self, key: str) -> str:
        """Get icon using bracket notation."""
        return self.get(key)
    
    def set_use_nerdfont(self, use_nerdfont: bool) -> None:
        """Change whether to use NerdFont icons."""
        self.use_nerdfont = use_nerdfont
        self._icons = self._select_icon_set()


# Global icon set instance
_icon_set: Optional[IconSet] = None


def get_icon_set(use_nerdfont: Optional[bool] = None) -> IconSet:
    """Get the global icon set instance.
    
    Args:
        use_nerdfont: Override NerdFont usage setting
        
    Returns:
        IconSet instance
    """
    global _icon_set
    if _icon_set is None or use_nerdfont is not None:
        _icon_set = IconSet(use_nerdfont if use_nerdfont is not None else True)
    return _icon_set


def get_icon(key: str, fallback: Optional[str] = None) -> str:
    """Convenience function to get an icon.
    
    Args:
        key: Icon key
        fallback: Fallback string if key not found
        
    Returns:
        Icon character(s) or fallback
    """
    return get_icon_set().get(key, fallback)