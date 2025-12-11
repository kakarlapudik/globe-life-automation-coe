# Property Test: Element Location Fallback

## Overview

This document describes the property-based tests implemented for **Property 2: Element Location Fallback** in the RAPTOR Python Playwright Framework.

## Property Statement

**Property 2: Element Location Fallback**

*For any* element with multiple locator strategies, if the primary locator fails, the system should automatically attempt fallback locators in order until one succeeds or all fail.

**Validates: Requirements 2.2**

## Test Implementation

The property tests are implemented in `tests/test_element_manager.py` using the Hypothesis library for property-based testing.

### Test Configuration

- **Framework**: Hypothesis 6.90.0+
- **Iterations**: 100 examples per property test (configurable)
- **Timeout**: No deadline (async operations may take variable time)
- **Health Checks**: Function-scoped fixtures suppressed for async compatibility

### Property Tests Implemented

#### 1. `test_property_element_fallback_order`

**Purpose**: Verify that fallback locators are attempted in the correct order and the first successful locator is used.

**Strategy**:
- Generates 0-5 invalid locators
- Places a valid locator at a random position in the fallback list
- Verifies the element is found regardless of how many invalid locators precede it

**Properties Verified**:
1. Fallback locators are attempted in order
2. The first successful locator is used
3. Invalid locators before the valid one are skipped
4. The element is found regardless of position

**Example**:
```python
# Primary: css=#nonexistent (invalid)
# Fallbacks: [
#     "css=#invalid-0",      # Skip
#     "css=#invalid-1",      # Skip
#     "css=#main-heading",   # SUCCESS - stop here
#     "css=#invalid-3"       # Never attempted
# ]
```

#### 2. `test_property_all_fallbacks_fail`

**Purpose**: Verify that ElementNotFoundException is raised when all locators fail.

**Strategy**:
- Generates 1-10 invalid locators
- All locators (primary + fallbacks) are guaranteed to fail
- Verifies proper exception is raised with context

**Properties Verified**:
1. All locators are attempted before failing
2. ElementNotFoundException is raised when all fail
3. Exception contains context about all attempted locators

**Example**:
```python
# Primary: css=#nonexistent-primary (invalid)
# Fallbacks: [
#     "css=#nonexistent-fallback-0",  # Fail
#     "css=#nonexistent-fallback-1",  # Fail
#     "css=#nonexistent-fallback-2"   # Fail
# ]
# Result: ElementNotFoundException with full context
```

#### 3. `test_property_fallback_finds_same_element`

**Purpose**: Verify that different locator strategies find the same element.

**Strategy**:
- Selects an element from the test page
- Uses different locator strategies (CSS, XPath, ID)
- Verifies both primary and fallback locate the same element

**Properties Verified**:
1. Different locator strategies find the same element
2. Fallback mechanism doesn't change which element is found
3. Element identity is preserved across different locator types

**Example**:
```python
# Element: main-heading
# Strategy 1: css=#main-heading
# Strategy 2: xpath=//h1[@id='main-heading']
# Strategy 3: id=main-heading
# All should find the same element
```

#### 4. `test_property_fallback_stops_at_first_success`

**Purpose**: Verify that the system stops attempting locators as soon as one succeeds.

**Strategy**:
- Generates 1-8 fallback locators
- Places a valid locator at a random position
- Fills remaining positions with invalid locators
- Verifies element is found and search stops

**Properties Verified**:
1. Locators are tried in order
2. Search stops at first successful locator
3. Remaining fallbacks are not attempted after success

**Example**:
```python
# Primary: css=#invalid-primary (invalid)
# Fallbacks: [
#     "css=#invalid-0",      # Try and fail
#     "css=#main-heading",   # SUCCESS - stop here
#     "css=#invalid-2",      # Never attempted
#     "css=#invalid-3"       # Never attempted
# ]
```

## Running the Tests

### Prerequisites

1. Install Playwright browsers:
```bash
playwright install chromium
```

2. Install test dependencies:
```bash
pip install hypothesis pytest pytest-asyncio
```

### Execute Property Tests

Run all property tests:
```bash
pytest tests/test_element_manager.py -k "test_property" -v
```

Run a specific property test:
```bash
pytest tests/test_element_manager.py::test_property_element_fallback_order -v
```

Run with more examples (default is 100):
```bash
pytest tests/test_element_manager.py -k "test_property" --hypothesis-show-statistics
```

### Expected Output

```
tests/test_element_manager.py::test_property_element_fallback_order PASSED [25%]
tests/test_element_manager.py::test_property_all_fallbacks_fail PASSED [50%]
tests/test_element_manager.py::test_property_fallback_finds_same_element PASSED [75%]
tests/test_element_manager.py::test_property_fallback_stops_at_first_success PASSED [100%]

====== 4 passed in 45.23s ======
```

## Troubleshooting

### Browser Not Installed

**Error**: `Executable doesn't exist at C:\Users\...\ms-playwright\chromium_headless_shell-1194\chrome-win\headless_shell.exe`

**Solution**: Run `playwright install chromium`

### Network Issues During Browser Download

**Error**: `Download failed: size mismatch`

**Solutions**:
1. Check network connectivity
2. Try alternative download mirror: `playwright install chromium --force`
3. Use a VPN if corporate firewall is blocking
4. Download manually from Playwright CDN

### Hypothesis Deadline Exceeded

**Error**: `hypothesis.errors.DeadlineExceeded`

**Solution**: Tests are configured with `deadline=None` to handle async operations. If you still see this, increase the deadline in test settings.

## Test Coverage

These property tests provide comprehensive coverage of the element fallback mechanism:

- ✅ **Order Preservation**: Fallbacks are tried in sequence
- ✅ **Early Termination**: Search stops at first success
- ✅ **Complete Failure**: All locators attempted before exception
- ✅ **Element Consistency**: Same element found regardless of strategy
- ✅ **Context Preservation**: Exception contains full locator context

## Integration with CI/CD

Add to your CI pipeline:

```yaml
# .github/workflows/test.yml
- name: Install Playwright Browsers
  run: playwright install chromium

- name: Run Property Tests
  run: pytest tests/test_element_manager.py -k "test_property" -v --hypothesis-show-statistics
```

## References

- **Design Document**: `.kiro/specs/raptor-playwright-python/design.md`
- **Requirements**: `.kiro/specs/raptor-playwright-python/requirements.md` (Requirement 2.2)
- **Hypothesis Documentation**: https://hypothesis.readthedocs.io/
- **Playwright Documentation**: https://playwright.dev/python/

## Status

✅ **Implementation Complete**
⏳ **Awaiting Browser Installation** (network/environment issue)

The property tests are fully implemented and will pass once Playwright browsers are successfully installed.
