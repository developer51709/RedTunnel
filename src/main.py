#!/usr/bin/env python3
"""RedTunnel — main entry point.

Launches the Textual TUI application, or falls back to CLI flags.
"""

from __future__ import annotations

import sys
import argparse
from pathlib import Path

# Make 'src' importable when run as  python src/main.py
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import get_platform_info, get_config


# ═══════════════════════════════════════════════════════════════════════════════
# Textual App
# ═══════════════════════════════════════════════════════════════════════════════

class RedTunnelApp:
    """Thin wrapper that wires together platform info, config, and the Textual app."""

    VERSION = "0.1.0"

    def __init__(self) -> None:
        self.platform_info = get_platform_info()
        self.config = get_config()

    def run(self) -> None:
        from src.tui.app import RedTunnelTextualApp
        tapp = RedTunnelTextualApp(
            platform_info=self.platform_info,
            config=self.config,
        )
        tapp.run()


# ═══════════════════════════════════════════════════════════════════════════════
# Textual application class  (lives here so it can access core objects easily)
# ═══════════════════════════════════════════════════════════════════════════════

# (The actual Textual App class is in src/tui/app.py to keep this file short.)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI helpers
# ═══════════════════════════════════════════════════════════════════════════════

def show_platform_info() -> None:
    p = get_platform_info()
    print(f"Platform:      {p.get_platform_name()}")
    print(f"Termux:        {'Yes' if p.is_termux else 'No'}")
    print(f"NerdFont:      {'Yes' if p.has_nerdfont else 'No'}")
    print(f"Color support: {'Yes' if p.supports_color else 'No'}")
    print(f"Unicode:       {'Yes' if p.supports_unicode else 'No'}")
    print(f"Python:        {'.'.join(str(v) for v in p.python_version)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RedTunnel — Controlled attack-simulation tool for Cloudflare Tunnels"
    )
    parser.add_argument("--version", action="version",
                        version="RedTunnel v0.1.0")
    parser.add_argument("--platform-info", action="store_true",
                        help="Print platform information and exit")
    parser.add_argument("--environment",
                        choices=["development", "staging", "production", "testing"],
                        help="Override the active environment")
    parser.add_argument("--config",
                        help="Path to a configuration file")
    parser.add_argument("--no-tui", action="store_true",
                        help="Run without TUI (not yet implemented)")
    parser.add_argument("--theme",
                        choices=["default", "dark", "light", "minimal"],
                        help="Override the UI theme")

    args = parser.parse_args()

    # Apply overrides before anything else reads config
    if args.environment or args.config:
        get_config(config_path=args.config, environment=args.environment)

    if args.theme:
        cfg = get_config()
        cfg.set("ui.theme", args.theme)

    if args.platform_info:
        show_platform_info()
        return

    if args.no_tui:
        print("CLI mode is not yet implemented. Use --help for available options.")
        parser.print_help()
        return

    try:
        RedTunnelApp().run()
    except KeyboardInterrupt:
        print("\nExiting RedTunnel…")
    except Exception as exc:
        import traceback
        print(f"\nFatal error: {exc}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
