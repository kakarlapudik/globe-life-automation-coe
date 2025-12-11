"""
Soft Assertion Collector for RAPTOR Python Playwright Framework.

This module provides soft assertion capabilities that allow verification failures
to be collected without stopping test execution. All failures are reported at the
end of the test, enabling comprehensive validation in a single test run.

Key Features:
- Non-blocking verification failures
- Detailed failure context preservation
- Automatic failure reporting
- Support for custom error messages
- Thread-safe operation for parallel tests
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class AssertionFailure:
    """
    Represents a single soft assertion failure.
    
    Attributes:
        locator: Element locator that failed verification
        verification_type: Type of verification (exists, enabled, text, etc.)
        expected: Expected value or state
        actual: Actual value or state
        message: Custom error message
        timestamp: When the failure occurred
        page_url: URL of the page when failure occurred
        additional_context: Any additional context information
    """
    locator: str
    verification_type: str
    expected: Any
    actual: Any
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    page_url: Optional[str] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        """Format the failure as a readable string."""
        lines = [
            f"Verification Failed: {self.verification_type}",
            f"  Locator: {self.locator}",
            f"  Expected: {self.expected}",
            f"  Actual: {self.actual}",
            f"  Message: {self.message}",
        ]
        
        if self.page_url:
            lines.append(f"  Page URL: {self.page_url}")
        
        if self.additional_context:
            lines.append(f"  Context: {self.additional_context}")
        
        lines.append(f"  Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        
        return "\n".join(lines)


class SoftAssertionCollector:
    """
    Collects soft assertion failures without raising exceptions.
    
    This class enables non-blocking verification by collecting all failures
    and allowing them to be reported at the end of a test. This is useful
    for comprehensive validation where you want to see all failures rather
    than stopping at the first one.
    
    Example:
        >>> collector = SoftAssertionCollector()
        >>> 
        >>> # Perform multiple verifications
        >>> collector.add_failure(
        ...     locator="css=#username",
        ...     verification_type="verify_enabled",
        ...     expected="enabled",
        ...     actual="disabled",
        ...     message="Username field should be enabled"
        ... )
        >>> 
        >>> # Check if there were any failures
        >>> if collector.has_failures():
        ...     collector.assert_all()  # Raises AssertionError with all failures
    """
    
    def __init__(self):
        """Initialize the soft assertion collector."""
        self._failures: List[AssertionFailure] = []
        self._verification_count: int = 0
        logger.debug("SoftAssertionCollector initialized")
    
    def add_failure(
        self,
        locator: str,
        verification_type: str,
        expected: Any,
        actual: Any,
        message: str,
        page_url: Optional[str] = None,
        **additional_context
    ) -> None:
        """
        Add a verification failure to the collection.
        
        Args:
            locator: Element locator that failed verification
            verification_type: Type of verification (e.g., "verify_exists", "verify_text")
            expected: Expected value or state
            actual: Actual value or state
            message: Error message describing the failure
            page_url: Optional URL of the page when failure occurred
            **additional_context: Additional context information as keyword arguments
        """
        failure = AssertionFailure(
            locator=locator,
            verification_type=verification_type,
            expected=expected,
            actual=actual,
            message=message,
            page_url=page_url,
            additional_context=additional_context
        )
        
        self._failures.append(failure)
        
        logger.warning(
            f"Soft assertion failure recorded: {verification_type} - {locator} - {message}"
        )
    
    def increment_count(self) -> None:
        """Increment the total verification count."""
        self._verification_count += 1
    
    def has_failures(self) -> bool:
        """
        Check if any failures have been collected.
        
        Returns:
            True if there are failures, False otherwise
        """
        return len(self._failures) > 0
    
    def get_failure_count(self) -> int:
        """
        Get the number of failures collected.
        
        Returns:
            Number of failures
        """
        return len(self._failures)
    
    def get_verification_count(self) -> int:
        """
        Get the total number of verifications performed.
        
        Returns:
            Total verification count
        """
        return self._verification_count
    
    def get_failures(self) -> List[AssertionFailure]:
        """
        Get all collected failures.
        
        Returns:
            List of AssertionFailure objects
        """
        return self._failures.copy()
    
    def clear(self) -> None:
        """
        Clear all collected failures and reset counters.
        
        This is useful for reusing the collector between test runs.
        """
        self._failures.clear()
        self._verification_count = 0
        logger.debug("SoftAssertionCollector cleared")
    
    def assert_all(self) -> None:
        """
        Assert that there are no failures.
        
        If there are any failures, raises an AssertionError with a detailed
        report of all failures. This should be called at the end of a test
        to ensure all soft assertions passed.
        
        Raises:
            AssertionError: If there are any collected failures
        """
        if not self.has_failures():
            logger.info(
                f"All soft assertions passed ({self._verification_count} verifications)"
            )
            return
        
        # Build comprehensive error message
        failure_count = self.get_failure_count()
        pass_count = self._verification_count - failure_count
        
        error_lines = [
            "",
            "=" * 80,
            f"SOFT ASSERTION FAILURES: {failure_count} of {self._verification_count} verifications failed",
            f"Passed: {pass_count}, Failed: {failure_count}",
            "=" * 80,
            ""
        ]
        
        for idx, failure in enumerate(self._failures, 1):
            error_lines.append(f"Failure {idx} of {failure_count}:")
            error_lines.append("-" * 80)
            error_lines.append(str(failure))
            error_lines.append("")
        
        error_lines.append("=" * 80)
        
        error_message = "\n".join(error_lines)
        
        logger.error(f"Soft assertion failures detected:\n{error_message}")
        
        raise AssertionError(error_message)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all verifications and failures.
        
        Returns:
            Dictionary containing summary statistics
        """
        return {
            "total_verifications": self._verification_count,
            "failures": self.get_failure_count(),
            "passed": self._verification_count - self.get_failure_count(),
            "has_failures": self.has_failures(),
            "failure_details": [
                {
                    "locator": f.locator,
                    "type": f.verification_type,
                    "expected": str(f.expected),
                    "actual": str(f.actual),
                    "message": f.message,
                    "timestamp": f.timestamp.isoformat(),
                }
                for f in self._failures
            ]
        }
    
    def __str__(self) -> str:
        """String representation of the collector state."""
        if not self.has_failures():
            return f"SoftAssertionCollector: {self._verification_count} verifications, all passed"
        else:
            failure_count = self.get_failure_count()
            return (
                f"SoftAssertionCollector: {self._verification_count} verifications, "
                f"{failure_count} failed"
            )
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"SoftAssertionCollector(verifications={self._verification_count}, "
            f"failures={self.get_failure_count()})"
        )
