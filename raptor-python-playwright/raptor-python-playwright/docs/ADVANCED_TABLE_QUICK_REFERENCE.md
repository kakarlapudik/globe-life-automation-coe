# Advanced Table Operations - Quick Reference

## Search Operations

```python
# Partial match, case-insensitive (default)
rows = await table_manager.search_table(
    "css=#table",
    search_text="john"
)

# Case-sensitive search
rows = await table_manager.search_table(
    "css=#table",
    search_text="John",
    case_sensitive=True
)

# Exact match only
rows = await table_manager.search_table(
    "css=#table",
    search_text="John Doe",
    partial_match=False
)
```

## Dynamic Loading

```python
# Wait for table to finish loading
await table_manager.wait_for_table_update("css=#table")

# Scroll table into view (triggers lazy loading)
await table_manager.scroll_table_into_view("css=#table")
```

## Infinite Scroll

```python
# Load all rows from infinite scroll table
total_rows = await table_manager.load_all_dynamic_rows(
    "css=#table",
    max_scrolls=100
)

# With custom scroll container
total_rows = await table_manager.load_all_dynamic_rows(
    "css=#table",
    scroll_container_locator="css=.container",
    max_scrolls=100
)
```

## Pagination

```python
# Navigate to next page
has_next = await table_manager.navigate_pagination("css=.next-page")

# Get pagination info
info = await table_manager.get_pagination_info(
    current_page_locator="css=.current-page",
    total_pages_locator="css=.total-pages"
)
# Returns: {'current_page': 3, 'total_pages': 10, 'has_next': True, 'has_previous': True}

# Navigate to specific page (using input)
await table_manager.navigate_to_page(
    5,
    page_input_locator="css=.page-input"
)

# Navigate to specific page (using button)
await table_manager.navigate_to_page(
    5,
    page_button_locator_template="css=button[data-page='{page}']"
)
```

## Common Patterns

### Search All Pages

```python
all_matches = []
while True:
    rows = await table_manager.search_table("css=#table", search_text="target")
    for row_idx in rows:
        data = await table_manager.get_cell_value("css=#table", row=row_idx, column=0)
        all_matches.append(data)
    
    if not await table_manager.navigate_pagination("css=.next-page"):
        break
    await table_manager.wait_for_table_update("css=#table")
```

### Process Infinite Scroll

```python
total_rows = await table_manager.load_all_dynamic_rows("css=#table", max_scrolls=100)
for row_idx in range(total_rows):
    value = await table_manager.get_cell_value("css=#table", row=row_idx, column=0)
    process(value)
```

### Dynamic Table Search

```python
await table_manager.wait_for_table_update("css=#table")
rows = await table_manager.search_table("css=#table", search_text="admin")
for row_idx in rows:
    data = await table_manager.get_cell_value("css=#table", row=row_idx, column=0)
    print(data)
```

## Method Signatures

```python
async def search_table(
    table_locator: str,
    search_text: str,
    case_sensitive: bool = False,
    partial_match: bool = True,
    timeout: Optional[int] = None
) -> List[int]

async def wait_for_table_update(
    table_locator: str,
    timeout: Optional[int] = None
) -> None

async def scroll_table_into_view(
    table_locator: str,
    timeout: Optional[int] = None
) -> None

async def load_all_dynamic_rows(
    table_locator: str,
    scroll_container_locator: Optional[str] = None,
    max_scrolls: int = 50,
    timeout: Optional[int] = None
) -> int

async def navigate_pagination(
    next_button_locator: str,
    timeout: Optional[int] = None
) -> bool

async def get_pagination_info(
    current_page_locator: Optional[str] = None,
    total_pages_locator: Optional[str] = None,
    timeout: Optional[int] = None
) -> Dict[str, Any]

async def navigate_to_page(
    page_number: int,
    page_input_locator: Optional[str] = None,
    page_button_locator_template: Optional[str] = None,
    timeout: Optional[int] = None
) -> bool
```

## Tips

- Always wait for table updates after navigation
- Use appropriate timeouts for slow-loading tables
- Limit max_scrolls to prevent infinite loops
- Handle empty search results gracefully
- Combine operations for efficiency

## See Also

- [Full Guide](ADVANCED_TABLE_OPERATIONS.md)
- [Examples](../examples/advanced_table_example.py)
- [Table Manager Guide](TABLE_MANAGER_GUIDE.md)
