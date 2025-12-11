"""
Example demonstrating Element State and Property Methods (Task 8).

This example shows how to use the new methods:
- get_text() - retrieve element text
- get_attribute() - retrieve attributes
- get_value() - for input values
- get_location() - for element coordinates
- is_selected() - for checkbox/radio state
"""

import asyncio
from playwright.async_api import async_playwright
from raptor.core.element_manager import ElementManager


async def main():
    """Demonstrate element state and property methods."""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Create ElementManager instance
        element_manager = ElementManager(page)
        
        # Navigate to a test page
        await page.goto("https://example.com")
        
        print("=== Element State and Property Methods Demo ===\n")
        
        # 1. Get Text from Element
        print("1. Getting text from heading:")
        heading_text = await element_manager.get_text("css=h1")
        print(f"   Heading text: '{heading_text}'")
        
        paragraph_text = await element_manager.get_text("css=p")
        print(f"   Paragraph text: '{paragraph_text[:50]}...'")
        print()
        
        # 2. Get Attributes from Element
        print("2. Getting attributes from link:")
        link_href = await element_manager.get_attribute("css=a", "href")
        print(f"   Link href: {link_href}")
        
        # Get non-existent attribute (returns None)
        data_attr = await element_manager.get_attribute("css=h1", "data-custom")
        print(f"   Non-existent attribute: {data_attr}")
        print()
        
        # Create a test form for remaining examples
        await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head><title>Test Form</title></head>
        <body>
            <h1>Test Form</h1>
            <form>
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" value="john.doe" />
                
                <label for="email">Email:</label>
                <input type="email" id="email" name="email" value="john@example.com" />
                
                <label for="bio">Bio:</label>
                <textarea id="bio" name="bio">Software Engineer</textarea>
                
                <input type="checkbox" id="terms" name="terms" checked />
                <label for="terms">Accept Terms</label>
                
                <input type="checkbox" id="newsletter" name="newsletter" />
                <label for="newsletter">Subscribe to Newsletter</label>
                
                <input type="radio" id="option1" name="option" value="1" checked />
                <label for="option1">Option 1</label>
                
                <input type="radio" id="option2" name="option" value="2" />
                <label for="option2">Option 2</label>
                
                <button id="submit" type="submit">Submit</button>
            </form>
            
            <div id="positioned" style="position: absolute; left: 100px; top: 300px; width: 200px; height: 100px; background: lightblue;">
                Positioned Element
            </div>
        </body>
        </html>
        """)
        
        # 3. Get Value from Input Elements
        print("3. Getting values from input elements:")
        username = await element_manager.get_value("css=#username")
        print(f"   Username: {username}")
        
        email = await element_manager.get_value("css=#email")
        print(f"   Email: {email}")
        
        bio = await element_manager.get_value("css=#bio")
        print(f"   Bio: {bio}")
        print()
        
        # 4. Modify and Get Updated Value
        print("4. Filling input and getting updated value:")
        await element_manager.fill("css=#username", "jane.smith")
        updated_username = await element_manager.get_value("css=#username")
        print(f"   Updated username: {updated_username}")
        print()
        
        # 5. Get Element Location and Dimensions
        print("5. Getting element location and dimensions:")
        location = await element_manager.get_location("css=#positioned")
        print(f"   Position: x={location['x']}, y={location['y']}")
        print(f"   Size: width={location['width']}, height={location['height']}")
        print()
        
        # 6. Check Selection State (Checkboxes)
        print("6. Checking checkbox selection state:")
        terms_checked = await element_manager.is_selected("css=#terms")
        print(f"   Terms checkbox is checked: {terms_checked}")
        
        newsletter_checked = await element_manager.is_selected("css=#newsletter")
        print(f"   Newsletter checkbox is checked: {newsletter_checked}")
        print()
        
        # 7. Check Selection State (Radio Buttons)
        print("7. Checking radio button selection state:")
        option1_selected = await element_manager.is_selected("css=#option1")
        print(f"   Option 1 is selected: {option1_selected}")
        
        option2_selected = await element_manager.is_selected("css=#option2")
        print(f"   Option 2 is selected: {option2_selected}")
        print()
        
        # 8. Change Selection and Verify
        print("8. Clicking newsletter checkbox and verifying:")
        await element_manager.click("css=#newsletter")
        newsletter_checked_after = await element_manager.is_selected("css=#newsletter")
        print(f"   Newsletter checkbox is now checked: {newsletter_checked_after}")
        print()
        
        # 9. Using Fallback Locators
        print("9. Using fallback locators:")
        text_with_fallback = await element_manager.get_text(
            "css=#nonexistent",
            fallback_locators=["css=h1", "xpath=//h1"]
        )
        print(f"   Text retrieved with fallback: '{text_with_fallback}'")
        
        value_with_fallback = await element_manager.get_value(
            "css=#wrong-id",
            fallback_locators=["css=#email", "xpath=//input[@name='email']"]
        )
        print(f"   Value retrieved with fallback: {value_with_fallback}")
        print()
        
        # 10. Get Multiple Attributes
        print("10. Getting multiple attributes from submit button:")
        button_id = await element_manager.get_attribute("css=#submit", "id")
        button_type = await element_manager.get_attribute("css=#submit", "type")
        print(f"   Button ID: {button_id}")
        print(f"   Button type: {button_type}")
        print()
        
        print("=== Demo Complete ===")
        
        # Keep browser open for a moment to see results
        await asyncio.sleep(2)
        
        # Cleanup
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
