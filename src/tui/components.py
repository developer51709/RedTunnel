"""TUI components for RedTunnel.

Components:
  ProgressBar     - Configurable fill-bar with percentage
  Spinner         - Braille / ASCII animated spinner
  Menu            - Full-width highlighted selection menu
  ScrollableList  - Content list with scroll tracking
  InputField      - Inline text-input widget
  StatusLine      - Padded three-column status row
  Table           - Column-aligned table renderer
  ConfirmationDialog - Yes/No dialog
  Breadcrumbs     - Path display
  NotificationToast - Timed toast messages
"""

import time
import threading
from typing import List, Optional, Callable, Any, Tuple

from .icons import get_icon_set
from .theme import get_theme


# ─── ProgressBar ──────────────────────────────────────────────────────────────

class ProgressBar:
    """Configurable fill-bar with optional percentage label."""

    def __init__(self, width: int = 40, fill: str = "█", empty: str = "░"):
        self.width = width
        self.fill = fill
        self.empty = empty
        self.progress = 0.0

    def update(self, progress: float) -> None:
        self.progress = max(0.0, min(1.0, progress))

    def render(self, show_percentage: bool = True, label: str = "") -> str:
        theme = get_theme()
        filled = int(self.width * self.progress)
        remainder = self.width - filled
        bar_filled = theme.success(self.fill * filled)
        bar_empty = theme.muted(self.empty * remainder)
        bar = f"[{bar_filled}{bar_empty}]"
        if show_percentage:
            pct = f" {self.progress * 100:5.1f}%"
            bar += theme.info(pct)
        if label:
            bar = f"{theme.muted(label)} {bar}"
        return bar


# ─── Spinner ──────────────────────────────────────────────────────────────────

class Spinner:
    """Animated spinner, usable in a background thread."""

    BRAILLE_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    ASCII_FRAMES   = ["-", "\\", "|", "/"]
    DOTS_FRAMES    = ["   ", ".  ", ".. ", "..."]

    def __init__(self, message: str = "Loading…", style: str = "braille",
                 use_ascii: bool = False):
        self.message = message
        if use_ascii:
            self.frames = self.ASCII_FRAMES
        elif style == "dots":
            self.frames = self.DOTS_FRAMES
        else:
            self.frames = self.BRAILLE_FRAMES
        self._idx = 0
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[], None]] = None

    def next_frame(self) -> str:
        theme = get_theme()
        frame = self.frames[self._idx]
        self._idx = (self._idx + 1) % len(self.frames)
        return f"{theme.primary(frame)} {self.message}"

    def reset(self) -> None:
        self._idx = 0

    # ── background animation ──────────────────────────────────────────────────

    def start(self, callback: Callable[[], None], interval: float = 0.1) -> None:
        """Start animating in a background thread, calling *callback* each frame."""
        self._running = True
        self._callback = callback

        def _loop():
            while self._running:
                callback()
                time.sleep(interval)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
            self._thread = None


# ─── Menu ─────────────────────────────────────────────────────────────────────

class Menu:
    """Full-width highlighted selection menu."""

    def __init__(self, title: str, options: List[str],
                 allow_exit: bool = True, width: int = 0):
        """
        Args:
            title:      Displayed above options.
            options:    List of option labels.
            allow_exit: Append an "Exit" entry at the bottom.
            width:      Fixed render width; 0 = auto (longest option + padding).
        """
        self.title = title
        self.options = options
        self.allow_exit = allow_exit
        self.width = width
        self.selected_index = 0
        self._theme = get_theme()
        self._icons = get_icon_set()

    # ── navigation ────────────────────────────────────────────────────────────

    @property
    def _max_index(self) -> int:
        return len(self.options) + (1 if self.allow_exit else 0) - 1

    def next(self) -> None:
        self.selected_index = min(self.selected_index + 1, self._max_index)

    def previous(self) -> None:
        self.selected_index = max(self.selected_index - 1, 0)

    def get_selected(self) -> Optional[str]:
        """Returns None when the Exit entry is selected."""
        if self.allow_exit and self.selected_index == len(self.options):
            return None
        return self.options[self.selected_index]

    def set_selected(self, option: str) -> None:
        """Select by option text."""
        if option in self.options:
            self.selected_index = self.options.index(option)

    # ── rendering ─────────────────────────────────────────────────────────────

    def render(self) -> str:
        theme = get_theme()
        icons = get_icon_set()
        lines: List[str] = []

        # Title
        lines.append(theme.primary(f"  {icons.get('menu')} {self.title}"))
        lines.append(theme.muted("  " + "─" * max(20, len(self.title) + 6)))
        lines.append("")

        all_opts = list(self.options)
        if self.allow_exit:
            all_opts.append("Exit")

        # Calculate render width
        render_w = self.width
        if render_w == 0:
            render_w = max((len(o) for o in all_opts), default=20) + 8

        for i, option in enumerate(all_opts):
            is_selected = i == self.selected_index
            is_exit = self.allow_exit and i == len(self.options)

            # Arrow indicator
            arrow = icons.get("arrow_right") if is_selected else " "

            label = f"  {arrow}  {option}"
            # Pad to full width
            plain_label = f"     {option}"
            pad = render_w - len(plain_label)
            if pad > 0:
                label += " " * pad

            if is_selected:
                label = theme.selected_row(f"  {arrow}  {option}" + " " * max(0, pad))
            elif is_exit:
                label = theme.muted(label)
            else:
                label = "  " + icons.get("radio_unchecked") + f"  {option}"

            lines.append(label)

        return "\n".join(lines)


# ─── ScrollableList ──────────────────────────────────────────────────────────

class ScrollableList:
    """A list of text lines with scroll tracking."""

    def __init__(self, items: List[str], height: int = 10):
        self.items = items
        self.height = height
        self._offset = 0

    def scroll_up(self, n: int = 1) -> None:
        self._offset = max(0, self._offset - n)

    def scroll_down(self, n: int = 1) -> None:
        self._offset = min(max(0, len(self.items) - self.height), self._offset + n)

    def render(self) -> str:
        theme = get_theme()
        visible = self.items[self._offset: self._offset + self.height]
        lines = list(visible)
        # Pad with blank lines
        while len(lines) < self.height:
            lines.append("")
        # Scroll hint
        if len(self.items) > self.height:
            end = self._offset + self.height
            hint = theme.muted(
                f"  ↑↓ scroll  [{self._offset + 1}–{min(end, len(self.items))}/{len(self.items)}]"
            )
            lines.append(hint)
        return "\n".join(lines)


# ─── InputField ───────────────────────────────────────────────────────────────

class InputField:
    """Inline text-input widget (rendered only; actual input via InputHandler.get_line)."""

    def __init__(self, label: str = "", value: str = "",
                 placeholder: str = "", secret: bool = False):
        self.label = label
        self.value = value
        self.placeholder = placeholder
        self.secret = secret

    def render(self, width: int = 40, focused: bool = True) -> str:
        theme = get_theme()
        display = ("*" * len(self.value)) if self.secret else self.value
        if not display and self.placeholder:
            display_str = theme.muted(self.placeholder)
        else:
            display_str = display

        inner = display_str.ljust(width - 2)[:width - 2]
        box = f"[ {inner} ]"

        label_str = f"{theme.info(self.label + ':')} " if self.label else ""
        cursor = theme.primary("▍") if focused else ""
        return f"{label_str}{box}{cursor}"


# ─── StatusLine ───────────────────────────────────────────────────────────────

class StatusLine:
    """Three-column status row (left, center, right)."""

    def __init__(self, left: str = "", center: str = "", right: str = ""):
        self.left = left
        self.center = center
        self.right = right

    def render(self, width: int = 80) -> str:
        theme = get_theme()
        left   = self.left
        center = self.center
        right  = self.right

        used = len(left) + len(center) + len(right)
        space = max(0, width - used)
        left_gap  = space // 2
        right_gap = space - left_gap

        return left + " " * left_gap + center + " " * right_gap + right


# ─── Table ───────────────────────────────────────────────────────────────────

class Table:
    """Column-aligned table renderer."""

    def __init__(self, headers: List[str], align: Optional[List[str]] = None):
        self.headers = headers
        self.align = align or ["left"] * len(headers)
        self.rows: List[List[str]] = []

    def add_row(self, row: List[str]) -> None:
        self.rows.append([str(c) for c in row])

    def render(self) -> str:
        theme = get_theme()
        if not self.headers:
            return ""

        # Column widths
        widths = [len(h) for h in self.headers]
        for row in self.rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(cell))

        def _cell(text: str, w: int, align: str) -> str:
            if align == "right":  return text.rjust(w)
            if align == "center": return text.center(w)
            return text.ljust(w)

        lines: List[str] = []
        header_parts = [theme.bold(_cell(h, w, a))
                        for h, w, a in zip(self.headers, widths, self.align)]
        lines.append(" │ ".join(header_parts))
        lines.append(theme.muted("─┼─".join("─" * w for w in widths)))
        for row in self.rows:
            cells = [_cell(row[i] if i < len(row) else "", widths[i], self.align[i])
                     for i in range(len(self.headers))]
            lines.append(" │ ".join(cells))
        return "\n".join(lines)


# ─── ConfirmationDialog ───────────────────────────────────────────────────────

class ConfirmationDialog:
    """Yes/No confirmation dialog."""

    def __init__(self, message: str, default: bool = False):
        self.message = message
        self.default = default

    def toggle(self) -> None:
        self.default = not self.default

    def get_selection(self) -> bool:
        return self.default

    def render(self) -> str:
        theme = get_theme()
        icons = get_icon_set()

        yes_label = "  Yes  "
        no_label  = "  No   "

        if self.default:
            yes_str = theme.selected_row(yes_label)
            no_str  = f"[ {no_label} ]"
        else:
            yes_str = f"[ {yes_label} ]"
            no_str  = theme.selected_row(no_label)

        return (
            f"  {theme.warning(icons.get('warning'))} {theme.bold(self.message)}\n"
            f"\n"
            f"  {yes_str}    {no_str}\n"
            f"\n"
            f"  {theme.muted('← →  or  h l  to switch,  Enter  to confirm')}"
        )


# ─── Breadcrumbs ──────────────────────────────────────────────────────────────

class Breadcrumbs:
    """Breadcrumb path display."""

    def __init__(self, crumbs: Optional[List[str]] = None):
        self.crumbs: List[str] = crumbs or []

    def push(self, label: str) -> None:
        self.crumbs.append(label)

    def pop(self) -> Optional[str]:
        return self.crumbs.pop() if self.crumbs else None

    def render(self) -> str:
        theme = get_theme()
        icons = get_icon_set()
        if not self.crumbs:
            return ""
        sep = theme.muted(f" {icons.get('arrow_right')} ")
        parts = []
        for i, c in enumerate(self.crumbs):
            if i == len(self.crumbs) - 1:
                parts.append(theme.primary(c))
            else:
                parts.append(theme.muted(c))
        return sep.join(parts)

    def as_list(self) -> List[str]:
        return list(self.crumbs)


# ─── NotificationToast ───────────────────────────────────────────────────────

class NotificationToast:
    """Manages a queue of timed toast messages."""

    def __init__(self, duration: float = 3.0):
        self.duration = duration
        self._message: Optional[str] = None
        self._style: str = "info"
        self._expires_at: float = 0.0

    def show(self, message: str, style: str = "info") -> None:
        self._message = message
        self._style = style
        self._expires_at = time.time() + self.duration

    def get_current(self) -> Tuple[Optional[str], str]:
        """Return (message, style) or (None, 'info') if expired."""
        if self._message and time.time() < self._expires_at:
            return self._message, self._style
        self._message = None
        return None, "info"

    def clear(self) -> None:
        self._message = None
