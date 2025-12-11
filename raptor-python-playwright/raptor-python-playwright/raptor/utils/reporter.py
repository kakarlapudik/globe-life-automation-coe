"""
Test Reporter for RAPTOR Framework

This module provides comprehensive test reporting capabilities including:
- HTML report generation
- Screenshot embedding in reports
- Execution duration tracking
- Pass/fail statistics
- Test result aggregation
"""

import os
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum


class TestStatus(Enum):
    """Test execution status enumeration."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """
    Represents the result of a single test execution.
    
    Attributes:
        test_id: Unique identifier for the test
        test_name: Human-readable test name
        status: Test execution status
        duration: Execution duration in seconds
        start_time: Test start timestamp
        end_time: Test end timestamp
        error_message: Error message if test failed
        stack_trace: Stack trace if test failed
        screenshots: List of screenshot file paths
        metadata: Additional test metadata
    """
    test_id: str
    test_name: str
    status: TestStatus
    duration: float
    start_time: datetime
    end_time: datetime
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    screenshots: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test result to dictionary."""
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "status": self.status.value,
            "duration": self.duration,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "error_message": self.error_message,
            "stack_trace": self.stack_trace,
            "screenshots": self.screenshots,
            "metadata": self.metadata,
        }


@dataclass
class TestStatistics:
    """
    Aggregated test execution statistics.
    
    Attributes:
        total_tests: Total number of tests executed
        passed: Number of passed tests
        failed: Number of failed tests
        skipped: Number of skipped tests
        errors: Number of tests with errors
        total_duration: Total execution duration in seconds
        pass_rate: Percentage of passed tests
    """
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    total_duration: float = 0.0
    
    @property
    def pass_rate(self) -> float:
        """Calculate pass rate percentage."""
        if self.total_tests == 0:
            return 0.0
        return (self.passed / self.total_tests) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert statistics to dictionary."""
        return {
            "total_tests": self.total_tests,
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "errors": self.errors,
            "total_duration": self.total_duration,
            "pass_rate": self.pass_rate,
        }


class TestReporter:
    """
    Manages test reporting and HTML report generation.
    
    Provides functionality to collect test results, track execution metrics,
    and generate comprehensive HTML reports with embedded screenshots.
    """
    
    def __init__(self, report_dir: str = "reports"):
        """
        Initialize the TestReporter.
        
        Args:
            report_dir: Directory where reports will be saved
        """
        self.report_dir = Path(report_dir)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        self.test_results: List[TestResult] = []
        self.suite_start_time: Optional[datetime] = None
        self.suite_end_time: Optional[datetime] = None
        self.suite_name: str = "Test Suite"
        
    def start_suite(self, suite_name: str = "Test Suite") -> None:
        """
        Mark the start of a test suite execution.
        
        Args:
            suite_name: Name of the test suite
        """
        self.suite_name = suite_name
        self.suite_start_time = datetime.now()
        self.test_results = []
    
    def end_suite(self) -> None:
        """Mark the end of a test suite execution."""
        self.suite_end_time = datetime.now()
    
    def add_test_result(self, result: TestResult) -> None:
        """
        Add a test result to the reporter.
        
        Args:
            result: TestResult object to add
        """
        self.test_results.append(result)
    
    def get_statistics(self) -> TestStatistics:
        """
        Calculate test execution statistics.
        
        Returns:
            TestStatistics object with aggregated metrics
        """
        stats = TestStatistics()
        stats.total_tests = len(self.test_results)
        
        for result in self.test_results:
            if result.status == TestStatus.PASSED:
                stats.passed += 1
            elif result.status == TestStatus.FAILED:
                stats.failed += 1
            elif result.status == TestStatus.SKIPPED:
                stats.skipped += 1
            elif result.status == TestStatus.ERROR:
                stats.errors += 1
            
            stats.total_duration += result.duration
        
        return stats
    
    def generate_html_report(
        self,
        output_file: Optional[str] = None,
        embed_screenshots: bool = True
    ) -> str:
        """
        Generate an HTML report of test results.
        
        Args:
            output_file: Optional custom output filename
            embed_screenshots: Whether to embed screenshots as base64
            
        Returns:
            Path to the generated HTML report
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_report_{timestamp}.html"
        
        report_path = self.report_dir / output_file
        
        # Generate HTML content
        html_content = self._generate_html_content(embed_screenshots)
        
        # Write to file
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def _generate_html_content(self, embed_screenshots: bool) -> str:
        """
        Generate the HTML content for the report.
        
        Args:
            embed_screenshots: Whether to embed screenshots as base64
            
        Returns:
            Complete HTML content as string
        """
        stats = self.get_statistics()
        
        # Calculate suite duration
        if self.suite_start_time and self.suite_end_time:
            suite_duration = (self.suite_end_time - self.suite_start_time).total_seconds()
        else:
            suite_duration = stats.total_duration
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RAPTOR Test Report - {self.suite_name}</title>
    <style>
        {self._get_css_styles()}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>RAPTOR Test Report</h1>
            <h2>{self.suite_name}</h2>
            <p class="timestamp">Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </header>
        
        <section class="summary">
            <h3>Test Summary</h3>
            <div class="stats-grid">
                <div class="stat-card total">
                    <div class="stat-value">{stats.total_tests}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat-card passed">
                    <div class="stat-value">{stats.passed}</div>
                    <div class="stat-label">Passed</div>
                </div>
                <div class="stat-card failed">
                    <div class="stat-value">{stats.failed}</div>
                    <div class="stat-label">Failed</div>
                </div>
                <div class="stat-card skipped">
                    <div class="stat-value">{stats.skipped}</div>
                    <div class="stat-label">Skipped</div>
                </div>
                <div class="stat-card error">
                    <div class="stat-value">{stats.errors}</div>
                    <div class="stat-label">Errors</div>
                </div>
                <div class="stat-card duration">
                    <div class="stat-value">{self._format_duration(suite_duration)}</div>
                    <div class="stat-label">Duration</div>
                </div>
                <div class="stat-card pass-rate">
                    <div class="stat-value">{stats.pass_rate:.1f}%</div>
                    <div class="stat-label">Pass Rate</div>
                </div>
            </div>
        </section>
        
        <section class="test-results">
            <h3>Test Results</h3>
            {self._generate_test_results_html(embed_screenshots)}
        </section>
    </div>
    
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""
        
        return html
    
    def _generate_test_results_html(self, embed_screenshots: bool) -> str:
        """
        Generate HTML for individual test results.
        
        Args:
            embed_screenshots: Whether to embed screenshots as base64
            
        Returns:
            HTML string for test results
        """
        if not self.test_results:
            return '<p class="no-results">No test results available.</p>'
        
        html_parts = []
        
        for idx, result in enumerate(self.test_results, 1):
            status_class = result.status.value
            status_icon = self._get_status_icon(result.status)
            
            html_parts.append(f"""
            <div class="test-result {status_class}">
                <div class="test-header" onclick="toggleDetails('test-{idx}')">
                    <span class="status-icon">{status_icon}</span>
                    <span class="test-name">{result.test_name}</span>
                    <span class="test-duration">{self._format_duration(result.duration)}</span>
                    <span class="toggle-icon">▼</span>
                </div>
                <div id="test-{idx}" class="test-details" style="display: none;">
                    <div class="detail-section">
                        <strong>Test ID:</strong> {result.test_id}
                    </div>
                    <div class="detail-section">
                        <strong>Start Time:</strong> {result.start_time.strftime("%Y-%m-%d %H:%M:%S")}
                    </div>
                    <div class="detail-section">
                        <strong>End Time:</strong> {result.end_time.strftime("%Y-%m-%d %H:%M:%S")}
                    </div>
                    <div class="detail-section">
                        <strong>Duration:</strong> {self._format_duration(result.duration)}
                    </div>
            """)
            
            # Add error information if test failed
            if result.error_message:
                html_parts.append(f"""
                    <div class="detail-section error-section">
                        <strong>Error Message:</strong>
                        <pre class="error-message">{self._escape_html(result.error_message)}</pre>
                    </div>
                """)
            
            if result.stack_trace:
                html_parts.append(f"""
                    <div class="detail-section error-section">
                        <strong>Stack Trace:</strong>
                        <pre class="stack-trace">{self._escape_html(result.stack_trace)}</pre>
                    </div>
                """)
            
            # Add screenshots
            if result.screenshots:
                html_parts.append('<div class="detail-section"><strong>Screenshots:</strong></div>')
                html_parts.append('<div class="screenshots">')
                
                for screenshot_path in result.screenshots:
                    if embed_screenshots and os.path.exists(screenshot_path):
                        img_data = self._encode_image_base64(screenshot_path)
                        html_parts.append(f"""
                            <div class="screenshot">
                                <img src="data:image/png;base64,{img_data}" 
                                     alt="Screenshot" 
                                     onclick="openModal(this.src)">
                                <p class="screenshot-name">{os.path.basename(screenshot_path)}</p>
                            </div>
                        """)
                    else:
                        html_parts.append(f"""
                            <div class="screenshot">
                                <a href="{screenshot_path}" target="_blank">
                                    {os.path.basename(screenshot_path)}
                                </a>
                            </div>
                        """)
                
                html_parts.append('</div>')
            
            # Add metadata if present
            if result.metadata:
                html_parts.append('<div class="detail-section"><strong>Metadata:</strong></div>')
                html_parts.append('<div class="metadata">')
                for key, value in result.metadata.items():
                    html_parts.append(f'<div><strong>{key}:</strong> {value}</div>')
                html_parts.append('</div>')
            
            html_parts.append('</div></div>')
        
        # Add modal for full-size screenshots
        html_parts.append("""
            <div id="imageModal" class="modal" onclick="closeModal()">
                <span class="close">&times;</span>
                <img class="modal-content" id="modalImage">
            </div>
        """)
        
        return '\n'.join(html_parts)
    
    def _get_status_icon(self, status: TestStatus) -> str:
        """Get icon for test status."""
        icons = {
            TestStatus.PASSED: "✓",
            TestStatus.FAILED: "✗",
            TestStatus.SKIPPED: "⊘",
            TestStatus.ERROR: "⚠",
        }
        return icons.get(status, "?")
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration in human-readable format.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.2f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
    
    def _encode_image_base64(self, image_path: str) -> str:
        """
        Encode image file as base64 string.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded string
        """
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception:
            return ""
    
    def _escape_html(self, text: str) -> str:
        """
        Escape HTML special characters.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text
        """
        if text is None:
            return ""
        return (text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for the HTML report."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            color: #333;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        header h2 {
            font-size: 1.5em;
            font-weight: normal;
            opacity: 0.9;
        }
        
        .timestamp {
            margin-top: 10px;
            opacity: 0.8;
        }
        
        .summary {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .summary h3 {
            margin-bottom: 20px;
            color: #667eea;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }
        
        .stat-card {
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .stat-card.total { background: #e3f2fd; }
        .stat-card.passed { background: #e8f5e9; }
        .stat-card.failed { background: #ffebee; }
        .stat-card.skipped { background: #fff3e0; }
        .stat-card.error { background: #fce4ec; }
        .stat-card.duration { background: #f3e5f5; }
        .stat-card.pass-rate { background: #e0f2f1; }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #666;
        }
        
        .test-results {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        
        .test-results h3 {
            margin-bottom: 20px;
            color: #667eea;
        }
        
        .test-result {
            margin-bottom: 15px;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .test-result.passed { border-left: 4px solid #4caf50; }
        .test-result.failed { border-left: 4px solid #f44336; }
        .test-result.skipped { border-left: 4px solid #ff9800; }
        .test-result.error { border-left: 4px solid #e91e63; }
        
        .test-header {
            display: flex;
            align-items: center;
            padding: 15px;
            background: #fafafa;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .test-header:hover {
            background: #f0f0f0;
        }
        
        .status-icon {
            font-size: 1.5em;
            margin-right: 15px;
            width: 30px;
            text-align: center;
        }
        
        .test-result.passed .status-icon { color: #4caf50; }
        .test-result.failed .status-icon { color: #f44336; }
        .test-result.skipped .status-icon { color: #ff9800; }
        .test-result.error .status-icon { color: #e91e63; }
        
        .test-name {
            flex: 1;
            font-weight: 500;
        }
        
        .test-duration {
            margin-right: 15px;
            color: #666;
            font-size: 0.9em;
        }
        
        .toggle-icon {
            transition: transform 0.3s;
        }
        
        .test-header.expanded .toggle-icon {
            transform: rotate(180deg);
        }
        
        .test-details {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .detail-section {
            margin-bottom: 15px;
        }
        
        .detail-section strong {
            color: #667eea;
        }
        
        .error-section {
            background: #fff5f5;
            padding: 15px;
            border-radius: 5px;
            border-left: 3px solid #f44336;
        }
        
        .error-message, .stack-trace {
            background: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            margin-top: 10px;
        }
        
        .screenshots {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }
        
        .screenshot {
            text-align: center;
        }
        
        .screenshot img {
            max-width: 100%;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .screenshot img:hover {
            transform: scale(1.05);
        }
        
        .screenshot-name {
            margin-top: 5px;
            font-size: 0.8em;
            color: #666;
        }
        
        .metadata {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }
        
        .metadata div {
            margin-bottom: 5px;
        }
        
        .no-results {
            text-align: center;
            padding: 40px;
            color: #999;
        }
        
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            padding-top: 50px;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0, 0, 0, 0.9);
        }
        
        .modal-content {
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90%;
        }
        
        .close {
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            cursor: pointer;
        }
        
        .close:hover {
            color: #bbb;
        }
        """
    
    def _get_javascript(self) -> str:
        """Get JavaScript for interactive features."""
        return """
        function toggleDetails(id) {
            const details = document.getElementById(id);
            const header = details.previousElementSibling;
            
            if (details.style.display === 'none') {
                details.style.display = 'block';
                header.classList.add('expanded');
            } else {
                details.style.display = 'none';
                header.classList.remove('expanded');
            }
        }
        
        function openModal(src) {
            const modal = document.getElementById('imageModal');
            const modalImg = document.getElementById('modalImage');
            modal.style.display = 'block';
            modalImg.src = src;
        }
        
        function closeModal() {
            document.getElementById('imageModal').style.display = 'none';
        }
        
        // Close modal on Escape key
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                closeModal();
            }
        });
        """
    
    def export_json(self, output_file: Optional[str] = None) -> str:
        """
        Export test results as JSON.
        
        Args:
            output_file: Optional custom output filename
            
        Returns:
            Path to the generated JSON file
        """
        import json
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_results_{timestamp}.json"
        
        report_path = self.report_dir / output_file
        
        data = {
            "suite_name": self.suite_name,
            "start_time": self.suite_start_time.isoformat() if self.suite_start_time else None,
            "end_time": self.suite_end_time.isoformat() if self.suite_end_time else None,
            "statistics": self.get_statistics().to_dict(),
            "test_results": [result.to_dict() for result in self.test_results],
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return str(report_path)
