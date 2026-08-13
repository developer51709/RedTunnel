#!/usr/bin/env python3
"""Main entry point for RedTunnel.

This module provides the main CLI interface and TUI integration
for the RedTunnel tool.
"""

import sys
import argparse
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core import get_platform_info, get_config, Environment
from src.tui import get_theme, get_icon_set, TUIApp, Menu


class RedTunnelApp(TUIApp):
    """Main RedTunnel TUI application."""
    
    def __init__(self):
        """Initialize RedTunnel application."""
        super().__init__("RedTunnel")
        
        # Initialize platform and config
        self.platform_info = get_platform_info()
        self.config = get_config()
        
        # Initialize TUI components with platform settings
        self.theme = get_theme(
            theme_name=self.config.get("ui.theme", "default"),
            use_color=self.config.get("ui.use_color", self.platform_info.supports_color)
        )
        self.icons = get_icon_set(
            use_nerdfont=self.config.get("ui.use_nerdfont", self.platform_info.has_nerdfont)
        )
        
        # Create main menu
        self.main_menu = Menu(
            "Main Menu",
            [
                "Verify Cloudflare Configuration",
                "Run Simulation",
                "View Reports",
                "Settings",
                "Help",
            ],
            allow_exit=True
        )
        
        # Set initial content
        self._show_welcome()
    
    def _show_welcome(self) -> None:
        """Show welcome screen."""
        welcome_text = f"""
{self.icons.get('shield')} Welcome to RedTunnel

{self.theme.info('Platform:')} {self.platform_info.get_platform_name()}
{self.theme.info('Environment:')} {self.config.get_environment().value.upper()}
{self.theme.info('NerdFont:')} {'Enabled' if self.icons.use_nerdfont else 'Disabled (Fallback)'}
{self.theme.info('Color:')} {'Enabled' if self.theme.use_color else 'Disabled'}

{self.theme.muted('RedTunnel is a controlled attack-simulation tool for Cloudflare Tunnels.')}
{self.theme.muted('Use the menu below to navigate the application.')}

{self.main_menu.render()}
"""
        self.renderer.set_content(welcome_text)
        self.renderer.set_status(f"{self.icons.get('info')} Press ↑/↓ to navigate, Enter to select, Q to quit")
    
    def handle_action(self, action: str) -> None:
        """Handle keyboard actions.
        
        Args:
            action: Action name from key bindings
        """
        if action == 'up':
            self.main_menu.previous()
            self._update_menu_display()
        elif action == 'down':
            self.main_menu.next()
            self._update_menu_display()
        elif action == 'enter':
            self._handle_menu_selection()
        elif action == 'quit':
            self.quit()
    
    def _update_menu_display(self) -> None:
        """Update the menu display."""
        welcome_text = f"""
{self.icons.get('shield')} Welcome to RedTunnel

{self.theme.info('Platform:')} {self.platform_info.get_platform_name()}
{self.theme.info('Environment:')} {self.config.get_environment().value.upper()}
{self.theme.info('NerdFont:')} {'Enabled' if self.icons.use_nerdfont else 'Disabled (Fallback)'}
{self.theme.info('Color:')} {'Enabled' if self.theme.use_color else 'Disabled'}

{self.theme.muted('RedTunnel is a controlled attack-simulation tool for Cloudflare Tunnels.')}
{self.theme.muted('Use the menu below to navigate the application.')}

{self.main_menu.render()}
"""
        self.renderer.set_content(welcome_text)
    
    def _handle_menu_selection(self) -> None:
        """Handle menu selection."""
        selection = self.main_menu.get_selected()
        
        if selection is None:
            self.quit()
            return
        
        if selection == "Verify Cloudflare Configuration":
            self._show_verification_screen()
        elif selection == "Run Simulation":
            self._show_simulation_screen()
        elif selection == "View Reports":
            self._show_reports_screen()
        elif selection == "Settings":
            self._show_settings_screen()
        elif selection == "Help":
            self._show_help_screen()
    
    def _show_verification_screen(self) -> None:
        """Show verification screen."""
        try:
            from cloudflare.verify import CloudflareVerifier
            
            verifier = CloudflareVerifier()
            self.renderer.set_content(f"""
{self.icons.get('server')} Cloudflare Verification

{self.theme.info('Verifying Cloudflare configuration...')}
{self.theme.muted('This may take a moment.')}

{self.icons.get('loading')} Checking account access...
{self.icons.get('loading')} Checking zone access...
""")
            self.renderer.display()
            
            # Perform verification
            account_ok = verifier.verify_account()
            zone_ok = verifier.verify_zone()
            
            # Show results
            result_text = f"""
{self.icons.get('server')} Cloudflare Verification Results

{self.theme.success('Account Access:')} {'✓ Valid' if account_ok else '✗ Invalid'}
{self.theme.success('Zone Access:')} {'✓ Valid' if zone_ok else '✗ Invalid'}

{self.theme.info('Overall Status:')} {self.theme.success('PASSED') if (account_ok and zone_ok) else self.theme.error('FAILED')}

{self.theme.muted('Press any key to return to main menu...')}
"""
            self.renderer.set_content(result_text)
            self.renderer.display()
            
            # Wait for key press
            self.input_handler.get_key()
            self._show_welcome()
            
        except Exception as e:
            error_text = f"""
{self.icons.get('error')} Verification Error

{self.theme.error(str(e))}

{self.theme.muted('Press any key to return to main menu...')}
"""
            self.renderer.set_content(error_text)
            self.renderer.display()
            self.input_handler.get_key()
            self._show_welcome()
    
    def _show_simulation_screen(self) -> None:
        """Show simulation screen."""
        self.renderer.set_content(f"""
{self.icons.get('tunnel')} Simulation

{self.theme.warning('Simulation feature is under development.')}
{self.theme.muted('This feature will be available in a future release.')}

{self.theme.muted('Press any key to return to main menu...')}
""")
        self.renderer.display()
        self.input_handler.get_key()
        self._show_welcome()
    
    def _show_reports_screen(self) -> None:
        """Show reports screen."""
        self.renderer.set_content(f"""
{self.icons.get('file')} Reports

{self.theme.warning('Reports feature is under development.')}
{self.theme.muted('This feature will be available in a future release.')}

{self.theme.muted('Press any key to return to main menu...')}
""")
        self.renderer.display()
        self.input_handler.get_key()
        self._show_welcome()
    
    def _show_settings_screen(self) -> None:
        """Show settings screen."""
        settings_text = f"""
{self.icons.get('settings')} Settings

{self.theme.info('Current Configuration:')}
{self.theme.muted('-' * 40)}
{self.theme.info('Environment:')} {self.config.get_environment().value.upper()}
{self.theme.info('Debug Mode:')} {self.config.get('debug', False)}
{self.theme.info('Log Level:')} {self.config.get('log_level', 'INFO')}
{self.theme.info('Use NerdFont:')} {self.config.get('ui.use_nerdfont', True)}
{self.theme.info('Use Color:')} {self.config.get('ui.use_color', True)}
{self.theme.info('Theme:')} {self.config.get('ui.theme', 'default')}

{self.theme.muted('Platform Information:')}
{self.theme.muted('-' * 40)}
{self.theme.info('Platform:')} {self.platform_info.get_platform_name()}
{self.theme.info('Termux:')} {'Yes' if self.platform_info.is_termux else 'No'}
{self.theme.info('NerdFont Available:')} {'Yes' if self.platform_info.has_nerdfont else 'No'}
{self.theme.info('Color Support:')} {'Yes' if self.platform_info.supports_color else 'No'}
{self.theme.info('Unicode Support:')} {'Yes' if self.platform_info.supports_unicode else 'No'}

{self.theme.muted('Press any key to return to main menu...')}
"""
        self.renderer.set_content(settings_text)
        self.renderer.display()
        self.input_handler.get_key()
        self._show_welcome()
    
    def _show_help_screen(self) -> None:
        """Show help screen."""
        help_text = f"""
{self.icons.get('help')} Help

{self.theme.bold('Keyboard Shortcuts:')}
{self.theme.muted('-' * 40)}
{self.icons.get('arrow_up')} / K : Move up
{self.icons.get('arrow_down')} / J : Move down
{self.icons.get('arrow_right')} / L : Select/Confirm
{self.icons.get('arrow_left')} / H : Go back
Q : Quit application

{self.theme.bold('Features:')}
{self.theme.muted('-' * 40)}
{self.icons.get('server')} Cloudflare Configuration Verification
{self.icons.get('tunnel')} Safe Attack Simulation
{self.icons.get('file')} Report Generation
{self.icons.get('settings')} Configuration Management

{self.theme.bold('Platform Support:')}
{self.theme.muted('-' * 40)}
{self.icons.get('server')} Linux
{self.icons.get('server')} macOS
{self.icons.get('server')} Windows
{self.icons.get('server')} Android (Termux)

{self.theme.muted('Press any key to return to main menu...')}
"""
        self.renderer.set_content(help_text)
        self.renderer.display()
        self.input_handler.get_key()
        self._show_welcome()


def run_tui() -> None:
    """Run the TUI application."""
    try:
        app = RedTunnelApp()
        app.run()
    except KeyboardInterrupt:
        print("\nExiting RedTunnel...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def show_platform_info() -> None:
    """Show platform information."""
    platform_info = get_platform_info()
    
    print(f"Platform: {platform_info.get_platform_name()}")
    print(f"Termux: {'Yes' if platform_info.is_termux else 'No'}")
    print(f"NerdFont Available: {'Yes' if platform_info.has_nerdfont else 'No'}")
    print(f"Color Support: {'Yes' if platform_info.supports_color else 'No'}")
    print(f"Unicode Support: {'Yes' if platform_info.supports_unicode else 'No'}")
    print(f"Python Version: {'.'.join(map(str, platform_info.python_version))}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="RedTunnel - Controlled attack-simulation tool for Cloudflare Tunnels"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="RedTunnel v0.1.0"
    )
    parser.add_argument(
        "--platform-info",
        action="store_true",
        help="Show platform information and exit"
    )
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production", "testing"],
        help="Set the environment"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--no-tui",
        action="store_true",
        help="Run in command-line mode without TUI"
    )
    
    args = parser.parse_args()
    
    # Initialize config with overrides
    if args.environment or args.config:
        get_config(config_path=args.config, environment=args.environment)
    
    # Handle platform info flag
    if args.platform_info:
        show_platform_info()
        return
    
    # Run TUI or CLI mode
    if args.no_tui:
        print("CLI mode not yet implemented. Use --help for options.")
        parser.print_help()
    else:
        run_tui()


if __name__ == "__main__":
    main()