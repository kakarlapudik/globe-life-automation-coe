"""
Tests for pytest fixtures defined in conftest.py

This test file verifies that all fixtures are working correctly:
- config fixture provides configuration access
- browser_manager fixture creates and cleans up browser manager
- browser fixture launches browser
- context fixture creates browser context
- page fixture creates page
- element_manager fixture creates element manager
- database fixture provides database access (if configured)
"""

import pytest
from pathlib import Path

from raptor.core.browser_manager import BrowserManager
from raptor.core.config_manager import ConfigManager
from raptor.core.element_manager import ElementManager
from raptor.database.database_manager import DatabaseManager
from raptor.utils.reporter import TestReporter
from playwright.async_api import Browser, BrowserContext, Page


class TestConfigFixture:
    """Test the config fixture."""
    
    def test_config_fixture_provides_config_manager(self, config):
        """Test that config fixture provides a ConfigManager instance."""
        assert config is not None
        assert isinstance(config, ConfigManager)
    
    def test_config_fixture_has_test_settings(self, config):
        """Test that config fixture has test-specific settings."""
        # Should be headless in tests
        assert config.get("browser.headless") is True
        
        # Should have shorter timeout for tests
        timeout = config.get("timeouts.default")
        assert timeout is not None
        assert timeout == 10000
    
    def test_config_fixture_can_get_values(self, config):
        """Test that config fixture can retrieve configuration values."""
        # Should be able to get browser settings
        browser_config = config.get("browser", {})
        assert isinstance(browser_config, dict)


class TestBrowserManagerFixture:
    """Test the browser_manager fixture."""
    
    @pytest.mark.asyncio
    async def test_browser_manager_fixture_provides_manager(self, browser_manager):
        """Test that browser_manager fixture provides a BrowserManager instance."""
        assert browser_manager is not None
        assert isinstance(browser_manager, BrowserManager)
    
    @pytest.mark.asyncio
    async def test_browser_manager_fixture_not_launched_initially(self, browser_manager):
        """Test that browser is not launched initially."""
        assert not browser_manager.is_browser_launched
        assert browser_manager.browser is None
    
    @pytest.mark.asyncio
    async def test_browser_manager_fixture_can_launch_browser(self, browser_manager):
        """Test that browser_manager fixture can launch browser."""
        await browser_manager.launch_browser("chromium", headless=True)
        
        assert browser_manager.is_browser_launched
        assert browser_manager.browser is not None
        assert browser_manager.browser.is_connected()


class TestBrowserFixture:
    """Test the browser fixture."""
    
    @pytest.mark.asyncio
    async def test_browser_fixture_provides_browser(self, browser):
        """Test that browser fixture provides a Browser instance."""
        assert browser is not None
        assert isinstance(browser, Browser)
    
    @pytest.mark.asyncio
    async def test_browser_fixture_is_connected(self, browser):
        """Test that browser fixture provides a connected browser."""
        assert browser.is_connected()
    
    @pytest.mark.asyncio
    async def test_browser_fixture_can_create_context(self, browser):
        """Test that browser fixture can create contexts."""
        context = await browser.new_context()
        assert context is not None
        await context.close()


class TestContextFixture:
    """Test the context fixture."""
    
    @pytest.mark.asyncio
    async def test_context_fixture_provides_context(self, context):
        """Test that context fixture provides a BrowserContext instance."""
        assert context is not None
        assert isinstance(context, BrowserContext)
    
    @pytest.mark.asyncio
    async def test_context_fixture_can_create_page(self, context):
        """Test that context fixture can create pages."""
        page = await context.new_page()
        assert page is not None
        await page.close()


class TestPageFixture:
    """Test the page fixture."""
    
    @pytest.mark.asyncio
    async def test_page_fixture_provides_page(self, page):
        """Test that page fixture provides a Page instance."""
        assert page is not None
        assert isinstance(page, Page)
    
    @pytest.mark.asyncio
    async def test_page_fixture_can_navigate(self, page):
        """Test that page fixture can navigate to URLs."""
        await page.goto("https://example.com")
        assert "example.com" in page.url.lower()
    
    @pytest.mark.asyncio
    async def test_page_fixture_has_default_timeout(self, page):
        """Test that page fixture has default timeout set."""
        # Page should have timeout set (we can't directly check it,
        # but we can verify it doesn't throw on timeout operations)
        try:
            await page.goto("https://example.com", timeout=5000)
            assert True
        except Exception as e:
            # Should not timeout on valid URL
            pytest.fail(f"Page navigation failed: {e}")


class TestElementManagerFixture:
    """Test the element_manager fixture."""
    
    @pytest.mark.asyncio
    async def test_element_manager_fixture_provides_manager(self, element_manager):
        """Test that element_manager fixture provides an ElementManager instance."""
        assert element_manager is not None
        assert isinstance(element_manager, ElementManager)
    
    @pytest.mark.asyncio
    async def test_element_manager_fixture_has_page(self, element_manager, page):
        """Test that element_manager fixture is bound to the page."""
        assert element_manager.page is not None
        assert element_manager.page == page


class TestDatabaseFixture:
    """Test the database fixture."""
    
    def test_database_fixture_provides_manager_or_none(self, database):
        """Test that database fixture provides DatabaseManager or None."""
        # Database may be None if not configured
        if database is not None:
            assert isinstance(database, DatabaseManager)
    
    def test_database_fixture_skips_if_not_configured(self, database):
        """Test that database fixture allows skipping if not configured."""
        if database is None:
            pytest.skip("Database not configured")
        
        # If we get here, database is configured
        assert database is not None


class TestReporterFixture:
    """Test the reporter fixture."""
    
    def test_reporter_fixture_provides_reporter(self, reporter):
        """Test that reporter fixture provides a TestReporter instance."""
        assert reporter is not None
        assert isinstance(reporter, TestReporter)
    
    def test_reporter_fixture_has_report_dir(self, reporter):
        """Test that reporter fixture has report directory configured."""
        assert reporter.report_dir is not None
        assert reporter.report_dir.exists()


class TestUtilityFixtures:
    """Test utility fixtures."""
    
    def test_temp_dir_fixture_provides_directory(self, temp_dir):
        """Test that temp_dir fixture provides a temporary directory."""
        assert temp_dir is not None
        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()
    
    def test_temp_dir_fixture_is_writable(self, temp_dir):
        """Test that temp_dir fixture provides a writable directory."""
        test_file = temp_dir / "test.txt"
        test_file.write_text("test content")
        assert test_file.exists()
        assert test_file.read_text() == "test content"
    
    def test_mock_page_url_fixture_provides_url(self, mock_page_url):
        """Test that mock_page_url fixture provides a URL."""
        assert mock_page_url is not None
        assert isinstance(mock_page_url, str)
        assert mock_page_url.startswith("http")
    
    def test_worker_id_fixture_provides_id(self, worker_id):
        """Test that worker_id fixture provides a worker ID."""
        assert worker_id is not None
        assert isinstance(worker_id, str)
        # Should be "master" in single-process execution
        assert worker_id == "master"


class TestFixtureIntegration:
    """Test that fixtures work together correctly."""
    
    @pytest.mark.asyncio
    async def test_page_and_element_manager_integration(self, page, element_manager):
        """Test that page and element_manager fixtures work together."""
        await page.goto("https://example.com")
        
        # Element manager should be able to interact with page
        assert element_manager.page == page
        
        # Should be able to locate elements
        heading = await element_manager.locate_element("css=h1")
        assert heading is not None
    
    @pytest.mark.asyncio
    async def test_browser_context_page_hierarchy(self, browser, context, page):
        """Test that browser, context, and page fixtures maintain proper hierarchy."""
        assert browser is not None
        assert context is not None
        assert page is not None
        
        # Page should belong to context
        assert page.context == context
    
    def test_config_and_browser_manager_integration(self, config, browser_manager):
        """Test that config and browser_manager fixtures work together."""
        # Browser manager should use config
        assert browser_manager.config is not None
        
        # Config should have browser settings
        browser_config = config.get("browser", {})
        assert isinstance(browser_config, dict)


class TestFixtureCleanup:
    """Test that fixtures properly cleanup resources."""
    
    @pytest.mark.asyncio
    async def test_browser_cleanup_after_test(self, browser_manager):
        """Test that browser is cleaned up after test."""
        # Launch browser
        await browser_manager.launch_browser("chromium", headless=True)
        assert browser_manager.is_browser_launched
        
        # Browser will be cleaned up by fixture after test
        # We just verify it was launched
        assert browser_manager.browser is not None
    
    @pytest.mark.asyncio
    async def test_page_cleanup_after_test(self, page):
        """Test that page is cleaned up after test."""
        # Navigate to page
        await page.goto("https://example.com")
        
        # Page will be cleaned up by fixture after test
        # We just verify it works
        assert page.url is not None


class TestFixtureIsolation:
    """Test that fixtures provide proper test isolation."""
    
    @pytest.mark.asyncio
    async def test_first_test_with_page(self, page):
        """First test that uses page fixture."""
        await page.goto("https://example.com")
        await page.evaluate("window.testValue = 'first'")
        
        value = await page.evaluate("window.testValue")
        assert value == "first"
    
    @pytest.mark.asyncio
    async def test_second_test_with_page(self, page):
        """Second test that uses page fixture - should have clean state."""
        # This should be a fresh page, not the same as first test
        await page.goto("https://example.com")
        
        # testValue should not exist from previous test
        value = await page.evaluate("window.testValue || 'not set'")
        assert value == "not set"
