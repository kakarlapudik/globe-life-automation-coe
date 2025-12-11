# RAPTOR Python Playwright Framework
## Team Training Presentation

---

## Slide 1: Welcome to RAPTOR

### What is RAPTOR?
**R**obust **A**utomated **P**laywright **T**est **O**rchestration & **R**eporting

A modern Python-based test automation framework built on Microsoft Playwright, designed to replace the legacy Java Selenium framework.

### Key Benefits
- 🚀 **30% faster** test execution
- 🎯 **95%+ test stability**
- 🐍 **Pythonic** and easy to learn
- 🔄 **Session reuse** for faster debugging
- 📊 **Rich reporting** with screenshots

---

## Slide 2: Why Playwright?

### Advantages Over Selenium
- **Auto-wait**: Built-in smart waiting mechanisms
- **Multi-browser**: Chromium, Firefox, WebKit support
- **Fast**: Parallel execution and efficient automation
- **Modern**: Active development by Microsoft
- **Reliable**: Better handling of dynamic content

### Python Benefits
- Simpler syntax than Java
- Rich ecosystem of libraries
- Faster development cycles
- Better readability and maintainability

---

## Slide 3: Architecture Overview

```
┌─────────────────────────────────────────┐
│         Test Scripts (pytest)           │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│          RAPTOR Core Framework          │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ Browser  │  │ Element  │  │Session ││
│  │ Manager  │  │ Manager  │  │Manager ││
│  └──────────┘  └──────────┘  └────────┘│
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         Playwright Browser API          │
└─────────────────────────────────────────┘
```

---

## Slide 4: Core Components

### 1. Browser Manager
- Launches and manages browser instances
- Supports Chromium, Firefox, WebKit
- Handles headless/headed modes

### 2. Element Manager
- Locates elements with fallback strategies
- Provides interaction methods (click, fill, etc.)
- Smart waiting and synchronization

### 3. Session Manager
- Saves and restores browser sessions
- Reduces test startup time by 50%+
- Enables debugging without re-running setup

---

## Slide 5: Element Location Strategies

### Multiple Locator Support
```python
# CSS Selector
element_manager.locate_element("css=#login-button")

# XPath
element_manager.locate_element("xpath=//button[@id='login']")

# Text content
element_manager.locate_element("text=Login")

# Role-based (accessibility)
element_manager.locate_element("role=button[name='Login']")
```

### Automatic Fallback
```python
# Primary fails → tries fallback1 → tries fallback2
element_manager.locate_element(
    "css=#login-btn",
    fallback_locators=["xpath=//button[@id='login']", "text=Login"]
)
```

---

## Slide 6: Basic Test Structure

```python
import pytest
from raptor.core import BrowserManager, ElementManager

@pytest.mark.asyncio
async def test_login():
    # Setup
    browser_manager = BrowserManager()
    browser = await browser_manager.launch_browser("chromium")
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
    
    element_manager = ElementManager(page)
    
    # Navigate
    await page.goto("https://example.com/login")
    
    # Interact
    await element_manager.fill("css=#username", "testuser")
    await element_manager.fill("css=#password", "password123")
    await element_manager.click("css=#login-button")
    
    # Verify
    assert await element_manager.is_visible("css=#dashboard")
    
    # Cleanup
    await browser_manager.close_browser()
```

---

## Slide 7: Using pytest Fixtures

### Simplified Test with Fixtures
```python
@pytest.mark.asyncio
async def test_login_with_fixtures(browser, page, element_manager):
    # Setup is handled by fixtures!
    
    await page.goto("https://example.com/login")
    
    await element_manager.fill("css=#username", "testuser")
    await element_manager.fill("css=#password", "password123")
    await element_manager.click("css=#login-button")
    
    assert await element_manager.is_visible("css=#dashboard")
    
    # Cleanup is automatic!
```

### Available Fixtures
- `browser`: Browser instance
- `page`: Page instance
- `element_manager`: Element manager
- `database`: Database connection
- `config`: Configuration manager

---

## Slide 8: Session Reuse

### Save a Session
```python
from raptor.core import SessionManager

session_manager = SessionManager()

# After logging in and navigating to desired state
await session_manager.save_session(page, "logged_in_session")
```

### Restore a Session
```python
# In a new test run
page = await session_manager.restore_session("logged_in_session")

# Continue from where you left off!
await element_manager.click("css=#new-feature")
```

### Benefits
- Skip login steps
- Faster test development
- Quick debugging iterations

---

## Slide 9: Data-Driven Testing

### Using DDDB Integration
```python
from raptor.database import DatabaseManager

@pytest.mark.asyncio
async def test_user_creation(database):
    # Load test data from DDDB
    test_data = await database.import_data(
        table="UserTestData",
        test_id=101,
        iteration=1,
        instance=1
    )
    
    # Use the data
    await element_manager.fill("css=#first-name", test_data["first_name"])
    await element_manager.fill("css=#last-name", test_data["last_name"])
    await element_manager.fill("css=#email", test_data["email"])
    
    # Save results back
    await database.export_data(
        table="UserTestData",
        pk_id=test_data["pk_id"],
        field="result",
        value="PASS"
    )
```

---

## Slide 10: Table Interactions

### Working with Data Tables
```python
from raptor.pages import TableManager

table_manager = TableManager(page, element_manager)

# Find a row by key value
row_index = await table_manager.find_row_by_key(
    table_locator="css=#users-table",
    key_column=0,  # First column
    key_value="john.doe@example.com"
)

# Get cell value
name = await table_manager.get_cell_value(
    table_locator="css=#users-table",
    row=row_index,
    column=1
)

# Click a cell (e.g., edit button)
await table_manager.click_cell(
    table_locator="css=#users-table",
    row=row_index,
    column=4  # Actions column
)
```

---

## Slide 11: Verification Methods

### Hard Assertions (Stop on Failure)
```python
# Element existence
await element_manager.verify_exists("css=#success-message")
await element_manager.verify_not_exists("css=#error-message")

# Element state
await element_manager.verify_enabled("css=#submit-button")
await element_manager.verify_disabled("css=#locked-field")
await element_manager.verify_visible("css=#dashboard")

# Text content
await element_manager.verify_text("css=#welcome", "Welcome, John!")
```

### Soft Assertions (Continue on Failure)
```python
from raptor.core import SoftAssertionCollector

soft_assert = SoftAssertionCollector()

soft_assert.verify_exists("css=#field1", "Field 1 should exist")
soft_assert.verify_exists("css=#field2", "Field 2 should exist")
soft_assert.verify_exists("css=#field3", "Field 3 should exist")

# All failures reported at once
soft_assert.assert_all()
```

---

## Slide 12: Error Handling

### Exception Hierarchy
```python
from raptor.core.exceptions import (
    RaptorException,           # Base exception
    ElementNotFoundException,  # Element not found
    TimeoutException,          # Operation timeout
    DatabaseException,         # Database errors
    SessionException          # Session errors
)

try:
    await element_manager.click("css=#missing-button")
except ElementNotFoundException as e:
    print(f"Element not found: {e}")
    # Take screenshot for debugging
    await page.screenshot(path="error.png")
```

### Automatic Error Handling
- Screenshots captured on test failures
- Detailed error messages with context
- Stack traces preserved for debugging

---

## Slide 13: Configuration Management

### Environment-Specific Settings
```yaml
# config/environments/dev.yaml
browser:
  type: chromium
  headless: false
  
timeouts:
  default: 20000
  page_load: 30000
  
database:
  server: dev-db-server
  database: TestData_Dev
```

### Loading Configuration
```python
from raptor.core import ConfigManager

config = ConfigManager()
config.load_config(environment="dev")

browser_type = config.get("browser.type")  # "chromium"
timeout = config.get("timeouts.default")   # 20000
```

---

## Slide 14: Reporting

### HTML Test Reports
```bash
# Run tests with HTML report
pytest --html=report.html --self-contained-html
```

### Report Features
- ✅ Pass/fail statistics
- ⏱️ Execution duration
- 📸 Screenshots on failures
- 📝 Detailed error messages
- 📊 Test trends over time

### ALM/JIRA Integration
```python
from raptor.integrations import JiraIntegration

jira = JiraIntegration(
    server="https://jira.company.com",
    username="testuser",
    api_token="token123"
)

# Update test execution status
await jira.update_test_execution(
    test_key="TEST-123",
    status="PASS",
    comment="All assertions passed"
)
```

---

## Slide 15: CLI Usage

### Running Tests
```bash
# Run all tests
raptor run

# Run specific test file
raptor run tests/test_login.py

# Run with specific browser
raptor run --browser firefox

# Run in headless mode
raptor run --headless

# Run with specific environment
raptor run --env staging
```

### Session Management
```bash
# List saved sessions
raptor session list

# Delete a session
raptor session delete logged_in_session
```

---

## Slide 16: Migration from Java

### Method Mapping
| Java (Selenium) | Python (Playwright) |
|----------------|---------------------|
| `driver.findElement()` | `element_manager.locate_element()` |
| `element.click()` | `element_manager.click()` |
| `element.sendKeys()` | `element_manager.fill()` |
| `WebDriverWait` | Built-in auto-wait |
| `Select` | `element_manager.select_option()` |

### Key Differences
- **Async/await**: Python uses async syntax
- **Auto-wait**: No explicit waits needed
- **Locators**: More flexible locator strategies
- **Context**: Browser contexts for isolation

---

## Slide 17: Best Practices

### 1. Use Page Objects
```python
class LoginPage(BasePage):
    def __init__(self, page, element_manager):
        super().__init__(page, element_manager)
        self.username_field = "css=#username"
        self.password_field = "css=#password"
        self.login_button = "css=#login-button"
    
    async def login(self, username, password):
        await self.element_manager.fill(self.username_field, username)
        await self.element_manager.fill(self.password_field, password)
        await self.element_manager.click(self.login_button)
```

### 2. Use Fixtures for Setup/Teardown
### 3. Leverage Session Reuse
### 4. Use Soft Assertions for Multiple Checks
### 5. Add Meaningful Test Names and Comments

---

## Slide 18: Performance Tips

### Parallel Execution
```bash
# Run tests in parallel (4 workers)
pytest -n 4
```

### Session Reuse
- Save sessions after expensive setup
- Restore sessions for quick iterations
- 50%+ time savings

### Selective Test Execution
```bash
# Run only smoke tests
pytest -m smoke

# Run specific test IDs
pytest -k "test_login or test_logout"
```

---

## Slide 19: Debugging Tips

### 1. Run in Headed Mode
```python
browser = await browser_manager.launch_browser("chromium", headless=False)
```

### 2. Add Breakpoints
```python
import pdb; pdb.set_trace()  # Python debugger
```

### 3. Take Screenshots
```python
await page.screenshot(path="debug.png")
```

### 4. Use Playwright Inspector
```bash
PWDEBUG=1 pytest tests/test_login.py
```

### 5. Check Logs
```python
from raptor.utils import logger
logger.info("Debug message here")
```

---

## Slide 20: Common Pitfalls

### ❌ Forgetting async/await
```python
# Wrong
element_manager.click("css=#button")

# Correct
await element_manager.click("css=#button")
```

### ❌ Not Waiting for Elements
```python
# Playwright auto-waits, but for custom conditions:
await page.wait_for_selector("css=#dynamic-content")
```

### ❌ Hardcoded Timeouts
```python
# Wrong
await asyncio.sleep(5)

# Correct
await element_manager.wait_for_element("css=#element", timeout=5000)
```

---

## Slide 21: Resources

### Documentation
- 📚 **User Guide**: `docs/USER_GUIDE.md`
- 🔧 **API Reference**: `docs/API_REFERENCE_GUIDE.md`
- 🚀 **Quick Start**: `docs/GETTING_STARTED.rst`
- 🔄 **Migration Guide**: `docs/MIGRATION_GUIDE_COMPREHENSIVE.md`

### Examples
- 💡 **Example Tests**: `examples/`
- 📖 **Code Samples**: Throughout documentation

### Support
- 💬 **Team Chat**: #raptor-support
- 🐛 **Bug Reports**: GitHub Issues
- 📧 **Email**: test-automation-team@company.com

---

## Slide 22: Next Steps

### 1. Complete Hands-On Exercises
- Exercise 1: Basic test creation
- Exercise 2: Page object implementation
- Exercise 3: Data-driven testing
- Exercise 4: Session reuse

### 2. Take Certification Quiz
- 20 questions covering all topics
- 80% passing score
- Certificate upon completion

### 3. Start Converting Tests
- Begin with simple smoke tests
- Use migration utilities
- Ask for help when needed

---

## Slide 23: Q&A

### Common Questions

**Q: How long does it take to learn?**
A: 1 week for experienced Selenium users

**Q: Can I use existing DDFE definitions?**
A: Yes! Full backward compatibility

**Q: What about existing test data?**
A: DDDB integration works seamlessly

**Q: Performance compared to Selenium?**
A: 30% faster on average

**Q: Browser support?**
A: Chromium, Firefox, WebKit

---

## Slide 24: Thank You!

### Get Started Today
1. Install RAPTOR: `pip install raptor-playwright`
2. Complete hands-on exercises
3. Take certification quiz
4. Start automating!

### Questions?
Contact the Test Automation Team

**Happy Testing! 🚀**

