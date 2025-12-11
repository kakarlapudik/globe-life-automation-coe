# pytest Fixtures Quick Reference

## Fixture Summary

| Fixture | Scope | Type | Purpose |
|---------|-------|------|---------|
| `config` | Session | Sync | Configuration access |
| `browser_manager` | Function | Async | Browser lifecycle management |
| `browser` | Function | Async | Launched browser instance |
| `context` | Function | Async | Browser context for isolation |
| `page` | Function | Async | Page for navigation/interaction |
| `element_manager` | Function | Async | Element interaction manager |
| `database` | Session | Sync | Database operations |
| `reporter` | Session | Sync | Test reporting |
| `temp_dir` | Function | Sync | Temporary directory |
| `mock_page_url` | Function | Sync | Mock URL for testing |
| `worker_id` | Session | Sync | Parallel execution worker ID |

## Quick Examples

### Basic Page Test
```python
@pytest.mark.asyncio
async def test_page(page):
    await page.goto("https://example.com")
    assert "Example" in await page.title()
```

### Element Interaction
```python
@pytest.mark.asyncio
async def test_interaction(element_manager, page):
    await page.goto("https://example.com")
    await element_manager.click("css=#button")
    await element_manager.fill("css=#input", "value")
```

### Configuration Access
```python
def test_config(config):
    timeout = config.get("timeouts.default")
    assert timeout == 10000
```

### Database Query
```python
def test_database(database):
    if database is None:
        pytest.skip("Database not configured")
    result = database.execute_query("SELECT * FROM TestData")
    assert len(result) > 0
```

### Browser Manager
```python
@pytest.mark.asyncio
async def test_browser_manager(browser_manager):
    await browser_manager.launch_browser("chromium", headless=True)
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
```

## Environment Variables

```bash
TEST_ENV=staging pytest          # Set environment
TEST_BROWSER=firefox pytest      # Set browser type
SKIP_SLOW=1 pytest              # Skip slow tests
```

## Parallel Execution

```bash
pytest -n auto                   # Use all CPU cores
pytest -n 4                      # Use 4 workers
```

## Custom Markers

```python
@pytest.mark.browser             # Browser test
@pytest.mark.database            # Database test
@pytest.mark.integration         # Integration test
@pytest.mark.slow                # Slow test
@pytest.mark.property            # Property-based test
```

## Automatic Features

✅ Screenshot on failure (page fixture)  
✅ Automatic cleanup (all fixtures)  
✅ Test isolation (function-scoped fixtures)  
✅ Parallel execution support  
✅ Automatic markers based on fixture usage  

## Common Patterns

### Skip if Database Not Available
```python
def test_db(database):
    if database is None:
        pytest.skip("Database not configured")
    # test code
```

### Use Temp Directory
```python
def test_files(temp_dir):
    file = temp_dir / "test.txt"
    file.write_text("content")
    assert file.exists()
```

### Parallel-Safe Tests
```python
async def test_parallel(page, worker_id):
    url = f"https://example.com?worker={worker_id}"
    await page.goto(url)
```

## See Also

- [Full Fixtures Guide](PYTEST_FIXTURES_GUIDE.md)
- [Browser Manager Guide](BROWSER_MANAGER_IMPLEMENTATION.md)
- [Element Manager Guide](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Database Manager Guide](DATABASE_MANAGER_IMPLEMENTATION.md)
