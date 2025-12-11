# Integration Tests Quick Reference

## Overview
Integration tests verify that RAPTOR framework components work together correctly in real-world scenarios.

## Running Tests

### All Integration Tests
```bash
pytest tests/test_integration.py -v
```

### Specific Test Class
```bash
# Browser + Element Manager
pytest tests/test_integration.py::TestBrowserElementManagerIntegration -v

# Database + Config
pytest tests/test_integration.py::TestDatabaseConfigIntegration -v

# Session + Browser
pytest tests/test_integration.py::TestSessionBrowserIntegration -v

# Page Objects
pytest tests/test_integration.py::TestPageObjectsIntegration -v

# Complex Scenarios
pytest tests/test_integration.py::TestComplexIntegrationScenarios -v
```

### Single Test
```bash
pytest tests/test_integration.py::TestBrowserElementManagerIntegration::test_browser_launch_and_element_location -v
```

## Test Categories

### 1. Browser + Element Manager (4 tests)
- ✅ Browser launch and element location
- ✅ Complete interaction workflow
- ✅ Multiple contexts isolation
- ✅ Element fallback with real browser

### 2. Database + Config (2 tests)
- ✅ Database with config timeout
- ✅ Config-driven operations

### 3. Session + Browser (3 tests)
- ✅ Save and restore session
- ✅ Session persistence across instances
- ✅ Multiple sessions with different browsers

### 4. Page Objects (3 tests)
- ✅ BasePage with browser and elements
- ✅ TableManager with real table
- ✅ End-to-end page object workflow

### 5. Complex Scenarios (3 tests)
- ✅ Full framework integration
- ✅ Multi-page workflow
- ✅ Concurrent operations

## Prerequisites

### Install Playwright Browsers
```bash
playwright install chromium firefox webkit
```

### Install Dependencies
```bash
pip install -e .
```

## Common Issues

### Issue: Browsers Not Installed
**Error**: `Executable doesn't exist at ...`
**Solution**: Run `playwright install chromium`

### Issue: Certificate Errors
**Error**: `self-signed certificate in certificate chain`
**Solution**: Configure corporate proxy or use `--ignore-certificate-errors`

### Issue: Timeout Errors
**Error**: `TimeoutException: Operation timed out`
**Solution**: Increase timeout in test or check network connectivity

## Test Patterns

### Basic Integration Test
```python
@pytest.mark.asyncio
async def test_integration():
    browser_manager = BrowserManager()
    try:
        await browser_manager.launch_browser("chromium", headless=True)
        page = await browser_manager.create_page()
        
        # Test integration
        element_manager = ElementManager(page, ConfigManager())
        await page.set_content("<h1 id='test'>Hello</h1>")
        element = await element_manager.locate_element("css=#test")
        
        assert element is not None
    finally:
        await browser_manager.close_browser()
```

### Multi-Component Integration
```python
@pytest.mark.asyncio
async def test_multi_component():
    browser_manager = BrowserManager()
    session_manager = SessionManager()
    
    try:
        await browser_manager.launch_browser("chromium", headless=True)
        page = await browser_manager.create_page()
        
        # Save session
        await session_manager.save_session(page, "test")
        
        # Verify session
        assert session_manager.validate_session("test")
    finally:
        await browser_manager.close_browser()
```

## CI/CD Integration

### GitHub Actions
```yaml
- name: Install Playwright
  run: playwright install --with-deps chromium

- name: Run Integration Tests
  run: pytest tests/test_integration.py -v --tb=short
```

### Azure DevOps
```yaml
- script: |
    playwright install --with-deps chromium
    pytest tests/test_integration.py -v
  displayName: 'Integration Tests'
```

## Performance

### Expected Execution Times
- Browser + Element Manager: ~5-10 seconds
- Database + Config: ~2-3 seconds
- Session + Browser: ~8-12 seconds
- Page Objects: ~10-15 seconds
- Complex Scenarios: ~15-20 seconds
- **Total**: ~40-60 seconds

## Coverage

### Components Tested
- ✅ BrowserManager
- ✅ ElementManager
- ✅ SessionManager
- ✅ ConfigManager
- ✅ DatabaseManager
- ✅ BasePage
- ✅ TableManager

### Integration Points
- ✅ Browser ↔ Element Manager
- ✅ Database ↔ Config Manager
- ✅ Session ↔ Browser Manager
- ✅ Page Objects ↔ All Managers

## Troubleshooting

### Debug Mode
```bash
pytest tests/test_integration.py -v --tb=long --log-cli-level=DEBUG
```

### Run Single Test with Debugging
```bash
pytest tests/test_integration.py::TestBrowserElementManagerIntegration::test_browser_launch_and_element_location -v -s
```

### Check Test Collection
```bash
pytest tests/test_integration.py --collect-only
```

## Best Practices

1. **Always Clean Up**: Use `try/finally` blocks
2. **Use Headless Mode**: For CI/CD environments
3. **Set Appropriate Timeouts**: Based on environment
4. **Isolate Tests**: Each test should be independent
5. **Mock External Dependencies**: When appropriate

## Quick Commands

```bash
# Run all integration tests
pytest tests/test_integration.py -v

# Run with coverage
pytest tests/test_integration.py --cov=raptor

# Run in parallel (if pytest-xdist installed)
pytest tests/test_integration.py -n auto

# Run with HTML report
pytest tests/test_integration.py --html=report.html

# Run with markers
pytest tests/test_integration.py -m "not slow"
```

## Related Documentation
- [Task 41 Completion Summary](TASK_41_COMPLETION_SUMMARY.md)
- [Unit Tests](../tests/)
- [Property-Based Tests](../tests/test_property_*.py)
- [User Guide](USER_GUIDE_QUICK_REFERENCE.md)
