# Installation Guide

This guide covers installing RedTunnel on various platforms including Linux, macOS, Windows, and Android (Termux).

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Standard Installation

### Clone the Repository

```bash
git clone https://github.com/developer51709/RedTunnel.git
cd RedTunnel
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install in Development Mode

```bash
pip install -e .
```

This will create the `redtunnel` command-line tool.

## Platform-Specific Installation

### Linux

Most Linux distributions come with Python pre-installed. You may need to install pip:

```bash
# Debian/Ubuntu
sudo apt-get update
sudo apt-get install python3 python3-pip

# Fedora/RHEL
sudo dnf install python3 python3-pip

# Arch Linux
sudo pacman -S python python-pip
```

Then follow the standard installation steps.

### macOS

macOS comes with Python, but you may want to use Homebrew for a more recent version:

```bash
brew install python3
```

Then follow the standard installation steps.

### Windows

1. Download Python from [python.org](https://python.org)
2. During installation, check "Add Python to PATH"
3. Open Command Prompt or PowerShell

```cmd
git clone https://github.com/developer51709/RedTunnel.git
cd RedTunnel
pip install -r requirements.txt
pip install -e .
```

### Android (Termux)

RedTunnel is fully supported on Android via Termux.

#### Install Termux

1. Install Termux from F-Droid (recommended) or Google Play
2. Open Termux and update packages:

```bash
pkg update && pkg upgrade
```

#### Install Python and Dependencies

```bash
pkg install python git
```

#### Clone and Install

```bash
git clone https://github.com/developer51709/RedTunnel.git
cd RedTunnel
pip install -r requirements.txt
```

#### Run RedTunnel

```bash
python src/main.py
```

Note: On Termux, RedTunnel automatically detects the mobile environment and adjusts settings accordingly.

## Optional: NerdFont Support

RedTunnel includes NerdFont support for enhanced icons and symbols. The tool automatically falls back to standard ASCII if NerdFont is not available.

### Install NerdFont (Optional)

#### Linux/macOS

```bash
# Install a NerdFont (e.g., FiraCode)
wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.0.2/FiraCode.zip
unzip FiraCode.zip -d ~/.local/share/fonts
fc-cache -fv
```

#### Termux

```bash
# Install a NerdFont in Termux
pkg install fontconfig
mkdir -p ~/.termux/font
wget https://github.com/ryanoasis/nerd-fonts/raw/master/patched-fonts/FiraCode/Regular/FiraCodeNerdFont-Regular.ttf -O ~/.termux/font/FiraCodeNerdFont-Regular.ttf
termux-reload-settings
```

## Verification

Test your installation:

```bash
# Check platform information
python src/main.py --platform-info

# Run the TUI
python src/main.py
```

## Troubleshooting

### Python Not Found

Ensure Python 3.8+ is installed and in your PATH:

```bash
python3 --version
```

### Permission Errors

If you encounter permission errors, try:

```bash
pip install --user -r requirements.txt
```

### Termux Issues

If you encounter issues on Termux:

1. Ensure packages are up to date: `pkg update && pkg upgrade`
2. Check Python version: `python --version`
3. Reinstall dependencies: `pip install --force-reinstall -r requirements.txt`

### NerdFont Not Working

If NerdFont icons don't display:

1. Verify the font is installed correctly
2. Check your terminal configuration
3. RedTunnel will automatically fall back to ASCII icons

## Development Installation

For development, install with dev dependencies:

```bash
pip install -e ".[dev]"
```

This includes testing and linting tools:
- pytest
- pytest-cov
- black
- flake8
- mypy