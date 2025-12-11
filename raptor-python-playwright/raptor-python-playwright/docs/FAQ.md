# RAPTOR Frequently Asked Questions (FAQ)

This document answers common questions about the RAPTOR Python Playwright Framework.

## Table of Contents

- [General Questions](#general-questions)
- [Installation and Setup](#installation-and-setup)
- [Browser and Element Management](#browser-and-element-management)
- [Database and Data-Driven Testing](#database-and-data-driven-testing)
- [Session Management](#session-management)
- [Test Execution](#test-execution)
- [Reporting and Debugging](#reporting-and-debugging)
- [Migration from Java/Selenium](#migration-from-javaselium)
- [Performance and Optimization](#performance-and-optimization)
- [Best Practices](#best-practices)

## General Questions

### What is RAPTOR?

RAPTOR (Robust Automated Playwright Test Orchestration & Reporting) is a Python-based test automation framework built on Microsoft Playwright. It provides a robust, maintainable approach to automated testing with features like intelligent element location, session management, data-driven testing, and comprehensive reporting.

### Why choose RAPTOR over other frameworks?

RAPTOR offers several advantages:
- **Modern Technology**: Built on Playwright, which is faster and more reliable than Selenium
- **Intelligent Element Location**: Multiple locator strategies with automatic fallback
- **Session Persistence**: Save and restore browser sessions between test runs
- **Data-Driven Testing**: Built-in integration with DDDB
- **Property-Based Testing**: Support for Hypothesis framework
- **Migration Tools**: Utilities for converting existing Java/Selenium tests
- **Comprehensive Documentation**: Extensive guides and examples

### Is RAPTOR free and open source?

Yes, RAPTOR is open source and free to use under the MIT license.

### What browsers does RAPTOR support?

RAPTOR supports all browsers that Playwright supports:
- Chromium (Chrome, Edge)
- Firefox
- WebKit (Safari)

### What Python versions are supported?

RAPTOR requires Python 3.8 or higher. Python 3.10+ is recommended for best performance.

### Can I use RAPTOR with existing test frameworks?

Yes, RAPTOR integrates seamlessly with pytest and can work alongside other testing tools.

## Installation and Setup

### How do I install RAPTOR?

```bash
pip install raptor-playwright
playwright install
```

See the [Installation Guide](INSTALLATION_GUIDE.md) for detailed instructions.

### Do I need to install browsers separately?

Yes, after installing RAPTOR, you must install Playwright browser binaries:

```bash
playwright install
```

### Can I install only specific browsers?

Yes:

```bash
playwright install chromium  # Only Chromium
playwright install firefox   # Only Firefox
playwright install webkit    # Only WebKit
```

### How do I set up a virtual environment?

```bash
python -m venv raptor-env
source raptor-env/bin/activate  # Windows: raptor-env\Scripts\activate
pip install raptor-playwright
```

### Where should I put my configuration files?

Create a `config` directory in your project root:
```
project/
├── config/
│   ├── settings.yaml
│   └── environments/
│       ├── dev.yaml
│       ├── staging.yaml
│       └── prod.yaml
├── tests/
└── ...
```

### How do I handle sensitive credentials?

Use environment variables:

1. Create a `.env` file:
```bash
DB_PASSWORD=secure_password
API_KEY=your_api_key
```

2. Reference in configuration:
```yaml
database:
  password: ${DB_PASSWORD}
```

3. Add `.env` to `.gitignore`

## Browser and Element Management

### How do I run tests in headless mode?

Set in configuration:
```yaml
browser:
  headless: true
```

Or programmatically:
```python
await browser_manager.launch_browser("chromium", headless=True)
```

### How do I handle elements in iframes?

```python
# Locate iframe
frame = page.frame_locator("iframe[name='myframe']")

# Interact with elements in iframe
await frame.locator("#element-id").click()
```

### What if my element locator keeps changing?

Use multiple locator strategies with fallback:

```python
await element_manager.locate_element(
    "css=#dynamic-id",
    fallback_locators=[
        "xpath=//button[@class='submit']",
        "text=Submit",
        "role=button[name='Submit']"
    ]
)
```

### How do I wait for an element to appear?

```python
# Wait with default timeout
await element_manager.wait_for_element("css=#element-id")

# Wait with custom timeout
await element_manager.wait_for_element("css=#element-id", timeout=60000)

# Wait for specific state
await page.locator("#element-id").wait_for(state="visible")
```

### How do I handle dynamic content that loads slowly?

```python
# Wait for network idle
await page.wait_for_load_state("networkidle")

# Wait for specific element
await page.wait_for_selector("#content-loaded")

# Wait for custom condition
await page.wait_for_function("document.readyState === 'complete'")
```

### Can I take screenshots during test execution?

Yes:

```python
# Full page screenshot
await page.screenshot(path="screenshot.png", full_page=True)

# Element screenshot
await page.locator("#element-id").screenshot(path="element.png")

# Automatic on failure
# Configure in settings.yaml
reporting:
  screenshots:
    on_failure: true
```

### How do I handle file uploads?

```python
# Set input files
await page.locator("input[type='file']").set_input_files("path/to/file.pdf")

# Multiple files
await page.locator("input[type='file']").set_input_files([
    "file1.pdf",
    "file2.pdf"
])
```

### How do I handle file downloads?

```python
# Wait for download
async with page.expect_download() as download_info:
    await page.locator("#download-button").click()

download = await download_info.value

# Save to specific location
await download.save_as("downloads/file.pdf")
```

## Database and Data-Driven Testing

### How do I connect to a database?

```python
from raptor.database import DatabaseManager

db_manager = DatabaseManager(
    connection_string="DRIVER={SQL Server};SERVER=localhost;DATABASE=test_db",
    user="test_user",
    password="password"
)

await db_manager.connect()
```

### How do I load test data from DDDB?

```python
test_data = await db_manager.import_data(
    table="TestData",
    test_id=1,
    iteration=1,
    instance=1
)

username = test_data.get("username")
password = test_data.get("password")
```

### Can I use different databases?

Yes, RAPTOR supports:
- SQL Server
- PostgreSQL
- MySQL
- Oracle
- SQLite

Configure in `settings.yaml`:
```yaml
database:
  type: postgresql  # or mysql, oracle, sqlite
  server: localhost
  port: 5432
  database: test_db
```

### How do I run the same test with multiple data sets?

Use pytest parametrization:

```python
@pytest.mark.parametrize("username,password", [
    ("user1", "pass1"),
    ("user2", "pass2"),
    ("user3", "pass3"),
])
@pytest.mark.asyncio
async def test_login(username, password):
    # Test implementation
```

Or load from database:

```python
from raptor.utils.data_driven import load_test_data

@pytest.mark.asyncio
async def test_login_data_driven():
    test_data = await load_test_data(
        db_manager=db_manager,
        table="LoginTests",
        test_id=1
    )
    
    for data in test_data:
        # Run test with each data set
```

## Session Management

### What is session management?

Session management allows you to save a browser session (including cookies, local storage, etc.) and restore it later, avoiding repeated login steps and speeding up test execution.

### How do I save a browser session?

```python
from raptor.core import SessionManager

session_manager = SessionManager()

# After logging in
await session_manager.save_session(page, "my_session")
```

### How do I restore a saved session?

```python
# Try to restore session
page = await session_manager.restore_session("my_session")

if page is None:
    # Session doesn't exist, create new
    await browser_manager.launch_browser("chromium")
    page = await browser_manager.create_page()
    # Perform login
    await session_manager.save_session(page, "my_session")
```

### How long do sessions last?

By default, sessions expire after 24 hours. Configure in `settings.yaml`:

```yaml
session:
  expiration_hours: 48  # 2 days
```

### Can I share sessions between tests?

Yes, sessions are stored on disk and can be shared:

```python
# Test 1 saves session
await session_manager.save_session(page, "shared_session")

# Test 2 restores session
page = await session_manager.restore_session("shared_session")
```

### How do I clear old sessions?

```python
# Delete specific session
await session_manager.delete_session("old_session")

# List all sessions
sessions = await session_manager.list_sessions()

# Auto-cleanup (configure in settings.yaml)
session:
  auto_cleanup: true
  cleanup_interval: 3600  # seconds
```

## Test Execution

### How do I run tests?

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_login.py

# Run specific test
pytest tests/test_login.py::test_login_success

# Run with markers
pytest -m smoke
```

### How do I run tests in parallel?

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run with 4 workers
pytest -n 4
```

Or configure in `settings.yaml`:
```yaml
execution:
  parallel:
    enabled: true
    workers: 4
```

### How do I retry failed tests?

Configure in `settings.yaml`:
```yaml
execution:
  retry:
    enabled: true
    max_attempts: 3
    delay: 1
```

Or use pytest-rerunfailures:
```bash
pip install pytest-rerunfailures
pytest --reruns 2
```

### How do I skip tests conditionally?

```python
import pytest

@pytest.mark.skipif(condition, reason="Reason for skipping")
@pytest.mark.asyncio
async def test_something():
    # Test implementation
```

### How do I set test timeouts?

```python
@pytest.mark.timeout(300)  # 5 minutes
@pytest.mark.asyncio
async def test_long_running():
    # Test implementation
```

Or configure globally:
```yaml
execution:
  timeout:
    default: 300  # seconds
```

### Can I run tests in different environments?

Yes, use environment-specific configuration:

```bash
# Development
TEST_ENVIRONMENT=dev pytest

# Staging
TEST_ENVIRONMENT=staging pytest

# Production
TEST_ENVIRONMENT=prod pytest
```

## Reporting and Debugging

### How do I generate HTML reports?

```bash
# Install pytest-html
pip install pytest-html

# Generate report
pytest --html=report.html
```

Or use RAPTOR's built-in reporter:
```python
from raptor.utils import TestReporter

reporter = TestReporter()
reporter.generate_html_report("reports/report.html")
```

### How do I enable debug logging?

```yaml
logging:
  level: DEBUG
  console:
    enabled: true
```

Or programmatically:
```python
from raptor.utils.logger import get_logger

logger = get_logger(__name__, level="DEBUG")
```

### How do I debug failing tests?

1. Run in headed mode:
```yaml
browser:
  headless: false
```

2. Use slow motion:
```python
await browser_manager.launch_browser("chromium", slow_mo=1000)
```

3. Use Playwright Inspector:
```bash
PWDEBUG=1 pytest test_file.py
```

4. Take screenshots:
```python
await page.screenshot(path="debug.png")
```

5. Check console logs:
```python
page.on("console", lambda msg: print(f"Console: {msg.text}"))
```

### How do I capture video recordings?

```yaml
browser:
  recording:
    video: true
    video_size:
      width: 1920
      height: 1080
```

Videos are saved automatically on test failure.

## Migration from Java/Selenium

### Can I migrate existing Java/Selenium tests?

Yes, RAPTOR provides migration utilities:

```python
from raptor.migration import JavaToPythonConverter

converter = JavaToPythonConverter()
python_code = converter.convert_file("JavaTest.java")
```

### What's the equivalent of WebDriver in RAPTOR?

Use `BrowserManager`:

```python
# Java/Selenium
WebDriver driver = new ChromeDriver();

# RAPTOR
browser_manager = BrowserManager()
await browser_manager.launch_browser("chromium")
page = await browser_manager.create_page()
```

### How do I convert WebElement operations?

```python
# Java/Selenium
WebElement element = driver.findElement(By.id("element-id"));
element.click();

# RAPTOR
await element_manager.click("css=#element-id")
```

### Are DDFE element definitions compatible?

Yes, RAPTOR supports existing DDFE element definitions. Use the validator:

```python
from raptor.migration import DDFEValidator

validator = DDFEValidator()
is_valid = validator.validate_element_definition(element_def)
```

### How long does migration typically take?

- Simple tests: 1-2 hours per test
- Complex tests: 4-8 hours per test
- Framework setup: 1-2 weeks

Use migration utilities to speed up the process.

## Performance and Optimization

### How can I make my tests faster?

1. Use headless mode
2. Run tests in parallel
3. Reuse browser sessions
4. Optimize locators
5. Reduce unnecessary waits
6. Use connection pooling for database

See [Performance Optimization](user_guide.rst#performance-optimization) for details.

### Why are my tests slow?

Common causes:
- Running in headed mode
- Excessive fixed waits (`sleep`)
- Inefficient locators
- Not using parallel execution
- Slow network/database connections
- Large screenshots/videos

### How much memory do tests typically use?

- Single browser instance: 100-200MB
- With video recording: 300-500MB
- Parallel execution (4 workers): 800MB-2GB

### Can I run tests on low-resource machines?

Yes, optimize for low resources:

```yaml
browser:
  headless: true
  args:
    - --disable-dev-shm-usage
    - --disable-gpu

execution:
  parallel:
    workers: 2  # Reduce workers

reporting:
  video:
    on_failure: false  # Disable video
```

## Best Practices

### Should I use Page Object Model?

Yes, Page Object Model improves maintainability:

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

### How should I organize my tests?

```
project/
├── config/
│   └── settings.yaml
├── tests/
│   ├── conftest.py
│   ├── test_login.py
│   ├── test_checkout.py
│   └── ...
├── pages/
│   ├── login_page.py
│   ├── checkout_page.py
│   └── ...
├── utils/
│   └── helpers.py
└── reports/
```

### Should I use soft assertions?

Use soft assertions when you want to collect multiple failures:

```python
from raptor.core import SoftAssertionCollector

soft_assert = SoftAssertionCollector()

soft_assert.verify_exists("css=#element1")
soft_assert.verify_text("css=#title", "Expected")
soft_assert.verify_enabled("css=#button")

soft_assert.assert_all()  # Fails if any assertion failed
```

### How do I handle flaky tests?

1. Use proper waits (not fixed sleeps)
2. Implement retry logic
3. Use fallback locators
4. Check for race conditions
5. Isolate test data
6. Use stable test environments

### Should I commit configuration files?

- Commit: `settings.yaml`, environment configs
- Don't commit: `.env`, credentials, secrets
- Use `.gitignore`:
```
.env
*.log
screenshots/
videos/
reports/
.sessions/
```

## Still Have Questions?

- Check the [User Guide](user_guide.rst)
- Review [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
- Browse [Examples](examples.rst)
- Visit [GitHub Issues](https://github.com/your-org/raptor-playwright/issues)
- Join [Community Forum](https://community.raptor-framework.org)
- Contact support: support@raptor-framework.org
