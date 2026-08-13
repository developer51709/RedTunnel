"""TUI renderer and input handler for RedTunnel.

Provides a full-screen terminal renderer with:
- Real terminal width/height detection
- Box-drawing borders (with ASCII fallback)
- Persistent header and footer bars
- Proper screen clearing and cursor control
- Raw-mode keyboard input with escape-sequence parsing
"""

import os
import sys
import tty
import termios
import shutil
import signal
from typing import Optional, Callable, List


# ─── Box-drawing character sets ──────────────────────────────────────────────

BOX_UNICODE = {
    "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
    "h": "═", "v": "║",
    "ml": "╠", "mr": "╣", "mt": "╦", "mb": "╩", "m": "╬",
    "tl_s": "┌", "tr_s": "┐", "bl_s": "└", "br_s": "┘",
    "h_s": "─", "v_s": "│",
}

BOX_ASCII = {
    "tl": "+", "tr": "+", "bl": "+", "br": "+",
    "h": "-", "v": "|",
    "ml": "+", "mr": "+", "mt": "+", "mb": "+", "m": "+",
    "tl_s": "+", "tr_s": "+", "bl_s": "+", "br_s": "+",
    "h_s": "-", "v_s": "|",
}


# ─── ANSI helpers ─────────────────────────────────────────────────────────────

def _ansi(code: str) -> str:
    return f"\033[{code}"


def cursor_to(row: int, col: int) -> str:
    return f"\033[{row};{col}H"


def clear_screen() -> str:
    return "\033[2J\033[H"


def hide_cursor() -> str:
    return "\033[?25l"


def show_cursor() -> str:
    return "\033[?25h"


def clear_line() -> str:
    return "\033[2K"


# ─── Terminal size ─────────────────────────────────────────────────────────────

def get_terminal_size() -> tuple[int, int]:
    """Return (cols, rows) of the current terminal."""
    try:
        size = shutil.get_terminal_size(fallback=(80, 24))
        return size.columns, size.lines
    except Exception:
        return 80, 24


# ─── TUIRenderer ──────────────────────────────────────────────────────────────

class TUIRenderer:
    """Full-screen TUI rendering engine.

    Layout (row numbers are 1-based):
      Row 1          : Header bar
      Row 2          : Top border of content box
      Rows 3…H-3     : Scrollable content area
      Row H-2        : Bottom border of content box
      Row H-1        : Status / navigation bar
      Row H           : Input prompt (shown when active)
    """

    VERSION = "v0.1.0"

    def __init__(self, title: str = "RedTunnel", use_unicode: bool = True):
        self.title = title
        self.use_unicode = use_unicode
        self._box = BOX_UNICODE if use_unicode else BOX_ASCII
        self._content_lines: List[str] = []
        self._status = ""
        self._breadcrumbs: List[str] = []
        self._scroll_offset = 0
        self._notification: Optional[str] = None
        self._notification_style: str = "info"  # info | success | warning | error

        # Register resize handler
        try:
            signal.signal(signal.SIGWINCH, self._on_resize)
        except (AttributeError, OSError):
            pass  # Not available on Windows / some environments

    # ── public API ────────────────────────────────────────────────────────────

    def set_content(self, content: str) -> None:
        """Replace the main content area."""
        self._content_lines = content.splitlines()
        self._scroll_offset = 0

    def set_status(self, status: str) -> None:
        """Set the bottom status / nav bar text."""
        self._status = status

    def set_breadcrumbs(self, crumbs: List[str]) -> None:
        """Set the breadcrumb path shown in the header."""
        self._breadcrumbs = crumbs

    def set_notification(self, message: str, style: str = "info") -> None:
        """Show a one-line notification toast above the status bar."""
        self._notification = message
        self._notification_style = style

    def clear_notification(self) -> None:
        self._notification = None

    def scroll_up(self, lines: int = 1) -> None:
        self._scroll_offset = max(0, self._scroll_offset - lines)

    def scroll_down(self, lines: int = 1) -> None:
        cols, rows = get_terminal_size()
        content_height = self._content_area_height(rows)
        max_offset = max(0, len(self._content_lines) - content_height)
        self._scroll_offset = min(max_offset, self._scroll_offset + lines)

    def display(self) -> None:
        """Render and write the complete TUI frame to stdout."""
        cols, rows = get_terminal_size()
        buf: List[str] = []

        buf.append(hide_cursor())
        buf.append(clear_screen())

        buf.append(self._render_header(cols))
        buf.append(self._render_content_box(cols, rows))
        buf.append(self._render_notification_bar(cols, rows))
        buf.append(self._render_status_bar(cols, rows))

        # Keep cursor off
        buf.append(hide_cursor())

        sys.stdout.write("".join(buf))
        sys.stdout.flush()

    def clear(self) -> None:
        """Clear screen and restore cursor before exit."""
        sys.stdout.write(clear_screen() + show_cursor())
        sys.stdout.flush()

    # ── rendering helpers ─────────────────────────────────────────────────────

    def _render_header(self, cols: int) -> str:
        """Row 1: full-width header bar."""
        from .theme import get_theme
        theme = get_theme()
        box = self._box

        # Left: app name + version
        left = f" {self.title} {self.VERSION}"
        # Right: breadcrumbs
        crumb_str = (" > ".join(self._breadcrumbs)) if self._breadcrumbs else ""
        right = f"{crumb_str} " if crumb_str else ""

        # Fill middle
        gap = cols - len(left) - len(right)
        if gap < 0:
            right = ""
            gap = cols - len(left)
        if gap < 0:
            left = left[:cols]
            gap = 0

        line = left + " " * gap + right
        # Apply header styling (bold primary on colored bg)
        styled = theme.header_bar(line)
        return cursor_to(1, 1) + styled

    def _render_content_box(self, cols: int, rows: int) -> str:
        """Rows 2…H-2: bordered content box with scrollable lines."""
        from .theme import get_theme
        theme = get_theme()
        box = self._box

        content_height = self._content_area_height(rows)
        inner_width = cols - 2  # inside the vertical borders

        lines_buf: List[str] = []

        # ── top border (row 2) ──
        top_border = (box["tl"] + box["h"] * inner_width + box["tr"])
        lines_buf.append(cursor_to(2, 1) + theme.border(top_border))

        # ── content rows (rows 3 … 3+content_height-1) ──
        visible = self._visible_lines(content_height, inner_width)
        for idx, line in enumerate(visible):
            row = 3 + idx
            # Pad / truncate to inner_width (strip ANSI for length calc)
            plain_len = len(self._strip_ansi(line))
            if plain_len < inner_width:
                line = line + " " * (inner_width - plain_len)
            elif plain_len > inner_width:
                line = self._truncate_ansi(line, inner_width)
            lines_buf.append(
                cursor_to(row, 1) + theme.border(box["v"]) + line + theme.border(box["v"])
            )

        # Fill remaining empty rows
        for idx in range(len(visible), content_height):
            row = 3 + idx
            lines_buf.append(
                cursor_to(row, 1)
                + theme.border(box["v"])
                + " " * inner_width
                + theme.border(box["v"])
            )

        # ── scroll indicator ──
        total = len(self._content_lines)
        if total > content_height:
            pct = int(self._scroll_offset / max(1, total - content_height) * 100)
            indicator = f" {self._scroll_offset + 1}-{min(total, self._scroll_offset + content_height)}/{total} ({pct}%) "
            indicator = indicator[:inner_width]
        else:
            indicator = ""

        # ── bottom border (row 3+content_height) ──
        bot_row = 3 + content_height
        if indicator:
            left_fill = (inner_width - len(indicator)) // 2
            right_fill = inner_width - len(indicator) - left_fill
            bot_border = (
                box["bl"]
                + box["h"] * left_fill
                + indicator
                + box["h"] * right_fill
                + box["br"]
            )
        else:
            bot_border = box["bl"] + box["h"] * inner_width + box["br"]
        lines_buf.append(cursor_to(bot_row, 1) + theme.border(bot_border))

        return "".join(lines_buf)

    def _render_notification_bar(self, cols: int, rows: int) -> str:
        """One row above the status bar; shown only when notification is set."""
        if not self._notification:
            return ""
        from .theme import get_theme
        theme = get_theme()
        notif_row = rows - 1
        msg = f" {self._notification} "
        msg = msg[:cols].ljust(cols)
        styled = theme.notification(msg, self._notification_style)
        return cursor_to(notif_row, 1) + styled

    def _render_status_bar(self, cols: int, rows: int) -> str:
        """Bottom row: status / key-hint bar."""
        from .theme import get_theme
        theme = get_theme()
        status = self._status if self._status else "↑/↓ Navigate  Enter Select  ESC Back  Q Quit"
        line = f" {status} "
        line = line[:cols].ljust(cols)
        return cursor_to(rows, 1) + theme.status_bar(line)

    # ── internal helpers ──────────────────────────────────────────────────────

    def _content_area_height(self, rows: int) -> int:
        """Number of usable content rows inside the box."""
        # Header(1) + top-border(1) + bottom-border(1) + notification(1) + status(1) = 5
        return max(1, rows - 5)

    def _visible_lines(self, height: int, width: int) -> List[str]:
        """Return the slice of content lines visible in the scroll window."""
        return self._content_lines[self._scroll_offset: self._scroll_offset + height]

    @staticmethod
    def _strip_ansi(text: str) -> str:
        """Remove ANSI escape codes for length measurement."""
        import re
        return re.sub(r"\033\[[0-9;]*m", "", text)

    @staticmethod
    def _truncate_ansi(text: str, max_len: int) -> str:
        """Truncate visible characters to max_len, preserving ANSI codes."""
        import re
        result = []
        visible = 0
        i = 0
        while i < len(text):
            if text[i] == "\033":
                # Consume the full escape sequence
                j = i + 1
                while j < len(text) and text[j] not in "m":
                    j += 1
                result.append(text[i:j + 1])
                i = j + 1
            else:
                if visible >= max_len:
                    break
                result.append(text[i])
                visible += 1
                i += 1
        return "".join(result)

    def _on_resize(self, signum, frame) -> None:
        """Handle terminal resize."""
        self.display()


# ─── InputHandler ─────────────────────────────────────────────────────────────

class InputHandler:
    """Raw-mode keyboard input with escape-sequence parsing."""

    def __init__(self):
        self._old_settings = None

    def enable_raw(self) -> None:
        if sys.stdin.isatty():
            try:
                self._old_settings = termios.tcgetattr(sys.stdin.fileno())
                tty.setraw(sys.stdin.fileno())
            except termios.error:
                pass

    def disable_raw(self) -> None:
        if self._old_settings is not None:
            try:
                termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, self._old_settings)
            except termios.error:
                pass
            self._old_settings = None

    def get_key(self) -> str:
        """Block until a key is pressed; return the key string."""
        self.enable_raw()
        try:
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                # Try to read more (escape sequences are [ + letter)
                import select
                if select.select([sys.stdin], [], [], 0.05)[0]:
                    ch2 = sys.stdin.read(1)
                    ch += ch2
                    if ch2 == "[":
                        if select.select([sys.stdin], [], [], 0.05)[0]:
                            ch3 = sys.stdin.read(1)
                            ch += ch3
                            # Some terminals send more (e.g. F-keys)
                            if ch3 in "0123456789":
                                if select.select([sys.stdin], [], [], 0.05)[0]:
                                    ch4 = sys.stdin.read(1)
                                    ch += ch4
            return ch
        finally:
            self.disable_raw()

    def get_line(self, prompt: str = "", renderer: Optional["TUIRenderer"] = None,
                 cols: int = 80, row: int = 23) -> str:
        """Read a line of text with a visible prompt drawn at (row, 1).

        If a renderer is provided, the input is drawn inline inside the TUI
        rather than on a bare stdin line.
        """
        sys.stdout.write(show_cursor())
        sys.stdout.flush()
        buf: List[str] = []

        def _redraw():
            display_str = prompt + "".join(buf)
            display_str = display_str[:cols - 1]
            sys.stdout.write(cursor_to(row, 1) + clear_line() + display_str)
            sys.stdout.flush()

        _redraw()
        self.enable_raw()
        try:
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    break
                elif ch in ("\x7f", "\x08"):  # Backspace / DEL
                    if buf:
                        buf.pop()
                        _redraw()
                elif ch == "\x03":  # Ctrl-C
                    raise KeyboardInterrupt
                elif ch == "\x1b":  # ESC – cancel
                    sys.stdout.write(show_cursor())
                    sys.stdout.flush()
                    return ""
                elif ch.isprintable():
                    buf.append(ch)
                    _redraw()
        finally:
            self.disable_raw()

        sys.stdout.write(hide_cursor())
        sys.stdout.flush()
        return "".join(buf)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.disable_raw()
        sys.stdout.write(show_cursor())
        sys.stdout.flush()


# ─── KeyBindings ──────────────────────────────────────────────────────────────

class KeyBindings:
    """Map raw key sequences to named actions."""

    BINDINGS = {
        "\x1b[A": "up",
        "\x1b[B": "down",
        "\x1b[C": "right",
        "\x1b[D": "left",
        "\r":     "enter",
        "\n":     "enter",
        " ":      "space",
        "\x03":   "quit",   # Ctrl-C
        "\x04":   "quit",   # Ctrl-D
        "\x1b":   "escape",
        # VI-style (lower-case only; upper handled separately in main)
        "k":      "up",
        "j":      "down",
        "h":      "left",
        "l":      "right",
        "q":      "quit",
        "Q":      "quit",
        # Page scroll
        "\x1b[5~": "page_up",
        "\x1b[6~": "page_down",
    }

    @classmethod
    def get_action(cls, key: str) -> Optional[str]:
        return cls.BINDINGS.get(key)


# ─── TUIApp ────────────────────────────────────────────────────────────────────

class TUIApp:
    """Base TUI application. Subclass and override handle_action / handle_key."""

    def __init__(self, title: str = "RedTunnel"):
        self.renderer = TUIRenderer(title)
        self.input_handler = InputHandler()
        self.running = False

    def run(self) -> None:
        self.running = True
        try:
            with self.input_handler:
                while self.running:
                    self.renderer.display()
                    key = self.input_handler.get_key()
                    action = KeyBindings.get_action(key)
                    if action == "quit":
                        self.running = False
                    elif action:
                        self.handle_action(action)
                    else:
                        self.handle_key(key)
        except KeyboardInterrupt:
            pass
        finally:
            self.renderer.clear()

    def handle_action(self, action: str) -> None:
        """Override in subclass."""
        pass

    def handle_key(self, key: str) -> None:
        """Override in subclass."""
        pass

    def quit(self) -> None:
        self.running = False
