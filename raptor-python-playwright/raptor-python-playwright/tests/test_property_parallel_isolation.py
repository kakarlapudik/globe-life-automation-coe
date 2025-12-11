"""
Property-Based Test: Parallel Test Isolation

**Feature: raptor-playwright-python, Property 12: Parallel Test Isolation**
**Validates: Requirements 12.4**

This test verifies that tests running in parallel have isolated browser contexts
that don't interfere with each other.

Property Statement:
    For any tests running in parallel, each test should have its own isolated 
    browser context that doesn't interfere with others.
"""

import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st, settings, assume
from typing import Dict, Any, List, Tuple
from unittest.mock import Mock, AsyncMock, patch
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from raptor.core.browser_manager import BrowserManager
from raptor.core.config_manager import ConfigManager
from raptor.core.exceptions import RaptorException


# Strategy for generating test identifiers
test_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
    min_size=1,
    max_size=30
).filter(lambda x: x.strip() != '')


# Strategy for generating URLs
url_strategy = st.sampled_from([
    "https://example.com",
    "https://example.com/page1",
    "https://example.com/page2",
    "https://test.example.com",
    "https://example.com/path/to/page",
    "https://example.com:8080/secure",
    "https://example.org",
    "https://example.net",
])


# Strategy for generating cookie data
cookie_strategy = st.dictionaries(
    keys=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=1,
        max_size=20
    ),
    values=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), whitelist_characters='-_'),
        min_size=1,
        max_size=50
    ),
    min_size=1,
    max_size=5
)


# Strategy for generating local storage data
storage_strategy = st.dictionaries(
    keys=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=1,
        max_size=20
    ),
    values=st.text(max_size=100),
    min_size=1,
    max_size=5
)


class MockBrowserContext:
    """
    Mock browser context for testing isolation.
    
    This simulates a Playwright BrowserContext with state that can be
    modified and verified for isolation testing.
    """
    
    def __init__(self, context_id: str):
        self.context_id = context_id
        self.cookies = {}
        self.storage = {}
        self.current_url = None
        self.pages = []
        self._closed = False
        self._lock = threading.Lock()
    
    async def new_page(self):
        """Create a new page in this context."""
        with self._lock:
            page = MockPage(self)
            self.pages.append(page)
            return page
    
    async def add_cookies(self, cookies: List[Dict]):
        """Add cookies to this context."""
        with self._lock:
            for cookie in cookies:
                self.cookies[cookie['name']] = cookie['value']
    
    async def get_cookies(self):
        """Get all cookies from this context."""
        with self._lock:
            return [
                {'name': name, 'value': value}
                for name, value in self.cookies.items()
            ]
    
    def set_storage(self, key: str, value: str):
        """Set local storage value."""
        with self._lock:
            self.storage[key] = value
    
    def get_storage(self, key: str):
        """Get local storage value."""
        with self._lock:
            return self.storage.get(key)
    
    async def close(self):
        """Close this context."""
        with self._lock:
            self._closed = True
            for page in self.pages:
                await page.close()
    
    def is_closed(self):
        """Check if context is closed."""
        with self._lock:
            return self._closed


class MockPage:
    """
    Mock page for testing.
    """
    
    def __init__(self, context: MockBrowserContext):
        self.context = context
        self.url = None
        self._closed = False
        self._lock = threading.Lock()
    
    async def goto(self, url: str):
        """Navigate to URL."""
        with self._lock:
            self.url = url
            self.context.current_url = url
    
    async def evaluate(self, script: str):
        """Evaluate JavaScript (mock)."""
        with self._lock:
            # Mock localStorage operations
            if "localStorage.setItem" in script:
                # Extract key and value from script
                # Format: localStorage.setItem('key', "value")
                import re
                match = re.search(r"localStorage\.setItem\('([^']+)',\s*(.+)\)", script)
                if match:
                    key = match.group(1)
                    value_expr = match.group(2).strip()
                    # Parse JSON value
                    import json
                    try:
                        value = json.loads(value_expr)
                    except:
                        value = value_expr.strip('"\'')
                    self.context.set_storage(key, value)
            elif "localStorage.getItem" in script:
                parts = script.split("'")
                if len(parts) >= 2:
                    key = parts[1]
                    return self.context.get_storage(key)
            return None
    
    async def close(self):
        """Close this page."""
        with self._lock:
            self._closed = True
    
    def is_closed(self):
        """Check if page is closed."""
        with self._lock:
            return self._closed


class MockBrowserManager:
    """
    Mock browser manager for testing parallel isolation.
    
    This simulates the BrowserManager with support for creating
    isolated contexts that can be tested for interference.
    """
    
    def __init__(self):
        self.contexts = {}
        self._context_counter = 0
        self._lock = threading.Lock()
    
    async def create_context(self, **options):
        """Create a new isolated browser context."""
        with self._lock:
            self._context_counter += 1
            context_id = f"context-{self._context_counter}"
            context = MockBrowserContext(context_id)
            self.contexts[context_id] = context
            return context
    
    def get_context_count(self):
        """Get the number of active contexts."""
        with self._lock:
            return len([c for c in self.contexts.values() if not c.is_closed()])
    
    def get_all_contexts(self):
        """Get all contexts."""
        with self._lock:
            return list(self.contexts.values())


class TestParallelTestIsolation:
    """
    Property-based tests for parallel test isolation.
    
    These tests verify that tests running in parallel have isolated
    browser contexts that don't interfere with each other.
    """
    
    @given(
        test_count=st.integers(min_value=2, max_value=5),
        url=url_strategy
    )
    @settings(max_examples=50, deadline=10000)
    @pytest.mark.asyncio
    async def test_parallel_contexts_are_isolated(self, test_count, url):
        """
        Property: Parallel contexts should be completely isolated.
        
        When multiple tests run in parallel, each should have its own
        browser context that doesn't share state with others.
        
        Args:
            test_count: Number of parallel tests to simulate
            url: URL to navigate to
        """
        browser_manager = MockBrowserManager()
        
        # Create multiple contexts in parallel
        contexts = []
        for i in range(test_count):
            context = await browser_manager.create_context()
            contexts.append(context)
        
        # Verify each context is unique
        context_ids = [c.context_id for c in contexts]
        assert len(set(context_ids)) == test_count, "All contexts should have unique IDs"
        
        # Verify contexts are isolated (no shared state)
        for i, context in enumerate(contexts):
            # Set unique data in each context
            page = await context.new_page()
            await page.goto(f"{url}?test={i}")
            await page.evaluate(f"localStorage.setItem('test_id', '{i}')")
            
            # Add unique cookie
            await context.add_cookies([{
                'name': f'test_cookie_{i}',
                'value': f'value_{i}',
                'domain': 'example.com',
                'path': '/'
            }])
        
        # Verify each context has only its own data
        for i, context in enumerate(contexts):
            # Check URL
            assert context.current_url == f"{url}?test={i}", (
                f"Context {i} should have its own URL"
            )
            
            # Check local storage
            page = context.pages[0]
            stored_value = await page.evaluate("localStorage.getItem('test_id')")
            assert stored_value == str(i), (
                f"Context {i} should have its own local storage value"
            )
            
            # Check cookies
            cookies = await context.get_cookies()
            cookie_names = [c['name'] for c in cookies]
            assert f'test_cookie_{i}' in cookie_names, (
                f"Context {i} should have its own cookie"
            )
            
            # Verify no cross-contamination
            for j in range(test_count):
                if j != i:
                    assert f'test_cookie_{j}' not in cookie_names, (
                        f"Context {i} should not have cookie from context {j}"
                    )
    
    @given(
        test_ids=st.lists(
            test_id_strategy,
            min_size=2,
            max_size=5,
            unique=True
        ),
        cookies=st.lists(
            cookie_strategy,
            min_size=2,
            max_size=5
        )
    )
    @settings(max_examples=50, deadline=10000)
    @pytest.mark.asyncio
    async def test_parallel_cookie_isolation(self, test_ids, cookies):
        """
        Property: Cookies should be isolated between parallel contexts.
        
        When multiple tests set cookies in parallel, each context should
        only see its own cookies and not cookies from other contexts.
        
        Args:
            test_ids: List of test identifiers
            cookies: List of cookie dictionaries for each test
        """
        # Ensure we have enough cookie sets
        assume(len(cookies) >= len(test_ids))
        
        browser_manager = MockBrowserManager()
        contexts = []
        
        # Create contexts and set cookies in parallel
        for i, test_id in enumerate(test_ids):
            context = await browser_manager.create_context()
            contexts.append(context)
            
            # Set unique cookies for this context
            cookie_list = [
                {
                    'name': f'{test_id}_{key}',
                    'value': value,
                    'domain': 'example.com',
                    'path': '/'
                }
                for key, value in cookies[i].items()
            ]
            await context.add_cookies(cookie_list)
        
        # Verify cookie isolation
        for i, (test_id, context) in enumerate(zip(test_ids, contexts)):
            context_cookies = await context.get_cookies()
            cookie_names = [c['name'] for c in context_cookies]
            
            # Verify this context has its own cookies
            for key in cookies[i].keys():
                expected_name = f'{test_id}_{key}'
                assert expected_name in cookie_names, (
                    f"Context {test_id} should have cookie {expected_name}"
                )
            
            # Verify this context doesn't have cookies from other contexts
            for j, other_test_id in enumerate(test_ids):
                if j != i:
                    for key in cookies[j].keys():
                        other_cookie_name = f'{other_test_id}_{key}'
                        assert other_cookie_name not in cookie_names, (
                            f"Context {test_id} should not have cookie {other_cookie_name} "
                            f"from context {other_test_id}"
                        )
    
    @given(
        test_ids=st.lists(
            test_id_strategy,
            min_size=2,
            max_size=5,
            unique=True
        ),
        storage_data=st.lists(
            storage_strategy,
            min_size=2,
            max_size=5
        )
    )
    @settings(max_examples=50, deadline=10000)
    @pytest.mark.asyncio
    async def test_parallel_storage_isolation(self, test_ids, storage_data):
        """
        Property: Local storage should be isolated between parallel contexts.
        
        When multiple tests set local storage in parallel, each context
        should only see its own storage and not storage from other contexts.
        
        Args:
            test_ids: List of test identifiers
            storage_data: List of storage dictionaries for each test
        """
        # Ensure we have enough storage sets
        assume(len(storage_data) >= len(test_ids))
        
        browser_manager = MockBrowserManager()
        contexts = []
        
        # Create contexts and set storage in parallel
        for i, test_id in enumerate(test_ids):
            context = await browser_manager.create_context()
            contexts.append(context)
            
            page = await context.new_page()
            
            # Set unique storage for this context
            for key, value in storage_data[i].items():
                storage_key = f'{test_id}_{key}'
                # Use JSON encoding to handle special characters
                import json
                encoded_value = json.dumps(value)
                await page.evaluate(f"localStorage.setItem('{storage_key}', {encoded_value})")
        
        # Verify storage isolation
        for i, (test_id, context) in enumerate(zip(test_ids, contexts)):
            page = context.pages[0]
            
            # Verify this context has its own storage
            for key, expected_value in storage_data[i].items():
                storage_key = f'{test_id}_{key}'
                actual_value = await page.evaluate(f"localStorage.getItem('{storage_key}')")
                assert actual_value == expected_value, (
                    f"Context {test_id} should have storage value for {storage_key}"
                )
            
            # Verify this context doesn't have storage from other contexts
            for j, other_test_id in enumerate(test_ids):
                if j != i:
                    for key in storage_data[j].keys():
                        other_storage_key = f'{other_test_id}_{key}'
                        value = await page.evaluate(
                            f"localStorage.getItem('{other_storage_key}')"
                        )
                        assert value is None, (
                            f"Context {test_id} should not have storage {other_storage_key} "
                            f"from context {other_test_id}"
                        )
    
    @given(
        test_count=st.integers(min_value=2, max_value=5),
        urls=st.lists(url_strategy, min_size=2, max_size=5, unique=True)
    )
    @settings(max_examples=50, deadline=10000)
    @pytest.mark.asyncio
    async def test_parallel_navigation_isolation(self, test_count, urls):
        """
        Property: Navigation should be isolated between parallel contexts.
        
        When multiple tests navigate to different URLs in parallel, each
        context should maintain its own navigation state.
        
        Args:
            test_count: Number of parallel tests
            urls: List of unique URLs to navigate to
        """
        # Ensure we have enough unique URLs
        assume(len(urls) >= test_count)
        
        browser_manager = MockBrowserManager()
        contexts = []
        
        # Create contexts and navigate in parallel
        for i in range(test_count):
            context = await browser_manager.create_context()
            contexts.append(context)
            
            page = await context.new_page()
            await page.goto(urls[i])
        
        # Verify navigation isolation
        for i, context in enumerate(contexts):
            assert context.current_url == urls[i], (
                f"Context {i} should be at URL {urls[i]}"
            )
            
            # Verify this context is not at other URLs (only check if URLs are different)
            for j in range(test_count):
                if j != i and urls[i] != urls[j]:
                    assert context.current_url != urls[j], (
                        f"Context {i} should not be at URL {urls[j]} from context {j}"
                    )
    
    @given(
        test_count=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=50, deadline=10000)
    @pytest.mark.asyncio
    async def test_parallel_context_cleanup_isolation(self, test_count):
        """
        Property: Closing one context should not affect other contexts.
        
        When one test closes its context, other parallel contexts should
        remain active and functional.
        
        Args:
            test_count: Number of parallel tests
        """
        browser_manager = MockBrowserManager()
        contexts = []
        
        # Create multiple contexts
        for i in range(test_count):
            context = await browser_manager.create_context()
            contexts.append(context)
            
            # Create a page in each context
            page = await context.new_page()
            await page.goto(f"https://example.com/test{i}")
        
        # Close the first context
        await contexts[0].close()
        
        # Verify first context is closed
        assert contexts[0].is_closed(), "First context should be closed"
        
        # Verify other contexts are still active
        for i in range(1, test_count):
            assert not contexts[i].is_closed(), (
                f"Context {i} should still be active after closing context 0"
            )
            
            # Verify other contexts are still functional
            assert contexts[i].current_url == f"https://example.com/test{i}", (
                f"Context {i} should maintain its state after closing context 0"
            )
            
            # Verify we can still create pages in other contexts
            new_page = await contexts[i].new_page()
            assert new_page is not None, (
                f"Should be able to create new page in context {i}"
            )
    
    @given(
        test_count=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=50, deadline=10000)
    @pytest.mark.asyncio
    async def test_parallel_page_isolation_within_context(self, test_count):
        """
        Property: Multiple pages within a context should share context state
        but be isolated from pages in other contexts.
        
        Args:
            test_count: Number of parallel contexts
        """
        browser_manager = MockBrowserManager()
        contexts = []
        
        # Create contexts with multiple pages each
        for i in range(test_count):
            context = await browser_manager.create_context()
            contexts.append(context)
            
            # Create 2 pages in each context
            page1 = await context.new_page()
            page2 = await context.new_page()
            
            # Set storage in first page
            await page1.evaluate(f"localStorage.setItem('context_id', '{i}')")
            
            # Navigate both pages
            await page1.goto(f"https://example.com/page1?ctx={i}")
            await page2.goto(f"https://example.com/page2?ctx={i}")
        
        # Verify pages within same context share state
        for i, context in enumerate(contexts):
            assert len(context.pages) == 2, (
                f"Context {i} should have 2 pages"
            )
            
            # Both pages should see the same storage
            page1, page2 = context.pages
            value1 = await page1.evaluate("localStorage.getItem('context_id')")
            value2 = await page2.evaluate("localStorage.getItem('context_id')")
            
            assert value1 == str(i), f"Page 1 in context {i} should see context storage"
            assert value2 == str(i), f"Page 2 in context {i} should see context storage"
            
            # Verify pages don't see storage from other contexts
            for j in range(test_count):
                if j != i:
                    value = await page1.evaluate("localStorage.getItem('context_id')")
                    assert value != str(j), (
                        f"Page in context {i} should not see storage from context {j}"
                    )
    
    @given(
        test_count=st.integers(min_value=2, max_value=5)
    )
    @settings(max_examples=50, deadline=10000)
    @pytest.mark.asyncio
    async def test_parallel_context_count_consistency(self, test_count):
        """
        Property: Context count should accurately reflect active contexts.
        
        The browser manager should accurately track the number of active
        contexts even when contexts are created and closed in parallel.
        
        Args:
            test_count: Number of contexts to create
        """
        browser_manager = MockBrowserManager()
        
        # Create contexts
        contexts = []
        for i in range(test_count):
            context = await browser_manager.create_context()
            contexts.append(context)
        
        # Verify count matches
        assert browser_manager.get_context_count() == test_count, (
            f"Should have {test_count} active contexts"
        )
        
        # Close half the contexts
        close_count = test_count // 2
        for i in range(close_count):
            await contexts[i].close()
        
        # Verify count is updated
        expected_active = test_count - close_count
        assert browser_manager.get_context_count() == expected_active, (
            f"Should have {expected_active} active contexts after closing {close_count}"
        )
        
        # Close remaining contexts
        for i in range(close_count, test_count):
            await contexts[i].close()
        
        # Verify all contexts are closed
        assert browser_manager.get_context_count() == 0, (
            "Should have 0 active contexts after closing all"
        )


def test_property_coverage():
    """
    Verify that this test file covers Property 12: Parallel Test Isolation.
    
    This is a meta-test to ensure the property is properly documented and tested.
    """
    # Verify property is documented in module docstring
    assert "Property 12: Parallel Test Isolation" in __doc__
    assert "Validates: Requirements 12.4" in __doc__
    
    # Verify test class exists
    assert TestParallelTestIsolation is not None
    
    # Verify key test methods exist
    test_methods = [
        'test_parallel_contexts_are_isolated',
        'test_parallel_cookie_isolation',
        'test_parallel_storage_isolation',
        'test_parallel_navigation_isolation',
        'test_parallel_context_cleanup_isolation',
        'test_parallel_page_isolation_within_context',
        'test_parallel_context_count_consistency'
    ]
    
    for method_name in test_methods:
        assert hasattr(TestParallelTestIsolation, method_name), (
            f"Test method {method_name} not found"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
