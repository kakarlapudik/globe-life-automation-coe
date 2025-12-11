"""
RAPTOR Logger Usage Examples

Demonstrates various logging features including:
- Basic logging at different levels
- Context management
- Structured logging
- Exception logging
- Log rotation
"""

from pathlib import Path
from raptor.utils.logger import get_logger, configure_logger


def basic_logging_example():
    """Demonstrate basic logging at different levels."""
    print("\n=== Basic Logging Example ===")
    
    logger = get_logger(
        name="basic_example",
        log_dir=Path("logs/examples"),
        log_level="DEBUG"
    )
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    print("✓ Logged messages at all levels")
    print("  Check logs/examples/basic_example.log")


def context_logging_example():
    """Demonstrate logging with context."""
    print("\n=== Context Logging Example ===")
    
    logger = configure_logger(
        name="context_example",
        log_dir=Path("logs/examples"),
        log_level="INFO"
    )
    
    # Set context that will be included in all subsequent logs
    logger.set_context(
        test_id="TC001",
        browser="chromium",
        environment="staging"
    )
    
    logger.info("Starting test execution")
    logger.info("Navigating to login page")
    logger.info("Entering credentials")
    
    # Clear context
    logger.clear_context()
    
    logger.info("Test completed (no context)")
    
    print("✓ Logged messages with context")
    print("  Check logs/examples/context_example.log")


def exception_logging_example():
    """Demonstrate exception logging."""
    print("\n=== Exception Logging Example ===")
    
    logger = configure_logger(
        name="exception_example",
        log_dir=Path("logs/examples"),
        log_level="INFO"
    )
    
    try:
        # Simulate an error
        result = 10 / 0
    except ZeroDivisionError:
        logger.exception("Division by zero error occurred")
    
    try:
        # Simulate another error
        data = {"key": "value"}
        value = data["missing_key"]
    except KeyError:
        logger.error("Key not found in dictionary", exc_info=True)
    
    print("✓ Logged exceptions with full tracebacks")
    print("  Check logs/examples/exception_example.log")
    print("  Check logs/examples/exception_example_error.log")


def structured_logging_example():
    """Demonstrate structured JSON logging."""
    print("\n=== Structured Logging Example ===")
    
    logger = configure_logger(
        name="structured_example",
        log_dir=Path("logs/examples"),
        log_level="INFO",
        structured_format=True
    )
    
    logger.set_context(test_suite="login_tests")
    
    logger.info("Test started", test_name="test_valid_login")
    logger.info("Element located", element_id="username_field", locator="css=#username")
    logger.info("Test passed", duration_ms=1234, assertions_passed=5)
    
    print("✓ Logged structured JSON messages")
    print("  Check logs/examples/structured_example.log")


def test_execution_logging_example():
    """Demonstrate logging during test execution."""
    print("\n=== Test Execution Logging Example ===")
    
    logger = configure_logger(
        name="test_execution",
        log_dir=Path("logs/examples"),
        log_level="DEBUG"
    )
    
    # Simulate a test execution
    logger.set_context(test_id="TC002", test_name="test_user_registration")
    
    logger.info("Test execution started")
    logger.debug("Launching browser")
    logger.debug("Creating new page")
    
    logger.info("Navigating to registration page", url="https://example.com/register")
    logger.debug("Waiting for page load")
    
    logger.info("Filling registration form")
    logger.debug("Located username field", locator="css=#username")
    logger.debug("Entered username", value="testuser123")
    
    logger.debug("Located email field", locator="css=#email")
    logger.debug("Entered email", value="test@example.com")
    
    logger.info("Submitting form")
    logger.debug("Clicked submit button", locator="css=#submit")
    
    logger.info("Verifying registration success")
    logger.debug("Waiting for success message")
    logger.debug("Success message displayed", success_message="Registration successful")
    
    logger.info("Test execution completed", status="PASSED", duration_ms=5432)
    
    logger.clear_context()
    
    print("✓ Logged complete test execution flow")
    print("  Check logs/examples/test_execution.log")


def log_level_filtering_example():
    """Demonstrate log level filtering."""
    print("\n=== Log Level Filtering Example ===")
    
    # Create logger with WARNING level
    logger = configure_logger(
        name="filtering_example",
        log_dir=Path("logs/examples"),
        log_level="WARNING"
    )
    
    logger.debug("This debug message will not be logged")
    logger.info("This info message will not be logged")
    logger.warning("This warning message WILL be logged")
    logger.error("This error message WILL be logged")
    
    # Change log level dynamically
    logger.set_level("DEBUG")
    
    logger.debug("Now debug messages are logged")
    logger.info("And info messages too")
    
    print("✓ Demonstrated log level filtering")
    print("  Check logs/examples/filtering_example.log")


def console_and_file_output_example():
    """Demonstrate console and file output control."""
    print("\n=== Console and File Output Example ===")
    
    # Console only
    console_logger = configure_logger(
        name="console_only",
        log_dir=Path("logs/examples"),
        log_level="INFO",
        console_output=True,
        file_output=False
    )
    
    print("\nConsole only output:")
    console_logger.info("This appears in console only")
    
    # File only
    file_logger = configure_logger(
        name="file_only",
        log_dir=Path("logs/examples"),
        log_level="INFO",
        console_output=False,
        file_output=True
    )
    
    file_logger.info("This appears in file only")
    print("(File only message logged - check logs/examples/file_only.log)")
    
    # Both console and file
    both_logger = configure_logger(
        name="both_outputs",
        log_dir=Path("logs/examples"),
        log_level="INFO",
        console_output=True,
        file_output=True
    )
    
    print("\nBoth console and file output:")
    both_logger.info("This appears in both console and file")
    
    print("✓ Demonstrated output control")


def main():
    """Run all examples."""
    print("=" * 60)
    print("RAPTOR Logger Examples")
    print("=" * 60)
    
    basic_logging_example()
    context_logging_example()
    exception_logging_example()
    structured_logging_example()
    test_execution_logging_example()
    log_level_filtering_example()
    console_and_file_output_example()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("Check the logs/examples/ directory for log files")
    print("=" * 60)


if __name__ == "__main__":
    main()
