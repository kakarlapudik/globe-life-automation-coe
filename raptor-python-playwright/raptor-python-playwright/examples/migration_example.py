"""
Example usage of RAPTOR Migration Utilities

This example demonstrates how to use the migration utilities to:
1. Convert Java tests to Python
2. Validate DDFE element definitions
3. Check compatibility
4. Generate migration reports
"""

import asyncio
from pathlib import Path

from raptor.migration import (
    JavaToPythonConverter,
    DDFEValidator,
    CompatibilityChecker,
    MigrationReporter
)
from raptor.migration.ddfe_validator import ElementDefinition


# Example Java test code
SAMPLE_JAVA_CODE = """
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;

public class LoginTest {
    private WebDriver driver;
    
    public void testLogin() {
        driver.get("https://example.com/login");
        
        WebElement username = driver.findElement(By.id("username"));
        username.sendKeys("testuser");
        
        WebElement password = driver.findElement(By.id("password"));
        password.sendKeys("password123");
        
        WebElement loginButton = driver.findElement(By.cssSelector("button.login"));
        loginButton.click();
        
        waitForElement("css=.dashboard");
        verifyExists("css=.welcome-message");
    }
}
"""


async def example_java_to_python_conversion():
    """Example: Convert Java test to Python"""
    print("="*80)
    print("Java to Python Conversion Example")
    print("="*80)
    
    converter = JavaToPythonConverter()
    result = converter.convert_file(SAMPLE_JAVA_CODE)
    
    print("\nConverted Python Code:")
    print("-"*80)
    print(result.python_code)
    
    print("\n" + converter.get_conversion_summary())
    
    # Save converted code
    output_path = Path("output/converted_test.py")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result.python_code)
    print(f"\nConverted code saved to: {output_path}")


async def example_ddfe_validation():
    """Example: Validate DDFE element definitions"""
    print("\n" + "="*80)
    print("DDFE Element Validation Example")
    print("="*80)
    
    # Create sample element definitions
    elements = [
        ElementDefinition(
            pv_name="login_username",
            application_name="LoginApp",
            field_type="textbox",
            locator_primary="css=#username",
            locator_fallback1="xpath=//input[@id='username']",
            locator_fallback2="id=username"
        ),
        ElementDefinition(
            pv_name="login_password",
            application_name="LoginApp",
            field_type="textbox",
            locator_primary="css=#password",
            locator_fallback1="xpath=//input[@type='password']"
        ),
        ElementDefinition(
            pv_name="login_button",
            application_name="LoginApp",
            field_type="button",
            locator_primary="css=button.login",
            locator_fallback1="xpath=//button[contains(text(), 'Login')]"
        ),
        # Invalid element (missing required field)
        ElementDefinition(
            pv_name="invalid_element",
            application_name="LoginApp",
            field_type="",  # Missing field type
            locator_primary="css=.invalid"
        ),
    ]
    
    validator = DDFEValidator()
    results = validator.validate_elements(elements)
    
    print("\nValidation Results:")
    print("-"*80)
    
    for result in results:
        print(f"\nElement: {result.element.pv_name}")
        print(f"  Valid: {result.is_valid}")
        print(f"  Compatibility Score: {result.compatibility_score}")
        
        if result.issues:
            print(f"  Issues:")
            for issue in result.issues:
                print(f"    [{issue.severity.value.upper()}] {issue.field}: {issue.message}")
                if issue.suggestion:
                    print(f"      Suggestion: {issue.suggestion}")
    
    print("\n" + validator.get_validation_summary(results))


async def example_compatibility_check():
    """Example: Check Java test compatibility"""
    print("\n" + "="*80)
    print("Compatibility Check Example")
    print("="*80)
    
    checker = CompatibilityChecker()
    result = checker.check_compatibility(SAMPLE_JAVA_CODE)
    
    print(checker.get_compatibility_summary(result))
    
    print("\nMigration Checklist:")
    print("-"*80)
    checklist = checker.generate_migration_checklist(result)
    for item in checklist:
        print(item)


async def example_migration_report():
    """Example: Generate comprehensive migration report"""
    print("\n" + "="*80)
    print("Migration Report Generation Example")
    print("="*80)
    
    # Convert Java code
    converter = JavaToPythonConverter()
    conversion_result = converter.convert_file(SAMPLE_JAVA_CODE)
    
    # Validate elements
    elements = [
        ElementDefinition(
            pv_name="login_username",
            application_name="LoginApp",
            field_type="textbox",
            locator_primary="css=#username",
            locator_fallback1="xpath=//input[@id='username']"
        ),
        ElementDefinition(
            pv_name="login_password",
            application_name="LoginApp",
            field_type="textbox",
            locator_primary="css=#password"
        ),
    ]
    
    validator = DDFEValidator()
    validation_results = validator.validate_elements(elements)
    
    # Check compatibility
    checker = CompatibilityChecker()
    compatibility_result = checker.check_compatibility(SAMPLE_JAVA_CODE)
    
    # Generate report
    reporter = MigrationReporter(project_name="Login Test Migration")
    
    # Generate HTML report
    html_report = reporter.generate_report(
        conversion_results=[conversion_result],
        validation_results=validation_results,
        compatibility_results=[compatibility_result],
        output_format='html',
        output_path=Path('output/migration_report.html')
    )
    print("\nHTML report generated: output/migration_report.html")
    
    # Generate Markdown report
    md_report = reporter.generate_report(
        conversion_results=[conversion_result],
        validation_results=validation_results,
        compatibility_results=[compatibility_result],
        output_format='markdown',
        output_path=Path('output/migration_report.md')
    )
    print("Markdown report generated: output/migration_report.md")
    
    # Generate JSON report
    json_report = reporter.generate_report(
        conversion_results=[conversion_result],
        validation_results=validation_results,
        compatibility_results=[compatibility_result],
        output_format='json',
        output_path=Path('output/migration_report.json')
    )
    print("JSON report generated: output/migration_report.json")
    
    # Print text summary
    text_report = reporter.generate_report(
        conversion_results=[conversion_result],
        validation_results=validation_results,
        compatibility_results=[compatibility_result],
        output_format='text'
    )
    print("\n" + text_report)


async def main():
    """Run all examples"""
    print("\n" + "="*80)
    print("RAPTOR Migration Utilities - Examples")
    print("="*80)
    
    await example_java_to_python_conversion()
    await example_ddfe_validation()
    await example_compatibility_check()
    await example_migration_report()
    
    print("\n" + "="*80)
    print("All examples completed!")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
