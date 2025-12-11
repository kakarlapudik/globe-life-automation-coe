# Performance Testing Quick Reference

## Quick Start

```bash
# Run all performance tests
pytest tests/test_performance.py -v

# Run with output
pytest tests/test_performance.py -v -s

# Run specific test
pytest tests/test_performance.py::test_framework_initialization_performance -v
```

## Performance Targets

| Metric | Target | Baseline (Java) | Improvement Goal |
|--------|--------|-----------------|------------------|
| Framework Init | < 5s | 8s | 37.5% faster |
| Element Location | < 20s | 25s | 20% faster |
| Session Restore | < 3s | 5s | 40% faster |
| Database Query | < 2s | 2.5s | 20% faster |
| Browser Launch | < 10s | 15s | 33% faster |

## Test Suite

### 1. Framework Initialization
- **Test**: `test_framework_initialization_performance`
- **Measures**: Time to initialize ConfigManager, BrowserManager, SessionManager, ElementManager
- **Target**: < 5 seconds

### 2. Element Location
- **Test**: `test_element_location_performance`
- **Measures**: Time to locate elements with CSS, XPath, text, and fallback strategies
- **Target**: < 20 seconds

### 3. Session Restore
- **Test**: `test_session_restore_performance`
- **Measures**: Time to save and restore browser sessions
- **Target**: < 3 seconds

### 4. Database Query
- **Test**: `test_database_query_performance`
- **Measures**: Time for SELECT and UPDATE queries
- **Target**: < 2 seconds
- **Note**: Requires database configuration

### 5. Browser Launch
- **Test**: `test_browser_launch_performance`
- **Measures**: Time to launch Chromium, Firefox, WebKit
- **Target**: < 10 seconds

### 6. Comprehensive Report
- **Test**: `test_generate_comprehensive_performance_report`
- **Generates**: Aggregated report with all results
- **Output**: `reports/performance/PERFORMANCE_REPORT.txt`

## Results Location

```
reports/performance/
├── framework_init_results.json
├── element_location_results.json
├── session_performance_results.json
├── database_performance_results.json
├── browser_launch_results.json
└── PERFORMANCE_REPORT.txt
```

## Interpreting Results

### Metrics Explained
- **Mean**: Average time across iterations
- **Median**: Middle value (less affected by outliers)
- **Min/Max**: Fastest/slowest execution
- **Std Dev**: Variability in measurements
- **Meets Target**: ✓ YES or ✗ NO

### Baseline Comparison
- **Improvement**: Time saved vs Java/Selenium
- **Percentage**: Relative performance gain
- **Status**: ✓ FASTER or ✗ SLOWER

## Common Issues

### Slow Initialization
- Check browser binary installation
- Verify disk I/O performance
- Close unnecessary applications

### Slow Element Location
- Use local test pages
- Prefer CSS over XPath
- Optimize locator strategies

### Slow Session Restore
- Ensure browser stays running
- Check CDP endpoint availability
- Use local browser instances

### Slow Database Queries
- Use local database
- Add indexes to columns
- Limit result set size

## Optimization Tips

### 1. Enable Connection Pooling
```python
db_manager = DatabaseManager(
    server="localhost",
    database="DDFE",
    use_pooling=True
)
```

### 2. Reuse Browser Sessions
```python
# Save once
await session_manager.save_session(page, "session_name")

# Restore in tests
page = await session_manager.restore_session("session_name")
```

### 3. Use Headless Mode
```python
await browser_manager.launch_browser("chromium", headless=True)
```

### 4. Parallel Execution
```bash
pytest -n auto tests/
```

## CI/CD Integration

```yaml
# GitHub Actions
- name: Run Performance Tests
  run: pytest tests/test_performance.py -v
  
- name: Upload Results
  uses: actions/upload-artifact@v2
  with:
    name: performance-results
    path: reports/performance/
```

## Configuration

Edit `test_performance.py` to adjust:

```python
# Number of iterations
PERF_ITERATIONS = 10

# Performance targets
TARGETS = {
    "framework_init": 5.0,
    "element_location": 20.0,
    "session_restore": 3.0,
    "database_query": 2.0,
    "browser_launch": 10.0,
}

# Java baseline for comparison
JAVA_BASELINE = {
    "framework_init": 8.0,
    "element_location": 25.0,
    "session_restore": 5.0,
    "database_query": 2.5,
    "browser_launch": 15.0,
}
```

## Success Criteria

Performance tests pass if:
1. ✓ Mean time < target threshold
2. ✓ 80%+ of tests pass
3. ✓ Improvement over Java baseline

## Example Output

```
======================================================================
Performance Test: framework_init
======================================================================
Iterations:        10
Mean Time:         3.245s
Median Time:       3.198s
Min Time:          2.987s
Max Time:          3.654s
Std Deviation:     0.198s
Target:            5.000s
Meets Target:      ✓ YES

Comparison to Java/Selenium Baseline:
Baseline Time:     8.000s
Improvement:       4.755s (59.4%)
Result:            ✓ FASTER
======================================================================
```

## View Results

```bash
# View comprehensive report
cat reports/performance/PERFORMANCE_REPORT.txt

# View JSON results
cat reports/performance/framework_init_results.json | python -m json.tool

# View all results
ls -lh reports/performance/
```

## Markers

```bash
# Run slow tests (includes performance)
pytest -m slow

# Run only performance tests
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

## Best Practices

1. ✓ Run on consistent hardware
2. ✓ Minimize background processes
3. ✓ Use realistic test data
4. ✓ Monitor system resources
5. ✓ Document environment specs

## Need Help?

- Full Guide: `docs/PERFORMANCE_TESTING_GUIDE.md`
- Troubleshooting: See "Common Issues" section above
- Configuration: Edit `tests/test_performance.py`

## Requirements

- Python 3.8+
- Playwright browsers installed
- pytest and pytest-asyncio
- Optional: Database configuration for DB tests
