"""TUI components for RedTunnel.

This module provides reusable text-based UI components that work
with the icon and theme systems.
"""

from typing import List, Optional, Callable, Any
from .icons import get_icon_set
from .theme import get_theme


class ProgressBar:
    """Text-based progress bar."""
    
    def __init__(self, width: int = 40, character: str = "="):
        """Initialize progress bar.
        
        Args:
            width: Width of the progress bar in characters
            character: Character to use for the filled portion
        """
        self.width = width
        self.character = character
        self.progress = 0.0
    
    def update(self, progress: float) -> None:
        """Update progress.
        
        Args:
            progress: Progress value between 0.0 and 1.0
        """
        self.progress = max(0.0, min(1.0, progress))
    
    def render(self, show_percentage: bool = True) -> str:
        """Render the progress bar.
        
        Args:
            show_percentage: Whether to show percentage
            
        Returns:
            Rendered progress bar string
        """
        filled = int(self.width * self.progress)
        empty = self.width - filled
        
        bar = f"[{self.character * filled}{' ' * empty}]"
        
        if show_percentage:
            bar += f" {self.progress * 100:.1f}%"
        
        return bar


class Spinner:
    """Loading spinner animation."""
    
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    ASCII_FRAMES = ["-", "\\", "|", "/"]
    
    def __init__(self, message: str = "Loading", use_ascii: bool = False):
        """Initialize spinner.
        
        Args:
            message: Message to display
            use_ascii: Whether to use ASCII frames instead of Unicode
        """
        self.message = message
        self.use_ascii = use_ascii
        self.frame_index = 0
        self.frames = self.ASCII_FRAMES if use_ascii else self.FRAMES
    
    def next_frame(self) -> str:
        """Get next animation frame.
        
        Returns:
            Current frame string
        """
        frame = self.frames[self.frame_index]
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        return f"{frame} {self.message}"
    
    def reset(self) -> None:
        """Reset spinner to initial state."""
        self.frame_index = 0


class Menu:
    """Interactive menu component."""
    
    def __init__(self, title: str, options: List[str], allow_exit: bool = True):
        """Initialize menu.
        
        Args:
            title: Menu title
            options: List of menu options
            allow_exit: Whether to add an exit option
        """
        self.title = title
        self.options = options
        self.allow_exit = allow_exit
        self.selected_index = 0
        self.theme = get_theme()
        self.icons = get_icon_set()
    
    def render(self) -> str:
        """Render the menu.
        
        Returns:
            Rendered menu string
        """
        lines = []
        
        # Title
        lines.append(self.theme.primary(f"{self.icons.get('menu')} {self.title}"))
        lines.append("")
        
        # Options
        for i, option in enumerate(self.options):
            prefix = self.icons.get("radio_checked") if i == self.selected_index else self.icons.get("radio_unchecked")
            if i == self.selected_index:
                lines.append(f"{prefix} {self.theme.bold(option)}")
            else:
                lines.append(f"{prefix} {option}")
        
        # Exit option
        if self.allow_exit:
            lines.append("")
            exit_prefix = self.icons.get("radio_checked") if self.selected_index == len(self.options) else self.icons.get("radio_unchecked")
            lines.append(f"{exit_prefix} {self.theme.muted('Exit')}")
        
        return "\n".join(lines)
    
    def next(self) -> None:
        """Move selection to next option."""
        max_index = len(self.options) - (0 if self.allow_exit else 1)
        self.selected_index = min(self.selected_index + 1, max_index)
    
    def previous(self) -> None:
        """Move selection to previous option."""
        self.selected_index = max(self.selected_index - 1, 0)
    
    def get_selected(self) -> Optional[str]:
        """Get currently selected option.
        
        Returns:
            Selected option text or None if exit selected
        """
        if self.allow_exit and self.selected_index == len(self.options):
            return None
        return self.options[self.selected_index]


class StatusLine:
    """Status line component for displaying information."""
    
    def __init__(self, left: str = "", center: str = "", right: str = ""):
        """Initialize status line.
        
        Args:
            left: Left-aligned text
            center: Center-aligned text
            right: Right-aligned text
        """
        self.left = left
        self.center = center
        self.right = right
        self.theme = get_theme()
        self.icons = get_icon_set()
    
    def render(self, width: int = 80) -> str:
        """Render the status line.
        
        Args:
            width: Total width of the status line
            
        Returns:
            Rendered status line string
        """
        # Calculate available space
        left_len = len(self.left)
        right_len = len(self.right)
        center_space = width - left_len - right_len - 4  # 4 for padding
        
        # Truncate center if necessary
        if center_space > 0:
            center = self.center[:center_space]
            # Pad center to be centered
            padding = (center_space - len(center)) // 2
            center = " " * padding + center + " " * (center_space - padding - len(center))
        else:
            center = ""
        
        return f"{self.left} {center} {self.right}"


class Table:
    """Simple text table component."""
    
    def __init__(self, headers: List[str], align: Optional[List[str]] = None):
        """Initialize table.
        
        Args:
            headers: Column headers
            align: List of alignments ('left', 'center', 'right')
        """
        self.headers = headers
        self.align = align or ['left'] * len(headers)
        self.rows: List[List[str]] = []
        self.theme = get_theme()
    
    def add_row(self, row: List[str]) -> None:
        """Add a row to the table.
        
        Args:
            row: List of cell values
        """
        self.rows.append(row)
    
    def _calculate_column_widths(self) -> List[int]:
        """Calculate the width of each column."""
        widths = [len(header) for header in self.headers]
        
        for row in self.rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
        
        return widths
    
    def _align_cell(self, cell: str, width: int, align: str) -> str:
        """Align a cell within its column width.
        
        Args:
            cell: Cell content
            width: Column width
            align: Alignment type
            
        Returns:
            Aligned cell string
        """
        cell = str(cell)
        if align == 'center':
            return cell.center(width)
        elif align == 'right':
            return cell.rjust(width)
        else:  # left
            return cell.ljust(width)
    
    def render(self) -> str:
        """Render the table.
        
        Returns:
            Rendered table string
        """
        if not self.headers:
            return ""
        
        widths = self._calculate_column_widths()
        lines = []
        
        # Header
        header_cells = [
            self.theme.bold(self._align_cell(header, width, align))
            for header, width, align in zip(self.headers, widths, self.align)
        ]
        lines.append(" | ".join(header_cells))
        
        # Separator
        separator = "-+-".join(["-" * width for width in widths])
        lines.append(self.theme.muted(separator))
        
        # Rows
        for row in self.rows:
            cells = [
                self._align_cell(str(cell), widths[i], self.align[i])
                for i, cell in enumerate(row) if i < len(widths)
            ]
            lines.append(" | ".join(cells))
        
        return "\n".join(lines)


class ConfirmationDialog:
    """Yes/No confirmation dialog."""
    
    def __init__(self, message: str, default: bool = False):
        """Initialize confirmation dialog.
        
        Args:
            message: Confirmation message
            default: Default selection (True for Yes, False for No)
        """
        self.message = message
        self.default = default
        self.theme = get_theme()
        self.icons = get_icon_set()
    
    def render(self) -> str:
        """Render the confirmation dialog.
        
        Returns:
            Rendered dialog string
        """
        yes_selected = self.default
        no_selected = not self.default
        
        yes_str = f"[{self.icons.get('checkbox_checked')} Yes]" if yes_selected else f"[{self.icons.get('checkbox_unchecked')} Yes]"
        no_str = f"[{self.icons.get('checkbox_checked')} No]" if no_selected else f"[{self.icons.get('checkbox_unchecked')} No]"
        
        if yes_selected:
            yes_str = self.theme.bold(yes_str)
        else:
            no_str = self.theme.bold(no_str)
        
        return f"{self.icons.get('info')} {self.message}\n{yes_str}  {no_str}"
    
    def toggle(self) -> None:
        """Toggle selection."""
        self.default = not self.default
    
    def get_selection(self) -> bool:
        """Get current selection.
        
        Returns:
            True if Yes selected, False if No selected
        """
        return self.default