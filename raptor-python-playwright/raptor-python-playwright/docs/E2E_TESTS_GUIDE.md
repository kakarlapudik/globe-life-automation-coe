# End-to-End Test Suite Guide

## Overview

The RAPTOR framework includes a comprehensive End-to-End (E2E) test suite that validates complete workflows from start to finish. These tests ensure that all components work together correctly in real-world scenarios.

**Location**: `tests/test_e2e.py`

**Validates**: Requirements NFR-002 (Reliability), NFR-003 (Maintainability)

## Test Categories

### 1. Complete Login Workflow (`TestE2ELoginWorkflow`)

Tests the entire authentication process including session management.

#### Test: `test_complete_login_workflow_with_session_persistence`

**Covers**:
1. Browser initialization
2. Navigation to login page
3. Form filling and submission
4. Authentication verification
5. Session saving
6. Session restoration
7. Verification of persisted state

**Key Features**:
- Tests "Remember Me" functionality
- Validates session persistence across browser instances
- Verifies user state after session restoration
- Captures screenshots for documentation

#### Test: `test_login_with_error_handling_and_retry`

**Covers**:
1. Invalid login attempt
2. Error message verification
3. Retry with correct credentials
4. Successful authentication

**Key Features**:
- Tests error handling
- Validates retry logic
- Verifies error messages are displayed correctly

### 2. Data-Driven Execution (`TestE2EDataDrivenExecution`)

Tests complete data-driven workflows with database integration.

#### Test: `test_complete_data_driven_workflow`

**Covers**:
1. Loading test data from database
2. Executing tests with multiple iterations
3. Exporting results back to database
4. Verifying data persistence

**Key Features**:
- Tests database integration
- Validates data-driven test execution
- Verifies result export functionality
- Tests multiple iterations with different data sets

**Database Schema**:
```sql
CREATE TABLE UserTestData (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER,
    iteration INTEGER,
    instance INTEGER,
    username TEXT,
    email TEXT,
    password TEXT,
    expected_result TEXT,
    test_result TEXT,
    result_message TEXT
)
```

### 3. Multi-Page Navigation (`TestE2EMultiPageNavigation`)

Tests complex user journeys across multiple pages.

#### Test: `test_complete_multi_page_shopping_workflow`

**Covers**:
1. Login page
2. Product browsing page
3. Product details page
4. Shopping cart page
5. Checkout page
6. Order confirmation page
7. Order history page

**Key Features**:
- Tests state management across pages
- Validates navigation flow
- Verifies data persistence between pages
- Tests complete e-commerce workflow

**Workflow Steps**:
```
Login → Browse Products → View Details → Add to Cart → 
View Cart → Checkout → Confirm Order → View History
```

### 4. Table Operations (`TestE2ETableOperations`)

Tests complete table management workflows.

#### Test: `test_complete_table_management_workflow`

**Covers**:
1. Table data loading and display
2. Searching for specific rows
3. Reading cell values
4. Editing cell values
5. Sorting table data
6. Pagination navigation
7. Bulk operations

**Key Features**:
- Tests table search functionality
- Validates cell editing
- Tests sorting mechanisms
- Verifies bulk operations
- Tests pagination

## Running E2E Tests

### Prerequisites

1. **Install Playwright Browsers**:
   ```bash
   playwright install chromium
   ```

2. **Database Setup** (for data-driven tests):
   - SQLite database is created automatically for tests
   - No additional setup required

### Run All E2E Tests

```bash
pytest tests/test_e2e.py -v
```

### Run Specific Test Class

```bash
# Login workflow tests
pytest tests/test_e2e.py::TestE2ELoginWorkflow -v

# Data-driven tests
pytest tests/test_e2e.py::TestE2EDataDrivenExecution -v

# Multi-page navigation tests
pytest tests/test_e2e.py::TestE2EMultiPageNavigation -v

# Table operations tests
pytest tests/test_e2e.py::TestE2ETableOperations -v
```

### Run Specific Test

```bash
pytest tests/test_e2e.py::TestE2ELoginWorkflow::test_complete_login_workflow_with_session_persistence -v
```

### Run with Detailed Output

```bash
pytest tests/test_e2e.py -v -s --tb=short
```

## Test Reports

E2E tests generate HTML reports in the `reports/e2e` directory.

**Report Contents**:
- Test execution summary
- Step-by-step logs
- Screenshots at key points
- Execution duration
- Pass/fail statistics

**Accessing Reports**:
```bash
# Reports are saved to:
reports/e2e/test_report_<timestamp>.html
```

## Screenshots

E2E tests capture screenshots at critical points:

- `e2e_login_success.png` - After successful login
- `e2e_data_driven_iteration_<N>.png` - Each data-driven iteration
- `e2e_order_confirmation.png` - Order confirmation page
- `e2e_table_operations_complete.png` - After table operations

**Screenshot Location**: `screenshots/`

## Test Data

### Login Test Data

```python
# Valid credentials
username: "testuser"
password: "TestPass123!"

# Invalid credentials (for error testing)
username: "wronguser"
password: "wrongpass"
```

### Data-Driven Test Data

Test data is loaded from database with multiple iterations:

```python
# Iteration 1: Valid user
username: "user1"
email: "user1@example.com"
expected_result: "success"

# Iteration 2: Valid user
username: "user2"
email: "user2@example.com"
expected_result: "success"

# Iteration 3: Invalid user
username: "invalid"
email: "invalid@example.com"
expected_result: "failure"
```

### Table Test Data

Sample user table with 5 users:
- Alice Johnson (Admin, Active)
- Bob Smith (User, Active)
- Charlie Brown (Manager, Inactive)
- Diana Prince (User, Active)
- Eve Wilson (Manager, Inactive)

## Best Practices

### 1. Test Isolation

Each E2E test should be independent:
```python
@pytest.mark.asyncio
async def test_example(self):
    # Setup
    browser_manager = BrowserManager(config)
    
    try:
        # Test logic
        pass
    finally:
        # Cleanup
        await browser_manager.close_browser()
```

### 2. Use Reporters

Generate reports for better visibility:
```python
reporter = TestReporter("reports/e2e")
reporter.start_test("Test Name")
reporter.log_step("Step description")
reporter.end_test("PASS")
report_path = await reporter.generate_html_report()
```

### 3. Take Screenshots

Capture screenshots at key points:
```python
await base_page.take_screenshot("descriptive_name")
```

### 4. Verify State

Always verify state after actions:
```python
# After login
assert await element_manager.is_visible("css=.welcome-message")
welcome_text = await element_manager.get_text("css=.welcome-message")
assert "Welcome" in welcome_text
```

### 5. Handle Async Operations

Use appropriate waits:
```python
# Wait for element
await element_manager.wait_for_element("css=#result", timeout=5000)

# Wait for DOM updates
await asyncio.sleep(0.1)

# Wait for navigation
await page.wait_for_url("**/dashboard", timeout=10000)
```

## Troubleshooting

### Browser Not Found

**Error**: `Executable doesn't exist at ...`

**Solution**:
```bash
playwright install chromium
```

### Database Connection Issues

**Error**: `Data source name not found`

**Solution**: E2E tests use SQLite which doesn't require ODBC. The fixture creates a temporary database automatically.

### Test Timeout

**Error**: `TimeoutException`

**Solution**: Increase timeout in test:
```python
await element_manager.wait_for_element("css=#slow-element", timeout=30000)
```

### Session Not Found

**Error**: `SessionException: Session not found`

**Solution**: Ensure session is saved before attempting to restore:
```python
# Save session
await session_manager.save_session(page, "session_name")

# Verify session exists
assert "session_name" in session_manager.list_sessions()

# Then restore
restored_page = await session_manager.restore_session("session_name")
```

## Performance Considerations

### Test Execution Time

- Login workflow: ~2-3 seconds
- Data-driven (3 iterations): ~5-7 seconds
- Multi-page navigation: ~8-10 seconds
- Table operations: ~5-6 seconds

**Total E2E Suite**: ~20-25 seconds

### Optimization Tips

1. **Reuse Browser Instances**: When possible, reuse browser instances across tests
2. **Parallel Execution**: Run test classes in parallel with pytest-xdist
3. **Headless Mode**: Always use headless mode for CI/CD
4. **Minimize Waits**: Use explicit waits only when necessary

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install chromium
      
      - name: Run E2E tests
        run: pytest tests/test_e2e.py -v --html=report.html
      
      - name: Upload test report
        uses: actions/upload-artifact@v2
        if: always()
        with:
          name: e2e-test-report
          path: report.html
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'playwright install chromium'
            }
        }
        
        stage('E2E Tests') {
            steps {
                sh 'pytest tests/test_e2e.py -v --junitxml=results.xml'
            }
        }
    }
    
    post {
        always {
            junit 'results.xml'
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
        }
    }
}
```

## Related Documentation

- [Integration Tests Guide](INTEGRATION_TESTS_QUICK_REFERENCE.md)
- [Test Reporter Guide](TEST_REPORTER_GUIDE.md)
- [Session Manager Guide](SESSION_MANAGER_IMPLEMENTATION.md)
- [Database Manager Guide](DATABASE_MANAGER_IMPLEMENTATION.md)
- [Table Manager Guide](TABLE_MANAGER_GUIDE.md)

## Summary

The E2E test suite provides comprehensive coverage of real-world workflows:

✅ **Complete Login Workflow** - Authentication and session management  
✅ **Data-Driven Execution** - Database integration and multiple iterations  
✅ **Multi-Page Navigation** - Complex user journeys across pages  
✅ **Table Operations** - Complete table management workflows  

These tests ensure the RAPTOR framework works correctly in production scenarios and meets the reliability requirements (NFR-002) and maintainability requirements (NFR-003).
