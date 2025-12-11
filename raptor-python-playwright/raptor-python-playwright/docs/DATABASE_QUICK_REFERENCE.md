# Database Manager Quick Reference

## Import

```python
from raptor.database import DatabaseManager
from raptor.core.exceptions import DatabaseException
```

## Initialization

```python
# Connection string
db = DatabaseManager(connection_string="DRIVER={...};SERVER=...;DATABASE=...")

# Individual parameters
db = DatabaseManager(server="localhost", database="DDFE", user="user", password="pass")

# Windows Authentication
db = DatabaseManager(server="localhost", database="DDFE")

# With pooling (default)
db = DatabaseManager(server="localhost", database="DDFE", use_pooling=True, pool_max_size=10)
```

## Connection Management

```python
# Context manager (recommended)
with DatabaseManager(server="localhost", database="DDFE") as db:
    results = db.execute_query("SELECT * FROM Users")

# Manual
db = DatabaseManager(server="localhost", database="DDFE")
db.connect()
# ... operations ...
db.disconnect()
```

## Query Operations

```python
# SELECT - all rows
results = db.execute_query("SELECT * FROM Users WHERE active = 1")

# SELECT - single row
result = db.execute_query("SELECT * FROM Users WHERE id = ?", params=(123,), fetch_all=False)

# Parameterized query
results = db.execute_query("SELECT * FROM Users WHERE name = ?", params=('John',))

# INSERT
rows = db.execute_update("INSERT INTO Users (name, email) VALUES (?, ?)", params=('John', 'john@example.com'))

# UPDATE
rows = db.execute_update("UPDATE Users SET active = 1 WHERE id = ?", params=(123,))

# DELETE
rows = db.execute_update("DELETE FROM Users WHERE id = ?", params=(123,))
```

## DDDB Operations

```python
# Import test data
data = db.import_data(table="TestData_Login", test_id=101, iteration=1, instance=1)
username = data['username']
password = data['password']

# Export test result
db.export_data(table="TestData_Login", pk_id=12345, field="test_result", value="PASS")

# Get single field
value = db.get_field(table="TestData_Login", field="username", pk_id=12345)

# Get complete row
row = db.get_row(table="TestData_Login", pk_id=12345)
```

## DDFE Operations

```python
# Get element definition
element = db.get_element_definition(pv_name="login_button", application_name="V3")
primary_locator = element['locator_primary']
fallback1 = element['locator_fallback1']
```

## Connection Pool

```python
# Get pool statistics
stats = db.get_pool_stats()
print(f"Total: {stats['total_connections']}, In use: {stats['in_use']}, Available: {stats['available']}")
```

## Error Handling

```python
try:
    results = db.execute_query("SELECT * FROM Users")
except DatabaseException as e:
    print(f"Error: {e.message}")
    print(f"Context: {e.context}")
```

## Common Patterns

### Test Data Workflow

```python
with DatabaseManager(server="localhost", database="DDFE") as db:
    # Import
    data = db.import_data(table="TestData_Login", test_id=101, iteration=1, instance=1)
    
    # Use data in test
    username = data['username']
    password = data['password']
    
    # Export results
    db.export_data(table="TestData_Login", pk_id=data['pk_id'], field="test_result", value="PASS")
    db.export_data(table="TestData_Login", pk_id=data['pk_id'], field="err_msg", value="Success")
```

### Element Definition Workflow

```python
with DatabaseManager(server="localhost", database="DDFE") as db:
    # Get element
    element = db.get_element_definition(pv_name="login_button")
    
    # Use in automation
    primary = element['locator_primary']
    fallbacks = [element['locator_fallback1'], element['locator_fallback2']]
    
    # element_manager.locate_element(primary, fallback_locators=fallbacks)
```

### pytest Integration

```python
@pytest.fixture(scope="session")
def database():
    db = DatabaseManager(server="localhost", database="DDFE")
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture
def test_data(database):
    return database.import_data(table="TestData_Login", test_id=101, iteration=1, instance=1)

def test_login(database, test_data):
    username = test_data['username']
    # ... test code ...
    database.export_data(table="TestData_Login", pk_id=test_data['pk_id'], field="test_result", value="PASS")
```

## Key Methods

| Method | Purpose | Returns |
|--------|---------|---------|
| `connect()` | Establish connection | None |
| `disconnect()` | Close connection | None |
| `execute_query(sql, params)` | Execute SELECT | List[Dict] |
| `execute_update(sql, params)` | Execute INSERT/UPDATE/DELETE | int (rows affected) |
| `import_data(table, test_id, iteration, instance)` | Import test data | Dict |
| `export_data(table, pk_id, field, value)` | Export result | int (rows affected) |
| `get_field(table, field, pk_id)` | Get single field | Any |
| `get_row(table, pk_id)` | Get complete row | Dict |
| `get_element_definition(pv_name, application_name)` | Get element | Dict |
| `get_pool_stats()` | Get pool statistics | Dict |

## Best Practices

✅ **DO:**
- Use context managers (`with` statement)
- Use parameterized queries
- Enable pooling for multiple operations
- Handle DatabaseException errors
- Close connections when done

❌ **DON'T:**
- Concatenate user input into SQL strings
- Forget to close connections
- Ignore error handling
- Use pooling for single operations

