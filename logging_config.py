"""
Logging configuration for the pizzeria management system.
Provides structured logging with file rotation and different log levels.
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


def get_safe_log_directory() -> Path:
    """
    Get a safe directory for log files.
    Uses EXE directory if running from EXE, otherwise uses current directory.
    Always returns an absolute path to avoid issues with working directory.
    
    Returns:
        Path to log directory (absolute path)
    """
    # Check if running from PyInstaller EXE
    if getattr(sys, 'frozen', False):
        # Running from EXE - use EXE directory (always absolute)
        exe_dir = Path(sys.executable).parent.resolve()
        log_dir = exe_dir / "logs"
    else:
        # Running from Python script - use project logs directory
        # Use absolute path to avoid issues with working directory changes
        try:
            # Try to use the script's directory
            script_dir = Path(__file__).parent.resolve()
            log_dir = script_dir / "logs"
        except:
            # Fallback to current working directory (but make it absolute)
            log_dir = Path.cwd().resolve() / "logs"
    
    # Ensure we have an absolute path
    log_dir = log_dir.resolve()
    
    # Create directory if it doesn't exist
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except (PermissionError, OSError) as e:
        # If we can't create in the intended location, use temp directory
        import tempfile
        temp_dir = Path(tempfile.gettempdir()) / "pizzeria_logs"
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir.resolve()
    
    return log_dir


def setup_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Path to log file (default: app.log in safe directory)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        
    Returns:
        Configured logger instance
    """
    # Get safe log directory
    log_dir = get_safe_log_directory()
    
    # Always use absolute paths based on safe log directory
    if log_file is None:
        log_file = str(log_dir / "app.log")
    else:
        # If relative path, make it relative to log directory
        log_path = Path(log_file)
        if not log_path.is_absolute():
            log_file = str(log_dir / log_file)
        else:
            # Even if absolute, ensure it's in a safe location
            # If it's in a protected directory, move it to safe log directory
            try:
                # Test if we can write to the parent directory
                log_path.parent.mkdir(parents=True, exist_ok=True)
                # Try to create a test file
                test_file = log_path.parent / ".test_write"
                try:
                    test_file.touch()
                    test_file.unlink()
                except (PermissionError, OSError):
                    # Can't write here, use safe directory instead
                    log_file = str(log_dir / log_path.name)
            except (PermissionError, OSError):
                # Can't create parent, use safe directory
                log_file = str(log_dir / Path(log_file).name)
    
    # Ensure log_file is now an absolute path in a safe location
    log_path = Path(log_file).resolve()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("pizzeria")
    logger.setLevel(log_level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler with rotation
    try:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except (PermissionError, OSError) as e:
        # If we can't write to log file, try alternative location
        print(f"Warning: Could not write to {log_file}: {e}")
        # Try user's temp directory as fallback
        try:
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "pizzeria_logs"
            temp_dir.mkdir(exist_ok=True)
            fallback_log = temp_dir / "app.log"
            file_handler = logging.handlers.RotatingFileHandler(
                str(fallback_log),
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(detailed_formatter)
            logger.addHandler(file_handler)
            print(f"Using fallback log location: {fallback_log}")
        except Exception as fallback_error:
            print(f"Error: Could not create log file even in temp directory: {fallback_error}")
            # Continue without file logging - only console logging
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # Error log handler (separate file for errors only)
    # Use the same safe directory as the main log file
    error_log_file = log_path.parent / "app_errors.log"
    try:
        # Ensure parent directory exists and is writable
        error_log_file.parent.mkdir(parents=True, exist_ok=True)
        error_handler = logging.handlers.RotatingFileHandler(
            str(error_log_file),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
    except (PermissionError, OSError) as e:
        # If we can't write to error log, try fallback location
        print(f"Warning: Could not create error log file at {error_log_file}: {e}")
        try:
            import tempfile
            temp_dir = Path(tempfile.gettempdir()) / "pizzeria_logs"
            temp_dir.mkdir(exist_ok=True)
            fallback_error_log = temp_dir / "app_errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                str(fallback_error_log),
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            print(f"Using fallback error log location: {fallback_error_log}")
        except Exception as fallback_error:
            print(f"Error: Could not create error log file even in temp directory: {fallback_error}")
            error_handler = None
    
    if error_handler:
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (default: 'pizzeria')
        
    Returns:
        Logger instance
    """
    if name is None:
        name = "pizzeria"
    return logging.getLogger(name)



