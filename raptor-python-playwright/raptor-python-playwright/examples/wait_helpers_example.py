"""
Example usage of Wait and Synchronization Helpers.

This example demonstrates:
- Custom wait conditions
- Polling mechanisms
- Exponential backoff
- Retry decorators
- Timeout handling
- Synchronization
"""

import asyncio
from playwright.async_api import async_playwright
from raptor.utils.wait_helpers import (
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


async def example_custom_wait_conditions():
    """Example: Using custom wait conditions."""
    print("\n=== Custom Wait Conditions ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to a page
        await page.goto("https://example.com")
        
        # Wait for element text to contain specific string
        h1_locator = page.locator("h1")
        condition = ElementTextContains(h1_locator, "Example")
        
        try:
            result = await wait_for_condition(condition, timeout=10000)
            print(f"✓ Element text found: {result}")
        except Exception as e:
            print(f"✗ Wait failed: {e}")
        
        # Wait for page URL to contain fragment
        url_condition = PageUrlContains(page, "example.com")
        result = await wait_for_condition(url_condition, timeout=5000)
        print(f"✓ URL contains 'example.com': {result}")
        
        await browser.close()


async def example_polling_mechanism():
    """Example: Using polling mechanism."""
    print("\n=== Polling Mechanism ===\n")
    
    # Simulate checking if API is ready
    attempts = {"count": 0}
    
    async def check_api_ready():
        """Simulate API health check."""
        attempts["count"] += 1
        print(f"  Checking API (attempt {attempts['count']})...")
        
        # Simulate API becoming ready after 3 attempts
        if attempts["count"] >= 3:
            return {"status": "ready"}
        return None
    
    try:
        result = await poll_until(
            check_api_ready,
            timeout=10000,
            poll_interval=500
        )
        print(f"✓ API is ready: {result}")
    except Exception as e:
        print(f"✗ API not ready: {e}")


async def example_exponential_backoff():
    """Example: Using exponential backoff."""
    print("\n=== Exponential Backoff ===\n")
    
    backoff = ExponentialBackoff(
        initial_delay=0.5,
        max_delay=10.0,
        factor=2.0,
        jitter=True
    )
    
    print("Exponential backoff delays:")
    for attempt in range(6):
        delay = backoff.get_delay(attempt)
        print(f"  Attempt {attempt + 1}: {delay:.2f}s")


async def example_retry_with_backoff():
    """Example: Using retry with backoff."""
    print("\n=== Retry with Backoff ===\n")
    
    attempts = {"count": 0}
    
    async def flaky_operation():
        """Simulate a flaky operation that fails sometimes."""
        attempts["count"] += 1
        print(f"  Attempting operation (attempt {attempts['count']})...")
        
        # Fail first 2 attempts
        if attempts["count"] < 3:
            raise ConnectionError("Connection failed")
        
        return "Success!"
    
    try:
        result = await retry_with_backoff(
            flaky_operation,
            max_attempts=5,
            initial_delay=0.5,
            exceptions=(ConnectionError,)
        )
        print(f"✓ Operation succeeded: {result}")
    except Exception as e:
        print(f"✗ Operation failed: {e}")


async def example_retry_decorator():
    """Example: Using retry decorator."""
    print("\n=== Retry Decorator ===\n")
    
    attempts = {"count": 0}
    
    @with_retry(max_attempts=5, initial_delay=0.5, exceptions=(ValueError,))
    async def fetch_data():
        """Simulate fetching data with retries."""
        attempts["count"] += 1
        print(f"  Fetching data (attempt {attempts['count']})...")
        
        # Fail first 2 attempts
        if attempts["count"] < 3:
            raise ValueError("Data not available")
        
        return {"data": "important information"}
    
    try:
        result = await fetch_data()
        print(f"✓ Data fetched: {result}")
    except Exception as e:
        print(f"✗ Failed to fetch data: {e}")


async def example_timeout_decorator():
    """Example: Using timeout decorator."""
    print("\n=== Timeout Decorator ===\n")
    
    @with_timeout(2.0)
    async def quick_operation():
        """Operation that completes quickly."""
        await asyncio.sleep(0.5)
        return "Completed"
    
    @with_timeout(1.0)
    async def slow_operation():
        """Operation that takes too long."""
        await asyncio.sleep(5.0)
        return "Completed"
    
    # Quick operation should succeed
    try:
        result = await quick_operation()
        print(f"✓ Quick operation: {result}")
    except Exception as e:
        print(f"✗ Quick operation failed: {e}")
    
    # Slow operation should timeout
    try:
        result = await slow_operation()
        print(f"✓ Slow operation: {result}")
    except Exception as e:
        print(f"✗ Slow operation timed out (expected)")


async def example_synchronized_decorator():
    """Example: Using synchronized decorator."""
    print("\n=== Synchronized Decorator ===\n")
    
    class SharedResource:
        """Example class with synchronized access."""
        
        def __init__(self):
            self._lock = asyncio.Lock()
            self.counter = 0
        
        @synchronized()
        async def increment(self, task_id: int):
            """Increment counter with synchronized access."""
            print(f"  Task {task_id} acquired lock")
            current = self.counter
            await asyncio.sleep(0.1)  # Simulate work
            self.counter = current + 1
            print(f"  Task {task_id} incremented counter to {self.counter}")
    
    resource = SharedResource()
    
    # Run multiple tasks concurrently
    tasks = [resource.increment(i) for i in range(5)]
    await asyncio.gather(*tasks)
    
    print(f"✓ Final counter value: {resource.counter}")


async def example_wait_for_all():
    """Example: Using wait_for_all."""
    print("\n=== Wait for All ===\n")
    
    async def fetch_users():
        """Simulate fetching users."""
        await asyncio.sleep(0.5)
        print("  ✓ Users fetched")
        return ["Alice", "Bob", "Charlie"]
    
    async def fetch_products():
        """Simulate fetching products."""
        await asyncio.sleep(0.3)
        print("  ✓ Products fetched")
        return ["Product A", "Product B"]
    
    async def fetch_orders():
        """Simulate fetching orders."""
        await asyncio.sleep(0.4)
        print("  ✓ Orders fetched")
        return ["Order 1", "Order 2", "Order 3"]
    
    print("Fetching all data concurrently...")
    results = await wait_for_all(
        fetch_users(),
        fetch_products(),
        fetch_orders(),
        timeout=5.0
    )
    
    users, products, orders = results
    print(f"\n✓ All data fetched:")
    print(f"  Users: {len(users)}")
    print(f"  Products: {len(products)}")
    print(f"  Orders: {len(orders)}")


async def example_wait_for_any():
    """Example: Using wait_for_any."""
    print("\n=== Wait for Any ===\n")
    
    async def fetch_from_cache():
        """Simulate fetching from cache (fast)."""
        await asyncio.sleep(0.2)
        return {"source": "cache", "data": "cached data"}
    
    async def fetch_from_database():
        """Simulate fetching from database (medium)."""
        await asyncio.sleep(1.0)
        return {"source": "database", "data": "db data"}
    
    async def fetch_from_api():
        """Simulate fetching from API (slow)."""
        await asyncio.sleep(2.0)
        return {"source": "api", "data": "api data"}
    
    print("Fetching from multiple sources (first one wins)...")
    result, index = await wait_for_any(
        fetch_from_cache(),
        fetch_from_database(),
        fetch_from_api(),
        timeout=5.0
    )
    
    sources = ["cache", "database", "api"]
    print(f"✓ Got result from {sources[index]}: {result}")


async def example_complex_scenario():
    """Example: Complex scenario combining multiple features."""
    print("\n=== Complex Scenario ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate with retry
        @with_retry(max_attempts=3, initial_delay=1.0, exceptions=(Exception,))
        async def navigate_with_retry(url: str):
            """Navigate to URL with retry logic."""
            print(f"  Navigating to {url}...")
            await page.goto(url, wait_until="domcontentloaded")
        
        try:
            await navigate_with_retry("https://example.com")
            print("✓ Navigation successful")
        except Exception as e:
            print(f"✗ Navigation failed: {e}")
            await browser.close()
            return
        
        # Wait for multiple conditions in parallel
        async def wait_for_title():
            """Wait for page title to be set."""
            await poll_until(
                lambda: page.title() if page.title() else None,
                timeout=5000,
                poll_interval=100
            )
            return await page.title()
        
        async def wait_for_content():
            """Wait for main content to load."""
            h1_locator = page.locator("h1")
            condition = ElementTextContains(h1_locator, "Example")
            return await wait_for_condition(condition, timeout=5000)
        
        print("Waiting for page to load...")
        title, content = await wait_for_all(
            wait_for_title(),
            wait_for_content(),
            timeout=10.0
        )
        
        print(f"✓ Page loaded:")
        print(f"  Title: {title}")
        print(f"  Content: {content}")
        
        await browser.close()


async def main():
    """Run all examples."""
    print("=" * 60)
    print("Wait and Synchronization Helpers Examples")
    print("=" * 60)
    
    await example_custom_wait_conditions()
    await example_polling_mechanism()
    await example_exponential_backoff()
    await example_retry_with_backoff()
    await example_retry_decorator()
    await example_timeout_decorator()
    await example_synchronized_decorator()
    await example_wait_for_all()
    await example_wait_for_any()
    await example_complex_scenario()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
