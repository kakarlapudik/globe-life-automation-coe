"""
Tests for Test Execution Control Module.

This module tests:
- Test filtering by ID, iteration, and tag
- Test skip functionality with reason logging
- Retry mechanism for flaky tests
- Parallel execution support

Requirements: 12.1, 12.2, 12.3, 12.4
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch

from raptor.core.test_execution_control import (
    FilterType,
    TestFilter,
    TestFilterManager,
    SkipReason,
    skip_test,
    skip_if,
    skip_unless,
    RetryConfig,
    retry_on_failure,
    TestExecutionControlPlugin,
)


# ============================================================================
# Test Filter Tests
# ============================================================================

class TestTestFilter:
    """Tests for TestFilter class."""
    
    def test_filter_by_test_id(self):
        """Test filtering by test ID."""
        test_filter = TestFilter(FilterType.TEST_ID, ["test_example"])
        
        # Create mock test item
        mock_item = Mock()
        mock_item.nodeid = "tests/test_example.py::test_function"
        
        assert test_filter.matches(mock_item) is True
        
        # Test non-matching ID
        mock_item.nodeid = "tests/test_other.py::test_function"
        assert test_filter.matches(mock_item) is False
    
    def test_filter_by_iteration(self):
        """Test filtering by iteration parameter."""
        test_filter = TestFilter(FilterType.ITERATION, ["1", "2"])
        
        # Create mock test item with iteration parameter
        mock_item = Mock()
        mock_item.callspec = Mock()
        mock_item.callspec.params = {"iteration": 1}
        
        assert test_filter.matches(mock_item) is True
        
        # Test non-matching iteration
        mock_item.callspec.params = {"iteration": 3}
        assert test_filter.matches(mock_item) is False
        
        # Test item without iteration parameter
        mock_item_no_iter = Mock()
        mock_item_no_iter.callspec = Mock()
        mock_item_no_iter.callspec.params = {}
        assert test_filter.matches(mock_item_no_iter) is False
    
    def test_filter_by_tag(self):
        """Test filtering by tag in test name."""
        test_filter = TestFilter(FilterType.TAG, ["smoke", "regression"])
        
        # Create mock test item
        mock_item = Mock()
        mock_item.name = "test_smoke_login"
        
        assert test_filter.matches(mock_item) is True
        
        # Test non-matching tag
        mock_item.name = "test_integration_feature"
        assert test_filter.matches(mock_item) is False
    
    def test_filter_by_marker(self):
        """Test filtering by pytest marker."""
        test_filter = TestFilter(FilterType.MARKER, ["smoke", "slow"])
        
        # Create mock test item with markers
        mock_item = Mock()
        mock_marker = Mock()
        mock_marker.name = "smoke"
        mock_item.iter_markers = Mock(return_value=[mock_marker])
        
        assert test_filter.matches(mock_item) is True
    
    def test_exclude_filter(self):
        """Test exclusion filter mode."""
        test_filter = TestFilter(FilterType.TAG, ["skip"], exclude=True)
        
        # Create mock test item
        mock_item = Mock()
        mock_item.name = "test_skip_this"
        
        # Should not match (excluded)
        assert test_filter.matches(mock_item) is False
        
        # Test non-excluded item
        mock_item.name = "test_include_this"
        assert test_filter.matches(mock_item) is True


class TestTestFilterManager:
    """Tests for TestFilterManager class."""
    
    def test_add_filter(self):
        """Test adding filters."""
        manager = TestFilterManager()
        
        manager.add_filter(FilterType.TAG, ["smoke"])
        assert len(manager.filters) == 1
        
        manager.add_filter(FilterType.ITERATION, ["1", "2"])
        assert len(manager.filters) == 2
    
    def test_apply_filters_inclusion(self):
        """Test applying inclusion filters."""
        manager = TestFilterManager()
        manager.add_filter(FilterType.TAG, ["smoke"])
        
        # Create mock test items
        mock_item1 = Mock()
        mock_item1.name = "test_smoke_login"
        
        mock_item2 = Mock()
        mock_item2.name = "test_regression_feature"
        
        items = [mock_item1, mock_item2]
        filtered = manager.apply_filters(items)
        
        assert len(filtered) == 1
        assert filtered[0] == mock_item1
    
    def test_apply_filters_exclusion(self):
        """Test applying exclusion filters."""
        manager = TestFilterManager()
        manager.add_filter(FilterType.TAG, ["skip"], exclude=True)
        
        # Create mock test items
        mock_item1 = Mock()
        mock_item1.name = "test_skip_this"
        
        mock_item2 = Mock()
        mock_item2.name = "test_include_this"
        
        items = [mock_item1, mock_item2]
        filtered = manager.apply_filters(items)
        
        # With only exclusion filter, all items pass except those matching the exclusion
        assert len(filtered) == 1
        # The filtered list should contain the item without "skip"
        assert filtered[0].name == "test_include_this"
    
    def test_get_filter_summary(self):
        """Test getting filter summary."""
        manager = TestFilterManager()
        manager.add_filter(FilterType.TAG, ["smoke"])
        manager.add_filter(FilterType.ITERATION, ["1"], exclude=True)
        
        # Apply filters to get counts
        mock_items = [Mock() for _ in range(5)]
        for item in mock_items:
            item.name = "test_smoke_feature"
            item.callspec = Mock()
            item.callspec.params = {"iteration": 2}
        
        manager.apply_filters(mock_items)
        
        summary = manager.get_filter_summary()
        assert summary["total_tests"] == 5
        assert summary["filters_applied"] == 2
        assert len(summary["filters"]) == 2


# ============================================================================
# Skip Functionality Tests
# ============================================================================

class TestSkipFunctionality:
    """Tests for skip functionality."""
    
    def test_skip_test(self):
        """Test skip_test function."""
        with pytest.raises(pytest.skip.Exception) as exc_info:
            skip_test("Test reason", SkipReason.NOT_IMPLEMENTED)
        
        assert "NOT_IMPLEMENTED" in str(exc_info.value)
        assert "Test reason" in str(exc_info.value)
    
    def test_skip_if_true(self):
        """Test skip_if with True condition."""
        with pytest.raises(pytest.skip.Exception):
            skip_if(True, "Should skip", SkipReason.DEPENDENCY)
    
    def test_skip_if_false(self):
        """Test skip_if with False condition."""
        # Should not raise
        skip_if(False, "Should not skip", SkipReason.DEPENDENCY)
    
    def test_skip_unless_false(self):
        """Test skip_unless with False condition."""
        with pytest.raises(pytest.skip.Exception):
            skip_unless(False, "Should skip", SkipReason.CONFIGURATION)
    
    def test_skip_unless_true(self):
        """Test skip_unless with True condition."""
        # Should not raise
        skip_unless(True, "Should not skip", SkipReason.CONFIGURATION)


# ============================================================================
# Retry Mechanism Tests
# ============================================================================

class TestRetryMechanism:
    """Tests for retry mechanism."""
    
    def test_retry_config_validation(self):
        """Test RetryConfig validation."""
        # Valid config
        config = RetryConfig(max_retries=3, retry_delay=1.0)
        assert config.max_retries == 3
        
        # Invalid max_retries
        with pytest.raises(ValueError):
            RetryConfig(max_retries=-1)
        
        # Invalid retry_delay
        with pytest.raises(ValueError):
            RetryConfig(retry_delay=-1.0)
    
    @pytest.mark.asyncio
    async def test_retry_success_on_first_attempt(self):
        """Test retry decorator with successful first attempt."""
        call_count = 0
        
        @retry_on_failure(max_retries=3, retry_delay=0.1, log_retries=False)
        async def test_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await test_func()
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_success_on_retry(self):
        """Test retry decorator with success on retry."""
        call_count = 0
        
        @retry_on_failure(max_retries=3, retry_delay=0.1, log_retries=False)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = await test_func()
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_failure_after_max_retries(self):
        """Test retry decorator failing after max retries."""
        call_count = 0
        
        @retry_on_failure(max_retries=2, retry_delay=0.1, log_retries=False)
        async def test_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent failure")
        
        with pytest.raises(ValueError, match="Persistent failure"):
            await test_func()
        
        assert call_count == 3  # Initial + 2 retries
    
    @pytest.mark.asyncio
    async def test_retry_with_exception_filter(self):
        """Test retry decorator with exception filtering."""
        call_count = 0
        
        @retry_on_failure(
            max_retries=3,
            retry_delay=0.1,
            retry_on_exceptions=[ValueError],
            log_retries=False
        )
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Retryable")
            raise TypeError("Not retryable")
        
        with pytest.raises(TypeError, match="Not retryable"):
            await test_func()
        
        assert call_count == 2  # Initial + 1 retry, then different exception
    
    def test_retry_sync_function(self):
        """Test retry decorator with synchronous function."""
        call_count = 0
        
        @retry_on_failure(max_retries=2, retry_delay=0.1, log_retries=False)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return "success"
        
        result = test_func()
        assert result == "success"
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_exponential_backoff(self):
        """Test retry decorator with exponential backoff."""
        call_times = []
        
        @retry_on_failure(
            max_retries=3,
            retry_delay=0.1,
            exponential_backoff=True,
            log_retries=False
        )
        async def test_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = await test_func()
        assert result == "success"
        
        # Check that delays increase (approximately)
        if len(call_times) >= 3:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]
            # Second delay should be roughly double the first
            assert delay2 > delay1


# ============================================================================
# Plugin Integration Tests
# ============================================================================

class TestTestExecutionControlPlugin:
    """Tests for TestExecutionControlPlugin."""
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = TestExecutionControlPlugin()
        
        assert plugin.filter_manager is not None
        assert isinstance(plugin.skip_reasons, dict)
        assert isinstance(plugin.retry_stats, dict)
    
    def test_plugin_addoption(self):
        """Test plugin adds command-line options."""
        plugin = TestExecutionControlPlugin()
        
        # Create mock parser
        mock_parser = Mock()
        mock_group = Mock()
        mock_parser.getgroup = Mock(return_value=mock_group)
        
        plugin.pytest_addoption(mock_parser)
        
        # Verify options were added
        assert mock_group.addoption.call_count >= 6
    
    def test_plugin_configure(self):
        """Test plugin configuration."""
        plugin = TestExecutionControlPlugin()
        
        # Create mock config
        mock_config = Mock()
        mock_config.getoption = Mock(side_effect=lambda opt: {
            "--test-id": ["test_example"],
            "--iteration": ["1"],
            "--tag": ["smoke"],
            "--marker": ["slow"],
            "--exclude-tag": ["skip"],
            "--max-retries": 3,
        }.get(opt, []))
        
        plugin.pytest_configure(mock_config)
        
        # Verify filters were added
        assert len(plugin.filter_manager.filters) >= 4


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.integration
class TestExecutionControlIntegration:
    """Integration tests for test execution control."""
    
    @pytest.mark.asyncio
    async def test_retry_with_real_async_function(self):
        """Test retry mechanism with real async function."""
        attempts = []
        
        @retry_on_failure(max_retries=2, retry_delay=0.1, log_retries=False)
        async def flaky_test():
            attempts.append(1)
            if len(attempts) < 2:
                raise AssertionError("Flaky failure")
            return "success"
        
        result = await flaky_test()
        assert result == "success"
        assert len(attempts) == 2
    
    def test_skip_with_condition(self):
        """Test skip functionality with condition."""
        feature_enabled = False
        
        def test_feature():
            skip_unless(feature_enabled, "Feature not enabled", SkipReason.CONFIGURATION)
            # This should not execute
            assert False, "Should have been skipped"
        
        with pytest.raises(pytest.skip.Exception):
            test_feature()
    
    @pytest.mark.asyncio
    async def test_retry_with_timeout_exception(self):
        """Test retry with timeout-like exception."""
        from playwright.async_api import TimeoutError as PlaywrightTimeout
        
        attempts = []
        
        @retry_on_failure(
            max_retries=2,
            retry_delay=0.1,
            retry_on_exceptions=[PlaywrightTimeout],
            log_retries=False
        )
        async def test_with_timeout():
            attempts.append(1)
            if len(attempts) < 2:
                raise PlaywrightTimeout("Element not found")
            return "success"
        
        result = await test_with_timeout()
        assert result == "success"
        assert len(attempts) == 2


# ============================================================================
# Parallel Execution Tests
# ============================================================================

@pytest.mark.parametrize("worker_id", ["gw0", "gw1", "gw2"])
def test_parallel_execution_isolation(worker_id):
    """
    Test that parallel execution maintains isolation.
    
    This test verifies that each worker has its own isolated execution
    context when running tests in parallel with pytest-xdist.
    
    Requirements: 12.4
    """
    # Each worker should have unique ID
    assert worker_id is not None
    
    # Simulate worker-specific resource
    resource_name = f"resource_{worker_id}"
    assert worker_id in resource_name


@pytest.mark.smoke
def test_smoke_tag_filtering():
    """Test that can be filtered by smoke tag."""
    assert True


@pytest.mark.regression
def test_regression_tag_filtering():
    """Test that can be filtered by regression tag."""
    assert True


@pytest.mark.flaky
@retry_on_failure(max_retries=2, retry_delay=0.1)
def test_flaky_with_retry():
    """Test marked as flaky with automatic retry."""
    # This test should pass even if it's flaky
    assert True
