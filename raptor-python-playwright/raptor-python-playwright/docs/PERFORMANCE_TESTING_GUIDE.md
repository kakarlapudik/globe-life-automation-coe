# RAPTOR Performance Testing Guide

## Overview

This guide explains how to run and interpret performance tests for the RAPTOR Python Playwright Framework. Performance testing ensures the framework meets the required performance targets specified in NFR-001.

## Performance Targets

The framework has the following performance targets:

| Metric | Target | Java/Selenium Baseline | Goal |
|--------|--------|------------------------|------|
| Framework Initialization | < 5 seconds | 8 seconds | 37.5% faster |
| Element Location | < 20 seconds | 25 seconds | 20% faster |
| Session Restore | < 3 seconds | 5 seconds | 40% faster |
| Database Query | < 2 seconds | 2.5 seconds | 20% faster |
| Browser Launch | < 10 seconds | 15 seconds | 33% faster |

## Running Performance Tests

### Run All Performance Tests

```bash
# Run all performance tests
pytest tests/test_performance.py -v

# Run with detailed output
pytest tests/test_performance.py -v -s

# Run specific performance test
pytest tests/test_performance.py::test_framework_initialization_performance -v
```

### Run Performance Tests with Markers

```bash
# Run only slow tests (includes performance tests)
pytest -m slow

# Run only performance tests
pytest -m performance

# Skip slow tests
pytest -m "not slow"
```

### Performance Test Configuration

Performance tests use the following configuration:

- **Iterations**: 10 measurements per test (configurable via `PERF_ITERATIONS`)
- **Browser**: Chromium in headless mode
- **Environment**: Development configuration
- **Results Directory**: `reports/performance/`

## Performance Test Suite

### 1. Framework Initialization Performance

**Test**: `test_framework_initialization_performance`

**Measures**: Time to initialize core framework components:
- ConfigManager
- BrowserManager
- SessionManager
- ElementManager (with browser and page)

**Target**: < 5 seconds

**Example Output**:
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

### 2. Element Location Performance

**Test**: `test_element_location_performance`

**Measures**: Time to locate elements using various strategies:
- CSS selectors
- XPath
- Text locators
- Fallback strategies

**Target**: < 20 seconds (configurable timeout)

**Tests Multiple Scenarios**:
- Simple CSS selector
- XPath selector
- Text-based locator
- Fallback locator mechanism

### 3. Session Restore Performance

**Test**: `test_session_restore_performance`

**Measures**: Time to:
- Save a browser session
- Restore a saved session

**Target**: < 3 seconds for restore

**Use Case**: Session reuse reduces test startup time by avoiding full browser launches.

### 4. Database Query Performance

**Test**: `test_database_query_performance`

**Measures**: Time to execute:
- SELECT queries
- UPDATE queries
- Test data import
- Test result export

**Target**: < 2 seconds

**Note**: Requires database configuration. Test is skipped if database is not configured.

### 5. Browser Launch Performance

**Test**: `test_browser_launch_performance`

**Measures**: Time to launch browsers:
- Chromium
- Firefox (if available)
- WebKit (if available)

**Target**: < 10 seconds

**Comparison**: Tests all supported browsers and compares launch times.

### 6. Comprehensive Performance Report

**Test**: `test_generate_comprehensive_performance_report`

**Generates**: Aggregated performance report with:
- Summary of all performance tests
- Pass/fail status for each test
- Comparison with Java/Selenium baseline
- Overall success rate

**Output**: `reports/performance/PERFORMANCE_REPORT.txt`

## Interpreting Results

### Performance Metrics

Each performance test provides the following metrics:

- **Mean Time**: Average execution time across all iterations
- **Median Time**: Middle value when sorted (less affected by outliers)
- **Min/Max Time**: Fastest and slowest execution times
- **Standard Deviation**: Measure of variability in measurements
- **Target**: Required performance threshold
- **Meets Target**: Whether the test passes the performance requirement

### Baseline Comparison

Performance tests compare results against Java/Selenium baseline:

- **Improvement (seconds)**: Absolute time saved compared to baseline
- **Improvement (percentage)**: Relative performance improvement
- **Faster/Slower**: Whether RAPTOR is faster than the baseline

### Success Criteria

A performance test passes if:
1. Mean execution time is below the target threshold
2. At least 80% of all performance tests pass
3. Framework shows improvement over Java/Selenium baseline

## Performance Test Results

### Results Files

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

### JSON Result Format

```json
{
  "operation": "framework_init",
  "count": 10,
  "min": 2.987,
  "max": 3.654,
  "mean": 3.245,
  "median": 3.198,
  "stdev": 0.198,
  "target": 5.0,
  "baseline": 8.0,
  "meets_target": true,
  "vs_baseline": {
    "improvement_seconds": 4.755,
    "improvement_percentage": 59.4,
    "faster": true
  }
}
```

## Troubleshooting Performance Issues

### Slow Framework Initialization

**Symptoms**: Framework initialization exceeds 5 seconds

**Possible Causes**:
- Slow disk I/O for configuration loading
- Network delays in browser binary download
- System resource constraints

**Solutions**:
- Ensure browser binaries are pre-installed
- Use SSD for faster file access
- Close unnecessary applications

### Slow Element Location

**Symptoms**: Element location exceeds 20 seconds

**Possible Causes**:
- Network latency to test page
- Complex page with many elements
- Inefficient locator strategies

**Solutions**:
- Use local test pages for performance testing
- Optimize locator strategies (prefer CSS over XPath)
- Reduce timeout values for performance tests

### Slow Session Restore

**Symptoms**: Session restore exceeds 3 seconds

**Possible Causes**:
- Browser process crashed
- CDP endpoint not responding
- Network issues

**Solutions**:
- Ensure browser remains running between save/restore
- Check CDP endpoint availability
- Use local browser instances

### Slow Database Queries

**Symptoms**: Database queries exceed 2 seconds

**Possible Causes**:
- Network latency to database server
- Missing indexes on query columns
- Large result sets

**Solutions**:
- Use local database for performance testing
- Add indexes to frequently queried columns
- Limit result set size with TOP/LIMIT clauses

## Performance Optimization Tips

### 1. Use Connection Pooling

Enable database connection pooling to reuse connections:

```python
db_manager = DatabaseManager(
    server="localhost",
    database="DDFE",
    use_pooling=True,
    pool_min_size=2,
    pool_max_size=10
)
```

### 2. Reuse Browser Sessions

Save and restore browser sessions to avoid repeated launches:

```python
# Save session after login
await session_manager.save_session(page, "logged_in_session")

# Restore in subsequent tests
page = await session_manager.restore_session("logged_in_session")
```

### 3. Use Headless Mode

Run browsers in headless mode for better performance:

```python
await browser_manager.launch_browser("chromium", headless=True)
```

### 4. Optimize Locator Strategies

Use efficient locator strategies:
- Prefer CSS selectors over XPath
- Use specific selectors (IDs) when possible
- Avoid complex XPath expressions

### 5. Parallel Test Execution

Run tests in parallel with pytest-xdist:

```bash
pytest -n auto tests/
```

## Continuous Performance Monitoring

### CI/CD Integration

Add performance tests to your CI/CD pipeline:

```yaml
# GitHub Actions example
- name: Run Performance Tests
  run: |
    pytest tests/test_performance.py -v
    
- name: Upload Performance Results
  uses: actions/upload-artifact@v2
  with:
    name: performance-results
    path: reports/performance/
```

### Performance Regression Detection

Monitor performance trends over time:
1. Store performance results in a database or artifact repository
2. Compare current results with historical baseline
3. Alert on performance regressions (> 10% slower)

### Performance Benchmarking

Establish performance benchmarks for your environment:
1. Run performance tests on target hardware
2. Record baseline metrics
3. Update targets based on actual requirements

## Best Practices

1. **Run on Consistent Hardware**: Performance tests should run on the same hardware for consistent results
2. **Minimize Background Processes**: Close unnecessary applications during performance testing
3. **Use Realistic Test Data**: Test with data similar to production workloads
4. **Test Under Load**: Consider running performance tests with multiple parallel instances
5. **Monitor System Resources**: Track CPU, memory, and disk usage during tests
6. **Document Environment**: Record hardware specs, OS version, and configuration

## Performance Test Maintenance

### Updating Performance Targets

If performance targets need adjustment:

1. Update `TARGETS` dictionary in `test_performance.py`
2. Update baseline comparison in `JAVA_BASELINE`
3. Update documentation in this guide
4. Re-run tests to validate new targets

### Adding New Performance Tests

To add a new performance test:

1. Create a new test function in `test_performance.py`
2. Use `PerformanceMetrics` class to track measurements
3. Add target and baseline values to configuration
4. Update this documentation

## Example: Running Performance Tests

```bash
# 1. Ensure dependencies are installed
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Run performance tests
pytest tests/test_performance.py -v -s

# 4. View results
cat reports/performance/PERFORMANCE_REPORT.txt

# 5. Check individual test results
cat reports/performance/framework_init_results.json
```

## Performance Test Output Example

```
============================= test session starts ==============================
platform win32 -- Python 3.11.0, pytest-7.4.0, pluggy-1.3.0
rootdir: /path/to/raptor-python-playwright
plugins: asyncio-0.21.0, playwright-0.4.0
collected 6 items

tests/test_performance.py::test_framework_initialization_performance PASSED
tests/test_performance.py::test_element_location_performance PASSED
tests/test_performance.py::test_session_restore_performance PASSED
tests/test_performance.py::test_database_query_performance SKIPPED (database not configured)
tests/test_performance.py::test_browser_launch_performance PASSED
tests/test_performance.py::test_generate_comprehensive_performance_report PASSED

======================== 5 passed, 1 skipped in 125.43s ========================
```

## Conclusion

Performance testing ensures the RAPTOR Python Playwright Framework meets its performance requirements and provides measurable improvements over the Java/Selenium baseline. Regular performance testing helps identify regressions and optimization opportunities.

For questions or issues with performance testing, please refer to the troubleshooting section or contact the framework maintainers.
