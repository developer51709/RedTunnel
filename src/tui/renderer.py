"""TUI renderer and input handler.

This module provides the main TUI rendering engine and input handling
for interactive terminal interfaces.
"""

import sys
import os
import tty
import termios
from typing import Optional, Callable
from .theme import get_theme
from .icons import get_icon_set


class TUIRenderer:
    """Main TUI rendering engine."""
    
    def __init__(self, title: str = "RedTunnel"):
        """Initialize TUI renderer.
        
        Args:
            title: Application title
        """
        self.title = title
        self.theme = get_theme()
        self.icons = get_icon_set()
        self.content = ""
        self.status_line = ""
        self.clear_screen = True
    
    def set_content(self, content: str) -> None:
        """Set the main content to display.
        
        Args:
            content: Content string
        """
        self.content = content
    
    def set_status(self, status: str) -> None:
        """Set the status line text.
        
        Args:
            status: Status line text
        """
        self.status_line = status
    
    def render(self) -> str:
        """Render the complete TUI.
        
        Returns:
            Complete rendered TUI string
        """
        lines = []
        
        # Clear screen if requested
        if self.clear_screen:
            lines.append("\033[2J\033[H")  # Clear screen and move cursor to top
        
        # Header
        header = self._render_header()
        lines.append(header)
        lines.append(self.theme.muted("─" * len(header)))
        lines.append("")
        
        # Main content
        lines.append(self.content)
        lines.append("")
        
        # Status line
        if self.status_line:
            lines.append(self.theme.muted("─" * 80))
            lines.append(self.status_line)
        
        return "\n".join(lines)
    
    def _render_header(self) -> str:
        """Render the header bar.
        
        Returns:
            Header string
        """
        version = "v0.1.0"
        return f"{self.icons.get('terminal')} {self.theme.bold(self.title)} {self.theme.muted(version)}"
    
    def display(self) -> None:
        """Display the rendered TUI to stdout."""
        output = self.render()
        sys.stdout.write(output)
        sys.stdout.flush()
    
    def clear(self) -> None:
        """Clear the screen."""
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()


class InputHandler:
    """Input handler for interactive TUI."""
    
    def __init__(self):
        """Initialize input handler."""
        self.old_settings = None
    
    def _enable_raw_mode(self) -> None:
        """Enable raw input mode."""
        if sys.stdin.isatty():
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setraw(sys.stdin.fileno())
    
    def _disable_raw_mode(self) -> None:
        """Disable raw input mode."""
        if self.old_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            self.old_settings = None
    
    def get_key(self) -> str:
        """Get a single key press.
        
        Returns:
            Key character
        """
        self._enable_raw_mode()
        try:
            key = sys.stdin.read(1)
            # Handle special keys
            if key == '\x1b':  # Escape sequence
                # Read additional characters
                key += sys.stdin.read(2)
            return key
        finally:
            self._disable_raw_mode()
    
    def get_line(self, prompt: str = "") -> str:
        """Get a line of input.
        
        Args:
            prompt: Prompt to display
            
        Returns:
            Input line
        """
        if prompt:
            sys.stdout.write(prompt)
            sys.stdout.flush()
        
        line = sys.stdin.readline()
        return line.rstrip('\n')
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self._disable_raw_mode()


class KeyBindings:
    """Key binding configuration."""
    
    BINDINGS = {
        # Navigation
        '\x1b[A': 'up',      # Up arrow
        '\x1b[B': 'down',    # Down arrow
        '\x1b[C': 'right',   # Right arrow
        '\x1b[D': 'left',    # Left arrow
        
        # Actions
        '\r': 'enter',       # Enter
        ' ': 'space',        # Space
        '\x03': 'ctrl_c',    # Ctrl+C
        '\x04': 'ctrl_d',    # Ctrl+D
        '\x1b': 'escape',    # Escape
        
        # Alternative bindings (for different terminals)
        'k': 'up',
        'j': 'down',
        'h': 'left',
        'l': 'right',
        'q': 'quit',
    }
    
    @classmethod
    def get_action(cls, key: str) -> Optional[str]:
        """Get action for a key.
        
        Args:
            key: Key string
            
        Returns:
            Action name or None if not bound
        """
        return cls.BINDINGS.get(key)


class TUIApp:
    """Main TUI application class."""
    
    def __init__(self, title: str = "RedTunnel"):
        """Initialize TUI application.
        
        Args:
            title: Application title
        """
        self.renderer = TUIRenderer(title)
        self.input_handler = InputHandler()
        self.running = False
    
    def run(self) -> None:
        """Run the TUI application."""
        self.running = True
        
        try:
            with self.input_handler:
                while self.running:
                    # Render current state
                    self.renderer.display()
                    
                    # Get input
                    key = self.input_handler.get_key()
                    
                    # Handle input
                    action = KeyBindings.get_action(key)
                    if action:
                        self.handle_action(action)
                    else:
                        self.handle_key(key)
                    
                    # Check for quit
                    if action in ('quit', 'ctrl_c'):
                        self.running = False
        
        except KeyboardInterrupt:
            self.running = False
        finally:
            self.renderer.clear()
    
    def handle_action(self, action: str) -> None:
        """Handle a bound action.
        
        Args:
            action: Action name
        """
        # Override in subclass
        pass
    
    def handle_key(self, key: str) -> None:
        """Handle an unbound key.
        
        Args:
            key: Key character
        """
        # Override in subclass
        pass
    
    def quit(self) -> None:
        """Quit the application."""
        self.running = False