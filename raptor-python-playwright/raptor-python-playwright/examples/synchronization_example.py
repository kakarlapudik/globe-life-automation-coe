"""
Example demonstrating synchronization methods in RAPTOR.

This example shows how to use various synchronization methods to handle
dynamic page loading, spinners, modals, and network activity.
"""

import asyncio
from playwright.async_api import async_playwright
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager


async def main():
    """Demonstrate synchronization methods."""
    
    # Initialize Playwright
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Initialize ElementManager
        config = ConfigManager()
        element_manager = ElementManager(page, config)
        
        print("=== RAPTOR Synchronization Methods Demo ===\n")
        
        # Example 1: Wait for page load state
        print("1. Waiting for page load state...")
        await page.goto("https://example.com")
        await element_manager.wait_for_load_state("load")
        print("   ✓ Page loaded successfully\n")
        
        # Example 2: Wait for DOM content loaded
        print("2. Waiting for DOM content loaded...")
        await page.goto("https://example.com")
        await element_manager.wait_for_load_state("domcontentloaded")
        print("   ✓ DOM content loaded\n")
        
        # Example 3: Wait for network idle
        print("3. Waiting for network idle...")
        await page.goto("https://example.com")
        await element_manager.wait_for_network_idle(timeout=10000)
        print("   ✓ Network is idle\n")
        
        # Example 4: Wait for spinner to disappear
        print("4. Demonstrating spinner wait...")
        spinner_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Spinner Demo</title>
            <style>
                #spinner {
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    font-size: 24px;
                    color: #007bff;
                }
                #content {
                    display: none;
                    padding: 20px;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div id="spinner">⏳ Loading...</div>
            <div id="content">
                <h1>Content Loaded!</h1>
                <p>The spinner has disappeared.</p>
            </div>
            <script>
                setTimeout(() => {
                    document.getElementById('spinner').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                }, 3000);
            </script>
        </body>
        </html>
        """
        
        await page.set_content(spinner_html)
        print("   Waiting for spinner to disappear (3 seconds)...")
        await element_manager.wait_for_spinner("css=#spinner", timeout=10000)
        print("   ✓ Spinner disappeared\n")
        
        # Example 5: Wait for modal/disabled pane
        print("5. Demonstrating modal wait...")
        modal_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Modal Demo</title>
            <style>
                .modal-backdrop {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .modal-content {
                    background: white;
                    padding: 20px;
                    border-radius: 5px;
                }
                #main-content {
                    display: none;
                    padding: 20px;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div class="modal-backdrop">
                <div class="modal-content">
                    <h2>Loading Modal</h2>
                    <p>Please wait...</p>
                </div>
            </div>
            <div id="main-content">
                <h1>Main Content</h1>
                <p>Modal has been closed.</p>
            </div>
            <script>
                setTimeout(() => {
                    document.querySelector('.modal-backdrop').style.display = 'none';
                    document.getElementById('main-content').style.display = 'block';
                }, 3000);
            </script>
        </body>
        </html>
        """
        
        await page.set_content(modal_html)
        print("   Waiting for modal to close (3 seconds)...")
        await element_manager.wait_for_disabled_pane("css=.modal-backdrop", timeout=10000)
        print("   ✓ Modal closed\n")
        
        # Example 6: Wait for modal using default selectors
        print("6. Demonstrating modal wait with default selectors...")
        await page.set_content(modal_html)
        print("   Waiting for modal using default selectors...")
        await element_manager.wait_for_disabled_pane(timeout=10000)
        print("   ✓ Modal detected and closed using default selectors\n")
        
        # Example 7: Combined synchronization workflow
        print("7. Demonstrating combined synchronization workflow...")
        complex_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Complex Loading Demo</title>
            <style>
                #loading-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.8);
                    color: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                }
                #content {
                    display: none;
                    padding: 20px;
                }
            </style>
        </head>
        <body>
            <div id="loading-overlay">
                <div>
                    <div id="spinner">⏳ Loading data...</div>
                </div>
            </div>
            <div id="content">
                <h1>Data Loaded</h1>
                <div id="data-container"></div>
            </div>
            <script>
                // Simulate AJAX request
                setTimeout(() => {
                    fetch('https://jsonplaceholder.typicode.com/todos/1')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('loading-overlay').style.display = 'none';
                            document.getElementById('content').style.display = 'block';
                            document.getElementById('data-container').textContent = 
                                'Loaded: ' + data.title;
                        });
                }, 2000);
            </script>
        </body>
        </html>
        """
        
        await page.set_content(complex_html)
        
        print("   Step 1: Wait for page load...")
        await element_manager.wait_for_load_state("load")
        print("   ✓ Page loaded")
        
        print("   Step 2: Wait for loading overlay to disappear...")
        await element_manager.wait_for_disabled_pane("css=#loading-overlay", timeout=10000)
        print("   ✓ Loading overlay disappeared")
        
        print("   Step 3: Wait for network idle...")
        await element_manager.wait_for_network_idle(timeout=10000)
        print("   ✓ Network is idle")
        
        print("   Step 4: Verify content is loaded...")
        content = await element_manager.get_text("css=#data-container")
        print(f"   ✓ Content loaded: {content}\n")
        
        # Example 8: Handling timeouts gracefully
        print("8. Demonstrating timeout handling...")
        timeout_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Timeout Demo</title>
        </head>
        <body>
            <div id="persistent-spinner" style="display: block;">
                This spinner never disappears...
            </div>
        </body>
        </html>
        """
        
        await page.set_content(timeout_html)
        
        try:
            print("   Attempting to wait for spinner that never disappears...")
            await element_manager.wait_for_spinner(
                "css=#persistent-spinner",
                timeout=3000
            )
        except Exception as e:
            print(f"   ✓ Timeout handled gracefully: {type(e).__name__}\n")
        
        print("=== Demo Complete ===")
        
        # Keep browser open for a moment
        await asyncio.sleep(2)
        
        # Cleanup
        await context.close()
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
