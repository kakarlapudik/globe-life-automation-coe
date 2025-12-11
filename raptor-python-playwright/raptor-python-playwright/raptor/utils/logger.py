"""
RAPTOR Logger Module

Provides structured logging with context, multiple output handlers, and log rotation.
Supports DEBUG, INFO, WARNING, ERROR, and CRITICAL log levels.

Requirements: 1.4, 9.3
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json


class ContextFilter(logging.Filter):
    """Filter that adds context information to log records."""
    
    def __init__(self):
        super().__init__()
        self.context: Dict[str, Any] = {}
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Add context to the log record."""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True
    
    def set_context(self, **kwargs):
        """Set context values that will be added to all log records."""
        self.context.update(kwargs)
    
    def clear_context(self):
        """Clear all context values."""
        self.context.clear()


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured log messages with context."""
    
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a structured message."""
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add context if enabled
        if self.include_context:
            context = {}
            for key in dir(record):
                if not key.startswith('_') and key not in [
                    'args', 'created', 'exc_info', 'exc_text', 'filename',
                    'funcName', 'levelname', 'levelno', 'lineno', 'module',
                    'msecs', 'msg', 'name', 'pathname', 'process', 'processName',
                    'relativeCreated', 'stack_info', 'thread', 'threadName',
                    'getMessage', 'message'
                ]:
                    value = getattr(record, key)
                    if value is not None and not callable(value):
                        context[key] = value
            
            if context:
                log_data['context'] = context
        
        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """Formatter that adds colors to console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with colors."""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Build the message
        message = f"{color}[{record.levelname}]{reset} {timestamp} - {record.name} - {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message


class RaptorLogger:
    """
    Main logger class for RAPTOR framework.
    
    Provides structured logging with context, file rotation, and multiple output handlers.
    """
    
    def __init__(
        self,
        name: str = "raptor",
        log_dir: Optional[Path] = None,
        log_level: str = "INFO",
        console_output: bool = True,
        file_output: bool = True,
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        structured_format: bool = False
    ):
        """
        Initialize the RAPTOR logger.
        
        Args:
            name: Logger name
            log_dir: Directory for log files (default: ./logs)
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console_output: Enable console output
            file_output: Enable file output
            max_bytes: Maximum size of log file before rotation
            backup_count: Number of backup files to keep
            structured_format: Use structured JSON format for file logs
        """
        self.name = name
        self.log_dir = log_dir or Path("logs")
        self.log_level = getattr(logging, log_level.upper())
        self.console_output = console_output
        self.file_output = file_output
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.structured_format = structured_format
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.log_level)
        self.logger.propagate = False
        
        # Add context filter
        self.context_filter = ContextFilter()
        self.logger.addFilter(self.context_filter)
        
        # Clear any existing handlers
        self.logger.handlers.clear()
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup console and file handlers."""
        # Console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_formatter = ColoredConsoleFormatter()
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # File handler with rotation
        if self.file_output:
            # Create log directory if it doesn't exist
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
            # Main log file
            log_file = self.log_dir / f"{self.name}.log"
            file_handler = logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)
            
            # Use structured or standard format
            if self.structured_format:
                file_formatter = StructuredFormatter(include_context=True)
            else:
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
            
            # Error log file (only ERROR and CRITICAL)
            error_log_file = self.log_dir / f"{self.name}_error.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self.max_bytes,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(file_formatter)
            self.logger.addHandler(error_handler)
    
    def set_context(self, **kwargs):
        """
        Set context values that will be included in all subsequent log messages.
        
        Args:
            **kwargs: Context key-value pairs
        
        Example:
            logger.set_context(test_id="TC001", browser="chromium")
        """
        self.context_filter.set_context(**kwargs)
    
    def clear_context(self):
        """Clear all context values."""
        self.context_filter.clear_context()
    
    def debug(self, message: str, **kwargs):
        """
        Log a DEBUG level message.
        
        Args:
            message: Log message
            **kwargs: Additional context for this message only
        """
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """
        Log an INFO level message.
        
        Args:
            message: Log message
            **kwargs: Additional context for this message only
        """
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """
        Log a WARNING level message.
        
        Args:
            message: Log message
            **kwargs: Additional context for this message only
        """
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """
        Log an ERROR level message.
        
        Args:
            message: Log message
            exc_info: Include exception information
            **kwargs: Additional context for this message only
        """
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """
        Log a CRITICAL level message.
        
        Args:
            message: Log message
            exc_info: Include exception information
            **kwargs: Additional context for this message only
        """
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """
        Log an exception with ERROR level and full traceback.
        
        Args:
            message: Log message
            **kwargs: Additional context for this message only
        """
        self.logger.exception(message, extra=kwargs)
    
    def set_level(self, level: str):
        """
        Change the logging level.
        
        Args:
            level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        new_level = getattr(logging, level.upper())
        self.logger.setLevel(new_level)
        for handler in self.logger.handlers:
            handler.setLevel(new_level)
    
    def close(self):
        """
        Close all handlers and release file handles.
        
        This should be called when the logger is no longer needed,
        especially important on Windows to release file locks.
        """
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)


# Global logger instance
_global_logger: Optional[RaptorLogger] = None


def get_logger(
    name: str = "raptor",
    log_dir: Optional[Path] = None,
    log_level: str = "INFO",
    **kwargs
) -> RaptorLogger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        log_level: Minimum log level
        **kwargs: Additional arguments for RaptorLogger
    
    Returns:
        RaptorLogger instance
    """
    global _global_logger
    
    if _global_logger is None:
        _global_logger = RaptorLogger(
            name=name,
            log_dir=log_dir,
            log_level=log_level,
            **kwargs
        )
    
    return _global_logger


def configure_logger(
    name: str = "raptor",
    log_dir: Optional[Path] = None,
    log_level: str = "INFO",
    **kwargs
) -> RaptorLogger:
    """
    Configure and return a new logger instance.
    
    This will replace any existing global logger.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        log_level: Minimum log level
        **kwargs: Additional arguments for RaptorLogger
    
    Returns:
        RaptorLogger instance
    """
    global _global_logger
    
    _global_logger = RaptorLogger(
        name=name,
        log_dir=log_dir,
        log_level=log_level,
        **kwargs
    )
    
    return _global_logger
