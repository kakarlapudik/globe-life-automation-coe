# Database Manager Implementation

## Overview

The Database Manager provides comprehensive database operations for the RAPTOR Python Playwright framework, including SQL Server connectivity, connection pooling, and DDFE/DDDB integration.

## Features

- **SQL Server Connectivity**: Full support for SQL Server via pyodbc
- **Connection Pooling**: Efficient connection management with configurable pool sizes
- **Parameterized Queries**: SQL injection prevention through parameterized queries
- **DDFE Integration**: Element definition retrieval from DDFE database
- **DDDB Operations**: Test data import/export functionality
- **Error Handling**: Comprehensive error handling with detailed context

## Installation Requirements

```bash
# Install pyodbc for SQL Server connectivity
pip install pyodbc

# Windows: ODBC Driver 17 for SQL Server (usually pre-installed)
# Linux: Install unixODBC and SQL Server ODBC driver
# macOS: Install unixODBC via Homebrew
```

## Basic Usage

### Initialization

```python
from raptor.database import DatabaseManager

# Using connection string
db = DatabaseManager(
    connection_string="DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=DDFE;UID=user;PWD=pass"
)

# Using individual parameters
db = DatabaseManager(
    server="localhost",
    database="DDFE",
    user="testuser",
    password="password"
)

# Using Windows Authentication
db = DatabaseManager(
    server="localhost",
    database="DDFE"
    # No user/password = Windows Authentication
)
```

### Connection Management

```python
# Manual connection management
db = DatabaseManager(server="localhost", database="DDFE")
db.connect()
# ... perform operations ...
db.disconnect()

# Context manager (recommended)
with DatabaseManager(server="localhost", database="DDFE") as db:
    results = db.execute_query("SELECT * FROM Users")
    # Connection automatically closed
```

## Query Operations

### SELECT Queries

```python
# Simple query
results = db.execute_query("SELECT * FROM Users WHERE active = 1")
for row in results:
    print(f"User: {row['username']}, Email: {row['email']}")

# Parameterized query (prevents SQL injection)
results = db.execute_query(
    "SELECT * FROM Users WHERE user_id = ?",
    params=(123,)
)

# Named parameters
results = db.execute_query(
    "SELECT * FROM Users WHERE name = :name AND age > :age",
    params={'name': 'John', 'age': 25}
)

# Fetch single row
result = db.execute_query(
    "SELECT * FROM Users WHERE user_id = ?",
    params=(123,),
    fetch_all=False
)
```

### INSERT, UPDATE, DELETE Operations

```python
# Insert
rows_affected = db.execute_update(
    "INSERT INTO Users (name, email, active) VALUES (?, ?, ?)",
    params=('John Doe', 'john@example.com', 1)
)

# Update
rows_affected = db.execute_update(
    "UPDATE Users SET active = 1 WHERE user_id = ?",
    params=(123,)
)

# Delete
rows_affected = db.execute_update(
    "DELETE FROM Users WHERE user_id = ?",
    params=(123,)
)

# Without auto-commit (for transactions)
rows_affected = db.execute_update(
    "UPDATE Users SET active = 0 WHERE user_id = ?",
    params=(123,),
    commit=False
)
```

## DDDB Operations

### Import Test Data

```python
# Import test data for a specific test
data = db.import_data(
    table="TestData_Login",
    test_id=101,
    iteration=1,
    instance=1
)

# Access imported data
username = data['username']
password = data['password']
expected_result = data['expected_result']

# Import with additional filters
data = db.import_data(
    table="TestData_Login",
    test_id=101,
    iteration=1,
    instance=1,
    additional_filters={'environment': 'staging'}
)
```

### Export Test Results

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

### Retrieve Field Values

```python
# Get single field value
username = db.get_field(
    table="TestData_Login",
    field="username",
    pk_id=12345
)

# Get complete row
row = db.get_row(
    table="TestData_Login",
    pk_id=12345
)
username = row['username']
password = row['password']
```

## DDFE Operations

### Retrieve Element Definitions

```python
# Get element definition by pv_name
element = db.get_element_definition(
    pv_name="login_button"
)

# Access element properties
primary_locator = element['locator_primary']
fallback1 = element['locator_fallback1']
fallback2 = element['locator_fallback2']
field_type = element['field_type']

# Get element with application filter
element = db.get_element_definition(
    pv_name="login_button",
    application_name="V3"
)
```

## Connection Pooling

### Configuration

```python
# Enable connection pooling (default)
db = DatabaseManager(
    server="localhost",
    database="DDFE",
    use_pooling=True,
    pool_min_size=2,    # Minimum connections
    pool_max_size=10    # Maximum connections
)

# Disable connection pooling
db = DatabaseManager(
    server="localhost",
    database="DDFE",
    use_pooling=False
)
```

### Pool Statistics

```python
# Get pool statistics
stats = db.get_pool_stats()
if stats:
    print(f"Total connections: {stats['total_connections']}")
    print(f"In use: {stats['in_use']}")
    print(f"Available: {stats['available']}")
    print(f"Pool queue size: {stats['pool_queue_size']}")
```

## Error Handling

```python
from raptor.core.exceptions import DatabaseException

try:
    results = db.execute_query("SELECT * FROM NonExistentTable")
except DatabaseException as e:
    print(f"Database error: {e.message}")
    print(f"Operation: {e.context['database_operation']}")
    print(f"SQL: {e.context['sql_query']}")
    
    # Log full error details
    error_dict = e.to_dict()
    logger.error(f"Database error details: {error_dict}")
```

## Complete Example

```python
from raptor.database import DatabaseManager
from raptor.core.exceptions import DatabaseException
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_test_with_database():
    """Example test using database operations."""
    
    # Initialize database manager
    with DatabaseManager(
        server="localhost",
        database="DDFE",
        user="testuser",
        password="password",
        use_pooling=True
    ) as db:
        
        try:
            # Import test data
            test_data = db.import_data(
                table="TestData_Login",
                test_id=101,
                iteration=1,
                instance=1
            )
            
            logger.info(f"Test data imported: {test_data}")
            
            # Get element definition
            login_button = db.get_element_definition(
                pv_name="login_button",
                application_name="V3"
            )
            
            logger.info(f"Element locator: {login_button['locator_primary']}")
            
            # Perform test operations...
            # (browser automation code here)
            
            # Update test result
            db.export_data(
                table="TestData_Login",
                pk_id=test_data['pk_id'],
                field="test_result",
                value="PASS"
            )
            
            db.export_data(
                table="TestData_Login",
                pk_id=test_data['pk_id'],
                field="err_msg",
                value="Test completed successfully"
            )
            
            logger.info("Test completed and results exported")
            
        except DatabaseException as e:
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            logger.error(f"Test error: {e}")
            raise

if __name__ == "__main__":
    run_test_with_database()
```

## Integration with pytest

```python
import pytest
from raptor.database import DatabaseManager

@pytest.fixture(scope="session")
def database():
    """Provide database connection for tests."""
    db = DatabaseManager(
        server="localhost",
        database="DDFE",
        use_pooling=True
    )
    db.connect()
    yield db
    db.disconnect()

@pytest.fixture
def test_data(database):
    """Load test data for each test."""
    data = database.import_data(
        table="TestData_Login",
        test_id=101,
        iteration=1,
        instance=1
    )
    return data

def test_login(database, test_data):
    """Test login functionality with database data."""
    username = test_data['username']
    password = test_data['password']
    
    # Perform test...
    result = "PASS"
    
    # Update result
    database.export_data(
        table="TestData_Login",
        pk_id=test_data['pk_id'],
        field="test_result",
        value=result
    )
```

## Best Practices

### 1. Use Context Managers

```python
# Good - automatic cleanup
with DatabaseManager(server="localhost", database="DDFE") as db:
    results = db.execute_query("SELECT * FROM Users")

# Avoid - manual cleanup required
db = DatabaseManager(server="localhost", database="DDFE")
db.connect()
results = db.execute_query("SELECT * FROM Users")
db.disconnect()  # Easy to forget!
```

### 2. Always Use Parameterized Queries

```python
# Good - prevents SQL injection
user_id = request.get('user_id')
results = db.execute_query(
    "SELECT * FROM Users WHERE user_id = ?",
    params=(user_id,)
)

# Bad - vulnerable to SQL injection
user_id = request.get('user_id')
results = db.execute_query(
    f"SELECT * FROM Users WHERE user_id = {user_id}"
)
```

### 3. Enable Connection Pooling for Multiple Operations

```python
# Good for multiple operations
db = DatabaseManager(
    server="localhost",
    database="DDFE",
    use_pooling=True,
    pool_min_size=2,
    pool_max_size=10
)

# Good for single operation
db = DatabaseManager(
    server="localhost",
    database="DDFE",
    use_pooling=False
)
```

### 4. Handle Errors Appropriately

```python
from raptor.core.exceptions import DatabaseException

try:
    data = db.import_data(
        table="TestData_Login",
        test_id=101,
        iteration=1,
        instance=1
    )
except DatabaseException as e:
    # Log error with context
    logger.error(f"Failed to import test data: {e}")
    logger.error(f"Context: {e.context}")
    
    # Re-raise or handle appropriately
    raise
```

## Performance Considerations

### Connection Pooling

- **Enable pooling** for applications with multiple database operations
- **Disable pooling** for single-operation scripts
- **Tune pool size** based on concurrent operation needs

### Query Optimization

- Use **specific column names** instead of `SELECT *` when possible
- Add **appropriate indexes** on frequently queried columns
- Use **fetch_all=False** when only one row is needed

### Resource Management

- Always **close connections** when done (use context managers)
- **Monitor pool statistics** to tune pool size
- **Clean up idle connections** periodically

## Troubleshooting

### Connection Issues

```python
# Test basic connectivity
try:
    db = DatabaseManager(
        server="localhost",
        database="DDFE",
        user="testuser",
        password="password"
    )
    db.connect()
    print("Connection successful!")
    db.disconnect()
except DatabaseException as e:
    print(f"Connection failed: {e}")
    print(f"Error details: {e.context}")
```

### Driver Issues

```bash
# Check installed ODBC drivers
# Windows
odbcad32.exe

# Linux
odbcinst -q -d

# macOS
odbcinst -q -d
```

### Pool Exhaustion

```python
# Monitor pool usage
stats = db.get_pool_stats()
if stats['available'] == 0:
    logger.warning("Connection pool exhausted!")
    logger.info(f"Pool stats: {stats}")
    
    # Consider increasing max_size
    db = DatabaseManager(
        server="localhost",
        database="DDFE",
        pool_max_size=20  # Increased from default 10
    )
```

## API Reference

See the inline documentation in `database_manager.py` for complete API details.

### Key Methods

- `connect()` - Establish database connection
- `disconnect()` - Close database connection
- `execute_query()` - Execute SELECT queries
- `execute_update()` - Execute INSERT/UPDATE/DELETE
- `import_data()` - Import test data from DDDB
- `export_data()` - Export results to DDDB
- `get_field()` - Get single field value
- `get_row()` - Get complete row
- `get_element_definition()` - Get DDFE element definition
- `get_pool_stats()` - Get connection pool statistics

## Related Documentation

- [Connection Pool Implementation](../raptor/database/connection_pool.py)
- [Database Exceptions](../raptor/core/exceptions.py)
- [Requirements Document](../../.kiro/specs/raptor-playwright-python/requirements.md)
- [Design Document](../../.kiro/specs/raptor-playwright-python/design.md)

