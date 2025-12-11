"""
Test Execution Control Examples

This module demonstrates the test execution control features:
- Test filtering by ID, iteration, and tag
- Test skip functionality with reason logging
- Retry mechanism for flaky tests
- Parallel execution support

Requirements: 12.1, 12.2, 12.3, 12.4
"""

import pytest
import asyncio
import os
from playwright.async_api import TimeoutError

from raptor.core.test_execution_control import (
    skip_test,
    skip_if,
    skip_unless,
    SkipReason,
    retry_on_failure,
)


# ============================================================================
# Example 1: Test Filtering by Tags
# ============================================================================

@pytest.mark.smoke
async def test_smoke_login(page):
    """
    Smoke test for login functionality.
    
    Run with: pytest --marker smoke
    """
    await page.goto("https://example.com/login")
    await page.fill("#username", "testuser")
    await page.fill("#password", "testpass")
    await page.click("#login-button")
    
    # Verify login success
    await page.wait_for_selector("#dashboard", timeout=5000)
    assert "dashboard" in page.url.lower()


@pytest.mark.regression
async def test_regression_password_reset(page):
    """
    Regression test for password reset.
    
    Run with: pytest --marker regression
    """
    await page.goto("https://example.com/login")
    await page.click("text=Forgot Password?")
    await page.fill("#email", "test@example.com")
    await page.click("#reset-button")
    
    # Verify reset email sent
    await page.wait_for_selector("text=Reset email sent")


@pytest.mark.smoke
@pytest.mark.regression
async def test_critical_feature(page):
    """
    Test marked with multiple tags.
    
    Run with: pytest --marker smoke
    Or: pytest --marker regression
    """
    await page.goto("https://example.com")
    assert await page.title() == "Example Domain"


# ============================================================================
# Example 2: Data-Driven Tests with Iteration Filtering
# ============================================================================

@pytest.mark.parametrize("iteration,username,expected_role", [
    (1, "admin", "Administrator"),
    (2, "user", "Standard User"),
    (3, "guest", "Guest"),
])
async def test_user_roles(page, iteration, username, expected_role):
    """
    Data-driven test with iteration parameter.
    
    Run specific iterations:
    pytest --iteration 1 --iteration 2
    """
    await page.goto("https://example.com/login")
    await page.fill("#username", username)
    await page.fill("#password", "password")
    await page.click("#login-button")
    
    # Verify role
    role_text = await page.text_content("#user-role")
    assert expected_role in role_text


# ============================================================================
# Example 3: Skip Functionality
# ============================================================================

def test_not_implemented_feature():
    """
    Test for feature not yet implemented.
    
    This test will be skipped with appropriate reason.
    """
    skip_test(
        "Advanced search feature not implemented in v1.0",
        SkipReason.NOT_IMPLEMENTED
    )
    
    # Test code would go here
    assert False, "Should not reach here"


def test_environment_specific(database):
    """
    Test that only runs when database is available.
    
    Skips with reason if database not configured.
    """
    skip_if(
        database is None,
        "Database not configured for this environment",
        SkipReason.CONFIGURATION
    )
    
    # Database test code
    result = database.execute_query("SELECT * FROM Users")
    assert len(result) > 0


def test_platform_specific():
    """
    Test that only runs on Windows.
    
    Skips on other platforms with reason.
    """
    import platform
    
    skip_unless(
        platform.system() == "Windows",
        "This feature is only supported on Windows",
        SkipReason.PLATFORM
    )
    
    # Windows-specific test code
    assert True


def test_requires_vpn():
    """
    Test that requires VPN connection.
    
    Skips if VPN not available.
    """
    vpn_available = os.getenv("VPN_CONNECTED") == "true"
    
    skip_unless(
        vpn_available,
        "VPN connection required for this test",
        SkipReason.DEPENDENCY
    )
    
    # VPN-dependent test code
    assert True


# ============================================================================
# Example 4: Retry Mechanism for Flaky Tests
# ============================================================================

@pytest.mark.flaky
@retry_on_failure(max_retries=3, retry_delay=1.0)
async def test_flaky_element_load(page):
    """
    Test with known flakiness - automatically retries.
    
    This test may fail occasionally due to timing issues,
    but will retry up to 3 times before failing.
    """
    await page.goto("https://example.com/dynamic")
    
    # Element may take time to load
    await page.wait_for_selector("#dynamic-content", timeout=3000)
    
    # Verify content loaded
    content = await page.text_content("#dynamic-content")
    assert len(content) > 0


@retry_on_failure(
    max_retries=5,
    retry_delay=2.0,
    exponential_backoff=True
)
async def test_network_operation(page):
    """
    Test with exponential backoff retry.
    
    Retries with increasing delays: 2s, 4s, 8s, 16s, 32s
    """
    await page.goto("https://example.com/api/data")
    
    # Network operation that may be slow
    response = await page.wait_for_response(
        lambda r: "api/data" in r.url,
        timeout=5000
    )
    
    assert response.ok


@retry_on_failure(
    max_retries=3,
    retry_delay=1.0,
    retry_on_exceptions=[TimeoutError, AssertionError]
)
async def test_with_exception_filter(page):
    """
    Test that only retries on specific exceptions.
    
    Retries on TimeoutError and AssertionError only.
    Other exceptions fail immediately.
    """
    await page.goto("https://example.com")
    
    # May timeout occasionally
    await page.wait_for_selector("#content", timeout=3000)
    
    # May fail assertion occasionally
    title = await page.title()
    assert "Example" in title


# ============================================================================
# Example 5: Combining Features
# ============================================================================

@pytest.mark.smoke
@pytest.mark.flaky
@retry_on_failure(max_retries=2, retry_delay=1.0)
async def test_smoke_with_retry(page):
    """
    Smoke test with automatic retry.
    
    Combines smoke tag with retry mechanism for critical but flaky test.
    
    Run with: pytest --marker smoke
    """
    await page.goto("https://example.com")
    
    # Critical check that may be flaky
    await page.wait_for_selector("#main-content", timeout=5000)
    
    # Verify page loaded
    assert await page.is_visible("#main-content")


@pytest.mark.regression
@pytest.mark.parametrize("iteration,feature", [
    (1, "search"),
    (2, "filter"),
    (3, "sort"),
])
async def test_regression_with_iteration(page, iteration, feature):
    """
    Regression test with iteration filtering.
    
    Run specific iterations:
    pytest --marker regression --iteration 1
    """
    await page.goto(f"https://example.com/{feature}")
    
    # Verify feature page loaded
    assert feature in page.url.lower()


# ============================================================================
# Example 6: Parallel Execution
# ============================================================================

@pytest.mark.parametrize("page_num", range(1, 11))
async def test_parallel_page_load(page, page_num):
    """
    Test designed for parallel execution.
    
    Run in parallel:
    pytest -n auto test_parallel_page_load
    
    Each worker will process different page numbers.
    """
    await page.goto(f"https://example.com/page/{page_num}")
    
    # Verify page loaded
    assert await page.is_visible("#content")


def test_worker_isolation(worker_id):
    """
    Test that verifies worker isolation in parallel execution.
    
    Each worker should have unique ID.
    
    Run with: pytest -n 4
    """
    # Each worker has unique ID
    assert worker_id is not None
    
    # Simulate worker-specific resource
    resource = f"resource_{worker_id}"
    assert worker_id in resource


# ============================================================================
# Example 7: Complex Filtering Scenarios
# ============================================================================

@pytest.mark.smoke
@pytest.mark.integration
async def test_smoke_integration(page):
    """
    Test with multiple markers.
    
    Run with: pytest --marker smoke --marker integration
    """
    await page.goto("https://example.com")
    assert True


def test_skip_in_ci():
    """
    Test that skips in CI environment.
    
    Useful for tests that require manual interaction.
    """
    is_ci = os.getenv("CI") == "true"
    
    skip_if(
        is_ci,
        "Test requires manual interaction",
        SkipReason.MANUAL
    )
    
    # Manual test code
    print("Please verify the UI manually")


@pytest.mark.slow
@retry_on_failure(max_retries=2, retry_delay=3.0)
async def test_slow_with_retry(page):
    """
    Slow test with retry mechanism.
    
    Run with: pytest --marker slow
    Exclude with: pytest --exclude-tag slow
    """
    await page.goto("https://example.com/slow-page")
    
    # Wait for slow operation
    await page.wait_for_timeout(5000)
    
    # Verify result
    assert await page.is_visible("#result")


# ============================================================================
# Example 8: Real-World Scenario
# ============================================================================

@pytest.mark.smoke
@retry_on_failure(
    max_retries=3,
    retry_delay=2.0,
    exponential_backoff=True,
    retry_on_exceptions=[TimeoutError]
)
async def test_complete_user_workflow(page):
    """
    Complete user workflow test with retry.
    
    This test demonstrates a real-world scenario:
    - Marked as smoke test for critical path
    - Retries on timeout errors (network issues)
    - Uses exponential backoff for reliability
    
    Run with: pytest --marker smoke -n auto
    """
    # Step 1: Navigate to login
    await page.goto("https://example.com/login")
    await page.wait_for_load_state("networkidle")
    
    # Step 2: Login
    await page.fill("#username", "testuser")
    await page.fill("#password", "testpass")
    await page.click("#login-button")
    
    # Step 3: Wait for dashboard
    await page.wait_for_selector("#dashboard", timeout=10000)
    
    # Step 4: Navigate to feature
    await page.click("text=My Profile")
    await page.wait_for_selector("#profile-form")
    
    # Step 5: Update profile
    await page.fill("#email", "newemail@example.com")
    await page.click("#save-button")
    
    # Step 6: Verify success
    await page.wait_for_selector("text=Profile updated successfully")
    
    # Step 7: Logout
    await page.click("#logout-button")
    await page.wait_for_selector("#login-form")


# ============================================================================
# Running Examples
# ============================================================================

"""
Command-line examples:

1. Run all smoke tests:
   pytest --marker smoke examples/test_execution_control_example.py

2. Run specific iterations:
   pytest --iteration 1 --iteration 2 examples/test_execution_control_example.py

3. Run in parallel:
   pytest -n auto examples/test_execution_control_example.py

4. Exclude flaky tests:
   pytest --exclude-tag flaky examples/test_execution_control_example.py

5. Run smoke tests in parallel:
   pytest --marker smoke -n auto examples/test_execution_control_example.py

6. Run with verbose output:
   pytest -v --marker smoke examples/test_execution_control_example.py

7. Combine filters:
   pytest --marker smoke --exclude-tag slow -n 4 examples/test_execution_control_example.py
"""
