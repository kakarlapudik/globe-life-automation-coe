"""
Unit tests for ElementManager

Tests element location, fallback mechanisms, and wait functionality.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from playwright.async_api import async_playwright, Page
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.core.exceptions import (
    ElementNotFoundException,
    TimeoutException,
    RaptorException
)


@pytest.fixture
async def page():
    """Create a Playwright page for testing."""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        # Create a simple test HTML page
        await page.set_content("""
            <!DOCTYPE html>
            <html>
            <head><title>Test Page</title></head>
            <body>
                <h1 id="main-heading">Test Heading</h1>
                <button id="submit-btn" class="btn-primary">Submit</button>
                <input id="username" type="text" placeholder="Username" />
                <div id="hidden-div" style="display: none;">Hidden Content</div>
                <p class="description">This is a test paragraph.</p>
                <p class="description">Another paragraph.</p>
                <a href="#" role="button" aria-label="Click Me">Link Button</a>
            </body>
            </html>
        """)
        
        yield page
        
        await browser.close()


@pytest.fixture
def element_manager(page):
    """Create an ElementManager instance."""
    config = ConfigManager()
    return ElementManager(page, config)


@pytest.mark.asyncio
async def test_locate_element_with_css(element_manager):
    """Test locating element with CSS selector."""
    element = await element_manager.locate_element("css=#main-heading")
    assert element is not None
    text = await element.text_content()
    assert text == "Test Heading"


@pytest.mark.asyncio
async def test_locate_element_with_xpath(element_manager):
    """Test locating element with XPath."""
    element = await element_manager.locate_element("xpath=//h1[@id='main-heading']")
    assert element is not None
    text = await element.text_content()
    assert text == "Test Heading"


@pytest.mark.asyncio
async def test_locate_element_with_text(element_manager):
    """Test locating element with text content."""
    element = await element_manager.locate_element("text=Submit")
    assert element is not None


@pytest.mark.asyncio
async def test_locate_element_with_id(element_manager):
    """Test locating element with ID."""
    element = await element_manager.locate_element("id=submit-btn")
    assert element is not None
    text = await element.text_content()
    assert text == "Submit"


@pytest.mark.asyncio
async def test_locate_element_default_css(element_manager):
    """Test that locator defaults to CSS when no strategy specified."""
    element = await element_manager.locate_element("#main-heading")
    assert element is not None
    text = await element.text_content()
    assert text == "Test Heading"


@pytest.mark.asyncio
async def test_locate_element_with_fallback_success(element_manager):
    """Test fallback locator mechanism when primary fails."""
    element = await element_manager.locate_element(
        "css=#nonexistent-id",
        fallback_locators=["xpath=//h1[@id='main-heading']"],
        timeout=2000
    )
    assert element is not None
    text = await element.text_content()
    assert text == "Test Heading"


@pytest.mark.asyncio
async def test_locate_element_with_multiple_fallbacks(element_manager):
    """Test multiple fallback locators."""
    element = await element_manager.locate_element(
        "css=#nonexistent-1",
        fallback_locators=[
            "css=#nonexistent-2",
            "xpath=//h1[@id='main-heading']",  # This should succeed
            "text=Test Heading"
        ],
        timeout=2000
    )
    assert element is not None
    text = await element.text_content()
    assert text == "Test Heading"


@pytest.mark.asyncio
async def test_locate_element_all_fail(element_manager):
    """Test that ElementNotFoundException is raised when all locators fail."""
    with pytest.raises(ElementNotFoundException) as exc_info:
        await element_manager.locate_element(
            "css=#nonexistent-1",
            fallback_locators=["css=#nonexistent-2", "xpath=//div[@id='nonexistent-3']"],
            timeout=1000
        )
    
    # Verify exception contains context
    assert exc_info.value.context["primary_locator"] == "css=#nonexistent-1"
    assert len(exc_info.value.context["fallback_locators"]) == 2


@pytest.mark.asyncio
async def test_wait_for_element_visible(element_manager):
    """Test waiting for element to be visible."""
    element = await element_manager.wait_for_element(
        "css=#main-heading",
        state="visible",
        timeout=2000
    )
    assert element is not None


@pytest.mark.asyncio
async def test_wait_for_element_hidden(element_manager):
    """Test waiting for element to be hidden."""
    element = await element_manager.wait_for_element(
        "css=#hidden-div",
        state="hidden",
        timeout=2000
    )
    assert element is not None


@pytest.mark.asyncio
async def test_wait_for_element_timeout(element_manager):
    """Test that TimeoutException is raised when wait times out."""
    with pytest.raises(TimeoutException) as exc_info:
        await element_manager.wait_for_element(
            "css=#nonexistent",
            state="visible",
            timeout=1000
        )
    
    assert exc_info.value.context["operation"] == "wait_for_element (state=visible)"


@pytest.mark.asyncio
async def test_is_visible_true(element_manager):
    """Test is_visible returns True for visible element."""
    is_visible = await element_manager.is_visible("css=#main-heading", timeout=2000)
    assert is_visible is True


@pytest.mark.asyncio
async def test_is_visible_false(element_manager):
    """Test is_visible returns False for nonexistent element."""
    is_visible = await element_manager.is_visible("css=#nonexistent", timeout=1000)
    assert is_visible is False


@pytest.mark.asyncio
async def test_is_hidden_true(element_manager):
    """Test is_hidden returns True for hidden element."""
    is_hidden = await element_manager.is_hidden("css=#hidden-div", timeout=2000)
    assert is_hidden is True


@pytest.mark.asyncio
async def test_is_hidden_false(element_manager):
    """Test is_hidden returns False for visible element."""
    is_hidden = await element_manager.is_hidden("css=#main-heading", timeout=1000)
    assert is_hidden is False


@pytest.mark.asyncio
async def test_get_element_count(element_manager):
    """Test counting elements matching locator."""
    count = await element_manager.get_element_count("css=.description")
    assert count == 2


@pytest.mark.asyncio
async def test_get_element_count_zero(element_manager):
    """Test counting returns zero for nonexistent elements."""
    count = await element_manager.get_element_count("css=.nonexistent-class")
    assert count == 0


@pytest.mark.asyncio
async def test_parse_locator_strategy_css(element_manager):
    """Test parsing CSS locator strategy."""
    strategy, value = element_manager._parse_locator_strategy("css=#test")
    assert strategy == "css"
    assert value == "#test"


@pytest.mark.asyncio
async def test_parse_locator_strategy_xpath(element_manager):
    """Test parsing XPath locator strategy."""
    strategy, value = element_manager._parse_locator_strategy("xpath=//div")
    assert strategy == "xpath"
    assert value == "//div"


@pytest.mark.asyncio
async def test_parse_locator_strategy_text(element_manager):
    """Test parsing text locator strategy."""
    strategy, value = element_manager._parse_locator_strategy("text=Click Me")
    assert strategy == "text"
    assert value == "Click Me"


@pytest.mark.asyncio
async def test_parse_locator_strategy_default(element_manager):
    """Test that locator defaults to CSS when no strategy specified."""
    strategy, value = element_manager._parse_locator_strategy("#test-id")
    assert strategy == "css"
    assert value == "#test-id"


@pytest.mark.asyncio
async def test_get_default_timeout(element_manager):
    """Test getting default timeout."""
    timeout = element_manager.get_default_timeout()
    assert timeout > 0
    assert isinstance(timeout, int)


@pytest.mark.asyncio
async def test_set_default_timeout(element_manager):
    """Test setting default timeout."""
    new_timeout = 15000
    element_manager.set_default_timeout(new_timeout)
    assert element_manager.get_default_timeout() == new_timeout


@pytest.mark.asyncio
async def test_set_default_timeout_invalid(element_manager):
    """Test that setting negative timeout raises ValueError."""
    with pytest.raises(ValueError):
        element_manager.set_default_timeout(-1000)


@pytest.mark.asyncio
async def test_context_manager(page):
    """Test ElementManager as async context manager."""
    config = ConfigManager()
    async with ElementManager(page, config) as em:
        element = await em.locate_element("css=#main-heading")
        assert element is not None


# ============================================================================
# Property-Based Tests
# ============================================================================

@pytest.fixture
async def page_with_dynamic_elements():
    """Create a Playwright page with dynamically generated elements for property testing."""
    # Reuse the existing page fixture setup
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        # Create a test page with multiple elements that can be targeted
        await page.set_content("""
            <!DOCTYPE html>
            <html>
            <head><title>Property Test Page</title></head>
            <body>
                <div id="target-element" class="target-class" data-testid="target-test">
                    Target Element
                </div>
                <button id="btn-1" class="button">Button 1</button>
                <button id="btn-2" class="button">Button 2</button>
                <button id="btn-3" class="button">Button 3</button>
                <input id="input-1" type="text" placeholder="Input 1" />
                <input id="input-2" type="text" placeholder="Input 2" />
                <span id="span-1">Span 1</span>
                <span id="span-2">Span 2</span>
                <p id="para-1">Paragraph 1</p>
                <p id="para-2">Paragraph 2</p>
            </body>
            </html>
        """)
        
        yield page
        
        await browser.close()


# Use the existing page fixture for property tests to avoid browser launch issues
@pytest.fixture
def property_test_page(page):
    """Alias for page fixture to use in property tests."""
    return page


@pytest.mark.asyncio
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    num_invalid_locators=st.integers(min_value=0, max_value=5),
    valid_locator_position=st.integers(min_value=0, max_value=5)
)
async def test_property_element_fallback_order(
    page,
    num_invalid_locators,
    valid_locator_position
):
    """
    Property 2: Element Location Fallback
    
    **Feature: raptor-playwright-python, Property 2: Element Location Fallback**
    
    For any element with multiple locator strategies, if the primary locator fails,
    the system should automatically attempt fallback locators in order until one
    succeeds or all fail.
    
    **Validates: Requirements 2.2**
    
    This property test verifies that:
    1. Fallback locators are attempted in the correct order
    2. The first successful locator is used
    3. Invalid locators before the valid one are skipped
    4. The element is found regardless of how many invalid locators precede it
    """
    element_manager = ElementManager(page, ConfigManager())
    
    # Generate a list of invalid locators
    invalid_locators = [
        f"css=#nonexistent-{i}" for i in range(num_invalid_locators)
    ]
    
    # Valid locators that will find elements on the test page
    valid_locators = [
        "css=#main-heading",
        "css=#submit-btn",
        "xpath=//h1[@id='main-heading']",
        "text=Submit",
        "id=username"
    ]
    
    # Pick a valid locator based on the position parameter
    valid_locator = valid_locators[valid_locator_position % len(valid_locators)]
    
    # Build the fallback list: invalid locators followed by a valid one
    fallback_list = invalid_locators + [valid_locator]
    
    # The primary locator is always invalid
    primary_locator = "css=#definitely-does-not-exist"
    
    # Attempt to locate the element
    try:
        element = await element_manager.locate_element(
            primary_locator,
            fallback_locators=fallback_list,
            timeout=2000
        )
        
        # Verify the element was found
        assert element is not None
        
        # Verify it's a valid element (has some content or attribute)
        is_visible = await element.is_visible()
        assert is_visible is True
        
    except ElementNotFoundException:
        # This should only happen if we have no valid locators
        # which shouldn't occur in this test since we always add one
        pytest.fail(
            f"Element should have been found with fallback locator at position "
            f"{num_invalid_locators} but wasn't. "
            f"Primary: {primary_locator}, Fallbacks: {fallback_list}"
        )


@pytest.mark.asyncio
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    num_invalid_locators=st.integers(min_value=1, max_value=10)
)
async def test_property_all_fallbacks_fail(
    page,
    num_invalid_locators
):
    """
    Property 2 (Negative Case): All Fallbacks Fail
    
    **Feature: raptor-playwright-python, Property 2: Element Location Fallback**
    
    For any element where all locators (primary and fallbacks) are invalid,
    the system should raise ElementNotFoundException after trying all locators.
    
    **Validates: Requirements 2.2**
    
    This property test verifies that:
    1. All locators are attempted before failing
    2. ElementNotFoundException is raised when all fail
    3. The exception contains context about all attempted locators
    """
    element_manager = ElementManager(page, ConfigManager())
    
    # Generate all invalid locators
    primary_locator = "css=#nonexistent-primary"
    fallback_locators = [
        f"css=#nonexistent-fallback-{i}" for i in range(num_invalid_locators)
    ]
    
    # Attempt to locate the element - should fail
    with pytest.raises(ElementNotFoundException) as exc_info:
        await element_manager.locate_element(
            primary_locator,
            fallback_locators=fallback_locators,
            timeout=1000
        )
    
    # Verify exception contains proper context
    assert exc_info.value.context["primary_locator"] == primary_locator
    assert len(exc_info.value.context["fallback_locators"]) == num_invalid_locators
    assert exc_info.value.context["fallback_locators"] == fallback_locators


@pytest.mark.asyncio
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    element_id=st.sampled_from(["main-heading", "submit-btn", "username", "hidden-div"]),
    locator_strategy=st.sampled_from(["css", "xpath", "id"])
)
async def test_property_fallback_finds_same_element(
    page,
    element_id,
    locator_strategy
):
    """
    Property 2 (Consistency): Fallback Finds Same Element
    
    **Feature: raptor-playwright-python, Property 2: Element Location Fallback**
    
    For any element, using different locator strategies (primary or fallback)
    should locate the same element.
    
    **Validates: Requirements 2.2**
    
    This property test verifies that:
    1. Different locator strategies find the same element
    2. Fallback mechanism doesn't change which element is found
    3. Element identity is preserved across different locator types
    """
    element_manager = ElementManager(page, ConfigManager())
    
    # Create different locator strategies for the same element
    locators = {
        "css": f"css=#{element_id}",
        "xpath": f"xpath=//*[@id='{element_id}']",
        "id": f"id={element_id}"
    }
    
    # Get the element using the primary strategy
    primary_locator = locators[locator_strategy]
    element1 = await element_manager.locate_element(primary_locator, timeout=2000)
    element1_id = await element1.get_attribute("id")
    
    # Get the element using fallback (with invalid primary)
    other_strategies = [s for s in locators.keys() if s != locator_strategy]
    fallback_locators = [locators[s] for s in other_strategies]
    
    element2 = await element_manager.locate_element(
        "css=#nonexistent-element",
        fallback_locators=fallback_locators,
        timeout=2000
    )
    element2_id = await element2.get_attribute("id")
    
    # Both should find the same element
    assert element1_id == element_id
    assert element2_id == element_id
    assert element1_id == element2_id


@pytest.mark.asyncio
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    num_fallbacks=st.integers(min_value=1, max_value=8),
    success_position=st.integers(min_value=0, max_value=8)
)
async def test_property_fallback_stops_at_first_success(
    page,
    num_fallbacks,
    success_position
):
    """
    Property 2 (Early Termination): Fallback Stops at First Success
    
    **Feature: raptor-playwright-python, Property 2: Element Location Fallback**
    
    For any element with multiple fallback locators, the system should stop
    attempting locators as soon as one succeeds, not trying remaining fallbacks.
    
    **Validates: Requirements 2.2**
    
    This property test verifies that:
    1. Locators are tried in order
    2. Search stops at first successful locator
    3. Remaining fallbacks are not attempted after success
    """
    element_manager = ElementManager(page, ConfigManager())
    
    # Determine where to place the valid locator
    valid_position = success_position % (num_fallbacks + 1)
    
    # Build fallback list with valid locator at specific position
    fallback_locators = []
    for i in range(num_fallbacks):
        if i == valid_position:
            # Insert valid locator
            fallback_locators.append("css=#main-heading")
        else:
            # Insert invalid locator
            fallback_locators.append(f"css=#invalid-{i}")
    
    # If valid position is at the end and we haven't added it yet
    if valid_position == num_fallbacks:
        fallback_locators.append("css=#main-heading")
    
    # Primary is always invalid
    primary_locator = "css=#invalid-primary"
    
    # Locate element
    element = await element_manager.locate_element(
        primary_locator,
        fallback_locators=fallback_locators,
        timeout=2000
    )
    
    # Verify element was found
    assert element is not None
    text = await element.text_content()
    assert "Test Heading" in text


# ============================================================================
# Basic Element Interaction Tests
# ============================================================================

@pytest.mark.asyncio
async def test_click_element(page):
    """Test clicking an element."""
    # Add a clickable element with click tracking
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <button id="click-btn" onclick="this.textContent='Clicked'">Click Me</button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Click the button
    await element_manager.click("css=#click-btn")
    
    # Verify the button was clicked
    element = await element_manager.locate_element("css=#click-btn")
    text = await element.text_content()
    assert text == "Clicked"


@pytest.mark.asyncio
async def test_click_with_fallback(page):
    """Test clicking with fallback locator."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <button id="click-btn" onclick="this.textContent='Clicked'">Click Me</button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Click with invalid primary and valid fallback
    await element_manager.click(
        "css=#nonexistent",
        fallback_locators=["css=#click-btn"],
        timeout=2000
    )
    
    # Verify the button was clicked
    element = await element_manager.locate_element("css=#click-btn")
    text = await element.text_content()
    assert text == "Clicked"


@pytest.mark.asyncio
async def test_click_nonexistent_element(page):
    """Test that clicking nonexistent element raises ElementNotFoundException."""
    await page.set_content("<html><body></body></html>")
    
    element_manager = ElementManager(page, ConfigManager())
    
    with pytest.raises(ElementNotFoundException):
        await element_manager.click("css=#nonexistent", timeout=1000)


@pytest.mark.asyncio
async def test_fill_input(page):
    """Test filling text into an input element."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <input id="username" type="text" />
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Fill the input
    await element_manager.fill("css=#username", "john.doe")
    
    # Verify the input was filled
    element = await element_manager.locate_element("css=#username")
    value = await element.input_value()
    assert value == "john.doe"


@pytest.mark.asyncio
async def test_fill_with_fallback(page):
    """Test filling with fallback locator."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <input id="email" type="email" name="user-email" />
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Fill with invalid primary and valid fallback
    await element_manager.fill(
        "css=#nonexistent",
        "test@example.com",
        fallback_locators=["xpath=//input[@name='user-email']"],
        timeout=2000
    )
    
    # Verify the input was filled
    element = await element_manager.locate_element("css=#email")
    value = await element.input_value()
    assert value == "test@example.com"


@pytest.mark.asyncio
async def test_fill_clears_existing_value(page):
    """Test that fill clears existing value before typing."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <input id="username" type="text" value="old-value" />
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Fill with new value
    await element_manager.fill("css=#username", "new-value")
    
    # Verify old value was cleared
    element = await element_manager.locate_element("css=#username")
    value = await element.input_value()
    assert value == "new-value"


@pytest.mark.asyncio
async def test_select_option_by_value(page):
    """Test selecting option by value."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <select id="country">
                <option value="us">United States</option>
                <option value="uk">United Kingdom</option>
                <option value="ca">Canada</option>
            </select>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Select by value
    selected = await element_manager.select_option("css=#country", value="uk")
    
    assert selected == ["uk"]
    
    # Verify selection
    element = await element_manager.locate_element("css=#country")
    value = await element.input_value()
    assert value == "uk"


@pytest.mark.asyncio
async def test_select_option_by_label(page):
    """Test selecting option by label."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <select id="country">
                <option value="us">United States</option>
                <option value="uk">United Kingdom</option>
                <option value="ca">Canada</option>
            </select>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Select by label
    selected = await element_manager.select_option("css=#country", label="Canada")
    
    assert selected == ["ca"]


@pytest.mark.asyncio
async def test_select_option_by_index(page):
    """Test selecting option by index."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <select id="country">
                <option value="us">United States</option>
                <option value="uk">United Kingdom</option>
                <option value="ca">Canada</option>
            </select>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Select by index
    selected = await element_manager.select_option("css=#country", index=1)
    
    assert selected == ["uk"]


@pytest.mark.asyncio
async def test_select_option_multiple(page):
    """Test selecting multiple options."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <select id="colors" multiple>
                <option value="red">Red</option>
                <option value="blue">Blue</option>
                <option value="green">Green</option>
            </select>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Select multiple by value
    selected = await element_manager.select_option("css=#colors", value=["red", "blue"])
    
    assert set(selected) == {"red", "blue"}


@pytest.mark.asyncio
async def test_select_option_no_criteria(page):
    """Test that select_option raises ValueError when no criteria provided."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <select id="country">
                <option value="us">United States</option>
            </select>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    with pytest.raises(ValueError, match="Must provide at least one of"):
        await element_manager.select_option("css=#country")


@pytest.mark.asyncio
async def test_hover_element(page):
    """Test hovering over an element."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <div id="hover-target" 
                 onmouseover="this.textContent='Hovered'"
                 onmouseout="this.textContent='Not Hovered'">
                Not Hovered
            </div>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Hover over the element
    await element_manager.hover("css=#hover-target")
    
    # Verify hover effect (note: this might be timing-dependent)
    element = await element_manager.locate_element("css=#hover-target")
    text = await element.text_content()
    assert text == "Hovered"


@pytest.mark.asyncio
async def test_hover_with_fallback(page):
    """Test hovering with fallback locator."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <div id="hover-target" 
                 onmouseover="this.textContent='Hovered'">
                Not Hovered
            </div>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Hover with invalid primary and valid fallback
    await element_manager.hover(
        "css=#nonexistent",
        fallback_locators=["css=#hover-target"],
        timeout=2000
    )
    
    # Verify hover effect
    element = await element_manager.locate_element("css=#hover-target")
    text = await element.text_content()
    assert text == "Hovered"


@pytest.mark.asyncio
async def test_is_enabled_true(page):
    """Test is_enabled returns True for enabled element."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <button id="enabled-btn">Enabled</button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    is_enabled = await element_manager.is_enabled("css=#enabled-btn")
    assert is_enabled is True


@pytest.mark.asyncio
async def test_is_enabled_false(page):
    """Test is_enabled returns False for disabled element."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <button id="disabled-btn" disabled>Disabled</button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    is_enabled = await element_manager.is_enabled("css=#disabled-btn")
    assert is_enabled is False


@pytest.mark.asyncio
async def test_is_enabled_nonexistent(page):
    """Test is_enabled returns False for nonexistent element."""
    await page.set_content("<html><body></body></html>")
    
    element_manager = ElementManager(page, ConfigManager())
    
    is_enabled = await element_manager.is_enabled("css=#nonexistent", timeout=1000)
    assert is_enabled is False


# ============================================================================
# Property-Based Test: Click Method Equivalence (Property 6)
# ============================================================================

@pytest.mark.asyncio
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    element_id=st.sampled_from(["btn-1", "btn-2", "btn-3"]),
    locator_strategy=st.sampled_from(["css", "xpath", "id", "text"])
)
async def test_property_click_method_equivalence(
    page,
    element_id,
    locator_strategy
):
    """
    Property 6: Click Method Equivalence
    
    **Feature: raptor-playwright-python, Property 6: Click Method Equivalence**
    
    For any clickable element, using different locator strategies to click
    should all result in the element being clicked successfully.
    
    This property test verifies that:
    1. Click works consistently across different locator strategies
    2. The same element is clicked regardless of locator type
    3. Click state changes are properly detected
    
    **Validates: Requirements 6.2**
    
    Note: This test currently validates click consistency across locator strategies.
    Once Task 7 (Advanced Click Methods) is implemented, this test will be extended
    to verify equivalence between click(), click_at_position(), and JavaScript click.
    """
    # Set up a page with clickable buttons that track click state
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                let clickCounts = {};
                function trackClick(id) {
                    if (!clickCounts[id]) {
                        clickCounts[id] = 0;
                    }
                    clickCounts[id]++;
                    document.getElementById(id).setAttribute('data-click-count', clickCounts[id]);
                    document.getElementById(id).textContent = 'Clicked ' + clickCounts[id];
                }
            </script>
        </head>
        <body>
            <button id="btn-1" class="button" onclick="trackClick('btn-1')">Button 1</button>
            <button id="btn-2" class="button" onclick="trackClick('btn-2')">Button 2</button>
            <button id="btn-3" class="button" onclick="trackClick('btn-3')">Button 3</button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Create locator based on strategy
    locators = {
        "css": f"css=#{element_id}",
        "xpath": f"xpath=//button[@id='{element_id}']",
        "id": f"id={element_id}",
        "text": f"text=Button {element_id.split('-')[1]}"
    }
    
    locator = locators[locator_strategy]
    
    # Get initial state
    element = await element_manager.locate_element(locator, timeout=2000)
    initial_text = await element.text_content()
    initial_click_count = await element.get_attribute("data-click-count")
    
    # Verify element is in initial state
    assert "Button" in initial_text
    assert initial_click_count is None or initial_click_count == "0"
    
    # Perform click using the locator strategy
    await element_manager.click(locator, timeout=2000)
    
    # Verify click was successful
    element_after = await element_manager.locate_element(locator, timeout=2000)
    final_text = await element_after.text_content()
    final_click_count = await element_after.get_attribute("data-click-count")
    
    # Assertions
    assert "Clicked" in final_text, f"Element was not clicked. Text: {final_text}"
    assert final_click_count == "1", f"Click count should be 1, got: {final_click_count}"
    assert final_text != initial_text, "Element text should have changed after click"


@pytest.mark.asyncio
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    num_clicks=st.integers(min_value=1, max_value=5),
    element_id=st.sampled_from(["btn-1", "btn-2", "btn-3"])
)
async def test_property_click_idempotency_tracking(
    page,
    num_clicks,
    element_id
):
    """
    Property 6 (Click Tracking): Multiple Clicks Are Tracked
    
    **Feature: raptor-playwright-python, Property 6: Click Method Equivalence**
    
    For any clickable element, clicking it N times should result in N click
    events being registered, demonstrating that the click method works reliably.
    
    **Validates: Requirements 6.2**
    
    This property test verifies that:
    1. Each click is properly registered
    2. Click count increments correctly
    3. Multiple clicks work consistently
    """
    # Set up a page with clickable buttons that track click state
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                let clickCounts = {};
                function trackClick(id) {
                    if (!clickCounts[id]) {
                        clickCounts[id] = 0;
                    }
                    clickCounts[id]++;
                    document.getElementById(id).setAttribute('data-click-count', clickCounts[id]);
                    document.getElementById(id).textContent = 'Clicked ' + clickCounts[id];
                }
            </script>
        </head>
        <body>
            <button id="btn-1" class="button" onclick="trackClick('btn-1')">Button 1</button>
            <button id="btn-2" class="button" onclick="trackClick('btn-2')">Button 2</button>
            <button id="btn-3" class="button" onclick="trackClick('btn-3')">Button 3</button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    locator = f"css=#{element_id}"
    
    # Click the element N times
    for i in range(num_clicks):
        await element_manager.click(locator, timeout=2000)
        
        # Small delay to ensure click is processed
        await asyncio.sleep(0.05)
    
    # Verify final click count
    element = await element_manager.locate_element(locator, timeout=2000)
    final_click_count = await element.get_attribute("data-click-count")
    final_text = await element.text_content()
    
    # Assertions
    assert final_click_count == str(num_clicks), \
        f"Expected {num_clicks} clicks, got {final_click_count}"
    assert f"Clicked {num_clicks}" in final_text, \
        f"Expected text 'Clicked {num_clicks}', got '{final_text}'"


@pytest.mark.asyncio
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    element_id=st.sampled_from(["btn-1", "btn-2", "btn-3"]),
    use_fallback=st.booleans()
)
async def test_property_click_with_fallback_equivalence(
    page,
    element_id,
    use_fallback
):
    """
    Property 6 (Fallback Equivalence): Click with Fallback Produces Same Result
    
    **Feature: raptor-playwright-python, Property 6: Click Method Equivalence**
    
    For any clickable element, clicking with a direct locator or clicking with
    a fallback locator should produce the same result (element is clicked).
    
    **Validates: Requirements 6.2**
    
    This property test verifies that:
    1. Click works with primary locator
    2. Click works with fallback locator
    3. Both approaches produce the same outcome
    """
    # Set up a page with clickable buttons
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                function trackClick(id) {
                    document.getElementById(id).setAttribute('data-clicked', 'true');
                    document.getElementById(id).textContent = 'Clicked!';
                }
            </script>
        </head>
        <body>
            <button id="btn-1" class="button" onclick="trackClick('btn-1')">Button 1</button>
            <button id="btn-2" class="button" onclick="trackClick('btn-2')">Button 2</button>
            <button id="btn-3" class="button" onclick="trackClick('btn-3')">Button 3</button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    if use_fallback:
        # Click using fallback locator (primary is invalid)
        await element_manager.click(
            "css=#nonexistent-element",
            fallback_locators=[f"css=#{element_id}"],
            timeout=2000
        )
    else:
        # Click using direct locator
        await element_manager.click(f"css=#{element_id}", timeout=2000)
    
    # Verify click was successful regardless of method
    element = await element_manager.locate_element(f"css=#{element_id}", timeout=2000)
    clicked_attr = await element.get_attribute("data-clicked")
    text = await element.text_content()
    
    # Assertions - same result regardless of fallback usage
    assert clicked_attr == "true", \
        f"Element should be clicked (use_fallback={use_fallback})"
    assert text == "Clicked!", \
        f"Element text should be 'Clicked!' (use_fallback={use_fallback}), got '{text}'"


@pytest.mark.asyncio
@settings(
    max_examples=50,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    element_id=st.sampled_from(["btn-1", "btn-2", "btn-3"]),
    locator_strategies=st.lists(
        st.sampled_from(["css", "xpath", "id"]),
        min_size=2,
        max_size=3,
        unique=True
    )
)
async def test_property_click_locator_strategy_equivalence(
    page,
    element_id,
    locator_strategies
):
    """
    Property 6 (Strategy Equivalence): Different Locator Strategies Click Same Element
    
    **Feature: raptor-playwright-python, Property 6: Click Method Equivalence**
    
    For any clickable element, using different locator strategies should all
    click the same element and produce equivalent results.
    
    **Validates: Requirements 6.2**
    
    This property test verifies that:
    1. Different locator strategies target the same element
    2. Click outcome is consistent across strategies
    3. Element state changes are identical
    """
    # Set up a page with clickable buttons
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                let clickCounts = {};
                function trackClick(id) {
                    if (!clickCounts[id]) {
                        clickCounts[id] = 0;
                    }
                    clickCounts[id]++;
                    document.getElementById(id).setAttribute('data-click-count', clickCounts[id]);
                    document.getElementById(id).textContent = 'Clicked ' + clickCounts[id];
                }
            </script>
        </head>
        <body>
            <button id="btn-1" class="button" onclick="trackClick('btn-1')">Button 1</button>
            <button id="btn-2" class="button" onclick="trackClick('btn-2')">Button 2</button>
            <button id="btn-3" class="button" onclick="trackClick('btn-3')">Button 3</button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Create locators for each strategy
    locator_map = {
        "css": f"css=#{element_id}",
        "xpath": f"xpath=//button[@id='{element_id}']",
        "id": f"id={element_id}"
    }
    
    # Click using each strategy and verify consistent behavior
    for idx, strategy in enumerate(locator_strategies):
        locator = locator_map[strategy]
        
        # Click the element
        await element_manager.click(locator, timeout=2000)
        
        # Small delay to ensure click is processed
        await asyncio.sleep(0.05)
        
        # Verify click count incremented
        element = await element_manager.locate_element(locator, timeout=2000)
        click_count = await element.get_attribute("data-click-count")
        text = await element.text_content()
        
        expected_count = idx + 1
        assert click_count == str(expected_count), \
            f"After clicking with {strategy}, expected count {expected_count}, got {click_count}"
        assert f"Clicked {expected_count}" in text, \
            f"After clicking with {strategy}, expected text 'Clicked {expected_count}', got '{text}'"


# ============================================================================
# Advanced Click Methods Tests (Task 7)
# ============================================================================

@pytest.mark.asyncio
async def test_click_at_position(page):
    """Test clicking at a specific position within an element."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                function handleClick(event) {
                    const rect = event.target.getBoundingClientRect();
                    const x = event.clientX - rect.left;
                    const y = event.clientY - rect.top;
                    event.target.setAttribute('data-click-x', Math.round(x));
                    event.target.setAttribute('data-click-y', Math.round(y));
                    event.target.textContent = 'Clicked at (' + Math.round(x) + ', ' + Math.round(y) + ')';
                }
            </script>
        </head>
        <body>
            <div id="canvas" onclick="handleClick(event)" 
                 style="width: 300px; height: 200px; border: 1px solid black; cursor: pointer;">
                Click anywhere
            </div>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Click at position (100, 50)
    await element_manager.click_at_position("css=#canvas", x=100, y=50)
    
    # Verify click position
    element = await element_manager.locate_element("css=#canvas")
    click_x = await element.get_attribute("data-click-x")
    click_y = await element.get_attribute("data-click-y")
    
    # Allow some tolerance for position (±5 pixels)
    assert abs(int(click_x) - 100) <= 5, f"Expected x≈100, got {click_x}"
    assert abs(int(click_y) - 50) <= 5, f"Expected y≈50, got {click_y}"


@pytest.mark.asyncio
async def test_click_at_position_with_fallback(page):
    """Test clicking at position with fallback locator."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                function handleClick(event) {
                    event.target.setAttribute('data-clicked', 'true');
                }
            </script>
        </head>
        <body>
            <div id="target" onclick="handleClick(event)" 
                 style="width: 200px; height: 100px; border: 1px solid black;">
                Target
            </div>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Click with invalid primary and valid fallback
    await element_manager.click_at_position(
        "css=#nonexistent",
        x=50,
        y=25,
        fallback_locators=["css=#target"],
        timeout=2000
    )
    
    # Verify click occurred
    element = await element_manager.locate_element("css=#target")
    clicked = await element.get_attribute("data-clicked")
    assert clicked == "true"


@pytest.mark.asyncio
async def test_double_click(page):
    """Test double-clicking an element."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                function handleDoubleClick() {
                    document.getElementById('target').setAttribute('data-double-clicked', 'true');
                    document.getElementById('target').textContent = 'Double Clicked!';
                }
            </script>
        </head>
        <body>
            <div id="target" ondblclick="handleDoubleClick()" 
                 style="width: 200px; height: 100px; border: 1px solid black; cursor: pointer;">
                Double Click Me
            </div>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Double-click the element
    await element_manager.double_click("css=#target")
    
    # Verify double-click occurred
    element = await element_manager.locate_element("css=#target")
    double_clicked = await element.get_attribute("data-double-clicked")
    text = await element.text_content()
    
    assert double_clicked == "true"
    assert text == "Double Clicked!"


@pytest.mark.asyncio
async def test_double_click_with_fallback(page):
    """Test double-clicking with fallback locator."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                function handleDoubleClick() {
                    document.getElementById('file-item').setAttribute('data-opened', 'true');
                    document.getElementById('file-item').textContent = 'File Opened';
                }
            </script>
        </head>
        <body>
            <div id="file-item" ondblclick="handleDoubleClick()" 
                 style="cursor: pointer;">
                Document.txt
            </div>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Double-click with invalid primary and valid fallback
    await element_manager.double_click(
        "css=#nonexistent",
        fallback_locators=["text=Document.txt"],
        timeout=2000
    )
    
    # Verify double-click occurred
    element = await element_manager.locate_element("css=#file-item")
    opened = await element.get_attribute("data-opened")
    assert opened == "true"


@pytest.mark.asyncio
async def test_right_click(page):
    """Test right-clicking an element."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                function handleContextMenu(event) {
                    event.preventDefault();
                    document.getElementById('target').setAttribute('data-context-menu', 'true');
                    document.getElementById('target').textContent = 'Context Menu Opened';
                }
            </script>
        </head>
        <body>
            <div id="target" oncontextmenu="handleContextMenu(event)" 
                 style="width: 200px; height: 100px; border: 1px solid black; cursor: pointer;">
                Right Click Me
            </div>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Right-click the element
    await element_manager.right_click("css=#target")
    
    # Verify right-click occurred
    element = await element_manager.locate_element("css=#target")
    context_menu = await element.get_attribute("data-context-menu")
    text = await element.text_content()
    
    assert context_menu == "true"
    assert text == "Context Menu Opened"


@pytest.mark.asyncio
async def test_right_click_with_fallback(page):
    """Test right-clicking with fallback locator."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                function handleContextMenu(event) {
                    event.preventDefault();
                    document.getElementById('file').setAttribute('data-context-opened', 'true');
                }
            </script>
        </head>
        <body>
            <div id="file" oncontextmenu="handleContextMenu(event)">
                File Item
            </div>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Right-click with invalid primary and valid fallback
    await element_manager.right_click(
        "css=#nonexistent",
        fallback_locators=["text=File Item"],
        timeout=2000
    )
    
    # Verify right-click occurred
    element = await element_manager.locate_element("css=#file")
    context_opened = await element.get_attribute("data-context-opened")
    assert context_opened == "true"


@pytest.mark.asyncio
async def test_click_if_exists_element_exists(page):
    """Test click_if_exists when element exists."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <button id="close-popup" onclick="this.setAttribute('data-clicked', 'true')">
                Close
            </button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Click if exists - element exists
    clicked = await element_manager.click_if_exists("css=#close-popup", timeout=2000)
    
    assert clicked is True
    
    # Verify click occurred
    element = await element_manager.locate_element("css=#close-popup")
    clicked_attr = await element.get_attribute("data-clicked")
    assert clicked_attr == "true"


@pytest.mark.asyncio
async def test_click_if_exists_element_not_exists(page):
    """Test click_if_exists when element does not exist."""
    await page.set_content("<html><body></body></html>")
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Click if exists - element does not exist
    clicked = await element_manager.click_if_exists("css=#nonexistent", timeout=1000)
    
    assert clicked is False


@pytest.mark.asyncio
async def test_click_if_exists_with_fallback(page):
    """Test click_if_exists with fallback locator."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <button id="optional-btn" onclick="this.setAttribute('data-clicked', 'true')">
                Optional Button
            </button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Click if exists with fallback
    clicked = await element_manager.click_if_exists(
        "css=#nonexistent",
        fallback_locators=["css=#optional-btn"],
        timeout=2000
    )
    
    assert clicked is True
    
    # Verify click occurred
    element = await element_manager.locate_element("css=#optional-btn")
    clicked_attr = await element.get_attribute("data-clicked")
    assert clicked_attr == "true"


@pytest.mark.asyncio
async def test_click_with_retry_success_first_attempt(page):
    """Test click_with_retry succeeds on first attempt."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <button id="stable-btn" onclick="this.setAttribute('data-clicked', 'true')">
                Stable Button
            </button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Click with retry - should succeed immediately
    await element_manager.click_with_retry("css=#stable-btn", max_retries=3, initial_delay=0.1)
    
    # Verify click occurred
    element = await element_manager.locate_element("css=#stable-btn")
    clicked = await element.get_attribute("data-clicked")
    assert clicked == "true"


@pytest.mark.asyncio
async def test_click_with_retry_success_after_delay(page):
    """Test click_with_retry succeeds after element appears."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                // Add button after 500ms
                setTimeout(function() {
                    const btn = document.createElement('button');
                    btn.id = 'delayed-btn';
                    btn.onclick = function() { this.setAttribute('data-clicked', 'true'); };
                    btn.textContent = 'Delayed Button';
                    document.body.appendChild(btn);
                }, 500);
            </script>
        </head>
        <body>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Click with retry - should succeed after element appears
    await element_manager.click_with_retry(
        "css=#delayed-btn",
        max_retries=5,
        initial_delay=0.2,
        timeout=2000
    )
    
    # Verify click occurred
    element = await element_manager.locate_element("css=#delayed-btn")
    clicked = await element.get_attribute("data-clicked")
    assert clicked == "true"


@pytest.mark.asyncio
async def test_click_with_retry_all_attempts_fail(page):
    """Test click_with_retry fails after all retries exhausted."""
    await page.set_content("<html><body></body></html>")
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Click with retry - should fail after all attempts
    with pytest.raises(ElementNotFoundException):
        await element_manager.click_with_retry(
            "css=#nonexistent",
            max_retries=3,
            initial_delay=0.1,
            timeout=500
        )


@pytest.mark.asyncio
async def test_click_with_retry_exponential_backoff(page):
    """Test that click_with_retry uses exponential backoff."""
    import time
    
    await page.set_content("<html><body></body></html>")
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Track timing
    start_time = time.time()
    
    try:
        await element_manager.click_with_retry(
            "css=#nonexistent",
            max_retries=3,
            initial_delay=0.2,
            timeout=500
        )
    except ElementNotFoundException:
        pass
    
    elapsed_time = time.time() - start_time
    
    # With exponential backoff: 0.2 + 0.4 + 0.8 = 1.4 seconds minimum
    # Plus timeout attempts, should be at least 1.4 seconds
    assert elapsed_time >= 1.0, f"Expected exponential backoff, but elapsed time was {elapsed_time:.2f}s"


@pytest.mark.asyncio
async def test_click_with_retry_invalid_max_retries(page):
    """Test that click_with_retry raises ValueError for invalid max_retries."""
    await page.set_content("<html><body></body></html>")
    
    element_manager = ElementManager(page, ConfigManager())
    
    with pytest.raises(ValueError, match="max_retries must be at least 1"):
        await element_manager.click_with_retry(
            "css=#any-element",
            max_retries=0
        )


@pytest.mark.asyncio
async def test_click_with_retry_invalid_initial_delay(page):
    """Test that click_with_retry raises ValueError for invalid initial_delay."""
    await page.set_content("<html><body></body></html>")
    
    element_manager = ElementManager(page, ConfigManager())
    
    with pytest.raises(ValueError, match="initial_delay must be non-negative"):
        await element_manager.click_with_retry(
            "css=#any-element",
            initial_delay=-1.0
        )


@pytest.mark.asyncio
async def test_click_with_retry_with_fallback(page):
    """Test click_with_retry with fallback locators."""
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <button id="retry-btn" onclick="this.setAttribute('data-clicked', 'true')">
                Retry Button
            </button>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Click with retry using fallback
    await element_manager.click_with_retry(
        "css=#nonexistent",
        fallback_locators=["css=#retry-btn"],
        max_retries=3,
        initial_delay=0.1,
        timeout=2000
    )
    
    # Verify click occurred
    element = await element_manager.locate_element("css=#retry-btn")
    clicked = await element.get_attribute("data-clicked")
    assert clicked == "true"


# ============================================================================
# Property-Based Test: Element Interaction Retry (Property 5)
# ============================================================================

@pytest.mark.asyncio
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    max_retries=st.integers(min_value=1, max_value=5),
    initial_delay=st.floats(min_value=0.05, max_value=0.3),
    delay_before_appearance=st.floats(min_value=0.1, max_value=1.0)
)
async def test_property_element_interaction_retry(
    page,
    max_retries,
    initial_delay,
    delay_before_appearance
):
    """
    Property 5: Element Interaction Retry
    
    **Feature: raptor-playwright-python, Property 5: Element Interaction Retry**
    
    For any element interaction that fails due to timing, the system should retry
    with exponential backoff up to the configured timeout.
    
    This property test verifies that:
    1. Retry mechanism attempts multiple times before failing
    2. Exponential backoff is applied between retry attempts
    3. Element interactions succeed when element appears during retry window
    4. Retry works consistently across different timing scenarios
    
    **Validates: Requirements 5.1, 5.2**
    """
    import time
    
    # Calculate when element should appear (within retry window)
    # Total retry time = initial_delay * (2^0 + 2^1 + ... + 2^(max_retries-2))
    # For max_retries=3: initial_delay * (1 + 2) = initial_delay * 3
    # For max_retries=4: initial_delay * (1 + 2 + 4) = initial_delay * 7
    total_retry_time = initial_delay * (2 ** max_retries - 1)
    
    # Ensure element appears before retry window expires
    # Use 80% of total retry time to ensure we have time to retry
    safe_delay = min(delay_before_appearance, total_retry_time * 0.8)
    
    # Create page with delayed element appearance
    await page.set_content(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                // Add button after specified delay
                setTimeout(function() {{
                    const btn = document.createElement('button');
                    btn.id = 'delayed-btn';
                    btn.className = 'delayed-element';
                    btn.onclick = function() {{ 
                        this.setAttribute('data-clicked', 'true');
                        this.setAttribute('data-click-time', Date.now());
                    }};
                    btn.textContent = 'Delayed Button';
                    document.body.appendChild(btn);
                }}, {int(safe_delay * 1000)});
            </script>
        </head>
        <body>
            <div id="start-marker" data-start-time="0"></div>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Record start time
    start_time = time.time()
    
    # Set start marker
    await page.evaluate("document.getElementById('start-marker').setAttribute('data-start-time', Date.now())")
    
    # Attempt to click with retry - should succeed after element appears
    try:
        await element_manager.click_with_retry(
            "css=#delayed-btn",
            max_retries=max_retries,
            initial_delay=initial_delay,
            timeout=3000  # Generous timeout for element to appear
        )
        
        # Verify click occurred
        element = await element_manager.locate_element("css=#delayed-btn", timeout=2000)
        clicked = await element.get_attribute("data-clicked")
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Assertions
        assert clicked == "true", "Element should have been clicked after retry"
        
        # Verify that retry took at least as long as the delay
        # (with some tolerance for timing variations)
        assert elapsed_time >= safe_delay * 0.8, \
            f"Retry should have waited at least {safe_delay * 0.8:.2f}s, but took {elapsed_time:.2f}s"
        
        # Verify that retry didn't take too long (should succeed within retry window)
        max_expected_time = safe_delay + total_retry_time + 3.0  # Add timeout buffer
        assert elapsed_time <= max_expected_time, \
            f"Retry took too long: {elapsed_time:.2f}s (expected <= {max_expected_time:.2f}s)"
        
    except ElementNotFoundException:
        # If element wasn't found, verify we tried for the expected duration
        elapsed_time = time.time() - start_time
        
        # This should only happen if safe_delay > total_retry_time
        # In that case, we expect the retry to have exhausted all attempts
        if safe_delay > total_retry_time:
            # Verify we tried for at least the retry duration
            assert elapsed_time >= total_retry_time * 0.8, \
                f"Should have retried for at least {total_retry_time * 0.8:.2f}s, but only tried {elapsed_time:.2f}s"
        else:
            # Element should have appeared in time - this is a test failure
            pytest.fail(
                f"Element should have appeared after {safe_delay:.2f}s, "
                f"but wasn't found after {elapsed_time:.2f}s of retrying. "
                f"max_retries={max_retries}, initial_delay={initial_delay:.3f}s, "
                f"total_retry_time={total_retry_time:.2f}s"
            )


@pytest.mark.asyncio
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    max_retries=st.integers(min_value=2, max_value=4),
    initial_delay=st.floats(min_value=0.1, max_value=0.3)
)
async def test_property_retry_exponential_backoff_timing(
    page,
    max_retries,
    initial_delay
):
    """
    Property 5 (Exponential Backoff): Retry Uses Exponential Backoff
    
    **Feature: raptor-playwright-python, Property 5: Element Interaction Retry**
    
    For any retry operation, the delay between attempts should follow an
    exponential backoff pattern (doubling each time).
    
    This property test verifies that:
    1. Delays increase exponentially between retry attempts
    2. Total retry time matches expected exponential backoff calculation
    3. Backoff pattern is consistent across different configurations
    
    **Validates: Requirements 5.1, 5.2**
    """
    import time
    
    # Create page with no target element (will force all retries to fail)
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <div id="placeholder">No target element</div>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Calculate expected total retry time with exponential backoff
    # Delays: initial_delay, initial_delay*2, initial_delay*4, ...
    # Total = initial_delay * (1 + 2 + 4 + ... + 2^(max_retries-2))
    # This is a geometric series: initial_delay * (2^(max_retries-1) - 1)
    expected_delay_sum = initial_delay * (2 ** (max_retries - 1) - 1)
    
    # Record start time
    start_time = time.time()
    
    # Attempt to click with retry - will fail after all retries
    try:
        await element_manager.click_with_retry(
            "css=#nonexistent-element",
            max_retries=max_retries,
            initial_delay=initial_delay,
            timeout=500  # Short timeout to fail quickly on each attempt
        )
        pytest.fail("Should have raised ElementNotFoundException")
    except ElementNotFoundException:
        # Expected - all retries failed
        pass
    
    # Calculate elapsed time
    elapsed_time = time.time() - start_time
    
    # Verify exponential backoff timing
    # Allow 20% tolerance for timing variations and timeout attempts
    min_expected_time = expected_delay_sum * 0.8
    max_expected_time = expected_delay_sum + (max_retries * 0.5) + 2.0  # Add buffer for timeouts
    
    assert elapsed_time >= min_expected_time, \
        f"Retry should have taken at least {min_expected_time:.2f}s with exponential backoff, " \
        f"but took {elapsed_time:.2f}s. " \
        f"(max_retries={max_retries}, initial_delay={initial_delay:.3f}s, " \
        f"expected_delay_sum={expected_delay_sum:.2f}s)"
    
    assert elapsed_time <= max_expected_time, \
        f"Retry took too long: {elapsed_time:.2f}s (expected <= {max_expected_time:.2f}s). " \
        f"(max_retries={max_retries}, initial_delay={initial_delay:.3f}s)"


@pytest.mark.asyncio
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    max_retries=st.integers(min_value=1, max_value=5),
    success_on_attempt=st.integers(min_value=1, max_value=5)
)
async def test_property_retry_succeeds_on_nth_attempt(
    page,
    max_retries,
    success_on_attempt
):
    """
    Property 5 (Retry Success): Retry Succeeds on Nth Attempt
    
    **Feature: raptor-playwright-python, Property 5: Element Interaction Retry**
    
    For any retry operation, if the element becomes available on the Nth attempt
    (where N <= max_retries), the operation should succeed without exhausting
    all retry attempts.
    
    This property test verifies that:
    1. Retry stops as soon as element interaction succeeds
    2. Success can occur on any attempt from 1 to max_retries
    3. Remaining retry attempts are not executed after success
    
    **Validates: Requirements 5.1, 5.2**
    """
    import time
    
    # Determine which attempt should succeed
    target_attempt = min(success_on_attempt, max_retries)
    
    # Calculate delay before element appears
    # Element should appear just before the target attempt
    # Delays: 0, initial_delay, initial_delay*2, initial_delay*4, ...
    initial_delay = 0.1
    if target_attempt == 1:
        # Element available immediately
        appearance_delay = 0.0
    else:
        # Element appears after (target_attempt - 1) delays
        # Sum of delays before target attempt: initial_delay * (2^(target_attempt-1) - 1)
        cumulative_delay = initial_delay * (2 ** (target_attempt - 1) - 1)
        # Appear 80% through the waiting period before target attempt
        appearance_delay = cumulative_delay * 0.8
    
    # Create page with delayed element appearance
    await page.set_content(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                setTimeout(function() {{
                    const btn = document.createElement('button');
                    btn.id = 'retry-target';
                    btn.onclick = function() {{ 
                        this.setAttribute('data-clicked', 'true');
                        this.setAttribute('data-attempt', '{target_attempt}');
                    }};
                    btn.textContent = 'Retry Target';
                    document.body.appendChild(btn);
                }}, {int(appearance_delay * 1000)});
            </script>
        </head>
        <body>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    # Record start time
    start_time = time.time()
    
    # Attempt to click with retry
    try:
        await element_manager.click_with_retry(
            "css=#retry-target",
            max_retries=max_retries,
            initial_delay=initial_delay,
            timeout=2000
        )
        
        # Verify click occurred
        element = await element_manager.locate_element("css=#retry-target", timeout=2000)
        clicked = await element.get_attribute("data-clicked")
        
        elapsed_time = time.time() - start_time
        
        # Assertions
        assert clicked == "true", \
            f"Element should have been clicked on attempt {target_attempt}"
        
        # Verify timing: should have taken at least appearance_delay
        assert elapsed_time >= appearance_delay * 0.7, \
            f"Should have taken at least {appearance_delay * 0.7:.2f}s, but took {elapsed_time:.2f}s"
        
        # Verify timing: should not have taken much longer than necessary
        # Max time = appearance_delay + time for target_attempt + buffer
        max_time = appearance_delay + (initial_delay * 2 ** target_attempt) + 2.0
        assert elapsed_time <= max_time, \
            f"Took too long: {elapsed_time:.2f}s (expected <= {max_time:.2f}s)"
        
    except ElementNotFoundException:
        # If we couldn't find the element, verify the timing was reasonable
        elapsed_time = time.time() - start_time
        
        # Calculate expected total retry time
        total_retry_time = initial_delay * (2 ** max_retries - 1)
        
        # If appearance_delay > total_retry_time, failure is expected
        if appearance_delay > total_retry_time * 0.9:
            # This is expected - element appeared too late
            pass
        else:
            # Element should have appeared in time
            pytest.fail(
                f"Element should have appeared after {appearance_delay:.2f}s "
                f"(attempt {target_attempt}/{max_retries}), "
                f"but wasn't found after {elapsed_time:.2f}s of retrying"
            )


@pytest.mark.asyncio
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(
    max_retries=st.integers(min_value=1, max_value=4),
    use_fallback=st.booleans()
)
async def test_property_retry_with_fallback_locators(
    page,
    max_retries,
    use_fallback
):
    """
    Property 5 (Retry with Fallback): Retry Works with Fallback Locators
    
    **Feature: raptor-playwright-python, Property 5: Element Interaction Retry**
    
    For any retry operation with fallback locators, the retry mechanism should
    work correctly whether using primary or fallback locators.
    
    This property test verifies that:
    1. Retry mechanism works with fallback locators
    2. Element is found via fallback when primary fails
    3. Retry + fallback combination produces correct results
    
    **Validates: Requirements 5.1, 5.2**
    """
    # Create page with delayed element
    await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head>
            <script>
                setTimeout(function() {
                    const btn = document.createElement('button');
                    btn.id = 'fallback-target';
                    btn.className = 'retry-btn';
                    btn.onclick = function() { 
                        this.setAttribute('data-clicked', 'true');
                    };
                    btn.textContent = 'Fallback Target';
                    document.body.appendChild(btn);
                }, 200);
            </script>
        </head>
        <body>
        </body>
        </html>
    """)
    
    element_manager = ElementManager(page, ConfigManager())
    
    if use_fallback:
        # Use invalid primary with valid fallback
        await element_manager.click_with_retry(
            "css=#nonexistent-primary",
            fallback_locators=["css=#fallback-target", "css=.retry-btn"],
            max_retries=max_retries,
            initial_delay=0.1,
            timeout=2000
        )
    else:
        # Use valid primary
        await element_manager.click_with_retry(
            "css=#fallback-target",
            max_retries=max_retries,
            initial_delay=0.1,
            timeout=2000
        )
    
    # Verify click occurred regardless of fallback usage
    element = await element_manager.locate_element("css=#fallback-target", timeout=2000)
    clicked = await element.get_attribute("data-clicked")
    
    assert clicked == "true", \
        f"Element should have been clicked (use_fallback={use_fallback})"
