

# Data-Driven Testing Guide

## Overview

The RAPTOR framework provides comprehensive support for data-driven testing using DDDB (Data-Driven Database). This guide explains how to load test data from the database and use it with pytest parametrization.

## Table of Contents

1. [Introduction](#introduction)
2. [Core Concepts](#core-concepts)
3. [Loading Test Data](#loading-test-data)
4. [Pytest Parametrization](#pytest-parametrization)
5. [Iteration-Based Testing](#iteration-based-testing)
6. [Instance-Based Testing](#instance-based-testing)
7. [Exporting Results](#exporting-results)
8. [Advanced Usage](#advanced-usage)
9. [Best Practices](#best-practices)

## Introduction

Data-driven testing allows you to run the same test logic with multiple sets of input data. The RAPTOR framework integrates with DDDB to provide:

- **Automatic data loading** from database tables
- **pytest parametrization** decorators for easy test setup
- **Iteration and instance support** for hierarchical test data
- **Result export** back to the database
- **Flexible filtering** and data manipulation

## Core Concepts

### Test Data Structure

DDDB test data follows a hierarchical structure:

```
Test ID
  └── Iteration (major scenario)
      └── Instance (variation within scenario)
          └── Data Fields (username, password, etc.)
```

**Example:**
- Test ID 101: Login Tests
  - Iteration 1: Valid Credentials
    - Instance 1: Admin user
    - Instance 2: Regular user
  - Iteration 2: Invalid Credentials
    - Instance 1: Wrong password
    - Instance 2: Non-existent user

### Data Classes

#### TestDataRow

Represents a single row of test data:

```python
@dataclass
class TestDataRow:
    pk_id: int              # Primary key
    test_id: int            # Test identifier
    iteration: int          # Iteration number
    instance: int           # Instance number
    fk_id: Optional[int]    # Foreign key (optional)
    action: Optional[str]   # Action to perform
    err_msg: Optional[str]  # Expected error message
    data: Dict[str, Any]    # All field values
```

#### TestDataSet

Represents a complete set of test data:

```python
@dataclass
class TestDataSet:
    test_id: int                    # Test identifier
    table_name: str                 # Source table
    rows: List[TestDataRow]         # All data rows
    total_iterations: int           # Number of iterations
    total_instances: int            # Max instances per iteration
```

## Loading Test Data

### Basic Loading

```python
from raptor.database.database_manager import DatabaseManager
from raptor.utils.data_driven import DataDrivenTestLoader

# Initialize database
db = DatabaseManager(
    server="localhost",
    database="DDDB",
    user="testuser",
    password="testpass"
)

# Create loader
loader = DataDrivenTestLoader(db)

# Load all test data for test_id 101
data_set = loader.load_test_data(
    table="TestData_Login",
    test_id=101
)

# Access the data
for row in data_set.rows:
    username = row['username']
    password = row['password']
    print(f"Testing {username}")
```

### Loading Specific Iterations

```python
# Load only iterations 1 and 2
data_set = loader.load_test_data(
    table="TestData_Login",
    test_id=101,
    iterations=[1, 2]
)
```

### Loading Specific Instances

```python
# Load only instances 1 and 3
data_set = loader.load_test_data(
    table="TestData_Login",
    test_id=101,
    instances=[1, 3]
)
```

### Loading by Iteration

```python
# Load all instances for iteration 1
iteration_data = loader.load_by_iteration(
    table="TestData_Login",
    test_id=101,
    iteration=1
)
```

### Loading by Instance

```python
# Load a specific instance
row = loader.load_by_instance(
    table="TestData_Login",
    test_id=101,
    iteration=1,
    instance=1
)

if row:
    username = row['username']
    password = row['password']
```

## Pytest Parametrization

### Using the Decorator

The simplest way to parametrize tests with DDDB data:

```python
from raptor.utils.data_driven import parametrize_from_dddb

@parametrize_from_dddb(
    table="TestData_Login",
    test_id=101,
    database=database  # From fixture
)
def test_login(test_data):
    """Test runs once for each row in DDDB."""
    username = test_data['username']
    password = test_data['password']
    expected = test_data['expected_result']
    
    # Perform login
    result = perform_login(username, password)
    
    # Verify result
    assert result == expected
```

### Custom Test IDs

Generate meaningful test IDs:

```python
def custom_id(row):
    return f"{row['username']}_iter{row.iteration}"

@parametrize_from_dddb(
    table="TestData_Login",
    test_id=101,
    database=database,
    id_func=custom_id
)
def test_login(test_data):
    # Test code...
    pass
```

### Manual Parametrization

For more control:

```python
from raptor.utils.data_driven import get_test_data_params

def test_login_manual(database):
    # Get test data and IDs
    test_data, test_ids = get_test_data_params(
        database,
        table="TestData_Login",
        test_id=101,
        iterations=[1, 2]
    )
    
    # Use with pytest.mark.parametrize
    @pytest.mark.parametrize("data", test_data, ids=test_ids)
    def inner_test(data):
        username = data['username']
        # Test code...
    
    # Run tests
    for data in test_data:
        inner_test(data)
```

## Iteration-Based Testing

Run tests once per iteration, receiving all instances:

```python
from raptor.utils.data_driven import parametrize_iterations

@parametrize_iterations(
    table="TestData_Login",
    test_id=101,
    database=database
)
def test_login_workflow(iteration_data):
    """
    Test runs once per iteration.
    iteration_data is a list of all instances for that iteration.
    """
    print(f"Testing with {len(iteration_data)} instances")
    
    for instance in iteration_data:
        username = instance['username']
        password = instance['password']
        
        # Perform test for this instance
        result = perform_login(username, password)
        
        # Verify result
        assert result is not None
```

### Use Cases for Iteration-Based Testing

- **Multi-step workflows**: Each instance represents a step
- **Related test scenarios**: Test variations of the same scenario
- **Setup/teardown dependencies**: Share setup across instances

## Instance-Based Testing

Run tests for instances within a specific iteration:

```python
from raptor.utils.data_driven import parametrize_instances

@parametrize_instances(
    table="TestData_Login",
    test_id=101,
    iteration=1,  # Test only iteration 1
    database=database
)
def test_valid_logins(instance_data):
    """
    Test runs once per instance in iteration 1.
    Useful for testing a specific scenario with variations.
    """
    username = instance_data['username']
    password = instance_data['password']
    
    result = perform_login(username, password)
    assert result == "success"
```

### Specifying Instances

```python
@parametrize_instances(
    table="TestData_Login",
    test_id=101,
    iteration=1,
    instances=[1, 3, 5],  # Test only specific instances
    database=database
)
def test_specific_instances(instance_data):
    # Test code...
    pass
```

## Exporting Results

Export test results back to DDDB:

```python
from raptor.utils.data_driven import export_test_result

@parametrize_from_dddb(
    table="TestData_Login",
    test_id=101,
    database=database
)
def test_login_with_export(test_data, database):
    username = test_data['username']
    password = test_data['password']
    
    try:
        # Perform test
        result = perform_login(username, password)
        
        # Export success
        export_test_result(database, test_data, "PASS")
        
    except Exception as e:
        # Export failure with error message
        export_test_result(database, test_data, "FAIL", str(e))
        raise
```

## Advanced Usage

### Using Fixtures

Create reusable fixtures for test data:

```python
from raptor.utils.data_driven import load_test_data_for_fixture

@pytest.fixture
def login_test_data(database):
    """Fixture that loads test data once."""
    return load_test_data_for_fixture(
        database,
        table="TestData_Login",
        test_id=101
    )

def test_with_fixture(login_test_data):
    """Use the fixture in multiple tests."""
    for row in login_test_data.rows:
        username = row['username']
        # Test code...
```

### Filtering Test Data

Filter data before running tests:

```python
from raptor.utils.data_driven import filter_test_data

def test_with_filtering(database):
    # Load all data
    loader = DataDrivenTestLoader(database)
    data_set = loader.load_test_data("TestData_Login", test_id=101)
    
    # Filter for successful scenarios only
    success_data = filter_test_data(
        data_set,
        lambda row: row.get('expected_result') == 'success'
    )
    
    # Run tests with filtered data
    for row in success_data.rows:
        # Test code...
        pass
```

### Merging Test Data

Combine data from multiple sources:

```python
from raptor.utils.data_driven import merge_test_data

# Load data from different test IDs
data1 = loader.load_test_data("TestData_Login", test_id=101)
data2 = loader.load_test_data("TestData_Login", test_id=102)

# Merge into single data set
merged = merge_test_data(data1, data2)

# Run tests with merged data
for row in merged.rows:
    # Test code...
    pass
```

### Accessing Data Fields

Multiple ways to access test data:

```python
# Dictionary-style access
username = row['username']

# Get method with default
email = row.get('email', 'default@example.com')

# Direct attribute access for standard fields
pk_id = row.pk_id
test_id = row.test_id
iteration = row.iteration
instance = row.instance
```

### Working with Hierarchical Data

```python
def test_hierarchical_data(database):
    loader = DataDrivenTestLoader(database)
    data_set = loader.load_test_data("TestData_Login", test_id=101)
    
    # Process by iteration
    for iteration_num in data_set.get_iterations():
        print(f"Testing Iteration {iteration_num}")
        
        # Get all instances for this iteration
        iteration_rows = data_set.get_by_iteration(iteration_num)
        
        for row in iteration_rows:
            print(f"  Instance {row.instance}")
            # Test code...
```

## Best Practices

### 1. Use Descriptive Test IDs

```python
# Good: Meaningful test IDs
def custom_id(row):
    return f"{row['username']}_{row['expected_result']}"

# Bad: Generic IDs
# Uses default: iter1_inst1, iter2_inst1, etc.
```

### 2. Export Results for Tracking

```python
# Always export results for audit trail
try:
    # Test code...
    export_test_result(database, test_data, "PASS")
except Exception as e:
    export_test_result(database, test_data, "FAIL", str(e))
    raise
```

### 3. Use Fixtures for Shared Data

```python
# Good: Load data once in fixture
@pytest.fixture(scope="module")
def test_data(database):
    return load_test_data_for_fixture(database, "TestData", 101)

# Bad: Load data in every test
def test_1(database):
    data = load_test_data_for_fixture(database, "TestData", 101)
    # ...

def test_2(database):
    data = load_test_data_for_fixture(database, "TestData", 101)
    # ...
```

### 4. Filter Data for Specific Scenarios

```python
# Good: Filter for relevant data
success_data = filter_test_data(
    data_set,
    lambda row: row.get('expected_result') == 'success'
)

# Bad: Check condition in every test iteration
for row in data_set.rows:
    if row.get('expected_result') == 'success':
        # Test code...
```

### 5. Use Iterations for Related Tests

```python
# Good: Group related scenarios in iterations
# Iteration 1: Valid credentials
# Iteration 2: Invalid credentials
# Iteration 3: Edge cases

@parametrize_iterations(table="TestData", test_id=101, database=db)
def test_login_scenarios(iteration_data):
    # Test all instances in the iteration together
    pass

# Bad: Mix unrelated scenarios in same iteration
```

### 6. Handle Missing Data Gracefully

```python
# Good: Check for None and provide defaults
email = row.get('email', 'default@example.com')
phone = row.get('phone')
if phone:
    # Use phone...

# Bad: Assume all fields exist
email = row['email']  # May raise KeyError
```

### 7. Use Meaningful Field Names in DDDB

```python
# Good: Clear field names
username = row['username']
password = row['password']
expected_result = row['expected_result']

# Bad: Generic field names
field1 = row['field1']
field2 = row['field2']
```

## Common Patterns

### Pattern 1: Simple Parametrization

```python
@parametrize_from_dddb("TestData_Login", test_id=101, database=db)
def test_login(test_data):
    result = perform_login(test_data['username'], test_data['password'])
    assert result == test_data['expected_result']
```

### Pattern 2: Multi-Step Workflow

```python
@parametrize_iterations("TestData_Workflow", test_id=201, database=db)
def test_workflow(iteration_data):
    # Each instance is a step in the workflow
    for step in iteration_data:
        action = step['action']
        if action == 'login':
            perform_login(step['username'], step['password'])
        elif action == 'navigate':
            navigate_to(step['url'])
        elif action == 'verify':
            verify_element(step['element'])
```

### Pattern 3: Data Setup and Cleanup

```python
@parametrize_from_dddb("TestData_CRUD", test_id=301, database=db)
def test_crud_operations(test_data, database):
    try:
        # Setup
        entity = create_entity(test_data)
        
        # Test
        result = perform_operation(entity, test_data['operation'])
        assert result == test_data['expected']
        
        # Export success
        export_test_result(database, test_data, "PASS")
        
    finally:
        # Cleanup
        cleanup_entity(entity)
```

### Pattern 4: Conditional Testing

```python
@parametrize_from_dddb("TestData_Login", test_id=101, database=db)
def test_conditional(test_data):
    if test_data.get('skip_reason'):
        pytest.skip(test_data['skip_reason'])
    
    # Perform test
    result = perform_login(test_data['username'], test_data['password'])
    assert result == test_data['expected_result']
```

## Troubleshooting

### Issue: No test data found

**Problem:** `load_test_data()` returns empty data set

**Solutions:**
1. Verify test_id exists in the database
2. Check table name is correct
3. Verify database connection is working
4. Check iteration/instance filters aren't too restrictive

### Issue: KeyError when accessing fields

**Problem:** `row['field_name']` raises KeyError

**Solutions:**
1. Use `row.get('field_name', default)` instead
2. Verify field name matches database column
3. Check if field is NULL in database

### Issue: Tests not parametrized

**Problem:** Decorator doesn't parametrize the test

**Solutions:**
1. Ensure database fixture is properly configured
2. Check that test data exists for the test_id
3. Verify decorator is applied before other decorators

### Issue: Export fails

**Problem:** `export_test_result()` raises exception

**Solutions:**
1. Verify pk_id is valid
2. Check database connection is still active
3. Ensure table name is correct
4. Verify field names exist in the table

## See Also

- [Database Manager Guide](DATABASE_MANAGER_IMPLEMENTATION.md)
- [pytest Fixtures Guide](PYTEST_FIXTURES_GUIDE.md)
- [Test Execution Control](TEST_EXECUTION_CONTROL_GUIDE.md)
- [Examples](../examples/data_driven_example.py)
