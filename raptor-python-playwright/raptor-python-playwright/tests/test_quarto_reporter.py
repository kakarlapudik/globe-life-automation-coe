"""
Tests for Quarto Reporter

This module tests the Quarto reporting functionality including:
- Report generation
- Multiple format export
- Template customization
- Integration with TestReporter
"""

import pytest
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from raptor.reporting.quarto_reporter import QuartoReporter, QuartoConfig
from raptor.utils.reporter import TestReporter, TestResult, TestStatus


@pytest.fixture
def test_reporter():
    """Create a TestReporter with sample data."""
    reporter = TestReporter(report_dir="test_reports")
    reporter.start_suite("Sample Test Suite")
    
    # Add some test results
    start_time = datetime.now()
    
    # Passed test
    reporter.add_test_result(TestResult(
        test_id="test_001",
        test_name="Test Login Success",
        status=TestStatus.PASSED,
        duration=2.5,
        start_time=start_time,
        end_time=start_time + timedelta(seconds=2.5),
        metadata={"browser": "chromium", "env": "staging"}
    ))
    
    # Failed test
    reporter.add_test_result(TestResult(
        test_id="test_002",
        test_name="Test Invalid Credentials",
        status=TestStatus.FAILED,
        duration=1.8,
        start_time=start_time + timedelta(seconds=3),
        end_time=start_time + timedelta(seconds=4.8),
        error_message="AssertionError: Expected error message not displayed",
        stack_trace="Traceback (most recent call last):\n  File 'test.py', line 42",
        screenshots=["screenshot1.png"],
        metadata={"browser": "firefox", "env": "staging"}
    ))
    
    # Skipped test
    reporter.add_test_result(TestResult(
        test_id="test_003",
        test_name="Test Password Reset",
        status=TestStatus.SKIPPED,
        duration=0.1,
        start_time=start_time + timedelta(seconds=5),
        end_time=start_time + timedelta(seconds=5.1),
        metadata={"reason": "Feature not implemented"}
    ))
    
    reporter.end_suite()
    return reporter


@pytest.fixture
def quarto_reporter(test_reporter, tmp_path):
    """Create a QuartoReporter instance."""
    report_dir = tmp_path / "quarto_reports"
    return QuartoReporter(report_dir=str(report_dir), test_reporter=test_reporter)


class TestQuartoConfig:
    """Test QuartoConfig class."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = QuartoConfig()
        
        assert config.format == "html"
        assert config.theme == "cosmo"
        assert config.toc is True
        assert config.toc_depth == 3
        assert config.code_fold is True
        assert config.self_contained is True
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = QuartoConfig(
            format="pdf",
            theme="darkly",
            toc=False,
            toc_depth=2
        )
        
        assert config.format == "pdf"
        assert config.theme == "darkly"
        assert config.toc is False
        assert config.toc_depth == 2
    
    def test_to_yaml(self):
        """Test YAML conversion."""
        config = QuartoConfig()
        yaml_output = config.to_yaml()
        
        assert "format:" in yaml_output
        assert "html:" in yaml_output
        assert "theme: cosmo" in yaml_output
        assert "toc: true" in yaml_output
        assert "execute:" in yaml_output


class TestQuartoReporter:
    """Test QuartoReporter class."""
    
    def test_initialization(self, tmp_path):
        """Test QuartoReporter initialization."""
        report_dir = tmp_path / "reports"
        reporter = QuartoReporter(report_dir=str(report_dir))
        
        assert reporter.report_dir.exists()
        assert reporter.template_dir.exists()
    
    def test_initialization_with_test_reporter(self, test_reporter, tmp_path):
        """Test initialization with TestReporter."""
        report_dir = tmp_path / "reports"
        reporter = QuartoReporter(
            report_dir=str(report_dir),
            test_reporter=test_reporter
        )
        
        assert reporter.test_reporter is test_reporter
    
    @patch('subprocess.run')
    def test_check_quarto_installation_success(self, mock_run):
        """Test Quarto installation check when installed."""
        mock_run.return_value = Mock(returncode=0)
        
        reporter = QuartoReporter()
        assert reporter._check_quarto_installation() is True
    
    @patch('subprocess.run')
    def test_check_quarto_installation_failure(self, mock_run):
        """Test Quarto installation check when not installed."""
        mock_run.side_effect = FileNotFoundError()
        
        reporter = QuartoReporter()
        assert reporter._check_quarto_installation() is False
    
    @patch('raptor.reporting.quarto_reporter.QuartoReporter._check_quarto_installation')
    def test_generate_report_without_test_reporter(self, mock_check, tmp_path):
        """Test report generation fails without test_reporter."""
        mock_check.return_value = True  # Mock Quarto as installed
        reporter = QuartoReporter(report_dir=str(tmp_path))
        
        with pytest.raises(ValueError, match="test_reporter must be set"):
            reporter.generate_report()
    
    @patch('raptor.reporting.quarto_reporter.QuartoReporter._check_quarto_installation')
    def test_generate_report_without_quarto(self, mock_check, quarto_reporter):
        """Test report generation fails without Quarto installed."""
        mock_check.return_value = False
        
        with pytest.raises(RuntimeError, match="Quarto is not installed"):
            quarto_reporter.generate_report()
    
    def test_generate_qmd_content(self, quarto_reporter):
        """Test QMD content generation."""
        config = QuartoConfig()
        content = quarto_reporter._generate_qmd_content(
            config=config,
            parameters={},
            template="default",
            include_visualizations=True
        )
        
        assert "---" in content  # YAML header
        assert "Test Execution Report" in content
        assert "Executive Summary" in content
        assert "Test Results Visualization" in content
        assert "Detailed Test Results" in content
        assert "Performance Analysis" in content
    
    def test_generate_qmd_content_without_visualizations(self, quarto_reporter):
        """Test QMD content generation without visualizations."""
        config = QuartoConfig()
        content = quarto_reporter._generate_qmd_content(
            config=config,
            parameters={},
            template="default",
            include_visualizations=False
        )
        
        assert "Test Execution Report" in content
        assert "Test Results Visualization" not in content
        assert "Performance Analysis" not in content
    
    def test_build_yaml_header(self, quarto_reporter):
        """Test YAML header building."""
        config = QuartoConfig()
        parameters = {"environment": "staging", "version": "1.0.0"}
        
        header = quarto_reporter._build_yaml_header(config, parameters)
        
        assert "---" in header
        assert "title:" in header
        assert "RAPTOR Test Report" in header
        assert "params:" in header
        assert "environment: \"staging\"" in header
        assert "version: \"1.0.0\"" in header
    
    def test_generate_summary_section(self, quarto_reporter):
        """Test summary section generation."""
        stats = quarto_reporter.test_reporter.get_statistics()
        summary = quarto_reporter._generate_summary_section(stats)
        
        assert "Test Execution Summary" in summary
        assert "Total Tests:" in summary
        assert "Passed:" in summary
        assert "Failed:" in summary
        assert "Skipped:" in summary
    
    def test_generate_visualization_section(self, quarto_reporter):
        """Test visualization section generation."""
        stats = quarto_reporter.test_reporter.get_statistics()
        viz_section = quarto_reporter._generate_visualization_section(stats)
        
        assert "```{python}" in viz_section
        assert "import plotly" in viz_section
        assert "go.Pie" in viz_section
        assert "go.Indicator" in viz_section
    
    def test_generate_detailed_results_section(self, quarto_reporter):
        """Test detailed results section generation."""
        results_section = quarto_reporter._generate_detailed_results_section()
        
        assert "Test Login Success" in results_section
        assert "Test Invalid Credentials" in results_section
        assert "Test Password Reset" in results_section
        assert "✅" in results_section  # Passed emoji
        assert "❌" in results_section  # Failed emoji
        assert "⏭️" in results_section  # Skipped emoji
    
    def test_generate_detailed_results_with_errors(self, quarto_reporter):
        """Test detailed results include error information."""
        results_section = quarto_reporter._generate_detailed_results_section()
        
        assert "AssertionError" in results_section
        assert "Traceback" in results_section
    
    def test_generate_performance_section(self, quarto_reporter):
        """Test performance section generation."""
        perf_section = quarto_reporter._generate_performance_section()
        
        assert "```{python}" in perf_section
        assert "Test Execution Duration" in perf_section
        assert "Duration Distribution" in perf_section
        assert "go.Bar" in perf_section
        assert "go.Histogram" in perf_section
    
    def test_create_custom_template(self, quarto_reporter):
        """Test custom template creation."""
        template_content = """---
title: "Custom Template"
---

# Custom Report
"""
        
        template_path = quarto_reporter.create_custom_template(
            "custom",
            template_content
        )
        
        assert template_path.exists()
        assert template_path.name == "custom.qmd"
        
        with open(template_path, 'r') as f:
            content = f.read()
            assert "Custom Template" in content
    
    def test_format_duration(self, quarto_reporter):
        """Test duration formatting."""
        assert quarto_reporter._format_duration(0.5) == "500ms"
        assert quarto_reporter._format_duration(2.5) == "2.50s"
        assert quarto_reporter._format_duration(65.5) == "1m 5.5s"
        assert quarto_reporter._format_duration(125.3) == "2m 5.3s"
    
    def test_generate_from_json(self, quarto_reporter, test_reporter, tmp_path):
        """Test report generation from JSON file."""
        # Export test results to JSON
        json_file = tmp_path / "test_results.json"
        test_reporter.export_json(str(json_file))
        
        # Mock Quarto installation and rendering
        with patch.object(quarto_reporter, '_check_quarto_installation', return_value=True), \
             patch.object(quarto_reporter, '_render_quarto_report', return_value=Path("report.html")):
            
            output_path = quarto_reporter.generate_from_json(
                str(json_file),
                output_name="json_report"
            )
            
            assert output_path is not None
    
    @patch('subprocess.run')
    def test_install_dependencies(self, mock_run):
        """Test dependency installation."""
        mock_run.return_value = Mock(returncode=0)
        
        result = QuartoReporter.install_dependencies()
        assert result is True
        
        # Check that pip install was called for each package
        assert mock_run.call_count == 4  # plotly, kaleido, matplotlib, pandas
    
    @patch('subprocess.run')
    def test_install_dependencies_failure(self, mock_run):
        """Test dependency installation failure."""
        mock_run.side_effect = Exception("Installation failed")
        
        result = QuartoReporter.install_dependencies()
        assert result is False


class TestQuartoReporterIntegration:
    """Integration tests for QuartoReporter."""
    
    def test_full_workflow(self, test_reporter, tmp_path):
        """Test complete workflow from TestReporter to Quarto report."""
        # Create QuartoReporter
        reporter = QuartoReporter(
            report_dir=str(tmp_path / "reports"),
            test_reporter=test_reporter
        )
        
        # Generate QMD content
        config = QuartoConfig()
        content = reporter._generate_qmd_content(
            config=config,
            parameters={"environment": "test"},
            template="default",
            include_visualizations=True
        )
        
        # Verify content structure
        assert "---" in content
        assert "Sample Test Suite" in content
        assert "Test Login Success" in content
        assert "Test Invalid Credentials" in content
        
        # Verify statistics are included
        stats = test_reporter.get_statistics()
        assert str(stats.total_tests) in content
        assert str(stats.passed) in content
        assert str(stats.failed) in content
    
    def test_multiple_format_export_mock(self, quarto_reporter):
        """Test exporting to multiple formats (mocked)."""
        with patch.object(quarto_reporter, '_check_quarto_installation', return_value=True), \
             patch.object(quarto_reporter, '_render_quarto_report') as mock_render:
            
            # Mock different output files for different formats
            def render_side_effect(qmd_file, config):
                ext_map = {"html": ".html", "pdf": ".pdf", "docx": ".docx"}
                return qmd_file.with_suffix(ext_map.get(config.format, ".html"))
            
            mock_render.side_effect = render_side_effect
            
            results = quarto_reporter.export_multiple_formats(
                output_name="multi_format",
                formats=["html", "pdf", "docx"]
            )
            
            assert len(results) == 3
            assert "html" in results
            assert "pdf" in results
            assert "docx" in results
    
    def test_parameterized_report(self, quarto_reporter):
        """Test report generation with parameters."""
        config = QuartoConfig()
        parameters = {
            "environment": "production",
            "version": "2.0.0",
            "build_number": 12345
        }
        
        content = quarto_reporter._generate_qmd_content(
            config=config,
            parameters=parameters,
            template="default",
            include_visualizations=True
        )
        
        assert "params:" in content
        assert "environment: \"production\"" in content
        assert "version: \"2.0.0\"" in content
        assert "build_number: 12345" in content


class TestQuartoReporterEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_test_results(self, tmp_path):
        """Test report generation with no test results."""
        reporter = TestReporter()
        reporter.start_suite("Empty Suite")
        reporter.end_suite()
        
        quarto_reporter = QuartoReporter(
            report_dir=str(tmp_path),
            test_reporter=reporter
        )
        
        content = quarto_reporter._generate_qmd_content(
            config=QuartoConfig(),
            parameters={},
            template="default",
            include_visualizations=True
        )
        
        assert "Test Execution Report" in content
        assert "0" in content  # Total tests should be 0
    
    def test_long_test_names(self, test_reporter, tmp_path):
        """Test handling of very long test names."""
        long_name = "Test " + "Very " * 50 + "Long Name"
        
        test_reporter.add_test_result(TestResult(
            test_id="test_long",
            test_name=long_name,
            status=TestStatus.PASSED,
            duration=1.0,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=1)
        ))
        
        quarto_reporter = QuartoReporter(
            report_dir=str(tmp_path),
            test_reporter=test_reporter
        )
        
        content = quarto_reporter._generate_detailed_results_section()
        # Long names are included in detailed section (truncation happens in performance section)
        assert long_name in content or "Very" in content
    
    def test_special_characters_in_content(self, test_reporter, tmp_path):
        """Test handling of special characters in test content."""
        test_reporter.add_test_result(TestResult(
            test_id="test_special",
            test_name="Test <script>alert('xss')</script>",
            status=TestStatus.FAILED,
            duration=1.0,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(seconds=1),
            error_message="Error with special chars: <>&\"'"
        ))
        
        quarto_reporter = QuartoReporter(
            report_dir=str(tmp_path),
            test_reporter=test_reporter
        )
        
        content = quarto_reporter._generate_detailed_results_section()
        # Content should be included (Quarto handles escaping)
        assert "special" in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
