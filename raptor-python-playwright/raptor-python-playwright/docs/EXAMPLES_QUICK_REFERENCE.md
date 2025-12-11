# RAPTOR Examples - Quick Reference

## Quick Start

```bash
# Run all examples
pytest examples/test_example_*.py -v

# Run specific example
pytest examples/test_example_login.py -v

# Run with output
pytest examples/test_example_login.py -v -s
```

## Example Files

| File | Purpose | Test Cases | Key Features |
|------|---------|------------|--------------|
| `test_example_login.py` | Authentication workflows | 5 | Login, validation, keyboard nav, session save |
| `test_example_data_driven.py` | Database-driven testing | 4 | DDDB integration, iterations, parametrization |
| `test_example_table_interaction.py` | Table operations | 6 | Row finding, editing, search, pagination |
| `test_example_multi_page_workflow.py` | Complex workflows | 3 | E-commerce flow, profile mgmt, admin ops |
| `test_example_session_reuse.py` | Session management | 7 | Save/restore, multi-user, performance |

## Common Code Snippets

### Login Pattern
```python
await base_page.navigate("https://example.com/login")
await element_manager.fill("css=#username", "user@example.com")
await element_manager.fill("css=#password", "password")
await element_manager.click("css=#login-button")
await page.wait_for_url("**/dashboard", timeout=10000)
```

### Data-Driven Pattern
```python
test_data = await db_manager.import_data(
    table="TestData", test_id=1001, iteration=1, instance=1
)
await element_manager.fill("css=#field", test_data.get("value"))
await db_manager.export_data(
    table="TestData", pk_id=test_data["pk_id"], 
    field="result", value="PASS"
)
```

### Table Pattern
```python
row_index = await table_manager.find_row_by_key(
    table_locator="css=#table", key_column=0, key_value="key"
)
value = await table_manager.get_cell_value("css=#table", row_index, 1)
await table_manager.set_cell_value("css=#table", row_index, 1, "new_value")
```

### Session Reuse Pattern
```python
# Create session
await session_manager.save_session(page, "my_session")

# Reuse session (50-70% faster!)
page = await session_manager.restore_session("my_session")
```

## Adaptation Guide

### Step 1: Copy Example
```bash
cp examples/test_example_login.py tests/test_my_login.py
```

### Step 2: Update URLs
```python
# Change from:
await base_page.navigate("https://example.com/login")

# To:
await base_page.navigate("https://your-app.com/login")
```

### Step 3: Update Locators
```python
# Change from:
await element_manager.fill("css=#username", "user")

# To:
await element_manager.fill("css=#your-username-id", "user")
```

### Step 4: Run Your Test
```bash
pytest tests/test_my_login.py -v
```

## Performance Tips

1. **Use Session Reuse**: 50-70% faster
2. **Run in Parallel**: `pytest examples/ -n 4`
3. **Use Headless Mode**: Default in examples
4. **Minimize Waits**: Only when necessary

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Timeout errors | Increase timeout: `config.set("browser.timeout", 30000)` |
| Element not found | Add explicit wait: `await element_manager.wait_for_element(...)` |
| DB connection fails | Check `settings.yaml` connection string |
| Session restore fails | Recreate session with fresh login |

## Resources

- **Full README**: `examples/README_EXAMPLES.md`
- **API Docs**: `docs/API_REFERENCE_GUIDE.md`
- **User Guide**: `docs/USER_GUIDE_QUICK_REFERENCE.md`
- **Completion Summary**: `docs/TASK_38_COMPLETION_SUMMARY.md`

## Example Test Structure

```python
import pytest
from raptor.core.browser_manager import BrowserManager
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.pages.base_page import BasePage

@pytest.mark.asyncio
class TestMyFeature:
    async def test_my_scenario(self):
        """Test description"""
        config = ConfigManager()
        browser_manager = BrowserManager(config)
        
        try:
            browser = await browser_manager.launch_browser("chromium", headless=True)
            context = await browser_manager.create_context()
            page = await browser_manager.create_page(context)
            
            element_manager = ElementManager(page, config)
            base_page = BasePage(page, element_manager)
            
            # Your test code here
            await base_page.navigate("https://your-app.com")
            # ... more test steps ...
            
        finally:
            await browser_manager.close_browser()
```

## Next Steps

1. Review examples in `examples/` directory
2. Read full README: `examples/README_EXAMPLES.md`
3. Copy and adapt examples for your needs
4. Consult API docs for detailed method information
5. Check troubleshooting guide for common issues

---

**Quick Tip**: Start with `test_example_login.py` - it's the simplest and most commonly needed pattern!
