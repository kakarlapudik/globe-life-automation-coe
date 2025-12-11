# RAPTOR Framework - Example Tests

This directory contains comprehensive example tests demonstrating real-world usage of the RAPTOR Python Playwright framework. These examples are fully functional pytest tests that you can run, study, and adapt for your own test automation needs.

## Overview

The example tests cover five major categories:

1. **Login Tests** - Authentication workflows
2. **Data-Driven Tests** - Database-driven test execution
3. **Table Interaction Tests** - Working with data tables
4. **Multi-Page Workflow Tests** - Complex user journeys
5. **Session Reuse Tests** - Session management and optimization

## Example Test Files

### 1. test_example_login.py

**Purpose**: Demonstrates complete login workflows and authentication testing.

**Key Features**:
- Basic login with valid credentials
- Login failure with invalid credentials
- "Remember Me" functionality
- Keyboard navigation for accessibility
- Session saving after login

**Run Command**:
```bash
pytest examples/test_example_login.py -v
```

**What You'll Learn**:
- Browser initialization and management
- Form filling and submission
- Element verification
- Cookie and session handling
- Screenshot capture for documentation

---

### 2. test_example_data_driven.py

**Purpose**: Shows how to implement data-driven testing using DDDB (Data-Driven Database).

**Key Features**:
- Loading test data from database
- Running multiple iterations with different data
- Parametrized tests with pytest
- Exporting results back to database
- Complex workflows with related data tables

**Run Command**:
```bash
pytest examples/test_example_data_driven.py -v
```

**What You'll Learn**:
- Database connection and queries
- Test data import/export
- Iteration-based testing
- Foreign key relationships
- Result tracking in database

**Prerequisites**:
- Database connection configured in settings
- Test data tables created in DDDB

---

### 3. test_example_table_interaction.py

**Purpose**: Demonstrates comprehensive table operations and data manipulation.

**Key Features**:
- Finding rows by key values
- Reading and writing cell data
- Searching tables with various criteria
- Pagination handling
- Bulk operations on table data
- Sorting and filtering

**Run Command**:
```bash
pytest examples/test_example_table_interaction.py -v
```

**What You'll Learn**:
- Table row location strategies
- Cell value extraction
- In-place editing
- Multi-page table navigation
- Batch operations
- Table state verification

---

### 4. test_example_multi_page_workflow.py

**Purpose**: Shows complex multi-page workflows and end-to-end user journeys.

**Key Features**:
- Complete e-commerce purchase flow (10 steps)
- User profile management across pages
- Admin user management workflow
- State maintenance between pages
- Test reporting integration

**Run Command**:
```bash
pytest examples/test_example_multi_page_workflow.py -v
```

**What You'll Learn**:
- Multi-step workflow orchestration
- Page-to-page navigation
- Shopping cart operations
- Checkout process automation
- Admin panel interactions
- End-to-end verification

---

### 5. test_example_session_reuse.py

**Purpose**: Demonstrates session management and reuse for test optimization.

**Key Features**:
- Creating and saving sessions
- Restoring saved sessions
- Managing multiple user sessions
- Session expiration handling
- Performance comparison with/without session reuse

**Run Command**:
```bash
pytest examples/test_example_session_reuse.py -v
```

**What You'll Learn**:
- Session lifecycle management
- Authentication state persistence
- Multi-user session handling
- Session cleanup strategies
- Performance optimization techniques

**Performance Benefits**:
- 50-70% faster test execution
- Reduced server load
- Improved test stability

---

## Running the Examples

### Run All Examples

```bash
pytest examples/test_example_*.py -v
```

### Run Specific Example

```bash
pytest examples/test_example_login.py -v
```

### Run with Output

```bash
pytest examples/test_example_login.py -v -s
```

### Run Specific Test

```bash
pytest examples/test_example_login.py::TestLoginExample::test_successful_login -v
```

### Run in Headed Mode (See Browser)

Modify the test to set `headless=False`:
```python
browser = await browser_manager.launch_browser("chromium", headless=False)
```

## Configuration

### Prerequisites

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
playwright install
```

2. **Configure Settings**:
Edit `raptor/config/settings.yaml` with your environment settings:
```yaml
browser:
  default_browser: "chromium"
  headless: true
  timeout: 20000

database:
  connection_string: "your_connection_string"
  user: "your_username"
  password: "your_password"
```

3. **Set Up Test Environment**:
- Ensure test application is accessible
- Database is configured (for data-driven tests)
- Test data is loaded (for data-driven tests)

## Adapting Examples for Your Tests

### Step 1: Copy Example

```bash
cp examples/test_example_login.py tests/test_my_login.py
```

### Step 2: Modify URLs

Replace example URLs with your application URLs:
```python
await base_page.navigate("https://your-app.com/login")
```

### Step 3: Update Locators

Replace CSS selectors with your application's locators:
```python
await element_manager.fill("css=#your-username-field", "user@example.com")
```

### Step 4: Adjust Assertions

Modify assertions to match your application's behavior:
```python
assert "Your Welcome Message" in welcome_text
```

## Best Practices Demonstrated

### 1. Resource Management
```python
try:
    # Test code
finally:
    await browser_manager.close_browser()
```

### 2. Explicit Waits
```python
await element_manager.wait_for_element("css=#element", timeout=10000)
await page.wait_for_url("**/dashboard", timeout=10000)
```

### 3. Error Handling
```python
try:
    await element_manager.click("css=#button")
except Exception as e:
    print(f"Click failed: {e}")
    await base_page.take_screenshot("error_state")
    raise
```

### 4. Verification
```python
assert await element_manager.is_visible("css=.success-message")
success_text = await element_manager.get_text("css=.success-message")
assert "success" in success_text.lower()
```

### 5. Documentation
```python
"""
Test successful login with valid credentials

This example shows:
1. Browser initialization
2. Form filling
3. Verification
"""
```

## Common Patterns

### Pattern 1: Login and Navigate
```python
# Login
await base_page.navigate("https://example.com/login")
await element_manager.fill("css=#username", "user@example.com")
await element_manager.fill("css=#password", "password")
await element_manager.click("css=#login-button")
await page.wait_for_url("**/dashboard", timeout=10000)

# Navigate to target page
await base_page.navigate("https://example.com/target-page")
```

### Pattern 2: Form Filling
```python
# Fill all fields
await element_manager.fill("css=#field1", "value1")
await element_manager.fill("css=#field2", "value2")
await element_manager.select_option("css=#dropdown", "option1")
await element_manager.click("css=#checkbox")

# Submit
await element_manager.click("css=#submit-button")
```

### Pattern 3: Table Operations
```python
# Find row
row_index = await table_manager.find_row_by_key(
    table_locator="css=#table",
    key_column=0,
    key_value="search_value"
)

# Read data
cell_value = await table_manager.get_cell_value("css=#table", row_index, 1)

# Edit data
await table_manager.set_cell_value("css=#table", row_index, 1, "new_value")
```

### Pattern 4: Session Reuse
```python
# First test - create session
await session_manager.save_session(page, "my_session")

# Later tests - reuse session
page = await session_manager.restore_session("my_session")
```

## Troubleshooting

### Issue: Tests Fail with Timeout

**Solution**: Increase timeout values
```python
config.set("browser.timeout", 30000)  # 30 seconds
```

### Issue: Elements Not Found

**Solution**: Verify locators and add explicit waits
```python
await element_manager.wait_for_element("css=#element", timeout=10000)
```

### Issue: Database Connection Fails

**Solution**: Check connection string and credentials
```python
# Verify in settings.yaml
database:
  connection_string: "correct_connection_string"
```

### Issue: Session Restoration Fails

**Solution**: Check session expiration and recreate
```python
try:
    page = await session_manager.restore_session("session_name")
except Exception:
    # Create new session
    # ... login code ...
    await session_manager.save_session(page, "session_name")
```

## Performance Tips

1. **Use Session Reuse**: Save 50-70% execution time
2. **Run Tests in Parallel**: Use pytest-xdist
   ```bash
   pytest examples/ -n 4
   ```
3. **Use Headless Mode**: Faster execution
4. **Minimize Waits**: Use explicit waits only when needed
5. **Reuse Browser Contexts**: When possible

## Additional Resources

- **API Documentation**: `docs/API_REFERENCE_GUIDE.md`
- **User Guide**: `docs/USER_GUIDE_QUICK_REFERENCE.md`
- **Migration Guide**: `docs/MIGRATION_GUIDE_COMPREHENSIVE.md`
- **Troubleshooting**: `docs/TROUBLESHOOTING_GUIDE.md`

## Contributing Examples

If you create useful examples, consider contributing them:

1. Follow the existing example format
2. Include comprehensive docstrings
3. Add comments explaining key concepts
4. Test thoroughly
5. Update this README

## Support

For questions or issues with examples:
- Check the documentation in `docs/`
- Review the API reference
- Consult the troubleshooting guide
- Contact the RAPTOR team

---

**Note**: These examples use placeholder URLs (`https://example.com`). Replace them with your actual application URLs when adapting for your tests.

**Requirements**: NFR-004 - Usability and Documentation
