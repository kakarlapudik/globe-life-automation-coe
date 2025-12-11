# RAPTOR Troubleshooting Guide

This guide helps you diagnose and resolve common issues when using the RAPTOR Python Playwright Framework.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Browser Issues](#browser-issues)
- [Element Location Issues](#element-location-issues)
- [Timeout Issues](#timeout-issues)
- [Database Issues](#database-issues)
- [Session Management Issues](#session-management-issues)
- [Performance Issues](#performance-issues)
- [Configuration Issues](#configuration-issues)
- [Test Execution Issues](#test-execution-issues)
- [Reporting Issues](#reporting-issues)
- [Platform-Specific Issues](#platform-specific-issues)
- [Debugging Techniques](#debugging-techniques)

## Installation Issues

### Issue: pip install fails with permission error

**Symptoms**:
```
ERROR: Could not install packages due to an EnvironmentError: [Errno 13] Permission denied
```

**Solutions**:

1. Use virtual environment (recommended):
```bash
python -m venv raptor-env
source raptor-env/bin/activate  # Windows: raptor-env\Scripts\activate
pip install raptor-playwright
```

2. Install for current user only:
```bash
pip install --user raptor-playwright
```

3. Use sudo (not recommended):
```bash
sudo pip install raptor-playwright
```

### Issue: Playwright browsers fail to install

**Symptoms**:
```
Failed to install browsers
Error: browserType.launch: Executable doesn't exist
```

**Solutions**:

1. Install browsers explicitly:
```bash
playwright install
```

2. Install with system dependencies (Linux):
```bash
playwright install --with-deps
```

3. Install specific browser:
```bash
playwright install chromium
```

4. Check system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2
```

### Issue: Import errors after installation

**Symptoms**:
```python
ImportError: No module named 'raptor'
```

**Solutions**:

1. Verify installation:
```bash
pip list | grep raptor
```

2. Check Python path:
```python
import sys
print(sys.path)
```

3. Reinstall package:
```bash
pip uninstall raptor-playwright
pip install raptor-playwright
```

4. Check virtual environment activation:
```bash
which python  # Should point to venv
```

## Browser Issues

### Issue: Browser fails to launch

**Symptoms**:
```
browserType.launch: Browser closed unexpectedly
```

**Solutions**:

1. Check browser installation:
```bash
playwright list-browsers
```

2. Try different browser:
```python
await browser_manager.launch_browser("firefox")  # Instead of chromium
```

3. Add browser arguments:
```python
await browser_manager.launch_browser(
    "chromium",
    args=["--no-sandbox", "--disable-dev-shm-usage"]
)
```

4. Check system resources:
```bash
free -h  # Check available memory
df -h    # Check disk space
```

### Issue: Browser crashes during test execution

**Symptoms**:
```
Browser closed unexpectedly
Target page, context or browser has been closed
```

**Solutions**:

1. Increase timeout:
```yaml
browser:
  timeout: 60000  # Increase to 60 seconds
```

2. Disable GPU acceleration:
```yaml
browser:
  args:
    - --disable-gpu
    - --disable-software-rasterizer
```

3. Increase shared memory (Docker):
```yaml
browser:
  args:
    - --disable-dev-shm-usage
```

4. Check browser logs:
```python
browser = await browser_manager.launch_browser("chromium", headless=False)
# Check console for errors
```

### Issue: Headless mode behaves differently than headed

**Symptoms**:
- Tests pass in headed mode but fail in headless
- Elements not found in headless mode

**Solutions**:

1. Use same viewport size:
```yaml
browser:
  viewport:
    width: 1920
    height: 1080
```

2. Wait for network idle:
```python
await page.wait_for_load_state("networkidle")
```

3. Add delays for dynamic content:
```python
await page.wait_for_timeout(1000)
```

4. Check for JavaScript errors:
```python
page.on("console", lambda msg: print(f"Console: {msg.text}"))
page.on("pageerror", lambda err: print(f"Error: {err}"))
```

## Element Location Issues

### Issue: Element not found

**Symptoms**:
```
ElementNotFoundException: Element not found: css=#element-id
```

**Solutions**:

1. Verify locator is correct:
```python
# Try in browser console first
document.querySelector("#element-id")
```

2. Wait for element:
```python
await element_manager.wait_for_element("css=#element-id", timeout=30000)
```

3. Use fallback locators:
```python
await element_manager.locate_element(
    "css=#element-id",
    fallback_locators=[
        "xpath=//div[@id='element-id']",
        "text=Click Me"
    ]
)
```

4. Check if element is in iframe:
```python
frame = page.frame_locator("iframe[name='myframe']")
await frame.locator("#element-id").click()
```

5. Wait for page load:
```python
await page.wait_for_load_state("domcontentloaded")
```

### Issue: Element found but not interactable

**Symptoms**:
```
ElementNotInteractableException: Element is not visible or enabled
```

**Solutions**:

1. Wait for element to be visible:
```python
await element_manager.wait_for_element("css=#element-id")
await page.locator("#element-id").wait_for(state="visible")
```

2. Scroll element into view:
```python
await page.locator("#element-id").scroll_into_view_if_needed()
```

3. Wait for element to be enabled:
```python
await page.locator("#element-id").wait_for(state="enabled")
```

4. Use force click:
```python
await page.locator("#element-id").click(force=True)
```

5. Try JavaScript click:
```python
await page.evaluate("document.querySelector('#element-id').click()")
```

### Issue: Stale element reference

**Symptoms**:
```
Error: Element is not attached to the DOM
```

**Solutions**:

1. Re-locate element:
```python
# Don't store element references
# Instead, use locators
locator = page.locator("#element-id")
await locator.click()
```

2. Wait after DOM changes:
```python
await page.wait_for_timeout(500)
await element_manager.click("css=#element-id")
```

3. Use Playwright's auto-waiting:
```python
# Playwright automatically waits for element
await page.locator("#element-id").click()
```

## Timeout Issues

### Issue: Tests timing out

**Symptoms**:
```
TimeoutException: Timeout 30000ms exceeded
```

**Solutions**:

1. Increase timeout:
```python
await element_manager.wait_for_element("css=#element-id", timeout=60000)
```

2. Wait for specific condition:
```python
await page.wait_for_function("document.readyState === 'complete'")
```

3. Wait for network idle:
```python
await page.wait_for_load_state("networkidle")
```

4. Check network requests:
```python
page.on("request", lambda request: print(f"Request: {request.url}"))
page.on("response", lambda response: print(f"Response: {response.url} - {response.status}"))
```

5. Disable timeout for debugging:
```python
await page.locator("#element-id").click(timeout=0)  # No timeout
```

### Issue: Slow test execution

**Symptoms**:
- Tests take much longer than expected
- Excessive waiting

**Solutions**:

1. Reduce unnecessary waits:
```python
# Don't use fixed waits
# await page.wait_for_timeout(5000)  # Bad

# Use conditional waits
await page.wait_for_selector("#element-id")  # Good
```

2. Use network idle strategically:
```python
# Only wait for network idle when necessary
await page.goto(url, wait_until="domcontentloaded")  # Faster
```

3. Optimize locators:
```python
# Use efficient locators
await page.locator("#id").click()  # Fast
# await page.locator("div > div > div > span").click()  # Slow
```

4. Enable parallel execution:
```yaml
execution:
  parallel:
    enabled: true
    workers: 4
```

## Database Issues

### Issue: Database connection fails

**Symptoms**:
```
DatabaseException: Unable to connect to database
```

**Solutions**:

1. Verify connection string:
```python
print(config.get("database.server"))
print(config.get("database.database"))
```

2. Test connection manually:
```python
import pyodbc
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=test_db;"
    "UID=test_user;"
    "PWD=password"
)
```

3. Check database driver:
```bash
# List ODBC drivers
odbcinst -q -d
```

4. Install missing driver:
```bash
# Ubuntu/Debian
sudo apt-get install unixodbc unixodbc-dev

# Install SQL Server driver
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

5. Check firewall:
```bash
telnet database-server 1433
```

### Issue: Query execution fails

**Symptoms**:
```
DatabaseException: Error executing query
```

**Solutions**:

1. Check SQL syntax:
```python
# Test query in database client first
```

2. Use parameterized queries:
```python
# Bad
query = f"SELECT * FROM users WHERE id = {user_id}"

# Good
query = "SELECT * FROM users WHERE id = ?"
result = await db_manager.execute_query(query, params=[user_id])
```

3. Check permissions:
```sql
-- Verify user has necessary permissions
GRANT SELECT, INSERT, UPDATE ON database.table TO user;
```

4. Enable query logging:
```yaml
database:
  connection_pool:
    echo: true  # Log all SQL statements
```

### Issue: Connection pool exhausted

**Symptoms**:
```
DatabaseException: Connection pool exhausted
```

**Solutions**:

1. Increase pool size:
```yaml
database:
  connection_pool:
    max_size: 20
    max_overflow: 10
```

2. Close connections properly:
```python
try:
    result = await db_manager.execute_query(query)
finally:
    await db_manager.disconnect()
```

3. Use connection pooling:
```python
# Framework handles this automatically
# Just ensure proper cleanup
```

## Session Management Issues

### Issue: Session restore fails

**Symptoms**:
```
SessionException: Failed to restore session
```

**Solutions**:

1. Check session exists:
```python
sessions = await session_manager.list_sessions()
print(sessions)
```

2. Verify session hasn't expired:
```yaml
session:
  expiration_hours: 48  # Increase expiration
```

3. Clear old sessions:
```python
await session_manager.delete_session("old_session")
```

4. Create new session:
```python
page = await session_manager.restore_session("my_session")
if page is None:
    # Session doesn't exist, create new
    await browser_manager.launch_browser("chromium")
    page = await browser_manager.create_page()
    await session_manager.save_session(page, "my_session")
```

### Issue: Session data not persisting

**Symptoms**:
- Cookies not saved
- Local storage not restored

**Solutions**:

1. Enable persistence:
```yaml
session:
  persistence:
    save_cookies: true
    save_local_storage: true
    save_session_storage: true
```

2. Verify storage directory:
```bash
ls -la .sessions/
```

3. Check permissions:
```bash
chmod 755 .sessions/
```

## Performance Issues

### Issue: High memory usage

**Symptoms**:
- Tests consume excessive memory
- System becomes slow

**Solutions**:

1. Close browsers properly:
```python
try:
    # Test code
finally:
    await browser_manager.close_browser()
```

2. Limit parallel workers:
```yaml
execution:
  parallel:
    workers: 2  # Reduce from 4
```

3. Disable video recording:
```yaml
browser:
  recording:
    video: false
```

4. Clear cache periodically:
```python
await page.context.clear_cookies()
await page.context.clear_permissions()
```

### Issue: Slow element location

**Symptoms**:
- Element location takes several seconds
- Tests are slower than expected

**Solutions**:

1. Use efficient locators:
```python
# Fast
await page.locator("#id").click()
await page.locator(".class").click()

# Slow
await page.locator("div > div > div > span").click()
await page.locator("//div[@class='a']//span[@class='b']").click()
```

2. Reduce fallback attempts:
```yaml
elements:
  fallback:
    max_attempts: 2  # Reduce from 3
```

3. Cache element references:
```python
# Use locators, not elements
login_button = page.locator("#login-button")
await login_button.click()
```

## Configuration Issues

### Issue: Configuration not loading

**Symptoms**:
```
ConfigurationException: Configuration file not found
```

**Solutions**:

1. Verify file exists:
```bash
ls -la config/settings.yaml
```

2. Check file path:
```python
import os
print(os.getcwd())
print(os.path.exists("config/settings.yaml"))
```

3. Use absolute path:
```python
config = ConfigManager(config_path="/absolute/path/to/config/settings.yaml")
```

### Issue: Environment variables not working

**Symptoms**:
- ${VAR_NAME} not being replaced
- Configuration shows literal ${VAR_NAME}

**Solutions**:

1. Load .env file:
```python
from dotenv import load_dotenv
load_dotenv()
```

2. Set environment variables:
```bash
export DB_PASSWORD=mypassword
```

3. Verify environment variables:
```python
import os
print(os.getenv("DB_PASSWORD"))
```

## Test Execution Issues

### Issue: Tests fail in CI/CD but pass locally

**Symptoms**:
- Tests pass on local machine
- Same tests fail in CI/CD pipeline

**Solutions**:

1. Use headless mode in CI:
```yaml
browser:
  headless: true
```

2. Add CI-specific arguments:
```yaml
browser:
  args:
    - --no-sandbox
    - --disable-dev-shm-usage
    - --disable-gpu
```

3. Increase timeouts:
```yaml
execution:
  timeout:
    default: 600  # 10 minutes
```

4. Check CI environment:
```python
import os
if os.getenv("CI"):
    # CI-specific configuration
    config.set("browser.headless", True)
```

### Issue: Parallel tests interfere with each other

**Symptoms**:
- Tests pass when run individually
- Tests fail when run in parallel

**Solutions**:

1. Use isolated contexts:
```python
# Each test gets its own context
@pytest.fixture
async def page(browser_manager):
    await browser_manager.launch_browser("chromium")
    page = await browser_manager.create_page()
    yield page
    await browser_manager.close_browser()
```

2. Use unique test data:
```python
# Generate unique data per test
import uuid
test_id = str(uuid.uuid4())
```

3. Clean up after tests:
```python
@pytest.fixture(autouse=True)
async def cleanup():
    yield
    # Cleanup code
    await clear_test_data()
```

## Reporting Issues

### Issue: Screenshots not captured

**Symptoms**:
- No screenshots in reports
- Screenshot directory empty

**Solutions**:

1. Enable screenshots:
```yaml
reporting:
  screenshots:
    on_failure: true
    path: screenshots
```

2. Create directory:
```bash
mkdir -p screenshots
```

3. Check permissions:
```bash
chmod 755 screenshots
```

4. Capture manually:
```python
await page.screenshot(path="screenshots/test.png")
```

### Issue: HTML report not generated

**Symptoms**:
- No HTML report file
- Report generation fails

**Solutions**:

1. Enable HTML reporting:
```yaml
reporting:
  html:
    enabled: true
    output_file: reports/report.html
```

2. Create reports directory:
```bash
mkdir -p reports
```

3. Generate manually:
```python
from raptor.utils import TestReporter
reporter = TestReporter()
reporter.generate_html_report("reports/report.html")
```

## Platform-Specific Issues

### Windows Issues

**Issue**: PowerShell execution policy

**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Issue**: Long path names

**Solution**:
```powershell
# Enable long paths
New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
```

### macOS Issues

**Issue**: Browser permission dialogs

**Solution**:
```bash
# Grant terminal full disk access
# System Preferences > Security & Privacy > Privacy > Full Disk Access
```

**Issue**: M1/M2 compatibility

**Solution**:
```bash
# Install Rosetta 2
softwareupdate --install-rosetta
```

### Linux Issues

**Issue**: Missing system dependencies

**Solution**:
```bash
# Install all dependencies
playwright install-deps
```

**Issue**: Permission denied

**Solution**:
```bash
# Add user to necessary groups
sudo usermod -a -G video $USER
sudo usermod -a -G audio $USER
```

## Debugging Techniques

### Enable Debug Logging

```python
from raptor.utils.logger import get_logger

logger = get_logger(__name__, level="DEBUG")
logger.debug("Debug message")
```

### Use Playwright Inspector

```python
# Set environment variable
import os
os.environ["PWDEBUG"] = "1"

# Run test - inspector will open
```

### Capture Network Traffic

```python
page.on("request", lambda request: print(f">> {request.method} {request.url}"))
page.on("response", lambda response: print(f"<< {response.status} {response.url}"))
```

### Take Screenshots at Each Step

```python
await page.screenshot(path="step1.png")
await element_manager.click("css=#button")
await page.screenshot(path="step2.png")
```

### Use Slow Motion

```python
await browser_manager.launch_browser("chromium", slow_mo=1000)  # 1 second delay
```

### Check Console Logs

```python
page.on("console", lambda msg: print(f"Console {msg.type}: {msg.text}"))
page.on("pageerror", lambda err: print(f"Page error: {err}"))
```

## Getting Additional Help

If you can't resolve your issue:

1. Check [FAQ](FAQ.md)
2. Review [GitHub Issues](https://github.com/your-org/raptor-playwright/issues)
3. Join [Community Forum](https://community.raptor-framework.org)
4. Contact support: support@raptor-framework.org

When reporting issues, include:
- RAPTOR version
- Python version
- Operating system
- Browser and version
- Full error message and stack trace
- Minimal reproducible example
- Configuration (sanitized)
