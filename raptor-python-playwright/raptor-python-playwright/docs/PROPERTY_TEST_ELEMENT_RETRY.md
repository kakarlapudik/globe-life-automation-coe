# Property Test: Element Interaction Retry (Property 5)

## Overview

This document describes the property-based test implementation for **Property 5: Element Interaction Retry**, which validates that element interactions retry with exponential backoff when they fail due to timing issues.

## Property Statement

**Property 5: Element Interaction Retry**

*For any* element interaction that fails due to timing, the system should retry with exponential backoff up to the configured timeout.

**Validates: Requirements 5.1, 5.2**

## Test Implementation

The property test is implemented in `tests/test_element_manager.py` and consists of four complementary property tests:

### 1. Main Property Test: `test_property_element_interaction_retry`

**Purpose**: Verifies that retry mechanism works correctly when elements appear during the retry window.

**Strategy**: 
- Generates random retry configurations (max_retries, initial_delay, delay_before_appearance)
- Creates a page where an element appears after a calculated delay
- Attempts to click the element using `click_with_retry()`
- Verifies the element is found and clicked successfully
- Validates timing constraints

**Key Assertions**:
- Element is clicked successfully after retry
- Retry waits at least as long as the element appearance delay
- Retry doesn't take excessively long
- Handles cases where element appears too late

**Hypothesis Configuration**:
- `max_examples=100`: Runs 100 different random scenarios
- Generates `max_retries` from 1 to 5
- Generates `initial_delay` from 0.05s to 0.3s
- Generates `delay_before_appearance` from 0.1s to 1.0s

### 2. Exponential Backoff Timing Test: `test_property_retry_exponential_backoff_timing`

**Purpose**: Verifies that retry delays follow an exponential backoff pattern.

**Strategy**:
- Creates a page with no target element (forces all retries to fail)
- Measures total elapsed time for all retry attempts
- Calculates expected delay sum using geometric series formula
- Verifies actual timing matches exponential backoff expectations

**Key Assertions**:
- Total retry time matches expected exponential backoff calculation
- Timing falls within acceptable tolerance range (±20%)
- Backoff pattern is consistent across different configurations

**Formula Verification**:
```
Expected delay sum = initial_delay * (2^(max_retries-1) - 1)

For max_retries=3, initial_delay=0.2:
  Delays: 0.2s, 0.4s (total = 0.6s)
  Formula: 0.2 * (2^2 - 1) = 0.2 * 3 = 0.6s ✓

For max_retries=4, initial_delay=0.1:
  Delays: 0.1s, 0.2s, 0.4s (total = 0.7s)
  Formula: 0.1 * (2^3 - 1) = 0.1 * 7 = 0.7s ✓
```

### 3. Nth Attempt Success Test: `test_property_retry_succeeds_on_nth_attempt`

**Purpose**: Verifies that retry stops as soon as element interaction succeeds, without exhausting all attempts.

**Strategy**:
- Generates random configurations for max_retries and success_on_attempt
- Calculates when element should appear to succeed on target attempt
- Creates page with element appearing at calculated time
- Verifies retry succeeds on the expected attempt
- Confirms remaining attempts are not executed

**Key Assertions**:
- Element is clicked successfully on target attempt
- Timing matches expected delay for target attempt
- Retry doesn't continue after success
- Works for any attempt from 1 to max_retries

### 4. Retry with Fallback Test: `test_property_retry_with_fallback_locators`

**Purpose**: Verifies that retry mechanism works correctly with fallback locators.

**Strategy**:
- Generates random retry configurations
- Randomly chooses to use primary or fallback locator
- Creates page with delayed element
- Attempts click with retry using chosen locator strategy
- Verifies success regardless of locator type

**Key Assertions**:
- Retry works with fallback locators
- Element is found via fallback when primary fails
- Retry + fallback combination produces correct results
- Behavior is consistent whether using primary or fallback

## Test Execution

### Running the Property Tests

```bash
# Run all Property 5 tests
pytest tests/test_element_manager.py -k "test_property_element_interaction_retry or test_property_retry" -v

# Run with detailed output
pytest tests/test_element_manager.py::test_property_element_interaction_retry -v --tb=short

# Run with Hypothesis statistics
pytest tests/test_element_manager.py::test_property_element_interaction_retry -v --hypothesis-show-statistics
```

### Prerequisites

Before running the tests, ensure Playwright browsers are installed:

```bash
playwright install chromium
```

## Property Test Configuration

All property tests use the following Hypothesis settings:

```python
@settings(
    max_examples=100,  # Run 100 random test cases
    deadline=None,     # No deadline for async operations
    suppress_health_check=[HealthCheck.function_scoped_fixture]  # Allow function-scoped fixtures
)
```

## Expected Behavior

### Successful Retry Scenario

```
1. Element not found (attempt 1)
   - Wait: initial_delay (e.g., 0.1s)
   
2. Element not found (attempt 2)
   - Wait: initial_delay * 2 (e.g., 0.2s)
   
3. Element appears and is found (attempt 3)
   - Click succeeds
   - Remaining attempts (4, 5) are not executed
```

### Failed Retry Scenario

```
1. Element not found (attempt 1)
   - Wait: initial_delay (e.g., 0.1s)
   
2. Element not found (attempt 2)
   - Wait: initial_delay * 2 (e.g., 0.2s)
   
3. Element not found (attempt 3)
   - Wait: initial_delay * 4 (e.g., 0.4s)
   
4. All retries exhausted
   - Raise ElementNotFoundException
```

## Validation Against Requirements

### Requirement 5.1: Page Load Waiting

The retry mechanism ensures that elements are found even when pages load slowly or dynamically. The exponential backoff provides increasing wait times to accommodate various loading scenarios.

### Requirement 5.2: Dynamic Element Waiting

The retry mechanism handles dynamically appearing elements by:
- Attempting multiple times with increasing delays
- Stopping as soon as the element is found
- Providing configurable retry counts and delays
- Working with fallback locators for robust element location

## Edge Cases Covered

1. **Immediate Success**: Element available on first attempt (no retry needed)
2. **Late Success**: Element appears on last possible attempt
3. **Complete Failure**: Element never appears (all retries exhausted)
4. **Fallback Success**: Primary locator fails but fallback succeeds
5. **Variable Timing**: Different appearance delays and retry configurations
6. **Exponential Growth**: Proper doubling of delays between attempts

## Integration with ElementManager

The property tests validate the `click_with_retry()` method in `ElementManager`:

```python
async def click_with_retry(
    self,
    locator: str,
    fallback_locators: Optional[List[str]] = None,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    timeout: Optional[int] = None,
    **options
) -> None:
    """
    Click an element with exponential backoff retry logic.
    
    Attempts to click the element multiple times with increasing delays
    between attempts. Useful for handling transient failures or elements
    that may be temporarily obscured.
    """
```

## Troubleshooting

### Test Failures

If property tests fail, check:

1. **Timing Issues**: Adjust tolerance values if system is slow
2. **Browser Installation**: Ensure Playwright browsers are installed
3. **Async Handling**: Verify async/await patterns are correct
4. **Hypothesis Seed**: Use `--hypothesis-seed=<seed>` to reproduce failures

### Common Issues

**Issue**: Tests timeout or hang
**Solution**: Check that `deadline=None` is set in `@settings`

**Issue**: Browser not found
**Solution**: Run `playwright install chromium`

**Issue**: Timing assertions fail
**Solution**: Increase tolerance percentages or adjust test delays

## Related Documentation

- [Element Manager Implementation](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Property Test: Element Fallback](PROPERTY_TEST_ELEMENT_FALLBACK.md)
- [Property Test: Click Equivalence](PROPERTY_TEST_CLICK_EQUIVALENCE.md)
- [Requirements Document](../.kiro/specs/raptor-playwright-python/requirements.md)
- [Design Document](../.kiro/specs/raptor-playwright-python/design.md)

## Conclusion

The Property 5 tests provide comprehensive validation that the retry mechanism:
- Works correctly across various timing scenarios
- Uses proper exponential backoff
- Stops at first success
- Integrates with fallback locators
- Handles edge cases appropriately

These tests ensure that the RAPTOR framework can reliably interact with elements even in challenging timing situations, meeting the requirements for robust test automation.
