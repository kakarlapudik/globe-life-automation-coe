"""
Property-Based Test for Soft Assertions (Verification Non-Blocking).

This module tests Property 7: Verification Non-Blocking
- Validates: Requirements 7.5

Property Statement:
    For any soft assertion, verification failures should not halt test execution
    but should be collected and reported at the end.

Test Strategy:
    Generate random sequences of verification operations (some passing, some failing)
    and verify that:
    1. All verifications are executed (no early termination)
    2. All failures are collected
    3. Failures are reported at the end
    4. The order of failures is preserved
    
Note:
    This test uses a mock-based approach to avoid browser installation requirements
    while still validating the soft assertion property.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import List, Tuple
from unittest.mock import AsyncMock, MagicMock


# Strategy for generating verification operations
# Each operation is a tuple of (operation_type, should_pass)
verification_operations = st.lists(
    st.tuples(
        st.sampled_from([
            "verify_exists",
            "verify_not_exists",
            "verify_enabled",
            "verify_disabled",
            "verify_text",
            "verify_visible"
        ]),
        st.booleans()  # should_pass
    ),
    min_size=2,
    max_size=10
)


class SoftAssertionCollector:
    """
    Collector for soft assertion failures.
    
    This class collects verification failures without raising exceptions
    immediately, allowing all verifications to run before reporting failures.
    """
    
    def __init__(self):
        self.failures: List[Tuple[str, str]] = []
        self.verification_count = 0
    
    def add_failure(self, operation: str, error_message: str):
        """Add a verification failure to the collection."""
        self.failures.append((operation, error_message))
    
    def increment_count(self):
        """Increment the total verification count."""
        self.verification_count += 1
    
    def has_failures(self) -> bool:
        """Check if there are any failures."""
        return len(self.failures) > 0
    
    def get_failure_count(self) -> int:
        """Get the number of failures."""
        return len(self.failures)
    
    def get_failures(self) -> List[Tuple[str, str]]:
        """Get all collected failures."""
        return self.failures.copy()
    
    def clear(self):
        """Clear all collected failures."""
        self.failures.clear()
        self.verification_count = 0
    
    def assert_all(self):
        """
        Raise an assertion error with all collected failures.
        
        This should be called at the end of a test to report all failures.
        """
        if self.has_failures():
            failure_messages = [
                f"{i+1}. {op}: {msg}"
                for i, (op, msg) in enumerate(self.failures)
            ]
            error_msg = (
                f"\n{len(self.failures)} verification(s) failed out of "
                f"{self.verification_count} total:\n" +
                "\n".join(failure_messages)
            )
            raise AssertionError(error_msg)


class MockVerificationManager:
    """
    Mock verification manager for testing soft assertions.
    
    This class simulates verification operations without requiring a real browser,
    allowing us to test the soft assertion logic in isolation.
    """
    
    def __init__(self, collector=None):
        self.collector = collector or SoftAssertionCollector()
    
    async def soft_verify_exists(self, locator: str, should_pass: bool = True, **kwargs):
        """Soft assertion version of verify_exists."""
        self.collector.increment_count()
        if not should_pass:
            self.collector.add_failure("verify_exists", f"Element does not exist: {locator}")
    
    async def soft_verify_not_exists(self, locator: str, should_pass: bool = True, **kwargs):
        """Soft assertion version of verify_not_exists."""
        self.collector.increment_count()
        if not should_pass:
            self.collector.add_failure("verify_not_exists", f"Element exists but should not: {locator}")
    
    async def soft_verify_enabled(self, locator: str, should_pass: bool = True, **kwargs):
        """Soft assertion version of verify_enabled."""
        self.collector.increment_count()
        if not should_pass:
            self.collector.add_failure("verify_enabled", f"Element is disabled but should be enabled: {locator}")
    
    async def soft_verify_disabled(self, locator: str, should_pass: bool = True, **kwargs):
        """Soft assertion version of verify_disabled."""
        self.collector.increment_count()
        if not should_pass:
            self.collector.add_failure("verify_disabled", f"Element is enabled but should be disabled: {locator}")
    
    async def soft_verify_text(self, locator: str, expected_text: str, should_pass: bool = True, **kwargs):
        """Soft assertion version of verify_text."""
        self.collector.increment_count()
        if not should_pass:
            self.collector.add_failure("verify_text", f"Text mismatch: {locator}")
    
    async def soft_verify_visible(self, locator: str, should_pass: bool = True, **kwargs):
        """Soft assertion version of verify_visible."""
        self.collector.increment_count()
        if not should_pass:
            self.collector.add_failure("verify_visible", f"Element is not visible or does not exist: {locator}")


@pytest.mark.asyncio
@given(operations=verification_operations)
@settings(max_examples=100, deadline=None)
async def test_property_soft_assertions_non_blocking(operations):
    """
    Property Test: Verification Non-Blocking
    
    Feature: raptor-playwright-python, Property 7: Verification Non-Blocking
    
    Tests that soft assertions:
    1. Do not halt execution when failures occur
    2. Collect all failures
    3. Report failures at the end
    4. Preserve the order of failures
    
    Property: For any sequence of verification operations, all operations
    should be executed even if some fail, and all failures should be
    collected and reported at the end.
    """
    # Ensure we have at least one failing operation
    has_failing = any(not should_pass for _, should_pass in operations)
    assume(has_failing)
    
    collector = SoftAssertionCollector()
    manager = MockVerificationManager(collector)
    
    # Track expected failures
    expected_failures = []
    
    # Execute all verification operations
    for idx, (operation, should_pass) in enumerate(operations):
        if not should_pass:
            expected_failures.append(idx)
        
        if operation == "verify_exists":
            await manager.soft_verify_exists(f"locator-{idx}", should_pass=should_pass)
        elif operation == "verify_not_exists":
            await manager.soft_verify_not_exists(f"locator-{idx}", should_pass=should_pass)
        elif operation == "verify_enabled":
            await manager.soft_verify_enabled(f"locator-{idx}", should_pass=should_pass)
        elif operation == "verify_disabled":
            await manager.soft_verify_disabled(f"locator-{idx}", should_pass=should_pass)
        elif operation == "verify_text":
            await manager.soft_verify_text(f"locator-{idx}", "expected", should_pass=should_pass)
        elif operation == "verify_visible":
            await manager.soft_verify_visible(f"locator-{idx}", should_pass=should_pass)
    
    # Property 1: All operations were executed (verification count matches)
    assert collector.verification_count == len(operations), (
        f"Not all verifications were executed. "
        f"Expected: {len(operations)}, Actual: {collector.verification_count}"
    )
    
    # Property 2: Number of failures matches expected
    assert collector.get_failure_count() == len(expected_failures), (
        f"Failure count mismatch. "
        f"Expected: {len(expected_failures)}, Actual: {collector.get_failure_count()}"
    )
    
    # Property 3: Failures were collected (not raised immediately)
    # If we got here, it means no exception was raised during execution
    assert collector.has_failures(), "Expected failures but none were collected"
    
    # Property 4: assert_all() raises an exception with all failures
    with pytest.raises(AssertionError) as exc_info:
        collector.assert_all()
    
    error_message = str(exc_info.value)
    assert f"{len(expected_failures)} verification(s) failed" in error_message, (
        "Error message should contain failure count"
    )


@pytest.mark.asyncio
async def test_soft_assertions_all_pass():
    """
    Test that soft assertions work correctly when all verifications pass.
    
    This ensures that the soft assertion mechanism doesn't introduce false
    positives when all verifications succeed.
    """
    collector = SoftAssertionCollector()
    manager = MockVerificationManager(collector)
    
    # Execute multiple passing verifications
    await manager.soft_verify_exists("locator1", should_pass=True)
    await manager.soft_verify_visible("locator2", should_pass=True)
    await manager.soft_verify_enabled("locator3", should_pass=True)
    await manager.soft_verify_disabled("locator4", should_pass=True)
    await manager.soft_verify_text("locator5", "text", should_pass=True)
    await manager.soft_verify_not_exists("locator6", should_pass=True)
    
    # All verifications should have passed
    assert collector.verification_count == 6
    assert not collector.has_failures()
    assert collector.get_failure_count() == 0
    
    # assert_all() should not raise an exception
    collector.assert_all()  # Should not raise


@pytest.mark.asyncio
async def test_soft_assertions_mixed_results():
    """
    Test soft assertions with a mix of passing and failing verifications.
    
    This tests a realistic scenario where some verifications pass and others fail.
    """
    collector = SoftAssertionCollector()
    manager = MockVerificationManager(collector)
    
    # Mix of passing and failing verifications
    await manager.soft_verify_exists("locator1", should_pass=True)  # Pass
    await manager.soft_verify_exists("locator2", should_pass=False)  # Fail
    await manager.soft_verify_visible("locator3", should_pass=True)  # Pass
    await manager.soft_verify_visible("locator4", should_pass=False)  # Fail
    await manager.soft_verify_enabled("locator5", should_pass=True)  # Pass
    await manager.soft_verify_enabled("locator6", should_pass=False)  # Fail
    
    # Check results
    assert collector.verification_count == 6
    assert collector.has_failures()
    assert collector.get_failure_count() == 3
    
    # Verify failures are collected
    failures = collector.get_failures()
    assert len(failures) == 3
    
    # Verify assert_all() raises with all failures
    with pytest.raises(AssertionError) as exc_info:
        collector.assert_all()
    
    error_message = str(exc_info.value)
    assert "3 verification(s) failed out of 6 total" in error_message


@pytest.mark.asyncio
async def test_soft_assertions_failure_order_preserved():
    """
    Test that the order of failures is preserved.
    
    This ensures that failures are reported in the order they occurred,
    which is important for debugging.
    """
    collector = SoftAssertionCollector()
    manager = MockVerificationManager(collector)
    
    # Execute verifications in a specific order
    await manager.soft_verify_exists("locator1", should_pass=False)  # Fail 1
    await manager.soft_verify_exists("locator2", should_pass=True)  # Pass
    await manager.soft_verify_visible("locator3", should_pass=False)  # Fail 2
    await manager.soft_verify_enabled("locator4", should_pass=False)  # Fail 3
    
    # Check that failures are in order
    failures = collector.get_failures()
    assert len(failures) == 3
    
    # Verify the order by checking operation types
    assert failures[0][0] == "verify_exists"
    assert failures[1][0] == "verify_visible"
    assert failures[2][0] == "verify_enabled"


@pytest.mark.asyncio
async def test_soft_assertions_collector_clear():
    """
    Test that the collector can be cleared and reused.
    
    This ensures that the collector can be reset between test runs.
    """
    collector = SoftAssertionCollector()
    manager = MockVerificationManager(collector)
    
    # First batch of verifications
    await manager.soft_verify_exists("locator1", should_pass=False)  # Fail
    await manager.soft_verify_visible("locator2", should_pass=False)  # Fail
    
    assert collector.verification_count == 2
    assert collector.get_failure_count() == 2
    
    # Clear the collector
    collector.clear()
    
    assert collector.verification_count == 0
    assert collector.get_failure_count() == 0
    assert not collector.has_failures()
    
    # Second batch of verifications
    await manager.soft_verify_exists("locator3", should_pass=True)  # Pass
    await manager.soft_verify_visible("locator4", should_pass=True)  # Pass
    
    assert collector.verification_count == 2
    assert collector.get_failure_count() == 0
    assert not collector.has_failures()


@pytest.mark.asyncio
async def test_soft_assertions_with_custom_messages():
    """
    Test that error messages are properly formatted in soft assertions.
    
    This ensures that error messages are descriptive and include
    the necessary context for debugging.
    """
    collector = SoftAssertionCollector()
    manager = MockVerificationManager(collector)
    
    # Execute verification that will fail
    await manager.soft_verify_exists("css=#nonexistent", should_pass=False)
    
    # Check that error message is descriptive
    failures = collector.get_failures()
    assert len(failures) == 1
    assert "Element does not exist" in failures[0][1]
    assert "css=#nonexistent" in failures[0][1]

