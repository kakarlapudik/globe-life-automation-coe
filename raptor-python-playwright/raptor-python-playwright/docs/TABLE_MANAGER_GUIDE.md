# Table Manager Guide

## Overview

The `TableManager` class provides specialized operations for interacting with HTML tables in web applications. It handles common table operations like finding rows, reading/writing cell values, searching, and pagination.

## Features

- **Row Location**: Find rows by key column values
- **Cell Operations**: Read and write cell values
- **Cell Interaction**: Click cells for buttons or links
- **Table Search**: Search with partial matching and case sensitivity options
- **Pagination**: Navigate multi-page tables
- **Column Operations**: Extract all values from a specific column
- **Robust Error Handling**: Detailed error messages and logging

## Basic Usage

### Initialization

```python
from raptor.pages.table_manager import TableManager
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager

# Initialize dependencies
config = ConfigManager()
element_manager = ElementManager(page, config)

# Create TableManager instance
table_manager = TableManager(page, element_manager, config)
```

### Finding Rows by Key

Find a table row by searching for a specific value in a key column:

```python
# Find row where column 0 contains "john.doe"
row_index = await table_manager.find_row_by_key(
    table_locator="css=#users-table",
    key_column=0,
    key_value="john.doe"
)

print(f"Found user at row {row_index}")
```

### Reading Cell Values

Get the text content of a specific cell:

```python
# Get value from row 2, column 1
email = await table_manager.get_cell_value(
    table_locator="css=#users-table",
    row=2,
    column=1
)

print(f"Email: {email}")
```

### Writing Cell Values

Set the value of an editable cell:

```python
# Update cell value
await table_manager.set_cell_value(
    table_locator="css=#users-table",
    row=2,
    column=1,
    value="new.email@example.com"
)
```

**Note**: The method will:
1. First try to find an input element within the cell
2. If not found, double-click the cell to enter edit mode
3. Then fill the input with the new value

### Clicking Cells

Click on a cell (useful for buttons or links):

```python
# Click edit button in column 4
await table_manager.click_cell(
    table_locator="css=#users-table",
    row=2,
    column=4
)
```

### Getting Row Count

Get the total number of rows in a table:

```python
count = await table_manager.get_row_count("css=#users-table")
print(f"Table has {count} rows")
```

## Advanced Features

### Searching Tables

Search for text across all cells in a table:

```python
# Case-insensitive partial match
matching_rows = await table_manager.search_table(
    table_locator="css=#users-table",
    search_text="admin",
    case_sensitive=False,
    partial_match=True
)

print(f"Found matches in rows: {matching_rows}")
```

**Search Options**:
- `case_sensitive`: Whether to match case (default: False)
- `partial_match`: Allow partial matches (default: True)

### Getting Column Values

Extract all values from a specific column:

```python
# Get all usernames (column 0)
usernames = await table_manager.get_column_values(
    table_locator="css=#users-table",
    column=0
)

for username in usernames:
    print(username)
```

### Navigating Pagination

Navigate through multi-page tables:

```python
page_num = 1

while True:
    print(f"Processing page {page_num}...")
    
    # Process current page
    row_count = await table_manager.get_row_count("css=#users-table")
    
    # Try to go to next page
    has_next = await table_manager.navigate_pagination("css=.next-page")
    
    if not has_next:
        print("Reached last page")
        break
    
    page_num += 1
```

## Complete Workflow Example

Here's a complete example that combines multiple operations:

```python
async def update_user_status():
    """Find and update status for all admin users."""
    
    # Search for admin users
    admin_rows = await table_manager.search_table(
        table_locator="css=#users-table",
        search_text="admin",
        case_sensitive=False
    )
    
    print(f"Found {len(admin_rows)} admin users")
    
    # Update each admin user
    for row_idx in admin_rows:
        # Get username
        username = await table_manager.get_cell_value(
            "css=#users-table",
            row=row_idx,
            column=0
        )
        
        print(f"Updating {username}...")
        
        # Update status
        await table_manager.set_cell_value(
            "css=#users-table",
            row=row_idx,
            column=3,  # Status column
            value="Active"
        )
        
        # Click save button
        await table_manager.click_cell(
            "css=#users-table",
            row=row_idx,
            column=5  # Save button column
        )
    
    print("All admin users updated")
```

## Table Locator Strategies

The `table_locator` parameter supports all standard Playwright locator strategies:

```python
# CSS selector
"css=#users-table"

# XPath
"xpath=//table[@id='users-table']"

# Data attribute
"css=[data-testid='users-table']"

# Class name
"css=.data-table"
```

## Error Handling

The TableManager raises specific exceptions for different error conditions:

```python
from raptor.core.exceptions import (
    ElementNotFoundException,
    ElementNotInteractableException,
    TimeoutException
)

try:
    row_index = await table_manager.find_row_by_key(
        "css=#users-table",
        key_column=0,
        key_value="nonexistent"
    )
except ElementNotFoundException as e:
    print(f"Row not found: {e}")
except TimeoutException as e:
    print(f"Operation timed out: {e}")
```

## Configuration

### Timeouts

Configure default timeout for table operations:

```yaml
# config/settings.yaml
timeouts:
  default: 20000  # 20 seconds
```

Override timeout for specific operations:

```python
# Use custom timeout
row_index = await table_manager.find_row_by_key(
    "css=#users-table",
    key_column=0,
    key_value="john.doe",
    timeout=30000  # 30 seconds
)
```

## Best Practices

### 1. Use Stable Locators

Use stable table locators that won't change:

```python
# Good - uses ID
"css=#users-table"

# Good - uses data attribute
"css=[data-testid='users-table']"

# Avoid - fragile class names
"css=.table-1234"
```

### 2. Handle Missing Data

Always handle cases where data might not exist:

```python
try:
    row_index = await table_manager.find_row_by_key(
        "css=#users-table",
        key_column=0,
        key_value=username
    )
    # Process row
except ElementNotFoundException:
    print(f"User {username} not found in table")
```

### 3. Wait for Table Updates

After modifying table data, wait for updates to complete:

```python
# Update cell
await table_manager.set_cell_value(
    "css=#users-table",
    row=row_idx,
    column=1,
    value="new value"
)

# Wait for save to complete
await page.wait_for_load_state("networkidle")

# Verify update
updated_value = await table_manager.get_cell_value(
    "css=#users-table",
    row=row_idx,
    column=1
)
assert updated_value == "new value"
```

### 4. Use Column Values for Bulk Operations

When processing all rows, use `get_column_values` for efficiency:

```python
# Efficient - single query for all values
usernames = await table_manager.get_column_values(
    "css=#users-table",
    column=0
)

for username in usernames:
    process_user(username)

# Less efficient - multiple queries
row_count = await table_manager.get_row_count("css=#users-table")
for i in range(row_count):
    username = await table_manager.get_cell_value(
        "css=#users-table",
        row=i,
        column=0
    )
    process_user(username)
```

## Troubleshooting

### Table Not Found

**Problem**: `ElementNotFoundException: Could not locate table`

**Solutions**:
- Verify the table locator is correct
- Ensure the table is visible on the page
- Wait for page to load before accessing table
- Check if table is in an iframe

### Cell Not Editable

**Problem**: `ElementNotInteractableException: Cell is not editable`

**Solutions**:
- Verify the cell contains an input element
- Check if double-click enables edit mode
- Ensure the cell is not disabled
- Verify user has permission to edit

### Row Not Found

**Problem**: `ElementNotFoundException: Key value not found`

**Solutions**:
- Verify the key value exists in the table
- Check if table is paginated (search other pages)
- Ensure correct column index is used
- Check for whitespace or formatting differences

### Pagination Not Working

**Problem**: Navigation button not found or disabled

**Solutions**:
- Verify the next button locator is correct
- Check if already on the last page
- Ensure pagination controls are visible
- Wait for page load after navigation

## API Reference

### find_row_by_key()

```python
async def find_row_by_key(
    table_locator: str,
    key_column: int,
    key_value: str,
    timeout: Optional[int] = None
) -> int
```

Find a table row by key value.

**Parameters**:
- `table_locator`: Locator for the table element
- `key_column`: Zero-based column index to search
- `key_value`: Value to search for
- `timeout`: Optional timeout in milliseconds

**Returns**: Zero-based row index

**Raises**: `ElementNotFoundException`, `TimeoutException`

### get_cell_value()

```python
async def get_cell_value(
    table_locator: str,
    row: int,
    column: int,
    timeout: Optional[int] = None
) -> str
```

Get the text value of a cell.

**Parameters**:
- `table_locator`: Locator for the table element
- `row`: Zero-based row index
- `column`: Zero-based column index
- `timeout`: Optional timeout in milliseconds

**Returns**: Cell text content

**Raises**: `ElementNotFoundException`, `TimeoutException`

### set_cell_value()

```python
async def set_cell_value(
    table_locator: str,
    row: int,
    column: int,
    value: str,
    timeout: Optional[int] = None
) -> None
```

Set the value of an editable cell.

**Parameters**:
- `table_locator`: Locator for the table element
- `row`: Zero-based row index
- `column`: Zero-based column index
- `value`: Value to set
- `timeout`: Optional timeout in milliseconds

**Raises**: `ElementNotFoundException`, `ElementNotInteractableException`, `TimeoutException`

### click_cell()

```python
async def click_cell(
    table_locator: str,
    row: int,
    column: int,
    timeout: Optional[int] = None
) -> None
```

Click on a specific cell.

**Parameters**:
- `table_locator`: Locator for the table element
- `row`: Zero-based row index
- `column`: Zero-based column index
- `timeout`: Optional timeout in milliseconds

**Raises**: `ElementNotFoundException`, `TimeoutException`

### get_row_count()

```python
async def get_row_count(
    table_locator: str,
    timeout: Optional[int] = None
) -> int
```

Get the number of rows in a table.

**Parameters**:
- `table_locator`: Locator for the table element
- `timeout`: Optional timeout in milliseconds

**Returns**: Number of rows

**Raises**: `ElementNotFoundException`, `TimeoutException`

### search_table()

```python
async def search_table(
    table_locator: str,
    search_text: str,
    case_sensitive: bool = False,
    partial_match: bool = True,
    timeout: Optional[int] = None
) -> List[int]
```

Search for text in a table.

**Parameters**:
- `table_locator`: Locator for the table element
- `search_text`: Text to search for
- `case_sensitive`: Whether search is case-sensitive
- `partial_match`: Whether to allow partial matches
- `timeout`: Optional timeout in milliseconds

**Returns**: List of matching row indices

**Raises**: `ElementNotFoundException`, `TimeoutException`

### navigate_pagination()

```python
async def navigate_pagination(
    next_button_locator: str,
    timeout: Optional[int] = None
) -> bool
```

Navigate to the next page in a paginated table.

**Parameters**:
- `next_button_locator`: Locator for the next page button
- `timeout`: Optional timeout in milliseconds

**Returns**: True if navigation succeeded, False if on last page

**Raises**: `TimeoutException`

### get_column_values()

```python
async def get_column_values(
    table_locator: str,
    column: int,
    timeout: Optional[int] = None
) -> List[str]
```

Get all values from a specific column.

**Parameters**:
- `table_locator`: Locator for the table element
- `column`: Zero-based column index
- `timeout`: Optional timeout in milliseconds

**Returns**: List of cell values

**Raises**: `ElementNotFoundException`, `TimeoutException`

## See Also

- [Element Manager Guide](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Base Page Guide](BASE_PAGE_QUICK_REFERENCE.md)
- [Configuration Guide](CONFIG_MANAGER_IMPLEMENTATION.md)
