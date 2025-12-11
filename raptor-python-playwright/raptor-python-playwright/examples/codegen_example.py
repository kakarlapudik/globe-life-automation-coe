"""
Code Generation Tools Example

Demonstrates how to use the code generation tools to:
1. Generate page objects from DDFE definitions
2. Generate test templates
3. Suggest optimal locators
4. Format generated code
"""

import asyncio
from pathlib import Path
from raptor.codegen.page_object_generator import (
    PageObjectGenerator,
    ElementDefinition
)
from raptor.codegen.test_template_generator import (
    TestTemplateGenerator,
    TestScenario,
    TestType
)
from raptor.codegen.locator_suggester import (
    LocatorSuggester,
    ElementInfo
)
from raptor.codegen.code_formatter import (
    CodeFormatter,
    FormatterConfig,
    FormatterType
)


def example_page_object_generation():
    """Example: Generate a page object from DDFE elements"""
    print("=" * 60)
    print("Example 1: Page Object Generation")
    print("=" * 60)
    
    # Define elements (typically loaded from DDFE database)
    elements = [
        ElementDefinition(
            pv_name="UsernameField",
            application_name="Login",
            field_type="textbox",
            locator_primary="css=#username",
            locator_fallback1="xpath=//input[@name='username']",
            locator_fallback2="role=textbox, name=Username"
        ),
        ElementDefinition(
            pv_name="PasswordField",
            application_name="Login",
            field_type="textbox",
            locator_primary="css=#password",
            locator_fallback1="xpath=//input[@type='password']"
        ),
        ElementDefinition(
            pv_name="LoginButton",
            application_name="Login",
            field_type="button",
            locator_primary="css=#login-btn",
            locator_fallback1="role=button, name=Login",
            locator_fallback2="text=Login"
        ),
        ElementDefinition(
            pv_name="RememberMeCheckbox",
            application_name="Login",
            field_type="checkbox",
            locator_primary="css=#remember-me"
        )
    ]
    
    # Generate page object
    generator = PageObjectGenerator()
    page_object = generator.generate_page_object(
        application_name="Login",
        elements=elements,
        base_url="https://example.com/login"
    )
    
    print(f"\nGenerated Page Object:")
    print(f"  Class Name: {page_object.class_name}")
    print(f"  File Name: {page_object.file_name}")
    print(f"  Methods: {len(page_object.methods)}")
    print(f"\nGenerated Code Preview (first 50 lines):")
    print("-" * 60)
    lines = page_object.code.split('\n')[:50]
    print('\n'.join(lines))
    print("...")
    
    return page_object


def example_test_template_generation():
    """Example: Generate test templates"""
    print("\n" + "=" * 60)
    print("Example 2: Test Template Generation")
    print("=" * 60)
    
    # Define test scenarios
    scenarios = [
        TestScenario(
            name="verify_successful_login",
            description="Verify user can login with valid credentials",
            test_type=TestType.FUNCTIONAL,
            page_object="LoginPage",
            steps=[
                "Navigate to login page",
                "Enter valid username",
                "Enter valid password",
                "Click login button",
                "Wait for dashboard to load"
            ],
            assertions=[
                "User is redirected to dashboard",
                "Welcome message is displayed",
                "Logout button is visible"
            ],
            tags=["login", "smoke", "critical"]
        ),
        TestScenario(
            name="verify_invalid_credentials",
            description="Verify error message for invalid credentials",
            test_type=TestType.FUNCTIONAL,
            page_object="LoginPage",
            steps=[
                "Navigate to login page",
                "Enter invalid username",
                "Enter invalid password",
                "Click login button"
            ],
            assertions=[
                "Error message is displayed",
                "User remains on login page"
            ],
            tags=["login", "negative"]
        )
    ]
    
    # Generate test file
    generator = TestTemplateGenerator()
    test_file = generator.generate_test_file(
        page_object_name="LoginPage",
        scenarios=scenarios,
        include_fixtures=True
    )
    
    print(f"\nGenerated Test File:")
    print(f"  File Name: {test_file.file_name}")
    print(f"  Test Count: {test_file.test_count}")
    print(f"\nGenerated Code Preview (first 60 lines):")
    print("-" * 60)
    lines = test_file.code.split('\n')[:60]
    print('\n'.join(lines))
    print("...")
    
    return test_file


def example_locator_suggestion():
    """Example: Suggest optimal locators for elements"""
    print("\n" + "=" * 60)
    print("Example 3: Locator Suggestion")
    print("=" * 60)
    
    # Define element information
    elements_to_analyze = [
        ElementInfo(
            tag_name="button",
            id="submit-btn",
            classes=["btn", "btn-primary"],
            text="Submit Form",
            role="button",
            aria_label="Submit the form"
        ),
        ElementInfo(
            tag_name="input",
            id="email-input",
            type="email",
            name="email",
            placeholder="Enter your email",
            test_id="email-field"
        ),
        ElementInfo(
            tag_name="a",
            classes=["nav-link"],
            text="Dashboard",
            href="/dashboard"
        )
    ]
    
    suggester = LocatorSuggester()
    
    for i, element_info in enumerate(elements_to_analyze, 1):
        print(f"\n--- Element {i}: {element_info.tag_name} ---")
        
        # Get suggestions
        suggestions = suggester.suggest_locators(element_info, max_suggestions=3)
        
        # Display suggestions
        for j, suggestion in enumerate(suggestions, 1):
            priority_emoji = {
                "EXCELLENT": "🟢",
                "GOOD": "🟡",
                "ACCEPTABLE": "🟠",
                "POOR": "🔴"
            }
            
            print(f"\n  {j}. {priority_emoji[suggestion.priority.name]} {suggestion.strategy.value.upper()}")
            print(f"     Priority: {suggestion.priority.name}")
            print(f"     Confidence: {suggestion.confidence:.0%}")
            print(f"     Locator: {suggestion.locator}")
            print(f"     Playwright: {suggestion.playwright_syntax}")
            print(f"     Reason: {suggestion.reason}")


def example_code_formatting():
    """Example: Format generated code"""
    print("\n" + "=" * 60)
    print("Example 4: Code Formatting")
    print("=" * 60)
    
    # Unformatted code
    unformatted_code = """
import sys
import os
from pathlib import Path
import asyncio


class   MyPage:
    def __init__(  self,page  ):
        self.page=page
    
    async def   click_button(self):
        await self.page.locator(  "#button"  ).click(  )
"""
    
    print("\nOriginal Code:")
    print("-" * 60)
    print(unformatted_code)
    
    # Format with Black
    formatter = CodeFormatter(
        FormatterConfig(
            formatter_type=FormatterType.BLACK,
            line_length=88
        )
    )
    
    result = formatter.format_code(unformatted_code, sort_imports=True)
    
    print("\nFormatted Code:")
    print("-" * 60)
    if result.success:
        print(result.formatted_code)
        print(f"\nFormatter Used: {result.formatter_used.value if result.formatter_used else 'None'}")
        print(f"Changes Made: {result.changes_made}")
    else:
        print(f"Formatting failed: {result.error_message}")
        print("Original code returned")


def example_complete_workflow():
    """Example: Complete workflow from element to formatted test"""
    print("\n" + "=" * 60)
    print("Example 5: Complete Workflow")
    print("=" * 60)
    
    # Step 1: Suggest optimal locators
    print("\nStep 1: Analyzing element and suggesting locators...")
    
    element_info = ElementInfo(
        tag_name="button",
        id="login-submit",
        role="button",
        text="Sign In",
        test_id="login-button"
    )
    
    suggester = LocatorSuggester()
    suggestions = suggester.suggest_locators(element_info, max_suggestions=1)
    best_locator = suggestions[0].locator
    
    print(f"  Best locator: {best_locator}")
    print(f"  Strategy: {suggestions[0].strategy.value}")
    print(f"  Priority: {suggestions[0].priority.name}")
    
    # Step 2: Generate page object with suggested locator
    print("\nStep 2: Generating page object...")
    
    element = ElementDefinition(
        pv_name="LoginButton",
        application_name="Login",
        field_type="button",
        locator_primary=best_locator
    )
    
    page_generator = PageObjectGenerator()
    page_object = page_generator.generate_page_object("Login", [element])
    
    print(f"  Generated: {page_object.class_name}")
    
    # Step 3: Generate test template
    print("\nStep 3: Generating test template...")
    
    scenario = TestScenario(
        name="verify_login_button_click",
        description="Verify login button can be clicked",
        test_type=TestType.SMOKE,
        page_object="LoginPage",
        steps=["Click login button"],
        assertions=["Button is clicked successfully"],
        tags=["smoke"]
    )
    
    test_generator = TestTemplateGenerator()
    test_file = test_generator.generate_test_file("LoginPage", [scenario])
    
    print(f"  Generated: {test_file.file_name}")
    
    # Step 4: Format all generated code
    print("\nStep 4: Formatting generated code...")
    
    formatter = CodeFormatter()
    
    page_result = formatter.format_code(page_object.code)
    test_result = formatter.format_code(test_file.code)
    
    print(f"  Page object formatted: {page_result.success}")
    print(f"  Test file formatted: {test_result.success}")
    
    print("\n✅ Complete workflow finished successfully!")
    print(f"\nGenerated files:")
    print(f"  - {page_object.file_name}")
    print(f"  - {test_file.file_name}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("RAPTOR Code Generation Tools Examples")
    print("=" * 60)
    
    # Run examples
    example_page_object_generation()
    example_test_template_generation()
    example_locator_suggestion()
    example_code_formatting()
    example_complete_workflow()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
