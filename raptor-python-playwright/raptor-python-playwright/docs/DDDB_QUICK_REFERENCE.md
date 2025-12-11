# DDDB Integration - Quick Reference

## Overview

Quick reference for DDDB (Data-Driven Database) operations in RAPTOR Python Playwright framework.

## Import Test Data

```python
# Basic import
data = db.import_data(
    table="TestData_Login",
    test_id=101,
    iteration=1,
    instance=1
)

# Access data fields
username = data['username']
password = data['password']
pk_id = data['pk_id']  # Primary key for updates
```

## Export Test Results

```python
# Update test result
db.export_data(
    table="TestData_Login",
    pk_id=12345,
    field="test_result",
    value="PASS"
)

# Update error message
db.export_data(
    table="TestData_Login",
    pk_id=12345,
    field="err_msg",
    value="Login successful"
)

# Update execution time
db.export_data(
    table="TestData_Login",
    pk_id=12345,
    field="execution_time",
    value=2.5
)
```

## Query Single Field

```python
# Get specific field value
username = db.get_field(
    table="TestData_Login",
    field="username",
    pk_id=12345
)
```

## Get Complete Row

```python
# Get all fields from row
row = db.get_row(
    table="TestData_Login",
    pk_id=12345
)

# Access fields
username = row['username']
password = row['password']
test_result = row['test_result']
```

## Multiple Iterations

```python
# Run test with multiple data sets
for iteration in range(1, 6):
    data = db.import_data(
        table="TestData_Login",
        test_id=101,
        iteration=iteration,
        instance=1
    )
    # Execute test with this data...
```

## Multiple Instances

```python
# Run parallel tests with different instances
for instance in range(1, 4):
    data = db.import_data(
        table="TestData_Login",
        test_id=101,
        iteration=1,
        instance=instance
    )
    # Execute test with this data...
```

## Additional Filters

```python
# Import with extra filter criteria
data = db.import_data(
    table="TestData_Login",
    test_id=101,
    iteration=1,
    instance=1,
    additional_filters={
        'environment': 'staging',
        'browser': 'chrome'
    }
)
```

## Complete Workflow

```python
from raptor.database import DatabaseManager
from raptor.core.exceptions import DatabaseException

def run_data_driven_test():
    with DatabaseManager(server="localhost", database="DDFE") as db:
        try:
            # 1. Import test data
            data = db.import_data(
                table="TestData_Login",
                test_id=101,
                iteration=1,
                instance=1
            )
            
            pk_id = data['pk_id']
            username = data['username']
            password = data['password']
            
            # 2. Execute test
            # (browser automation here)
            result = "PASS"
            message = "Login successful"
            
            # 3. Export results
            db.export_data(
                table="TestData_Login",
                pk_id=pk_id,
                field="test_result",
                value=result
            )
            
            db.export_data(
                table="TestData_Login",
                pk_id=pk_id,
                field="err_msg",
                value=message
            )
            
        except DatabaseException as e:
            # Handle database errors
            logger.error(f"Database error: {e}")
            
            # Export failure
            db.export_data(
                table="TestData_Login",
                pk_id=pk_id,
                field="test_result",
                value="FAIL"
            )
            db.export_data(
                table="TestData_Login",
                pk_id=pk_id,
                field="err_msg",
                value=str(e)
            )
```

## pytest Integration

```python
import pytest
from raptor.database import DatabaseManager

@pytest.fixture(scope="session")
def database():
    """Database connection fixture."""
    db = DatabaseManager(server="localhost", database="DDFE")
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture
def test_data(database, request):
    """Load test data for each test."""
    # Get test ID from test marker
    marker = request.node.get_closest_marker("test_id")
    test_id = marker.args[0] if marker else 101
    
    data = database.import_data(
        table="TestData_Login",
        test_id=test_id,
        iteration=1,
        instance=1
    )
    
    yield data
    
    # Export results after test
    result = "PASS" if not request.node.rep_call.failed else "FAIL"
    database.export_data(
        table="TestData_Login",
        pk_id=data['pk_id'],
        field="test_result",
        value=result
    )

@pytest.mark.test_id(101)
def test_login(database, test_data):
    """Test login with database data."""
    username = test_data['username']
    password = test_data['password']
    
    # Execute test...
    assert True  # Test logic here
```

## Error Handling

```python
from raptor.core.exceptions import DatabaseException

# Handle missing data
try:
    data = db.import_data(
        table="TestData_Login",
        test_id=999,
        iteration=1,
        instance=1
    )
except DatabaseException as e:
    logger.warning(f"No test data found: {e}")
    # Use defaults or skip test
    pytest.skip("No test data available")

# Handle export errors
try:
    db.export_data(
        table="TestData_Login",
        pk_id=12345,
        field="test_result",
        value="PASS"
    )
except DatabaseException as e:
    logger.error(f"Failed to export results: {e}")
    # Continue or raise based on requirements
```

## Common Patterns

### Pattern 1: Data-Driven Test Suite

```python
def test_suite_with_iterations():
    """Run test suite with multiple data iterations."""
    with DatabaseManager(server="localhost", database="DDFE") as db:
        test_id = 101
        
        for iteration in range(1, 11):  # 10 iterations
            data = db.import_data(
                table="TestData_Login",
                test_id=test_id,
                iteration=iteration,
                instance=1
            )
            
            # Execute test
            result = execute_test(data)
            
            # Export result
            db.export_data(
                table="TestData_Login",
                pk_id=data['pk_id'],
                field="test_result",
                value=result
            )
```

### Pattern 2: Parallel Test Execution

```python
import concurrent.futures

def run_parallel_tests():
    """Run tests in parallel with different instances."""
    with DatabaseManager(server="localhost", database="DDFE") as db:
        test_id = 101
        iteration = 1
        
        def run_test_instance(instance):
            data = db.import_data(
                table="TestData_Login",
                test_id=test_id,
                iteration=iteration,
                instance=instance
            )
            
            result = execute_test(data)
            
            db.export_data(
                table="TestData_Login",
                pk_id=data['pk_id'],
                field="test_result",
                value=result
            )
        
        # Run 5 instances in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(run_test_instance, range(1, 6))
```

### Pattern 3: Conditional Data Loading

```python
def load_test_data_conditionally():
    """Load different data based on conditions."""
    with DatabaseManager(server="localhost", database="DDFE") as db:
        # Try to load staging data first
        try:
            data = db.import_data(
                table="TestData_Login",
                test_id=101,
                iteration=1,
                instance=1,
                additional_filters={'environment': 'staging'}
            )
        except DatabaseException:
            # Fall back to dev data
            data = db.import_data(
                table="TestData_Login",
                test_id=101,
                iteration=1,
                instance=1,
                additional_filters={'environment': 'dev'}
            )
        
        return data
```

### Pattern 4: Incremental Result Updates

```python
def test_with_incremental_updates():
    """Update test results incrementally during execution."""
    with DatabaseManager(server="localhost", database="DDFE") as db:
        data = db.import_data(
            table="TestData_Login",
            test_id=101,
            iteration=1,
            instance=1
        )
        
        pk_id = data['pk_id']
        
        # Update status: In Progress
        db.export_data(
            table="TestData_Login",
            pk_id=pk_id,
            field="status",
            value="IN_PROGRESS"
        )
        
        # Execute test steps
        for step in test_steps:
            step_result = execute_step(step)
            
            # Update step result
            db.export_data(
                table="TestData_Login",
                pk_id=pk_id,
                field=f"step_{step}_result",
                value=step_result
            )
        
        # Update final status
        db.export_data(
            table="TestData_Login",
            pk_id=pk_id,
            field="status",
            value="COMPLETED"
        )
```

## Best Practices

1. **Always use context managers** for automatic connection cleanup
2. **Handle missing data gracefully** with try/except blocks
3. **Export results even on failure** to maintain test history
4. **Use parameterized queries** (handled automatically by methods)
5. **Enable connection pooling** for multiple operations
6. **Log all database operations** for debugging
7. **Validate data after import** before using in tests
8. **Use transactions** for multiple related updates

## Common Issues

### Issue: No data found
```python
# Problem: Test data doesn't exist
data = db.import_data(table="TestData", test_id=999, iteration=1, instance=1)
# Raises: DatabaseException

# Solution: Check if data exists first or handle exception
try:
    data = db.import_data(table="TestData", test_id=999, iteration=1, instance=1)
except DatabaseException:
    pytest.skip("Test data not available")
```

### Issue: Export fails silently
```python
# Problem: Exporting to wrong pk_id
db.export_data(table="TestData", pk_id=99999, field="result", value="PASS")
# Returns: 0 rows affected (no error)

# Solution: Check return value
rows = db.export_data(table="TestData", pk_id=pk_id, field="result", value="PASS")
if rows == 0:
    logger.warning(f"No rows updated for pk_id={pk_id}")
```

### Issue: Connection pool exhausted
```python
# Problem: Too many concurrent operations
# Solution: Increase pool size
db = DatabaseManager(
    server="localhost",
    database="DDFE",
    use_pooling=True,
    pool_max_size=20  # Increased from default 10
)
```

## See Also

- [Database Manager Implementation Guide](DATABASE_MANAGER_IMPLEMENTATION.md)
- [Task 11 Completion Summary](TASK_11_COMPLETION_SUMMARY.md)
- [Database Examples](../examples/database_example.py)
- [Requirements Document](../../.kiro/specs/raptor-playwright-python/requirements.md)
