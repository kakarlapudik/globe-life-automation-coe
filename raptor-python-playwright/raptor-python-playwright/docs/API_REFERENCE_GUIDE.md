# RAPTOR Python Playwright Framework - API Reference Guide

## Overview

This guide provides a comprehensive reference for all public APIs in the RAPTOR framework. Each section includes method signatures, parameters, return types, and practical examples.

## Table of Contents

1. [Core Modules](#core-modules)
   - [BrowserManager](#browsermanager)
   - [ElementManager](#elementmanager)
   - [SessionManager](#sessionmanager)
   - [ConfigManager](#configmanager)
2. [Database Modules](#database-modules)
3. [Page Objects](#page-objects)
4. [Utility Modules](#utility-modules)
5. [Integration Modules](#integration-modules)
6. [Migration Modules](#migration-modules)
7. [Code Generation Modules](#code-generation-modules)

---

## Core Modules

### BrowserManager

Manages browser lifecycle, contexts, and pages.

#### Methods

##### `launch_browser(browser_type: str, headless: bool = False, **options) -> Browser`

Launches a browser instance.

**Parameters:**
- `browser_type` (str): Browser type - "chromium", "firefox", or "webkit"
- `headless` (bool): Run in headless mode (default: False)
- `**options`: Additional browser launch options

**Returns:**
- `Browser`: Playwright browser instance

**Example:**
```python
browser_manager = BrowserManager()
browser = await browser_manager.launch_browser("chromium", headless=True)
```

##### `create_context(**options) -> BrowserContext`

Creates a new browser context.

**Parameters:**
- `**options`: Context options (viewport, user_agent, etc.)

**Returns:**
- `BrowserContext`: New browser context

**Example:**
```python
context = await browser_manager.create_context(
    viewport={'width': 1920, 'height': 1080},
    user_agent='Custom User Agent'
)
```

##### `create_page(context: BrowserContext = None) -> Page`

Creates a new page in the browser context.

**Parameters:**
- `context` (BrowserContext, optional): Context to create page in

**Returns:**
- `Page`: New page instance

**Example:**
```python
page = await browser_manager.create_page()
```

##### `close_browser()`

Closes the browser and cleans up resources.

**Example:**
```python
await browser_manager.close_browser()
```

---

### ElementManager

Handles element location and interactions with multiple locator strategies.

#### Methods

##### `locate_element(locator: str, fallback_locators: List[str] = None, timeout: int = 20000) -> Locator`

Locates an element using primary and fallback locators.

**Parameters:**
- `locator` (str): Primary locator string (e.g., "css=#button")
- `fallback_locators` (List[str], optional): List of fallback locators
- `timeout` (int): Timeout in milliseconds (default: 20000)

**Returns:**
- `Locator`: Playwright locator object

**Example:**
```python
element = await element_manager.locate_element(
    "css=#submit-button",
    fallback_locators=["xpath=//button[@id='submit-button']", "text=Submit"]
)
```

##### `click(locator: str, **options)`

Clicks an element.

**Parameters:**
- `locator` (str): Element locator
- `**options`: Click options (button, click_count, delay, etc.)

**Example:**
```python
await element_manager.click("css=#login-button")
await element_manager.click("css=#menu", button="right")  # Right-click
```

##### `fill(locator: str, text: str, **options)`

Fills an input field with text.

**Parameters:**
- `locator` (str): Input field locator
- `text` (str): Text to fill
- `**options`: Fill options

**Example:**
```python
await element_manager.fill("css=#username", "testuser")
```

##### `select_option(locator: str, value: str, **options)`

Selects an option from a dropdown.

**Parameters:**
- `locator` (str): Dropdown locator
- `value` (str): Option value to select
- `**options`: Select options

**Example:**
```python
await element_manager.select_option("css=#country", "USA")
```

##### `hover(locator: str, **options)`

Hovers over an element.

**Parameters:**
- `locator` (str): Element locator
- `**options`: Hover options

**Example:**
```python
await element_manager.hover("css=#dropdown-menu")
```

##### `wait_for_element(locator: str, timeout: int = 20000, state: str = "visible")`

Waits for an element to reach a specific state.

**Parameters:**
- `locator` (str): Element locator
- `timeout` (int): Timeout in milliseconds
- `state` (str): Element state - "visible", "hidden", "attached", "detached"

**Example:**
```python
await element_manager.wait_for_element("css=#dashboard", timeout=30000)
```

##### `is_visible(locator: str) -> bool`

Checks if an element is visible.

**Parameters:**
- `locator` (str): Element locator

**Returns:**
- `bool`: True if visible, False otherwise

**Example:**
```python
if await element_manager.is_visible("css=#error-message"):
    print("Error message is displayed")
```

##### `is_enabled(locator: str) -> bool`

Checks if an element is enabled.

**Parameters:**
- `locator` (str): Element locator

**Returns:**
- `bool`: True if enabled, False otherwise

**Example:**
```python
if await element_manager.is_enabled("css=#submit-button"):
    await element_manager.click("css=#submit-button")
```

##### `get_text(locator: str) -> str`

Gets the text content of an element.

**Parameters:**
- `locator` (str): Element locator

**Returns:**
- `str`: Element text content

**Example:**
```python
message = await element_manager.get_text("css=#welcome-message")
print(f"Welcome message: {message}")
```

##### `get_attribute(locator: str, attribute: str) -> str`

Gets an attribute value from an element.

**Parameters:**
- `locator` (str): Element locator
- `attribute` (str): Attribute name

**Returns:**
- `str`: Attribute value

**Example:**
```python
href = await element_manager.get_attribute("css=#link", "href")
```

---

### SessionManager

Manages browser session persistence and restoration.

#### Methods

##### `save_session(page: Page, session_name: str)`

Saves the current browser session.

**Parameters:**
- `page` (Page): Page to save session from
- `session_name` (str): Name for the session

**Example:**
```python
await session_manager.save_session(page, "user_session")
```

##### `restore_session(session_name: str) -> Page`

Restores a previously saved session.

**Parameters:**
- `session_name` (str): Name of session to restore

**Returns:**
- `Page`: Restored page or None if session doesn't exist

**Example:**
```python
page = await session_manager.restore_session("user_session")
if page is None:
    # Session doesn't exist, create new
    pass
```

##### `list_sessions() -> List[str]`

Lists all available sessions.

**Returns:**
- `List[str]`: List of session names

**Example:**
```python
sessions = await session_manager.list_sessions()
print(f"Available sessions: {sessions}")
```

##### `delete_session(session_name: str)`

Deletes a saved session.

**Parameters:**
- `session_name` (str): Name of session to delete

**Example:**
```python
await session_manager.delete_session("old_session")
```

---

### ConfigManager

Handles configuration loading and management.

#### Methods

##### `load_config(environment: str = "dev") -> Dict`

Loads configuration for specified environment.

**Parameters:**
- `environment` (str): Environment name - "dev", "staging", "prod"

**Returns:**
- `Dict`: Configuration dictionary

**Example:**
```python
config = ConfigManager()
config.load_config(environment="staging")
```

##### `get(key: str, default: Any = None) -> Any`

Gets a configuration value.

**Parameters:**
- `key` (str): Configuration key (dot notation supported)
- `default` (Any): Default value if key not found

**Returns:**
- `Any`: Configuration value

**Example:**
```python
timeout = config.get("browser.timeout", 30000)
db_server = config.get("database.server")
```

##### `set(key: str, value: Any)`

Sets a configuration value.

**Parameters:**
- `key` (str): Configuration key
- `value` (Any): Value to set

**Example:**
```python
config.set("browser.headless", True)
```

---

## Database Modules

### DatabaseManager

Manages database connections and operations.

#### Methods

##### `__init__(connection_string: str, user: str, password: str)`

Initializes database manager.

**Parameters:**
- `connection_string` (str): Database connection string
- `user` (str): Database username
- `password` (str): Database password

**Example:**
```python
db_manager = DatabaseManager(
    connection_string="DRIVER={SQL Server};SERVER=localhost;DATABASE=test_db",
    user="test_user",
    password="test_password"
)
```

##### `execute_query(sql: str, params: Dict = None) -> List[Dict]`

Executes a SELECT query.

**Parameters:**
- `sql` (str): SQL query string
- `params` (Dict, optional): Query parameters

**Returns:**
- `List[Dict]`: List of result rows as dictionaries

**Example:**
```python
results = await db_manager.execute_query(
    "SELECT * FROM Users WHERE username = ?",
    params={"username": "testuser"}
)
```

##### `execute_update(sql: str, params: Dict = None) -> int`

Executes an INSERT/UPDATE/DELETE query.

**Parameters:**
- `sql` (str): SQL query string
- `params` (Dict, optional): Query parameters

**Returns:**
- `int`: Number of affected rows

**Example:**
```python
rows_affected = await db_manager.execute_update(
    "UPDATE Users SET status = ? WHERE id = ?",
    params={"status": "active", "id": 123}
)
```

##### `import_data(table: str, test_id: int, iteration: int, instance: int) -> Dict`

Imports test data from DDDB.

**Parameters:**
- `table` (str): Table name
- `test_id` (int): Test ID
- `iteration` (int): Iteration number
- `instance` (int): Instance number

**Returns:**
- `Dict`: Test data dictionary

**Example:**
```python
test_data = await db_manager.import_data(
    table="LoginTests",
    test_id=1,
    iteration=1,
    instance=1
)
username = test_data["username"]
```

##### `export_data(table: str, pk_id: int, field: str, value: str)`

Exports test results to DDDB.

**Parameters:**
- `table` (str): Table name
- `pk_id` (int): Primary key ID
- `field` (str): Field name to update
- `value` (str): Value to set

**Example:**
```python
await db_manager.export_data(
    table="LoginTests",
    pk_id=123,
    field="result",
    value="PASS"
)
```

---

## Page Objects

### BasePage

Base class for all page objects.

#### Methods

##### `__init__(page: Page, element_manager: ElementManager)`

Initializes base page.

**Parameters:**
- `page` (Page): Playwright page instance
- `element_manager` (ElementManager): Element manager instance

##### `navigate(url: str)`

Navigates to a URL.

**Parameters:**
- `url` (str): URL to navigate to

**Example:**
```python
await base_page.navigate("https://example.com/login")
```

##### `wait_for_load()`

Waits for page to finish loading.

**Example:**
```python
await base_page.wait_for_load()
```

##### `take_screenshot(name: str)`

Takes a screenshot of the page.

**Parameters:**
- `name` (str): Screenshot filename

**Example:**
```python
await base_page.take_screenshot("login_page.png")
```

##### `get_title() -> str`

Gets the page title.

**Returns:**
- `str`: Page title

**Example:**
```python
title = await base_page.get_title()
assert "Login" in title
```

##### `get_url() -> str`

Gets the current URL.

**Returns:**
- `str`: Current URL

**Example:**
```python
url = await base_page.get_url()
assert "dashboard" in url
```

---

### TableManager

Specialized operations for data tables.

#### Methods

##### `find_row_by_key(table_locator: str, key_column: int, key_value: str) -> int`

Finds a table row by key column value.

**Parameters:**
- `table_locator` (str): Table locator
- `key_column` (int): Key column index
- `key_value` (str): Value to search for

**Returns:**
- `int`: Row index or -1 if not found

**Example:**
```python
row = await table_manager.find_row_by_key(
    "css=#users-table",
    key_column=0,
    key_value="John Doe"
)
```

##### `get_cell_value(table_locator: str, row: int, column: int) -> str`

Gets the value of a table cell.

**Parameters:**
- `table_locator` (str): Table locator
- `row` (int): Row index
- `column` (int): Column index

**Returns:**
- `str`: Cell value

**Example:**
```python
email = await table_manager.get_cell_value("css=#users-table", row=2, column=3)
```

##### `click_cell(table_locator: str, row: int, column: int)`

Clicks a table cell.

**Parameters:**
- `table_locator` (str): Table locator
- `row` (int): Row index
- `column` (int): Column index

**Example:**
```python
await table_manager.click_cell("css=#users-table", row=2, column=5)  # Click edit button
```

##### `search_table(table_locator: str, search_text: str, case_sensitive: bool = False) -> List[int]`

Searches for text in table and returns matching row indices.

**Parameters:**
- `table_locator` (str): Table locator
- `search_text` (str): Text to search for
- `case_sensitive` (bool): Case-sensitive search (default: False)

**Returns:**
- `List[int]`: List of matching row indices

**Example:**
```python
matching_rows = await table_manager.search_table(
    "css=#products-table",
    search_text="laptop",
    case_sensitive=False
)
```

---

## Utility Modules

### Logger

Structured logging with context.

#### Functions

##### `get_logger(name: str, level: str = "INFO") -> Logger`

Gets a logger instance.

**Parameters:**
- `name` (str): Logger name
- `level` (str): Log level - "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

**Returns:**
- `Logger`: Logger instance

**Example:**
```python
from raptor.utils.logger import get_logger

logger = get_logger(__name__, level="DEBUG")
logger.info("Test started")
logger.debug("Debug information")
logger.error("An error occurred")
```

---

### TestReporter

Test result reporting and HTML generation.

#### Methods

##### `add_test_result(test_name: str, status: str, duration: float, error: str = None)`

Adds a test result.

**Parameters:**
- `test_name` (str): Test name
- `status` (str): Test status - "PASS", "FAIL", "SKIP"
- `duration` (float): Test duration in seconds
- `error` (str, optional): Error message if failed

**Example:**
```python
reporter = TestReporter()
reporter.add_test_result(
    test_name="test_login",
    status="PASS",
    duration=5.2
)
```

##### `generate_html_report(output_path: str)`

Generates HTML test report.

**Parameters:**
- `output_path` (str): Output file path

**Example:**
```python
reporter.generate_html_report("reports/test_report.html")
```

---

### WaitHelpers

Custom wait conditions and synchronization.

#### Functions

##### `wait_for_condition(condition: Callable, timeout: int = 30, message: str = None)`

Waits for a custom condition to be true.

**Parameters:**
- `condition` (Callable): Async function that returns bool
- `timeout` (int): Timeout in seconds
- `message` (str, optional): Error message if timeout

**Example:**
```python
from raptor.utils.wait_helpers import wait_for_condition

async def items_loaded():
    items = await page.locator("css=.item").all()
    return len(items) >= 10

await wait_for_condition(
    condition=items_loaded,
    timeout=30,
    message="Items not loaded"
)
```

##### `exponential_backoff(max_attempts: int = 5, base_delay: float = 1.0)`

Implements exponential backoff retry logic.

**Parameters:**
- `max_attempts` (int): Maximum retry attempts
- `base_delay` (float): Base delay in seconds

**Example:**
```python
from raptor.utils.wait_helpers import exponential_backoff

for attempt in exponential_backoff(max_attempts=5):
    try:
        await element_manager.click("css=#button")
        break
    except Exception as e:
        if attempt == 4:  # Last attempt
            raise
        await asyncio.sleep(attempt)
```

---

## Integration Modules

### ALMIntegration

Integration with HP ALM.

#### Methods

##### `publish_test_result(test_id: str, status: str, details: Dict)`

Publishes test result to ALM.

**Parameters:**
- `test_id` (str): ALM test ID
- `status` (str): Test status
- `details` (Dict): Test details

**Example:**
```python
from raptor.integrations import ALMIntegration

alm = ALMIntegration(
    server="alm.example.com",
    username="user",
    password="pass"
)

await alm.publish_test_result(
    test_id="TC-001",
    status="PASS",
    details={"duration": 10.5, "environment": "staging"}
)
```

---

### JIRAIntegration

Integration with Atlassian JIRA.

#### Methods

##### `create_issue(project: str, summary: str, description: str, issue_type: str = "Bug")`

Creates a JIRA issue.

**Parameters:**
- `project` (str): JIRA project key
- `summary` (str): Issue summary
- `description` (str): Issue description
- `issue_type` (str): Issue type (default: "Bug")

**Returns:**
- `str`: Created issue key

**Example:**
```python
from raptor.integrations import JIRAIntegration

jira = JIRAIntegration(
    server="jira.example.com",
    username="user",
    api_token="token"
)

issue_key = await jira.create_issue(
    project="TEST",
    summary="Login button not working",
    description="The login button does not respond to clicks",
    issue_type="Bug"
)
```

---

## Migration Modules

### JavaToPythonConverter

Converts Java test code to Python.

#### Methods

##### `convert_file(input_path: str, output_path: str)`

Converts a Java file to Python.

**Parameters:**
- `input_path` (str): Input Java file path
- `output_path` (str): Output Python file path

**Example:**
```python
from raptor.migration import JavaToPythonConverter

converter = JavaToPythonConverter()
converter.convert_file("LoginTest.java", "test_login.py")
```

---

## Code Generation Modules

### PageObjectGenerator

Generates page objects from DDFE definitions.

#### Methods

##### `generate_page_object(ddfe_file: str, output_path: str)`

Generates a page object from DDFE file.

**Parameters:**
- `ddfe_file` (str): DDFE XML file path
- `output_path` (str): Output Python file path

**Example:**
```python
from raptor.codegen import PageObjectGenerator

generator = PageObjectGenerator()
generator.generate_page_object(
    "elements/login_page.xml",
    "pages/login_page.py"
)
```

---

## Best Practices

### Error Handling

Always use try-finally for cleanup:

```python
browser_manager = BrowserManager()
try:
    await browser_manager.launch_browser("chromium")
    # ... test code
finally:
    await browser_manager.close_browser()
```

### Async/Await

Always await async methods:

```python
# ❌ Wrong
element_manager.click("css=#button")

# ✓ Correct
await element_manager.click("css=#button")
```

### Locator Strategies

Use fallback locators for resilience:

```python
await element_manager.locate_element(
    "css=#primary-button",
    fallback_locators=[
        "xpath=//button[@id='primary-button']",
        "text=Submit"
    ]
)
```

### Configuration

Use environment-specific configs:

```python
config = ConfigManager()
config.load_config(environment="staging")
```

---

## Additional Resources

- **Full Documentation**: https://raptor-docs.example.com
- **GitHub Repository**: https://github.com/your-org/raptor-playwright
- **Issue Tracker**: https://github.com/your-org/raptor-playwright/issues
- **Slack Channel**: #raptor-support

---

## Version History

- **v1.0.0** (2024-11-28): Initial release with complete API documentation
