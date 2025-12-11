"""
Example demonstrating basic element interaction methods in RAPTOR.

This example shows how to use the ElementManager to:
- Click elements
- Fill text inputs
- Select dropdown options
- Hover over elements
- Check element state (enabled/disabled)
"""

import asyncio
from playwright.async_api import async_playwright
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager


async def main():
    """Demonstrate basic element interactions."""
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Create ElementManager
        config = ConfigManager()
        element_manager = ElementManager(page, config)
        
        # Create a test page with various interactive elements
        await page.set_content("""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Element Interaction Demo</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; }
                    .container { max-width: 600px; margin: 0 auto; }
                    .form-group { margin-bottom: 15px; }
                    label { display: block; margin-bottom: 5px; font-weight: bold; }
                    input, select { width: 100%; padding: 8px; box-sizing: border-box; }
                    button { padding: 10px 20px; background: #007bff; color: white; 
                             border: none; cursor: pointer; margin-right: 10px; }
                    button:hover { background: #0056b3; }
                    button:disabled { background: #ccc; cursor: not-allowed; }
                    .hover-demo { padding: 20px; background: #f0f0f0; margin: 20px 0; }
                    .hover-demo:hover { background: #007bff; color: white; }
                    .result { margin-top: 20px; padding: 10px; background: #e7f3ff; 
                              border-left: 4px solid #007bff; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>RAPTOR Element Interaction Demo</h1>
                    
                    <div class="form-group">
                        <label for="username">Username:</label>
                        <input id="username" type="text" placeholder="Enter username" />
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input id="email" type="email" placeholder="Enter email" />
                    </div>
                    
                    <div class="form-group">
                        <label for="country">Country:</label>
                        <select id="country">
                            <option value="">Select a country</option>
                            <option value="us">United States</option>
                            <option value="uk">United Kingdom</option>
                            <option value="ca">Canada</option>
                            <option value="au">Australia</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <button id="submit-btn" onclick="handleSubmit()">Submit</button>
                        <button id="disabled-btn" disabled>Disabled Button</button>
                    </div>
                    
                    <div class="hover-demo" id="hover-target">
                        Hover over me to see the effect!
                    </div>
                    
                    <div id="result" class="result" style="display: none;">
                        <h3>Form Submitted!</h3>
                        <p id="result-text"></p>
                    </div>
                </div>
                
                <script>
                    function handleSubmit() {
                        const username = document.getElementById('username').value;
                        const email = document.getElementById('email').value;
                        const country = document.getElementById('country').value;
                        
                        const resultDiv = document.getElementById('result');
                        const resultText = document.getElementById('result-text');
                        
                        resultText.innerHTML = `
                            <strong>Username:</strong> ${username}<br>
                            <strong>Email:</strong> ${email}<br>
                            <strong>Country:</strong> ${country}
                        `;
                        
                        resultDiv.style.display = 'block';
                    }
                </script>
            </body>
            </html>
        """)
        
        print("=== RAPTOR Element Interaction Demo ===\n")
        
        # 1. Fill text inputs
        print("1. Filling text inputs...")
        await element_manager.fill("css=#username", "john.doe")
        print("   ✓ Filled username: john.doe")
        
        await element_manager.fill("css=#email", "john.doe@example.com")
        print("   ✓ Filled email: john.doe@example.com")
        
        await asyncio.sleep(1)  # Pause to see the effect
        
        # 2. Select dropdown option
        print("\n2. Selecting dropdown option...")
        await element_manager.select_option("css=#country", value="ca")
        print("   ✓ Selected country: Canada")
        
        await asyncio.sleep(1)
        
        # 3. Hover over element
        print("\n3. Hovering over element...")
        await element_manager.hover("css=#hover-target")
        print("   ✓ Hovered over demo element")
        
        await asyncio.sleep(1)
        
        # 4. Check element states
        print("\n4. Checking element states...")
        submit_enabled = await element_manager.is_enabled("css=#submit-btn")
        print(f"   ✓ Submit button enabled: {submit_enabled}")
        
        disabled_enabled = await element_manager.is_enabled("css=#disabled-btn")
        print(f"   ✓ Disabled button enabled: {disabled_enabled}")
        
        await asyncio.sleep(1)
        
        # 5. Click button
        print("\n5. Clicking submit button...")
        await element_manager.click("css=#submit-btn")
        print("   ✓ Clicked submit button")
        
        await asyncio.sleep(2)
        
        # 6. Verify result
        print("\n6. Verifying form submission...")
        result_visible = await element_manager.is_visible("css=#result")
        print(f"   ✓ Result displayed: {result_visible}")
        
        # 7. Demonstrate fallback locators
        print("\n7. Testing fallback locators...")
        await element_manager.click(
            "css=#nonexistent-button",
            fallback_locators=["css=#submit-btn"],
            timeout=2000
        )
        print("   ✓ Clicked button using fallback locator")
        
        print("\n=== Demo Complete ===")
        print("\nPress Enter to close the browser...")
        
        # Keep browser open for inspection
        await asyncio.sleep(5)
        
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
