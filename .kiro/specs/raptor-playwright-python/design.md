# RAPTOR Python Playwright Framework - Design Document

## Overview

This document outlines the detailed design for converting the RAPTOR Java Selenium framework to a modern Python Playwright-based test automation framework. The conversion will maintain functional parity with the existing Java framework while leveraging Playwright's modern capabilities and Python's simplicity.

### Design Goals

1. **Functional Parity**: Maintain 100% of existing RAPTOR functionality
2. **Modern Architecture**: Leverage Playwright's async capabilities and modern browser automation
3. **Pythonic Design**: Follow Python best practices and idioms
4. **Backward Compatibility**: Support existing DDFE element definitions and DDDB test data
5. **Enhanced Performance**: Improve test execution speed through Playwright's efficiency
6. **Better Maintainability**: Cleaner code structure with comprehensive documentation

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Test Scripts (pytest)                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  RAPTOR Core Framework                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Browser   │  │  Element   │  │  Session   │           │
│  │  Manager   │  │  Manager   │  │  Manager   │           │
│  └────────────┘  └────────────┘  └────────────┘           │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Database  │  │   Config   │  │  Reporter  │           │
│  │  Manager   │  │  Manager   │  │            │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Page Object Layer (POM)                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Base Page │  │   Table    │  │  V3 Pages  │           │
│  │            │  │  Manager   │  │            │           │
│  └────────────┘  └────────────┘  └────────────┘           │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    Playwright API                            │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
raptor/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── browser_manager.py      # Browser lifecycle management
│   ├── element_manager.py      # Element location and interaction
│   ├── session_manager.py      # Session persistence
│   ├── config_manager.py       # Configuration handling
│   └── exceptions.py           # Custom exceptions
├── database/
│   ├── __init__.py
│   ├── database_manager.py     # Database operations
│   └── connection_pool.py      # Connection pooling
├── pages/
│   ├── __init__.py
│   ├── base_page.py           # Base page object
│   ├── table_manager.py       # Table operations
│   └── v3/                    # V3-specific pages
│       ├── __init__.py
│       ├── home_page.py
│       └── ...
├── utils/
│   ├── __init__.py
│   ├── logger.py              # Logging utilities
│   ├── reporter.py            # Test reporting
│   └── helpers.py             # Helper functions
├── config/
│   ├── __init__.py
│   ├── settings.yaml          # Default settings
│   └── environments/          # Environment configs
│       ├── dev.yaml
│       ├── staging.yaml
│       └── prod.yaml
└── tests/
    ├── __init__.py
    ├── conftest.py            # pytest fixtures
    └── ...
```

## Components and Interfaces

### 1. Browser Manager (`raptor/core/browser_manager.py`)

**Purpose**: Manage browser lifecycle, contexts, and sessions

**Key Methods**:
```python
class BrowserManager:
    async def launch_browser(browser_type: str, headless: bool = False) -> Browser
    async def create_context(**options) -> BrowserContext
    async def create_page(context: BrowserContext) -> Page
    async def close_browser()
    async def save_session(session_id: str, cdp_url: str)
    async def restore_session(session_id: str) -> Page
```

**Java Equivalent**: `Global.java` (driver management) + `Common.createDriverFromSession()`

### 2. Element Manager (`raptor/core/element_manager.py`)

**Purpose**: Locate and interact with web elements using multiple strategies

**Key Methods**:
```python
class ElementManager:
    async def locate_element(locator: str, fallback_locators: List[str] = None) -> Locator
    async def click(locator: str, **options)
    async def fill(locator: str, text: str, **options)
    async def select_option(locator: str, value: str, **options)
    async def hover(locator: str, **options)
    async def wait_for_element(locator: str, timeout: int = 20000)
    async def is_visible(locator: str) -> bool
    async def is_enabled(locator: str) -> bool
    async def get_text(locator: str) -> str
    async def get_attribute(locator: str, attribute: str) -> str
```

**Java Equivalent**: `Web.java` + `LFG.java` (element operations)

### 3. Session Manager (`raptor/core/session_manager.py`)

**Purpose**: Persist and restore browser sessions between test runs

**Key Methods**:
```python
class SessionManager:
    async def save_session(page: Page, session_name: str)
    async def restore_session(session_name: str) -> Page
    async def list_sessions() -> List[str]
    async def delete_session(session_name: str)
    def get_session_info(session_name: str) -> Dict
```

**Java Equivalent**: `Common.createDriverFromSession()` + session storage logic

### 4. Database Manager (`raptor/database/database_manager.py`)

**Purpose**: Handle DDFE and DDDB database operations

**Key Methods**:
```python
class DatabaseManager:
    def __init__(self, connection_string: str, user: str, password: str)
    async def connect()
    async def disconnect()
    async def execute_query(sql: str) -> List[Dict]
    async def execute_update(sql: str) -> int
    async def import_data(table: str, test_id: int, iteration: int, instance: int) -> Dict
    async def export_data(table: str, pk_id: int, field: str, value: str)
    async def get_field(table: str, field: str, pk_id: int) -> str
```

**Java Equivalent**: `Dms.java` + `Common.databaseImport()`, `Common.databaseExport()`, etc.

### 5. Configuration Manager (`raptor/core/config_manager.py`)

**Purpose**: Load and manage configuration settings

**Key Methods**:
```python
class ConfigManager:
    def __init__(self, config_path: str = None)
    def load_config(environment: str = "dev") -> Dict
    def get(key: str, default: Any = None) -> Any
    def set(key: str, value: Any)
    def get_browser_options() -> Dict
    def get_timeout(timeout_type: str = "default") -> int
```

**Java Equivalent**: `Global.java` (configuration variables)

### 6. Base Page (`raptor/pages/base_page.py`)

**Purpose**: Base class for all page objects with common functionality

**Key Methods**:
```python
class BasePage:
    def __init__(self, page: Page, element_manager: ElementManager)
    async def navigate(url: str)
    async def wait_for_load()
    async def take_screenshot(name: str)
    async def get_title() -> str
    async def get_url() -> str
    async def execute_script(script: str, *args)
```

**Java Equivalent**: `Common.java` (common page operations)

### 7. Table Manager (`raptor/pages/table_manager.py`)

**Purpose**: Specialized operations for data tables

**Key Methods**:
```python
class TableManager:
    def __init__(self, page: Page, element_manager: ElementManager)
    async def find_row_by_key(table_locator: str, key_column: int, key_value: str) -> int
    async def get_cell_value(table_locator: str, row: int, column: int) -> str
    async def set_cell_value(table_locator: str, row: int, column: int, value: str)
    async def click_cell(table_locator: str, row: int, column: int)
    async def get_row_count(table_locator: str) -> int
    async def search_table(table_locator: str, search_text: str, case_sensitive: bool = False) -> List[int]
```

**Java Equivalent**: `Table.java` + table-related methods in `Web.java`

## Data Models

### Element Definition (from DDFE)

```python
@dataclass
class ElementDefinition:
    pv_name: str                    # Primary identifier
    application_name: str           # Application context
    field_type: str                 # Element type (button, textbox, etc.)
    locator_primary: str            # Primary locator strategy
    locator_fallback1: str = None   # First fallback locator
    locator_fallback2: str = None   # Second fallback locator
    frame: str = None               # Frame context if applicable
    table_column: int = None        # Table column index
    table_key: int = None           # Table key column
    analyst: str = None             # Creator/owner
```

### Test Data (from DDDB)

```python
@dataclass
class TestData:
    pk_id: int                      # Primary key
    test_id: int                    # Test identifier
    iteration: int                  # Iteration number
    instance: int                   # Instance number
    fk_id: int = None               # Foreign key for sub-tables
    action: str = None              # Action to perform
    err_msg: str = None             # Expected error message
    data_fields: Dict[str, Any] = field(default_factory=dict)  # Dynamic fields
```

### Session Information

```python
@dataclass
class SessionInfo:
    session_id: str                 # Unique session identifier
    cdp_url: str                    # Chrome DevTools Protocol URL
    browser_type: str               # chromium, firefox, webkit
    created_at: datetime            # Session creation time
    last_accessed: datetime         # Last access time
    metadata: Dict[str, Any] = field(default_factory=dict)  # Additional info
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Browser Launch Consistency
*For any* browser type (Chromium, Firefox, WebKit), launching a browser should result in a valid browser instance that can create contexts and pages.
**Validates: Requirements 1.1**

### Property 2: Element Location Fallback
*For any* element with multiple locator strategies, if the primary locator fails, the system should automatically attempt fallback locators in order until one succeeds or all fail.
**Validates: Requirements 2.2**

### Property 3: Session Persistence Round-Trip
*For any* browser session, saving and then restoring the session should result in the same browser state (URL, cookies, storage).
**Validates: Requirements 3.1, 3.2**

### Property 4: Database Query Idempotence
*For any* database query with the same parameters, executing it multiple times should return the same results (assuming no data changes).
**Validates: Requirements 4.1**

### Property 5: Element Interaction Retry
*For any* element interaction that fails due to timing, the system should retry with exponential backoff up to the configured timeout.
**Validates: Requirements 5.1, 5.2**

### Property 6: Click Method Equivalence
*For any* clickable element, using click(), clickXY(), or JavaScript click should all result in the element being clicked successfully.
**Validates: Requirements 6.2**

### Property 7: Verification Non-Blocking
*For any* soft assertion, verification failures should not halt test execution but should be collected and reported at the end.
**Validates: Requirements 7.5**

### Property 8: Table Row Location Consistency
*For any* table with a key column, locating a row by key value should always return the same row index for the same key.
**Validates: Requirements 8.1**

### Property 9: Screenshot Capture Reliability
*For any* test failure, a screenshot should be captured and saved with a unique identifier.
**Validates: Requirements 9.1**

### Property 10: Configuration Environment Isolation
*For any* environment configuration, loading a specific environment should not affect other environment settings.
**Validates: Requirements 10.2**

### Property 11: Error Context Preservation
*For any* error or exception, the system should preserve the full stack trace and context information for debugging.
**Validates: Requirements 11.1**

### Property 12: Parallel Test Isolation
*For any* tests running in parallel, each test should have its own isolated browser context that doesn't interfere with others.
**Validates: Requirements 12.4**

## Error Handling

### Exception Hierarchy

```python
class RaptorException(Exception):
    """Base exception for all RAPTOR errors"""
    pass

class ElementNotFoundException(RaptorException):
    """Raised when an element cannot be located"""
    pass

class ElementNotInteractableException(RaptorException):
    """Raised when an element exists but cannot be interacted with"""
    pass

class TimeoutException(RaptorException):
    """Raised when an operation exceeds the timeout"""
    pass

class DatabaseException(RaptorException):
    """Raised for database-related errors"""
    pass

class SessionException(RaptorException):
    """Raised for session management errors"""
    pass

class ConfigurationException(RaptorException):
    """Raised for configuration-related errors"""
    pass
```

### Error Handling Strategy

1. **Graceful Degradation**: Attempt fallback strategies before failing
2. **Detailed Logging**: Log full context including element locators, timeouts, and stack traces
3. **Screenshot on Failure**: Automatically capture screenshots for visual debugging
4. **Retry Logic**: Implement exponential backoff for transient failures
5. **Clean Cleanup**: Ensure resources are released even after failures

## Testing Strategy

### Unit Testing

**Framework**: pytest with pytest-asyncio for async tests

**Coverage Areas**:
- Element location with various locator strategies
- Database connection and query execution
- Configuration loading and validation
- Session save/restore operations
- Error handling and exception raising

**Example Unit Test**:
```python
@pytest.mark.asyncio
async def test_element_location_with_fallback():
    """Test that fallback locators are tried when primary fails"""
    element_manager = ElementManager(page)
    
    # Primary locator fails, fallback should succeed
    locator = await element_manager.locate_element(
        "css=#nonexistent",
        fallback_locators=["css=#existing", "xpath=//div[@id='existing']"]
    )
    
    assert locator is not None
    assert await locator.is_visible()
```

### Property-Based Testing

**Framework**: Hypothesis for property-based testing

**Test Configuration**: Minimum 100 iterations per property test

**Property Test Examples**:

```python
from hypothesis import given, strategies as st

@given(
    browser_type=st.sampled_from(["chromium", "firefox", "webkit"]),
    headless=st.booleans()
)
@pytest.mark.asyncio
async def test_property_browser_launch_consistency(browser_type, headless):
    """Property 1: Browser launch should always succeed for valid types"""
    browser_manager = BrowserManager()
    browser = await browser_manager.launch_browser(browser_type, headless)
    
    assert browser is not None
    assert browser.is_connected()
    
    await browser_manager.close_browser()

@given(
    primary_locator=st.text(min_size=5),
    fallback_locators=st.lists(st.text(min_size=5), min_size=1, max_size=3)
)
@pytest.mark.asyncio
async def test_property_element_fallback(primary_locator, fallback_locators):
    """Property 2: Fallback locators should be attempted in order"""
    # Test implementation
    pass
```

### Integration Testing

**Scope**: Test interactions between components

**Test Areas**:
- Browser + Element Manager integration
- Database + Configuration integration
- Session Manager + Browser Manager integration
- Page Objects + Element Manager integration

### End-to-End Testing

**Scope**: Full workflow tests using actual applications

**Test Scenarios**:
- Complete login flow with session persistence
- Data-driven test execution with DDDB
- Multi-page navigation with element interactions
- Table operations with data validation

## Performance Considerations

### Optimization Strategies

1. **Async/Await**: Leverage Python's asyncio for concurrent operations
2. **Connection Pooling**: Reuse database connections
3. **Session Reuse**: Minimize browser launches by reusing sessions
4. **Lazy Loading**: Load configurations and resources only when needed
5. **Caching**: Cache element locators and frequently accessed data

### Performance Targets

- Framework initialization: < 5 seconds
- Element location: < 20 seconds (configurable)
- Session restore: < 3 seconds
- Database query: < 2 seconds
- Page load: < 30 seconds (configurable)

## Security Considerations

1. **Credential Management**: Store credentials securely using environment variables or secret management
2. **SQL Injection Prevention**: Use parameterized queries exclusively
3. **Session Security**: Encrypt session data at rest
4. **Audit Logging**: Log all database modifications
5. **Access Control**: Implement role-based access for sensitive operations

## Migration Strategy

### Phase 1: Core Framework (Weeks 1-2)
- Implement exception hierarchy
- Create Browser Manager
- Create Element Manager foundation
- Implement Configuration Manager

### Phase 2: Database & Session (Week 3)
- Implement Database Manager
- Create Session Manager
- Implement connection pooling

### Phase 3: Page Objects (Week 4)
- Create Base Page class
- Implement Table Manager
- Convert V3 page objects

### Phase 4: Testing & Utilities (Week 5)
- Implement test reporter
- Create pytest fixtures
- Add helper utilities

### Phase 5: Advanced Features (Week 6)
- CLI implementation
- Migration utilities
- Performance optimization

### Phase 6: Validation (Ongoing)
- Unit test coverage
- Property-based testing
- Integration testing
- Documentation

## Java to Python Class Mapping

| Java Class | Python Module | Primary Responsibility |
|------------|---------------|------------------------|
| `Common.java` | `raptor/pages/base_page.py` | Common page operations, error handling |
| `Web.java` | `raptor/core/element_manager.py` | Element interactions |
| `Global.java` | `raptor/core/config_manager.py` | Configuration and global state |
| `Table.java` | `raptor/pages/table_manager.py` | Table-specific operations |
| `Dms.java` | `raptor/database/database_manager.py` | Database operations |
| `LFG.java` | `raptor/core/element_manager.py` | Element location and framework ops |
| `V3/*.java` | `raptor/pages/v3/*.py` | V3-specific page objects |

## Key Method Conversions

### Click Operations

| Java Method | Python Method | Notes |
|-------------|---------------|-------|
| `click()` | `async def click(locator)` | Standard click |
| `clickXY()` | `async def click_at_position(locator)` | Position-based click |
| `clickIfExists()` | `async def click_if_exists(locator)` | Conditional click |
| `clickSync()` | `async def click_with_sync(locator)` | Click with spinner wait |
| `doubleClick()` | `async def double_click(locator)` | Double click |

### Verification Operations

| Java Method | Python Method | Notes |
|-------------|---------------|-------|
| `verifyExists()` | `async def verify_exists(locator)` | Assert element exists |
| `verifyNotExists()` | `async def verify_not_exists(locator)` | Assert element doesn't exist |
| `verifyEnabled()` | `async def verify_enabled(locator)` | Assert element is enabled |
| `verifyDisabled()` | `async def verify_disabled(locator)` | Assert element is disabled |

### Database Operations

| Java Method | Python Method | Notes |
|-------------|---------------|-------|
| `databaseImport()` | `async def import_data()` | Load test data from DDDB |
| `databaseExport()` | `async def export_data()` | Save results to DDDB |
| `databaseQuery()` | `async def query_field()` | Query single field |
| `databaseExec()` | `async def execute_update()` | Execute SQL update |

## Dependencies

### Core Dependencies
```
playwright>=1.40.0
pytest>=7.4.0
pytest-asyncio>=0.21.0
pyyaml>=6.0
python-dotenv>=1.0.0
```

### Database Dependencies
```
pyodbc>=5.0.0          # SQL Server
pymssql>=2.2.0         # Alternative SQL Server driver
```

### Testing Dependencies
```
hypothesis>=6.90.0     # Property-based testing
pytest-cov>=4.1.0      # Code coverage
pytest-html>=4.1.0     # HTML reports
```

### Optional Dependencies
```
allure-pytest>=2.13.0  # Allure reporting
pytest-xdist>=3.5.0    # Parallel execution
```

## Documentation Requirements

1. **API Documentation**: Comprehensive docstrings for all public methods
2. **User Guide**: Step-by-step guide for test developers
3. **Migration Guide**: Instructions for converting Java tests to Python
4. **Configuration Guide**: Detailed configuration options
5. **Troubleshooting Guide**: Common issues and solutions
6. **Examples**: Working examples for all major features

## Success Metrics

1. **Code Coverage**: >80% unit test coverage
2. **Performance**: 30% faster than Java/Selenium implementation
3. **Reliability**: >95% test stability
4. **Adoption**: 100% of team trained within 3 months
5. **Migration**: All critical tests migrated within 6 months
