# Advanced Table Operations Guide

This guide covers advanced table operations in the RAPTOR Python Playwright Framework, including dynamic table loading, pagination, and search functionality.

## Table of Contents

1. [Search Operations](#search-operations)
2. [Dynamic Table Loading](#dynamic-table-loading)
3. [Infinite Scroll Tables](#infinite-scroll-tables)
4. [Pagination Navigation](#pagination-navigation)
5. [Best Practices](#best-practices)

## Search Operations

### Basic Search with Partial Matching

Search for text within a table with partial matching support:

```python
from raptor.pages.table_manager import TableManager

# Search for rows containing "john" (case-insensitive)
matching_rows = await table_manager.search_table(
    table_locator="css=#users-table",
    search_text="john",
    case_sensitive=False,
    partial_match=True
)

print(f"Found matches in rows: {matching_rows}")
```

### Case-Sensitive Search

Perform case-sensitive searches:

```python
# Case-sensitive search
matching_rows = await table_manager.search_table(
    table_locator="css=#users-table",
    search_text="John",
    case_sensitive=True,
    partial_match=True
)
```

### Exact Match Search

Search for exact matches only:

```python
# Exact match (no partial matching)
matching_rows = await table_manager.search_table(
    table_locator="css=#users-table",
    search_text="John Doe",
    case_sensitive=False,
    partial_match=False
)
```

## Dynamic Table Loading

### Wait for Table Updates

Wait for a dynamically loading table to finish updating:

```python
# Wait for table to finish loading
await table_manager.wait_for_table_update("css=#dynamic-table")

# Now safe to read table data
row_count = await table_manager.get_row_count("css=#dynamic-table")
```

**How it works:**
- Waits for network idle state
- Checks for common loading indicators (`.loading`, `.spinner`, etc.)
- Monitors row count stability
- Returns when table has stabilized

### Scroll Table Into View

Scroll a table into view to trigger lazy loading:

```python
# Scroll table into view
await table_manager.scroll_table_into_view("css=#lazy-table")

# Wait for content to load
await table_manager.wait_for_table_update("css=#lazy-table")
```

## Infinite Scroll Tables

### Load All Rows

Load all rows from an infinite scroll table:

```python
# Load all rows by scrolling
total_rows = await table_manager.load_all_dynamic_rows(
    table_locator="css=#infinite-scroll-table",
    max_scrolls=100  # Maximum scroll attempts
)

print(f"Loaded {total_rows} total rows")
```

### With Custom Scroll Container

If the table is inside a custom scroll container:

```python
# Specify custom scroll container
total_rows = await table_manager.load_all_dynamic_rows(
    table_locator="css=#infinite-scroll-table",
    scroll_container_locator="css=.scroll-container",
    max_scrolls=100
)
```

**How it works:**
- Scrolls to bottom of table/container
- Waits for new content to load
- Checks for loading indicators
- Repeats until no new rows appear or max_scrolls reached
- Returns total number of rows loaded

## Pagination Navigation

### Navigate to Next Page

Navigate through paginated tables:

```python
# Navigate to next page
has_next = await table_manager.navigate_pagination("css=.next-page")

if has_next:
    print("Navigated to next page")
    await table_manager.wait_for_table_update("css=#data-table")
else:
    print("Already on last page")
```

### Get Pagination Information

Get current pagination state:

```python
# Get pagination info
pagination_info = await table_manager.get_pagination_info(
    current_page_locator="css=.current-page",
    total_pages_locator="css=.total-pages"
)

print(f"Page {pagination_info['current_page']} of {pagination_info['total_pages']}")
print(f"Has next: {pagination_info['has_next']}")
print(f"Has previous: {pagination_info['has_previous']}")
```

### Navigate to Specific Page

Jump to a specific page number:

```python
# Using page input field
success = await table_manager.navigate_to_page(
    page_number=5,
    page_input_locator="css=.page-input"
)

# Or using page button
success = await table_manager.navigate_to_page(
    page_number=5,
    page_button_locator_template="css=button[data-page='{page}']"
)
```

### Process All Pages

Loop through all pages:

```python
page_num = 1
all_data = []

while True:
    print(f"Processing page {page_num}...")
    
    # Process current page
    row_count = await table_manager.get_row_count("css=#data-table")
    for row_idx in range(row_count):
        cell_value = await table_manager.get_cell_value(
            "css=#data-table",
            row=row_idx,
            column=0
        )
        all_data.append(cell_value)
    
    # Try to navigate to next page
    has_next = await table_manager.navigate_pagination("css=.next-page")
    
    if not has_next:
        break
    
    page_num += 1
    await table_manager.wait_for_table_update("css=#data-table")

print(f"Collected {len(all_data)} total records")
```

## Best Practices

### 1. Always Wait for Table Updates

After navigation or dynamic loading, wait for the table to stabilize:

```python
# After pagination
await table_manager.navigate_pagination("css=.next-page")
await table_manager.wait_for_table_update("css=#data-table")

# After scrolling
await table_manager.scroll_table_into_view("css=#lazy-table")
await table_manager.wait_for_table_update("css=#lazy-table")
```

### 2. Use Appropriate Timeouts

Configure timeouts based on your application's loading speed:

```python
# Longer timeout for slow-loading tables
await table_manager.wait_for_table_update(
    "css=#slow-table",
    timeout=60000  # 60 seconds
)
```

### 3. Handle Edge Cases

Check for empty results and handle gracefully:

```python
matching_rows = await table_manager.search_table(
    "css=#users-table",
    search_text="nonexistent"
)

if not matching_rows:
    print("No matches found")
else:
    print(f"Found {len(matching_rows)} matches")
```

### 4. Limit Infinite Scroll Attempts

Always set a reasonable max_scrolls limit:

```python
# Prevent infinite loops
total_rows = await table_manager.load_all_dynamic_rows(
    "css=#infinite-scroll-table",
    max_scrolls=50  # Reasonable limit
)
```

### 5. Combine Operations Efficiently

Combine search and pagination for efficient data collection:

```python
all_matches = []
page_num = 1

while True:
    # Search current page
    matching_rows = await table_manager.search_table(
        "css=#data-table",
        search_text="target"
    )
    
    # Collect matching data
    for row_idx in matching_rows:
        data = await table_manager.get_cell_value(
            "css=#data-table",
            row=row_idx,
            column=0
        )
        all_matches.append(data)
    
    # Navigate to next page
    if not await table_manager.navigate_pagination("css=.next-page"):
        break
    
    page_num += 1
    await table_manager.wait_for_table_update("css=#data-table")

print(f"Found {len(all_matches)} total matches across {page_num} pages")
```

## Common Patterns

### Pattern 1: Search Across All Pages

```python
async def search_all_pages(table_manager, search_text):
    """Search for text across all pages of a paginated table."""
    all_matches = []
    page_num = 1
    
    while True:
        matching_rows = await table_manager.search_table(
            "css=#data-table",
            search_text=search_text,
            case_sensitive=False
        )
        
        for row_idx in matching_rows:
            row_data = await table_manager.get_cell_value(
                "css=#data-table",
                row=row_idx,
                column=0
            )
            all_matches.append(row_data)
        
        if not await table_manager.navigate_pagination("css=.next-page"):
            break
        
        page_num += 1
        await table_manager.wait_for_table_update("css=#data-table")
    
    return all_matches
```

### Pattern 2: Load and Process Infinite Scroll

```python
async def process_infinite_scroll(table_manager):
    """Load all rows from infinite scroll and process them."""
    # Load all rows
    total_rows = await table_manager.load_all_dynamic_rows(
        "css=#infinite-scroll-table",
        max_scrolls=100
    )
    
    # Process all loaded rows
    results = []
    for row_idx in range(total_rows):
        cell_value = await table_manager.get_cell_value(
            "css=#infinite-scroll-table",
            row=row_idx,
            column=0
        )
        results.append(cell_value)
    
    return results
```

### Pattern 3: Dynamic Table with Search

```python
async def search_dynamic_table(table_manager, search_text):
    """Search a dynamically loading table."""
    # Wait for table to load
    await table_manager.wait_for_table_update("css=#dynamic-table")
    
    # Perform search
    matching_rows = await table_manager.search_table(
        "css=#dynamic-table",
        search_text=search_text
    )
    
    # Extract matching data
    results = []
    for row_idx in matching_rows:
        row_data = await table_manager.get_cell_value(
            "css=#dynamic-table",
            row=row_idx,
            column=0
        )
        results.append(row_data)
    
    return results
```

## Troubleshooting

### Table Not Stabilizing

If `wait_for_table_update()` times out:

1. Check if loading indicators are present
2. Increase timeout value
3. Verify table structure matches expected format
4. Check network requests in browser DevTools

### Infinite Scroll Not Loading

If `load_all_dynamic_rows()` doesn't load all rows:

1. Verify scroll container is correct
2. Check if table uses virtual scrolling
3. Increase `max_scrolls` parameter
4. Verify loading indicators are detected

### Pagination Not Working

If `navigate_pagination()` fails:

1. Verify next button locator is correct
2. Check if button is enabled/disabled properly
3. Ensure page waits for network idle
4. Verify table updates after navigation

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 8.4**: Search table with partial match support ✓
- **Requirement 8.4**: Case-insensitive search option ✓
- **Requirement 8.5**: Navigate pagination for multi-page tables ✓
- **Requirement 8.5**: Support for dynamic table loading ✓

## See Also

- [Table Manager Guide](TABLE_MANAGER_GUIDE.md)
- [Element Manager Guide](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Advanced Table Examples](../examples/advanced_table_example.py)
