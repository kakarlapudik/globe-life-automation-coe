"""
pytest Configuration and Fixtures for RAPTOR Framework

This module provides pytest configuration and reusable fixtures for test execution:
- Browser management fixtures
- Page creation fixtures
- Database connection fixtures
- Configuration access fixtures
- Test isolation and cleanup
- Parallel execution support

Requirements: 12.1, 12.3
"""

import pytest
import asyncio
import os
import logging
from pathlib import Path
from typing import Generator, AsyncGenerator, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from raptor.core.browser_manager import BrowserManager
from raptor.core.config_manager import ConfigManager
from raptor.core.element_manager import ElementManager
from raptor.database.database_manager import DatabaseManager
from raptor.utils.reporter import TestReporter
from raptor.utils.cleanup import (
    cleanup_manager,
    BrowserCleanupHelper,
    DatabaseCleanupHelper,
    ScreenshotCleanupHelper,
    LogCleanupHelper,
    ReportCleanupHelper
)


# ============================================================================
# Pytest Configuration
# ============================================================================

# Import test execution control plugin
pytest_plugins = ["raptor.core.test_execution_control"]


def pytest_configure(config):
    """
    Configure pytest with custom markers and settings.
    
    Args:
        config: pytest configuration object
    """
    # Register custom markers
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )
    config.addinivalue_line(
        "markers", "browser: mark test as requiring browser"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "property: mark test as property-based test"
    )
    config.addinivalue_line(
        "markers", "smoke: mark test as smoke test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as regression test"
    )
    config.addinivalue_line(
        "markers", "flaky: mark test as potentially flaky"
    )
    
    # Setup logging for tests
    log_dir = Path("logs/tests")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "test_execution.log"),
            logging.StreamHandler()
        ]
    )


def pytest_collection_modifyitems(config, items):
    """
    Modify test collection to add markers based on test names.
    
    Args:
        config: pytest configuration object
        items: list of collected test items
    """
    for item in items:
        # Add asyncio marker to async tests
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)
        
        # Add browser marker to tests that use browser fixtures
        if "browser" in item.fixturenames or "page" in item.fixturenames:
            item.add_marker(pytest.mark.browser)
        
        # Add database marker to tests that use database fixtures
        if "database" in item.fixturenames:
            item.add_marker(pytest.mark.database)
        
        # Add property marker to property-based tests
        if "property" in item.name.lower():
            item.add_marker(pytest.mark.property)


# ============================================================================
# Event Loop Fixture
# ============================================================================

@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for the entire test session.
    
    This fixture ensures that async tests can run properly and that
    the event loop is properly cleaned up after all tests complete.
    
    Yields:
        asyncio.AbstractEventLoop: Event loop for async operations
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============================================================================
# Configuration Fixture
# ============================================================================

@pytest.fixture(scope="session")
def config() -> ConfigManager:
    """
    Provide ConfigManager instance for test configuration access.
    
    This fixture loads the test environment configuration and provides
    access to all configuration settings throughout the test session.
    
    Returns:
        ConfigManager: Configuration manager instance
        
    Example:
        def test_timeout_config(config):
            timeout = config.get("timeouts.default")
            assert timeout > 0
    """
    # Load test environment configuration
    config_manager = ConfigManager()
    
    # Override with test-specific settings if needed
    test_env = os.getenv("TEST_ENV", "dev")
    config_manager.load_config(test_env)
    
    # Set test-specific overrides
    config_manager.set("browser.headless", True)  # Always headless in tests
    config_manager.set("timeouts.default", 10000)  # Shorter timeouts for tests
    
    return config_manager


# ============================================================================
# Browser Manager Fixture
# ============================================================================

@pytest.fixture(scope="function")
async def browser_manager(config: ConfigManager) -> AsyncGenerator[BrowserManager, None]:
    """
    Provide BrowserManager instance with automatic cleanup.
    
    This fixture creates a BrowserManager for each test function and ensures
    proper cleanup after the test completes. The browser is not launched
    automatically - tests must call launch_browser() explicitly.
    
    Args:
        config: Configuration manager fixture
        
    Yields:
        BrowserManager: Browser manager instance
        
    Example:
        async def test_navigation(browser_manager):
            await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            await page.goto("https://example.com")
    """
    manager = BrowserManager(config=config)
    
    # Register cleanup task with cleanup manager
    cleanup_manager.register_cleanup(
        name=f"browser_manager_{id(manager)}",
        callback=lambda: asyncio.run(BrowserCleanupHelper.cleanup_browser_manager(manager)),
        priority=10  # High priority - cleanup browsers early
    )
    
    try:
        yield manager
    finally:
        # Cleanup: close browser if it was launched
        if manager.is_browser_launched:
            await manager.close_browser()
        
        # Unregister cleanup task
        cleanup_manager.unregister_cleanup(f"browser_manager_{id(manager)}")


# ============================================================================
# Browser Fixture
# ============================================================================

@pytest.fixture(scope="function")
async def browser(
    browser_manager: BrowserManager,
    config: ConfigManager
) -> AsyncGenerator[Browser, None]:
    """
    Provide a launched Browser instance with automatic cleanup.
    
    This fixture launches a browser (Chromium by default) and ensures
    proper cleanup after the test completes. The browser type can be
    configured via the TEST_BROWSER environment variable.
    
    Args:
        browser_manager: Browser manager fixture
        config: Configuration manager fixture
        
    Yields:
        Browser: Playwright browser instance
        
    Example:
        async def test_with_browser(browser):
            context = await browser.new_context()
            page = await context.new_page()
            await page.goto("https://example.com")
    """
    # Get browser type from environment or config
    browser_type = os.getenv("TEST_BROWSER", "chromium")
    headless = config.get("browser.headless", True)
    
    # Launch browser
    browser_instance = await browser_manager.launch_browser(
        browser_type=browser_type,
        headless=headless
    )
    
    try:
        yield browser_instance
    finally:
        # Cleanup handled by browser_manager fixture
        pass


# ============================================================================
# Browser Context Fixture
# ============================================================================

@pytest.fixture(scope="function")
async def context(
    browser_manager: BrowserManager,
    browser: Browser
) -> AsyncGenerator[BrowserContext, None]:
    """
    Provide a BrowserContext instance with automatic cleanup.
    
    This fixture creates a new browser context for test isolation.
    Each test gets a fresh context with no shared state.
    
    Args:
        browser_manager: Browser manager fixture
        browser: Browser fixture
        
    Yields:
        BrowserContext: Playwright browser context
        
    Example:
        async def test_with_context(context):
            page = await context.new_page()
            await page.goto("https://example.com")
    """
    # Create context with test-specific options
    context_instance = await browser_manager.create_context(
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
        record_video_dir=None  # Disable video recording in tests
    )
    
    try:
        yield context_instance
    finally:
        # Close context
        await context_instance.close()


# ============================================================================
# Page Fixture
# ============================================================================

@pytest.fixture(scope="function")
async def page(
    browser_manager: BrowserManager,
    context: BrowserContext
) -> AsyncGenerator[Page, None]:
    """
    Provide a Page instance with automatic cleanup.
    
    This fixture creates a new page in the browser context for each test.
    The page is automatically closed after the test completes.
    
    Args:
        browser_manager: Browser manager fixture
        context: Browser context fixture
        
    Yields:
        Page: Playwright page instance
        
    Example:
        async def test_navigation(page):
            await page.goto("https://example.com")
            title = await page.title()
            assert "Example" in title
    """
    # Create page
    page_instance = await browser_manager.create_page(context)
    
    # Set default timeout
    page_instance.set_default_timeout(10000)
    
    try:
        yield page_instance
    finally:
        # Take screenshot on failure
        if hasattr(pytest, "current_test_failed") and pytest.current_test_failed:
            screenshot_dir = Path("screenshots/test_failures")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            
            test_name = os.getenv("PYTEST_CURRENT_TEST", "unknown").split(":")[-1].split(" ")[0]
            screenshot_path = screenshot_dir / f"{test_name}.png"
            
            try:
                await page_instance.screenshot(path=str(screenshot_path))
            except Exception as e:
                logging.warning(f"Failed to capture screenshot: {e}")
        
        # Close page
        await page_instance.close()


# ============================================================================
# Element Manager Fixture
# ============================================================================

@pytest.fixture(scope="function")
async def element_manager(page: Page) -> ElementManager:
    """
    Provide ElementManager instance for element interactions.
    
    This fixture creates an ElementManager bound to the current page,
    allowing tests to interact with web elements using RAPTOR's
    element management capabilities.
    
    Args:
        page: Page fixture
        
    Returns:
        ElementManager: Element manager instance
        
    Example:
        async def test_element_interaction(element_manager):
            await element_manager.click("css=#submit-button")
            await element_manager.fill("css=#username", "testuser")
    """
    return ElementManager(page)


# ============================================================================
# Database Fixture
# ============================================================================

@pytest.fixture(scope="session")
def database(config: ConfigManager) -> Generator[Optional[DatabaseManager], None, None]:
    """
    Provide DatabaseManager instance for database operations.
    
    This fixture creates a DatabaseManager for the test session. If database
    credentials are not configured, returns None to allow tests to skip
    database-dependent operations.
    
    Args:
        config: Configuration manager fixture
        
    Yields:
        Optional[DatabaseManager]: Database manager instance or None
        
    Example:
        def test_database_query(database):
            if database is None:
                pytest.skip("Database not configured")
            
            result = database.execute_query("SELECT * FROM TestData")
            assert len(result) > 0
    """
    # Get database configuration
    db_config = config.get("database", {})
    
    # Skip if database not configured
    if not db_config or not db_config.get("server"):
        logging.warning("Database not configured, database tests will be skipped")
        yield None
        return
    
    # Create database manager
    try:
        db_manager = DatabaseManager(
            server=db_config.get("server"),
            database=db_config.get("database"),
            user=db_config.get("user"),
            password=db_config.get("password"),
            use_pooling=True
        )
        
        # Register cleanup task with cleanup manager
        cleanup_manager.register_cleanup(
            name=f"database_manager_{id(db_manager)}",
            callback=DatabaseCleanupHelper.cleanup_database_manager,
            priority=20,  # Medium priority - cleanup after browsers
            database_manager=db_manager
        )
        
        yield db_manager
        
    except Exception as e:
        logging.error(f"Failed to initialize database manager: {e}")
        yield None
    finally:
        # Cleanup: disconnect if connected
        if 'db_manager' in locals() and db_manager:
            try:
                db_manager.disconnect()
                # Unregister cleanup task
                cleanup_manager.unregister_cleanup(f"database_manager_{id(db_manager)}")
            except Exception as e:
                logging.warning(f"Error during database cleanup: {e}")


# ============================================================================
# Test Reporter Fixture
# ============================================================================

@pytest.fixture(scope="session")
def reporter(config: ConfigManager) -> TestReporter:
    """
    Provide TestReporter instance for test reporting.
    
    This fixture creates a TestReporter for generating test reports
    throughout the test session.
    
    Args:
        config: Configuration manager fixture
        
    Returns:
        TestReporter: Test reporter instance
        
    Example:
        def test_with_reporting(reporter):
            reporter.start_suite("test_example")
            # ... test code ...
            reporter.end_suite()
    """
    report_dir = Path("reports/tests")
    report_dir.mkdir(parents=True, exist_ok=True)
    
    return TestReporter(report_dir=str(report_dir))


# ============================================================================
# Pytest Hooks for Test Lifecycle
# ============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to capture test results for screenshot on failure.
    
    This hook runs after each test phase and captures whether the test failed,
    allowing the page fixture to take screenshots on failure.
    """
    outcome = yield
    rep = outcome.get_result()
    
    # Store report in item for access by fixtures
    setattr(item, f"rep_{rep.when}", rep)
    
    # Set flag for screenshot capture
    if rep.when == "call" and rep.failed:
        pytest.current_test_failed = True
    else:
        pytest.current_test_failed = False


# ============================================================================
# Parallel Execution Support
# ============================================================================

@pytest.fixture(scope="session")
def worker_id(request):
    """
    Provide worker ID for parallel test execution.
    
    This fixture returns the worker ID when running tests in parallel
    with pytest-xdist. Returns "master" for single-process execution.
    
    Args:
        request: pytest request object
        
    Returns:
        str: Worker ID or "master"
        
    Example:
        def test_parallel_isolation(worker_id):
            # Each worker gets unique resources
            db_name = f"test_db_{worker_id}"
    """
    if hasattr(request.config, 'workerinput'):
        return request.config.workerinput['workerid']
    return "master"


# ============================================================================
# Session Cleanup Fixture
# ============================================================================

@pytest.fixture(scope="session", autouse=True)
def session_cleanup():
    """
    Perform cleanup at the end of the test session.
    
    This fixture ensures all resources are properly cleaned up when the
    test session ends, including graceful shutdown handling.
    """
    yield
    
    # Perform final cleanup
    logging.info("Test session ending, performing final cleanup")
    
    # Cleanup old reports
    ReportCleanupHelper.cleanup_old_reports(
        report_dir="reports",
        max_age_days=30,
        max_count=50
    )
    
    # Execute all registered cleanup tasks
    cleanup_manager.cleanup_all()
    
    logging.info("Session cleanup completed")


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(scope="function", autouse=True)
def cleanup_screenshots(request):
    """
    Automatically cleanup screenshots based on test results.
    
    This fixture runs after each test and removes screenshots for passed tests
    to save disk space while keeping screenshots for failed tests for debugging.
    """
    yield
    
    # Cleanup happens after test
    try:
        # Get test result
        test_passed = not hasattr(request.node, 'rep_call') or request.node.rep_call.passed
        
        if test_passed:
            # Clean up screenshot for this specific test if it passed
            test_name = request.node.name
            screenshot_dir = Path("screenshots/test_failures")
            
            if screenshot_dir.exists():
                screenshot_file = screenshot_dir / f"{test_name}.png"
                if screenshot_file.exists():
                    screenshot_file.unlink()
                    logging.debug(f"Deleted screenshot for passed test: {test_name}")
        
        # Also cleanup old screenshots to prevent disk space issues
        ScreenshotCleanupHelper.cleanup_old_screenshots(
            screenshot_dir="screenshots/test_failures",
            max_age_days=7,
            max_count=100
        )
    except Exception as e:
        logging.warning(f"Error during screenshot cleanup: {e}")


@pytest.fixture(scope="session", autouse=True)
def cleanup_logs():
    """
    Automatically cleanup old log files at session start and end.
    
    This fixture runs once per test session and removes old log files
    to prevent disk space issues.
    """
    # Cleanup at session start
    LogCleanupHelper.cleanup_old_logs(
        log_dir="logs",
        max_age_days=30,
        max_count=50
    )
    
    yield
    
    # Cleanup at session end
    LogCleanupHelper.cleanup_old_logs(
        log_dir="logs",
        max_age_days=30,
        max_count=50
    )


# ============================================================================
# Utility Fixtures
# ============================================================================

@pytest.fixture
def temp_dir(tmp_path):
    """
    Provide a temporary directory for test file operations.
    
    This fixture creates a temporary directory that is automatically
    cleaned up after the test completes.
    
    Args:
        tmp_path: pytest's built-in tmp_path fixture
        
    Returns:
        Path: Temporary directory path
        
    Example:
        def test_file_operations(temp_dir):
            test_file = temp_dir / "test.txt"
            test_file.write_text("test content")
            assert test_file.exists()
    """
    return tmp_path


@pytest.fixture
def mock_page_url():
    """
    Provide a mock page URL for testing.
    
    Returns:
        str: Mock page URL
    """
    return "https://example.com/test"


# ============================================================================
# Skip Conditions
# ============================================================================

def pytest_runtest_setup(item):
    """
    Setup hook to handle test skipping based on markers and conditions.
    
    This hook runs before each test and can skip tests based on:
    - Missing database configuration
    - Missing browser binaries
    - Environment-specific conditions
    """
    # Skip database tests if database not configured
    if "database" in item.keywords:
        config = ConfigManager()
        db_config = config.get("database", {})
        if not db_config or not db_config.get("server"):
            pytest.skip("Database not configured")
    
    # Skip slow tests if SKIP_SLOW environment variable is set
    if "slow" in item.keywords and os.getenv("SKIP_SLOW"):
        pytest.skip("Skipping slow test (SKIP_SLOW=1)")
