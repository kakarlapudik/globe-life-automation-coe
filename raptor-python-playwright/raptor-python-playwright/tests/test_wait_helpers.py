"""
Tests for Wait and Synchronization Helpers.

Tests cover:
- Custom wait conditions
- Polling mechanism
- Exponential backoff
- Retry decorators
- Timeout decorators
- Synchronization decorators
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch
from playwright.async_api import Page, Locator

from raptor.utils.wait_helpers import (
    WaitCondition,
    WaitConditionResult,
    ElementTextContains,
    ElementAttributeEquals,
    ElementCountEquals,
    PageUrlContains,
    CustomCondition,
    wait_for_condition,
    poll_until,
    ExponentialBackoff,
    retry_with_backoff,
    with_retry,
    with_timeout,
    synchronized,
    wait_for_all,
    wait_for_any,
)
from raptor.core.exceptions import TimeoutException


class TestWaitConditions:
    """Test custom wait condition classes."""
    
    @pytest.mark.asyncio
    async def test_element_text_contains_success(self):
        """Test ElementTextContains when text is found."""
        locator = AsyncMock(spec=Locator)
        locator.text_content.return_value = "Hello World"
        
        condition = ElementTextContains(locator, "World")
        result = await condition.check()
        
        assert result.success is True
        assert result.value == "Hello World"
    
    @pytest.mark.asyncio
    async def test_element_text_contains_case_insensitive(self):
        """Test ElementTextContains with case-insensitive search."""
        locator = AsyncMock(spec=Locator)
        locator.text_content.return_value = "Hello World"
        
        condition = ElementTextContains(locator, "world", case_sensitive=False)
        result = await condition.check()
        
        assert result.success is True
    
    @pytest.mark.asyncio
    async def test_element_text_contains_failure(self):
        """Test ElementTextContains when text is not found."""
        locator = AsyncMock(spec=Locator)
        locator.text_content.return_value = "Hello World"
        
        condition = ElementTextContains(locator, "Goodbye")
        result = await condition.check()
        
        assert result.success is False
        assert "not found" in result.message
    
    @pytest.mark.asyncio
    async def test_element_attribute_equals_success(self):
        """Test ElementAttributeEquals when attribute matches."""
        locator = AsyncMock(spec=Locator)
        locator.get_attribute.return_value = "active"
        
        condition = ElementAttributeEquals(locator, "class", "active")
        result = await condition.check()
        
        assert result.success is True
        assert result.value == "active"
    
    @pytest.mark.asyncio
    async def test_element_attribute_equals_failure(self):
        """Test ElementAttributeEquals when attribute doesn't match."""
        locator = AsyncMock(spec=Locator)
        locator.get_attribute.return_value = "inactive"
        
        condition = ElementAttributeEquals(locator, "class", "active")
        result = await condition.check()
        
        assert result.success is False
        assert "expected 'active'" in result.message
    
    @pytest.mark.asyncio
    async def test_element_count_equals_success(self):
        """Test ElementCountEquals when count matches."""
        locator = AsyncMock(spec=Locator)
        locator.count.return_value = 5
        
        condition = ElementCountEquals(locator, 5)
        result = await condition.check()
        
        assert result.success is True
        assert result.value == 5
    
    @pytest.mark.asyncio
    async def test_element_count_equals_failure(self):
        """Test ElementCountEquals when count doesn't match."""
        locator = AsyncMock(spec=Locator)
        locator.count.return_value = 3
        
        condition = ElementCountEquals(locator, 5)
        result = await condition.check()
        
        assert result.success is False
        assert "expected 5" in result.message
    
    @pytest.mark.asyncio
    async def test_page_url_contains_success(self):
        """Test PageUrlContains when URL contains fragment."""
        page = Mock(spec=Page)
        page.url = "https://example.com/dashboard"
        
        condition = PageUrlContains(page, "dashboard")
        result = await condition.check()
        
        assert result.success is True
        assert result.value == "https://example.com/dashboard"
    
    @pytest.mark.asyncio
    async def test_page_url_contains_failure(self):
        """Test PageUrlContains when URL doesn't contain fragment."""
        page = Mock(spec=Page)
        page.url = "https://example.com/home"
        
        condition = PageUrlContains(page, "dashboard")
        result = await condition.check()
        
        assert result.success is False
        assert "not found" in result.message
    
    @pytest.mark.asyncio
    async def test_custom_condition_success(self):
        """Test CustomCondition with successful function."""
        async def check_func():
            return "success"
        
        condition = CustomCondition(check_func, "test condition")
        result = await condition.check()
        
        assert result.success is True
        assert result.value == "success"
    
    @pytest.mark.asyncio
    async def test_custom_condition_failure(self):
        """Test CustomCondition with failing function."""
        async def check_func():
            return None
        
        condition = CustomCondition(check_func, "test condition")
        result = await condition.check()
        
        assert result.success is False
        assert "not met" in result.message


class TestWaitForCondition:
    """Test wait_for_condition polling mechanism."""
    
    @pytest.mark.asyncio
    async def test_wait_for_condition_immediate_success(self):
        """Test wait_for_condition when condition is immediately met."""
        async def check_func():
            return True
        
        condition = CustomCondition(check_func)
        result = await wait_for_condition(condition, timeout=5000, poll_interval=100)
        
        assert result is True
    
    @pytest.mark.asyncio
    async def test_wait_for_condition_eventual_success(self):
        """Test wait_for_condition when condition is met after retries."""
        attempts = {"count": 0}
        
        async def check_func():
            attempts["count"] += 1
            return attempts["count"] >= 3
        
        condition = CustomCondition(check_func)
        result = await wait_for_condition(condition, timeout=5000, poll_interval=100)
        
        assert result is True
        assert attempts["count"] >= 3
    
    @pytest.mark.asyncio
    async def test_wait_for_condition_timeout(self):
        """Test wait_for_condition when timeout is exceeded."""
        async def check_func():
            return False
        
        condition = CustomCondition(check_func)
        
        with pytest.raises(TimeoutException) as exc_info:
            await wait_for_condition(condition, timeout=1000, poll_interval=100)
        
        # Check that timeout exception was raised
        assert exc_info.value is not None
    
    @pytest.mark.asyncio
    async def test_wait_for_condition_custom_error_message(self):
        """Test wait_for_condition with custom error message."""
        async def check_func():
            return False
        
        condition = CustomCondition(check_func)
        custom_message = "Custom timeout message"
        
        with pytest.raises(TimeoutException) as exc_info:
            await wait_for_condition(
                condition,
                timeout=1000,
                poll_interval=100,
                error_message=custom_message
            )
        
        # Check that custom message is in context
        assert exc_info.value is not None
        assert hasattr(exc_info.value, 'context')
        assert exc_info.value.context.get('custom_message') == custom_message


class TestPollUntil:
    """Test poll_until function."""
    
    @pytest.mark.asyncio
    async def test_poll_until_immediate_success(self):
        """Test poll_until when function immediately returns truthy."""
        async def check_func():
            return "result"
        
        result = await poll_until(check_func, timeout=5000, poll_interval=100)
        assert result == "result"
    
    @pytest.mark.asyncio
    async def test_poll_until_eventual_success(self):
        """Test poll_until when function eventually returns truthy."""
        attempts = {"count": 0}
        
        async def check_func():
            attempts["count"] += 1
            if attempts["count"] >= 3:
                return "success"
            return None
        
        result = await poll_until(check_func, timeout=5000, poll_interval=100)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_poll_until_timeout(self):
        """Test poll_until when timeout is exceeded."""
        async def check_func():
            return None
        
        with pytest.raises(TimeoutException):
            await poll_until(check_func, timeout=1000, poll_interval=100)


class TestExponentialBackoff:
    """Test ExponentialBackoff class."""
    
    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation."""
        backoff = ExponentialBackoff(
            initial_delay=1.0,
            max_delay=60.0,
            factor=2.0,
            jitter=False
        )
        
        # Test exponential growth
        assert backoff.get_delay(0) == 1.0
        assert backoff.get_delay(1) == 2.0
        assert backoff.get_delay(2) == 4.0
        assert backoff.get_delay(3) == 8.0
    
    def test_exponential_backoff_max_delay(self):
        """Test that backoff respects max_delay."""
        backoff = ExponentialBackoff(
            initial_delay=1.0,
            max_delay=10.0,
            factor=2.0,
            jitter=False
        )
        
        # Should cap at max_delay
        assert backoff.get_delay(10) == 10.0
        assert backoff.get_delay(100) == 10.0
    
    def test_exponential_backoff_with_jitter(self):
        """Test that jitter produces variable delays."""
        backoff = ExponentialBackoff(
            initial_delay=1.0,
            max_delay=60.0,
            factor=2.0,
            jitter=True
        )
        
        # With jitter, delays should vary
        delays = [backoff.get_delay(3) for _ in range(10)]
        
        # All delays should be between 0 and 8
        assert all(0 <= d <= 8.0 for d in delays)
        
        # Delays should not all be the same (very unlikely with jitter)
        assert len(set(delays)) > 1
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_sleep(self):
        """Test exponential backoff sleep method."""
        backoff = ExponentialBackoff(
            initial_delay=0.01,
            max_delay=1.0,
            factor=2.0,
            jitter=False
        )
        
        start = time.time()
        await backoff.sleep(0)
        elapsed = time.time() - start
        
        # Should sleep for approximately initial_delay (allow more tolerance for Windows)
        assert 0.005 <= elapsed <= 0.05


class TestRetryWithBackoff:
    """Test retry_with_backoff function."""
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_immediate_success(self):
        """Test retry when function succeeds immediately."""
        async def func():
            return "success"
        
        result = await retry_with_backoff(func, max_attempts=3, initial_delay=0.01)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_eventual_success(self):
        """Test retry when function succeeds after failures."""
        attempts = {"count": 0}
        
        async def func():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ValueError("Not ready")
            return "success"
        
        result = await retry_with_backoff(
            func,
            max_attempts=5,
            initial_delay=0.01,
            exceptions=(ValueError,)
        )
        
        assert result == "success"
        assert attempts["count"] == 3
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_all_failures(self):
        """Test retry when all attempts fail."""
        async def func():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError) as exc_info:
            await retry_with_backoff(
                func,
                max_attempts=3,
                initial_delay=0.01,
                exceptions=(ValueError,)
            )
        
        assert "Always fails" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff_wrong_exception(self):
        """Test retry doesn't catch unexpected exceptions."""
        async def func():
            raise TypeError("Wrong exception")
        
        with pytest.raises(TypeError):
            await retry_with_backoff(
                func,
                max_attempts=3,
                initial_delay=0.01,
                exceptions=(ValueError,)
            )


class TestWithRetryDecorator:
    """Test with_retry decorator."""
    
    @pytest.mark.asyncio
    async def test_with_retry_decorator_success(self):
        """Test with_retry decorator on successful function."""
        @with_retry(max_attempts=3, initial_delay=0.01)
        async def func():
            return "success"
        
        result = await func()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_with_retry_decorator_eventual_success(self):
        """Test with_retry decorator with eventual success."""
        attempts = {"count": 0}
        
        @with_retry(max_attempts=5, initial_delay=0.01, exceptions=(ValueError,))
        async def func():
            attempts["count"] += 1
            if attempts["count"] < 3:
                raise ValueError("Not ready")
            return "success"
        
        result = await func()
        assert result == "success"
        assert attempts["count"] == 3
    
    @pytest.mark.asyncio
    async def test_with_retry_decorator_all_failures(self):
        """Test with_retry decorator when all attempts fail."""
        @with_retry(max_attempts=3, initial_delay=0.01, exceptions=(ValueError,))
        async def func():
            raise ValueError("Always fails")
        
        with pytest.raises(ValueError):
            await func()


class TestWithTimeoutDecorator:
    """Test with_timeout decorator."""
    
    @pytest.mark.asyncio
    async def test_with_timeout_decorator_success(self):
        """Test with_timeout decorator on fast function."""
        @with_timeout(1.0)
        async def func():
            await asyncio.sleep(0.01)
            return "success"
        
        result = await func()
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_with_timeout_decorator_timeout(self):
        """Test with_timeout decorator on slow function."""
        @with_timeout(0.1)
        async def func():
            await asyncio.sleep(1.0)
            return "success"
        
        with pytest.raises(TimeoutException):
            await func()


class TestSynchronizedDecorator:
    """Test synchronized decorator."""
    
    @pytest.mark.asyncio
    async def test_synchronized_decorator(self):
        """Test synchronized decorator prevents concurrent execution."""
        class Counter:
            def __init__(self):
                self._lock = asyncio.Lock()
                self.value = 0
            
            @synchronized()
            async def increment(self):
                current = self.value
                await asyncio.sleep(0.01)  # Simulate work
                self.value = current + 1
        
        counter = Counter()
        
        # Run multiple increments concurrently
        await asyncio.gather(*[counter.increment() for _ in range(10)])
        
        # With proper synchronization, value should be 10
        assert counter.value == 10
    
    @pytest.mark.asyncio
    async def test_synchronized_decorator_missing_lock(self):
        """Test synchronized decorator raises error when lock is missing."""
        class BadClass:
            @synchronized()
            async def method(self):
                pass
        
        obj = BadClass()
        
        with pytest.raises(AttributeError) as exc_info:
            await obj.method()
        
        assert "_lock" in str(exc_info.value)


class TestWaitForAll:
    """Test wait_for_all function."""
    
    @pytest.mark.asyncio
    async def test_wait_for_all_success(self):
        """Test wait_for_all when all awaitables succeed."""
        async def func1():
            await asyncio.sleep(0.01)
            return "result1"
        
        async def func2():
            await asyncio.sleep(0.02)
            return "result2"
        
        async def func3():
            await asyncio.sleep(0.01)
            return "result3"
        
        results = await wait_for_all(func1(), func2(), func3())
        
        assert results == ["result1", "result2", "result3"]
    
    @pytest.mark.asyncio
    async def test_wait_for_all_with_timeout(self):
        """Test wait_for_all with timeout."""
        async def fast_func():
            await asyncio.sleep(0.01)
            return "fast"
        
        async def slow_func():
            await asyncio.sleep(10.0)
            return "slow"
        
        with pytest.raises(TimeoutException):
            await wait_for_all(fast_func(), slow_func(), timeout=0.1)
    
    @pytest.mark.asyncio
    async def test_wait_for_all_with_exception(self):
        """Test wait_for_all when one awaitable raises exception."""
        async def good_func():
            return "success"
        
        async def bad_func():
            raise ValueError("Error")
        
        with pytest.raises(ValueError):
            await wait_for_all(good_func(), bad_func())
    
    @pytest.mark.asyncio
    async def test_wait_for_all_return_exceptions(self):
        """Test wait_for_all with return_exceptions=True."""
        async def good_func():
            return "success"
        
        async def bad_func():
            raise ValueError("Error")
        
        results = await wait_for_all(
            good_func(),
            bad_func(),
            return_exceptions=True
        )
        
        assert results[0] == "success"
        assert isinstance(results[1], ValueError)


class TestWaitForAny:
    """Test wait_for_any function."""
    
    @pytest.mark.asyncio
    async def test_wait_for_any_first_completes(self):
        """Test wait_for_any returns first completed result."""
        async def fast_func():
            await asyncio.sleep(0.01)
            return "fast"
        
        async def slow_func():
            await asyncio.sleep(1.0)
            return "slow"
        
        result, index = await wait_for_any(fast_func(), slow_func())
        
        assert result == "fast"
        assert index == 0
    
    @pytest.mark.asyncio
    async def test_wait_for_any_with_timeout(self):
        """Test wait_for_any with timeout."""
        async def slow_func1():
            await asyncio.sleep(10.0)
            return "slow1"
        
        async def slow_func2():
            await asyncio.sleep(10.0)
            return "slow2"
        
        with pytest.raises(TimeoutException):
            await wait_for_any(slow_func1(), slow_func2(), timeout=0.1)
    
    @pytest.mark.asyncio
    async def test_wait_for_any_cancels_pending(self):
        """Test wait_for_any cancels pending tasks."""
        completed = {"func1": False, "func2": False}
        
        async def func1():
            try:
                await asyncio.sleep(0.01)
                completed["func1"] = True
                return "func1"
            except asyncio.CancelledError:
                # Task was cancelled
                raise
        
        async def func2():
            try:
                await asyncio.sleep(10.0)
                completed["func2"] = True
                return "func2"
            except asyncio.CancelledError:
                # Task was cancelled
                raise
        
        result, index = await wait_for_any(func1(), func2())
        
        # Give a moment for cancellation to propagate
        await asyncio.sleep(0.01)
        
        assert result == "func1"
        assert index == 0
        assert completed["func1"] is True
        assert completed["func2"] is False  # Should be cancelled
