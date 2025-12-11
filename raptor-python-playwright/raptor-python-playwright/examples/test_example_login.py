"""
Example Login Test

This example demonstrates a complete login workflow using the RAPTOR framework.
It shows how to:
- Use the browser manager to launch a browser
- Navigate to a login page
- Interact with form elements
- Verify successful login
- Handle session management

Requirements: NFR-004
"""

import pytest
from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.pages.base_page import BasePage


@pytest.mark.asyncio
class TestLoginExample:
    """Example test class demonstrating login functionality"""
    
    async def test_successful_login(self):
        """
        Test successful login with valid credentials
        
        This example shows:
        1. Browser initialization
        2. Page navigation
        3. Form filling
        4. Button clicking
        5. Verification of successful login
        """
        # Initialize components
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            # Launch browser
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            # Initialize managers
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            
            # Navigate to login page
            await base_page.navigate("https://example.com/login")
            await base_page.wait_for_load()
            
            # Fill in login credentials
            await element_manager.fill("css=#username", "testuser@example.com")
            await element_manager.fill("css=#password", "SecurePassword123!")
            
            # Click login button
            await element_manager.click("css=#login-button")
            
            # Wait for navigation after login
            await page.wait_for_url("**/dashboard", timeout=10000)
            
            # Verify successful login
            assert await element_manager.is_visible("css=.welcome-message")
            welcome_text = await element_manager.get_text("css=.welcome-message")
            assert "Welcome" in welcome_text
            
            # Take screenshot for documentation
            await base_page.take_screenshot("successful_login")
            
        finally:
            # Clean up
            await browser_manager.close_browser()
    
    async def test_login_with_invalid_credentials(self):
        """
        Test login failure with invalid credentials
        
        This example shows:
        1. Error message verification
        2. Negative testing
        3. Soft assertions for multiple checks
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            
            # Navigate to login page
            await base_page.navigate("https://example.com/login")
            
            # Attempt login with invalid credentials
            await element_manager.fill("css=#username", "invalid@example.com")
            await element_manager.fill("css=#password", "WrongPassword")
            await element_manager.click("css=#login-button")
            
            # Wait for error message
            await element_manager.wait_for_element("css=.error-message", timeout=5000)
            
            # Verify error message is displayed
            assert await element_manager.is_visible("css=.error-message")
            error_text = await element_manager.get_text("css=.error-message")
            assert "Invalid credentials" in error_text or "Login failed" in error_text
            
            # Verify still on login page
            current_url = await base_page.get_url()
            assert "/login" in current_url
            
        finally:
            await browser_manager.close_browser()
    
    async def test_login_with_remember_me(self):
        """
        Test login with "Remember Me" functionality
        
        This example shows:
        1. Checkbox interaction
        2. Cookie/storage verification
        3. Session persistence
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            
            # Navigate and login
            await base_page.navigate("https://example.com/login")
            await element_manager.fill("css=#username", "testuser@example.com")
            await element_manager.fill("css=#password", "SecurePassword123!")
            
            # Check "Remember Me" checkbox
            remember_me_locator = "css=#remember-me"
            if not await element_manager.is_selected(remember_me_locator):
                await element_manager.click(remember_me_locator)
            
            # Verify checkbox is selected
            assert await element_manager.is_selected(remember_me_locator)
            
            # Submit login
            await element_manager.click("css=#login-button")
            await page.wait_for_url("**/dashboard", timeout=10000)
            
            # Verify session cookie is set
            cookies = await context.cookies()
            session_cookie = next((c for c in cookies if c['name'] == 'session_token'), None)
            assert session_cookie is not None
            
        finally:
            await browser_manager.close_browser()
    
    async def test_login_with_keyboard_navigation(self):
        """
        Test login using keyboard navigation
        
        This example shows:
        1. Keyboard interaction (Tab, Enter)
        2. Accessibility testing
        3. Alternative interaction methods
        """
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            
            # Navigate to login page
            await base_page.navigate("https://example.com/login")
            
            # Focus on username field
            await page.locator("css=#username").focus()
            await page.keyboard.type("testuser@example.com")
            
            # Tab to password field
            await page.keyboard.press("Tab")
            await page.keyboard.type("SecurePassword123!")
            
            # Tab to login button and press Enter
            await page.keyboard.press("Tab")
            await page.keyboard.press("Enter")
            
            # Verify login success
            await page.wait_for_url("**/dashboard", timeout=10000)
            assert "/dashboard" in await base_page.get_url()
            
        finally:
            await browser_manager.close_browser()


@pytest.mark.asyncio
async def test_login_with_session_reuse():
    """
    Standalone test demonstrating session reuse
    
    This example shows:
    1. Saving a browser session after login
    2. Reusing the session in a subsequent test
    3. Avoiding repeated login steps
    """
    from raptor.core.session_manager import SessionManager
    
    config = ConfigManager()
    browser_manager = BrowserManager(config)
    session_manager = SessionManager(config)
    
    try:
        # First login - create and save session
        browser = await browser_manager.launch_browser("chromium", headless=True)
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)
        
        element_manager = ElementManager(page, config)
        base_page = BasePage(page, element_manager)
        
        # Perform login
        await base_page.navigate("https://example.com/login")
        await element_manager.fill("css=#username", "testuser@example.com")
        await element_manager.fill("css=#password", "SecurePassword123!")
        await element_manager.click("css=#login-button")
        await page.wait_for_url("**/dashboard", timeout=10000)
        
        # Save session for reuse
        await session_manager.save_session(page, "login_session_example")
        
        # Close browser
        await browser_manager.close_browser()
        
        # Reuse session - no login required
        restored_page = await session_manager.restore_session("login_session_example")
        
        # Verify we're still logged in
        current_url = restored_page.url
        assert "/dashboard" in current_url
        
        # Can now continue with test actions without logging in again
        element_manager_restored = ElementManager(restored_page, config)
        assert await element_manager_restored.is_visible("css=.welcome-message")
        
    finally:
        # Cleanup
        await session_manager.delete_session("login_session_example")
        await browser_manager.close_browser()


if __name__ == "__main__":
    """
    Run this example directly:
    python examples/test_example_login.py
    
    Or with pytest:
    pytest examples/test_example_login.py -v
    """
    pytest.main([__file__, "-v", "-s"])
