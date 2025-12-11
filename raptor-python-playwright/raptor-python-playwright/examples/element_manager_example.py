"""
Element Manager Example

This example demonstrates the usage of ElementManager for locating elements
with primary and fallback locators.
"""

import asyncio
from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager


async def main():
    """Demonstrate ElementManager functionality."""
    
    # Initialize managers
    config = ConfigManager()
    browser_manager = BrowserManager(config)
    
    try:
        # Launch browser
        print("Launching browser...")
        await browser_manager.launch_browser("chromium", headless=False)
        
        # Create context and page
        context = await browser_manager.create_context()
        page = await browser_manager.create_page(context)
        
        # Initialize ElementManager
        element_manager = ElementManager(page, config)
        
        # Navigate to a test page
        print("\nNavigating to example.com...")
        await page.goto("https://example.com")
        
        # Example 1: Locate element with CSS selector
        print("\n--- Example 1: Basic CSS Locator ---")
        try:
            element = await element_manager.locate_element("css=h1")
            text = await element.text_content()
            print(f"✓ Found element with text: {text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Example 2: Locate element with fallback locators
        print("\n--- Example 2: Fallback Locators ---")
        try:
            element = await element_manager.locate_element(
                "css=#nonexistent-id",  # This will fail
                fallback_locators=[
                    "xpath=//h1",  # This should succeed
                    "text=Example Domain"
                ]
            )
            text = await element.text_content()
            print(f"✓ Found element using fallback: {text}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Example 3: Wait for element with specific state
        print("\n--- Example 3: Wait for Element ---")
        try:
            element = await element_manager.wait_for_element(
                "css=p",
                state="visible",
                timeout=5000
            )
            text = await element.text_content()
            print(f"✓ Element is visible: {text[:50]}...")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Example 4: Check element visibility
        print("\n--- Example 4: Check Visibility ---")
        is_visible = await element_manager.is_visible("css=h1")
        print(f"✓ H1 element is visible: {is_visible}")
        
        is_hidden = await element_manager.is_hidden("css=#nonexistent")
        print(f"✓ Nonexistent element is hidden: {is_hidden}")
        
        # Example 5: Count elements
        print("\n--- Example 5: Count Elements ---")
        count = await element_manager.get_element_count("css=p")
        print(f"✓ Found {count} paragraph elements")
        
        # Example 6: Different locator strategies
        print("\n--- Example 6: Different Locator Strategies ---")
        
        # Text locator
        try:
            element = await element_manager.locate_element("text=Example Domain")
            print("✓ Found element using text locator")
        except Exception as e:
            print(f"✗ Text locator failed: {e}")
        
        # XPath locator
        try:
            element = await element_manager.locate_element("xpath=//h1")
            print("✓ Found element using XPath locator")
        except Exception as e:
            print(f"✗ XPath locator failed: {e}")
        
        # Example 7: Custom timeout
        print("\n--- Example 7: Custom Timeout ---")
        try:
            element = await element_manager.locate_element(
                "css=h1",
                timeout=2000  # 2 second timeout
            )
            print("✓ Found element with custom timeout")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Example 8: Element not found scenario
        print("\n--- Example 8: Element Not Found ---")
        try:
            element = await element_manager.locate_element(
                "css=#definitely-does-not-exist",
                fallback_locators=["xpath=//div[@id='also-not-there']"],
                timeout=2000
            )
            print("✗ This should not print")
        except Exception as e:
            print(f"✓ Expected error caught: {type(e).__name__}")
        
        print("\n--- All Examples Complete ---")
        
        # Keep browser open for a moment to see results
        await asyncio.sleep(2)
        
    finally:
        # Clean up
        print("\nClosing browser...")
        await browser_manager.close_browser()
        print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
