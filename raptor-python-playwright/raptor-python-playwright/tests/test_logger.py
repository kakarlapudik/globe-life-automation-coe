"""
Unit tests for RAPTOR Logger

Tests logging functionality including:
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Console and file output
- Log rotation
- Structured logging
- Context management
"""

import pytest
import logging
import json
from pathlib import Path
import tempfile
import shutil
from raptor.utils.logger import (
    RaptorLogger,
    get_logger,
    configure_logger,
    ContextFilter,
    StructuredFormatter,
    ColoredConsoleFormatter
)


@pytest.fixture
def temp_log_dir():
    """Create a temporary directory for log files."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup - handle Windows file locking issues
    if temp_dir.exists():
        import time
        import gc
        
        # Force garbage collection to close file handles
        gc.collect()
        time.sleep(0.1)
        
        # Try to remove with retries
        max_retries = 3
        for i in range(max_retries):
            try:
                shutil.rmtree(temp_dir)
                break
            except PermissionError:
                if i < max_retries - 1:
                    time.sleep(0.2)
                else:
                    # If still failing, just pass - temp files will be cleaned up by OS
                    pass


@pytest.fixture
def logger(temp_log_dir):
    """Create a test logger instance."""
    logger_instance = RaptorLogger(
        name="test_logger",
        log_dir=temp_log_dir,
        log_level="DEBUG",
        console_output=False,
        file_output=True
    )
    yield logger_instance
    # Close logger to release file handles
    logger_instance.close()


class TestRaptorLogger:
    """Test suite for RaptorLogger class."""
    
    def test_logger_initialization(self, temp_log_dir):
        """Test logger can be initialized with various configurations."""
        logger = RaptorLogger(
            name="test",
            log_dir=temp_log_dir,
            log_level="INFO"
        )
        
        assert logger.name == "test"
        assert logger.log_dir == temp_log_dir
        assert logger.log_level == logging.INFO
    
    def test_log_directory_creation(self, temp_log_dir):
        """Test that log directory is created if it doesn't exist."""
        log_dir = temp_log_dir / "nested" / "logs"
        logger = RaptorLogger(
            name="test",
            log_dir=log_dir,
            file_output=True
        )
        
        assert log_dir.exists()
    
    def test_debug_logging(self, logger, temp_log_dir):
        """Test DEBUG level logging."""
        logger.debug("Debug message")
        
        log_file = temp_log_dir / "test_logger.log"
        assert log_file.exists()
        
        content = log_file.read_text()
        assert "DEBUG" in content
        assert "Debug message" in content
    
    def test_info_logging(self, logger, temp_log_dir):
        """Test INFO level logging."""
        logger.info("Info message")
        
        log_file = temp_log_dir / "test_logger.log"
        content = log_file.read_text()
        assert "INFO" in content
        assert "Info message" in content
    
    def test_warning_logging(self, logger, temp_log_dir):
        """Test WARNING level logging."""
        logger.warning("Warning message")
        
        log_file = temp_log_dir / "test_logger.log"
        content = log_file.read_text()
        assert "WARNING" in content
        assert "Warning message" in content
    
    def test_error_logging(self, logger, temp_log_dir):
        """Test ERROR level logging."""
        logger.error("Error message")
        
        # Check main log file
        log_file = temp_log_dir / "test_logger.log"
        content = log_file.read_text()
        assert "ERROR" in content
        assert "Error message" in content
        
        # Check error log file
        error_log_file = temp_log_dir / "test_logger_error.log"
        assert error_log_file.exists()
        error_content = error_log_file.read_text()
        assert "ERROR" in error_content
        assert "Error message" in error_content
    
    def test_critical_logging(self, logger, temp_log_dir):
        """Test CRITICAL level logging."""
        logger.critical("Critical message")
        
        log_file = temp_log_dir / "test_logger.log"
        content = log_file.read_text()
        assert "CRITICAL" in content
        assert "Critical message" in content
    
    def test_exception_logging(self, logger, temp_log_dir):
        """Test exception logging with traceback."""
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Exception occurred")
        
        log_file = temp_log_dir / "test_logger.log"
        content = log_file.read_text()
        assert "ERROR" in content
        assert "Exception occurred" in content
        assert "ValueError: Test exception" in content
        assert "Traceback" in content
    
    def test_log_level_filtering(self, temp_log_dir):
        """Test that log level filtering works correctly."""
        logger = RaptorLogger(
            name="test",
            log_dir=temp_log_dir,
            log_level="WARNING",
            console_output=False,
            file_output=True
        )
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        
        log_file = temp_log_dir / "test.log"
        content = log_file.read_text()
        
        # DEBUG and INFO should not be logged
        assert "Debug message" not in content
        assert "Info message" not in content
        
        # WARNING should be logged
        assert "WARNING" in content
        assert "Warning message" in content
    
    def test_context_management(self, logger, temp_log_dir):
        """Test setting and clearing context."""
        logger.set_context(test_id="TC001", browser="chromium")
        logger.info("Message with context")
        
        logger.clear_context()
        logger.info("Message without context")
        
        log_file = temp_log_dir / "test_logger.log"
        content = log_file.read_text()
        assert "Message with context" in content
        assert "Message without context" in content
    
    def test_set_level(self, logger, temp_log_dir):
        """Test changing log level dynamically."""
        logger.set_level("ERROR")
        
        logger.info("Info message")
        logger.error("Error message")
        
        log_file = temp_log_dir / "test_logger.log"
        content = log_file.read_text()
        
        # INFO should not be logged after level change
        assert "Info message" not in content
        
        # ERROR should be logged
        assert "ERROR" in content
        assert "Error message" in content
    
    def test_structured_logging(self, temp_log_dir):
        """Test structured JSON logging format."""
        logger = RaptorLogger(
            name="test",
            log_dir=temp_log_dir,
            log_level="INFO",
            console_output=False,
            file_output=True,
            structured_format=True
        )
        
        logger.info("Structured message", extra_field="extra_value")
        
        log_file = temp_log_dir / "test.log"
        content = log_file.read_text()
        
        # Parse JSON
        log_entry = json.loads(content.strip())
        
        assert log_entry['level'] == 'INFO'
        assert log_entry['message'] == 'Structured message'
        assert 'timestamp' in log_entry
        assert 'module' in log_entry
        assert 'function' in log_entry
    
    def test_console_output_disabled(self, temp_log_dir, capsys):
        """Test that console output can be disabled."""
        logger = RaptorLogger(
            name="test",
            log_dir=temp_log_dir,
            console_output=False,
            file_output=True
        )
        
        logger.info("Test message")
        
        captured = capsys.readouterr()
        assert "Test message" not in captured.out
    
    def test_file_output_disabled(self, temp_log_dir):
        """Test that file output can be disabled."""
        logger = RaptorLogger(
            name="test",
            log_dir=temp_log_dir,
            console_output=True,
            file_output=False
        )
        
        logger.info("Test message")
        
        log_file = temp_log_dir / "test.log"
        assert not log_file.exists()


class TestContextFilter:
    """Test suite for ContextFilter class."""
    
    def test_context_filter_initialization(self):
        """Test ContextFilter can be initialized."""
        filter = ContextFilter()
        assert filter.context == {}
    
    def test_set_context(self):
        """Test setting context values."""
        filter = ContextFilter()
        filter.set_context(key1="value1", key2="value2")
        
        assert filter.context["key1"] == "value1"
        assert filter.context["key2"] == "value2"
    
    def test_clear_context(self):
        """Test clearing context values."""
        filter = ContextFilter()
        filter.set_context(key1="value1")
        filter.clear_context()
        
        assert filter.context == {}
    
    def test_filter_adds_context_to_record(self):
        """Test that filter adds context to log records."""
        filter = ContextFilter()
        filter.set_context(test_id="TC001")
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        filter.filter(record)
        
        assert hasattr(record, 'test_id')
        assert record.test_id == "TC001"


class TestStructuredFormatter:
    """Test suite for StructuredFormatter class."""
    
    def test_structured_formatter_initialization(self):
        """Test StructuredFormatter can be initialized."""
        formatter = StructuredFormatter()
        assert formatter.include_context is True
    
    def test_format_basic_message(self):
        """Test formatting a basic log message."""
        formatter = StructuredFormatter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data['level'] == 'INFO'
        assert log_data['message'] == 'Test message'
        assert 'timestamp' in log_data
    
    def test_format_with_exception(self):
        """Test formatting a message with exception info."""
        formatter = StructuredFormatter()
        
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data['level'] == 'ERROR'
        assert 'exception' in log_data
        assert 'ValueError: Test error' in log_data['exception']


class TestColoredConsoleFormatter:
    """Test suite for ColoredConsoleFormatter class."""
    
    def test_colored_formatter_initialization(self):
        """Test ColoredConsoleFormatter can be initialized."""
        formatter = ColoredConsoleFormatter()
        assert formatter is not None
    
    def test_format_with_colors(self):
        """Test formatting with color codes."""
        formatter = ColoredConsoleFormatter()
        
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Check for ANSI color codes
        assert '\033[' in formatted
        assert 'INFO' in formatted
        assert 'Test message' in formatted


class TestGlobalLoggerFunctions:
    """Test suite for global logger functions."""
    
    def test_get_logger(self, temp_log_dir):
        """Test get_logger function."""
        logger = get_logger(
            name="test",
            log_dir=temp_log_dir,
            log_level="INFO"
        )
        
        assert isinstance(logger, RaptorLogger)
        assert logger.name == "test"
    
    def test_configure_logger(self, temp_log_dir):
        """Test configure_logger function."""
        logger = configure_logger(
            name="test",
            log_dir=temp_log_dir,
            log_level="DEBUG"
        )
        
        assert isinstance(logger, RaptorLogger)
        assert logger.name == "test"
        assert logger.log_level == logging.DEBUG


class TestLogRotation:
    """Test suite for log rotation functionality."""
    
    def test_log_rotation_configuration(self, temp_log_dir):
        """Test that log rotation is configured correctly."""
        logger = RaptorLogger(
            name="test",
            log_dir=temp_log_dir,
            max_bytes=1024,  # 1 KB
            backup_count=3
        )
        
        assert logger.max_bytes == 1024
        assert logger.backup_count == 3
    
    def test_log_rotation_creates_backup(self, temp_log_dir):
        """Test that log rotation creates backup files."""
        logger = RaptorLogger(
            name="test",
            log_dir=temp_log_dir,
            max_bytes=100,  # Very small to trigger rotation
            backup_count=2,
            console_output=False
        )
        
        # Write enough messages to trigger rotation
        for i in range(50):
            logger.info(f"Message {i} with some additional text to increase size")
        
        log_file = temp_log_dir / "test.log"
        assert log_file.exists()
        
        # Check if backup files were created
        backup_files = list(temp_log_dir.glob("test.log.*"))
        assert len(backup_files) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
