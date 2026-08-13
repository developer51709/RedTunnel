# Architecture Documentation

This document describes the architecture and design of RedTunnel.

## Overview

RedTunnel is designed with a modular, cross-platform architecture that supports multiple environments and provides a flexible foundation for Cloudflare tunnel simulation.

## Core Components

### 1. Platform Detection (`src/core/platform.py`)

The platform detection module provides:
- Cross-platform compatibility detection
- Termux/Android support
- Terminal capability detection (color, Unicode, NerdFont)
- Platform-specific configuration recommendations

**Key Classes:**
- `PlatformType`: Enum of supported platforms
- `PlatformInfo`: Main platform detection class

**Features:**
- Automatic detection of Termux on Android
- NerdFont availability detection
- Terminal capability assessment
- Platform-specific optimization recommendations

### 2. Environment Management (`src/core/environment.py`)

The environment management system provides:
- Multi-environment support (development, staging, production, testing)
- Configuration file loading and merging
- Environment variable overrides
- Environment-specific settings

**Key Classes:**
- `Environment`: Enum of environment types
- `EnvironmentConfig`: Configuration management class

**Configuration Hierarchy:**
1. Default configuration
2. Configuration file (settings.yml)
3. Environment-specific file (environments/{env}.yml)
4. Environment variables (REDTUNNEL_*)
5. Command-line overrides

### 3. TUI Framework (`src/tui/`)

The Text User Interface framework provides:

#### Icons (`src/tui/icons.py`)
- NerdFont icon support with ASCII fallback
- Icon set management
- Automatic detection and fallback

**Key Classes:**
- `IconSet`: Icon management with NerdFont/ASCII fallback

#### Theme (`src/tui/theme.py`)
- Color theme management
- ANSI color code handling
- Automatic color support detection
- Multiple built-in themes (default, dark, light, minimal)

**Key Classes:**
- `Theme`: Theme management class
- `Color`: ANSI color enum
- `Style`: Text styling utilities

#### Components (`src/tui/components.py`)
- Reusable TUI components
- Progress bars, spinners, menus, tables
- Status lines and confirmation dialogs

**Key Classes:**
- `ProgressBar`: Text-based progress indicator
- `Spinner`: Loading animation
- `Menu`: Interactive menu component
- `Table`: Text table formatting
- `ConfirmationDialog`: Yes/No confirmation

#### Renderer (`src/tui/renderer.py`)
- Main TUI rendering engine
- Input handling and key bindings
- Application lifecycle management

**Key Classes:**
- `TUIRenderer`: Main rendering engine
- `InputHandler`: Keyboard input processing
- `KeyBindings`: Key-to-action mapping
- `TUIApp`: Base application class

### 4. Cloudflare Integration (`src/cloudflare/`)

Cloudflare API integration for tunnel verification and management.

**Current Implementation:**
- `CloudflareVerifier`: Verifies Cloudflare account and zone access

**Planned Extensions:**
- Tunnel management
- Traffic simulation
- Attack pattern generation

## Project Structure

```
RedTunnel/
├── src/
│   ├── core/              # Core functionality
│   │   ├── platform.py    # Platform detection
│   │   └── environment.py # Environment management
│   ├── tui/               # TUI framework
│   │   ├── icons.py       # Icon management
│   │   ├── theme.py       # Theme management
│   │   ├── components.py  # UI components
│   │   └── renderer.py    # Rendering engine
│   ├── cloudflare/        # Cloudflare integration
│   │   └── verify.py      # Verification module
│   ├── utils/             # Utility functions
│   └── main.py            # Main entry point
├── config/
│   ├── settings.yml       # Main configuration
│   └── environments/      # Environment configs
│       ├── development.yml
│       ├── staging.yml
│       └── production.yml
├── docs/                  # Documentation
├── tests/                 # Test suite
└── setup.py              # Package setup
```

## Design Principles

### 1. Cross-Platform Compatibility

- Abstract platform differences
- Automatic capability detection
- Graceful degradation
- Termux/Android support

### 2. Modular Architecture

- Clear separation of concerns
- Reusable components
- Plugin-friendly design
- Easy testing

### 3. Configuration Flexibility

- Multiple configuration sources
- Environment-specific settings
- Runtime configuration
- Sensible defaults

### 4. User Experience

- Consistent interface across platforms
- Automatic fallback for unsupported features
- Clear error messages
- Intuitive navigation

## Data Flow

### Initialization Flow

1. Platform detection
2. Configuration loading
3. Theme and icon initialization
4. TUI component setup
5. Application start

### Configuration Loading Flow

```
Defaults → Config File → Environment Config → Environment Variables → CLI Args
```

### TUI Render Flow

```
State Update → Component Render → Theme Application → Icon Replacement → Display
```

## Extension Points

### Adding New Platforms

Extend `PlatformType` enum and add detection logic in `PlatformInfo._detect_platform()`.

### Adding New Environments

Add new environment to `Environment` enum and create corresponding config file in `config/environments/`.

### Adding New TUI Components

Create component classes in `src/tui/components.py` following the existing pattern.

### Adding New Themes

Add theme configuration to `Theme.THEMES` dictionary in `src/tui/theme.py`.

## Security Considerations

### Configuration Security

- API tokens stored in configuration files (not committed to git)
- Environment variable support for sensitive data
- No hardcoded credentials

### Platform Security

- Termux detection respects sandbox boundaries
- No privilege escalation
- Safe default configurations

### Cloudflare Security

- Verified domain ownership required
- Compliant with Cloudflare AUP
- No unauthorized access attempts

## Performance Considerations

### Mobile Optimization

- Reduced worker threads on mobile
- Aggressive caching
- Minimal network calls
- Resource-conscious defaults

### Desktop Optimization

- Parallel processing
- Extended caching options
- Full feature set enabled

## Testing Strategy

### Unit Tests

- Platform detection tests
- Configuration loading tests
- Component rendering tests
- Theme application tests

### Integration Tests

- End-to-end TUI tests
- Cloudflare API tests (mocked)
- Cross-platform compatibility tests

### Manual Testing

- Termux testing
- Different terminal emulators
- Various screen sizes
- Keyboard layout variations