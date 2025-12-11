"""
Example demonstrating the TestReporter usage.

This example shows how to:
- Create a test reporter
- Track test execution
- Add test results
- Generate HTML and JSON reports
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from raptor.utils.reporter import TestReporter, TestResult, TestStatus


async def simulate_test_execution():
    """Simulate a test suite execution with various test results."""
    
    # Initialize the reporter
    reporter = TestReporter(report_dir="reports")
    
    # Start the test suite
    reporter.start_suite("Example Test Suite - Login Module")
    print("Starting test suite execution...")
    
    # Test 1: Successful login test
    print("\n1. Running: Test Valid Login...")
    test1_start = datetime.now()
    await asyncio.sleep(0.5)  # Simulate test execution
    test1_end = datetime.now()
    
    result1 = TestResult(
        test_id="TC_001",
        test_name="Test Valid Login with Correct Credentials",
        status=TestStatus.PASSED,
        duration=(test1_end - test1_start).total_seconds(),
        start_time=test1_start,
        end_time=test1_end,
        metadata={
            "browser": "chromium",
            "environment": "staging",
            "test_type": "functional",
            "priority": "high"
        }
    )
    reporter.add_test_result(result1)
    print("   ✓ PASSED")
    
    # Test 2: Failed login test
    print("\n2. Running: Test Invalid Password...")
    test2_start = datetime.now()
    await asyncio.sleep(0.3)
    test2_end = datetime.now()
    
    result2 = TestResult(
        test_id="TC_002",
        test_name="Test Login with Invalid Password",
        status=TestStatus.FAILED,
        duration=(test2_end - test2_start).total_seconds(),
        start_time=test2_start,
        end_time=test2_end,
        error_message="AssertionError: Expected error message 'Invalid password' but got 'Login failed'",
        stack_trace="""Traceback (most recent call last):
  File "test_login.py", line 45, in test_invalid_password
    assert error_msg == "Invalid password"
AssertionError: Expected error message 'Invalid password' but got 'Login failed'""",
        screenshots=["screenshots/test_002_failure.png"],
        metadata={
            "browser": "chromium",
            "environment": "staging",
            "test_type": "negative",
            "priority": "high"
        }
    )
    reporter.add_test_result(result2)
    print("   ✗ FAILED")
    
    # Test 3: Successful logout test
    print("\n3. Running: Test Logout Functionality...")
    test3_start = datetime.now()
    await asyncio.sleep(0.4)
    test3_end = datetime.now()
    
    result3 = TestResult(
        test_id="TC_003",
        test_name="Test User Logout",
        status=TestStatus.PASSED,
        duration=(test3_end - test3_start).total_seconds(),
        start_time=test3_start,
        end_time=test3_end,
        metadata={
            "browser": "firefox",
            "environment": "staging",
            "test_type": "functional",
            "priority": "medium"
        }
    )
    reporter.add_test_result(result3)
    print("   ✓ PASSED")
    
    # Test 4: Skipped test
    print("\n4. Running: Test Password Reset...")
    test4_start = datetime.now()
    test4_end = test4_start
    
    result4 = TestResult(
        test_id="TC_004",
        test_name="Test Password Reset Email",
        status=TestStatus.SKIPPED,
        duration=0.0,
        start_time=test4_start,
        end_time=test4_end,
        error_message="Test skipped: Email service not available in staging environment",
        metadata={
            "browser": "chromium",
            "environment": "staging",
            "test_type": "functional",
            "priority": "low",
            "skip_reason": "Email service unavailable"
        }
    )
    reporter.add_test_result(result4)
    print("   ⊘ SKIPPED")
    
    # Test 5: Test with error
    print("\n5. Running: Test Session Timeout...")
    test5_start = datetime.now()
    await asyncio.sleep(0.2)
    test5_end = datetime.now()
    
    result5 = TestResult(
        test_id="TC_005",
        test_name="Test Session Timeout Handling",
        status=TestStatus.ERROR,
        duration=(test5_end - test5_start).total_seconds(),
        start_time=test5_start,
        end_time=test5_end,
        error_message="TimeoutError: Page load timeout after 30 seconds",
        stack_trace="""Traceback (most recent call last):
  File "test_session.py", line 78, in test_session_timeout
    page.wait_for_load_state("networkidle", timeout=30000)
  playwright._impl._api_types.TimeoutError: Timeout 30000ms exceeded.""",
        screenshots=["screenshots/test_005_timeout.png"],
        metadata={
            "browser": "webkit",
            "environment": "staging",
            "test_type": "functional",
            "priority": "medium"
        }
    )
    reporter.add_test_result(result5)
    print("   ⚠ ERROR")
    
    # Test 6: Another successful test
    print("\n6. Running: Test Remember Me Functionality...")
    test6_start = datetime.now()
    await asyncio.sleep(0.6)
    test6_end = datetime.now()
    
    result6 = TestResult(
        test_id="TC_006",
        test_name="Test Remember Me Checkbox",
        status=TestStatus.PASSED,
        duration=(test6_end - test6_start).total_seconds(),
        start_time=test6_start,
        end_time=test6_end,
        metadata={
            "browser": "chromium",
            "environment": "staging",
            "test_type": "functional",
            "priority": "low"
        }
    )
    reporter.add_test_result(result6)
    print("   ✓ PASSED")
    
    # End the test suite
    reporter.end_suite()
    print("\n" + "="*60)
    print("Test suite execution completed!")
    
    # Get and display statistics
    stats = reporter.get_statistics()
    print("\n" + "="*60)
    print("TEST EXECUTION SUMMARY")
    print("="*60)
    print(f"Total Tests:     {stats.total_tests}")
    print(f"Passed:          {stats.passed} ({stats.passed/stats.total_tests*100:.1f}%)")
    print(f"Failed:          {stats.failed}")
    print(f"Skipped:         {stats.skipped}")
    print(f"Errors:          {stats.errors}")
    print(f"Pass Rate:       {stats.pass_rate:.1f}%")
    print(f"Total Duration:  {stats.total_duration:.2f}s")
    print("="*60)
    
    # Generate HTML report
    print("\nGenerating HTML report...")
    html_path = reporter.generate_html_report()
    print(f"✓ HTML report generated: {html_path}")
    
    # Generate JSON report
    print("\nGenerating JSON report...")
    json_path = reporter.export_json()
    print(f"✓ JSON report generated: {json_path}")
    
    print("\n" + "="*60)
    print("Reports generated successfully!")
    print("="*60)
    
    return reporter


async def example_with_screenshots():
    """Example showing how to include screenshots in test results."""
    
    reporter = TestReporter(report_dir="reports")
    reporter.start_suite("Screenshot Example Suite")
    
    # Create a test result with multiple screenshots
    result = TestResult(
        test_id="TC_SCREENSHOT_001",
        test_name="Test with Multiple Screenshots",
        status=TestStatus.FAILED,
        duration=2.5,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(seconds=2.5),
        error_message="Element not found: #submit-button",
        stack_trace="ElementNotFoundException: Could not locate element #submit-button",
        screenshots=[
            "screenshots/before_click.png",
            "screenshots/after_error.png",
            "screenshots/page_state.png"
        ],
        metadata={
            "browser": "chromium",
            "viewport": "1920x1080",
            "test_data": "user_001"
        }
    )
    
    reporter.add_test_result(result)
    reporter.end_suite()
    
    # Generate report with embedded screenshots
    html_path = reporter.generate_html_report(embed_screenshots=True)
    print(f"Report with embedded screenshots: {html_path}")
    
    return reporter


async def example_custom_report_name():
    """Example showing custom report naming."""
    
    reporter = TestReporter(report_dir="reports/custom")
    reporter.start_suite("Custom Named Report Suite")
    
    # Add a simple test result
    result = TestResult(
        test_id="TC_CUSTOM_001",
        test_name="Custom Report Test",
        status=TestStatus.PASSED,
        duration=1.0,
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(seconds=1)
    )
    
    reporter.add_test_result(result)
    reporter.end_suite()
    
    # Generate report with custom name
    html_path = reporter.generate_html_report(output_file="my_custom_report.html")
    json_path = reporter.export_json(output_file="my_custom_results.json")
    
    print(f"Custom HTML report: {html_path}")
    print(f"Custom JSON report: {json_path}")
    
    return reporter


async def main():
    """Run all examples."""
    print("="*60)
    print("RAPTOR Test Reporter Examples")
    print("="*60)
    
    # Example 1: Basic test suite execution
    print("\n\nExample 1: Basic Test Suite Execution")
    print("-"*60)
    await simulate_test_execution()
    
    # Example 2: Test with screenshots
    print("\n\nExample 2: Test with Screenshots")
    print("-"*60)
    await example_with_screenshots()
    
    # Example 3: Custom report naming
    print("\n\nExample 3: Custom Report Naming")
    print("-"*60)
    await example_custom_report_name()
    
    print("\n\n" + "="*60)
    print("All examples completed successfully!")
    print("Check the 'reports' directory for generated reports.")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
