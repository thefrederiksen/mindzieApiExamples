#!/usr/bin/env python
"""
Common utility functions for mindzie API examples.

This module provides shared functionality for formatting output,
error handling, and other common operations used across examples.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

# Add parent directory to path for .env loading
sys.path.append(str(Path(__file__).parent.parent))

# Try to load .env file if it exists
try:
    from dotenv import load_dotenv
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

# Import the mindzie API library
from mindzie_api import MindzieAPIClient
from mindzie_api.exceptions import (
    MindzieAPIException, AuthenticationError, NotFoundError,
    ValidationError, ServerError, TimeoutError
)

# Import base utilities
from projects.api_utils import get_client as get_base_client


def create_client() -> Optional[MindzieAPIClient]:
    """Create and return a configured MindzieAPIClient instance.
    
    This is an alias for get_client() from api_utils.py for backward compatibility.
    
    Returns:
        MindzieAPIClient instance or None if credentials are missing
    """
    return get_base_client()


def handle_api_error(error: Exception, operation: str = "operation") -> None:
    """Handle API errors with user-friendly messages.
    
    Args:
        error: The exception that occurred
        operation: Description of the operation that failed
    """
    if isinstance(error, AuthenticationError):
        print(f"[ERROR] Authentication failed during {operation}")
        print("Check your API credentials (MINDZIE_TENANT_ID and MINDZIE_API_KEY)")
    elif isinstance(error, NotFoundError):
        print(f"[ERROR] Resource not found during {operation}")
        print("The requested resource may not exist or you may not have access to it")
    elif isinstance(error, ValidationError):
        print(f"[ERROR] Validation error during {operation}")
        print(f"Details: {error}")
    elif isinstance(error, TimeoutError):
        print(f"[ERROR] Request timed out during {operation}")
        print("The server may be busy or your network connection may be slow")
    elif isinstance(error, ServerError):
        print(f"[ERROR] Server error during {operation}")
        print("The server encountered an error. Please try again later")
    elif isinstance(error, MindzieAPIException):
        print(f"[ERROR] API error during {operation}: {error}")
    else:
        print(f"[ERROR] Unexpected error during {operation}: {error}")


def print_section(title: str, width: int = 70) -> None:
    """Print a formatted section header.
    
    Args:
        title: The section title
        width: Width of the separator line
    """
    print("\n" + "=" * width)
    print(title)
    print("=" * width)


def print_success(message: str) -> None:
    """Print a success message with green color (if terminal supports it).
    
    Args:
        message: The success message to print
    """
    # Simple success indicator without relying on terminal colors
    print(f"[SUCCESS] {message}")


def print_error(message: str) -> None:
    """Print an error message with red color (if terminal supports it).
    
    Args:
        message: The error message to print
    """
    print(f"[ERROR] {message}", file=sys.stderr)


def print_info(message: str) -> None:
    """Print an informational message.
    
    Args:
        message: The informational message to print
    """
    print(f"[INFO] {message}")


def print_warning(message: str) -> None:
    """Print a warning message.
    
    Args:
        message: The warning message to print
    """
    print(f"[WARNING] {message}")


def format_date(date_str: Any) -> str:
    """Format a date string to a readable format.
    
    Args:
        date_str: Date string in ISO format or datetime object
        
    Returns:
        Formatted date string
    """
    if not date_str:
        return "N/A"
    
    try:
        if isinstance(date_str, datetime):
            return date_str.strftime("%Y-%m-%d %H:%M")
        elif isinstance(date_str, str):
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        pass
    
    # Fallback: return first 19 characters
    return str(date_str)[:19] if len(str(date_str)) > 19 else str(date_str)


def validate_guid(guid_str: str) -> bool:
    """Validate if a string is a valid GUID/UUID format.
    
    Args:
        guid_str: String to validate
        
    Returns:
        True if valid GUID format, False otherwise
    """
    import re
    guid_pattern = re.compile(
        r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
    )
    return bool(guid_pattern.match(guid_str))


def mask_sensitive_string(sensitive_str: str, visible_chars: int = 4) -> str:
    """Mask a sensitive string showing only first and last few characters.
    
    Args:
        sensitive_str: The sensitive string to mask
        visible_chars: Number of characters to show at start and end
        
    Returns:
        Masked string
    """
    if not sensitive_str or len(sensitive_str) <= visible_chars * 2:
        return "*" * len(sensitive_str) if sensitive_str else ""
    
    return f"{sensitive_str[:visible_chars]}...{sensitive_str[-visible_chars:]}"


def safe_file_path(base_dir: str, filename: str) -> Optional[Path]:
    """Validate and create a safe file path preventing directory traversal.
    
    Args:
        base_dir: Base directory for file operations
        filename: Requested filename
        
    Returns:
        Safe Path object or None if validation fails
    """
    try:
        base = Path(base_dir).resolve()
        file_path = (base / filename).resolve()
        
        # Ensure the resolved path is within the base directory
        if not str(file_path).startswith(str(base)):
            print_error(f"Invalid file path: {filename}")
            return None
            
        return file_path
    except Exception as e:
        print_error(f"Error validating file path: {e}")
        return None


def confirm_action(prompt: str = "Continue?") -> bool:
    """Ask user for confirmation before proceeding.
    
    Args:
        prompt: The confirmation prompt
        
    Returns:
        True if user confirms, False otherwise
    """
    try:
        response = input(f"{prompt} (y/N): ").strip().lower()
        return response in ['y', 'yes']
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled by user")
        return False


def format_size(size_bytes: int) -> str:
    """Format byte size to human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """Create a simple text progress bar.
    
    Args:
        current: Current progress value
        total: Total value
        width: Width of the progress bar
        
    Returns:
        Progress bar string
    """
    if total == 0:
        return "[" + "=" * width + "]"
    
    progress = min(int((current / total) * width), width)
    return "[" + "=" * progress + "-" * (width - progress) + f"] {current}/{total}"


if __name__ == "__main__":
    print("Common Utilities for mindzie API Examples")
    print("=" * 50)
    print("\nThis module provides shared utility functions including:")
    print("- Output formatting (print_section, print_success, etc.)")
    print("- Error handling (handle_api_error)")
    print("- Input validation (validate_guid, safe_file_path)")
    print("- Data formatting (format_date, format_size)")
    print("- User interaction (confirm_action)")
    print("\nImport this module in your scripts:")
    print("  from common_utils import print_success, handle_api_error")