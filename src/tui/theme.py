"""Theme management for RedTunnel TUI.

Provides ANSI color themes with:
- Foreground + background color pairs
- Full-width selection highlight
- Status badges (success / warning / error / info)
- Header bar, status bar, border, and notification styling
- Plain-text fallback when color is disabled
"""

from enum import Enum
from typing import Optional, Dict


# ─── ANSI primitives ─────────────────────────────────────────────────────────

class _FG:
    """Foreground color codes (text colors)."""
    BLACK          = 30
    RED            = 31
    GREEN          = 32
    YELLOW         = 33
    BLUE           = 34
    MAGENTA        = 35
    CYAN           = 36
    WHITE          = 37
    BRIGHT_BLACK   = 90
    BRIGHT_RED     = 91
    BRIGHT_GREEN   = 92
    BRIGHT_YELLOW  = 93
    BRIGHT_BLUE    = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN    = 96
    BRIGHT_WHITE   = 97
    RESET          = 39


class _BG:
    """Background color codes."""
    BLACK          = 40
    RED            = 41
    GREEN          = 42
    YELLOW         = 43
    BLUE           = 44
    MAGENTA        = 45
    CYAN           = 46
    WHITE          = 47
    BRIGHT_BLACK   = 100
    BRIGHT_RED     = 101
    BRIGHT_GREEN   = 102
    BRIGHT_YELLOW  = 103
    BRIGHT_BLUE    = 104
    BRIGHT_MAGENTA = 105
    BRIGHT_CYAN    = 106
    BRIGHT_WHITE   = 107
    RESET          = 49


RESET_ALL = "\033[0m"


def _esc(*codes: int) -> str:
    return f"\033[{';'.join(str(c) for c in codes)}m"


def _styled(text: str, *codes: int) -> str:
    return f"{_esc(*codes)}{text}{RESET_ALL}"


# ─── Color enum (public, kept for backward compat) ───────────────────────────

class Color(Enum):
    BLACK          = 30
    RED            = 31
    GREEN          = 32
    YELLOW         = 33
    BLUE           = 34
    MAGENTA        = 35
    CYAN           = 36
    WHITE          = 37
    BRIGHT_BLACK   = 90
    BRIGHT_RED     = 91
    BRIGHT_GREEN   = 92
    BRIGHT_YELLOW  = 93
    BRIGHT_BLUE    = 94
    BRIGHT_MAGENTA = 95
    BRIGHT_CYAN    = 96
    BRIGHT_WHITE   = 97
    RESET          = 0


class Style:
    """Static helpers (backward-compat shim)."""
    BOLD      = "\033[1m"
    DIM       = "\033[2m"
    ITALIC    = "\033[3m"
    UNDERLINE = "\033[4m"
    RESET     = RESET_ALL

    @staticmethod
    def color(text: str, color: Color) -> str:
        return _styled(text, color.value)

    @staticmethod
    def bold(text: str) -> str:
        return _styled(text, 1)

    @staticmethod
    def dim(text: str) -> str:
        return _styled(text, 2)

    @staticmethod
    def underline(text: str) -> str:
        return _styled(text, 4)


# ─── Theme definitions ────────────────────────────────────────────────────────

# Each theme entry:
#   role → (fg_code, bg_code, bold)
# bg_code = None means default terminal background
_THEMES: Dict[str, Dict] = {
    "default": {
        "primary":    (_FG.BRIGHT_CYAN,    None,           True),
        "secondary":  (_FG.CYAN,           None,           False),
        "success":    (_FG.BRIGHT_GREEN,   None,           False),
        "warning":    (_FG.BRIGHT_YELLOW,  None,           False),
        "error":      (_FG.BRIGHT_RED,     None,           False),
        "info":       (_FG.BRIGHT_BLUE,    None,           False),
        "muted":      (_FG.BRIGHT_BLACK,   None,           False),
        "border":     (_FG.BRIGHT_BLACK,   None,           False),
        # Full-row UI elements
        "header_bar": (_FG.BLACK,          _BG.BRIGHT_CYAN,   True),
        "status_bar": (_FG.BLACK,          _BG.BRIGHT_BLACK,  False),
        "selected":   (_FG.BLACK,          _BG.BRIGHT_CYAN,   True),
        # Notifications (toast)
        "notif_info":    (_FG.BLACK, _BG.BRIGHT_BLUE,   False),
        "notif_success": (_FG.BLACK, _BG.BRIGHT_GREEN,  False),
        "notif_warning": (_FG.BLACK, _BG.BRIGHT_YELLOW, False),
        "notif_error":   (_FG.WHITE, _BG.RED,           True),
    },
    "dark": {
        "primary":    (_FG.BRIGHT_MAGENTA, None,          True),
        "secondary":  (_FG.MAGENTA,        None,          False),
        "success":    (_FG.BRIGHT_GREEN,   None,          False),
        "warning":    (_FG.BRIGHT_YELLOW,  None,          False),
        "error":      (_FG.BRIGHT_RED,     None,          False),
        "info":       (_FG.BRIGHT_CYAN,    None,          False),
        "muted":      (_FG.WHITE,          None,          False),
        "border":     (_FG.BRIGHT_BLACK,   None,          False),
        "header_bar": (_FG.WHITE,          _BG.MAGENTA,   True),
        "status_bar": (_FG.BRIGHT_WHITE,   _BG.BLACK,     False),
        "selected":   (_FG.WHITE,          _BG.MAGENTA,   True),
        "notif_info":    (_FG.WHITE, _BG.BRIGHT_BLUE,    False),
        "notif_success": (_FG.BLACK, _BG.BRIGHT_GREEN,   False),
        "notif_warning": (_FG.BLACK, _BG.BRIGHT_YELLOW,  False),
        "notif_error":   (_FG.WHITE, _BG.RED,            True),
    },
    "light": {
        "primary":    (_FG.BLUE,    None, True),
        "secondary":  (_FG.CYAN,    None, False),
        "success":    (_FG.GREEN,   None, False),
        "warning":    (_FG.YELLOW,  None, False),
        "error":      (_FG.RED,     None, False),
        "info":       (_FG.BLUE,    None, False),
        "muted":      (_FG.BLACK,   None, False),
        "border":     (_FG.BLACK,   None, False),
        "header_bar": (_FG.WHITE,   _BG.BLUE,  True),
        "status_bar": (_FG.WHITE,   _BG.BLACK, False),
        "selected":   (_FG.WHITE,   _BG.BLUE,  True),
        "notif_info":    (_FG.WHITE, _BG.BLUE,           False),
        "notif_success": (_FG.BLACK, _BG.GREEN,          False),
        "notif_warning": (_FG.BLACK, _BG.YELLOW,         False),
        "notif_error":   (_FG.WHITE, _BG.RED,            True),
    },
    "minimal": {
        "primary":    (_FG.WHITE,        None, True),
        "secondary":  (_FG.WHITE,        None, False),
        "success":    (_FG.BRIGHT_WHITE, None, False),
        "warning":    (_FG.BRIGHT_WHITE, None, False),
        "error":      (_FG.BRIGHT_WHITE, None, True),
        "info":       (_FG.BRIGHT_WHITE, None, False),
        "muted":      (_FG.BRIGHT_BLACK, None, False),
        "border":     (_FG.BRIGHT_BLACK, None, False),
        "header_bar": (_FG.BLACK,        _BG.WHITE,       True),
        "status_bar": (_FG.WHITE,        _BG.BRIGHT_BLACK, False),
        "selected":   (_FG.BLACK,        _BG.WHITE,       True),
        "notif_info":    (_FG.BLACK, _BG.WHITE,           False),
        "notif_success": (_FG.BLACK, _BG.WHITE,           False),
        "notif_warning": (_FG.BLACK, _BG.WHITE,           False),
        "notif_error":   (_FG.WHITE, _BG.BRIGHT_BLACK,    True),
    },
}


# ─── Theme class ──────────────────────────────────────────────────────────────

class Theme:
    """Apply color/styling to text based on role."""

    def __init__(self, theme_name: str = "default", use_color: bool = True):
        self.theme_name = theme_name
        self.use_color = use_color
        self._palette = _THEMES.get(theme_name, _THEMES["default"])

    # ── core styler ───────────────────────────────────────────────────────────

    def _apply(self, text: str, role: str) -> str:
        if not self.use_color:
            return text
        entry = self._palette.get(role)
        if entry is None:
            return text
        fg, bg, bold = entry
        codes = []
        if bold:
            codes.append(1)
        if fg is not None:
            codes.append(fg)
        if bg is not None:
            codes.append(bg)
        if not codes:
            return text
        return _styled(text, *codes)

    # ── semantic helpers ──────────────────────────────────────────────────────

    def style(self, text: str, role: str = "primary", bold: bool = False) -> str:
        result = self._apply(text, role)
        if bold and self.use_color and not self._palette.get(role, (None, None, False))[2]:
            result = _styled(result, 1)
        return result

    def primary(self, text: str) -> str:   return self._apply(text, "primary")
    def secondary(self, text: str) -> str: return self._apply(text, "secondary")
    def success(self, text: str) -> str:   return self._apply(text, "success")
    def warning(self, text: str) -> str:   return self._apply(text, "warning")
    def error(self, text: str) -> str:     return self._apply(text, "error")
    def info(self, text: str) -> str:      return self._apply(text, "info")
    def muted(self, text: str) -> str:     return self._apply(text, "muted")
    def border(self, text: str) -> str:    return self._apply(text, "border")

    def bold(self, text: str) -> str:
        if not self.use_color:
            return text
        return _styled(text, 1)

    def dim(self, text: str) -> str:
        if not self.use_color:
            return text
        return _styled(text, 2)

    def underline(self, text: str) -> str:
        if not self.use_color:
            return text
        return _styled(text, 4)

    # ── full-row UI elements ───────────────────────────────────────────────────

    def header_bar(self, text: str) -> str:
        return self._apply(text, "header_bar")

    def status_bar(self, text: str) -> str:
        return self._apply(text, "status_bar")

    def selected_row(self, text: str) -> str:
        """Highlight a full-width selected menu row."""
        return self._apply(text, "selected")

    def notification(self, text: str, style: str = "info") -> str:
        """Style a notification toast bar."""
        role = f"notif_{style}"
        return self._apply(text, role)

    # ── status badges ──────────────────────────────────────────────────────────

    def badge(self, text: str, style: str = "info") -> str:
        """Return a styled inline badge like  [ OK ] ."""
        label = f" {text} "
        return self._apply(label, style)

    def badge_success(self, text: str = "OK")      -> str: return self.badge(text, "success")
    def badge_warning(self, text: str = "WARN")    -> str: return self.badge(text, "warning")
    def badge_error(self, text: str = "FAIL")      -> str: return self.badge(text, "error")
    def badge_info(self, text: str = "INFO")       -> str: return self.badge(text, "info")

    # ── convenience ────────────────────────────────────────────────────────────

    def get_color(self, role: str) -> Color:
        """Backward-compat: return Color enum for role."""
        entry = self._palette.get(role)
        if entry:
            try:
                return Color(entry[0])
            except ValueError:
                pass
        return Color.WHITE

    def set_theme(self, theme_name: str) -> None:
        self.theme_name = theme_name
        self._palette = _THEMES.get(theme_name, _THEMES["default"])

    def set_use_color(self, use_color: bool) -> None:
        self.use_color = use_color


# ─── Singleton ────────────────────────────────────────────────────────────────

_theme: Optional[Theme] = None


def get_theme(
    theme_name: Optional[str] = None,
    use_color: Optional[bool] = None,
) -> Theme:
    """Return (and optionally reconfigure) the global Theme instance."""
    global _theme
    if _theme is None or theme_name is not None or use_color is not None:
        _theme = Theme(
            theme_name if theme_name is not None else "default",
            use_color  if use_color  is not None else True,
        )
    return _theme
