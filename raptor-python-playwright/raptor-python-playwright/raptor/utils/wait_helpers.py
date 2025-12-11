"""
Wait and Synchronization Helpers for RAPTOR Python Playwright Framework.

This module provides advanced wait conditions, polling mechanisms, exponential backoff,
and synchronization decorators to handle dynamic page loading and timing issues.

Features:
- Custom wait conditions for complex scenarios
- Polling mechanism with configurable timeout and interval
- Exponential backoff utility for retry logic
- Synchronization decorators for automatic retry and timeout handling
"""

from typing import Callable, Optional, Any, TypeVar, Union
from playwright.async_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from raptor.core.exceptions import TimeoutException, RaptorException
import asyncio
import logging
import time
from functools import wraps
from dataclasses import dataclass

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class WaitConditionResult:
    """Result of a wait condition check."""
    success: bool
    value: Any = None
    message: str = ""


class WaitCondition:
    """
    Base class for custom wait conditions.
    
    Subclass this to create custom wait conditions that can be used
    with the polling mechanism.
    
    Example:
        >>> class ElementTextContains(WaitCondition):
        ...     def __init__(self, locator: Locator, text: str):
        ...         self.locator = locator
        ...         self.text = text
        ...     
        ...     async def check(self) -> WaitConditionResult:
        ...         try:
        ...             element_text = await self.locator.text_content()
        ...             if element_text and self.text in element_text:
        ...                 return WaitConditionResult(True, element_text)
        ...             return WaitConditionResult(False, message=f"Text '{self.text}' not found")
        ...         except Exception as e:
        ...             return WaitConditionResult(False, message=str(e))
    """
    
    async def check(self) -> WaitConditionResult:
        """
        Check if the condition is met.
        
        Returns:
            WaitConditionResult indicating success/failure and optional value
        """
        raise NotImplementedError("Subclasses must implement check() method")


class ElementTextContains(WaitCondition):
    """Wait condition that checks if element text contains a specific string."""
    
    def __init__(self, locator: Locator, text: str, case_sensitive: bool = True):
        """
        Initialize the condition.
        
        Args:
            locator: Playwright Locator to check
            text: Text to search for
            case_sensitive: Whether the search should be case-sensitive
        """
        self.locator = locator
        self.text = text
        self.case_sensitive = case_sensitive
    
    async def check(self) -> WaitConditionResult:
        """Check if element text contains the specified text."""
        try:
            element_text = await self.locator.text_content()
            if element_text:
                search_text = self.text if self.case_sensitive else self.text.lower()
                content = element_text if self.case_sensitive else element_text.lower()
                
                if search_text in content:
                    return WaitConditionResult(True, element_text)
            
            return WaitConditionResult(
                False,
                message=f"Text '{self.text}' not found in element"
            )
        except Exception as e:
            return WaitConditionResult(False, message=str(e))


class ElementAttributeEquals(WaitCondition):
    """Wait condition that checks if element attribute equals a specific value."""
    
    def __init__(self, locator: Locator, attribute: str, value: str):
        """
        Initialize the condition.
        
        Args:
            locator: Playwright Locator to check
            attribute: Attribute name to check
            value: Expected attribute value
        """
        self.locator = locator
        self.attribute = attribute
        self.value = value
    
    async def check(self) -> WaitConditionResult:
        """Check if element attribute equals the specified value."""
        try:
            attr_value = await self.locator.get_attribute(self.attribute)
            if attr_value == self.value:
                return WaitConditionResult(True, attr_value)
            
            return WaitConditionResult(
                False,
                message=f"Attribute '{self.attribute}' is '{attr_value}', expected '{self.value}'"
            )
        except Exception as e:
            return WaitConditionResult(False, message=str(e))


class ElementCountEquals(WaitCondition):
    """Wait condition that checks if element count equals a specific number."""
    
    def __init__(self, locator: Locator, count: int):
        """
        Initialize the condition.
        
        Args:
            locator: Playwright Locator to check
            count: Expected element count
        """
        self.locator = locator
        self.count = count
    
    async def check(self) -> WaitConditionResult:
        """Check if element count equals the specified number."""
        try:
            actual_count = await self.locator.count()
            if actual_count == self.count:
                return WaitConditionResult(True, actual_count)
            
            return WaitConditionResult(
                False,
                message=f"Element count is {actual_count}, expected {self.count}"
            )
        except Exception as e:
            return WaitConditionResult(False, message=str(e))


class PageUrlContains(WaitCondition):
    """Wait condition that checks if page URL contains a specific string."""
    
    def __init__(self, page: Page, url_fragment: str):
        """
        Initialize the condition.
        
        Args:
            page: Playwright Page to check
            url_fragment: URL fragment to search for
        """
        self.page = page
        self.url_fragment = url_fragment
    
    async def check(self) -> WaitConditionResult:
        """Check if page URL contains the specified fragment."""
        try:
            current_url = self.page.url
            if self.url_fragment in current_url:
                return WaitConditionResult(True, current_url)
            
            return WaitConditionResult(
                False,
                message=f"URL fragment '{self.url_fragment}' not found in '{current_url}'"
            )
        except Exception as e:
            return WaitConditionResult(False, message=str(e))


class CustomCondition(WaitCondition):
    """Wait condition that uses a custom async function."""
    
    def __init__(self, condition_func: Callable[[], Any], description: str = "custom condition"):
        """
        Initialize the condition.
        
        Args:
            condition_func: Async function that returns truthy value when condition is met
            description: Description of the condition for logging
        """
        self.condition_func = condition_func
        self.description = description
    
    async def check(self) -> WaitConditionResult:
        """Check if custom condition is met."""
        try:
            result = await self.condition_func()
            if result:
                return WaitConditionResult(True, result)
            
            return WaitConditionResult(
                False,
                message=f"Custom condition '{self.description}' not met"
            )
        except Exception as e:
            return WaitConditionResult(False, message=str(e))


async def wait_for_condition(
    condition: WaitCondition,
    timeout: int = 30000,
    poll_interval: int = 500,
    error_message: Optional[str] = None
) -> Any:
    """
    Wait for a custom condition to be met using polling.
    
    Repeatedly checks the condition at the specified interval until it succeeds
    or the timeout is reached.
    
    Args:
        condition: WaitCondition instance to check
        timeout: Maximum time to wait in milliseconds (default: 30000)
        poll_interval: Time between checks in milliseconds (default: 500)
        error_message: Optional custom error message for timeout
        
    Returns:
        The value returned by the condition when it succeeds
        
    Raises:
        TimeoutException: If condition is not met within timeout
        
    Example:
        >>> condition = ElementTextContains(locator, "Success")
        >>> result = await wait_for_condition(condition, timeout=10000)
        >>> print(f"Element text: {result}")
    """
    start_time = time.time()
    timeout_seconds = timeout / 1000
    poll_seconds = poll_interval / 1000
    attempts = 0
    
    logger.debug(
        f"Starting wait for condition (timeout: {timeout}ms, interval: {poll_interval}ms)"
    )
    
    while True:
        attempts += 1
        elapsed = time.time() - start_time
        
        # Check if timeout exceeded
        if elapsed >= timeout_seconds:
            if error_message:
                logger.error(error_message)
                raise TimeoutException(
                    operation="wait_for_condition",
                    timeout_seconds=timeout_seconds,
                    additional_info={
                        "attempts": attempts,
                        "condition_type": type(condition).__name__,
                        "custom_message": error_message
                    }
                )
            else:
                error_msg = f"Condition not met after {attempts} attempts ({timeout}ms)"
                logger.error(error_msg)
                raise TimeoutException(
                    operation="wait_for_condition",
                    timeout_seconds=timeout_seconds,
                    additional_info={
                        "attempts": attempts,
                        "condition_type": type(condition).__name__
                    }
                )
        
        # Check the condition
        result = await condition.check()
        
        if result.success:
            logger.info(
                f"Condition met after {attempts} attempts "
                f"({elapsed:.2f}s elapsed)"
            )
            return result.value
        
        # Log progress periodically
        if attempts % 10 == 0:
            logger.debug(
                f"Condition not yet met (attempt {attempts}, "
                f"{elapsed:.2f}s elapsed): {result.message}"
            )
        
        # Wait before next check
        await asyncio.sleep(poll_seconds)


async def poll_until(
    check_func: Callable[[], Any],
    timeout: int = 30000,
    poll_interval: int = 500,
    error_message: Optional[str] = None
) -> Any:
    """
    Poll a function until it returns a truthy value or timeout is reached.
    
    This is a simpler alternative to wait_for_condition for basic polling needs.
    
    Args:
        check_func: Async function to poll (should return truthy when condition is met)
        timeout: Maximum time to wait in milliseconds (default: 30000)
        poll_interval: Time between checks in milliseconds (default: 500)
        error_message: Optional custom error message for timeout
        
    Returns:
        The truthy value returned by check_func
        
    Raises:
        TimeoutException: If function doesn't return truthy value within timeout
        
    Example:
        >>> async def check_api_ready():
        ...     response = await api_client.health_check()
        ...     return response.status == "ready"
        >>> 
        >>> await poll_until(check_api_ready, timeout=60000, poll_interval=1000)
    """
    condition = CustomCondition(check_func, description="poll_until")
    return await wait_for_condition(
        condition,
        timeout=timeout,
        poll_interval=poll_interval,
        error_message=error_message
    )


class ExponentialBackoff:
    """
    Exponential backoff utility for retry logic.
    
    Calculates wait times that increase exponentially with each retry,
    useful for handling transient failures and rate limiting.
    
    Example:
        >>> backoff = ExponentialBackoff(initial_delay=1.0, max_delay=60.0, factor=2.0)
        >>> for attempt in range(5):
        ...     delay = backoff.get_delay(attempt)
        ...     print(f"Attempt {attempt + 1}: wait {delay}s")
        ...     await asyncio.sleep(delay)
    """
    
    def __init__(
        self,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        factor: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize exponential backoff calculator.
        
        Args:
            initial_delay: Initial delay in seconds (default: 1.0)
            max_delay: Maximum delay in seconds (default: 60.0)
            factor: Multiplication factor for each retry (default: 2.0)
            jitter: Whether to add random jitter to delays (default: True)
        """
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.factor = factor
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt number.
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        import random
        
        # Calculate exponential delay
        delay = min(self.initial_delay * (self.factor ** attempt), self.max_delay)
        
        # Add jitter if enabled (random value between 0 and delay)
        if self.jitter:
            delay = random.uniform(0, delay)
        
        return delay
    
    async def sleep(self, attempt: int) -> None:
        """
        Sleep for the calculated delay.
        
        Args:
            attempt: Attempt number (0-indexed)
        """
        delay = self.get_delay(attempt)
        logger.debug(f"Exponential backoff: sleeping for {delay:.2f}s (attempt {attempt + 1})")
        await asyncio.sleep(delay)


async def retry_with_backoff(
    func: Callable[..., T],
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    factor: float = 2.0,
    exceptions: tuple = (Exception,),
    *args,
    **kwargs
) -> T:
    """
    Retry a function with exponential backoff.
    
    Attempts to execute the function multiple times with increasing delays
    between attempts. Useful for handling transient failures.
    
    Args:
        func: Async function to retry
        max_attempts: Maximum number of attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        factor: Multiplication factor for each retry (default: 2.0)
        exceptions: Tuple of exception types to catch and retry (default: (Exception,))
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func
        
    Returns:
        Result of successful function execution
        
    Raises:
        The last exception if all attempts fail
        
    Example:
        >>> async def flaky_api_call():
        ...     response = await api.get_data()
        ...     return response.json()
        >>> 
        >>> data = await retry_with_backoff(
        ...     flaky_api_call,
        ...     max_attempts=5,
        ...     exceptions=(ConnectionError, TimeoutError)
        ... )
    """
    backoff = ExponentialBackoff(
        initial_delay=initial_delay,
        max_delay=max_delay,
        factor=factor
    )
    
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            logger.debug(f"Attempt {attempt + 1}/{max_attempts} for {func.__name__}")
            result = await func(*args, **kwargs)
            
            if attempt > 0:
                logger.info(
                    f"Function {func.__name__} succeeded on attempt {attempt + 1}"
                )
            
            return result
            
        except exceptions as e:
            last_exception = e
            logger.warning(
                f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {str(e)}"
            )
            
            # Don't sleep after the last attempt
            if attempt < max_attempts - 1:
                await backoff.sleep(attempt)
    
    # All attempts failed
    logger.error(
        f"All {max_attempts} attempts failed for {func.__name__}"
    )
    raise last_exception


def with_retry(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator that adds retry logic with exponential backoff to async functions.
    
    Args:
        max_attempts: Maximum number of attempts (default: 3)
        initial_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        factor: Multiplication factor for each retry (default: 2.0)
        exceptions: Tuple of exception types to catch and retry (default: (Exception,))
        
    Example:
        >>> @with_retry(max_attempts=5, exceptions=(ConnectionError,))
        ... async def fetch_data():
        ...     response = await api.get("/data")
        ...     return response.json()
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_with_backoff(
                func,
                max_attempts=max_attempts,
                initial_delay=initial_delay,
                max_delay=max_delay,
                factor=factor,
                exceptions=exceptions,
                *args,
                **kwargs
            )
        return wrapper
    return decorator


def with_timeout(timeout_seconds: float):
    """
    Decorator that adds timeout handling to async functions.
    
    Args:
        timeout_seconds: Maximum execution time in seconds
        
    Raises:
        TimeoutException: If function execution exceeds timeout
        
    Example:
        >>> @with_timeout(30.0)
        ... async def slow_operation():
        ...     await asyncio.sleep(10)
        ...     return "completed"
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error(
                    f"Function {func.__name__} exceeded timeout of {timeout_seconds}s"
                )
                raise TimeoutException(
                    operation=func.__name__,
                    timeout_seconds=timeout_seconds,
                    additional_info={
                        "function": func.__name__,
                        "args": str(args)[:100],
                        "kwargs": str(kwargs)[:100]
                    }
                )
        return wrapper
    return decorator


def synchronized(lock_attr: str = "_lock"):
    """
    Decorator that synchronizes access to async functions using a lock.
    
    Ensures that only one coroutine can execute the decorated function at a time.
    The lock should be an asyncio.Lock instance stored as an attribute on the class.
    
    Args:
        lock_attr: Name of the lock attribute (default: "_lock")
        
    Example:
        >>> class DataManager:
        ...     def __init__(self):
        ...         self._lock = asyncio.Lock()
        ...     
        ...     @synchronized()
        ...     async def update_data(self, data):
        ...         # Only one coroutine can execute this at a time
        ...         await self._save_to_database(data)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> T:
            lock = getattr(self, lock_attr, None)
            if lock is None:
                raise AttributeError(
                    f"Instance must have '{lock_attr}' attribute (asyncio.Lock)"
                )
            
            async with lock:
                logger.debug(f"Acquired lock for {func.__name__}")
                try:
                    return await func(self, *args, **kwargs)
                finally:
                    logger.debug(f"Released lock for {func.__name__}")
        
        return wrapper
    return decorator


async def wait_for_all(
    *awaitables,
    timeout: Optional[float] = None,
    return_exceptions: bool = False
) -> list:
    """
    Wait for all awaitables to complete with optional timeout.
    
    Similar to asyncio.gather but with timeout support and better error handling.
    
    Args:
        *awaitables: Async functions or coroutines to wait for
        timeout: Optional timeout in seconds
        return_exceptions: If True, exceptions are returned instead of raised
        
    Returns:
        List of results from all awaitables
        
    Raises:
        TimeoutException: If timeout is exceeded
        Exception: First exception from awaitables (if return_exceptions=False)
        
    Example:
        >>> results = await wait_for_all(
        ...     fetch_user_data(),
        ...     fetch_product_data(),
        ...     fetch_order_data(),
        ...     timeout=30.0
        ... )
    """
    try:
        if timeout:
            return await asyncio.wait_for(
                asyncio.gather(*awaitables, return_exceptions=return_exceptions),
                timeout=timeout
            )
        else:
            return await asyncio.gather(*awaitables, return_exceptions=return_exceptions)
    except asyncio.TimeoutError:
        logger.error(f"wait_for_all exceeded timeout of {timeout}s")
        raise TimeoutException(
            operation="wait_for_all",
            timeout_seconds=timeout,
            additional_info={"awaitable_count": len(awaitables)}
        )


async def wait_for_any(
    *awaitables,
    timeout: Optional[float] = None
) -> tuple[Any, int]:
    """
    Wait for any awaitable to complete (first one wins).
    
    Returns the result of the first awaitable to complete along with its index.
    Other awaitables are cancelled.
    
    Args:
        *awaitables: Async functions or coroutines to wait for
        timeout: Optional timeout in seconds
        
    Returns:
        Tuple of (result, index) where index is the position of the completed awaitable
        
    Raises:
        TimeoutException: If timeout is exceeded before any complete
        
    Example:
        >>> result, index = await wait_for_any(
        ...     fetch_from_cache(),
        ...     fetch_from_database(),
        ...     fetch_from_api(),
        ...     timeout=5.0
        ... )
        >>> print(f"Got result from source {index}: {result}")
    """
    tasks = [asyncio.create_task(aw) for aw in awaitables]
    
    done, pending = await asyncio.wait(
        tasks,
        timeout=timeout,
        return_when=asyncio.FIRST_COMPLETED
    )
    
    # Check if any task completed
    if not done:
        # Timeout occurred - cancel all tasks
        for task in tasks:
            task.cancel()
        
        logger.error(f"wait_for_any exceeded timeout of {timeout}s")
        raise TimeoutException(
            operation="wait_for_any",
            timeout_seconds=timeout,
            additional_info={"awaitable_count": len(awaitables)}
        )
    
    # Cancel pending tasks
    for task in pending:
        task.cancel()
    
    # Get the first completed task
    completed_task = done.pop()
    result = await completed_task
    
    # Find the index of the completed task
    index = tasks.index(completed_task)
    
    logger.info(f"wait_for_any: awaitable {index} completed first")
    return result, index
