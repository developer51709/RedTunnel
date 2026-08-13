"""Utility functions for RedTunnel."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        
    Returns:
        Configured logger instance
    """
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)


def ensure_directory(path: str) -> Path:
    """Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path object for the directory
    """
    dir_path = Path(path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def read_file_safe(path: str, default: str = "") -> str:
    """Safely read a file, returning default if it doesn't exist.
    
    Args:
        path: File path
        default: Default value if file doesn't exist
        
    Returns:
        File contents or default value
    """
    file_path = Path(path)
    if file_path.exists():
        return file_path.read_text()
    return default


def write_file_safe(path: str, content: str) -> None:
    """Safely write to a file, creating directories if needed.
    
    Args:
        path: File path
        content: Content to write
    """
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)


def format_bytes(bytes_value: int) -> str:
    """Format bytes into human-readable string.
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration.
    
    Args:
        seconds: Number of seconds
        
    Returns:
        Formatted string (e.g., "1h 30m 45s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.0f}s"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    return f"{hours}h {remaining_minutes}m"


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate a string to a maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix