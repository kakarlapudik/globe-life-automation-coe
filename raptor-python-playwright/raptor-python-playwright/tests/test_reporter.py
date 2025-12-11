"""
Unit tests for the TestReporter class.

Tests cover:
- Test result collection
- Statistics calculation
- HTML report generation
- Screenshot embedding
- Duration tracking
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from raptor.utils.reporter import (
    TestReporter,
    TestResult,
    TestStatus,
    TestStatistics,
)


@pytest.fixture
def temp_report_dir():
    """Create a temporary directory for test reports."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def reporter(temp_report_dir):
    """Create a TestReporter instance with temporary directory."""
    return TestReporter(report_dir=temp_report_dir)


@pytest.fixture
def sample_test_result():
    """Create a sample test result."""
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=2.5)
    
    return TestResult(
        test_id="test_001",
        test_name="Test Login Functionality",
        status=TestStatus.PASSED,
        duration=2.5,
        start_time=start_time,
        end_time=end_time,
        metadata={"browser": "chromium", "environment": "dev"}
    )


@pytest.fixture
def failed_test_result():
    """Create a failed test result with error information."""
    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=1.2)
    
    return TestResult(
        test_id="test_002",
        test_name="Test Data Validation",
        status=TestStatus.FAILED,
        duration=1.2,
        start_time=start_time,
        end_time=end_time,
        error_message="AssertionError: Expected value 'test' but got 'prod'",
        stack_trace="Traceback (most recent call last):\n  File 'test.py', line 10\n    assert value == 'test'",
        metadata={"browser": "firefox"}
    )


class TestTestResult:
    """Tests for TestResult dataclass."""
    
    def test_test_result_creation(self, sample_test_result):
        """Test creating a TestResult instance."""
        assert sample_test_result.test_id == "test_001"
        assert sample_test_result.test_name == "Test Login Functionality"
        assert sample_test_result.status == TestStatus.PASSED
        assert sample_test_result.duration == 2.5
        assert sample_test_result.error_message is None
        assert len(sample_test_result.screenshots) == 0
    
    def test_test_result_to_dict(self, sample_test_result):
        """Test converting TestResult to dictionary."""
        result_dict = sample_test_result.to_dict()
        
        assert result_dict["test_id"] == "test_001"
        assert result_dict["test_name"] == "Test Login Functionality"
        assert result_dict["status"] == "passed"
        assert result_dict["duration"] == 2.5
        assert "start_time" in result_dict
        assert "end_time" in result_dict
    
    def test_failed_test_result(self, failed_test_result):
        """Test failed test result with error information."""
        assert failed_test_result.status == TestStatus.FAILED
        assert failed_test_result.error_message is not None
        assert failed_test_result.stack_trace is not None
        assert "AssertionError" in failed_test_result.error_message


class TestTestStatistics:
    """Tests for TestStatistics dataclass."""
    
    def test_empty_statistics(self):
        """Test statistics with no tests."""
        stats = TestStatistics()
        assert stats.total_tests == 0
        assert stats.passed == 0
        assert stats.failed == 0
        assert stats.pass_rate == 0.0
    
    def test_pass_rate_calculation(self):
        """Test pass rate calculation."""
        stats = TestStatistics(total_tests=10, passed=8, failed=2)
        assert stats.pass_rate == 80.0
    
    def test_statistics_to_dict(self):
        """Test converting statistics to dictionary."""
        stats = TestStatistics(
            total_tests=5,
            passed=3,
            failed=1,
            skipped=1,
            total_duration=10.5
        )
        
        stats_dict = stats.to_dict()
        assert stats_dict["total_tests"] == 5
        assert stats_dict["passed"] == 3
        assert stats_dict["failed"] == 1
        assert stats_dict["skipped"] == 1
        assert stats_dict["pass_rate"] == 60.0


class TestTestReporter:
    """Tests for TestReporter class."""
    
    def test_reporter_initialization(self, temp_report_dir):
        """Test reporter initialization."""
        reporter = TestReporter(report_dir=temp_report_dir)
        
        assert reporter.report_dir == Path(temp_report_dir)
        assert reporter.report_dir.exists()
        assert len(reporter.test_results) == 0
        assert reporter.suite_start_time is None
    
    def test_start_suite(self, reporter):
        """Test starting a test suite."""
        reporter.start_suite("My Test Suite")
        
        assert reporter.suite_name == "My Test Suite"
        assert reporter.suite_start_time is not None
        assert isinstance(reporter.suite_start_time, datetime)
    
    def test_end_suite(self, reporter):
        """Test ending a test suite."""
        reporter.start_suite()
        reporter.end_suite()
        
        assert reporter.suite_end_time is not None
        assert isinstance(reporter.suite_end_time, datetime)
        assert reporter.suite_end_time >= reporter.suite_start_time
    
    def test_add_test_result(self, reporter, sample_test_result):
        """Test adding a test result."""
        reporter.add_test_result(sample_test_result)
        
        assert len(reporter.test_results) == 1
        assert reporter.test_results[0] == sample_test_result
    
    def test_add_multiple_test_results(self, reporter, sample_test_result, failed_test_result):
        """Test adding multiple test results."""
        reporter.add_test_result(sample_test_result)
        reporter.add_test_result(failed_test_result)
        
        assert len(reporter.test_results) == 2
    
    def test_get_statistics_empty(self, reporter):
        """Test getting statistics with no results."""
        stats = reporter.get_statistics()
        
        assert stats.total_tests == 0
        assert stats.passed == 0
        assert stats.failed == 0
        assert stats.pass_rate == 0.0
    
    def test_get_statistics_with_results(self, reporter, sample_test_result, failed_test_result):
        """Test getting statistics with test results."""
        reporter.add_test_result(sample_test_result)
        reporter.add_test_result(failed_test_result)
        
        # Add a skipped test
        skipped_result = TestResult(
            test_id="test_003",
            test_name="Skipped Test",
            status=TestStatus.SKIPPED,
            duration=0.0,
            start_time=datetime.now(),
            end_time=datetime.now()
        )
        reporter.add_test_result(skipped_result)
        
        stats = reporter.get_statistics()
        
        assert stats.total_tests == 3
        assert stats.passed == 1
        assert stats.failed == 1
        assert stats.skipped == 1
        assert stats.total_duration == 3.7  # 2.5 + 1.2 + 0.0
        assert stats.pass_rate == pytest.approx(33.33, rel=0.1)
    
    def test_format_duration_milliseconds(self, reporter):
        """Test duration formatting for milliseconds."""
        formatted = reporter._format_duration(0.123)
        assert "ms" in formatted
        assert "123" in formatted
    
    def test_format_duration_seconds(self, reporter):
        """Test duration formatting for seconds."""
        formatted = reporter._format_duration(5.67)
        assert "s" in formatted
        assert "5.67" in formatted
    
    def test_format_duration_minutes(self, reporter):
        """Test duration formatting for minutes."""
        formatted = reporter._format_duration(125.5)
        assert "m" in formatted
        assert "2m" in formatted
    
    def test_escape_html(self, reporter):
        """Test HTML escaping."""
        text = '<script>alert("XSS")</script>'
        escaped = reporter._escape_html(text)
        
        assert "<script>" not in escaped
        assert "&lt;script&gt;" in escaped
        assert "&quot;" in escaped
    
    def test_escape_html_none(self, reporter):
        """Test HTML escaping with None value."""
        escaped = reporter._escape_html(None)
        assert escaped == ""
    
    def test_generate_html_report(self, reporter, sample_test_result):
        """Test HTML report generation."""
        reporter.start_suite("Test Suite")
        reporter.add_test_result(sample_test_result)
        reporter.end_suite()
        
        report_path = reporter.generate_html_report()
        
        assert os.path.exists(report_path)
        assert report_path.endswith(".html")
        
        # Read and verify content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "RAPTOR Test Report" in content
        assert "Test Suite" in content
        assert "Test Login Functionality" in content
        assert "test_001" in content
    
    def test_generate_html_report_with_custom_filename(self, reporter, sample_test_result):
        """Test HTML report generation with custom filename."""
        reporter.add_test_result(sample_test_result)
        
        report_path = reporter.generate_html_report(output_file="custom_report.html")
        
        assert os.path.exists(report_path)
        assert "custom_report.html" in report_path
    
    def test_generate_html_report_with_failed_test(self, reporter, failed_test_result):
        """Test HTML report with failed test."""
        reporter.start_suite()
        reporter.add_test_result(failed_test_result)
        reporter.end_suite()
        
        report_path = reporter.generate_html_report()
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "AssertionError" in content
        assert "Traceback" in content
        assert "failed" in content.lower()
    
    def test_export_json(self, reporter, sample_test_result, failed_test_result):
        """Test JSON export functionality."""
        import json
        
        reporter.start_suite("JSON Test Suite")
        reporter.add_test_result(sample_test_result)
        reporter.add_test_result(failed_test_result)
        reporter.end_suite()
        
        json_path = reporter.export_json()
        
        assert os.path.exists(json_path)
        assert json_path.endswith(".json")
        
        # Read and verify JSON content
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["suite_name"] == "JSON Test Suite"
        assert "statistics" in data
        assert "test_results" in data
        assert len(data["test_results"]) == 2
        assert data["statistics"]["total_tests"] == 2
        assert data["statistics"]["passed"] == 1
        assert data["statistics"]["failed"] == 1
    
    def test_export_json_custom_filename(self, reporter, sample_test_result):
        """Test JSON export with custom filename."""
        reporter.add_test_result(sample_test_result)
        
        json_path = reporter.export_json(output_file="custom_results.json")
        
        assert os.path.exists(json_path)
        assert "custom_results.json" in json_path
    
    def test_get_status_icon(self, reporter):
        """Test status icon retrieval."""
        assert reporter._get_status_icon(TestStatus.PASSED) == "✓"
        assert reporter._get_status_icon(TestStatus.FAILED) == "✗"
        assert reporter._get_status_icon(TestStatus.SKIPPED) == "⊘"
        assert reporter._get_status_icon(TestStatus.ERROR) == "⚠"
    
    def test_html_report_contains_statistics(self, reporter, sample_test_result, failed_test_result):
        """Test that HTML report contains statistics section."""
        reporter.start_suite()
        reporter.add_test_result(sample_test_result)
        reporter.add_test_result(failed_test_result)
        reporter.end_suite()
        
        report_path = reporter.generate_html_report()
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "Test Summary" in content
        assert "Total Tests" in content
        assert "Passed" in content
        assert "Failed" in content
        assert "Pass Rate" in content
    
    def test_html_report_with_metadata(self, reporter, sample_test_result):
        """Test HTML report includes test metadata."""
        reporter.add_test_result(sample_test_result)
        
        report_path = reporter.generate_html_report()
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "browser" in content
        assert "chromium" in content
        assert "environment" in content
        assert "dev" in content
    
    def test_complete_workflow(self, reporter):
        """Test complete reporter workflow."""
        # Start suite
        reporter.start_suite("Complete Test Suite")
        
        # Add various test results
        for i in range(5):
            status = TestStatus.PASSED if i < 3 else TestStatus.FAILED
            start = datetime.now()
            end = start + timedelta(seconds=i + 1)
            
            result = TestResult(
                test_id=f"test_{i:03d}",
                test_name=f"Test Case {i + 1}",
                status=status,
                duration=(i + 1),
                start_time=start,
                end_time=end,
                error_message=f"Error in test {i}" if status == TestStatus.FAILED else None
            )
            reporter.add_test_result(result)
        
        # End suite
        reporter.end_suite()
        
        # Generate reports
        html_path = reporter.generate_html_report()
        json_path = reporter.export_json()
        
        # Verify both reports exist
        assert os.path.exists(html_path)
        assert os.path.exists(json_path)
        
        # Verify statistics
        stats = reporter.get_statistics()
        assert stats.total_tests == 5
        assert stats.passed == 3
        assert stats.failed == 2
        assert stats.pass_rate == 60.0


class TestScreenshotHandling:
    """Tests for screenshot handling in reports."""
    
    def test_test_result_with_screenshots(self):
        """Test creating test result with screenshots."""
        result = TestResult(
            test_id="test_screenshot",
            test_name="Test with Screenshots",
            status=TestStatus.FAILED,
            duration=1.0,
            start_time=datetime.now(),
            end_time=datetime.now(),
            screenshots=["screenshot1.png", "screenshot2.png"]
        )
        
        assert len(result.screenshots) == 2
        assert "screenshot1.png" in result.screenshots
    
    def test_html_report_with_screenshot_paths(self, reporter):
        """Test HTML report includes screenshot paths."""
        result = TestResult(
            test_id="test_001",
            test_name="Test with Screenshot",
            status=TestStatus.FAILED,
            duration=1.0,
            start_time=datetime.now(),
            end_time=datetime.now(),
            screenshots=["test_screenshot.png"]
        )
        
        reporter.add_test_result(result)
        report_path = reporter.generate_html_report(embed_screenshots=False)
        
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "test_screenshot.png" in content
        assert "Screenshots" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
