# Data-Driven Testing Quick Reference

## Import Statements

```python
from raptor.database.database_manager import DatabaseManager
from raptor.utils.data_driven import (
    DataDrivenTestLoader,
    TestDataRow,
    TestDataSet,
    parametrize_from_dddb,
    parametrize_iterations,
    parametrize_instances,
    load_test_data_for_fixture,
    get_test_data_params,
    export_test_result,
    filter_test_data,
    merge_test_data
)
```

## Quick Start

### 1. Load Test Data

```python
# Initialize
db = DatabaseManager(server="localhost", database="DDDB", user="user", password="pass")
loader = DataDrivenTestLoader(db)

# Load all data
data_set = loader.load_test_data("TestData_Login", test_id=101)

# Load specific iterations
data_set = loader.load_test_data("TestData_Login", test_id=101, iterations=[1, 2])

# Load specific instances
data_set = loader.load_test_data("TestData_Login", test_id=101, instances=[1, 3])
```

### 2. Parametrize Tests

```python
# Simple parametrization
@parametrize_from_dddb("TestData_Login", test_id=101, database=db)
def test_login(test_data):
    username = test_data['username']
    password = test_data['password']
    # Test code...

# By iterations
@parametrize_iterations("TestData_Login", test_id=101, database=db)
def test_by_iteration(iteration_data):
    for instance in iteration_data:
        # Test code...

# By instances
@parametrize_instances("TestData_Login", test_id=101, iteration=1, database=db)
def test_by_instance(instance_data):
    # Test code...
```

### 3. Access Data

```python
# Dictionary access
username = row['username']

# Get with default
email = row.get('email', 'default@example.com')

# Standard fields
pk_id = row.pk_id
test_id = row.test_id
iteration = row.iteration
instance = row.instance
```

### 4. Export Results

```python
# Export success
export_test_result(database, test_data, "PASS")

# Export failure with message
export_test_result(database, test_data, "FAIL", "Login failed")
```

## Common Patterns

### Pattern: Simple Test

```python
@parametrize_from_dddb("TestData_Login", test_id=101, database=db)
def test_login(test_data):
    result = login(test_data['username'], test_data['password'])
    assert result == test_data['expected']
```

### Pattern: With Result Export

```python
@parametrize_from_dddb("TestData_Login", test_id=101, database=db)
def test_login(test_data, database):
    try:
        result = login(test_data['username'], test_data['password'])
        assert result == test_data['expected']
        export_test_result(database, test_data, "PASS")
    except Exception as e:
        export_test_result(database, test_data, "FAIL", str(e))
        raise
```

### Pattern: Multi-Step Workflow

```python
@parametrize_iterations("TestData_Workflow", test_id=201, database=db)
def test_workflow(iteration_data):
    for step in iteration_data:
        if step['action'] == 'login':
            login(step['username'], step['password'])
        elif step['action'] == 'navigate':
            navigate(step['url'])
```

### Pattern: Using Fixture

```python
@pytest.fixture
def test_data(database):
    return load_test_data_for_fixture(database, "TestData_Login", 101)

def test_with_fixture(test_data):
    for row in test_data.rows:
        # Test code...
```

### Pattern: Filtering Data

```python
def test_filtered(database):
    loader = DataDrivenTestLoader(database)
    data_set = loader.load_test_data("TestData_Login", 101)
    
    # Filter for success cases
    success_data = filter_test_data(
        data_set,
        lambda row: row.get('expected') == 'success'
    )
    
    for row in success_data.rows:
        # Test code...
```

## Data Classes

### TestDataRow

```python
@dataclass
class TestDataRow:
    pk_id: int              # Primary key
    test_id: int            # Test identifier
    iteration: int          # Iteration number
    instance: int           # Instance number
    fk_id: Optional[int]    # Foreign key
    action: Optional[str]   # Action to perform
    err_msg: Optional[str]  # Expected error
    data: Dict[str, Any]    # All fields
```

### TestDataSet

```python
@dataclass
class TestDataSet:
    test_id: int                    # Test identifier
    table_name: str                 # Source table
    rows: List[TestDataRow]         # All rows
    total_iterations: int           # Number of iterations
    total_instances: int            # Max instances
    
    # Methods
    get_by_iteration(iteration: int) -> List[TestDataRow]
    get_by_instance(iteration: int, instance: int) -> Optional[TestDataRow]
    get_iterations() -> List[int]
    get_instances(iteration: int) -> List[int]
```

## Decorators

### @parametrize_from_dddb

```python
@parametrize_from_dddb(
    table: str,                         # DDDB table name
    test_id: int,                       # Test identifier
    database: DatabaseManager,          # Database instance
    iterations: Optional[List[int]],    # Specific iterations
    instances: Optional[List[int]],     # Specific instances
    id_func: Optional[Callable]         # Custom ID generator
)
```

### @parametrize_iterations

```python
@parametrize_iterations(
    table: str,                         # DDDB table name
    test_id: int,                       # Test identifier
    database: DatabaseManager,          # Database instance
    iterations: Optional[List[int]]     # Specific iterations
)
```

### @parametrize_instances

```python
@parametrize_instances(
    table: str,                         # DDDB table name
    test_id: int,                       # Test identifier
    database: DatabaseManager,          # Database instance
    iteration: int = 1,                 # Iteration to load
    instances: Optional[List[int]]      # Specific instances
)
```

## Helper Functions

### load_test_data_for_fixture

```python
data_set = load_test_data_for_fixture(
    database,
    table="TestData_Login",
    test_id=101,
    iterations=[1, 2],
    instances=[1, 3]
)
```

### get_test_data_params

```python
test_data, test_ids = get_test_data_params(
    database,
    table="TestData_Login",
    test_id=101
)

@pytest.mark.parametrize("data", test_data, ids=test_ids)
def test_manual(data):
    # Test code...
```

### export_test_result

```python
export_test_result(
    database,
    test_data,
    result="PASS",              # PASS, FAIL, SKIP, etc.
    error_message=None          # Optional error message
)
```

### filter_test_data

```python
filtered = filter_test_data(
    data_set,
    lambda row: row.get('active') == True
)
```

### merge_test_data

```python
merged = merge_test_data(data_set1, data_set2, data_set3)
```

## DataDrivenTestLoader Methods

```python
loader = DataDrivenTestLoader(database)

# Load all data
data_set = loader.load_test_data(table, test_id, iterations, instances)

# Load by iteration
rows = loader.load_by_iteration(table, test_id, iteration)

# Load by instance
row = loader.load_by_instance(table, test_id, iteration, instance)
```

## Custom Test IDs

```python
def custom_id(row):
    return f"{row['username']}_iter{row.iteration}_inst{row.instance}"

@parametrize_from_dddb(
    "TestData_Login",
    test_id=101,
    database=db,
    id_func=custom_id
)
def test_with_custom_ids(test_data):
    # Test code...
```

## Error Handling

```python
try:
    # Load data
    data_set = loader.load_test_data("TestData_Login", 101)
except DatabaseException as e:
    print(f"Database error: {e}")

# Check for empty data
if not data_set.rows:
    pytest.skip("No test data found")

# Handle missing fields
email = row.get('email')
if email is None:
    pytest.skip("Email not provided")
```

## Best Practices

1. **Use fixtures for shared data**
   ```python
   @pytest.fixture(scope="module")
   def test_data(database):
       return load_test_data_for_fixture(database, "TestData", 101)
   ```

2. **Export results for tracking**
   ```python
   try:
       # Test code...
       export_test_result(database, test_data, "PASS")
   except Exception as e:
       export_test_result(database, test_data, "FAIL", str(e))
       raise
   ```

3. **Use meaningful test IDs**
   ```python
   id_func=lambda row: f"{row['username']}_{row['scenario']}"
   ```

4. **Filter data for specific scenarios**
   ```python
   success_data = filter_test_data(
       data_set,
       lambda row: row.get('expected') == 'success'
   )
   ```

5. **Handle missing data gracefully**
   ```python
   email = row.get('email', 'default@example.com')
   ```

## See Also

- [Full Guide](DATA_DRIVEN_TESTING_GUIDE.md)
- [Examples](../examples/data_driven_example.py)
- [Database Manager](DATABASE_QUICK_REFERENCE.md)
