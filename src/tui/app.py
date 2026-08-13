"""Textual application class for RedTunnel.

RedTunnelTextualApp is the root Textual App.  It:
  - Loads the CSS stylesheet
  - Holds shared state (platform_info, config)
  - Decides whether to start on WizardScreen or HomeScreen
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import App, ComposeResult
from textual.binding import Binding

if TYPE_CHECKING:
    from src.core.platform import PlatformInfo
    from src.core.environment import EnvironmentConfig


_CSS_PATH = Path(__file__).parent / "app.tcss"


class RedTunnelTextualApp(App):
    """Root Textual application."""

    CSS_PATH = _CSS_PATH
    TITLE = "RedTunnel"
    SUB_TITLE = "Cloudflare Tunnel Attack Simulation"

    # App-level bindings (available on every screen)
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=False),
    ]

    def __init__(
        self,
        platform_info: "PlatformInfo",
        config: "EnvironmentConfig",
    ) -> None:
        super().__init__()
        self.platform_info = platform_info
        self.config = config

    def on_mount(self) -> None:
        from src.tui.screens import HomeScreen, WizardScreen

        # If credentials are missing, show the wizard first
        if not self.config.get("cloudflare.api_token", ""):
            self.push_screen(WizardScreen())
        else:
            self.push_screen(HomeScreen())
