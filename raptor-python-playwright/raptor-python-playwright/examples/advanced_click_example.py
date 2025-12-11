"""
Advanced Click Methods Example

This example demonstrates all five advanced click methods in the RAPTOR framework:
1. click_at_position() - Click at specific coordinates
2. double_click() - Double-click elements
3. right_click() - Right-click for context menus
4. click_if_exists() - Conditional clicking
5. click_with_retry() - Retry with exponential backoff
"""

import asyncio
from playwright.async_api import async_playwright
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager


async def example_click_at_position():
    """Example: Click at specific position within an element."""
    print("\n=== Example 1: click_at_position() ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Create test page with canvas
        await page.set_content("""
            <!DOCTYPE html>
            <html>
            <head><title>Position Click Example</title></head>
            <body>
                <h2>Click on the canvas at different positions</h2>
                <canvas id="drawing-canvas" width="400" height="300" 
                        style="border: 1px solid black;"></canvas>
                <div id="click-log"></div>
                <script>
                    const canvas = document.getElementById('drawing-canvas');
                    const ctx = canvas.getContext('2d');
                    const log = document.getElementById('click-log');
                    
                    canvas.addEventListener('click', (e) => {
                        const rect = canvas.getBoundingClientRect();
                        const x = e.clientX - rect.left;
                        const y = e.clientY - rect.top;
                        
                        // Draw a circle at click position
                        ctx.fillStyle = 'blue';
                        ctx.beginPath();
                        ctx.arc(x, y, 5, 0, 2 * Math.PI);
                        ctx.fill();
                        
                        log.innerHTML += `<p>Clicked at (${Math.round(x)}, ${Math.round(y)})</p>`;
                    });
                </script>
            </body>
            </html>
        """)
        
        element_manager = ElementManager(page, ConfigManager())
        
        # Click at different positions on the canvas
        print("Clicking at position (100, 50)...")
        await element_manager.click_at_position("css=#drawing-canvas", x=100, y=50)
        await asyncio.sleep(0.5)
        
        print("Clicking at position (200, 150)...")
        await element_manager.click_at_position("css=#drawing-canvas", x=200, y=150)
        await asyncio.sleep(0.5)
        
        print("Clicking at position (300, 100)...")
        await element_manager.click_at_position("css=#drawing-canvas", x=300, y=100)
        await asyncio.sleep(2)
        
        await browser.close()
        print("✓ Position clicking completed successfully")


async def example_double_click():
    """Example: Double-click to select text or open items."""
    print("\n=== Example 2: double_click() ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Create test page with double-clickable elements
        await page.set_content("""
            <!DOCTYPE html>
            <html>
            <head><title>Double Click Example</title></head>
            <body>
                <h2>Double-click examples</h2>
                
                <div style="margin: 20px;">
                    <h3>File Explorer</h3>
                    <div id="file-item" style="padding: 10px; border: 1px solid gray; 
                                               width: 200px; cursor: pointer;">
                        📄 Document.txt
                    </div>
                    <div id="file-status"></div>
                </div>
                
                <div style="margin: 20px;">
                    <h3>Text Selection</h3>
                    <p id="text-content" style="padding: 10px; border: 1px solid gray;">
                        Double-click this text to select it
                    </p>
                </div>
                
                <script>
                    document.getElementById('file-item').addEventListener('dblclick', () => {
                        document.getElementById('file-status').innerHTML = 
                            '<p style="color: green;">✓ File opened!</p>';
                    });
                </script>
            </body>
            </html>
        """)
        
        element_manager = ElementManager(page, ConfigManager())
        
        # Double-click to open file
        print("Double-clicking file item...")
        await element_manager.double_click("css=#file-item")
        await asyncio.sleep(1)
        
        # Double-click to select text
        print("Double-clicking text to select...")
        await element_manager.double_click("css=#text-content")
        await asyncio.sleep(2)
        
        await browser.close()
        print("✓ Double-clicking completed successfully")


async def example_right_click():
    """Example: Right-click to open context menu."""
    print("\n=== Example 3: right_click() ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Create test page with context menu
        await page.set_content("""
            <!DOCTYPE html>
            <html>
            <head><title>Right Click Example</title></head>
            <body>
                <h2>Right-click to open context menu</h2>
                
                <div id="context-target" style="padding: 20px; border: 1px solid gray; 
                                                width: 300px; margin: 20px;">
                    Right-click me to see the context menu
                </div>
                
                <div id="context-menu" style="display: none; position: absolute; 
                                              background: white; border: 1px solid black; 
                                              padding: 10px;">
                    <div class="menu-item" style="padding: 5px; cursor: pointer;">Copy</div>
                    <div class="menu-item" style="padding: 5px; cursor: pointer;">Paste</div>
                    <div class="menu-item" style="padding: 5px; cursor: pointer;">Delete</div>
                </div>
                
                <div id="action-log"></div>
                
                <script>
                    const target = document.getElementById('context-target');
                    const menu = document.getElementById('context-menu');
                    const log = document.getElementById('action-log');
                    
                    target.addEventListener('contextmenu', (e) => {
                        e.preventDefault();
                        menu.style.display = 'block';
                        menu.style.left = e.pageX + 'px';
                        menu.style.top = e.pageY + 'px';
                        log.innerHTML = '<p style="color: green;">✓ Context menu opened!</p>';
                    });
                    
                    document.addEventListener('click', () => {
                        menu.style.display = 'none';
                    });
                    
                    document.querySelectorAll('.menu-item').forEach(item => {
                        item.addEventListener('click', () => {
                            log.innerHTML += `<p>Selected: ${item.textContent}</p>`;
                        });
                    });
                </script>
            </body>
            </html>
        """)
        
        element_manager = ElementManager(page, ConfigManager())
        
        # Right-click to open context menu
        print("Right-clicking to open context menu...")
        await element_manager.right_click("css=#context-target")
        await asyncio.sleep(1)
        
        # Click a menu item
        print("Clicking menu item...")
        await element_manager.click("text=Copy")
        await asyncio.sleep(2)
        
        await browser.close()
        print("✓ Right-clicking completed successfully")


async def example_click_if_exists():
    """Example: Conditionally click optional elements."""
    print("\n=== Example 4: click_if_exists() ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Create test page with optional popup
        await page.set_content("""
            <!DOCTYPE html>
            <html>
            <head><title>Conditional Click Example</title></head>
            <body>
                <h2>Conditional clicking of optional elements</h2>
                
                <button id="show-popup">Show Popup</button>
                <button id="show-banner">Show Banner</button>
                
                <div id="popup" style="display: none; position: fixed; top: 50%; left: 50%; 
                                       transform: translate(-50%, -50%); background: white; 
                                       border: 2px solid black; padding: 20px; z-index: 1000;">
                    <p>This is a popup!</p>
                    <button id="popup-close">Close</button>
                </div>
                
                <div id="banner" style="display: none; position: fixed; bottom: 0; 
                                        width: 100%; background: yellow; padding: 10px;">
                    <span>Cookie Banner</span>
                    <button id="banner-accept">Accept</button>
                </div>
                
                <div id="status-log"></div>
                
                <script>
                    const log = document.getElementById('status-log');
                    
                    document.getElementById('show-popup').addEventListener('click', () => {
                        document.getElementById('popup').style.display = 'block';
                        log.innerHTML += '<p>Popup shown</p>';
                    });
                    
                    document.getElementById('show-banner').addEventListener('click', () => {
                        document.getElementById('banner').style.display = 'block';
                        log.innerHTML += '<p>Banner shown</p>';
                    });
                    
                    document.getElementById('popup-close').addEventListener('click', () => {
                        document.getElementById('popup').style.display = 'none';
                        log.innerHTML += '<p style="color: green;">✓ Popup closed</p>';
                    });
                    
                    document.getElementById('banner-accept').addEventListener('click', () => {
                        document.getElementById('banner').style.display = 'none';
                        log.innerHTML += '<p style="color: green;">✓ Banner accepted</p>';
                    });
                </script>
            </body>
            </html>
        """)
        
        element_manager = ElementManager(page, ConfigManager())
        
        # Try to close popup (doesn't exist yet)
        print("Trying to close popup (not present)...")
        clicked = await element_manager.click_if_exists("css=#popup-close", timeout=2000)
        print(f"  Result: {'Clicked' if clicked else 'Not found'}")
        
        # Show popup
        print("Showing popup...")
        await element_manager.click("css=#show-popup")
        await asyncio.sleep(0.5)
        
        # Try to close popup (now exists)
        print("Trying to close popup (now present)...")
        clicked = await element_manager.click_if_exists("css=#popup-close", timeout=2000)
        print(f"  Result: {'Clicked' if clicked else 'Not found'}")
        await asyncio.sleep(1)
        
        # Show banner
        print("Showing banner...")
        await element_manager.click("css=#show-banner")
        await asyncio.sleep(0.5)
        
        # Accept banner
        print("Accepting banner...")
        clicked = await element_manager.click_if_exists("css=#banner-accept", timeout=2000)
        print(f"  Result: {'Clicked' if clicked else 'Not found'}")
        await asyncio.sleep(2)
        
        await browser.close()
        print("✓ Conditional clicking completed successfully")


async def example_click_with_retry():
    """Example: Click with retry and exponential backoff."""
    print("\n=== Example 5: click_with_retry() ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Create test page with delayed button
        await page.set_content("""
            <!DOCTYPE html>
            <html>
            <head><title>Retry Click Example</title></head>
            <body>
                <h2>Click with retry example</h2>
                
                <button id="show-delayed-button">Show Button After 3 Seconds</button>
                
                <div id="button-container"></div>
                
                <div id="status-log"></div>
                
                <script>
                    const log = document.getElementById('status-log');
                    
                    document.getElementById('show-delayed-button').addEventListener('click', () => {
                        log.innerHTML = '<p>Button will appear in 3 seconds...</p>';
                        
                        setTimeout(() => {
                            const btn = document.createElement('button');
                            btn.id = 'delayed-button';
                            btn.textContent = 'Click Me!';
                            btn.addEventListener('click', () => {
                                log.innerHTML += '<p style="color: green;">✓ Delayed button clicked!</p>';
                            });
                            document.getElementById('button-container').appendChild(btn);
                            log.innerHTML += '<p>Button appeared!</p>';
                        }, 3000);
                    });
                </script>
            </body>
            </html>
        """)
        
        element_manager = ElementManager(page, ConfigManager())
        
        # Trigger delayed button
        print("Triggering delayed button...")
        await element_manager.click("css=#show-delayed-button")
        await asyncio.sleep(0.5)
        
        # Click with retry (will retry until button appears)
        print("Clicking with retry (button will appear after 3 seconds)...")
        print("  Retry settings: max_retries=5, initial_delay=1.0")
        await element_manager.click_with_retry(
            "css=#delayed-button",
            max_retries=5,
            initial_delay=1.0
        )
        await asyncio.sleep(2)
        
        await browser.close()
        print("✓ Retry clicking completed successfully")


async def example_combined_patterns():
    """Example: Combining multiple advanced click methods."""
    print("\n=== Example 6: Combined Patterns ===")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Create test page with multiple interaction types
        await page.set_content("""
            <!DOCTYPE html>
            <html>
            <head><title>Combined Patterns Example</title></head>
            <body>
                <h2>Combined interaction patterns</h2>
                
                <!-- Optional cookie banner -->
                <div id="cookie-banner" style="position: fixed; bottom: 0; width: 100%; 
                                               background: #333; color: white; padding: 10px;">
                    <span>We use cookies</span>
                    <button id="cookie-accept" style="margin-left: 10px;">Accept</button>
                </div>
                
                <!-- Main content -->
                <div style="margin: 20px;">
                    <h3>File Explorer</h3>
                    <div id="file-1" class="file-item" style="padding: 10px; border: 1px solid gray; 
                                                              margin: 5px; width: 200px; cursor: pointer;">
                        📄 Document.txt
                    </div>
                    <div id="file-2" class="file-item" style="padding: 10px; border: 1px solid gray; 
                                                              margin: 5px; width: 200px; cursor: pointer;">
                        📄 Report.pdf
                    </div>
                </div>
                
                <!-- Context menu -->
                <div id="context-menu" style="display: none; position: absolute; 
                                              background: white; border: 1px solid black; 
                                              padding: 5px; z-index: 1000;">
                    <div class="menu-item" style="padding: 5px; cursor: pointer;">Open</div>
                    <div class="menu-item" style="padding: 5px; cursor: pointer;">Delete</div>
                </div>
                
                <div id="status-log"></div>
                
                <script>
                    const log = document.getElementById('status-log');
                    const menu = document.getElementById('context-menu');
                    
                    // Cookie banner
                    document.getElementById('cookie-accept').addEventListener('click', () => {
                        document.getElementById('cookie-banner').style.display = 'none';
                        log.innerHTML += '<p style="color: green;">✓ Cookies accepted</p>';
                    });
                    
                    // File double-click
                    document.querySelectorAll('.file-item').forEach(file => {
                        file.addEventListener('dblclick', () => {
                            log.innerHTML += `<p style="color: green;">✓ Opened: ${file.textContent.trim()}</p>`;
                        });
                        
                        // Right-click context menu
                        file.addEventListener('contextmenu', (e) => {
                            e.preventDefault();
                            menu.style.display = 'block';
                            menu.style.left = e.pageX + 'px';
                            menu.style.top = e.pageY + 'px';
                        });
                    });
                    
                    // Close menu on click
                    document.addEventListener('click', () => {
                        menu.style.display = 'none';
                    });
                    
                    // Menu item actions
                    document.querySelectorAll('.menu-item').forEach(item => {
                        item.addEventListener('click', () => {
                            log.innerHTML += `<p>Action: ${item.textContent}</p>`;
                        });
                    });
                </script>
            </body>
            </html>
        """)
        
        element_manager = ElementManager(page, ConfigManager())
        
        # Step 1: Handle optional cookie banner
        print("Step 1: Handling optional cookie banner...")
        clicked = await element_manager.click_if_exists("css=#cookie-accept", timeout=2000)
        if clicked:
            print("  ✓ Cookie banner dismissed")
        else:
            print("  ℹ No cookie banner found")
        await asyncio.sleep(1)
        
        # Step 2: Double-click to open file
        print("Step 2: Double-clicking to open file...")
        await element_manager.double_click("css=#file-1")
        await asyncio.sleep(1)
        
        # Step 3: Right-click for context menu
        print("Step 3: Right-clicking for context menu...")
        await element_manager.right_click("css=#file-2")
        await asyncio.sleep(0.5)
        
        # Step 4: Click menu item with retry
        print("Step 4: Clicking menu item with retry...")
        await element_manager.click_with_retry(
            "text=Delete",
            max_retries=3,
            initial_delay=0.5
        )
        await asyncio.sleep(2)
        
        await browser.close()
        print("✓ Combined patterns completed successfully")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("RAPTOR Advanced Click Methods Examples")
    print("=" * 60)
    
    try:
        await example_click_at_position()
        await example_double_click()
        await example_right_click()
        await example_click_if_exists()
        await example_click_with_retry()
        await example_combined_patterns()
        
        print("\n" + "=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
