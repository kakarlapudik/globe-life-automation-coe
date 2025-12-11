# Performance Testing README

## Overview

This directory contains comprehensive performance tests for the RAPTOR Python Playwright Framework. These tests measure and validate framework performance against the requirements specified in NFR-001.

## Quick Start

```bash
# Run all performance tests
pytest tests/test_performance.py -v

# Run with detailed output
pytest tests/test_performance.py -v -s

# Run specific test
pytest tests/test_performance.py::test_framework_initialization_performance -v
```

## Test Files

- `test_performance.py` - Complete performance test suite with 6 comprehensive tests

## Performance Tests

### 1. Framework Initialization (`test_framework_initialization_performance`)
- Measures time to initialize all core framework components
- Target: < 5 seconds
- Baseline: 8 seconds (Java/Selenium)

### 2. Element Location (`test_element_location_performance`)
- Measures time to locate elements using various strategies
- Target: < 20 seconds
- Baseline: 25 seconds (Java/Selenium)

### 3. Session Restore (`test_session_restore_performance`)
- Measures time to save and restore browser sessions
- Target: < 3 seconds
- Baseline: 5 seconds (Java/Selenium)

### 4. Database Query (`test_database_query_performance`)
- Measures time to execute database operations
- Target: < 2 seconds
- Baseline: 2.5 seconds (Java/Selenium)
- Note: Requires database configuration

### 5. Browser Launch (`test_browser_launch_performance`)
- Measures time to launch different browser types
- Target: < 10 seconds
- Baseline: 15 seconds (Java/Selenium)

### 6. Comprehensive Report (`test_generate_comprehensive_performance_report`)
- Generates aggregated performance report
- Compares all results with targets and baselines

## Results

Performance test results are saved in `reports/performance/`:

```
reports/performance/
├── framework_init_results.json
├── element_location_results.json
├── session_performance_results.json
├── database_performance_results.json
├── browser_launch_results.json
└── PERFORMANCE_REPORT.txt
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
```

## Documentation

- **Comprehensive Guide**: `docs/PERFORMANCE_TESTING_GUIDE.md`
- **Quick Reference**: `docs/PERFORMANCE_QUICK_REFERENCE.md`
- **Completion Summary**: `docs/TASK_43_COMPLETION_SUMMARY.md`

## Markers

Performance tests use the following pytest markers:

- `@pytest.mark.slow` - Marks test as slow running
- `@pytest.mark.performance` - Marks test as performance test
- `@pytest.mark.asyncio` - Marks test as async (auto-applied)
- `@pytest.mark.database` - Marks test as requiring database

## Running with Markers

```bash
# Run only performance tests
pytest -m performance

# Run slow tests (includes performance)
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

## Success Criteria

Performance tests pass if:
1. Mean execution time is below target threshold
2. At least 80% of all performance tests pass
3. Framework shows improvement over Java/Selenium baseline

## Troubleshooting

### Tests Taking Too Long
- Reduce `PERF_ITERATIONS` for faster testing
- Use headless mode (already default)
- Close unnecessary applications

### Database Tests Skipped
- Configure database connection in config
- Or skip database tests: `pytest -m "not database"`

### Browser Launch Failures
- Ensure Playwright browsers are installed: `playwright install`
- Check system resources (CPU, memory)

## CI/CD Integration

Add to your CI/CD pipeline:

```yaml
- name: Run Performance Tests
  run: pytest tests/test_performance.py -v
  
- name: Upload Results
  uses: actions/upload-artifact@v2
  with:
    name: performance-results
    path: reports/performance/
```

## Need Help?

- See `docs/PERFORMANCE_TESTING_GUIDE.md` for detailed documentation
- See `docs/PERFORMANCE_QUICK_REFERENCE.md` for quick reference
- Check troubleshooting section in the comprehensive guide
