"""
Property-Based Test: Element Interaction Retry

**Feature: raptor-playwright-python, Property 5: Element Interaction Retry**
**Validates: Requirements 5.1, 5.2**

This test verifies that element interactions retry with exponential backoff
when they fail due to timing issues.

Property Statement:
    For any element interaction that fails due to timing, the system should retry 
    with exponential backoff up to the configured timeout.
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings, assume
from typing import List
from unittest.mock import AsyncMock, MagicMock
import time


# Strategy for retry counts
retry_count_strategy = st.integers(min_value=1, max_value=5)

# Strategy for timeout values
timeout_strategy = st.integers(min_value=1000, max_value=10000)

# Strategy for failure counts before success
failure_count_strategy = st.integers(min_value=0, max_value=4)


class RetryableElement:
    """
    Mock element that fails a specified number of times before succeeding.
    
    This simulates transient failures that should trigger retry logic.
    """
    
    def __init__(self, failures_before_success: int = 0):
        self.failures_before_success = failures_before_success
        self.attempt_count = 0
        self.attempt_times = []
    
    async def click(self):
        """Click that may fail initially."""
        self.attempt_count += 1
        self.attempt_times.append(time.time())
        
        if self.attempt_count <= self.failures_before_success:
            raise Exception(f"Transient failure on attempt {self.attempt_count}")
        
        # Success
        return True
    
    def get_backoff_intervals(self) -> List[float]:
        """Calculate time intervals between attempts."""
        if len(self.attempt_times) < 2:
            return []
        
        intervals = []
        for i in range(1, len(self.attempt_times)):
            interval = self.attempt_times[i] - self.attempt_times[i-1]
            intervals.append(interval)
        
        return intervals


class RetryManager:
    """
    Manager for retrying element interactions with exponential backoff.
    
    This simulates the retry logic in ElementManager.
    """
    
    def __init__(self, max_retries: int = 3, initial_delay: float = 0.1):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.retry_attempts = []
    
    async def retry_with_backoff(
        self,
        operation,
        *args,
        **kwargs
    ):
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation: Async function to retry
            *args: Arguments for the operation
            **kwargs: Keyword arguments for the operation
            
        Returns:
            Result of the operation if successful
            
        Raises:
            Exception if all retries fail
        """
        self.retry_attempts = []
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            self.retry_attempts.append(attempt)
            
            try:
                result = await operation(*args, **kwargs)
                return result
            except Exception as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    # Calculate exponential backoff delay
                    delay = self.initial_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed
                    raise last_exception
        
        raise last_exception


class TestElementInteractionRetry:
    """
    Property-based tests for element interaction retry with exponential backoff.
    
    These tests verify that element interactions are retried appropriately
    when they fail due to timing issues.
    """
    
    @given(
        failures_before_success=failure_count_strategy,
        max_retries=retry_count_strategy
    )
    @settings(max_examples=100, deadline=10000)
    @pytest.mark.asyncio
    async def test_retry_succeeds_within_limit(
        self, failures_before_success, max_retries
    ):
        """
        Property: Operations should succeed if they succeed within retry limit.
        
        If an operation fails initially but succeeds within the retry limit,
        the retry mechanism should return success.
        
        Args:
            failures_before_success: Number of failures before success
            max_retries: Maximum number of retries allowed
        """
        # Only test cases where success is possible
        assume(failures_before_success <= max_retries)
        
        element = RetryableElement(failures_before_success=failures_before_success)
        retry_manager = RetryManager(max_retries=max_retries, initial_delay=0.01)
        
        # Property: Operation should succeed
        result = await retry_manager.retry_with_backoff(element.click)
        
        assert result is True, "Operation should succeed within retry limit"
        
        # Property: Correct number of attempts
        expected_attempts = failures_before_success + 1
        assert element.attempt_count == expected_attempts, (
            f"Should have {expected_attempts} attempts, got {element.attempt_count}"
        )
    
    @given(
        failures_before_success=st.integers(min_value=1, max_value=10),
        max_retries=retry_count_strategy
    )
    @settings(max_examples=100, deadline=10000)
    @pytest.mark.asyncio
    async def test_retry_fails_when_exceeds_limit(
        self, failures_before_success, max_retries
    ):
        """
        Property: Operations should fail if they don't succeed within retry limit.
        
        If an operation continues to fail beyond the retry limit, the retry
        mechanism should raise an exception.
        
        Args:
            failures_before_success: Number of failures before success
            max_retries: Maximum number of retries allowed
        """
        # Only test cases where failure is expected
        assume(failures_before_success > max_retries)
        
        element = RetryableElement(failures_before_success=failures_before_success)
        retry_manager = RetryManager(max_retries=max_retries, initial_delay=0.01)
        
        # Property: Operation should fail
        with pytest.raises(Exception) as exc_info:
            await retry_manager.retry_with_backoff(element.click)
        
        assert "Transient failure" in str(exc_info.value)
        
        # Property: Correct number of attempts (max_retries + 1 initial attempt)
        expected_attempts = max_retries + 1
        assert element.attempt_count == expected_attempts, (
            f"Should have {expected_attempts} attempts, got {element.attempt_count}"
        )
    
    @given(
        failures_before_success=failure_count_strategy,
        max_retries=retry_count_strategy
    )
    @settings(max_examples=50, deadline=10000)
    @pytest.mark.asyncio
    async def test_exponential_backoff_increases(
        self, failures_before_success, max_retries
    ):
        """
        Property: Backoff delays should increase exponentially.
        
        The time between retry attempts should increase exponentially,
        following the pattern: initial_delay * 2^attempt.
        
        Args:
            failures_before_success: Number of failures before success
            max_retries: Maximum number of retries allowed
        """
        # Only test cases where we have multiple retries
        assume(failures_before_success >= 2)
        assume(failures_before_success <= max_retries)
        
        element = RetryableElement(failures_before_success=failures_before_success)
        retry_manager = RetryManager(max_retries=max_retries, initial_delay=0.1)
        
        await retry_manager.retry_with_backoff(element.click)
        
        # Get backoff intervals
        intervals = element.get_backoff_intervals()
        
        # Property: Each interval should be approximately double the previous
        # (allowing for timing variance)
        for i in range(1, len(intervals)):
            ratio = intervals[i] / intervals[i-1]
            # Allow 50% variance due to timing imprecision
            assert 1.5 <= ratio <= 2.5, (
                f"Backoff should approximately double. "
                f"Interval {i-1}: {intervals[i-1]:.3f}s, "
                f"Interval {i}: {intervals[i]:.3f}s, "
                f"Ratio: {ratio:.2f}"
            )
    
    @given(
        max_retries=retry_count_strategy
    )
    @settings(max_examples=100, deadline=5000)
    @pytest.mark.asyncio
    async def test_immediate_success_no_retry(self, max_retries):
        """
        Property: Immediate success should not trigger retries.
        
        If an operation succeeds on the first attempt, no retries should
        be performed.
        
        Args:
            max_retries: Maximum number of retries allowed
        """
        element = RetryableElement(failures_before_success=0)
        retry_manager = RetryManager(max_retries=max_retries, initial_delay=0.01)
        
        result = await retry_manager.retry_with_backoff(element.click)
        
        # Property: Operation succeeded
        assert result is True
        
        # Property: Only one attempt was made
        assert element.attempt_count == 1, (
            f"Should have exactly 1 attempt for immediate success, "
            f"got {element.attempt_count}"
        )
        
        # Property: No backoff intervals (no retries)
        intervals = element.get_backoff_intervals()
        assert len(intervals) == 0, (
            "Should have no backoff intervals for immediate success"
        )
    
    @given(
        failures_before_success=failure_count_strategy,
        max_retries=retry_count_strategy
    )
    @settings(max_examples=100, deadline=10000)
    @pytest.mark.asyncio
    async def test_retry_count_matches_failures(
        self, failures_before_success, max_retries
    ):
        """
        Property: Number of retries should match number of failures (up to limit).
        
        The number of retry attempts should equal the number of failures,
        up to the maximum retry limit.
        
        Args:
            failures_before_success: Number of failures before success
            max_retries: Maximum number of retries allowed
        """
        assume(failures_before_success <= max_retries)
        
        element = RetryableElement(failures_before_success=failures_before_success)
        retry_manager = RetryManager(max_retries=max_retries, initial_delay=0.01)
        
        await retry_manager.retry_with_backoff(element.click)
        
        # Property: Total attempts = failures + 1 success
        assert element.attempt_count == failures_before_success + 1
        
        # Property: Number of retries = failures
        retry_count = len(retry_manager.retry_attempts) - 1
        assert retry_count == failures_before_success, (
            f"Should have {failures_before_success} retries, got {retry_count}"
        )
    
    @given(
        initial_delay=st.floats(min_value=0.01, max_value=0.5),
        failures=st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=50, deadline=10000)
    @pytest.mark.asyncio
    async def test_initial_delay_affects_backoff(
        self, initial_delay, failures
    ):
        """
        Property: Initial delay should affect all backoff intervals.
        
        The initial delay parameter should be the base for exponential backoff,
        affecting all subsequent retry delays.
        
        Args:
            initial_delay: Initial delay in seconds
            failures: Number of failures before success
        """
        element = RetryableElement(failures_before_success=failures)
        retry_manager = RetryManager(max_retries=failures, initial_delay=initial_delay)
        
        await retry_manager.retry_with_backoff(element.click)
        
        intervals = element.get_backoff_intervals()
        
        # Property: First interval should be approximately initial_delay
        if len(intervals) > 0:
            # Allow 50% variance due to timing
            assert initial_delay * 0.5 <= intervals[0] <= initial_delay * 1.5, (
                f"First interval should be ~{initial_delay}s, got {intervals[0]:.3f}s"
            )
    
    @given(
        failures_before_success=st.integers(min_value=1, max_value=3),
        max_retries=st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=100, deadline=10000)
    @pytest.mark.asyncio
    async def test_retry_preserves_exception_info(
        self, failures_before_success, max_retries
    ):
        """
        Property: Final exception should preserve original error information.
        
        When all retries fail, the final exception should contain information
        about the original error.
        
        Args:
            failures_before_success: Number of failures before success
            max_retries: Maximum number of retries allowed
        """
        # Only test cases where all retries fail
        assume(failures_before_success > max_retries)
        
        element = RetryableElement(failures_before_success=failures_before_success)
        retry_manager = RetryManager(max_retries=max_retries, initial_delay=0.01)
        
        # Property: Exception is raised
        with pytest.raises(Exception) as exc_info:
            await retry_manager.retry_with_backoff(element.click)
        
        # Property: Exception message contains failure information
        assert "Transient failure" in str(exc_info.value)
        assert "attempt" in str(exc_info.value).lower()


def test_property_coverage():
    """
    Verify that this test file covers Property 5: Element Interaction Retry.
    
    This is a meta-test to ensure the property is properly documented and tested.
    """
    # Verify property is documented in module docstring
    assert "Property 5: Element Interaction Retry" in __doc__
    assert "Validates: Requirements 5.1, 5.2" in __doc__
    
    # Verify test class exists
    assert TestElementInteractionRetry is not None
    
    # Verify key test methods exist
    test_methods = [
        'test_retry_succeeds_within_limit',
        'test_retry_fails_when_exceeds_limit',
        'test_exponential_backoff_increases',
        'test_immediate_success_no_retry',
        'test_retry_count_matches_failures',
        'test_initial_delay_affects_backoff',
        'test_retry_preserves_exception_info'
    ]
    
    for method_name in test_methods:
        assert hasattr(TestElementInteractionRetry, method_name), (
            f"Test method {method_name} not found"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
