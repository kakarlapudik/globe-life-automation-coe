"""
Tests for synchronization methods in ElementManager.

This module tests the synchronization capabilities including:
- wait_for_load_state() for page load states
- wait_for_spinner() for loading indicators
- wait_for_disabled_pane() for modal dialogs
- wait_for_network_idle() for network requests
"""

import pytest
from playwright.async_api import async_playwright, Page
from raptor.core.element_manager import ElementManager
from raptor.core.exceptions import TimeoutException, RaptorException


@pytest.fixture
async def browser_page():
    """Fixture to provide a browser page for testing."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        yield page
        await context.close()
        await browser.close()


@pytest.fixture
async def element_manager(browser_page):
    """Fixture to provide an ElementManager instance."""
    return ElementManager(browser_page)


@pytest.mark.asyncio
async def test_wait_for_load_state_load(element_manager, browser_page):
    """Test waiting for 'load' state."""
    # Navigate to a page
    await browser_page.goto("https://example.com")
    
    # Wait for load state
    await element_manager.wait_for_load_state("load")
    
    # Should complete without error
    assert browser_page.url == "https://example.com/"


@pytest.mark.asyncio
async def test_wait_for_load_state_domcontentloaded(element_manager, browser_page):
    """Test waiting for 'domcontentloaded' state."""
    # Navigate to a page
    await browser_page.goto("https://example.com")
    
    # Wait for domcontentloaded state
    await element_manager.wait_for_load_state("domcontentloaded")
    
    # Should complete without error
    assert browser_page.url == "https://example.com/"


@pytest.mark.asyncio
async def test_wait_for_load_state_networkidle(element_manager, browser_page):
    """Test waiting for 'networkidle' state."""
    # Navigate to a page
    await browser_page.goto("https://example.com")
    
    # Wait for network idle state
    await element_manager.wait_for_load_state("networkidle", timeout=10000)
    
    # Should complete without error
    assert browser_page.url == "https://example.com/"


@pytest.mark.asyncio
async def test_wait_for_load_state_invalid_state(element_manager, browser_page):
    """Test that invalid load state raises ValueError."""
    await browser_page.goto("https://example.com")
    
    with pytest.raises(ValueError, match="Invalid load state"):
        await element_manager.wait_for_load_state("invalid_state")


@pytest.mark.asyncio
async def test_wait_for_spinner_disappears(element_manager, browser_page):
    """Test waiting for a spinner to disappear."""
    # Create a page with a spinner that disappears
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Spinner Test</title>
    </head>
    <body>
        <div id="spinner" style="display: block;">Loading...</div>
        <script>
            setTimeout(() => {
                document.getElementById('spinner').style.display = 'none';
            }, 1000);
        </script>
    </body>
    </html>
    """
    
    await browser_page.set_content(html_content)
    
    # Wait for spinner to disappear
    await element_manager.wait_for_spinner("css=#spinner", timeout=5000)
    
    # Verify spinner is hidden
    is_visible = await element_manager.is_visible("css=#spinner", timeout=1000)
    assert not is_visible


@pytest.mark.asyncio
async def test_wait_for_spinner_already_gone(element_manager, browser_page):
    """Test waiting for a spinner that doesn't exist."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>No Spinner Test</title>
    </head>
    <body>
        <div id="content">Content loaded</div>
    </body>
    </html>
    """
    
    await browser_page.set_content(html_content)
    
    # Should complete immediately since spinner doesn't exist
    await element_manager.wait_for_spinner("css=#spinner", timeout=2000)


@pytest.mark.asyncio
async def test_wait_for_spinner_timeout(element_manager, browser_page):
    """Test that waiting for a spinner that never disappears times out."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Persistent Spinner Test</title>
    </head>
    <body>
        <div id="spinner" style="display: block;">Loading forever...</div>
    </body>
    </html>
    """
    
    await browser_page.set_content(html_content)
    
    # Should timeout since spinner never disappears
    with pytest.raises(TimeoutException):
        await element_manager.wait_for_spinner("css=#spinner", timeout=2000)


@pytest.mark.asyncio
async def test_wait_for_disabled_pane_with_locator(element_manager, browser_page):
    """Test waiting for a specific disabled pane to disappear."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Modal Test</title>
    </head>
    <body>
        <div id="modal-overlay" style="display: block;">Modal content</div>
        <script>
            setTimeout(() => {
                document.getElementById('modal-overlay').style.display = 'none';
            }, 1000);
        </script>
    </body>
    </html>
    """
    
    await browser_page.set_content(html_content)
    
    # Wait for modal to disappear
    await element_manager.wait_for_disabled_pane("css=#modal-overlay", timeout=5000)
    
    # Verify modal is hidden
    is_visible = await element_manager.is_visible("css=#modal-overlay", timeout=1000)
    assert not is_visible


@pytest.mark.asyncio
async def test_wait_for_disabled_pane_no_pane(element_manager, browser_page):
    """Test waiting for disabled pane when none exists."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>No Modal Test</title>
    </head>
    <body>
        <div id="content">Regular content</div>
    </body>
    </html>
    """
    
    await browser_page.set_content(html_content)
    
    # Should complete immediately since no pane exists
    await element_manager.wait_for_disabled_pane(timeout=2000)


@pytest.mark.asyncio
async def test_wait_for_disabled_pane_default_selectors(element_manager, browser_page):
    """Test waiting for disabled pane using default selectors."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Default Modal Test</title>
    </head>
    <body>
        <div class="modal-backdrop" style="display: block;">Backdrop</div>
        <script>
            setTimeout(() => {
                document.querySelector('.modal-backdrop').style.display = 'none';
            }, 1000);
        </script>
    </body>
    </html>
    """
    
    await browser_page.set_content(html_content)
    
    # Wait for modal using default selectors
    await element_manager.wait_for_disabled_pane(timeout=5000)
    
    # Verify modal is hidden
    is_visible = await element_manager.is_visible("css=.modal-backdrop", timeout=1000)
    assert not is_visible


@pytest.mark.asyncio
async def test_wait_for_network_idle(element_manager, browser_page):
    """Test waiting for network to become idle."""
    # Navigate to a page
    await browser_page.goto("https://example.com")
    
    # Wait for network idle
    await element_manager.wait_for_network_idle(timeout=10000)
    
    # Should complete without error
    assert browser_page.url == "https://example.com/"


@pytest.mark.asyncio
async def test_wait_for_network_idle_with_ajax(element_manager, browser_page):
    """Test waiting for network idle after AJAX requests."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AJAX Test</title>
    </head>
    <body>
        <div id="content">Loading...</div>
        <script>
            // Simulate AJAX request
            setTimeout(() => {
                fetch('https://jsonplaceholder.typicode.com/todos/1')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('content').textContent = 'Loaded: ' + data.title;
                    });
            }, 500);
        </script>
    </body>
    </html>
    """
    
    await browser_page.set_content(html_content)
    
    # Wait for network idle (should wait for fetch to complete)
    await element_manager.wait_for_network_idle(timeout=10000)
    
    # Content should be updated
    content = await element_manager.get_text("css=#content")
    assert "Loaded:" in content


@pytest.mark.asyncio
async def test_synchronization_methods_integration(element_manager, browser_page):
    """Test integration of multiple synchronization methods."""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Integration Test</title>
    </head>
    <body>
        <div id="spinner" style="display: block;">Loading...</div>
        <div id="content" style="display: none;">Content</div>
        <script>
            // Simulate page load with spinner
            setTimeout(() => {
                document.getElementById('spinner').style.display = 'none';
                document.getElementById('content').style.display = 'block';
            }, 1000);
        </script>
    </body>
    </html>
    """
    
    await browser_page.set_content(html_content)
    
    # Wait for load state
    await element_manager.wait_for_load_state("load")
    
    # Wait for spinner to disappear
    await element_manager.wait_for_spinner("css=#spinner", timeout=5000)
    
    # Wait for network idle
    await element_manager.wait_for_network_idle(timeout=5000)
    
    # Verify content is visible
    is_visible = await element_manager.is_visible("css=#content", timeout=2000)
    assert is_visible


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
