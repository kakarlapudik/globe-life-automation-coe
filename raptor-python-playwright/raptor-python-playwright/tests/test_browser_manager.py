"""
Unit tests for BrowserManager.

Tests cover:
- Browser launching for different browser types
- Context creation
- Page creation
- Cleanup and resource management
- Error handling
- Property-based tests for browser launch consistency
"""

import pytest
from hypothesis import given, strategies as st, settings
from raptor.core import BrowserManager, RaptorException, ConfigManager
from playwright.async_api import Browser, BrowserContext, Page


class TestBrowserManager:
    """Test suite for BrowserManager class."""

    @pytest.mark.asyncio
    async def test_browser_manager_initialization(self):
        """Test that BrowserManager initializes correctly."""
        browser_manager = BrowserManager()
        
        assert browser_manager is not None
        assert browser_manager.browser is None
        assert browser_manager.browser_type is None
        assert not browser_manager.is_browser_launched
        assert len(browser_manager.get_contexts()) == 0
        assert len(browser_manager.get_pages()) == 0

    @pytest.mark.asyncio
    async def test_launch_chromium_browser(self):
        """Test launching Chromium browser."""
        browser_manager = BrowserManager()
        
        try:
            browser = await browser_manager.launch_browser("chromium", headless=True)
            
            assert browser is not None
            assert isinstance(browser, Browser)
            assert browser.is_connected()
            assert browser_manager.is_browser_launched
            assert browser_manager.browser_type == "chromium"
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_launch_firefox_browser(self):
        """Test launching Firefox browser."""
        browser_manager = BrowserManager()
        
        try:
            browser = await browser_manager.launch_browser("firefox", headless=True)
            
            assert browser is not None
            assert isinstance(browser, Browser)
            assert browser.is_connected()
            assert browser_manager.browser_type == "firefox"
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_launch_webkit_browser(self):
        """Test launching WebKit browser."""
        browser_manager = BrowserManager()
        
        try:
            browser = await browser_manager.launch_browser("webkit", headless=True)
            
            assert browser is not None
            assert isinstance(browser, Browser)
            assert browser.is_connected()
            assert browser_manager.browser_type == "webkit"
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_launch_invalid_browser_type(self):
        """Test that launching invalid browser type raises exception."""
        browser_manager = BrowserManager()
        
        with pytest.raises(RaptorException) as exc_info:
            await browser_manager.launch_browser("invalid_browser")
        
        assert "Invalid browser type" in str(exc_info.value)
        assert not browser_manager.is_browser_launched

    @pytest.mark.asyncio
    async def test_create_context(self):
        """Test creating browser context."""
        browser_manager = BrowserManager()
        
        try:
            await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            
            assert context is not None
            assert isinstance(context, BrowserContext)
            assert len(browser_manager.get_contexts()) == 1
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_create_context_with_options(self):
        """Test creating context with custom options."""
        browser_manager = BrowserManager()
        
        try:
            await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Custom User Agent"
            )
            
            assert context is not None
            assert context.pages  # Context should be valid
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_create_context_without_browser(self):
        """Test that creating context without browser raises exception."""
        browser_manager = BrowserManager()
        
        with pytest.raises(RaptorException) as exc_info:
            await browser_manager.create_context()
        
        assert "No browser is currently launched" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_page(self):
        """Test creating page."""
        browser_manager = BrowserManager()
        
        try:
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            assert page is not None
            assert isinstance(page, Page)
            assert not page.is_closed()
            assert len(browser_manager.get_pages()) == 1
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_create_page_with_context(self):
        """Test creating page with specific context."""
        browser_manager = BrowserManager()
        
        try:
            await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            assert page is not None
            assert page.context == context
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_create_multiple_pages(self):
        """Test creating multiple pages."""
        browser_manager = BrowserManager()
        
        try:
            await browser_manager.launch_browser("chromium", headless=True)
            
            page1 = await browser_manager.create_page()
            page2 = await browser_manager.create_page()
            page3 = await browser_manager.create_page()
            
            assert len(browser_manager.get_pages()) == 3
            assert all(not p.is_closed() for p in [page1, page2, page3])
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_create_multiple_contexts(self):
        """Test creating multiple contexts."""
        browser_manager = BrowserManager()
        
        try:
            await browser_manager.launch_browser("chromium", headless=True)
            
            context1 = await browser_manager.create_context()
            context2 = await browser_manager.create_context()
            
            assert len(browser_manager.get_contexts()) == 2
            assert context1 != context2
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_close_browser(self):
        """Test browser cleanup."""
        browser_manager = BrowserManager()
        
        await browser_manager.launch_browser("chromium", headless=True)
        await browser_manager.create_page()
        await browser_manager.create_page()
        
        assert browser_manager.is_browser_launched
        assert len(browser_manager.get_pages()) == 2
        
        await browser_manager.close_browser()
        
        assert not browser_manager.is_browser_launched
        assert browser_manager.browser is None
        assert len(browser_manager.get_contexts()) == 0
        assert len(browser_manager.get_pages()) == 0

    @pytest.mark.asyncio
    async def test_close_browser_idempotent(self):
        """Test that closing browser multiple times doesn't error."""
        browser_manager = BrowserManager()
        
        await browser_manager.launch_browser("chromium", headless=True)
        await browser_manager.close_browser()
        
        # Should not raise exception
        await browser_manager.close_browser()
        
        assert not browser_manager.is_browser_launched

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager functionality."""
        async with BrowserManager() as browser_manager:
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            assert browser_manager.is_browser_launched
            assert page is not None
        
        # Browser should be closed after exiting context
        assert not browser_manager.is_browser_launched

    @pytest.mark.asyncio
    async def test_browser_navigation(self):
        """Test basic browser navigation."""
        browser_manager = BrowserManager()
        
        try:
            await browser_manager.launch_browser("chromium", headless=True)
            page = await browser_manager.create_page()
            
            # Navigate to a page
            await page.goto("https://example.com")
            
            # Verify navigation
            assert "example.com" in page.url
            title = await page.title()
            assert title is not None
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_headless_vs_headed_mode(self):
        """Test both headless and headed modes."""
        browser_manager = BrowserManager()
        
        try:
            # Test headless mode
            await browser_manager.launch_browser("chromium", headless=True)
            assert browser_manager.is_browser_launched
            await browser_manager.close_browser()
            
            # Test headed mode (will still work in CI)
            await browser_manager.launch_browser("chromium", headless=False)
            assert browser_manager.is_browser_launched
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_browser_relaunch(self):
        """Test relaunching browser after closing."""
        browser_manager = BrowserManager()
        
        try:
            # Launch first time
            await browser_manager.launch_browser("chromium", headless=True)
            assert browser_manager.browser_type == "chromium"
            await browser_manager.close_browser()
            
            # Launch second time with different browser
            await browser_manager.launch_browser("firefox", headless=True)
            assert browser_manager.browser_type == "firefox"
            assert browser_manager.is_browser_launched
        finally:
            await browser_manager.close_browser()

    @pytest.mark.asyncio
    async def test_browser_with_custom_config(self):
        """Test browser manager with custom configuration."""
        config = ConfigManager()
        browser_manager = BrowserManager(config=config)
        
        try:
            await browser_manager.launch_browser("chromium", headless=True)
            assert browser_manager.is_browser_launched
        finally:
            await browser_manager.close_browser()


class TestBrowserManagerProperties:
    """Property-based tests for BrowserManager.
    
    These tests validate correctness properties that should hold across
    all valid inputs using property-based testing with Hypothesis.
    """

    @given(
        browser_type=st.sampled_from(["chromium", "firefox", "webkit"]),
        headless=st.booleans()
    )
    @settings(max_examples=100, deadline=60000)  # 100 iterations, 60s timeout per test
    @pytest.mark.asyncio
    async def test_property_browser_launch_consistency(self, browser_type, headless):
        """
        **Feature: raptor-playwright-python, Property 1: Browser Launch Consistency**
        
        Property: For any valid browser type (Chromium, Firefox, WebKit) and any
        headless mode (True/False), launching a browser should result in a valid
        browser instance that can create contexts and pages.
        
        This property validates Requirements 1.1: "WHEN the framework is initialized 
        THEN the system SHALL support Chromium, Firefox, and WebKit browsers"
        
        **Validates: Requirements 1.1**
        
        Test strategy:
        1. Generate random combinations of browser types and headless modes
        2. Launch browser with generated parameters
        3. Verify browser is connected and valid
        4. Verify browser can create contexts
        5. Verify browser can create pages
        6. Verify proper cleanup
        """
        browser_manager = BrowserManager()
        
        try:
            # Step 1: Launch browser with generated parameters
            browser = await browser_manager.launch_browser(browser_type, headless=headless)
            
            # Step 2: Verify browser is valid and connected
            assert browser is not None, \
                f"Browser should not be None for {browser_type} (headless={headless})"
            
            assert isinstance(browser, Browser), \
                f"Browser should be Browser instance for {browser_type} (headless={headless})"
            
            assert browser.is_connected(), \
                f"Browser should be connected for {browser_type} (headless={headless})"
            
            assert browser_manager.is_browser_launched, \
                f"Browser manager should report browser as launched for {browser_type}"
            
            assert browser_manager.browser_type == browser_type.lower(), \
                f"Browser type should be {browser_type.lower()}, got {browser_manager.browser_type}"
            
            # Step 3: Verify browser can create contexts
            context = await browser_manager.create_context()
            assert context is not None, \
                f"Context should be created for {browser_type} (headless={headless})"
            
            assert isinstance(context, BrowserContext), \
                f"Context should be BrowserContext instance for {browser_type}"
            
            assert len(browser_manager.get_contexts()) >= 1, \
                f"At least one context should be tracked for {browser_type}"
            
            # Step 4: Verify browser can create pages
            page = await browser_manager.create_page(context)
            assert page is not None, \
                f"Page should be created for {browser_type} (headless={headless})"
            
            assert isinstance(page, Page), \
                f"Page should be Page instance for {browser_type}"
            
            assert not page.is_closed(), \
                f"Page should not be closed immediately after creation for {browser_type}"
            
            assert len(browser_manager.get_pages()) >= 1, \
                f"At least one page should be tracked for {browser_type}"
            
            # Step 5: Verify page is functional (can navigate)
            # Use a simple data URL to avoid network dependencies
            await page.goto("data:text/html,<h1>Test</h1>")
            assert page.url.startswith("data:"), \
                f"Page should be able to navigate for {browser_type}"
            
        finally:
            # Step 6: Verify proper cleanup
            await browser_manager.close_browser()
            
            assert not browser_manager.is_browser_launched, \
                f"Browser should not be launched after close for {browser_type}"
            
            assert browser_manager.browser is None, \
                f"Browser reference should be None after close for {browser_type}"
            
            assert len(browser_manager.get_contexts()) == 0, \
                f"All contexts should be cleaned up for {browser_type}"
            
            assert len(browser_manager.get_pages()) == 0, \
                f"All pages should be cleaned up for {browser_type}"
