# BasePage Quick Reference

## Overview

The `BasePage` class is the foundation for all page objects in the RAPTOR framework. It provides common functionality for page navigation, waiting, screenshots, and JavaScript execution.

## Basic Usage

```python
from raptor.pages.base_page import BasePage
from raptor.core.element_manager import ElementManager

# Create a custom page object
class LoginPage(BasePage):
    def __init__(self, page, element_manager=None):
        super().__init__(page, element_manager)
        
        # Define page-specific locators
        self.username_field = "css=#username"
        self.password_field = "css=#password"
        self.submit_button = "css=#login-button"
    
    async def login(self, username: str, password: str):
        await self.navigate("https://example.com/login")
        await self.element_manager.fill(self.username_field, username)
        await self.element_manager.fill(self.password_field, password)
        await self.element_manager.click(self.submit_button)
        await self.wait_for_load()
```

## Core Methods

### Navigation

#### `navigate(url, wait_until="load", timeout=None)`
Navigate to a URL and wait for page load.

```python
# Basic navigation
await page.navigate("https://example.com")

# Wait for network idle
await page.navigate("https://example.com", wait_until="networkidle")

# Custom timeout
await page.navigate("https://example.com", timeout=10000)
```

**Parameters:**
- `url` (str): URL to navigate to (must include protocol)
- `wait_until` (str): Load state to wait for
  - `"load"` - Wait for load event (default)
  - `"domcontentloaded"` - Wait for DOMContentLoaded event
  - `"networkidle"` - Wait for network to be idle
  - `"commit"` - Wait for navigation to commit
- `timeout` (int, optional): Timeout in milliseconds

**Raises:**
- `TimeoutException`: If navigation times out
- `RaptorException`: If navigation fails

---

#### `wait_for_load(state="load", timeout=None)`
Wait for page to reach a specific load state.

```python
# Wait for default load state
await page.wait_for_load()

# Wait for network idle
await page.wait_for_load(state="networkidle")

# Custom timeout
await page.wait_for_load(state="domcontentloaded", timeout=5000)
```

**Parameters:**
- `state` (str): Load state to wait for (same options as `navigate`)
- `timeout` (int, optional): Timeout in milliseconds

---

#### `reload(wait_until="load", timeout=None)`
Reload the current page.

```python
await page.reload()
await page.reload(wait_until="networkidle")
```

---

#### `go_back(wait_until="load", timeout=None)`
Navigate back in browser history.

```python
await page.go_back()
```

---

#### `go_forward(wait_until="load", timeout=None)`
Navigate forward in browser history.

```python
await page.go_forward()
```

---

### Screenshots

#### `take_screenshot(name=None, full_page=False, path=None)`
Capture a screenshot of the current page.

```python
# Auto-generated name with timestamp
screenshot_path = await page.take_screenshot()

# Custom name
screenshot_path = await page.take_screenshot("login_page")

# Full page screenshot
screenshot_path = await page.take_screenshot("full_page", full_page=True)

# Custom path
screenshot_path = await page.take_screenshot(path="/custom/path/screenshot.png")
```

**Parameters:**
- `name` (str, optional): Name for the screenshot file (without extension)
- `full_page` (bool): Whether to capture the full scrollable page
- `path` (str, optional): Custom path for the screenshot

**Returns:**
- `str`: Path to the saved screenshot file

**Default Location:** Screenshots are saved to the directory specified in configuration (default: `screenshots/`)

---

### Page Information

#### `get_title()`
Get the current page title.

```python
title = await page.get_title()
assert "Login" in title
```

**Returns:**
- `str`: Page title

---

#### `get_url()`
Get the current page URL.

```python
url = await page.get_url()
assert url == "https://example.com/dashboard"
```

**Returns:**
- `str`: Current page URL

---

### JavaScript Execution

#### `execute_script(script, *args)`
Execute JavaScript code in the page context.

```python
# Simple script
await page.execute_script("window.scrollTo(0, document.body.scrollHeight)")

# Script with return value
dimensions = await page.execute_script(
    "return {width: window.innerWidth, height: window.innerHeight}"
)

# Script with arguments
text = await page.execute_script(
    "return document.querySelector(arguments[0]).textContent",
    "#my-element"
)

# Multiple arguments
result = await page.execute_script(
    "return arguments[0] + arguments[1]",
    10,
    20
)

# Set local storage
await page.execute_script(
    "localStorage.setItem(arguments[0], arguments[1])",
    "key",
    "value"
)

# Get local storage
value = await page.execute_script(
    "return localStorage.getItem(arguments[0])",
    "key"
)
```

**Parameters:**
- `script` (str): JavaScript code to execute
- `*args`: Arguments to pass to the JavaScript function

**Returns:**
- `Any`: Result of the JavaScript execution (serializable values only)

**Common Use Cases:**
- Manipulating the DOM directly
- Accessing browser APIs
- Scrolling to specific positions
- Getting/setting local storage
- Retrieving computed values

---

### Getters

#### `get_page()`
Get the underlying Playwright Page object for advanced operations.

```python
playwright_page = page.get_page()
await playwright_page.set_viewport_size({"width": 1920, "height": 1080})
```

---

#### `get_element_manager()`
Get the ElementManager instance for element interactions.

```python
element_manager = page.get_element_manager()
await element_manager.click("css=#button")
```

---

#### `get_config()`
Get the ConfigManager instance for configuration access.

```python
config = page.get_config()
timeout = config.get_timeout("element")
```

---

## Creating Custom Page Objects

### Basic Pattern

```python
from raptor.pages.base_page import BasePage

class HomePage(BasePage):
    def __init__(self, page, element_manager=None):
        super().__init__(page, element_manager)
        
        # Define locators
        self.search_box = "css=#search"
        self.search_button = "css=button[type='submit']"
        self.results = "css=.search-results"
    
    async def search(self, query: str):
        """Perform a search."""
        await self.element_manager.fill(self.search_box, query)
        await self.element_manager.click(self.search_button)
        await self.wait_for_load(state="networkidle")
    
    async def get_results_count(self) -> int:
        """Get the number of search results."""
        count = await self.execute_script(
            "return document.querySelectorAll(arguments[0]).length",
            ".result-item"
        )
        return count
```

### Advanced Pattern with Multiple Pages

```python
class DashboardPage(BasePage):
    def __init__(self, page, element_manager=None):
        super().__init__(page, element_manager)
        
        self.profile_menu = "css=#profile-menu"
        self.logout_button = "css=#logout"
    
    async def logout(self):
        """Logout and return to login page."""
        await self.element_manager.click(self.profile_menu)
        await self.element_manager.click(self.logout_button)
        await self.wait_for_load()
        
        # Return a new LoginPage instance
        from .login_page import LoginPage
        return LoginPage(self.page, self.element_manager)
```

---

## Configuration

### Default Timeouts

Timeouts are configured in `config/settings.yaml`:

```yaml
timeouts:
  page: 30000      # Page load timeout (ms)
  element: 20000   # Element interaction timeout (ms)
```

### Screenshot Directory

Configure screenshot directory in `config/settings.yaml`:

```yaml
screenshots:
  directory: "screenshots"
```

---

## Error Handling

### Common Exceptions

- **`TimeoutException`**: Navigation or wait operation times out
- **`RaptorException`**: General framework errors

### Example Error Handling

```python
from raptor.core.exceptions import TimeoutException, RaptorException

try:
    await page.navigate("https://example.com")
except TimeoutException as e:
    print(f"Navigation timeout: {e}")
    # Take screenshot for debugging
    await page.take_screenshot("navigation_timeout")
except RaptorException as e:
    print(f"Navigation failed: {e}")
```

---

## Best Practices

### 1. Use Descriptive Locators

```python
# Good
self.submit_button = "css=#submit-form-button"
self.username_input = "css=input[name='username']"

# Avoid
self.btn = "css=#btn1"
self.input = "css=input"
```

### 2. Wait for Page Load After Actions

```python
async def submit_form(self):
    await self.element_manager.click(self.submit_button)
    await self.wait_for_load(state="networkidle")  # Wait for page to settle
```

### 3. Take Screenshots on Failures

```python
async def verify_login_success(self):
    try:
        await self.element_manager.wait_for_element(self.dashboard_header)
    except Exception as e:
        await self.take_screenshot("login_failure")
        raise
```

### 4. Use JavaScript for Complex Operations

```python
async def scroll_to_element(self, locator: str):
    """Scroll element into view using JavaScript."""
    await self.execute_script(
        "document.querySelector(arguments[0]).scrollIntoView()",
        locator
    )
```

### 5. Return Page Objects for Navigation

```python
async def navigate_to_settings(self):
    """Navigate to settings page and return SettingsPage object."""
    await self.element_manager.click(self.settings_link)
    await self.wait_for_load()
    
    from .settings_page import SettingsPage
    return SettingsPage(self.page, self.element_manager)
```

---

## Complete Example

```python
from raptor.pages.base_page import BasePage
from raptor.core.exceptions import TimeoutException

class ProductPage(BasePage):
    def __init__(self, page, element_manager=None):
        super().__init__(page, element_manager)
        
        # Locators
        self.add_to_cart_button = "css=#add-to-cart"
        self.quantity_input = "css=input[name='quantity']"
        self.cart_icon = "css=#cart-icon"
        self.cart_count = "css=.cart-count"
    
    async def load_product(self, product_id: str):
        """Load a specific product page."""
        url = f"https://example.com/products/{product_id}"
        await self.navigate(url, wait_until="networkidle")
        
        # Verify page loaded correctly
        title = await self.get_title()
        if "Product" not in title:
            await self.take_screenshot("product_load_error")
            raise Exception(f"Failed to load product page: {title}")
    
    async def add_to_cart(self, quantity: int = 1):
        """Add product to cart with specified quantity."""
        # Set quantity
        await self.element_manager.fill(self.quantity_input, str(quantity))
        
        # Get cart count before adding
        cart_before = await self.execute_script(
            "return parseInt(document.querySelector(arguments[0]).textContent)",
            self.cart_count
        )
        
        # Add to cart
        await self.element_manager.click(self.add_to_cart_button)
        
        # Wait for cart to update
        await self.wait_for_load(state="networkidle")
        
        # Verify cart count increased
        cart_after = await self.execute_script(
            "return parseInt(document.querySelector(arguments[0]).textContent)",
            self.cart_count
        )
        
        assert cart_after == cart_before + quantity, "Cart count did not update correctly"
        
        # Take screenshot for documentation
        await self.take_screenshot(f"product_added_qty_{quantity}")
    
    async def get_product_price(self) -> float:
        """Get the product price using JavaScript."""
        price_text = await self.execute_script(
            "return document.querySelector('.product-price').textContent"
        )
        # Remove currency symbol and convert to float
        return float(price_text.replace("$", "").strip())
```

---

## See Also

- [Element Manager Documentation](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Browser Manager Documentation](BROWSER_MANAGER_IMPLEMENTATION.md)
- [Configuration Guide](CONFIG_MANAGER_IMPLEMENTATION.md)
