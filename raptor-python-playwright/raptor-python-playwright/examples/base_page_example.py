"""
Example demonstrating BasePage usage in RAPTOR Python Playwright Framework.

This example shows how to:
1. Create a custom page object inheriting from BasePage
2. Navigate to URLs and wait for page load
3. Capture screenshots for debugging
4. Execute JavaScript in the page context
5. Use page navigation methods (back, forward, reload)
"""

import asyncio
from playwright.async_api import async_playwright
from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.pages.base_page import BasePage


class ExamplePage(BasePage):
    """
    Example page object demonstrating BasePage inheritance.
    
    This shows how to create a custom page object with specific
    locators and methods for a particular page.
    """
    
    def __init__(self, page, element_manager=None):
        super().__init__(page, element_manager)
        
        # Define page-specific locators
        self.search_input = "css=input[name='q']"
        self.search_button = "css=button[type='submit']"
        self.results_container = "css=#search-results"
    
    async def search(self, query: str):
        """Perform a search on the page."""
        await self.element_manager.fill(self.search_input, query)
        await self.element_manager.click(self.search_button)
        await self.wait_for_load(state="networkidle")


async def main():
    """Main example demonstrating BasePage functionality."""
    
    # Initialize browser manager
    browser_manager = BrowserManager()
    
    try:
        # Launch browser
        print("Launching browser...")
        await browser_manager.launch_browser("chromium", headless=False)
        
        # Create context and page
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)
        
        # Create element manager and base page
        element_manager = ElementManager(page)
        base_page = BasePage(page, element_manager)
        
        # Example 1: Navigate to a URL
        print("\n=== Example 1: Navigation ===")
        await base_page.navigate("https://example.com")
        print(f"Navigated to: {await base_page.get_url()}")
        print(f"Page title: {await base_page.get_title()}")
        
        # Example 2: Take a screenshot
        print("\n=== Example 2: Screenshot ===")
        screenshot_path = await base_page.take_screenshot("example_page")
        print(f"Screenshot saved to: {screenshot_path}")
        
        # Example 3: Execute JavaScript
        print("\n=== Example 3: JavaScript Execution ===")
        
        # Get page dimensions
        dimensions = await base_page.execute_script(
            "return {width: window.innerWidth, height: window.innerHeight}"
        )
        print(f"Page dimensions: {dimensions}")
        
        # Scroll to bottom
        await base_page.execute_script(
            "window.scrollTo(0, document.body.scrollHeight)"
        )
        print("Scrolled to bottom of page")
        
        # Get element count
        heading_count = await base_page.execute_script(
            "return document.querySelectorAll('h1').length"
        )
        print(f"Number of H1 elements: {heading_count}")
        
        # Example 4: Navigate to another page
        print("\n=== Example 4: Multi-page Navigation ===")
        await base_page.navigate("https://playwright.dev")
        print(f"Navigated to: {await base_page.get_url()}")
        
        # Go back
        await base_page.go_back()
        print(f"Went back to: {await base_page.get_url()}")
        
        # Go forward
        await base_page.go_forward()
        print(f"Went forward to: {await base_page.get_url()}")
        
        # Example 5: Reload page
        print("\n=== Example 5: Page Reload ===")
        await base_page.reload()
        print("Page reloaded successfully")
        
        # Example 6: Using custom page object
        print("\n=== Example 6: Custom Page Object ===")
        custom_page = ExamplePage(page, element_manager)
        await custom_page.navigate("https://example.com")
        print(f"Custom page loaded: {await custom_page.get_title()}")
        
        # Example 7: Full page screenshot
        print("\n=== Example 7: Full Page Screenshot ===")
        full_screenshot = await base_page.take_screenshot(
            "full_page_example",
            full_page=True
        )
        print(f"Full page screenshot saved to: {full_screenshot}")
        
        # Example 8: Wait for different load states
        print("\n=== Example 8: Load State Management ===")
        await base_page.navigate("https://example.com", wait_until="domcontentloaded")
        print("Waited for DOMContentLoaded")
        
        await base_page.wait_for_load(state="networkidle")
        print("Waited for network idle")
        
        # Example 9: JavaScript with arguments
        print("\n=== Example 9: JavaScript with Arguments ===")
        result = await base_page.execute_script(
            "return arguments[0] + arguments[1]",
            10,
            20
        )
        print(f"JavaScript calculation result: {result}")
        
        # Set and get local storage
        await base_page.execute_script(
            "localStorage.setItem(arguments[0], arguments[1])",
            "test_key",
            "test_value"
        )
        stored_value = await base_page.execute_script(
            "return localStorage.getItem(arguments[0])",
            "test_key"
        )
        print(f"Local storage value: {stored_value}")
        
        print("\n=== All Examples Completed Successfully ===")
        
        # Keep browser open for a moment to see results
        await asyncio.sleep(2)
        
    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        print("\nClosing browser...")
        await browser_manager.close_browser()
        print("Browser closed")


if __name__ == "__main__":
    asyncio.run(main())
