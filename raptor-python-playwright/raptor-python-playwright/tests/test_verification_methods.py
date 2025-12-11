"""
Tests for verification methods in ElementManager.

This module tests the verification methods that assert element states:
- verify_exists()
- verify_not_exists()
- verify_enabled()
- verify_disabled()
- verify_text()
- verify_visible()
"""

import pytest
from playwright.async_api import async_playwright, Page
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager


@pytest.fixture
async def page():
    """Create a Playwright page for testing."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        # Create a test HTML page
        await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head><title>Verification Test Page</title></head>
        <body>
            <h1 id="title">Test Page</h1>
            <button id="enabled-button">Enabled Button</button>
            <button id="disabled-button" disabled>Disabled Button</button>
            <div id="visible-div">Visible Content</div>
            <div id="hidden-div" style="display: none;">Hidden Content</div>
            <p id="message">Success!</p>
            <p id="partial-text">This is a partial match test</p>
            <input id="text-input" type="text" value="test value" />
        </body>
        </html>
        """)
        
        yield page
        
        await context.close()
        await browser.close()


@pytest.fixture
def element_manager(page):
    """Create an ElementManager instance."""
    config = ConfigManager()
    return ElementManager(page, config)


@pytest.mark.asyncio
async def test_verify_exists_success(element_manager):
    """Test verify_exists with an existing element."""
    # Should not raise an exception
    await element_manager.verify_exists("css=#title")
    await element_manager.verify_exists("css=#enabled-button")


@pytest.mark.asyncio
async def test_verify_exists_failure(element_manager):
    """Test verify_exists with a non-existing element."""
    with pytest.raises(AssertionError, match="Element does not exist"):
        await element_manager.verify_exists("css=#nonexistent", timeout=2000)


@pytest.mark.asyncio
async def test_verify_exists_custom_message(element_manager):
    """Test verify_exists with custom error message."""
    custom_msg = "Custom error: Element should exist"
    with pytest.raises(AssertionError, match=custom_msg):
        await element_manager.verify_exists(
            "css=#nonexistent",
            timeout=2000,
            message=custom_msg
        )


@pytest.mark.asyncio
async def test_verify_not_exists_success(element_manager):
    """Test verify_not_exists with a non-existing element."""
    # Should not raise an exception
    await element_manager.verify_not_exists("css=#nonexistent", timeout=2000)


@pytest.mark.asyncio
async def test_verify_not_exists_failure(element_manager):
    """Test verify_not_exists with an existing element."""
    with pytest.raises(AssertionError, match="Element exists but should not"):
        await element_manager.verify_not_exists("css=#title", timeout=2000)


@pytest.mark.asyncio
async def test_verify_not_exists_custom_message(element_manager):
    """Test verify_not_exists with custom error message."""
    custom_msg = "Custom error: Element should not exist"
    with pytest.raises(AssertionError, match=custom_msg):
        await element_manager.verify_not_exists(
            "css=#title",
            timeout=2000,
            message=custom_msg
        )


@pytest.mark.asyncio
async def test_verify_enabled_success(element_manager):
    """Test verify_enabled with an enabled element."""
    # Should not raise an exception
    await element_manager.verify_enabled("css=#enabled-button")


@pytest.mark.asyncio
async def test_verify_enabled_failure(element_manager):
    """Test verify_enabled with a disabled element."""
    with pytest.raises(AssertionError, match="Element is disabled but should be enabled"):
        await element_manager.verify_enabled("css=#disabled-button")


@pytest.mark.asyncio
async def test_verify_enabled_custom_message(element_manager):
    """Test verify_enabled with custom error message."""
    custom_msg = "Custom error: Button should be enabled"
    with pytest.raises(AssertionError, match=custom_msg):
        await element_manager.verify_enabled(
            "css=#disabled-button",
            message=custom_msg
        )


@pytest.mark.asyncio
async def test_verify_disabled_success(element_manager):
    """Test verify_disabled with a disabled element."""
    # Should not raise an exception
    await element_manager.verify_disabled("css=#disabled-button")


@pytest.mark.asyncio
async def test_verify_disabled_failure(element_manager):
    """Test verify_disabled with an enabled element."""
    with pytest.raises(AssertionError, match="Element is enabled but should be disabled"):
        await element_manager.verify_disabled("css=#enabled-button")


@pytest.mark.asyncio
async def test_verify_disabled_custom_message(element_manager):
    """Test verify_disabled with custom error message."""
    custom_msg = "Custom error: Button should be disabled"
    with pytest.raises(AssertionError, match=custom_msg):
        await element_manager.verify_disabled(
            "css=#enabled-button",
            message=custom_msg
        )


@pytest.mark.asyncio
async def test_verify_text_exact_match_success(element_manager):
    """Test verify_text with exact match."""
    # Should not raise an exception
    await element_manager.verify_text("css=#message", "Success!")


@pytest.mark.asyncio
async def test_verify_text_exact_match_failure(element_manager):
    """Test verify_text with exact match failure."""
    with pytest.raises(AssertionError, match="Text mismatch"):
        await element_manager.verify_text("css=#message", "Failure!")


@pytest.mark.asyncio
async def test_verify_text_partial_match_success(element_manager):
    """Test verify_text with partial match."""
    # Should not raise an exception
    await element_manager.verify_text(
        "css=#partial-text",
        "partial match",
        exact_match=False
    )


@pytest.mark.asyncio
async def test_verify_text_partial_match_failure(element_manager):
    """Test verify_text with partial match failure."""
    with pytest.raises(AssertionError, match="Text mismatch"):
        await element_manager.verify_text(
            "css=#partial-text",
            "not found",
            exact_match=False
        )


@pytest.mark.asyncio
async def test_verify_text_case_insensitive_success(element_manager):
    """Test verify_text with case-insensitive comparison."""
    # Should not raise an exception
    await element_manager.verify_text(
        "css=#message",
        "success!",
        case_sensitive=False
    )


@pytest.mark.asyncio
async def test_verify_text_case_insensitive_failure(element_manager):
    """Test verify_text with case-insensitive comparison failure."""
    with pytest.raises(AssertionError, match="Text mismatch"):
        await element_manager.verify_text(
            "css=#message",
            "failure!",
            case_sensitive=False
        )


@pytest.mark.asyncio
async def test_verify_text_custom_message(element_manager):
    """Test verify_text with custom error message."""
    custom_msg = "Custom error: Text should match"
    with pytest.raises(AssertionError, match=custom_msg):
        await element_manager.verify_text(
            "css=#message",
            "Wrong",
            message=custom_msg
        )


@pytest.mark.asyncio
async def test_verify_visible_success(element_manager):
    """Test verify_visible with a visible element."""
    # Should not raise an exception
    await element_manager.verify_visible("css=#visible-div")


@pytest.mark.asyncio
async def test_verify_visible_failure(element_manager):
    """Test verify_visible with a hidden element."""
    with pytest.raises(AssertionError, match="Element is not visible or does not exist"):
        await element_manager.verify_visible("css=#hidden-div", timeout=2000)


@pytest.mark.asyncio
async def test_verify_visible_custom_message(element_manager):
    """Test verify_visible with custom error message."""
    custom_msg = "Custom error: Element should be visible"
    with pytest.raises(AssertionError, match=custom_msg):
        await element_manager.verify_visible(
            "css=#hidden-div",
            timeout=2000,
            message=custom_msg
        )


@pytest.mark.asyncio
async def test_verify_with_fallback_locators(element_manager):
    """Test verification methods with fallback locators."""
    # Should use fallback locator when primary fails
    await element_manager.verify_exists(
        "css=#nonexistent",
        fallback_locators=["css=#title"],
        timeout=2000
    )
    
    await element_manager.verify_enabled(
        "css=#nonexistent",
        fallback_locators=["css=#enabled-button"],
        timeout=2000
    )


@pytest.mark.asyncio
async def test_multiple_verifications_in_sequence(element_manager):
    """Test multiple verification methods in sequence."""
    # All should pass
    await element_manager.verify_exists("css=#title")
    await element_manager.verify_visible("css=#title")
    await element_manager.verify_text("css=#title", "Test Page")
    await element_manager.verify_enabled("css=#enabled-button")
    await element_manager.verify_disabled("css=#disabled-button")
    await element_manager.verify_not_exists("css=#nonexistent", timeout=2000)
