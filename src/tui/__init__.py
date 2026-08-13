"""Text User Interface (TUI) framework for RedTunnel.

Primary entry point:
    from src.tui.app import RedTunnelTextualApp

Screens:
    HomeScreen, VerifyScreen, SimulationScreen,
    ReportsScreen, SettingsScreen, HelpScreen, WizardScreen

Legacy helpers (icon/theme/component) are kept for backward compatibility
but the main TUI now uses Textual exclusively.
"""

# ── Textual app & screens ────────────────────────────────────────────────────
from .app import RedTunnelTextualApp
from .screens import (
    HomeScreen,
    VerifyScreen,
    SimulationScreen,
    ReportsScreen,
    SettingsScreen,
    HelpScreen,
    WizardScreen,
)

# ── Legacy helpers (still used by cloudflare/utils layers) ──────────────────
from .icons import IconSet, get_icon_set, get_icon
from .theme import Theme, Color, Style, get_theme

__all__ = [
    # Textual
    "RedTunnelTextualApp",
    "HomeScreen",
    "VerifyScreen",
    "SimulationScreen",
    "ReportsScreen",
    "SettingsScreen",
    "HelpScreen",
    "WizardScreen",
    # Legacy
    "IconSet",
    "get_icon_set",
    "get_icon",
    "Theme",
    "Color",
    "Style",
    "get_theme",
]
