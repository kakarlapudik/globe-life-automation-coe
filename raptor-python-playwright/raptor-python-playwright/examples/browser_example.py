"""
Example demonstrating BrowserManager usage.

This example shows how to:
1. Launch different browsers (Chromium, Firefox, WebKit)
2. Create browser contexts
3. Create pages
4. Navigate to URLs
5. Properly clean up resources
"""

import asyncio
from raptor.core import BrowserManager, ConfigManager


async def basic_browser_example():
    """Basic example of launching a browser and navigating to a page."""
    print("=== Basic Browser Example ===\n")
    
    # Create browser manager
    browser_manager = BrowserManager()
    
    try:
        # Launch Chromium browser in headed mode
        print("Launching Chromium browser...")
        await browser_manager.launch_browser("chromium", headless=False)
        print(f"Browser launched: {browser_manager.is_browser_launched}")
        
        # Create a page
        print("\nCreating page...")
        page = await browser_manager.create_page()
        
        # Navigate to a URL
        print("Navigating to example.com...")
        await page.goto("https://example.com")
        print(f"Page title: {await page.title()}")
        
        # Wait a bit to see the page
        await asyncio.sleep(2)
        
    finally:
        # Clean up
        print("\nClosing browser...")
        await browser_manager.close_browser()
        print("Browser closed successfully")


async def multiple_contexts_example():
    """Example showing multiple isolated browser contexts."""
    print("\n=== Multiple Contexts Example ===\n")
    
    browser_manager = BrowserManager()
    
    try:
        # Launch browser
        print("Launching Firefox browser...")
        await browser_manager.launch_browser("firefox", headless=True)
        
        # Create first context with custom viewport
        print("\nCreating first context (desktop viewport)...")
        context1 = await browser_manager.create_context(
            viewport={"width": 1920, "height": 1080}
        )
        page1 = await browser_manager.create_page(context1)
        await page1.goto("https://example.com")
        print(f"Context 1 - Page title: {await page1.title()}")
        
        # Create second context with mobile viewport
        print("\nCreating second context (mobile viewport)...")
        context2 = await browser_manager.create_context(
            viewport={"width": 375, "height": 667},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        )
        page2 = await browser_manager.create_page(context2)
        await page2.goto("https://example.com")
        print(f"Context 2 - Page title: {await page2.title()}")
        
        print(f"\nTotal contexts: {len(browser_manager.get_contexts())}")
        print(f"Total pages: {len(browser_manager.get_pages())}")
        
    finally:
        print("\nClosing browser and all contexts...")
        await browser_manager.close_browser()
        print("Cleanup completed")


async def context_manager_example():
    """Example using async context manager for automatic cleanup."""
    print("\n=== Context Manager Example ===\n")
    
    # Using async context manager ensures cleanup even if errors occur
    async with BrowserManager() as browser_manager:
        print("Launching WebKit browser...")
        await browser_manager.launch_browser("webkit", headless=True)
        
        print("Creating page...")
        page = await browser_manager.create_page()
        
        print("Navigating to example.com...")
        await page.goto("https://example.com")
        print(f"Page title: {await page.title()}")
        
        # Browser will be automatically closed when exiting the context
        print("\nExiting context manager (automatic cleanup)...")


async def browser_options_example():
    """Example showing custom browser launch options."""
    print("\n=== Browser Options Example ===\n")
    
    browser_manager = BrowserManager()
    
    try:
        # Launch with custom options
        print("Launching Chromium with custom options...")
        await browser_manager.launch_browser(
            "chromium",
            headless=False,
            args=[
                "--start-maximized",
                "--disable-blink-features=AutomationControlled"
            ],
            slow_mo=100  # Slow down operations by 100ms for visibility
        )
        
        print("Creating page...")
        page = await browser_manager.create_page()
        
        print("Navigating to example.com...")
        await page.goto("https://example.com")
        
        # Take a screenshot
        print("Taking screenshot...")
        await page.screenshot(path="example_screenshot.png")
        print("Screenshot saved as example_screenshot.png")
        
        await asyncio.sleep(2)
        
    finally:
        print("\nClosing browser...")
        await browser_manager.close_browser()


async def error_handling_example():
    """Example showing error handling."""
    print("\n=== Error Handling Example ===\n")
    
    browser_manager = BrowserManager()
    
    try:
        # Try to launch invalid browser type
        print("Attempting to launch invalid browser type...")
        await browser_manager.launch_browser("invalid_browser")
    except Exception as e:
        print(f"Caught expected error: {e.__class__.__name__}")
        print(f"Error message: {str(e)}")
    
    try:
        # Try to create page without launching browser
        print("\nAttempting to create page without launching browser...")
        await browser_manager.create_page()
    except Exception as e:
        print(f"Caught expected error: {e.__class__.__name__}")
        print(f"Error message: {str(e)}")


async def main():
    """Run all examples."""
    print("RAPTOR Browser Manager Examples")
    print("=" * 50)
    
    # Run examples
    await basic_browser_example()
    await multiple_contexts_example()
    await context_manager_example()
    await browser_options_example()
    await error_handling_example()
    
    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
