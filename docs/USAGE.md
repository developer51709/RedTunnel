# Usage Guide

This guide covers how to use RedTunnel for Cloudflare tunnel verification and simulation.

## Command-Line Interface

### Basic Usage

```bash
python src/main.py
```

This launches the interactive TUI interface.

Note: If you're running on Termux, use the Termux Python:
```bash
/data/data/com.termux/files/usr/bin/python src/main.py
```

### Command-Line Options

```bash
python src/main.py --help
```

Available options:
- `--version`: Show version information
- `--platform-info`: Display platform information
- `--environment`: Set environment (development, staging, production, testing)
- `--config`: Specify configuration file path
- `--no-tui`: Run in command-line mode (not yet fully implemented)

### Examples

```bash
# Run with production environment
python src/main.py --environment production

# Use custom configuration file
python src/main.py --config /path/to/config.yml

# Check platform information
python src/main.py --platform-info
```

## Interactive TUI

### Main Menu

The TUI provides an interactive menu-driven interface:

1. **Verify Cloudflare Configuration** - Test your Cloudflare API credentials and zone access
2. **Run Simulation** - Execute safe attack simulations (under development)
3. **View Reports** - View simulation reports (under development)
4. **Settings** - View current configuration and platform information
5. **Help** - Display keyboard shortcuts and help information

### Keyboard Navigation

- **↑/K** - Move up in menus
- **↓/J** - Move down in menus
- **Enter** - Select menu item
- **Q** - Quit application

### Platform-Specific Behavior

#### Termux/Android

When running on Termux, RedTunnel automatically:
- Reduces resource usage
- Enables mobile-optimized settings
- Adjusts terminal handling for mobile keyboards

#### Desktop

On desktop platforms, RedTunnel uses:
- Full-color themes
- Enhanced keyboard shortcuts
- Standard terminal features

## Configuration

### Configuration File

The main configuration file is `config/settings.yml`:

```yaml
environment: development
debug: true
log_level: DEBUG

cloudflare:
  api_token: "your-api-token"
  account_id: "your-account-id"
  zone_id: "your-zone-id"

simulation:
  max_requests: 100
  timeout: 30
  delay_between_requests: 1.0

ui:
  use_nerdfont: true
  use_color: true
  use_unicode: true
  theme: default
```

### Environment Variables

Configuration can be overridden using environment variables:

- `REDTUNNEL_ENV` - Set environment
- `REDTUNNEL_DEBUG` - Enable debug mode
- `REDTUNNEL_LOG_LEVEL` - Set log level
- `REDTUNNEL_CF_API_TOKEN` - Cloudflare API token
- `REDTUNNEL_CF_ACCOUNT_ID` - Cloudflare account ID
- `REDTUNNEL_CF_ZONE_ID` - Cloudflare zone ID
- `REDTUNNEL_MAX_REQUESTS` - Maximum simulation requests
- `REDTUNNEL_TIMEOUT` - Request timeout

### Environment-Specific Configuration

Create environment-specific configurations in `config/environments/`:

- `development.yml` - Development settings
- `staging.yml` - Staging settings
- `production.yml` - Production settings

## Cloudflare Setup

### API Token

1. Go to Cloudflare Dashboard
2. Navigate to "My Profile" → "API Tokens"
3. Create a custom token with permissions:
   - Account - Account Settings: Read
   - Zone - Zone: Read
   - Zone - DNS: Read

### Account ID and Zone ID

1. In Cloudflare Dashboard, select your account
2. Copy the Account ID from the right sidebar
3. Select your zone/domain
4. Copy the Zone ID from the right sidebar

### Configuration

Add your credentials to `config/settings.yml`:

```yaml
cloudflare:
  api_token: "your-api-token-here"
  account_id: "your-account-id-here"
  zone_id: "your-zone-id-here"
```

Or use environment variables:

```bash
export REDTUNNEL_CF_API_TOKEN="your-api-token-here"
export REDTUNNEL_CF_ACCOUNT_ID="your-account-id-here"
export REDTUNNEL_CF_ZONE_ID="your-zone-id-here"
```

## Verification

### Verify Configuration

Use the TUI to verify your Cloudflare configuration:

1. Launch RedTunnel: `python src/main.py`
2. Select "Verify Cloudflare Configuration"
3. View verification results

### Expected Output

Successful verification shows:
- ✓ Account Access: Valid
- ✓ Zone Access: Valid
- Overall Status: PASSED

Failed verification shows:
- ✗ Account Access: Invalid
- ✗ Zone Access: Invalid
- Overall Status: FAILED

## Troubleshooting

### Common Issues

#### API Token Errors

- Ensure token has correct permissions
- Check token hasn't expired
- Verify token is copied correctly

#### Platform Detection Issues

- Run `python src/main.py --platform-info` to check detection
- Manually set environment variables if needed
- Check terminal capabilities

#### TUI Display Issues

- Disable NerdFont: Set `use_nerdfont: false` in config
- Disable color: Set `use_color: false` in config
- Try different terminal emulator

#### Termux Issues

- Update Termux: `pkg update && pkg upgrade`
- Check Python version: `python --version`
- Reinstall dependencies: `pip install --force-reinstall -r requirements.txt`

## Advanced Usage

### Custom Themes

Create custom themes by modifying `src/tui/theme.py`:

```python
THEMES = {
    "custom": {
        "primary": Color.CYAN,
        "secondary": Color.MAGENTA,
        # ... other colors
    },
}
```

### Custom Icons

Add custom icons in `src/tui/icons.py`:

```python
NERDFONT_ICONS = {
    "custom_icon": "",
    # ... other icons
}

ASCII_ICONS = {
    "custom_icon": "[C]",
    # ... other icons
}
```

### Programmatic Usage

Import RedTunnel components for programmatic use:

```python
from src.core import get_platform_info, get_config
from src.tui import get_theme, get_icon_set

# Get platform information
platform = get_platform_info()
print(f"Platform: {platform.get_platform_name()}")

# Get configuration
config = get_config()
print(f"Environment: {config.get_environment()}")

# Use TUI components
theme = get_theme()
icons = get_icon_set()
print(icons.get('success'))
```

## Best Practices

### Security

- Never commit API tokens to version control
- Use environment variables for sensitive data
- Rotate API tokens regularly
- Use read-only tokens when possible

### Performance

- Use appropriate environment settings
- Adjust worker counts based on platform
- Enable caching on mobile platforms
- Monitor resource usage

### Development

- Use development environment for testing
- Enable debug mode for troubleshooting
- Test on multiple platforms
- Validate configuration before production use