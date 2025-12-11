# RAPTOR Python Playwright Framework
## Hands-On Exercises

---

## Prerequisites

Before starting these exercises, ensure you have:
- ✅ RAPTOR framework installed (`pip install raptor-playwright`)
- ✅ Python 3.8+ installed
- ✅ Playwright browsers installed (`playwright install`)
- ✅ Access to test environment
- ✅ Completed training presentation

---

## Exercise 1: Your First RAPTOR Test (30 minutes)

### Objective
Create a basic test that navigates to a website, interacts with elements, and performs assertions.

### Setup
1. Create a new directory: `raptor-exercises`
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install RAPTOR: `pip install raptor-playwright`

### Task 1.1: Basic Navigation Test
Create a file `test_exercise1.py`:

```python
import pytest
from raptor.core import BrowserManager, ElementManager

@pytest.mark.asyncio
async def test_basic_navigation():
    """
    Test basic navigation to a website
    
    Steps:
    1. Launch browser
    2. Navigate to https://example.com
    3. Verify page title
    4. Close browser
    """
    # TODO: Implement the test
    # Hint: Use BrowserManager to launch browser
    # Hint: Use page.goto() to navigate
    # Hint: Use page.title() to get title
    pass
```

### Solution 1.1
<details>
<summary>Click to reveal solution</summary>

```python
import pytest
from raptor.core import BrowserManager, ElementManager

@pytest.mark.asyncio
async def test_basic_navigation():
    # Setup
    browser_manager = BrowserManager()
    browser = await browser_manager.launch_browser("chromium", headless=False)
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
    
    # Navigate
    await page.goto("https://example.com")
    
    # Verify
    title = await page.title()
    assert "Example Domain" in title
    
    # Cleanup
    await browser_manager.close_browser()
```
</details>

### Task 1.2: Element Interaction
Extend the test to interact with elements:

```python
@pytest.mark.asyncio
async def test_element_interaction():
    """
    Test element interaction
    
    Steps:
    1. Navigate to https://the-internet.herokuapp.com/login
    2. Fill in username: tomsmith
    3. Fill in password: SuperSecretPassword!
    4. Click login button
    5. Verify success message appears
    """
    # TODO: Implement the test
    # Hint: Use ElementManager for interactions
    # Hint: Use element_manager.fill() for text input
    # Hint: Use element_manager.click() for buttons
    pass
```

### Solution 1.2
<details>
<summary>Click to reveal solution</summary>

```python
@pytest.mark.asyncio
async def test_element_interaction():
    # Setup
    browser_manager = BrowserManager()
    browser = await browser_manager.launch_browser("chromium", headless=False)
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
    element_manager = ElementManager(page)
    
    # Navigate
    await page.goto("https://the-internet.herokuapp.com/login")
    
    # Interact
    await element_manager.fill("css=#username", "tomsmith")
    await element_manager.fill("css=#password", "SuperSecretPassword!")
    await element_manager.click("css=button[type='submit']")
    
    # Verify
    success_message = await element_manager.is_visible("css=.flash.success")
    assert success_message, "Success message should be visible"
    
    # Cleanup
    await browser_manager.close_browser()
```
</details>

### Task 1.3: Using Fixtures
Refactor the test to use pytest fixtures:

```python
# Create conftest.py in the same directory
import pytest
from raptor.core import BrowserManager, ElementManager

@pytest.fixture
async def browser_manager():
    # TODO: Create and return BrowserManager
    pass

@pytest.fixture
async def page(browser_manager):
    # TODO: Launch browser, create context and page
    # TODO: Yield page
    # TODO: Cleanup after test
    pass

@pytest.fixture
async def element_manager(page):
    # TODO: Create and return ElementManager
    pass

# Now refactor test_element_interaction to use fixtures
@pytest.mark.asyncio
async def test_with_fixtures(page, element_manager):
    # TODO: Implement using fixtures
    pass
```

### Solution 1.3
<details>
<summary>Click to reveal solution</summary>

```python
# conftest.py
import pytest
from raptor.core import BrowserManager, ElementManager

@pytest.fixture
async def browser_manager():
    manager = BrowserManager()
    yield manager
    await manager.close_browser()

@pytest.fixture
async def page(browser_manager):
    browser = await browser_manager.launch_browser("chromium", headless=False)
    context = await browser_manager.create_context()
    page = await browser_manager.create_page(context)
    yield page

@pytest.fixture
async def element_manager(page):
    return ElementManager(page)

# test_exercise1.py
@pytest.mark.asyncio
async def test_with_fixtures(page, element_manager):
    await page.goto("https://the-internet.herokuapp.com/login")
    
    await element_manager.fill("css=#username", "tomsmith")
    await element_manager.fill("css=#password", "SuperSecretPassword!")
    await element_manager.click("css=button[type='submit']")
    
    success_message = await element_manager.is_visible("css=.flash.success")
    assert success_message
```
</details>

### Verification
Run your tests:
```bash
pytest test_exercise1.py -v
```

Expected output: All tests should pass ✅

---

## Exercise 2: Page Object Pattern (45 minutes)

### Objective
Implement the Page Object Model pattern to create maintainable and reusable test code.

### Task 2.1: Create Login Page Object
Create `pages/login_page.py`:

```python
from raptor.pages import BasePage

class LoginPage(BasePage):
    """
    Page Object for Login Page
    
    TODO: Define locators as class attributes
    TODO: Implement login() method
    TODO: Implement verify_login_success() method
    TODO: Implement verify_login_failure() method
    """
    
    def __init__(self, page, element_manager):
        super().__init__(page, element_manager)
        # TODO: Define locators
        self.username_field = None
        self.password_field = None
        self.login_button = None
        self.success_message = None
        self.error_message = None
    
    async def login(self, username, password):
        """
        Perform login action
        
        Args:
            username: Username to enter
            password: Password to enter
        """
        # TODO: Implement login logic
        pass
    
    async def verify_login_success(self):
        """Verify successful login"""
        # TODO: Check for success message
        pass
    
    async def verify_login_failure(self):
        """Verify failed login"""
        # TODO: Check for error message
        pass
```

### Solution 2.1
<details>
<summary>Click to reveal solution</summary>

```python
from raptor.pages import BasePage

class LoginPage(BasePage):
    def __init__(self, page, element_manager):
        super().__init__(page, element_manager)
        self.username_field = "css=#username"
        self.password_field = "css=#password"
        self.login_button = "css=button[type='submit']"
        self.success_message = "css=.flash.success"
        self.error_message = "css=.flash.error"
    
    async def navigate(self):
        """Navigate to login page"""
        await self.page.goto("https://the-internet.herokuapp.com/login")
    
    async def login(self, username, password):
        await self.element_manager.fill(self.username_field, username)
        await self.element_manager.fill(self.password_field, password)
        await self.element_manager.click(self.login_button)
    
    async def verify_login_success(self):
        is_visible = await self.element_manager.is_visible(self.success_message)
        assert is_visible, "Success message should be visible"
    
    async def verify_login_failure(self):
        is_visible = await self.element_manager.is_visible(self.error_message)
        assert is_visible, "Error message should be visible"
```
</details>

### Task 2.2: Create Secure Area Page Object
Create `pages/secure_area_page.py`:

```python
from raptor.pages import BasePage

class SecureAreaPage(BasePage):
    """
    Page Object for Secure Area (after login)
    
    TODO: Define locators
    TODO: Implement verify_on_secure_page() method
    TODO: Implement logout() method
    """
    
    def __init__(self, page, element_manager):
        super().__init__(page, element_manager)
        # TODO: Define locators
        pass
    
    async def verify_on_secure_page(self):
        """Verify user is on secure page"""
        # TODO: Implement verification
        pass
    
    async def logout(self):
        """Click logout button"""
        # TODO: Implement logout
        pass
```

### Solution 2.2
<details>
<summary>Click to reveal solution</summary>

```python
from raptor.pages import BasePage

class SecureAreaPage(BasePage):
    def __init__(self, page, element_manager):
        super().__init__(page, element_manager)
        self.logout_button = "css=.button.secondary"
        self.secure_area_header = "css=h2"
    
    async def verify_on_secure_page(self):
        is_visible = await self.element_manager.is_visible(self.secure_area_header)
        assert is_visible, "Secure area header should be visible"
        
        header_text = await self.element_manager.get_text(self.secure_area_header)
        assert "Secure Area" in header_text
    
    async def logout(self):
        await self.element_manager.click(self.logout_button)
```
</details>

### Task 2.3: Write Tests Using Page Objects
Create `test_exercise2.py`:

```python
import pytest
from pages.login_page import LoginPage
from pages.secure_area_page import SecureAreaPage

@pytest.mark.asyncio
async def test_successful_login(page, element_manager):
    """
    Test successful login flow using page objects
    
    Steps:
    1. Navigate to login page
    2. Login with valid credentials
    3. Verify login success
    4. Verify on secure page
    """
    # TODO: Implement test using page objects
    pass

@pytest.mark.asyncio
async def test_failed_login(page, element_manager):
    """
    Test failed login with invalid credentials
    
    Steps:
    1. Navigate to login page
    2. Login with invalid credentials
    3. Verify login failure
    """
    # TODO: Implement test
    pass

@pytest.mark.asyncio
async def test_logout(page, element_manager):
    """
    Test logout functionality
    
    Steps:
    1. Login successfully
    2. Logout
    3. Verify back on login page
    """
    # TODO: Implement test
    pass
```

### Solution 2.3
<details>
<summary>Click to reveal solution</summary>

```python
import pytest
from pages.login_page import LoginPage
from pages.secure_area_page import SecureAreaPage

@pytest.mark.asyncio
async def test_successful_login(page, element_manager):
    login_page = LoginPage(page, element_manager)
    secure_page = SecureAreaPage(page, element_manager)
    
    await login_page.navigate()
    await login_page.login("tomsmith", "SuperSecretPassword!")
    await login_page.verify_login_success()
    await secure_page.verify_on_secure_page()

@pytest.mark.asyncio
async def test_failed_login(page, element_manager):
    login_page = LoginPage(page, element_manager)
    
    await login_page.navigate()
    await login_page.login("invalid", "invalid")
    await login_page.verify_login_failure()

@pytest.mark.asyncio
async def test_logout(page, element_manager):
    login_page = LoginPage(page, element_manager)
    secure_page = SecureAreaPage(page, element_manager)
    
    await login_page.navigate()
    await login_page.login("tomsmith", "SuperSecretPassword!")
    await secure_page.verify_on_secure_page()
    await secure_page.logout()
    
    # Verify back on login page
    is_visible = await element_manager.is_visible("css=#username")
    assert is_visible
```
</details>

### Verification
```bash
pytest test_exercise2.py -v
```

---

## Exercise 3: Data-Driven Testing (45 minutes)

### Objective
Learn to create data-driven tests using pytest parametrization and DDDB integration.

### Task 3.1: Parametrized Tests
Create `test_exercise3.py`:

```python
import pytest
from pages.login_page import LoginPage

# TODO: Use @pytest.mark.parametrize to test multiple login scenarios
# Test data: (username, password, should_succeed)
test_data = [
    ("tomsmith", "SuperSecretPassword!", True),
    ("invalid", "invalid", False),
    ("", "", False),
    ("tomsmith", "wrongpassword", False),
]

@pytest.mark.asyncio
# TODO: Add parametrize decorator
async def test_login_scenarios(page, element_manager, username, password, should_succeed):
    """
    Test multiple login scenarios
    
    TODO: Implement test that handles both success and failure cases
    """
    pass
```

### Solution 3.1
<details>
<summary>Click to reveal solution</summary>

```python
import pytest
from pages.login_page import LoginPage

test_data = [
    ("tomsmith", "SuperSecretPassword!", True),
    ("invalid", "invalid", False),
    ("", "", False),
    ("tomsmith", "wrongpassword", False),
]

@pytest.mark.asyncio
@pytest.mark.parametrize("username,password,should_succeed", test_data)
async def test_login_scenarios(page, element_manager, username, password, should_succeed):
    login_page = LoginPage(page, element_manager)
    
    await login_page.navigate()
    await login_page.login(username, password)
    
    if should_succeed:
        await login_page.verify_login_success()
    else:
        await login_page.verify_login_failure()
```
</details>

### Task 3.2: External Data File
Create `test_data.json`:

```json
{
  "login_tests": [
    {
      "test_id": "TC001",
      "username": "tomsmith",
      "password": "SuperSecretPassword!",
      "expected": "success"
    },
    {
      "test_id": "TC002",
      "username": "invalid",
      "password": "invalid",
      "expected": "failure"
    }
  ]
}
```

Create test that loads data from file:

```python
import json
import pytest
from pages.login_page import LoginPage

def load_test_data():
    """Load test data from JSON file"""
    # TODO: Load and return test data
    pass

@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", load_test_data())
async def test_login_from_file(page, element_manager, test_case):
    """
    Test login using data from external file
    
    TODO: Implement test
    """
    pass
```

### Solution 3.2
<details>
<summary>Click to reveal solution</summary>

```python
import json
import pytest
from pages.login_page import LoginPage

def load_test_data():
    with open("test_data.json", "r") as f:
        data = json.load(f)
    return data["login_tests"]

@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", load_test_data())
async def test_login_from_file(page, element_manager, test_case):
    login_page = LoginPage(page, element_manager)
    
    await login_page.navigate()
    await login_page.login(test_case["username"], test_case["password"])
    
    if test_case["expected"] == "success":
        await login_page.verify_login_success()
    else:
        await login_page.verify_login_failure()
```
</details>

### Task 3.3: DDDB Integration (Optional)
If you have access to DDDB:

```python
from raptor.database import DatabaseManager

@pytest.fixture
async def database():
    """Database fixture"""
    db = DatabaseManager(
        connection_string="your_connection_string",
        user="your_user",
        password="your_password"
    )
    await db.connect()
    yield db
    await db.disconnect()

@pytest.mark.asyncio
async def test_with_dddb(page, element_manager, database):
    """
    Test using data from DDDB
    
    TODO: Load test data from DDDB
    TODO: Execute test
    TODO: Save results back to DDDB
    """
    # Load data
    test_data = await database.import_data(
        table="LoginTestData",
        test_id=101,
        iteration=1,
        instance=1
    )
    
    # Execute test
    login_page = LoginPage(page, element_manager)
    await login_page.navigate()
    await login_page.login(test_data["username"], test_data["password"])
    
    # Verify and save result
    try:
        await login_page.verify_login_success()
        result = "PASS"
    except AssertionError:
        result = "FAIL"
    
    await database.export_data(
        table="LoginTestData",
        pk_id=test_data["pk_id"],
        field="result",
        value=result
    )
```

### Verification
```bash
pytest test_exercise3.py -v
```

---

## Exercise 4: Session Reuse (30 minutes)

### Objective
Learn to save and restore browser sessions for faster test development and debugging.

### Task 4.1: Save a Session
Create `test_exercise4.py`:

```python
import pytest
from raptor.core import SessionManager
from pages.login_page import LoginPage

@pytest.mark.asyncio
async def test_save_logged_in_session(page, element_manager):
    """
    Login and save the session
    
    Steps:
    1. Login successfully
    2. Navigate to a specific page
    3. Save the session
    """
    # TODO: Implement session saving
    pass
```

### Solution 4.1
<details>
<summary>Click to reveal solution</summary>

```python
import pytest
from raptor.core import SessionManager
from pages.login_page import LoginPage
from pages.secure_area_page import SecureAreaPage

@pytest.mark.asyncio
async def test_save_logged_in_session(page, element_manager):
    session_manager = SessionManager()
    login_page = LoginPage(page, element_manager)
    secure_page = SecureAreaPage(page, element_manager)
    
    # Login
    await login_page.navigate()
    await login_page.login("tomsmith", "SuperSecretPassword!")
    await secure_page.verify_on_secure_page()
    
    # Save session
    await session_manager.save_session(page, "logged_in_session")
    print("✅ Session saved as 'logged_in_session'")
```
</details>

### Task 4.2: Restore and Use Session
```python
@pytest.mark.asyncio
async def test_restore_and_continue():
    """
    Restore saved session and continue testing
    
    Steps:
    1. Restore the saved session
    2. Verify still logged in
    3. Perform additional actions
    """
    # TODO: Implement session restoration
    pass
```

### Solution 4.2
<details>
<summary>Click to reveal solution</summary>

```python
@pytest.mark.asyncio
async def test_restore_and_continue():
    session_manager = SessionManager()
    
    # Restore session
    page = await session_manager.restore_session("logged_in_session")
    element_manager = ElementManager(page)
    
    # Verify still logged in
    secure_page = SecureAreaPage(page, element_manager)
    await secure_page.verify_on_secure_page()
    
    # Continue testing from this point
    print("✅ Session restored successfully")
    
    # Cleanup
    browser_manager = BrowserManager()
    await browser_manager.close_browser()
```
</details>

### Task 4.3: Session Management CLI
Practice using the CLI:

```bash
# List all saved sessions
raptor session list

# Delete old sessions
raptor session delete old_session_name

# Run test and save session
pytest test_exercise4.py::test_save_logged_in_session -v

# Restore and use session
pytest test_exercise4.py::test_restore_and_continue -v
```

### Verification
1. Run the save session test
2. Verify session file created in `.raptor/sessions/`
3. Run the restore session test
4. Verify it continues from logged-in state

---

## Bonus Exercise: Table Interactions (30 minutes)

### Objective
Learn to work with data tables using TableManager.

### Task: Dynamic Table Test
Visit https://the-internet.herokuapp.com/tables and create tests:

```python
import pytest
from raptor.pages import TableManager

@pytest.mark.asyncio
async def test_table_operations(page, element_manager):
    """
    Test table operations
    
    Steps:
    1. Navigate to tables page
    2. Find a row by last name
    3. Get email from that row
    4. Verify email format
    5. Count total rows
    """
    await page.goto("https://the-internet.herokuapp.com/tables")
    
    table_manager = TableManager(page, element_manager)
    
    # TODO: Find row with last name "Smith"
    # TODO: Get email from that row
    # TODO: Verify email contains "@"
    # TODO: Get total row count
    pass
```

### Solution
<details>
<summary>Click to reveal solution</summary>

```python
import pytest
from raptor.pages import TableManager

@pytest.mark.asyncio
async def test_table_operations(page, element_manager):
    await page.goto("https://the-internet.herokuapp.com/tables")
    
    table_manager = TableManager(page, element_manager)
    
    # Find row by last name
    row_index = await table_manager.find_row_by_key(
        table_locator="css=#table1",
        key_column=0,  # Last name column
        key_value="Smith"
    )
    
    # Get email
    email = await table_manager.get_cell_value(
        table_locator="css=#table1",
        row=row_index,
        column=2  # Email column
    )
    
    # Verify
    assert "@" in email, f"Email should contain @: {email}"
    
    # Count rows
    row_count = await table_manager.get_row_count("css=#table1")
    assert row_count > 0, "Table should have rows"
    
    print(f"✅ Found {row_count} rows, Smith's email: {email}")
```
</details>

---

## Summary and Next Steps

### What You've Learned
- ✅ Basic RAPTOR test structure
- ✅ Element interactions and assertions
- ✅ Page Object Model pattern
- ✅ Data-driven testing
- ✅ Session reuse for efficiency
- ✅ Table operations

### Next Steps
1. **Take the Certification Quiz** to test your knowledge
2. **Start converting real tests** from Java to Python
3. **Join the RAPTOR community** for support
4. **Share your feedback** to improve the framework

### Additional Practice
- Create page objects for your application
- Convert an existing Java test to Python
- Implement a complete test suite with reporting
- Experiment with parallel execution

---

## Need Help?

### Resources
- 📚 Documentation: `docs/`
- 💡 Examples: `examples/`
- 🐛 Issues: GitHub Issues
- 💬 Support: #raptor-support

### Common Issues
- **Import errors**: Check virtual environment activation
- **Browser not found**: Run `playwright install`
- **Async errors**: Remember to use `async`/`await`
- **Element not found**: Check locator syntax

**Happy Testing! 🚀**
