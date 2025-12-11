# Running Property-Based Tests

## Quick Start

### 1. Install Playwright Browsers

```bash
cd raptor-python-playwright
playwright install chromium
```

### 2. Run All Property Tests

```bash
# Run all property tests
pytest tests/test_element_manager.py -k "test_property" -v

# Run with statistics
pytest tests/test_element_manager.py -k "test_property" -v --hypothesis-show-statistics
```

### 3. Run Specific Property Tests

```bash
# Property 1: Browser Launch Consistency
pytest tests/test_browser_manager.py::test_property_browser_launch_consistency -v

# Property 2: Element Location Fallback
pytest tests/test_element_manager.py::test_property_element_fallback_order -v

# Property 6: Click Method Equivalence
pytest tests/test_element_manager.py -k "test_property_click" -v
```

## Property Test Coverage

| Property | Test Function | Status | Examples |
|----------|--------------|--------|----------|
| Property 1: Browser Launch | test_property_browser_launch_consistency | ✅ | 100 |
| Property 2: Element Fallback | test_property_element_fallback_order | ✅ | 100 |
| Property 2: All Fallbacks Fail | test_property_all_fallbacks_fail | ✅ | 100 |
| Property 2: Same Element | test_property_fallback_finds_same_element | ✅ | 100 |
| Property 2: Early Termination | test_property_fallback_stops_at_first_success | ✅ | 50 |
| Property 6: Click Equivalence | test_property_click_method_equivalence | ✅ | 100 |
| Property 6: Click Tracking | test_property_click_idempotency_tracking | ✅ | 100 |
| Property 6: Fallback Equivalence | test_property_click_with_fallback_equivalence | ✅ | 100 |
| Property 6: Strategy Equivalence | test_property_click_locator_strategy_equivalence | ✅ | 50 |

## Troubleshooting

### Browser Not Installed

**Error**:
```
Error: Executable doesn't exist at .../chromium.../chrome.exe
```

**Solution**:
```bash
playwright install chromium
```

### Network Issues During Browser Install

**Error**:
```
Error: Download failed: size mismatch
```

**Solutions**:
1. Try again (network may be temporarily unavailable)
2. Use a different network connection
3. Install manually from Playwright releases

### Test Timeout

**Error**:
```
TimeoutError: Timeout 2000ms exceeded
```

**Solution**: Increase timeout in test configuration or individual tests

### Hypothesis Finds Counterexample

**What it means**: Hypothesis found input values that cause the test to fail

**What to do**:
1. Analyze the failing example shown in output
2. Determine if it's a:
   - Test bug (fix the test)
   - Implementation bug (fix the code)
   - Specification issue (discuss with team)

## Expected Output

### Successful Run

```
tests/test_element_manager.py::test_property_click_method_equivalence PASSED [100 examples]
tests/test_element_manager.py::test_property_click_idempotency_tracking PASSED [100 examples]
tests/test_element_manager.py::test_property_click_with_fallback_equivalence PASSED [100 examples]
tests/test_element_manager.py::test_property_click_locator_strategy_equivalence PASSED [50 examples]

====== 4 passed in 45.23s ======
```

### With Statistics

```
tests/test_element_manager.py::test_property_click_method_equivalence PASSED
  - 100 examples, 0 failing
  - Tried 100 examples
  - Typical runtimes: 50-200ms per example

====== 4 passed in 45.23s ======
```

## Performance Notes

- Each property test runs 50-100 examples
- Each example launches a browser page
- Total runtime: ~30-60 seconds for all property tests
- Can be parallelized with pytest-xdist

## CI/CD Integration

Add to your CI pipeline:

```yaml
- name: Install Playwright Browsers
  run: playwright install chromium

- name: Run Property Tests
  run: pytest tests/ -k "test_property" -v --hypothesis-show-statistics
```

## Related Documentation

- [Property Test: Click Equivalence](./PROPERTY_TEST_CLICK_EQUIVALENCE.md)
- [Property Test: Element Fallback](./PROPERTY_TEST_ELEMENT_FALLBACK.md)
- [Property Test: Browser Launch](./PROPERTY_TEST_BROWSER_LAUNCH.md)
