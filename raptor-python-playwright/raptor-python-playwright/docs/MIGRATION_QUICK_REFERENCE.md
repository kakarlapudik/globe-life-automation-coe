# RAPTOR Migration Quick Reference

## Quick Syntax Conversions

### Basic Patterns

| Java | Python |
|------|--------|
| `public void method()` | `async def method(self):` |
| `public String method()` | `async def method(self) -> str:` |
| `Web.click(locator)` | `await element_manager.click(locator)` |
| `Web.type(locator, text)` | `await element_manager.fill(locator, text)` |
| `if (condition) { }` | `if condition:` |
| `for (String item : items) { }` | `for item in items:` |
| `try { } catch (Exception e) { }` | `try: except Exception as e:` |
| `null` | `None` |
| `true/false` | `True/False` |

### Common Method Conversions

```python
# Navigation
Web.navigate(url)           → await page.goto(url)
Web.refresh()               → await page.reload()

# Clicks
Web.click(loc)              → await element_manager.click(loc)
Web.doubleClick(loc)        → await element_manager.double_click(loc)
Web.rightClick(loc)         → await element_manager.right_click(loc)

# Input
Web.type(loc, text)         → await element_manager.fill(loc, text)
Web.clear(loc)              → await element_manager.clear(loc)

# Verification
Web.verifyExists(loc)       → await verification.verify_exists(loc)
Web.verifyText(loc, text)   → await verification.verify_text(loc, text)

# Wait
Web.waitForElement(loc)     → await element_manager.wait_for_element(loc)

# Table
Table.findRowByKey(...)     → await table_manager.find_row_by_key(...)
Table.getCellValue(...)     → await table_manager.get_cell_value(...)

# Database
Dms.databaseImport(...)     → await db_manager.import_data(...)
Dms.databaseExport(...)     → await db_manager.export_data(...)
```

## Common Pitfalls

1. **Missing `await`** - Always await async calls
2. **Missing `@pytest.mark.asyncio`** - Required for async tests
3. **Wrong locator syntax** - Use `css=`, `xpath=`, `text=` prefixes
4. **Naming conventions** - Use `snake_case` not `camelCase`
5. **`null` vs `None`** - Use `None` in Python

## Test Template

```python
import pytest

@pytest.mark.asyncio
class TestExample:
    """Test suite description."""
    
    async def test_something(self, page, element_manager):
        """Test description."""
        # Navigate
        await page.goto("https://example.com")
        
        # Interact
        await element_manager.fill("css=#input", "value")
        await element_manager.click("css=#button")
        
        # Verify
        text = await element_manager.get_text("css=#result")
        assert text == "expected"
```

## Page Object Template

```python
from raptor.pages import BasePage

class MyPage(BasePage):
    """Page description."""
    
    def __init__(self, page, element_manager):
        super().__init__(page, element_manager)
        self.button = "css=#button"
        self.input = "css=#input"
    
    async def do_action(self, value: str):
        """Action description."""
        await self.element_manager.fill(self.input, value)
        await self.element_manager.click(self.button)
```

## Automated Conversion

```bash
# Convert single file
raptor migrate convert --input MyTest.java --output my_test.py

# Convert directory
raptor migrate convert --input tests/ --output python_tests/

# Validate DDFE
raptor migrate validate-ddfe --file elements.xml

# Check compatibility
raptor migrate check --input tests/
```
