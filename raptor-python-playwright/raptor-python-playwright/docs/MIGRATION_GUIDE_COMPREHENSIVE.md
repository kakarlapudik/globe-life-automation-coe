# RAPTOR Java to Python Migration Guide - Comprehensive Edition

## Table of Contents

1. [Overview](#overview)
2. [Java to Python Conversion Process](#java-to-python-conversion-process)
3. [Complete Method Mapping Reference](#complete-method-mapping-reference)
4. [Migration Examples](#migration-examples)
5. [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## Overview

This comprehensive guide provides detailed instructions for migrating Java Selenium RAPTOR tests to Python Playwright RAPTOR. It includes step-by-step conversion processes, complete method mappings, real-world examples, and solutions to common migration challenges.

### Why Migrate?

**Performance Benefits:**
- 30-50% faster test execution
- Reduced browser startup time
- Better resource utilization

**Developer Experience:**
- Simpler, more readable code
- Modern async/await patterns
- Better error messages
- Enhanced debugging capabilities

**Framework Advantages:**
- Auto-waiting mechanisms
- Built-in retry logic
- Better browser automation
- Modern web standards support

### Migration Approach

We recommend a **phased migration strategy**:

1. **Pilot Phase**: Migrate 5-10 representative tests
2. **Validation Phase**: Compare results and performance
3. **Scaling Phase**: Migrate remaining tests in batches
4. **Optimization Phase**: Refine and optimize converted tests
5. **Deployment Phase**: Update CI/CD and deploy


## Java to Python Conversion Process

### Step 1: Analyze Java Test Structure

Before converting, analyze your Java test:

```java
// Example Java test structure
public class UserManagementTest extends Common {
    private String usernameField = "css=#username";
    private String saveButton = "css=#save";
    
    @Test
    public void testCreateUser() {
        Web.navigate("https://app.example.com/users");
        Web.type(usernameField, "testuser");
        Web.click(saveButton);
        Web.verifyExists("css=#success-message");
    }
}
```

**Key elements to identify:**
1. Class inheritance (extends Common, BasePage, etc.)
2. Instance variables (locators, configuration)
3. Test methods (@Test annotations)
4. Helper methods
5. Database operations
6. Session management

### Step 2: Set Up Python Test Structure

Create equivalent Python structure:

```python
# Example Python test structure
import pytest
from raptor.pages import BasePage
from raptor.core.element_manager import ElementManager

class TestUserManagement:
    """User management test suite."""
    
    def __init__(self):
        self.username_field = "css=#username"
        self.save_button = "css=#save"
    
    @pytest.mark.asyncio
    async def test_create_user(self, page, element_manager):
        """Test user creation."""
        await page.goto("https://app.example.com/users")
        await element_manager.fill(self.username_field, "testuser")
        await element_manager.click(self.save_button)
        await element_manager.verify_exists("css=#success-message")
```


### Step 3: Convert Class Structure

**Java Pattern:**
```java
public class LoginPage extends Common {
    // Class variables
    private String username = "css=#user";
    private String password = "css=#pass";
    
    // Constructor
    public LoginPage() {
        super();
    }
    
    // Methods
    public void login(String user, String pass) {
        Web.type(username, user);
        Web.type(password, pass);
        Web.click("css=#login");
    }
}
```

**Python Equivalent:**
```python
from raptor.pages import BasePage

class LoginPage(BasePage):
    """Login page object."""
    
    def __init__(self, page, element_manager):
        super().__init__(page, element_manager)
        # Instance variables
        self.username = "css=#user"
        self.password = "css=#pass"
    
    async def login(self, user: str, password: str):
        """Perform login action."""
        await self.element_manager.fill(self.username, user)
        await self.element_manager.fill(self.password, password)
        await self.element_manager.click("css=#login")
```

**Key Differences:**
- Python uses `__init__` instead of constructor name
- All async methods need `async def` and `await`
- Type hints are optional but recommended
- Use `self.element_manager` instead of static `Web` class


### Step 4: Convert Method Signatures

**Java Method Patterns:**
```java
// Void method
public void clickButton() { }

// Return value method
public String getText() { return "text"; }

// Method with parameters
public void fillForm(String name, int age) { }

// Static method
public static void helper() { }
```

**Python Equivalents:**
```python
# Async void method
async def click_button(self) -> None:
    pass

# Async return value method
async def get_text(self) -> str:
    return "text"

# Method with parameters (with type hints)
async def fill_form(self, name: str, age: int) -> None:
    pass

# Static method (use @staticmethod)
@staticmethod
def helper() -> None:
    pass
```

**Naming Conventions:**
- Java: `camelCase` → Python: `snake_case`
- `clickButton()` → `click_button()`
- `getUserName()` → `get_user_name()`
- `isVisible()` → `is_visible()`


### Step 5: Convert Control Structures

**If Statements:**
```java
// Java
if (condition) {
    doSomething();
} else if (otherCondition) {
    doOther();
} else {
    doDefault();
}
```

```python
# Python
if condition:
    await do_something()
elif other_condition:
    await do_other()
else:
    await do_default()
```

**For Loops:**
```java
// Java - traditional for loop
for (int i = 0; i < 10; i++) {
    process(i);
}

// Java - enhanced for loop
for (String item : items) {
    process(item);
}
```

```python
# Python - range-based loop
for i in range(10):
    await process(i)

# Python - iteration
for item in items:
    await process(item)
```

**While Loops:**
```java
// Java
while (condition) {
    doWork();
}
```

```python
# Python
while condition:
    await do_work()
```

**Try-Catch:**
```java
// Java
try {
    riskyOperation();
} catch (Exception e) {
    handleError(e);
} finally {
    cleanup();
}
```

```python
# Python
try:
    await risky_operation()
except Exception as e:
    await handle_error(e)
finally:
    await cleanup()
```


## Complete Method Mapping Reference

### Element Interaction Methods

| Java Method | Python Method | Parameters | Notes |
|------------|---------------|------------|-------|
| `Web.click(locator)` | `await element_manager.click(locator)` | locator: str | Standard click |
| `Web.clickXY(locator, x, y)` | `await element_manager.click_at_position(locator, x, y)` | locator: str, x: int, y: int | Click at coordinates |
| `Web.clickIfExists(locator)` | `await element_manager.click_if_exists(locator)` | locator: str | Conditional click |
| `Web.clickSync(locator)` | `await element_manager.click_with_sync(locator)` | locator: str | Click with wait |
| `Web.doubleClick(locator)` | `await element_manager.double_click(locator)` | locator: str | Double click |
| `Web.rightClick(locator)` | `await element_manager.right_click(locator)` | locator: str | Context menu |
| `Web.type(locator, text)` | `await element_manager.fill(locator, text)` | locator: str, text: str | Fill input |
| `Web.clear(locator)` | `await element_manager.clear(locator)` | locator: str | Clear input |
| `Web.selectOption(locator, value)` | `await element_manager.select_option(locator, value)` | locator: str, value: str | Select dropdown |
| `Web.hover(locator)` | `await element_manager.hover(locator)` | locator: str | Mouse hover |
| `Web.focus(locator)` | `await element_manager.focus(locator)` | locator: str | Set focus |
| `Web.check(locator)` | `await element_manager.check(locator)` | locator: str | Check checkbox |
| `Web.uncheck(locator)` | `await element_manager.uncheck(locator)` | locator: str | Uncheck checkbox |

### Element State Methods

| Java Method | Python Method | Return Type | Notes |
|------------|---------------|-------------|-------|
| `Web.isVisible(locator)` | `await element_manager.is_visible(locator)` | bool | Check visibility |
| `Web.isEnabled(locator)` | `await element_manager.is_enabled(locator)` | bool | Check enabled state |
| `Web.isSelected(locator)` | `await element_manager.is_selected(locator)` | bool | Check selection |
| `Web.exists(locator)` | `await element_manager.exists(locator)` | bool | Check existence |
| `Web.getText(locator)` | `await element_manager.get_text(locator)` | str | Get text content |
| `Web.getValue(locator)` | `await element_manager.get_value(locator)` | str | Get input value |
| `Web.getAttribute(locator, attr)` | `await element_manager.get_attribute(locator, attr)` | str | Get attribute |
| `Web.getLocation(locator)` | `await element_manager.get_location(locator)` | Dict | Get coordinates |


### Verification Methods

| Java Method | Python Method | Behavior | Notes |
|------------|---------------|----------|-------|
| `Web.verifyExists(locator)` | `await verification.verify_exists(locator)` | Throws on failure | Hard assertion |
| `Web.verifyNotExists(locator)` | `await verification.verify_not_exists(locator)` | Throws on failure | Hard assertion |
| `Web.verifyEnabled(locator)` | `await verification.verify_enabled(locator)` | Throws on failure | Hard assertion |
| `Web.verifyDisabled(locator)` | `await verification.verify_disabled(locator)` | Throws on failure | Hard assertion |
| `Web.verifyVisible(locator)` | `await verification.verify_visible(locator)` | Throws on failure | Hard assertion |
| `Web.verifyText(locator, text)` | `await verification.verify_text(locator, text)` | Throws on failure | Hard assertion |
| `Web.softVerifyExists(locator)` | `soft_assert.verify_exists(locator)` | Continues on failure | Soft assertion |
| `Web.softVerifyText(locator, text)` | `soft_assert.verify_text(locator, text)` | Continues on failure | Soft assertion |

### Wait Methods

| Java Method | Python Method | Timeout | Notes |
|------------|---------------|---------|-------|
| `Web.waitForElement(locator)` | `await element_manager.wait_for_element(locator)` | 20s default | Wait for element |
| `Web.waitForElement(locator, timeout)` | `await element_manager.wait_for_element(locator, timeout)` | Custom | Custom timeout |
| `Web.waitForVisible(locator)` | `await element_manager.wait_for_visible(locator)` | 20s default | Wait for visibility |
| `Web.waitForSpinner()` | `await element_manager.wait_for_spinner()` | 30s default | Wait for loading |
| `Web.waitForDisabledPane()` | `await element_manager.wait_for_disabled_pane()` | 30s default | Wait for modal |
| `Common.waitForPageLoad()` | `await page.wait_for_load_state("load")` | 30s default | Wait for page |
| `Common.waitForNetworkIdle()` | `await page.wait_for_load_state("networkidle")` | 30s default | Wait for network |

### Navigation Methods

| Java Method | Python Method | Notes |
|------------|---------------|-------|
| `Web.navigate(url)` | `await page.goto(url)` | Navigate to URL |
| `Web.refresh()` | `await page.reload()` | Refresh page |
| `Web.goBack()` | `await page.go_back()` | Browser back |
| `Web.goForward()` | `await page.go_forward()` | Browser forward |
| `Common.getTitle()` | `await page.title()` | Get page title |
| `Common.getUrl()` | `page.url` | Get current URL |


### Table Operations

| Java Method | Python Method | Notes |
|------------|---------------|-------|
| `Table.findRowByKey(table, col, key)` | `await table_manager.find_row_by_key(table, col, key)` | Find row by key |
| `Table.getCellValue(table, row, col)` | `await table_manager.get_cell_value(table, row, col)` | Get cell value |
| `Table.setCellValue(table, row, col, val)` | `await table_manager.set_cell_value(table, row, col, val)` | Set cell value |
| `Table.clickCell(table, row, col)` | `await table_manager.click_cell(table, row, col)` | Click cell |
| `Table.getRowCount(table)` | `await table_manager.get_row_count(table)` | Count rows |
| `Table.searchTable(table, text)` | `await table_manager.search_table(table, text)` | Search table |

### Database Operations

| Java Method | Python Method | Notes |
|------------|---------------|-------|
| `Dms.databaseImport(table, id, iter, inst)` | `await db_manager.import_data(table, id, iter, inst)` | Load test data |
| `Dms.databaseExport(table, pk, field, val)` | `await db_manager.export_data(table, pk, field, val)` | Save results |
| `Dms.databaseQuery(table, field, pk)` | `await db_manager.query_field(table, field, pk)` | Query field |
| `Dms.databaseExec(sql)` | `await db_manager.execute_update(sql)` | Execute SQL |
| `Dms.executeQuery(sql)` | `await db_manager.execute_query(sql)` | Execute SELECT |

### Session Management

| Java Method | Python Method | Notes |
|------------|---------------|-------|
| `Common.createDriverFromSession(id)` | `await session_manager.restore_session(id)` | Restore session |
| `Common.saveSession(id)` | `await session_manager.save_session(page, id)` | Save session |
| `Common.listSessions()` | `session_manager.list_sessions()` | List sessions |
| `Common.deleteSession(id)` | `session_manager.delete_session(id)` | Delete session |

### Screenshot and Reporting

| Java Method | Python Method | Notes |
|------------|---------------|-------|
| `Common.takeScreenshot(name)` | `await page.screenshot(path=name)` | Take screenshot |
| `Common.takeFullScreenshot(name)` | `await page.screenshot(path=name, full_page=True)` | Full page screenshot |
| `Reporter.log(message)` | `logger.info(message)` | Log message |
| `Reporter.logError(message)` | `logger.error(message)` | Log error |


## Migration Examples

### Example 1: Simple Login Test

**Java (Before):**
```java
package com.example.tests;

import org.testng.annotations.Test;
import com.raptor.Common;
import com.raptor.Web;

public class LoginTest extends Common {
    
    @Test
    public void testValidLogin() {
        Web.navigate("https://app.example.com/login");
        Web.type("css=#username", "admin");
        Web.type("css=#password", "password123");
        Web.click("css=#login-button");
        Web.verifyExists("css=#dashboard");
        Web.verifyText("css=#welcome-message", "Welcome, Admin");
    }
    
    @Test
    public void testInvalidLogin() {
        Web.navigate("https://app.example.com/login");
        Web.type("css=#username", "invalid");
        Web.type("css=#password", "wrong");
        Web.click("css=#login-button");
        Web.verifyExists("css=#error-message");
        Web.verifyText("css=#error-message", "Invalid credentials");
    }
}
```

**Python (After):**
```python
"""Login test suite."""
import pytest

@pytest.mark.asyncio
class TestLogin:
    """Login test cases."""
    
    async def test_valid_login(self, page, element_manager, verification):
        """Test successful login with valid credentials."""
        await page.goto("https://app.example.com/login")
        await element_manager.fill("css=#username", "admin")
        await element_manager.fill("css=#password", "password123")
        await element_manager.click("css=#login-button")
        await verification.verify_exists("css=#dashboard")
        await verification.verify_text("css=#welcome-message", "Welcome, Admin")
    
    async def test_invalid_login(self, page, element_manager, verification):
        """Test login failure with invalid credentials."""
        await page.goto("https://app.example.com/login")
        await element_manager.fill("css=#username", "invalid")
        await element_manager.fill("css=#password", "wrong")
        await element_manager.click("css=#login-button")
        await verification.verify_exists("css=#error-message")
        await verification.verify_text("css=#error-message", "Invalid credentials")
```

**Key Changes:**
1. Import pytest instead of TestNG
2. Use `@pytest.mark.asyncio` decorator
3. Add `async` to method definitions
4. Add `await` to all async calls
5. Use fixtures (`page`, `element_manager`, `verification`)
6. Add docstrings for documentation


### Example 2: Page Object Pattern

**Java (Before):**
```java
package com.example.pages;

import com.raptor.Common;
import com.raptor.Web;

public class UserManagementPage extends Common {
    
    // Locators
    private String addUserButton = "css=#add-user";
    private String firstNameField = "css=#first-name";
    private String lastNameField = "css=#last-name";
    private String emailField = "css=#email";
    private String saveButton = "css=#save";
    private String successMessage = "css=#success";
    
    public void navigateToUserManagement() {
        Web.navigate("https://app.example.com/users");
        Web.waitForElement(addUserButton);
    }
    
    public void clickAddUser() {
        Web.click(addUserButton);
        Web.waitForElement(firstNameField);
    }
    
    public void fillUserForm(String firstName, String lastName, String email) {
        Web.type(firstNameField, firstName);
        Web.type(lastNameField, lastName);
        Web.type(emailField, email);
    }
    
    public void saveUser() {
        Web.click(saveButton);
        Web.waitForElement(successMessage);
    }
    
    public String getSuccessMessage() {
        return Web.getText(successMessage);
    }
}
```

**Python (After):**
```python
"""User management page object."""
from raptor.pages import BasePage

class UserManagementPage(BasePage):
    """Page object for user management functionality."""
    
    def __init__(self, page, element_manager):
        """Initialize user management page."""
        super().__init__(page, element_manager)
        
        # Locators
        self.add_user_button = "css=#add-user"
        self.first_name_field = "css=#first-name"
        self.last_name_field = "css=#last-name"
        self.email_field = "css=#email"
        self.save_button = "css=#save"
        self.success_message = "css=#success"
    
    async def navigate_to_user_management(self):
        """Navigate to user management page."""
        await self.page.goto("https://app.example.com/users")
        await self.element_manager.wait_for_element(self.add_user_button)
    
    async def click_add_user(self):
        """Click add user button."""
        await self.element_manager.click(self.add_user_button)
        await self.element_manager.wait_for_element(self.first_name_field)
    
    async def fill_user_form(self, first_name: str, last_name: str, email: str):
        """
        Fill user form with provided data.
        
        Args:
            first_name: User's first name
            last_name: User's last name
            email: User's email address
        """
        await self.element_manager.fill(self.first_name_field, first_name)
        await self.element_manager.fill(self.last_name_field, last_name)
        await self.element_manager.fill(self.email_field, email)
    
    async def save_user(self):
        """Save user and wait for confirmation."""
        await self.element_manager.click(self.save_button)
        await self.element_manager.wait_for_element(self.success_message)
    
    async def get_success_message(self) -> str:
        """Get success message text."""
        return await self.element_manager.get_text(self.success_message)
```


### Example 3: Data-Driven Test

**Java (Before):**
```java
package com.example.tests;

import org.testng.annotations.Test;
import com.raptor.Common;
import com.raptor.Web;
import com.raptor.Dms;
import java.util.HashMap;

public class DataDrivenTest extends Common {
    
    @Test
    public void testUserCreationWithData() {
        // Load test data from database
        HashMap<String, String> data = Dms.databaseImport(
            "UserTestData", 1, 1, 1
        );
        
        String firstName = data.get("first_name");
        String lastName = data.get("last_name");
        String email = data.get("email");
        String expectedMessage = data.get("expected_message");
        
        // Execute test
        Web.navigate("https://app.example.com/users");
        Web.click("css=#add-user");
        Web.type("css=#first-name", firstName);
        Web.type("css=#last-name", lastName);
        Web.type("css=#email", email);
        Web.click("css=#save");
        
        // Verify result
        Web.verifyText("css=#success", expectedMessage);
        
        // Export result to database
        int pkId = Integer.parseInt(data.get("pk_id"));
        Dms.databaseExport("UserTestData", pkId, "test_status", "PASS");
    }
}
```

**Python (After):**
```python
"""Data-driven test example."""
import pytest

@pytest.mark.asyncio
class TestDataDriven:
    """Data-driven test cases."""
    
    async def test_user_creation_with_data(
        self,
        page,
        element_manager,
        verification,
        database_manager
    ):
        """Test user creation using database test data."""
        # Load test data from database
        data = await database_manager.import_data(
            table="UserTestData",
            test_id=1,
            iteration=1,
            instance=1
        )
        
        first_name = data["first_name"]
        last_name = data["last_name"]
        email = data["email"]
        expected_message = data["expected_message"]
        
        # Execute test
        await page.goto("https://app.example.com/users")
        await element_manager.click("css=#add-user")
        await element_manager.fill("css=#first-name", first_name)
        await element_manager.fill("css=#last-name", last_name)
        await element_manager.fill("css=#email", email)
        await element_manager.click("css=#save")
        
        # Verify result
        await verification.verify_text("css=#success", expected_message)
        
        # Export result to database
        pk_id = int(data["pk_id"])
        await database_manager.export_data(
            table="UserTestData",
            pk_id=pk_id,
            field="test_status",
            value="PASS"
        )
```


### Example 4: Table Operations

**Java (Before):**
```java
package com.example.tests;

import org.testng.annotations.Test;
import com.raptor.Common;
import com.raptor.Web;
import com.raptor.Table;

public class TableTest extends Common {
    
    @Test
    public void testTableOperations() {
        Web.navigate("https://app.example.com/users");
        
        // Find row by key
        int row = Table.findRowByKey("css=#users-table", 0, "John Doe");
        
        // Get cell values
        String email = Table.getCellValue("css=#users-table", row, 2);
        String role = Table.getCellValue("css=#users-table", row, 3);
        
        // Verify values
        Web.verifyText("css=#users-table", email);
        
        // Click edit button in row
        Table.clickCell("css=#users-table", row, 4);
        
        // Update value
        Web.type("css=#email-field", "newemail@example.com");
        Web.click("css=#save");
        
        // Verify update
        String updatedEmail = Table.getCellValue("css=#users-table", row, 2);
        Web.verifyText("css=#users-table", "newemail@example.com");
    }
}
```

**Python (After):**
```python
"""Table operations test example."""
import pytest

@pytest.mark.asyncio
class TestTableOperations:
    """Table interaction test cases."""
    
    async def test_table_operations(
        self,
        page,
        element_manager,
        table_manager,
        verification
    ):
        """Test table search, read, and update operations."""
        await page.goto("https://app.example.com/users")
        
        # Find row by key
        row = await table_manager.find_row_by_key(
            table_locator="css=#users-table",
            key_column=0,
            key_value="John Doe"
        )
        
        # Get cell values
        email = await table_manager.get_cell_value(
            "css=#users-table", row, 2
        )
        role = await table_manager.get_cell_value(
            "css=#users-table", row, 3
        )
        
        # Verify values
        assert email is not None
        assert role is not None
        
        # Click edit button in row
        await table_manager.click_cell("css=#users-table", row, 4)
        
        # Update value
        await element_manager.fill("css=#email-field", "newemail@example.com")
        await element_manager.click("css=#save")
        
        # Verify update
        updated_email = await table_manager.get_cell_value(
            "css=#users-table", row, 2
        )
        assert updated_email == "newemail@example.com"
```


## Common Pitfalls and Solutions

### Pitfall 1: Forgetting `await` Keyword

**Problem:**
```python
# ❌ WRONG - Missing await
element_manager.click("css=#button")
result = element_manager.get_text("css=#label")
```

**Solution:**
```python
# ✅ CORRECT - Using await
await element_manager.click("css=#button")
result = await element_manager.get_text("css=#label")
```

**Why it matters:** Without `await`, the coroutine is not executed, and you'll get a coroutine object instead of the expected result.

### Pitfall 2: Missing `@pytest.mark.asyncio` Decorator

**Problem:**
```python
# ❌ WRONG - Missing decorator
async def test_login(page, element_manager):
    await page.goto("https://example.com")
    await element_manager.click("css=#login")
```

**Solution:**
```python
# ✅ CORRECT - With decorator
@pytest.mark.asyncio
async def test_login(page, element_manager):
    await page.goto("https://example.com")
    await element_manager.click("css=#login")
```

**Why it matters:** pytest needs this decorator to know the test is async and should be run with asyncio.

### Pitfall 3: Incorrect Locator Syntax

**Problem:**
```python
# ❌ WRONG - Missing locator strategy prefix
await element_manager.click("#button")
await element_manager.click("button")
```

**Solution:**
```python
# ✅ CORRECT - With proper prefix
await element_manager.click("css=#button")
await element_manager.click("text=Submit")
await element_manager.click("xpath=//button[@id='submit']")
```

**Why it matters:** Playwright requires explicit locator strategies for clarity and consistency.

### Pitfall 4: Not Handling Async Context Managers

**Problem:**
```python
# ❌ WRONG - Not using context manager
browser = await browser_manager.launch_browser()
page = await browser.new_page()
# ... test code ...
# Forgot to close browser
```

**Solution:**
```python
# ✅ CORRECT - Using fixtures (recommended)
@pytest.mark.asyncio
async def test_something(page, element_manager):
    # Fixtures handle setup and teardown
    await page.goto("https://example.com")
    # ... test code ...
    # Cleanup handled automatically

# OR using context manager manually
async with browser_manager.launch_browser() as browser:
    page = await browser.new_page()
    # ... test code ...
    # Automatically closed
```


### Pitfall 5: Synchronous Database Calls

**Problem:**
```python
# ❌ WRONG - Treating async method as sync
data = database_manager.import_data("TestData", 1, 1, 1)
```

**Solution:**
```python
# ✅ CORRECT - Using await
data = await database_manager.import_data("TestData", 1, 1, 1)
```

### Pitfall 6: Incorrect Exception Handling

**Problem:**
```java
// Java
try {
    Web.click("css=#button");
} catch (ElementNotFoundException e) {
    handleError(e);
}
```

```python
# ❌ WRONG - Direct translation
try:
    await element_manager.click("css=#button")
except ElementNotFoundException as e:
    handle_error(e)
```

**Solution:**
```python
# ✅ CORRECT - Import exception first
from raptor.core.exceptions import ElementNotFoundException

try:
    await element_manager.click("css=#button")
except ElementNotFoundException as e:
    await handle_error(e)  # Don't forget await if handle_error is async
```

### Pitfall 7: Static Method Calls

**Problem:**
```java
// Java - Static method call
Web.click("css=#button");
```

```python
# ❌ WRONG - Trying to use as static
Web.click("css=#button")
```

**Solution:**
```python
# ✅ CORRECT - Use instance through fixture
await element_manager.click("css=#button")
```

**Why it matters:** Python RAPTOR uses instance methods with dependency injection through fixtures, not static methods.

### Pitfall 8: Variable Naming Conventions

**Problem:**
```python
# ❌ WRONG - Using Java naming conventions
firstName = "John"
lastName = "Doe"
isVisible = True

def getUserName():
    pass
```

**Solution:**
```python
# ✅ CORRECT - Using Python naming conventions
first_name = "John"
last_name = "Doe"
is_visible = True

def get_user_name():
    pass
```


### Pitfall 9: Type Conversion Issues

**Problem:**
```java
// Java - Automatic type conversion
int value = Integer.parseInt(data.get("count"));
String result = String.valueOf(value + 1);
```

```python
# ❌ WRONG - Assuming automatic conversion
value = data["count"]  # Might be string
result = value + 1  # TypeError if value is string
```

**Solution:**
```python
# ✅ CORRECT - Explicit type conversion
value = int(data["count"])
result = str(value + 1)
```

### Pitfall 10: List/Array Indexing

**Problem:**
```java
// Java - Arrays are 0-indexed
String[] items = {"a", "b", "c"};
String first = items[0];
```

```python
# ✅ CORRECT - Python lists are also 0-indexed (same as Java)
items = ["a", "b", "c"]
first = items[0]

# But be careful with negative indexing (Python feature)
last = items[-1]  # Gets "c" - not available in Java
```

### Pitfall 11: String Comparison

**Problem:**
```java
// Java - Using .equals()
if (text.equals("expected")) {
    // do something
}
```

```python
# ❌ WRONG - Using Java syntax
if text.equals("expected"):
    pass

# ✅ CORRECT - Using Python syntax
if text == "expected":
    pass
```

### Pitfall 12: Null vs None

**Problem:**
```java
// Java
if (value == null) {
    return null;
}
```

```python
# ❌ WRONG - Using Java syntax
if value == null:
    return null

# ✅ CORRECT - Using Python syntax
if value is None:
    return None
```


## Best Practices

### 1. Use Type Hints

Type hints improve code readability and enable better IDE support:

```python
async def fill_user_form(
    self,
    first_name: str,
    last_name: str,
    age: int,
    active: bool = True
) -> None:
    """Fill user form with provided data."""
    await self.element_manager.fill(self.first_name_field, first_name)
    await self.element_manager.fill(self.last_name_field, last_name)
    await self.element_manager.fill(self.age_field, str(age))
```

### 2. Write Comprehensive Docstrings

Document your code with clear docstrings:

```python
async def search_user(self, search_term: str) -> List[Dict[str, str]]:
    """
    Search for users matching the search term.
    
    Args:
        search_term: The term to search for (name, email, etc.)
    
    Returns:
        List of dictionaries containing user information
    
    Raises:
        ElementNotFoundException: If search field is not found
        TimeoutException: If search takes too long
    
    Example:
        >>> users = await page.search_user("john")
        >>> print(users[0]["name"])
        'John Doe'
    """
    await self.element_manager.fill(self.search_field, search_term)
    await self.element_manager.click(self.search_button)
    return await self._parse_search_results()
```

### 3. Use Fixtures for Setup and Teardown

Leverage pytest fixtures for clean test setup:

```python
@pytest.fixture
async def user_management_page(page, element_manager):
    """Fixture providing initialized user management page."""
    user_page = UserManagementPage(page, element_manager)
    await user_page.navigate()
    yield user_page
    # Cleanup if needed
    await user_page.cleanup()

@pytest.mark.asyncio
async def test_create_user(user_management_page):
    """Test user creation."""
    await user_management_page.click_add_user()
    await user_management_page.fill_user_form("John", "Doe", "john@example.com")
    await user_management_page.save_user()
```

### 4. Organize Locators Effectively

Keep locators organized and maintainable:

```python
class UserManagementPage(BasePage):
    """User management page object."""
    
    # Group related locators
    class Locators:
        """Page locators."""
        # Form fields
        FIRST_NAME = "css=#first-name"
        LAST_NAME = "css=#last-name"
        EMAIL = "css=#email"
        
        # Buttons
        ADD_USER = "css=#add-user"
        SAVE = "css=#save"
        CANCEL = "css=#cancel"
        
        # Messages
        SUCCESS = "css=#success-message"
        ERROR = "css=#error-message"
    
    def __init__(self, page, element_manager):
        super().__init__(page, element_manager)
        self.loc = self.Locators()
```


### 5. Handle Errors Gracefully

Implement proper error handling:

```python
from raptor.core.exceptions import (
    ElementNotFoundException,
    TimeoutException,
    ElementNotInteractableException
)

async def safe_click(self, locator: str, max_retries: int = 3) -> bool:
    """
    Safely click element with retry logic.
    
    Args:
        locator: Element locator
        max_retries: Maximum number of retry attempts
    
    Returns:
        True if click succeeded, False otherwise
    """
    for attempt in range(max_retries):
        try:
            await self.element_manager.click(locator)
            return True
        except ElementNotFoundException:
            if attempt == max_retries - 1:
                self.logger.error(f"Element not found after {max_retries} attempts: {locator}")
                return False
            await asyncio.sleep(1)
        except ElementNotInteractableException:
            self.logger.warning(f"Element not interactable, retrying: {locator}")
            await asyncio.sleep(1)
    return False
```

### 6. Use Async Context Managers

Properly manage resources:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def temporary_user(page, element_manager):
    """Context manager for creating and cleaning up test user."""
    # Setup
    user_id = await create_test_user(page, element_manager)
    
    try:
        yield user_id
    finally:
        # Cleanup
        await delete_test_user(page, element_manager, user_id)

# Usage
async def test_user_operations(page, element_manager):
    async with temporary_user(page, element_manager) as user_id:
        # Test operations with user
        await perform_user_operations(user_id)
        # User automatically deleted after block
```

### 7. Implement Page Object Inheritance

Create reusable base page objects:

```python
class BasePage:
    """Base page with common functionality."""
    
    async def wait_for_page_load(self):
        """Wait for page to fully load."""
        await self.page.wait_for_load_state("networkidle")
    
    async def take_screenshot(self, name: str):
        """Take screenshot with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        await self.page.screenshot(path=f"screenshots/{filename}")

class UserManagementPage(BasePage):
    """User management page inheriting common functionality."""
    
    async def navigate(self):
        """Navigate to user management page."""
        await self.page.goto("https://app.example.com/users")
        await self.wait_for_page_load()  # Inherited method
```


## Troubleshooting

### Issue 1: "RuntimeError: Event loop is closed"

**Symptom:**
```
RuntimeError: Event loop is closed
```

**Cause:** Mixing sync and async code incorrectly.

**Solution:**
```python
# Ensure all test methods are properly marked as async
@pytest.mark.asyncio
async def test_example(page):
    await page.goto("https://example.com")
```

### Issue 2: "TypeError: object Coroutine can't be used in 'await' expression"

**Symptom:**
```
TypeError: object Coroutine can't be used in 'await' expression
```

**Cause:** Trying to await a non-async function.

**Solution:**
```python
# Check if the function is actually async
# If not, remove await or make the function async
result = await async_function()  # Correct
result = sync_function()  # Correct
```

### Issue 3: Locator Not Found

**Symptom:**
```
ElementNotFoundException: Element not found: css=#button
```

**Solutions:**
1. Verify locator syntax:
```python
# Check for typos and correct prefix
await element_manager.click("css=#button")  # Correct
```

2. Add explicit wait:
```python
await element_manager.wait_for_element("css=#button", timeout=30000)
await element_manager.click("css=#button")
```

3. Use fallback locators:
```python
await element_manager.locate_element(
    "css=#button",
    fallback_locators=["xpath=//button[@id='button']", "text=Submit"]
)
```

### Issue 4: Database Connection Failures

**Symptom:**
```
DatabaseException: Unable to connect to database
```

**Solutions:**
1. Check connection string:
```python
# Verify connection string format
connection_string = "DRIVER={SQL Server};SERVER=localhost;DATABASE=TestDB;UID=user;PWD=pass"
```

2. Verify database is accessible:
```python
# Test connection separately
db_manager = DatabaseManager(connection_string)
await db_manager.connect()
await db_manager.disconnect()
```

3. Check firewall and network settings

### Issue 5: Session Restore Failures

**Symptom:**
```
SessionException: Unable to restore session
```

**Solutions:**
1. Verify session exists:
```python
sessions = session_manager.list_sessions()
print(f"Available sessions: {sessions}")
```

2. Check session expiration:
```python
# Sessions may expire after certain time
# Create new session if needed
if not session_manager.session_exists(session_id):
    await create_new_session()
```


### Issue 6: Import Errors

**Symptom:**
```
ImportError: cannot import name 'ElementManager' from 'raptor.core'
```

**Solutions:**
1. Verify installation:
```bash
pip install -e .
pip list | grep raptor
```

2. Check import paths:
```python
# Correct imports
from raptor.core.element_manager import ElementManager
from raptor.pages.base_page import BasePage
from raptor.database.database_manager import DatabaseManager
```

3. Verify PYTHONPATH:
```bash
echo $PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/raptor"
```

### Issue 7: Fixture Not Found

**Symptom:**
```
fixture 'element_manager' not found
```

**Solution:**
Ensure conftest.py is in the correct location:
```
tests/
├── conftest.py  # Must be here
├── test_login.py
└── test_users.py
```

And fixtures are properly defined:
```python
# conftest.py
import pytest
from raptor.core.element_manager import ElementManager

@pytest.fixture
async def element_manager(page):
    """Provide element manager instance."""
    return ElementManager(page)
```

### Issue 8: Async Fixture Errors

**Symptom:**
```
ScopeMismatch: You tried to access the function scoped fixture with a session scoped request object
```

**Solution:**
Match fixture scopes correctly:
```python
@pytest.fixture(scope="function")
async def page(browser):
    """Function-scoped page fixture."""
    page = await browser.new_page()
    yield page
    await page.close()

@pytest.fixture(scope="session")
async def browser():
    """Session-scoped browser fixture."""
    browser = await launch_browser()
    yield browser
    await browser.close()
```

## Migration Checklist

Use this checklist to track your migration progress:

### Pre-Migration
- [ ] Review existing Java tests
- [ ] Identify test dependencies
- [ ] Set up Python environment
- [ ] Install RAPTOR Python framework
- [ ] Configure database connections
- [ ] Set up CI/CD pipeline

### During Migration
- [ ] Convert utility classes
- [ ] Convert page objects
- [ ] Convert test cases
- [ ] Update locators if needed
- [ ] Add type hints
- [ ] Write docstrings
- [ ] Handle async/await properly
- [ ] Update exception handling

### Post-Migration
- [ ] Run all tests
- [ ] Compare results with Java tests
- [ ] Fix any failures
- [ ] Optimize performance
- [ ] Update documentation
- [ ] Train team members
- [ ] Deploy to CI/CD
- [ ] Monitor test stability

## Additional Resources

- **RAPTOR Python Documentation**: See `docs/` directory
- **Playwright Documentation**: https://playwright.dev/python/
- **pytest Documentation**: https://docs.pytest.org/
- **Python Async/Await Guide**: https://docs.python.org/3/library/asyncio.html
- **Migration Tool**: Use `raptor migrate` command for automated conversion

## Getting Help

If you encounter issues during migration:

1. Check this guide's troubleshooting section
2. Review the API documentation
3. Check existing examples in `examples/` directory
4. Contact the RAPTOR support team
5. Submit issues on GitHub

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Maintained By:** RAPTOR Framework Team
