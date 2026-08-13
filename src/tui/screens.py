"""Textual screens for RedTunnel.

Screens:
    HomeScreen        – Main menu
    VerifyScreen      – Live Cloudflare credential verification
    SimulationScreen  – Simulation (placeholder)
    ReportsScreen     – Reports (placeholder)
    SettingsScreen    – Interactive settings editor
    HelpScreen        – Keyboard shortcuts & feature overview
    WizardScreen      – First-run configuration wizard
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Log,
    Markdown,
    ProgressBar,
    Rule,
    Static,
    Switch,
    Select,
)

if TYPE_CHECKING:
    from .app import RedTunnelApp


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _badge(text: str, kind: str = "info") -> str:
    """Return a Rich-markup badge string."""
    colours = {
        "success": ("green",  "dark_green"),
        "warning": ("yellow", "dark_goldenrod"),
        "error":   ("red",    "dark_red"),
        "info":    ("cyan",   "dark_cyan"),
    }
    fg, bg = colours.get(kind, ("cyan", "dark_cyan"))
    return f"[bold {fg} on {bg}] {text} [/]"


# ═══════════════════════════════════════════════════════════════════════════════
# HomeScreen
# ═══════════════════════════════════════════════════════════════════════════════

NAV_ITEMS = [
    ("verify",     "󰒃  Verify Cloudflare",   "Validate API credentials and zone ownership"),
    ("simulation", "󰒆  Run Simulation",       "Launch a compliant traffic simulation"),
    ("reports",    "󰈙  View Reports",         "Browse past simulation reports"),
    ("settings",   "󰒓  Settings",             "Edit configuration interactively"),
    ("help",       "󰋗  Help",                 "Keyboard shortcuts and feature overview"),
]


class HomeScreen(Screen):
    """Main menu / home screen."""

    BINDINGS = [
        Binding("q", "quit",              "Quit",     show=True),
        Binding("1", "nav_verify",        "Verify",   show=False),
        Binding("2", "nav_simulation",    "Simulate", show=False),
        Binding("3", "nav_reports",       "Reports",  show=False),
        Binding("4", "nav_settings",      "Settings", show=False),
        Binding("5", "nav_help",          "Help",     show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        app: RedTunnelApp = self.app  # type: ignore[assignment]
        pi = app.platform_info
        cfg = app.config

        env = cfg.get_environment().value.upper()
        env_badge = _badge(env, "error" if env == "PRODUCTION"
                           else "success" if env == "DEVELOPMENT"
                           else "warning")

        with ScrollableContainer(id="content"):
            yield Static(
                f"[bold cyan]󰒃  RedTunnel[/]  [dim]v0.1.0[/]  {env_badge}",
                id="home-banner",
            )
            yield Static(
                "[dim]Controlled attack-simulation for Cloudflare Tunnels.[/]",
                id="home-subtitle",
            )
            yield Rule()

            # Info row
            yield Static(
                f"[dim]Platform:[/] [cyan]{pi.get_platform_name()}[/]   "
                f"[dim]Python:[/] [cyan]{'.'.join(str(v) for v in pi.python_version)}[/]   "
                f"[dim]NerdFont:[/] [cyan]{'Yes' if pi.has_nerdfont else 'No'}[/]"
            )
            yield Rule()

            yield Label("[bold]Select an option:[/]")
            with Vertical(id="menu-container"):
                for key, label, tooltip in NAV_ITEMS:
                    btn = Button(label, id=f"btn-{key}", classes="menu-button")
                    btn.tooltip = tooltip
                    yield btn

        yield Footer()

    # ── button handlers ───────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed) -> None:
        mapping = {
            "btn-verify":     "verify",
            "btn-simulation": "simulation",
            "btn-reports":    "reports",
            "btn-settings":   "settings",
            "btn-help":       "help",
        }
        dest = mapping.get(event.button.id, "")
        if dest:
            self._navigate(dest)

    def _navigate(self, dest: str) -> None:
        screen_map = {
            "verify":     VerifyScreen,
            "simulation": SimulationScreen,
            "reports":    ReportsScreen,
            "settings":   SettingsScreen,
            "help":       HelpScreen,
        }
        cls = screen_map.get(dest)
        if cls:
            self.app.push_screen(cls())

    # ── key actions ───────────────────────────────────────────────────────────

    def action_quit(self) -> None:
        self.app.exit()

    def action_nav_verify(self)     -> None: self._navigate("verify")
    def action_nav_simulation(self) -> None: self._navigate("simulation")
    def action_nav_reports(self)    -> None: self._navigate("reports")
    def action_nav_settings(self)   -> None: self._navigate("settings")
    def action_nav_help(self)       -> None: self._navigate("help")


# ═══════════════════════════════════════════════════════════════════════════════
# VerifyScreen
# ═══════════════════════════════════════════════════════════════════════════════

class VerifyScreen(Screen):
    """Live Cloudflare credential + zone verification."""

    BINDINGS = [
        Binding("escape", "back", "Back", show=True),
        Binding("r",      "run",  "Re-run", show=True),
    ]

    # reactive flags
    _running: reactive[bool]  = reactive(False)
    _done:    reactive[bool]  = reactive(False)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="content"):
            yield Static("󰒃  Cloudflare Verification", classes="screen-title")
            yield ProgressBar(id="verify-progress", total=100, show_eta=False)
            yield Log(id="verify-log", auto_scroll=True)

            with Vertical(id="verify-results"):
                yield Static("", id="result-account")
                yield Static("", id="result-zone")
                yield Rule()
                yield Static("", id="result-overall")
        yield Footer()

    def on_mount(self) -> None:
        self._start_verification()

    def action_back(self) -> None:
        self.app.pop_screen()

    def action_run(self) -> None:
        log = self.query_one("#verify-log", Log)
        log.clear()
        results = self.query_one("#verify-results")
        results.remove_class("--visible")
        self._start_verification()

    @work(exclusive=True, thread=True)
    def _start_verification(self) -> None:
        """Run verification in a worker thread so the UI stays responsive."""
        import time
        log: Log = self.app.query_one("#verify-log", Log)  # type: ignore[arg-type]
        prog: ProgressBar = self.app.query_one("#verify-progress", ProgressBar)  # type: ignore[arg-type]

        def _log(msg: str) -> None:
            self.call_from_thread(log.write_line, msg)

        def _progress(pct: int) -> None:
            self.call_from_thread(prog.update, progress=pct)

        try:
            _log("Connecting to Cloudflare API…")
            _progress(10)
            time.sleep(0.3)

            from src.cloudflare.verify import CloudflareVerifier
            verifier = CloudflareVerifier()

            _log("Checking account access…")
            _progress(30)
            acct_ok = verifier.verify_account()
            acct_info = verifier.get_account_info() if acct_ok else None

            if acct_ok:
                name = (acct_info or {}).get("name", "")
                _log(f"  ✓ Account access confirmed{' — ' + name if name else ''}")
            else:
                _log("  ✗ Account access failed — check api_token and account_id")
            _progress(55)

            _log("Checking zone access…")
            zone_ok = verifier.verify_zone()
            zone_info = verifier.get_zone_info() if zone_ok else None

            if zone_ok:
                domain = (zone_info or {}).get("name", "")
                status = (zone_info or {}).get("status", "")
                _log(f"  ✓ Zone access confirmed{' — ' + domain if domain else ''}"
                     f"{' (' + status + ')' if status else ''}")
            else:
                _log("  ✗ Zone access failed — check zone_id")
            _progress(85)

            _log("Finalising…")
            time.sleep(0.2)
            _progress(100)
            _log("Done.")

            self.call_from_thread(
                self._show_results, acct_ok, zone_ok, acct_info, zone_info
            )

        except Exception as exc:
            _log(f"  ✗ Error: {exc}")
            _log("")
            _log("Ensure credentials are set in config/settings.yml")
            _log("or via REDTUNNEL_CF_* environment variables.")
            _progress(100)

    def _show_results(self, acct_ok: bool, zone_ok: bool,
                      acct_info: dict | None, zone_info: dict | None) -> None:
        results = self.query_one("#verify-results")
        results.add_class("--visible")

        def _tick(ok: bool) -> str:
            return _badge("PASS", "success") if ok else _badge("FAIL", "error")

        acct_name = (acct_info or {}).get("name", "")
        zone_name = (zone_info or {}).get("name", "")

        self.query_one("#result-account", Static).update(
            f"[dim]Account:[/]  {_tick(acct_ok)}"
            + (f"  [dim]{acct_name}[/]" if acct_name else "")
        )
        self.query_one("#result-zone", Static).update(
            f"[dim]Zone:   [/]  {_tick(zone_ok)}"
            + (f"  [dim]{zone_name}[/]" if zone_name else "")
        )

        overall = acct_ok and zone_ok
        if overall:
            self.query_one("#result-overall", Static).update(
                "[bold green]✓  All checks passed — ready to simulate![/]"
            )
            self.notify("Verification passed!", severity="information")
        else:
            self.query_one("#result-overall", Static).update(
                "[bold red]✗  Some checks failed — review your credentials.[/]"
            )
            self.notify("Verification failed — check credentials.", severity="error")


# ═══════════════════════════════════════════════════════════════════════════════
# SimulationScreen
# ═══════════════════════════════════════════════════════════════════════════════

class SimulationScreen(Screen):
    """Simulation screen (placeholder for future engine)."""

    BINDINGS = [Binding("escape", "back", "Back", show=True)]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="content"):
            yield Static("󰒆  Run Simulation", classes="screen-title")
            yield Static("[yellow]⚠  Simulation engine is under development.[/]")
            yield Rule()
            yield Markdown("""
This module will allow safe, Cloudflare-compliant traffic simulation
once your domain ownership has been verified.

**Planned capabilities:**

- Configurable request patterns (GET / POST / HEAD)
- Rate-limited bursts with adjustable concurrency
- Header and path variation
- Real-time request counter and latency histogram
- Automatic stop conditions (max requests / time limit)

Run **Verify Cloudflare** first to confirm your credentials are valid
before simulation becomes available.
""")
        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()


# ═══════════════════════════════════════════════════════════════════════════════
# ReportsScreen
# ═══════════════════════════════════════════════════════════════════════════════

class ReportsScreen(Screen):
    """Reports screen (placeholder)."""

    BINDINGS = [Binding("escape", "back", "Back", show=True)]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="content"):
            yield Static("󰈙  Reports", classes="screen-title")
            yield Static("[yellow]⚠  Report generation is under development.[/]")
            yield Rule()
            yield Markdown("""
Past simulation reports will be listed here once the simulation engine
is complete.

**Planned report features:**

- Per-run summary (requests sent, errors, latency p50/p95/p99)
- Timeline chart of request rate
- Comparison between runs
- Export to JSON / CSV / Markdown
""")
        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()


# ═══════════════════════════════════════════════════════════════════════════════
# SettingsScreen
# ═══════════════════════════════════════════════════════════════════════════════

_THEME_OPTIONS = [
    ("Default", "default"),
    ("Dark",    "dark"),
    ("Light",   "light"),
    ("Minimal", "minimal"),
]

_ENV_OPTIONS = [
    ("Development", "development"),
    ("Staging",     "staging"),
    ("Production",  "production"),
    ("Testing",     "testing"),
]

_LOG_OPTIONS = [
    ("DEBUG",   "DEBUG"),
    ("INFO",    "INFO"),
    ("WARNING", "WARNING"),
    ("ERROR",   "ERROR"),
]


class SettingsScreen(Screen):
    """Interactive settings editor."""

    BINDINGS = [
        Binding("escape", "back",  "Back",         show=True),
        Binding("ctrl+s", "save",  "Save & Apply", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        app: RedTunnelApp = self.app  # type: ignore[assignment]
        cfg = app.config

        with ScrollableContainer(id="content"):
            yield Static("󰒓  Settings", classes="screen-title")
            yield Static("[dim]Changes apply immediately. Press Ctrl+S to save to disk.[/]")
            yield Rule()

            # ── Cloudflare ────────────────────────────────────────────────────
            yield Static("[bold cyan]Cloudflare Credentials[/]")
            yield Rule()

            with Horizontal(classes="setting-row"):
                yield Label("API Token", classes="setting-label")
                yield Input(
                    value=cfg.get("cloudflare.api_token", ""),
                    placeholder="Paste your API token…",
                    password=True,
                    id="input-api-token",
                    classes="setting-control",
                )

            with Horizontal(classes="setting-row"):
                yield Label("Account ID", classes="setting-label")
                yield Input(
                    value=cfg.get("cloudflare.account_id", ""),
                    placeholder="e.g. abc123def456…",
                    id="input-account-id",
                    classes="setting-control",
                )

            with Horizontal(classes="setting-row"):
                yield Label("Zone ID", classes="setting-label")
                yield Input(
                    value=cfg.get("cloudflare.zone_id", ""),
                    placeholder="e.g. 789xyz…",
                    id="input-zone-id",
                    classes="setting-control",
                )

            yield Rule()

            # ── Appearance ────────────────────────────────────────────────────
            yield Static("[bold cyan]Appearance[/]")
            yield Rule()

            with Horizontal(classes="setting-row"):
                yield Label("Theme", classes="setting-label")
                yield Select(
                    _THEME_OPTIONS,
                    value=cfg.get("ui.theme", "default"),
                    id="select-theme",
                    classes="setting-control",
                )

            with Horizontal(classes="setting-row"):
                yield Label("Use Color", classes="setting-label")
                with Container(classes="setting-control"):
                    yield Switch(
                        value=bool(cfg.get("ui.use_color", True)),
                        id="switch-color",
                    )

            with Horizontal(classes="setting-row"):
                yield Label("Use NerdFont", classes="setting-label")
                with Container(classes="setting-control"):
                    yield Switch(
                        value=bool(cfg.get("ui.use_nerdfont", True)),
                        id="switch-nerdfont",
                    )

            yield Rule()

            # ── Runtime ───────────────────────────────────────────────────────
            yield Static("[bold cyan]Runtime[/]")
            yield Rule()

            with Horizontal(classes="setting-row"):
                yield Label("Environment", classes="setting-label")
                yield Select(
                    _ENV_OPTIONS,
                    value=cfg.get("environment", "development"),
                    id="select-env",
                    classes="setting-control",
                )

            with Horizontal(classes="setting-row"):
                yield Label("Debug Mode", classes="setting-label")
                with Container(classes="setting-control"):
                    yield Switch(
                        value=bool(cfg.get("debug", True)),
                        id="switch-debug",
                    )

            with Horizontal(classes="setting-row"):
                yield Label("Log Level", classes="setting-label")
                yield Select(
                    _LOG_OPTIONS,
                    value=cfg.get("log_level", "INFO"),
                    id="select-loglevel",
                    classes="setting-control",
                )

            yield Rule()
            yield Button("󰒓  Save & Apply", id="settings-save", variant="success")

        yield Footer()

    # ── event handlers ────────────────────────────────────────────────────────

    def on_input_changed(self, event: Input.Changed) -> None:
        app: RedTunnelApp = self.app  # type: ignore[assignment]
        mapping = {
            "input-api-token":  "cloudflare.api_token",
            "input-account-id": "cloudflare.account_id",
            "input-zone-id":    "cloudflare.zone_id",
        }
        key = mapping.get(event.input.id, "")
        if key:
            app.config.set(key, event.value)

    def on_switch_changed(self, event: Switch.Changed) -> None:
        app: RedTunnelApp = self.app  # type: ignore[assignment]
        mapping = {
            "switch-color":    "ui.use_color",
            "switch-nerdfont": "ui.use_nerdfont",
            "switch-debug":    "debug",
        }
        key = mapping.get(event.switch.id, "")
        if key:
            app.config.set(key, event.value)

    def on_select_changed(self, event: Select.Changed) -> None:
        app: RedTunnelApp = self.app  # type: ignore[assignment]
        mapping = {
            "select-theme":    "ui.theme",
            "select-env":      "environment",
            "select-loglevel": "log_level",
        }
        key = mapping.get(event.select.id, "")
        if key and event.value is not Select.BLANK:
            app.config.set(key, event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "settings-save":
            self.action_save()

    def action_save(self) -> None:
        try:
            app: RedTunnelApp = self.app  # type: ignore[assignment]
            app.config.save()
            self.notify("Settings saved to config/settings.yml", severity="information")
        except Exception as exc:
            self.notify(f"Save failed: {exc}", severity="error")

    def action_back(self) -> None:
        self.app.pop_screen()


# ═══════════════════════════════════════════════════════════════════════════════
# HelpScreen
# ═══════════════════════════════════════════════════════════════════════════════

_HELP_MD = """\
# Help

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| ↑ / ↓ | Navigate menus |
| Enter | Select / activate |
| Escape | Go back |
| Q | Quit application |
| 1–5 | Jump to menu item (Home screen) |
| Ctrl+S | Save settings (Settings screen) |
| R | Re-run verification (Verify screen) |

## Features

**󰒃  Verify Cloudflare**
Validates your API token, account ID, and zone ID against the
Cloudflare API. Shows a live progress log and a pass/fail summary.

**󰒆  Run Simulation**
_(Under development)_ Safe, rate-limited traffic simulation against
your own tunnel. Domain ownership must be verified first.

**󰈙  View Reports**
_(Under development)_ Browse, compare, and export past simulation
results.

**󰒓  Settings**
Edit all configuration values interactively. Changes apply immediately;
press **Ctrl+S** to persist them to `config/settings.yml`.

## Platform Support

- Linux · macOS · Windows · Android (Termux)

## Configuration

Set credentials via `config/settings.yml` or environment variables:

```
REDTUNNEL_CF_API_TOKEN=…
REDTUNNEL_CF_ACCOUNT_ID=…
REDTUNNEL_CF_ZONE_ID=…
```

## About

RedTunnel is built around four core principles:

- **Safety** — no illegal traffic, no spoofing
- **Verification** — ownership confirmed before any simulation
- **Compliance** — aligned with Cloudflare's AUP
- **Transparency** — open development and documentation
"""


class HelpScreen(Screen):
    """Help and keyboard shortcut reference."""

    BINDINGS = [Binding("escape", "back", "Back", show=True)]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with ScrollableContainer(id="content"):
            yield Markdown(_HELP_MD)
        yield Footer()

    def action_back(self) -> None:
        self.app.pop_screen()


# ═══════════════════════════════════════════════════════════════════════════════
# WizardScreen
# ═══════════════════════════════════════════════════════════════════════════════

_WIZARD_STEPS = [
    (
        "Step 1 of 3 — API Token",
        "cloudflare.api_token",
        True,   # password
        "Create one at: dash.cloudflare.com/profile/api-tokens",
    ),
    (
        "Step 2 of 3 — Account ID",
        "cloudflare.account_id",
        False,
        "Found in: Cloudflare Dashboard > Overview (right sidebar)",
    ),
    (
        "Step 3 of 3 — Zone ID",
        "cloudflare.zone_id",
        False,
        "Found in: Cloudflare Dashboard > select your domain > Overview",
    ),
]


class WizardScreen(Screen):
    """First-run setup wizard for Cloudflare credentials."""

    BINDINGS = [
        Binding("escape", "skip_step", "Skip", show=True),
    ]

    _step: reactive[int] = reactive(0)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="wizard-container"):
            with Vertical(id="wizard-box"):
                yield Static("󰒃  Welcome to RedTunnel", id="wizard-title")
                yield Static(
                    "[dim]Before you can verify or simulate, please provide your "
                    "Cloudflare credentials. You can also set these later in Settings.[/]",
                    id="wizard-hint",
                )
                yield Rule()
                yield ProgressBar(total=len(_WIZARD_STEPS), show_eta=False,
                                  id="wizard-progress")
                yield Static("", id="wizard-step-label")
                yield Static("", id="wizard-field-hint")
                yield Input(placeholder="Enter value…", id="wizard-input",
                            password=False)
                yield Rule()
                yield Button("Next →", id="wizard-next", variant="primary")
                yield Button("Skip this step", id="wizard-skip")
        yield Footer()

    _mounted: bool = False

    def on_mount(self) -> None:
        self._mounted = True
        self._refresh_step()

    def watch__step(self, step: int) -> None:
        if self._mounted:
            self._refresh_step()

    def _refresh_step(self) -> None:
        step = self._step
        if step >= len(_WIZARD_STEPS):
            self._finish()
            return

        title, key, is_password, hint = _WIZARD_STEPS[step]
        app: RedTunnelApp = self.app  # type: ignore[assignment]
        current = app.config.get(key, "")

        self.query_one("#wizard-step-label", Static).update(f"[bold]{title}[/]")
        self.query_one("#wizard-field-hint", Static).update(f"[dim]{hint}[/]")

        inp = self.query_one("#wizard-input", Input)
        inp.password = is_password
        inp.value = current or ""
        inp.focus()

        prog = self.query_one("#wizard-progress", ProgressBar)
        prog.update(progress=step)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "wizard-next":
            self._advance(skip=False)
        elif event.button.id == "wizard-skip":
            self._advance(skip=True)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self._advance(skip=False)

    def action_skip_step(self) -> None:
        self._advance(skip=True)

    def _advance(self, skip: bool) -> None:
        step = self._step
        if step >= len(_WIZARD_STEPS):
            self._finish()
            return

        _, key, _, _ = _WIZARD_STEPS[step]
        if not skip:
            val = self.query_one("#wizard-input", Input).value.strip()
            if val:
                app: RedTunnelApp = self.app  # type: ignore[assignment]
                app.config.set(key, val)

        self._step = step + 1

    def _finish(self) -> None:
        app: RedTunnelApp = self.app  # type: ignore[assignment]
        try:
            app.config.save()
            self.notify("Credentials saved!", severity="information")
        except Exception:
            self.notify(
                "Could not write config file — credentials kept in memory. "
                "Set REDTUNNEL_CF_* env vars to persist them.",
                severity="warning",
            )
        # Replace the wizard with the home screen
        self.app.pop_screen()
        self.app.push_screen(HomeScreen())
