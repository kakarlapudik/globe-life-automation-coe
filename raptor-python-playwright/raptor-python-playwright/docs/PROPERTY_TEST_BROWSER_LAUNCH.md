# Property-Based Test: Browser Launch Consistency

## Overview

This document describes the property-based test implementation for **Property 1: Browser Launch Consistency** as specified in the RAPTOR Python Playwright Framework design document.

## Property Definition

**Property 1: Browser Launch Consistency**

*For any* valid browser type (Chromium, Firefox, WebKit) and any headless mode (True/False), launching a browser should result in a valid browser instance that can create contexts and pages.

**Validates: Requirements 1.1**

> "WHEN the framework is initialized THEN the system SHALL support Chromium, Firefox, and WebKit browsers"

## Test Implementation

### Location
`raptor-python-playwright/tests/test_browser_manager.py::TestBrowserManagerProperties::test_property_browser_launch_consistency`

### Test Strategy

The property-based test uses Hypothesis to generate random combinations of:
- **Browser types**: chromium, firefox, webkit
- **Headless modes**: True, False

For each generated combination, the test validates:

1. **Browser Launch**: Browser launches successfully with generated parameters
2. **Browser Validity**: Browser instance is not None and is of correct type
3. **Browser Connectivity**: Browser is connected and responsive
4. **Browser Manager State**: Manager correctly tracks browser type and launch status
5. **Context Creation**: Browser can create valid browser contexts
6. **Page Creation**: Browser can create valid pages within contexts
7. **Page Functionality**: Pages can navigate to URLs
8. **Cleanup**: All resources are properly cleaned up after use

### Test Configuration

```python
@given(
    browser_type=st.sampled_from(["chromium", "firefox", "webkit"]),
    headless=st.booleans()
)
@settings(max_examples=100, deadline=60000)  # 100 iterations, 60s timeout
```

- **Iterations**: 100 test cases (as required by design document)
- **Timeout**: 60 seconds per test case
- **Input Space**: 6 possible combinations (3 browsers × 2 headless modes)

## Test Code

```python
@pytest.mark.asyncio
async def test_property_browser_launch_consistency(self, browser_type, headless):
    """
    **Feature: raptor-playwright-python, Property 1: Browser Launch Consistency**
    
    Property: For any valid browser type (Chromium, Firefox, WebKit) and any
    headless mode (True/False), launching a browser should result in a valid
    browser instance that can create contexts and pages.
    
    **Validates: Requirements 1.1**
    """
    browser_manager = BrowserManager()
    
    try:
        # Step 1: Launch browser with generated parameters
        browser = await browser_manager.launch_browser(browser_type, headless=headless)
        
        # Step 2: Verify browser is valid and connected
        assert browser is not None
        assert isinstance(browser, Browser)
        assert browser.is_connected()
        assert browser_manager.is_browser_launched
        assert browser_manager.browser_type == browser_type.lower()
        
        # Step 3: Verify browser can create contexts
        context = await browser_manager.create_context()
        assert context is not None
        assert isinstance(context, BrowserContext)
        assert len(browser_manager.get_contexts()) >= 1
        
        # Step 4: Verify browser can create pages
        page = await browser_manager.create_page(context)
        assert page is not None
        assert isinstance(page, Page)
        assert not page.is_closed()
        assert len(browser_manager.get_pages()) >= 1
        
        # Step 5: Verify page is functional
        await page.goto("data:text/html,<h1>Test</h1>")
        assert page.url.startswith("data:")
        
    finally:
        # Step 6: Verify proper cleanup
        await browser_manager.close_browser()
        assert not browser_manager.is_browser_launched
        assert browser_manager.browser is None
        assert len(browser_manager.get_contexts()) == 0
        assert len(browser_manager.get_pages()) == 0
```

## Running the Test

### Prerequisites

1. Install Playwright browsers:
   ```bash
   playwright install
   ```

2. Ensure Python dependencies are installed:
   ```bash
   pip install -e ".[dev]"
   ```

### Execution

Run the property-based test:
```bash
pytest raptor-python-playwright/tests/test_browser_manager.py::TestBrowserManagerProperties::test_property_browser_launch_consistency -v
```

Run all browser manager tests:
```bash
pytest raptor-python-playwright/tests/test_browser_manager.py -v
```

## Expected Results

When browsers are properly installed, the test should:
- Generate 100 random test cases
- Test all browser types multiple times
- Test both headless and headed modes
- Complete successfully with all assertions passing
- Demonstrate that browser launch is consistent across all valid inputs

## Known Issues

### Browser Installation Required

The test requires Playwright browser binaries to be installed. If browsers are not installed, you'll see:

```
Error: BrowserType.launch: Executable doesn't exist at [path]
╔════════════════════════════════════════════════════════════╗
║ Looks like Playwright was just installed or updated.       ║
║ Please run the following command to download new browsers: ║
║                                                            ║
║     playwright install                                     ║
╚════════════════════════════════════════════════════════════╝
```

**Solution**: Run `playwright install` to download browser binaries.

### Network/Certificate Issues

In corporate environments with SSL inspection or proxy servers, browser installation may fail with certificate errors.

**Solutions**:
1. Configure proxy settings
2. Use `NODE_TLS_REJECT_UNAUTHORIZED=0` (not recommended for production)
3. Install browsers on a different machine and copy binaries
4. Use pre-installed system browsers with `channel` option

## Benefits of Property-Based Testing

This property-based test provides several advantages over traditional unit tests:

1. **Comprehensive Coverage**: Tests all browser types and modes automatically
2. **Edge Case Discovery**: Hypothesis may discover unexpected edge cases
3. **Regression Prevention**: Ensures consistency across all valid inputs
4. **Documentation**: Serves as executable specification of the property
5. **Confidence**: 100 iterations provide high confidence in correctness

## Related Tests

- Unit tests in `TestBrowserManager` class provide specific scenario testing
- This property test validates the general correctness property
- Together they provide comprehensive test coverage

## References

- Design Document: `.kiro/specs/raptor-playwright-python/design.md`
- Requirements: `.kiro/specs/raptor-playwright-python/requirements.md`
- Task List: `.kiro/specs/raptor-playwright-python/tasks.md`
- Hypothesis Documentation: https://hypothesis.readthedocs.io/
