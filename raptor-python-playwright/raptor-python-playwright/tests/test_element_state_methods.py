"""
Unit tests for Element State and Property Methods (Task 8).

Tests the following ElementManager methods:
- get_text()
- get_attribute()
- get_value()
- get_location()
- is_selected()
"""

import pytest
from playwright.async_api import async_playwright, Page
from raptor.core.element_manager import ElementManager
from raptor.core.exceptions import ElementNotFoundException, RaptorException


@pytest.fixture
async def page():
    """Create a Playwright page for testing."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        # Create a test HTML page with various elements
        await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1 id="heading">Welcome to Test Page</h1>
            <p id="message">This is a test message with some content.</p>
            
            <a id="link" href="https://example.com" class="external-link" target="_blank">
                Click Here
            </a>
            
            <form>
                <input type="text" id="username" name="username" value="john.doe" />
                <input type="email" id="email" name="email" value="john@example.com" />
                <textarea id="bio" name="bio">Software Engineer</textarea>
                
                <input type="checkbox" id="terms" name="terms" checked />
                <label for="terms">Accept Terms</label>
                
                <input type="checkbox" id="newsletter" name="newsletter" />
                <label for="newsletter">Subscribe to Newsletter</label>
                
                <input type="radio" id="option1" name="option" value="1" checked />
                <label for="option1">Option 1</label>
                
                <input type="radio" id="option2" name="option" value="2" />
                <label for="option2">Option 2</label>
            </form>
            
            <div id="positioned" style="position: absolute; left: 100px; top: 200px; width: 150px; height: 75px;">
                Positioned Element
            </div>
            
            <button id="submit" type="submit" disabled>Submit</button>
            <button id="cancel" type="button">Cancel</button>
        </body>
        </html>
        """)
        
        yield page
        
        await context.close()
        await browser.close()


@pytest.mark.asyncio
async def test_get_text_simple(page: Page):
    """Test getting text from a simple element."""
    element_manager = ElementManager(page)
    
    text = await element_manager.get_text("css=#heading")
    assert text == "Welcome to Test Page"
    
    message = await element_manager.get_text("css=#message")
    assert "test message" in message


@pytest.mark.asyncio
async def test_get_text_with_fallback(page: Page):
    """Test getting text with fallback locators."""
    element_manager = ElementManager(page)
    
    text = await element_manager.get_text(
        "css=#nonexistent",
        fallback_locators=["css=#heading", "xpath=//h1"]
    )
    assert text == "Welcome to Test Page"


@pytest.mark.asyncio
async def test_get_text_element_not_found(page: Page):
    """Test getting text from non-existent element."""
    element_manager = ElementManager(page)
    
    with pytest.raises(ElementNotFoundException):
        await element_manager.get_text("css=#does-not-exist", timeout=1000)


@pytest.mark.asyncio
async def test_get_attribute_simple(page: Page):
    """Test getting attributes from elements."""
    element_manager = ElementManager(page)
    
    # Get href attribute
    href = await element_manager.get_attribute("css=#link", "href")
    assert href == "https://example.com"
    
    # Get class attribute
    class_name = await element_manager.get_attribute("css=#link", "class")
    assert class_name == "external-link"
    
    # Get target attribute
    target = await element_manager.get_attribute("css=#link", "target")
    assert target == "_blank"


@pytest.mark.asyncio
async def test_get_attribute_nonexistent(page: Page):
    """Test getting non-existent attribute returns None."""
    element_manager = ElementManager(page)
    
    result = await element_manager.get_attribute("css=#heading", "data-nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_get_attribute_with_fallback(page: Page):
    """Test getting attribute with fallback locators."""
    element_manager = ElementManager(page)
    
    href = await element_manager.get_attribute(
        "css=#wrong-id",
        "href",
        fallback_locators=["css=#link", "xpath=//a"]
    )
    assert href == "https://example.com"


@pytest.mark.asyncio
async def test_get_value_text_input(page: Page):
    """Test getting value from text input."""
    element_manager = ElementManager(page)
    
    username = await element_manager.get_value("css=#username")
    assert username == "john.doe"
    
    email = await element_manager.get_value("css=#email")
    assert email == "john@example.com"


@pytest.mark.asyncio
async def test_get_value_textarea(page: Page):
    """Test getting value from textarea."""
    element_manager = ElementManager(page)
    
    bio = await element_manager.get_value("css=#bio")
    assert bio == "Software Engineer"


@pytest.mark.asyncio
async def test_get_value_after_fill(page: Page):
    """Test getting value after filling input."""
    element_manager = ElementManager(page)
    
    # Fill new value
    await element_manager.fill("css=#username", "jane.smith")
    
    # Get the updated value
    username = await element_manager.get_value("css=#username")
    assert username == "jane.smith"


@pytest.mark.asyncio
async def test_get_value_with_fallback(page: Page):
    """Test getting value with fallback locators."""
    element_manager = ElementManager(page)
    
    value = await element_manager.get_value(
        "css=#wrong-id",
        fallback_locators=["css=#username", "xpath=//input[@name='username']"]
    )
    assert value == "john.doe"


@pytest.mark.asyncio
async def test_get_location_simple(page: Page):
    """Test getting element location and dimensions."""
    element_manager = ElementManager(page)
    
    location = await element_manager.get_location("css=#positioned")
    
    # Check that all required keys are present
    assert "x" in location
    assert "y" in location
    assert "width" in location
    assert "height" in location
    
    # Check approximate values (may vary slightly due to rendering)
    assert location["width"] == pytest.approx(150, abs=5)
    assert location["height"] == pytest.approx(75, abs=5)


@pytest.mark.asyncio
async def test_get_location_with_fallback(page: Page):
    """Test getting location with fallback locators."""
    element_manager = ElementManager(page)
    
    location = await element_manager.get_location(
        "css=#wrong-id",
        fallback_locators=["css=#positioned", "xpath=//div[@id='positioned']"]
    )
    
    assert "x" in location
    assert "y" in location
    assert location["width"] > 0
    assert location["height"] > 0


@pytest.mark.asyncio
async def test_is_selected_checkbox_checked(page: Page):
    """Test checking if checkbox is selected (checked)."""
    element_manager = ElementManager(page)
    
    # Terms checkbox is checked
    is_checked = await element_manager.is_selected("css=#terms")
    assert is_checked is True
    
    # Newsletter checkbox is not checked
    is_checked = await element_manager.is_selected("css=#newsletter")
    assert is_checked is False


@pytest.mark.asyncio
async def test_is_selected_radio_button(page: Page):
    """Test checking if radio button is selected."""
    element_manager = ElementManager(page)
    
    # Option 1 is checked
    is_selected = await element_manager.is_selected("css=#option1")
    assert is_selected is True
    
    # Option 2 is not checked
    is_selected = await element_manager.is_selected("css=#option2")
    assert is_selected is False


@pytest.mark.asyncio
async def test_is_selected_after_click(page: Page):
    """Test selection state changes after clicking."""
    element_manager = ElementManager(page)
    
    # Initially not checked
    assert await element_manager.is_selected("css=#newsletter") is False
    
    # Click to check
    await element_manager.click("css=#newsletter")
    
    # Now should be checked
    assert await element_manager.is_selected("css=#newsletter") is True


@pytest.mark.asyncio
async def test_is_selected_with_fallback(page: Page):
    """Test checking selection with fallback locators."""
    element_manager = ElementManager(page)
    
    is_checked = await element_manager.is_selected(
        "css=#wrong-id",
        fallback_locators=["css=#terms", "xpath=//input[@id='terms']"]
    )
    assert is_checked is True


@pytest.mark.asyncio
async def test_get_text_empty_element(page: Page):
    """Test getting text from element with no text content."""
    element_manager = ElementManager(page)
    
    # Add an empty div
    await page.evaluate("document.body.innerHTML += '<div id=\"empty\"></div>'")
    
    text = await element_manager.get_text("css=#empty")
    assert text == ""


@pytest.mark.asyncio
async def test_multiple_operations_sequence(page: Page):
    """Test performing multiple state operations in sequence."""
    element_manager = ElementManager(page)
    
    # Get initial value
    initial_value = await element_manager.get_value("css=#username")
    assert initial_value == "john.doe"
    
    # Fill new value
    await element_manager.fill("css=#username", "test.user")
    
    # Get updated value
    new_value = await element_manager.get_value("css=#username")
    assert new_value == "test.user"
    
    # Get attribute
    name_attr = await element_manager.get_attribute("css=#username", "name")
    assert name_attr == "username"
    
    # Get location
    location = await element_manager.get_location("css=#username")
    assert location["width"] > 0


@pytest.mark.asyncio
async def test_get_attribute_disabled_state(page: Page):
    """Test getting disabled attribute."""
    element_manager = ElementManager(page)
    
    # Submit button is disabled
    disabled = await element_manager.get_attribute("css=#submit", "disabled")
    assert disabled is not None  # Disabled attribute exists
    
    # Cancel button is not disabled
    disabled = await element_manager.get_attribute("css=#cancel", "disabled")
    assert disabled is None  # Disabled attribute doesn't exist


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
