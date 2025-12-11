"""
Unit Tests for Soft Assertion Support.

This module tests the soft assertion functionality including:
- SoftAssertionCollector behavior
- Soft verification methods in ElementManager
- Failure collection and reporting
- Collector state management
"""

import pytest
from datetime import datetime
from raptor.core.soft_assertion_collector import SoftAssertionCollector, AssertionFailure


class TestSoftAssertionCollector:
    """Test suite for SoftAssertionCollector class."""
    
    def test_collector_initialization(self):
        """Test that collector initializes with empty state."""
        collector = SoftAssertionCollector()
        
        assert collector.get_failure_count() == 0
        assert collector.get_verification_count() == 0
        assert not collector.has_failures()
        assert collector.get_failures() == []
    
    def test_add_failure(self):
        """Test adding a failure to the collector."""
        collector = SoftAssertionCollector()
        
        collector.add_failure(
            locator="css=#test",
            verification_type="verify_exists",
            expected="element exists",
            actual="element not found",
            message="Test element should exist",
            page_url="https://example.com"
        )
        
        assert collector.get_failure_count() == 1
        assert collector.has_failures()
        
        failures = collector.get_failures()
        assert len(failures) == 1
        assert failures[0].locator == "css=#test"
        assert failures[0].verification_type == "verify_exists"
        assert failures[0].expected == "element exists"
        assert failures[0].actual == "element not found"
        assert failures[0].message == "Test element should exist"
        assert failures[0].page_url == "https://example.com"
    
    def test_add_multiple_failures(self):
        """Test adding multiple failures."""
        collector = SoftAssertionCollector()
        
        collector.add_failure(
            locator="css=#element1",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Failure 1"
        )
        
        collector.add_failure(
            locator="css=#element2",
            verification_type="verify_enabled",
            expected="enabled",
            actual="disabled",
            message="Failure 2"
        )
        
        collector.add_failure(
            locator="css=#element3",
            verification_type="verify_text",
            expected="Hello",
            actual="Goodbye",
            message="Failure 3"
        )
        
        assert collector.get_failure_count() == 3
        assert len(collector.get_failures()) == 3
    
    def test_increment_count(self):
        """Test incrementing verification count."""
        collector = SoftAssertionCollector()
        
        assert collector.get_verification_count() == 0
        
        collector.increment_count()
        assert collector.get_verification_count() == 1
        
        collector.increment_count()
        collector.increment_count()
        assert collector.get_verification_count() == 3
    
    def test_has_failures(self):
        """Test has_failures() method."""
        collector = SoftAssertionCollector()
        
        assert not collector.has_failures()
        
        collector.add_failure(
            locator="css=#test",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Test failure"
        )
        
        assert collector.has_failures()
    
    def test_clear(self):
        """Test clearing the collector."""
        collector = SoftAssertionCollector()
        
        # Add some data
        collector.increment_count()
        collector.increment_count()
        collector.add_failure(
            locator="css=#test",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Test failure"
        )
        
        assert collector.get_verification_count() == 2
        assert collector.get_failure_count() == 1
        
        # Clear
        collector.clear()
        
        assert collector.get_verification_count() == 0
        assert collector.get_failure_count() == 0
        assert not collector.has_failures()
    
    def test_assert_all_no_failures(self):
        """Test assert_all() with no failures."""
        collector = SoftAssertionCollector()
        
        collector.increment_count()
        collector.increment_count()
        
        # Should not raise
        collector.assert_all()
    
    def test_assert_all_with_failures(self):
        """Test assert_all() with failures."""
        collector = SoftAssertionCollector()
        
        collector.increment_count()
        collector.add_failure(
            locator="css=#test",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Test failure"
        )
        
        with pytest.raises(AssertionError) as exc_info:
            collector.assert_all()
        
        error_message = str(exc_info.value)
        assert "SOFT ASSERTION FAILURES" in error_message
        assert "1 of 1 verifications failed" in error_message
        assert "css=#test" in error_message
        assert "Test failure" in error_message
    
    def test_assert_all_multiple_failures(self):
        """Test assert_all() with multiple failures."""
        collector = SoftAssertionCollector()
        
        collector.increment_count()
        collector.increment_count()
        collector.increment_count()
        
        collector.add_failure(
            locator="css=#element1",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Failure 1"
        )
        
        collector.add_failure(
            locator="css=#element2",
            verification_type="verify_enabled",
            expected="enabled",
            actual="disabled",
            message="Failure 2"
        )
        
        with pytest.raises(AssertionError) as exc_info:
            collector.assert_all()
        
        error_message = str(exc_info.value)
        assert "2 of 3 verifications failed" in error_message
        assert "Passed: 1, Failed: 2" in error_message
        assert "Failure 1" in error_message
        assert "Failure 2" in error_message
    
    def test_get_summary(self):
        """Test get_summary() method."""
        collector = SoftAssertionCollector()
        
        collector.increment_count()
        collector.increment_count()
        collector.increment_count()
        
        collector.add_failure(
            locator="css=#test",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Test failure"
        )
        
        summary = collector.get_summary()
        
        assert summary["total_verifications"] == 3
        assert summary["failures"] == 1
        assert summary["passed"] == 2
        assert summary["has_failures"] is True
        assert len(summary["failure_details"]) == 1
        assert summary["failure_details"][0]["locator"] == "css=#test"
        assert summary["failure_details"][0]["message"] == "Test failure"
    
    def test_str_representation(self):
        """Test string representation of collector."""
        collector = SoftAssertionCollector()
        
        # No failures
        collector.increment_count()
        collector.increment_count()
        str_repr = str(collector)
        assert "2 verifications" in str_repr
        assert "all passed" in str_repr
        
        # With failures
        collector.add_failure(
            locator="css=#test",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Test failure"
        )
        str_repr = str(collector)
        assert "2 verifications" in str_repr
        assert "1 failed" in str_repr
    
    def test_repr_representation(self):
        """Test repr representation of collector."""
        collector = SoftAssertionCollector()
        
        collector.increment_count()
        collector.add_failure(
            locator="css=#test",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Test failure"
        )
        
        repr_str = repr(collector)
        assert "SoftAssertionCollector" in repr_str
        assert "verifications=1" in repr_str
        assert "failures=1" in repr_str
    
    def test_failure_order_preserved(self):
        """Test that failure order is preserved."""
        collector = SoftAssertionCollector()
        
        collector.add_failure(
            locator="css=#first",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="First failure"
        )
        
        collector.add_failure(
            locator="css=#second",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Second failure"
        )
        
        collector.add_failure(
            locator="css=#third",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Third failure"
        )
        
        failures = collector.get_failures()
        assert failures[0].locator == "css=#first"
        assert failures[1].locator == "css=#second"
        assert failures[2].locator == "css=#third"
    
    def test_additional_context(self):
        """Test adding additional context to failures."""
        collector = SoftAssertionCollector()
        
        collector.add_failure(
            locator="css=#test",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Test failure",
            page_url="https://example.com",
            timeout_ms=5000,
            custom_field="custom_value"
        )
        
        failures = collector.get_failures()
        assert failures[0].additional_context["timeout_ms"] == 5000
        assert failures[0].additional_context["custom_field"] == "custom_value"


class TestAssertionFailure:
    """Test suite for AssertionFailure dataclass."""
    
    def test_assertion_failure_creation(self):
        """Test creating an AssertionFailure."""
        failure = AssertionFailure(
            locator="css=#test",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Test failure",
            page_url="https://example.com"
        )
        
        assert failure.locator == "css=#test"
        assert failure.verification_type == "verify_exists"
        assert failure.expected == "exists"
        assert failure.actual == "not found"
        assert failure.message == "Test failure"
        assert failure.page_url == "https://example.com"
        assert isinstance(failure.timestamp, datetime)
    
    def test_assertion_failure_str(self):
        """Test string representation of AssertionFailure."""
        failure = AssertionFailure(
            locator="css=#test",
            verification_type="verify_exists",
            expected="exists",
            actual="not found",
            message="Test failure",
            page_url="https://example.com"
        )
        
        str_repr = str(failure)
        assert "Verification Failed: verify_exists" in str_repr
        assert "Locator: css=#test" in str_repr
        assert "Expected: exists" in str_repr
        assert "Actual: not found" in str_repr
        assert "Message: Test failure" in str_repr
        assert "Page URL: https://example.com" in str_repr
    
    def test_assertion_failure_with_context(self):
        """Test AssertionFailure with additional context."""
        failure = AssertionFailure(
            locator="css=#test",
            verification_type="verify_text",
            expected="Hello",
            actual="Goodbye",
            message="Text mismatch",
            page_url="https://example.com",
            additional_context={"exact_match": True, "case_sensitive": False}
        )
        
        assert failure.additional_context["exact_match"] is True
        assert failure.additional_context["case_sensitive"] is False
        
        str_repr = str(failure)
        assert "Context:" in str_repr


class TestSoftAssertionIntegration:
    """Integration tests for soft assertions with ElementManager."""
    
    @pytest.mark.asyncio
    async def test_soft_assertions_workflow(self):
        """Test complete soft assertion workflow."""
        from playwright.async_api import async_playwright
        from raptor.core.element_manager import ElementManager
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Create a test page
            await page.set_content("""
            <!DOCTYPE html>
            <html>
            <body>
                <h1>Test Page</h1>
                <button id="enabled-button">Click Me</button>
                <button id="disabled-button" disabled>Disabled</button>
                <p id="message">Hello World</p>
            </body>
            </html>
            """)
            
            element_manager = ElementManager(page)
            collector = SoftAssertionCollector()
            
            # Perform soft verifications
            result1 = await element_manager.soft_verify_exists("css=h1", collector)
            assert result1 is True
            
            result2 = await element_manager.soft_verify_text("css=h1", "Test Page", collector)
            assert result2 is True
            
            result3 = await element_manager.soft_verify_enabled("css=#enabled-button", collector)
            assert result3 is True
            
            result4 = await element_manager.soft_verify_disabled("css=#disabled-button", collector)
            assert result4 is True
            
            result5 = await element_manager.soft_verify_visible("css=#message", collector)
            assert result5 is True
            
            # All should pass
            assert collector.get_verification_count() == 5
            assert collector.get_failure_count() == 0
            collector.assert_all()  # Should not raise
            
            await browser.close()
    
    @pytest.mark.asyncio
    async def test_soft_assertions_with_failures(self):
        """Test soft assertions that fail."""
        from playwright.async_api import async_playwright
        from raptor.core.element_manager import ElementManager
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            await page.set_content("""
            <!DOCTYPE html>
            <html>
            <body>
                <h1>Test Page</h1>
                <button id="button" disabled>Button</button>
            </body>
            </html>
            """)
            
            element_manager = ElementManager(page)
            collector = SoftAssertionCollector()
            
            # This will pass
            result1 = await element_manager.soft_verify_exists("css=h1", collector)
            assert result1 is True
            
            # This will fail - element doesn't exist
            result2 = await element_manager.soft_verify_exists("css=#nonexistent", collector, timeout=2000)
            assert result2 is False
            
            # This will fail - button is disabled
            result3 = await element_manager.soft_verify_enabled("css=#button", collector)
            assert result3 is False
            
            # This will fail - wrong text
            result4 = await element_manager.soft_verify_text("css=h1", "Wrong Text", collector)
            assert result4 is False
            
            # Check results
            assert collector.get_verification_count() == 4
            assert collector.get_failure_count() == 3
            assert collector.has_failures()
            
            # assert_all should raise
            with pytest.raises(AssertionError) as exc_info:
                collector.assert_all()
            
            error_message = str(exc_info.value)
            assert "3 of 4 verifications failed" in error_message
            
            await browser.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
