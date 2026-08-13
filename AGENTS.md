# Agent Guide for RedTunnel

This file contains important information for agents working on the RedTunnel project.

## Project Overview

RedTunnel is a controlled attack-simulation tool for Cloudflare Tunnels designed for security testing and verification.

**Repository**: https://github.com/developer51709/RedTunnel

## Key Technical Details

### Project Structure
- **Core Logic**: `src/core/` - Platform detection and environment management
- **TUI Framework**: `src/tui/` - Custom text-based UI with NerdFont support
- **Cloudflare Integration**: `src/cloudflare/` - API verification and tunnel management
- **Utilities**: `src/utils/` - Helper functions for logging, file operations
- **Configuration**: `config/` - Multi-environment configuration files
- **Documentation**: `docs/` - Installation, architecture, and usage guides

### Platform Support
- Linux, macOS, Windows
- Android via Termux (fully supported with auto-detection)
- Automatic capability detection (color, Unicode, NerdFont)
- Platform-specific optimizations

### Key Features
- Multi-environment support (development, staging, production, testing)
- Interactive TUI with keyboard navigation
- NerdFont icons with ASCII fallback
- Configurable themes (default, dark, light, minimal)
- Environment variable configuration overrides
- Cross-platform compatibility

## Development Commands

### Installation
```bash
pip install -r requirements.txt
pip install -e .
```

### Running the Application
```bash
# Run TUI
python src/main.py

# Check platform info
python src/main.py --platform-info

# Set environment
python src/main.py --environment production
```

### Configuration
- Main config: `config/settings.yml` (gitignored, use `settings.example.yml` as template)
- Environment configs: `config/environments/{env}.yml`
- Environment variables: `REDTUNNEL_*` prefix

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src
```

## Important Patterns

### Platform Detection
Always use `get_platform_info()` for platform-specific logic:
```python
from src.core import get_platform_info

platform = get_platform_info()
if platform.is_termux:
    # Termux-specific code
```

### Configuration Access
Use `get_config()` for configuration:
```python
from src.core import get_config

config = get_config()
api_token = config.get("cloudflare.api_token")
```

### TUI Components
Use the TUI framework for interactive elements:
```python
from src.tui import get_theme, get_icon_set, Menu

theme = get_theme()
icons = get_icon_set()
menu = Menu("Title", ["Option 1", "Option 2"])
```

## Security Considerations

- Never commit API tokens or credentials
- Use environment variables for sensitive data
- `config/settings.yml` is gitignored
- Validate user input for Cloudflare operations
- Follow Cloudflare AUP for all operations

## Cross-Platform Testing

When making changes, test on:
- Standard Linux terminal
- macOS Terminal
- Windows PowerShell/CMD
- Termux on Android (if possible)

## Adding New Features

1. Add core logic in appropriate `src/` subdirectory
2. Add TUI components in `src/tui/components.py` if needed
3. Update configuration schema if adding new settings
4. Add documentation in `docs/`
5. Test on multiple platforms

## Common Issues

### NerdFont Fallback
The NerdFont package is optional. The code automatically falls back to ASCII icons if not available. Always test with and without NerdFont installed.

### Termux Compatibility
Termux has limited resources. The platform detection automatically reduces worker counts and enables caching. Respect these limitations in new features.

### Configuration Loading
Configuration loads in this order: defaults → config file → environment config → environment variables → CLI args. Keep this in mind when debugging configuration issues.