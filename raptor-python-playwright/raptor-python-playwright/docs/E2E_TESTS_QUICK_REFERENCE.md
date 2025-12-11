# E2E Tests Quick Reference

## Quick Start

```bash
# Install browsers
playwright install chromium

# Run all E2E tests
pytest tests/test_e2e.py -v

# Run specific test class
pytest tests/test_e2e.py::TestE2ELoginWorkflow -v
```

## Test Classes

| Class | Tests | Purpose |
|-------|-------|---------|
| `TestE2ELoginWorkflow` | 2 | Authentication and session management |
| `TestE2EDataDrivenExecution` | 1 | Database integration and iterations |
| `TestE2EMultiPageNavigation` | 1 | Multi-page user journeys |
| `TestE2ETableOperations` | 1 | Table management workflows |

## Test Scenarios

### 1. Login Workflow

```python
# Test: test_complete_login_workflow_with_session_persistence
# Steps: Launch → Navigate → Fill Form → Submit → Verify → Save Session → Restore
# Duration: ~2-3 seconds
```

### 2. Data-Driven Execution

```python
# Test: test_complete_data_driven_workflow
# Steps: Load Data → Execute (x3) → Export Results → Verify
# Duration: ~5-7 seconds
```

### 3. Multi-Page Navigation

```python
# Test: test_complete_multi_page_shopping_workflow
# Steps: Login → Browse → Details → Cart → Checkout → Confirm → History
# Duration: ~8-10 seconds
```

### 4. Table Operations

```python
# Test: test_complete_table_management_workflow
# Steps: Load → Search → Read → Edit → Sort → Bulk Activate → Verify
# Duration: ~5-6 seconds
```

## Common Commands

```bash
# Run with output
pytest tests/test_e2e.py -v -s

# Run specific test
pytest tests/test_e2e.py::TestE2ELoginWorkflow::test_complete_login_workflow_with_session_persistence -v

# Generate HTML report
pytest tests/test_e2e.py --html=report.html

# Run in parallel
pytest tests/test_e2e.py -n 4
```

## Test Data

### Login
- Valid: `testuser` / `TestPass123!`
- Invalid: `wronguser` / `wrongpass`

### Data-Driven
- 3 iterations with different users
- Database: SQLite (auto-created)

### Table
- 5 users (2 inactive, 3 active)
- Roles: Admin, User, Manager

## Reports & Screenshots

```
reports/e2e/test_report_<timestamp>.html
screenshots/e2e_login_success.png
screenshots/e2e_order_confirmation.png
screenshots/e2e_table_operations_complete.png
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Browser not found | `playwright install chromium` |
| Test timeout | Increase timeout in test |
| Session not found | Verify session was saved first |
| Database error | Check SQLite is available |

## Key Features

✅ Complete workflow testing  
✅ Database integration  
✅ Session management  
✅ Multi-page navigation  
✅ Table operations  
✅ Screenshot capture  
✅ HTML reporting  
✅ Error handling  
✅ Async/await support  
✅ Cleanup guaranteed  

## Requirements Validated

- **NFR-002**: Reliability (>95% pass rate)
- **NFR-003**: Maintainability (PEP 8, documentation)

## Related Docs

- [E2E Tests Guide](E2E_TESTS_GUIDE.md) - Full documentation
- [Task 42 Summary](TASK_42_COMPLETION_SUMMARY.md) - Implementation details
- [Integration Tests](INTEGRATION_TESTS_QUICK_REFERENCE.md) - Integration testing
