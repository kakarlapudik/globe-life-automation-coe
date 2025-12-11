"""
Quarto Reporter Example

This example demonstrates how to use the QuartoReporter to generate
rich, interactive test reports with visualizations.
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path

from raptor.utils.reporter import TestReporter, TestResult, TestStatus
from raptor.reporting.quarto_reporter import QuartoReporter, QuartoConfig


def create_sample_test_results():
    """Create sample test results for demonstration."""
    reporter = TestReporter(report_dir="reports")
    reporter.start_suite("E-Commerce Application Test Suite")
    
    start_time = datetime.now()
    
    # Successful tests
    reporter.add_test_result(TestResult(
        test_id="TC001",
        test_name="User Login with Valid Credentials",
        status=TestStatus.PASSED,
        duration=3.2,
        start_time=start_time,
        end_time=start_time + timedelta(seconds=3.2),
        metadata={
            "browser": "chromium",
            "environment": "staging",
            "priority": "high"
        }
    ))
    
    reporter.add_test_result(TestResult(
        test_id="TC002",
        test_name="Product Search Functionality",
        status=TestStatus.PASSED,
        duration=2.8,
        start_time=start_time + timedelta(seconds=4),
        end_time=start_time + timedelta(seconds=6.8),
        metadata={
            "browser": "firefox",
            "environment": "staging",
            "priority": "high"
        }
    ))
    
    reporter.add_test_result(TestResult(
        test_id="TC003",
        test_name="Add Item to Shopping Cart",
        status=TestStatus.PASSED,
        duration=4.1,
        start_time=start_time + timedelta(seconds=7),
        end_time=start_time + timedelta(seconds=11.1),
        metadata={
            "browser": "webkit",
            "environment": "staging",
            "priority": "critical"
        }
    ))
    
    # Failed test
    reporter.add_test_result(TestResult(
        test_id="TC004",
        test_name="Checkout Process with Payment",
        status=TestStatus.FAILED,
        duration=5.5,
        start_time=start_time + timedelta(seconds=12),
        end_time=start_time + timedelta(seconds=17.5),
        error_message="Payment gateway timeout: Connection refused after 30 seconds",
        stack_trace="""Traceback (most recent call last):
  File "tests/test_checkout.py", line 45, in test_checkout_payment
    payment_result = await page.click("#submit-payment")
  File "raptor/core/element_manager.py", line 123, in click
    raise TimeoutException("Element not clickable")
TimeoutException: Payment button not clickable after timeout""",
        screenshots=["screenshots/checkout_failure.png"],
        metadata={
            "browser": "chromium",
            "environment": "staging",
            "priority": "critical",
            "payment_method": "credit_card"
        }
    ))
    
    # Skipped test
    reporter.add_test_result(TestResult(
        test_id="TC005",
        test_name="Guest Checkout Flow",
        status=TestStatus.SKIPPED,
        duration=0.1,
        start_time=start_time + timedelta(seconds=18),
        end_time=start_time + timedelta(seconds=18.1),
        metadata={
            "reason": "Feature disabled in staging environment",
            "priority": "medium"
        }
    ))
    
    # More passed tests
    reporter.add_test_result(TestResult(
        test_id="TC006",
        test_name="User Profile Update",
        status=TestStatus.PASSED,
        duration=2.3,
        start_time=start_time + timedelta(seconds=19),
        end_time=start_time + timedelta(seconds=21.3),
        metadata={
            "browser": "chromium",
            "environment": "staging",
            "priority": "medium"
        }
    ))
    
    reporter.add_test_result(TestResult(
        test_id="TC007",
        test_name="Order History Display",
        status=TestStatus.PASSED,
        duration=1.9,
        start_time=start_time + timedelta(seconds=22),
        end_time=start_time + timedelta(seconds=23.9),
        metadata={
            "browser": "firefox",
            "environment": "staging",
            "priority": "low"
        }
    ))
    
    # Error test
    reporter.add_test_result(TestResult(
        test_id="TC008",
        test_name="Product Review Submission",
        status=TestStatus.ERROR,
        duration=1.2,
        start_time=start_time + timedelta(seconds=24),
        end_time=start_time + timedelta(seconds=25.2),
        error_message="Database connection error: Unable to connect to review service",
        stack_trace="""Traceback (most recent call last):
  File "tests/test_reviews.py", line 28, in test_submit_review
    await database.execute_query("INSERT INTO reviews...")
DatabaseException: Connection pool exhausted""",
        metadata={
            "browser": "webkit",
            "environment": "staging",
            "priority": "medium"
        }
    ))
    
    reporter.end_suite()
    return reporter


def example_basic_report():
    """Example 1: Generate a basic HTML report."""
    print("Example 1: Basic HTML Report")
    print("-" * 50)
    
    # Create test results
    test_reporter = create_sample_test_results()
    
    # Create Quarto reporter
    quarto_reporter = QuartoReporter(
        report_dir="reports/quarto",
        test_reporter=test_reporter
    )
    
    # Check if Quarto is installed
    if not quarto_reporter._check_quarto_installation():
        print("⚠️  Quarto is not installed!")
        print("   Please install from: https://quarto.org")
        print("   Skipping report generation...")
        return
    
    try:
        # Generate HTML report
        output_path = quarto_reporter.generate_report(
            output_name="basic_report",
            include_visualizations=True
        )
        print(f"✅ Report generated: {output_path}")
    except Exception as e:
        print(f"❌ Error generating report: {e}")


def example_custom_config():
    """Example 2: Generate report with custom configuration."""
    print("\nExample 2: Custom Configuration")
    print("-" * 50)
    
    test_reporter = create_sample_test_results()
    quarto_reporter = QuartoReporter(
        report_dir="reports/quarto",
        test_reporter=test_reporter
    )
    
    if not quarto_reporter._check_quarto_installation():
        print("⚠️  Quarto is not installed - skipping")
        return
    
    # Create custom configuration
    config = QuartoConfig(
        format="html",
        theme="darkly",  # Dark theme
        toc=True,
        toc_depth=4,
        code_fold=False,  # Show code by default
        fig_width=12,
        fig_height=7
    )
    
    try:
        output_path = quarto_reporter.generate_report(
            output_name="custom_config_report",
            config=config,
            include_visualizations=True
        )
        print(f"✅ Custom report generated: {output_path}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_parameterized_report():
    """Example 3: Generate parameterized report."""
    print("\nExample 3: Parameterized Report")
    print("-" * 50)
    
    test_reporter = create_sample_test_results()
    quarto_reporter = QuartoReporter(
        report_dir="reports/quarto",
        test_reporter=test_reporter
    )
    
    if not quarto_reporter._check_quarto_installation():
        print("⚠️  Quarto is not installed - skipping")
        return
    
    # Define parameters
    parameters = {
        "environment": "staging",
        "version": "2.1.0",
        "build_number": 12345,
        "test_run_id": "TR-2024-001"
    }
    
    try:
        output_path = quarto_reporter.generate_report(
            output_name="parameterized_report",
            parameters=parameters,
            include_visualizations=True
        )
        print(f"✅ Parameterized report generated: {output_path}")
        print(f"   Parameters: {parameters}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_multiple_formats():
    """Example 4: Export to multiple formats."""
    print("\nExample 4: Multiple Format Export")
    print("-" * 50)
    
    test_reporter = create_sample_test_results()
    quarto_reporter = QuartoReporter(
        report_dir="reports/quarto",
        test_reporter=test_reporter
    )
    
    if not quarto_reporter._check_quarto_installation():
        print("⚠️  Quarto is not installed - skipping")
        return
    
    try:
        # Export to HTML, PDF, and Word
        results = quarto_reporter.export_multiple_formats(
            output_name="multi_format_report",
            formats=["html", "pdf", "docx"],
            include_visualizations=True
        )
        
        print("✅ Reports generated in multiple formats:")
        for format_type, path in results.items():
            if not path.startswith("Error"):
                print(f"   {format_type.upper()}: {path}")
            else:
                print(f"   {format_type.upper()}: {path}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_custom_template():
    """Example 5: Use custom template."""
    print("\nExample 5: Custom Template")
    print("-" * 50)
    
    test_reporter = create_sample_test_results()
    quarto_reporter = QuartoReporter(
        report_dir="reports/quarto",
        test_reporter=test_reporter
    )
    
    # Create custom template
    custom_template = """---
title: "Custom Executive Report"
author: "QA Team"
date: today
format:
  html:
    theme: united
    toc: true
    toc-depth: 2
execute:
  echo: false
---

# Executive Summary

::: {.callout-important}
## Critical Metrics
This is a custom executive template focusing on high-level metrics.
:::

## Test Results

Custom visualization and analysis will be inserted here.

## Action Items

Based on test results, here are the recommended actions.
"""
    
    # Save custom template
    template_path = quarto_reporter.create_custom_template(
        "executive_custom",
        custom_template
    )
    print(f"✅ Custom template created: {template_path}")


def example_from_json():
    """Example 6: Generate report from JSON file."""
    print("\nExample 6: Generate from JSON")
    print("-" * 50)
    
    # First, create and export test results to JSON
    test_reporter = create_sample_test_results()
    json_path = test_reporter.export_json("sample_results.json")
    print(f"✅ Test results exported to: {json_path}")
    
    # Now generate Quarto report from JSON
    quarto_reporter = QuartoReporter(report_dir="reports/quarto")
    
    if not quarto_reporter._check_quarto_installation():
        print("⚠️  Quarto is not installed - skipping")
        return
    
    try:
        output_path = quarto_reporter.generate_from_json(
            json_file=json_path,
            output_name="json_based_report",
            include_visualizations=True
        )
        print(f"✅ Report generated from JSON: {output_path}")
    except Exception as e:
        print(f"❌ Error: {e}")


def example_integration_with_test_reporter():
    """Example 7: Seamless integration with TestReporter."""
    print("\nExample 7: Integration with TestReporter")
    print("-" * 50)
    
    # Create test reporter
    test_reporter = create_sample_test_results()
    
    # Generate traditional HTML report
    html_report = test_reporter.generate_html_report(
        output_file="traditional_report.html"
    )
    print(f"✅ Traditional HTML report: {html_report}")
    
    # Generate Quarto report from same data
    quarto_reporter = QuartoReporter(
        report_dir="reports/quarto",
        test_reporter=test_reporter
    )
    
    if not quarto_reporter._check_quarto_installation():
        print("⚠️  Quarto is not installed - skipping Quarto report")
        return
    
    try:
        quarto_report = quarto_reporter.generate_report(
            output_name="integrated_report",
            include_visualizations=True
        )
        print(f"✅ Quarto report: {quarto_report}")
        print("\n📊 Both reports generated from the same test data!")
    except Exception as e:
        print(f"❌ Error generating Quarto report: {e}")


def main():
    """Run all examples."""
    print("=" * 50)
    print("RAPTOR Quarto Reporter Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_report()
    example_custom_config()
    example_parameterized_report()
    example_multiple_formats()
    example_custom_template()
    example_from_json()
    example_integration_with_test_reporter()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("=" * 50)
    print("\n📝 Note: To generate actual reports, ensure Quarto is installed:")
    print("   https://quarto.org/docs/get-started/")
    print("\n📦 Install Python dependencies:")
    print("   pip install plotly kaleido matplotlib pandas")


if __name__ == "__main__":
    main()
