"""
Example: Using Soft Assertions in RAPTOR

This example demonstrates how to use soft assertions to perform multiple
verifications without stopping at the first failure. All failures are
collected and reported at the end.

Soft assertions are useful when you want to:
- Validate multiple elements in a single test
- Get a comprehensive view of all failures
- Continue testing even when some verifications fail
- Reduce test execution time by not stopping early
"""

import asyncio
from playwright.async_api import async_playwright
from raptor.core.element_manager import ElementManager
from raptor.core.soft_assertion_collector import SoftAssertionCollector


async def example_soft_assertions_basic():
    """
    Basic example of soft assertions.
    
    This example shows how to perform multiple verifications and collect
    all failures for reporting at the end.
    """
    print("\n" + "=" * 80)
    print("Example 1: Basic Soft Assertions")
    print("=" * 80 + "\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to a test page
        await page.goto("https://example.com")
        
        # Create element manager and soft assertion collector
        element_manager = ElementManager(page)
        collector = SoftAssertionCollector()
        
        print("Performing multiple soft verifications...")
        
        # Perform multiple verifications - none will stop execution
        await element_manager.soft_verify_exists(
            "css=h1",
            collector,
            message="Page should have a heading"
        )
        
        await element_manager.soft_verify_text(
            "css=h1",
            "Example Domain",
            collector,
            message="Heading should say 'Example Domain'"
        )
        
        await element_manager.soft_verify_visible(
            "css=p",
            collector,
            message="Paragraph should be visible"
        )
        
        # This will fail but won't stop execution
        await element_manager.soft_verify_exists(
            "css=#nonexistent-element",
            collector,
            message="This element doesn't exist - failure will be collected"
        )
        
        # More verifications continue
        await element_manager.soft_verify_not_exists(
            "css=#error-message",
            collector,
            message="Error message should not be present"
        )
        
        print(f"\nVerifications completed: {collector.get_verification_count()}")
        print(f"Failures detected: {collector.get_failure_count()}")
        
        # Check if there were any failures
        if collector.has_failures():
            print("\n⚠️  Some verifications failed. Details:")
            for idx, failure in enumerate(collector.get_failures(), 1):
                print(f"\n  Failure {idx}:")
                print(f"    Type: {failure.verification_type}")
                print(f"    Locator: {failure.locator}")
                print(f"    Message: {failure.message}")
        
        # Assert all at the end - this will raise if there were failures
        try:
            collector.assert_all()
            print("\n✅ All soft assertions passed!")
        except AssertionError as e:
            print("\n❌ Soft assertion failures detected:")
            print(str(e))
        
        await browser.close()


async def example_soft_assertions_form_validation():
    """
    Example: Validating a form with soft assertions.
    
    This demonstrates a realistic use case where you want to validate
    multiple form fields and see all validation errors at once.
    """
    print("\n" + "=" * 80)
    print("Example 2: Form Validation with Soft Assertions")
    print("=" * 80 + "\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Create a simple form page for testing
        await page.set_content("""
        <!DOCTYPE html>
        <html>
        <head><title>Form Validation Test</title></head>
        <body>
            <h1>Registration Form</h1>
            <form id="registration-form">
                <input id="username" type="text" placeholder="Username" />
                <input id="email" type="email" placeholder="Email" disabled />
                <input id="password" type="password" placeholder="Password" />
                <button id="submit" type="submit">Submit</button>
                <button id="cancel" type="button" disabled>Cancel</button>
            </form>
            <div id="success-message" style="display:none;">Success!</div>
        </body>
        </html>
        """)
        
        element_manager = ElementManager(page)
        collector = SoftAssertionCollector()
        
        print("Validating form elements...")
        
        # Validate form structure
        await element_manager.soft_verify_exists(
            "css=#registration-form",
            collector,
            message="Registration form should exist"
        )
        
        await element_manager.soft_verify_visible(
            "css=h1",
            collector,
            message="Form heading should be visible"
        )
        
        # Validate input fields
        await element_manager.soft_verify_exists(
            "css=#username",
            collector,
            message="Username field should exist"
        )
        
        await element_manager.soft_verify_enabled(
            "css=#username",
            collector,
            message="Username field should be enabled"
        )
        
        await element_manager.soft_verify_exists(
            "css=#email",
            collector,
            message="Email field should exist"
        )
        
        await element_manager.soft_verify_disabled(
            "css=#email",
            collector,
            message="Email field should be disabled"
        )
        
        # Validate buttons
        await element_manager.soft_verify_enabled(
            "css=#submit",
            collector,
            message="Submit button should be enabled"
        )
        
        await element_manager.soft_verify_disabled(
            "css=#cancel",
            collector,
            message="Cancel button should be disabled"
        )
        
        # Validate success message is hidden
        await element_manager.soft_verify_not_exists(
            "css=#success-message:visible",
            collector,
            timeout=2000,
            message="Success message should not be visible initially"
        )
        
        # Validate text content
        await element_manager.soft_verify_text(
            "css=h1",
            "Registration Form",
            collector,
            message="Heading should say 'Registration Form'"
        )
        
        print(f"\nForm validation completed:")
        print(f"  Total checks: {collector.get_verification_count()}")
        print(f"  Passed: {collector.get_verification_count() - collector.get_failure_count()}")
        print(f"  Failed: {collector.get_failure_count()}")
        
        # Get summary
        summary = collector.get_summary()
        print(f"\nValidation Summary:")
        print(f"  Pass rate: {(summary['passed'] / summary['total_verifications'] * 100):.1f}%")
        
        # Assert all at the end
        try:
            collector.assert_all()
            print("\n✅ All form validations passed!")
        except AssertionError as e:
            print("\n❌ Form validation failures detected")
            # In a real test, this would fail the test
        
        await browser.close()


async def example_soft_assertions_with_cleanup():
    """
    Example: Using soft assertions with collector cleanup.
    
    This shows how to reuse a collector across multiple test scenarios
    by clearing it between runs.
    """
    print("\n" + "=" * 80)
    print("Example 3: Reusing Collector with Cleanup")
    print("=" * 80 + "\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        element_manager = ElementManager(page)
        collector = SoftAssertionCollector()
        
        # Scenario 1: Test homepage
        print("Scenario 1: Testing homepage...")
        await page.goto("https://example.com")
        
        await element_manager.soft_verify_exists("css=h1", collector)
        await element_manager.soft_verify_visible("css=p", collector)
        
        print(f"  Verifications: {collector.get_verification_count()}")
        print(f"  Failures: {collector.get_failure_count()}")
        
        try:
            collector.assert_all()
            print("  ✅ Scenario 1 passed")
        except AssertionError:
            print("  ❌ Scenario 1 failed")
        
        # Clear collector for next scenario
        collector.clear()
        print("\n  Collector cleared for next scenario")
        
        # Scenario 2: Test another page
        print("\nScenario 2: Testing another page...")
        await page.set_content("<html><body><h1>Test</h1></body></html>")
        
        await element_manager.soft_verify_exists("css=h1", collector)
        await element_manager.soft_verify_text("css=h1", "Test", collector)
        
        print(f"  Verifications: {collector.get_verification_count()}")
        print(f"  Failures: {collector.get_failure_count()}")
        
        try:
            collector.assert_all()
            print("  ✅ Scenario 2 passed")
        except AssertionError:
            print("  ❌ Scenario 2 failed")
        
        await browser.close()


async def example_soft_assertions_custom_messages():
    """
    Example: Using custom error messages with soft assertions.
    
    This demonstrates how to provide meaningful context for failures
    using custom messages.
    """
    print("\n" + "=" * 80)
    print("Example 4: Custom Error Messages")
    print("=" * 80 + "\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.set_content("""
        <!DOCTYPE html>
        <html>
        <body>
            <div id="user-profile">
                <h2>John Doe</h2>
                <p class="email">john@example.com</p>
                <button id="edit-profile">Edit Profile</button>
            </div>
        </body>
        </html>
        """)
        
        element_manager = ElementManager(page)
        collector = SoftAssertionCollector()
        
        print("Validating user profile with custom messages...")
        
        # Use descriptive custom messages
        await element_manager.soft_verify_exists(
            "css=#user-profile",
            collector,
            message="User profile container must be present on the page"
        )
        
        await element_manager.soft_verify_text(
            "css=h2",
            "John Doe",
            collector,
            message="User's full name should be displayed in the heading"
        )
        
        await element_manager.soft_verify_text(
            "css=.email",
            "john@example.com",
            collector,
            message="User's email address should be correctly displayed"
        )
        
        await element_manager.soft_verify_enabled(
            "css=#edit-profile",
            collector,
            message="Edit Profile button should be enabled for user interaction"
        )
        
        # This will fail with a custom message
        await element_manager.soft_verify_exists(
            "css=#delete-account",
            collector,
            message="Delete Account button should be available in user profile (EXPECTED TO FAIL)"
        )
        
        print(f"\nValidation completed: {collector.get_verification_count()} checks")
        
        if collector.has_failures():
            print(f"\n⚠️  {collector.get_failure_count()} validation(s) failed:")
            for failure in collector.get_failures():
                print(f"\n  • {failure.message}")
                print(f"    Locator: {failure.locator}")
                print(f"    Expected: {failure.expected}")
                print(f"    Actual: {failure.actual}")
        
        await browser.close()


async def main():
    """Run all soft assertion examples."""
    print("\n" + "=" * 80)
    print("RAPTOR Soft Assertion Examples")
    print("=" * 80)
    
    await example_soft_assertions_basic()
    await example_soft_assertions_form_validation()
    await example_soft_assertions_with_cleanup()
    await example_soft_assertions_custom_messages()
    
    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
