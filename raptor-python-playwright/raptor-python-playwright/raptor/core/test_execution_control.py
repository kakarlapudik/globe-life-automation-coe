"""
Test Execution Control for RAPTOR Python Playwright Framework.

This module provides test execution control features including:
- Test filtering by ID, iteration, or tag
- Test skip functionality with reason logging
- Retry mechanism for flaky tests
- Support for parallel execution with pytest-xdist

Requirements: 12.1, 12.2, 12.3, 12.4
"""

import logging
import functools
import time
from typing import Optional, Callable, Any, List, Dict, Set
from dataclasses import dataclass
from enum import Enum

import pytest

logger = logging.getLogger(__name__)


# ============================================================================
# Test Filter Configuration
# ============================================================================

class FilterType(Enum):
    """Types of test filters supported."""
    TEST_ID = "test_id"
    ITERATION = "iteration"
    TAG = "tag"
    MARKER = "marker"


@dataclass
class TestFilter:
    """
    Configuration for test filtering.
    
    Attributes:
        filter_type: Type of filter to apply
        values: List of values to match
        exclude: If True, exclude matching tests instead of including them
    """
    filter_type: FilterType
    values: List[str]
    exclude: bool = False
    
    def matches(self, test_item: pytest.Item) -> bool:
        """
        Check if a test item matches this filter.
        
        Args:
            test_item: pytest test item to check
            
        Returns:
            True if test matches filter criteria
        """
        if self.filter_type == FilterType.TEST_ID:
            # Match by test node ID
            test_id = test_item.nodeid
            matches = any(value in test_id for value in self.values)
            
        elif self.filter_type == FilterType.ITERATION:
            # Match by iteration parameter
            if hasattr(test_item, 'callspec') and 'iteration' in test_item.callspec.params:
                iteration = str(test_item.callspec.params['iteration'])
                matches = iteration in self.values
            else:
                matches = False
                
        elif self.filter_type == FilterType.TAG:
            # Match by custom tag in test name or markers
            test_name = test_item.name.lower()
            matches = any(tag.lower() in test_name for tag in self.values)
            
        elif self.filter_type == FilterType.MARKER:
            # Match by pytest marker
            test_markers = {marker.name for marker in test_item.iter_markers()}
            matches = any(marker in test_markers for marker in self.values)
            
        else:
            matches = False
        
        # Invert if exclude mode
        return not matches if self.exclude else matches


class TestFilterManager:
    """
    Manages test filtering configuration and application.
    
    This class handles:
    - Registering test filters
    - Applying filters to test collection
    - Logging filter results
    
    Example:
        >>> filter_manager = TestFilterManager()
        >>> filter_manager.add_filter(FilterType.TAG, ["smoke", "regression"])
        >>> filter_manager.add_filter(FilterType.ITERATION, ["1", "2"])
    """
    
    def __init__(self):
        """Initialize the test filter manager."""
        self.filters: List[TestFilter] = []
        self._filtered_count = 0
        self._total_count = 0
        
    def add_filter(
        self,
        filter_type: FilterType,
        values: List[str],
        exclude: bool = False
    ) -> None:
        """
        Add a test filter.
        
        Args:
            filter_type: Type of filter to add
            values: List of values to match
            exclude: If True, exclude matching tests
        """
        test_filter = TestFilter(filter_type, values, exclude)
        self.filters.append(test_filter)
        logger.info(
            f"Added {'exclusion' if exclude else 'inclusion'} filter: "
            f"{filter_type.value} = {values}"
        )
    
    def apply_filters(self, items: List[pytest.Item]) -> List[pytest.Item]:
        """
        Apply all registered filters to test items.
        
        Args:
            items: List of pytest test items
            
        Returns:
            Filtered list of test items
        """
        if not self.filters:
            return items
        
        self._total_count = len(items)
        filtered_items = []
        
        for item in items:
            # Check all filters
            include = True
            
            # For inclusion filters: test must match ALL of them
            inclusion_filters = [f for f in self.filters if not f.exclude]
            if inclusion_filters:
                for test_filter in inclusion_filters:
                    if not test_filter.matches(item):
                        include = False
                        break
            
            # For exclusion filters: test must not match ANY of them
            # Note: matches() already inverts for exclude=True filters
            if include:
                exclusion_filters = [f for f in self.filters if f.exclude]
                for test_filter in exclusion_filters:
                    # For exclusion filters, matches() returns True if item should be INCLUDED
                    # (because it inverts the match internally)
                    if not test_filter.matches(item):
                        include = False
                        break
            
            if include:
                filtered_items.append(item)
        
        self._filtered_count = len(filtered_items)
        logger.info(
            f"Test filtering: {self._filtered_count}/{self._total_count} tests selected"
        )
        
        return filtered_items
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """
        Get summary of filter application.
        
        Returns:
            Dictionary with filter statistics
        """
        return {
            "total_tests": self._total_count,
            "filtered_tests": self._filtered_count,
            "filters_applied": len(self.filters),
            "filters": [
                {
                    "type": f.filter_type.value,
                    "values": f.values,
                    "exclude": f.exclude
                }
                for f in self.filters
            ]
        }


# ============================================================================
# Test Skip Functionality
# ============================================================================

class SkipReason(Enum):
    """Standard skip reasons for tests."""
    NOT_IMPLEMENTED = "Feature not yet implemented"
    ENVIRONMENT = "Not available in current environment"
    DEPENDENCY = "Required dependency not available"
    CONFIGURATION = "Required configuration missing"
    PLATFORM = "Not supported on current platform"
    FLAKY = "Test is known to be flaky"
    MANUAL = "Manual test - requires human interaction"
    CUSTOM = "Custom skip reason"


def skip_test(
    reason: str,
    skip_reason_type: SkipReason = SkipReason.CUSTOM,
    log_level: int = logging.INFO
) -> None:
    """
    Skip a test with detailed reason logging.
    
    This function provides a standardized way to skip tests with proper
    logging and categorization of skip reasons.
    
    Args:
        reason: Detailed reason for skipping the test
        skip_reason_type: Category of skip reason
        log_level: Logging level for skip message
        
    Example:
        >>> def test_feature():
        ...     if not feature_available():
        ...         skip_test("Feature X not available", SkipReason.DEPENDENCY)
        ...     # test code
    """
    skip_message = f"[{skip_reason_type.name}] {reason}"
    logger.log(log_level, f"Skipping test: {skip_message}")
    pytest.skip(skip_message)


def skip_if(
    condition: bool,
    reason: str,
    skip_reason_type: SkipReason = SkipReason.CUSTOM
) -> None:
    """
    Conditionally skip a test.
    
    Args:
        condition: If True, skip the test
        reason: Reason for skipping
        skip_reason_type: Category of skip reason
        
    Example:
        >>> def test_database_feature(database):
        ...     skip_if(database is None, "Database not configured", SkipReason.CONFIGURATION)
        ...     # test code
    """
    if condition:
        skip_test(reason, skip_reason_type)


def skip_unless(
    condition: bool,
    reason: str,
    skip_reason_type: SkipReason = SkipReason.CUSTOM
) -> None:
    """
    Skip test unless condition is met.
    
    Args:
        condition: If False, skip the test
        reason: Reason for skipping
        skip_reason_type: Category of skip reason
        
    Example:
        >>> def test_feature():
        ...     skip_unless(has_feature(), "Feature not enabled", SkipReason.CONFIGURATION)
        ...     # test code
    """
    if not condition:
        skip_test(reason, skip_reason_type)


# ============================================================================
# Retry Mechanism for Flaky Tests
# ============================================================================

@dataclass
class RetryConfig:
    """
    Configuration for test retry mechanism.
    
    Attributes:
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        exponential_backoff: If True, use exponential backoff for delays
        retry_on_exceptions: List of exception types to retry on
        log_retries: If True, log each retry attempt
    """
    max_retries: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = True
    retry_on_exceptions: Optional[List[type]] = None
    log_retries: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_delay < 0:
            raise ValueError("retry_delay must be non-negative")


def retry_on_failure(
    max_retries: int = 3,
    retry_delay: float = 1.0,
    exponential_backoff: bool = True,
    retry_on_exceptions: Optional[List[type]] = None,
    log_retries: bool = True
) -> Callable:
    """
    Decorator to retry flaky tests on failure.
    
    This decorator automatically retries failed tests with configurable
    retry logic including exponential backoff and exception filtering.
    
    Args:
        max_retries: Maximum number of retry attempts
        retry_delay: Initial delay between retries in seconds
        exponential_backoff: If True, double delay after each retry
        retry_on_exceptions: Only retry on these exception types (None = all)
        log_retries: If True, log each retry attempt
        
    Returns:
        Decorated test function with retry logic
        
    Example:
        >>> @retry_on_failure(max_retries=3, retry_delay=2.0)
        ... async def test_flaky_feature(page):
        ...     await page.goto("https://example.com")
        ...     # flaky test code
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            config = RetryConfig(
                max_retries=max_retries,
                retry_delay=retry_delay,
                exponential_backoff=exponential_backoff,
                retry_on_exceptions=retry_on_exceptions,
                log_retries=log_retries
            )
            
            last_exception = None
            current_delay = config.retry_delay
            
            for attempt in range(config.max_retries + 1):
                try:
                    if config.log_retries and attempt > 0:
                        logger.info(
                            f"Retry attempt {attempt}/{config.max_retries} "
                            f"for test: {func.__name__}"
                        )
                    
                    result = await func(*args, **kwargs)
                    
                    if attempt > 0 and config.log_retries:
                        logger.info(
                            f"Test {func.__name__} succeeded on retry attempt {attempt}"
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry on this exception
                    if config.retry_on_exceptions:
                        should_retry = any(
                            isinstance(e, exc_type)
                            for exc_type in config.retry_on_exceptions
                        )
                        if not should_retry:
                            raise
                    
                    # Don't retry if we've exhausted attempts
                    if attempt >= config.max_retries:
                        if config.log_retries:
                            logger.error(
                                f"Test {func.__name__} failed after "
                                f"{config.max_retries} retries: {str(e)}"
                            )
                        raise
                    
                    # Wait before retry
                    if config.log_retries:
                        logger.warning(
                            f"Test {func.__name__} failed (attempt {attempt + 1}), "
                            f"retrying in {current_delay}s: {str(e)}"
                        )
                    
                    time.sleep(current_delay)
                    
                    # Apply exponential backoff
                    if config.exponential_backoff:
                        current_delay *= 2
            
            # Should never reach here, but just in case
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            config = RetryConfig(
                max_retries=max_retries,
                retry_delay=retry_delay,
                exponential_backoff=exponential_backoff,
                retry_on_exceptions=retry_on_exceptions,
                log_retries=log_retries
            )
            
            last_exception = None
            current_delay = config.retry_delay
            
            for attempt in range(config.max_retries + 1):
                try:
                    if config.log_retries and attempt > 0:
                        logger.info(
                            f"Retry attempt {attempt}/{config.max_retries} "
                            f"for test: {func.__name__}"
                        )
                    
                    result = func(*args, **kwargs)
                    
                    if attempt > 0 and config.log_retries:
                        logger.info(
                            f"Test {func.__name__} succeeded on retry attempt {attempt}"
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    
                    # Check if we should retry on this exception
                    if config.retry_on_exceptions:
                        should_retry = any(
                            isinstance(e, exc_type)
                            for exc_type in config.retry_on_exceptions
                        )
                        if not should_retry:
                            raise
                    
                    # Don't retry if we've exhausted attempts
                    if attempt >= config.max_retries:
                        if config.log_retries:
                            logger.error(
                                f"Test {func.__name__} failed after "
                                f"{config.max_retries} retries: {str(e)}"
                            )
                        raise
                    
                    # Wait before retry
                    if config.log_retries:
                        logger.warning(
                            f"Test {func.__name__} failed (attempt {attempt + 1}), "
                            f"retrying in {current_delay}s: {str(e)}"
                        )
                    
                    time.sleep(current_delay)
                    
                    # Apply exponential backoff
                    if config.exponential_backoff:
                        current_delay *= 2
            
            # Should never reach here, but just in case
            raise last_exception
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# ============================================================================
# Pytest Plugin for Test Execution Control
# ============================================================================

class TestExecutionControlPlugin:
    """
    Pytest plugin for test execution control.
    
    This plugin integrates with pytest to provide:
    - Test filtering
    - Skip tracking
    - Retry statistics
    - Parallel execution support
    """
    
    def __init__(self):
        """Initialize the plugin."""
        self.filter_manager = TestFilterManager()
        self.skip_reasons: Dict[str, List[str]] = {}
        self.retry_stats: Dict[str, int] = {}
        
    def pytest_addoption(self, parser):
        """Add custom command-line options."""
        group = parser.getgroup("raptor", "RAPTOR test execution control")
        
        group.addoption(
            "--test-id",
            action="append",
            default=[],
            help="Filter tests by ID (can be used multiple times)"
        )
        
        group.addoption(
            "--iteration",
            action="append",
            default=[],
            help="Filter tests by iteration number (can be used multiple times)"
        )
        
        group.addoption(
            "--tag",
            action="append",
            default=[],
            help="Filter tests by tag (can be used multiple times)"
        )
        
        group.addoption(
            "--marker",
            action="append",
            default=[],
            help="Filter tests by pytest marker (can be used multiple times)"
        )
        
        group.addoption(
            "--exclude-tag",
            action="append",
            default=[],
            help="Exclude tests with tag (can be used multiple times)"
        )
        
        group.addoption(
            "--max-retries",
            type=int,
            default=0,
            help="Maximum number of retries for failed tests"
        )
    
    def pytest_configure(self, config):
        """Configure the plugin based on command-line options."""
        # Setup test ID filters
        test_ids = config.getoption("--test-id")
        if test_ids:
            self.filter_manager.add_filter(FilterType.TEST_ID, test_ids)
        
        # Setup iteration filters
        iterations = config.getoption("--iteration")
        if iterations:
            self.filter_manager.add_filter(FilterType.ITERATION, iterations)
        
        # Setup tag filters
        tags = config.getoption("--tag")
        if tags:
            self.filter_manager.add_filter(FilterType.TAG, tags)
        
        # Setup marker filters
        markers = config.getoption("--marker")
        if markers:
            self.filter_manager.add_filter(FilterType.MARKER, markers)
        
        # Setup exclusion filters
        exclude_tags = config.getoption("--exclude-tag")
        if exclude_tags:
            self.filter_manager.add_filter(FilterType.TAG, exclude_tags, exclude=True)
    
    def pytest_collection_modifyitems(self, config, items):
        """Modify test collection based on filters."""
        if self.filter_manager.filters:
            filtered_items = self.filter_manager.apply_filters(items)
            items[:] = filtered_items
            
            # Log filter summary
            summary = self.filter_manager.get_filter_summary()
            logger.info(f"Test filter summary: {summary}")
    
    def pytest_runtest_makereport(self, item, call):
        """Track test results for retry statistics."""
        if call.when == "call":
            if call.excinfo is not None:
                # Test failed
                test_name = item.nodeid
                self.retry_stats[test_name] = self.retry_stats.get(test_name, 0) + 1
    
    def pytest_terminal_summary(self, terminalreporter, exitstatus, config):
        """Add custom summary information to test report."""
        # Report filter summary
        if self.filter_manager.filters:
            terminalreporter.write_sep("=", "Test Filtering Summary")
            summary = self.filter_manager.get_filter_summary()
            terminalreporter.write_line(
                f"Filters applied: {summary['filters_applied']}"
            )
            terminalreporter.write_line(
                f"Tests selected: {summary['filtered_tests']}/{summary['total_tests']}"
            )
            for filter_info in summary['filters']:
                terminalreporter.write_line(
                    f"  - {filter_info['type']}: {filter_info['values']} "
                    f"({'exclude' if filter_info['exclude'] else 'include'})"
                )
        
        # Report retry statistics
        if self.retry_stats:
            terminalreporter.write_sep("=", "Test Retry Statistics")
            for test_name, retry_count in self.retry_stats.items():
                terminalreporter.write_line(
                    f"{test_name}: {retry_count} retries"
                )


# ============================================================================
# Pytest Plugin Registration
# ============================================================================

def pytest_configure(config):
    """Register the test execution control plugin."""
    plugin = TestExecutionControlPlugin()
    config.pluginmanager.register(plugin, "test_execution_control")
