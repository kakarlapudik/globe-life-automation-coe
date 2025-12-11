## RAPTOR Migration Utilities Guide

Comprehensive guide for migrating Java Selenium tests to Python Playwright using RAPTOR migration utilities.

### Overview

The RAPTOR migration utilities provide automated tools to help convert Java Selenium tests to Python Playwright tests. The utilities include:

1. **Java to Python Converter** - Converts Java test code to Python
2. **DDFE Validator** - Validates element definitions for Playwright compatibility
3. **Compatibility Checker** - Analyzes Java tests for compatibility issues
4. **Migration Reporter** - Generates comprehensive migration reports

### Installation

The migration utilities are included with the RAPTOR framework:

```python
from raptor.migration import (
    JavaToPythonConverter,
    DDFEValidator,
    CompatibilityChecker,
    MigrationReporter
)
```

### Java to Python Converter

#### Basic Usage

```python
from raptor.migration import JavaToPythonConverter

# Initialize converter
converter = JavaToPythonConverter()

# Convert Java code
java_code = """
public class LoginTest {
    public void testLogin() {
        click("css=#loginButton");
        type("css=#username", "testuser");
        verifyExists("css=.dashboard");
    }
}
"""

result = converter.convert_file(java_code)

# Access converted code
print(result.python_code)

# Check warnings
for warning in result.warnings:
    print(f"Warning: {warning}")

# Check items needing manual review
for item in result.manual_review_needed:
    print(f"Manual Review: {item}")

# View conversion statistics
print(result.conversion_stats)
```

#### Method Mappings

The converter automatically maps Java methods to Python equivalents:

| Java Method | Python Method |
|-------------|---------------|
| `click()` | `await element_manager.click()` |
| `clickXY()` | `await element_manager.click_at_position()` |
| `type()` | `await element_manager.fill()` |
| `verifyExists()` | `await verification.verify_exists()` |
| `waitForElement()` | `await element_manager.wait_for_element()` |
| `databaseImport()` | `await database_manager.import_data()` |

#### Type Mappings

Java types are converted to Python types:

| Java Type | Python Type |
|-----------|-------------|
| `String` | `str` |
| `Integer` | `int` |
| `Boolean` | `bool` |
| `List<String>` | `List[str]` |
| `void` | `None` |

#### Conversion Summary

```python
summary = converter.get_conversion_summary()
print(summary)
```

Output:
```
Conversion Summary:
==================
Methods Converted: 15
Types Converted: 8
Imports Added: 7
Async Methods Created: 5

Warnings: 2
Manual Review Items: 3
```

### DDFE Validator

#### Basic Usage

```python
from raptor.migration import DDFEValidator
from raptor.migration.ddfe_validator import ElementDefinition

# Initialize validator
validator = DDFEValidator()

# Create element definition
element = ElementDefinition(
    pv_name="login_button",
    application_name="LoginApp",
    field_type="button",
    locator_primary="css=#loginBtn",
    locator_fallback1="xpath=//button[@id='loginBtn']",
    locator_fallback2="id=loginBtn"
)

# Validate element
result = validator.validate_element(element)

# Check if valid
if result.is_valid:
    print(f"Element is valid! Score: {result.compatibility_score}")
else:
    print("Element has issues:")
    for issue in result.issues:
        print(f"  [{issue.severity.value}] {issue.field}: {issue.message}")
        if issue.suggestion:
            print(f"    Suggestion: {issue.suggestion}")
```

#### Validating Multiple Elements

```python
elements = [
    ElementDefinition(...),
    ElementDefinition(...),
    ElementDefinition(...)
]

results = validator.validate_elements(elements)

# Get summary
summary = validator.get_validation_summary(results)
print(summary)
```

#### Validation Checks

The validator checks for:

- **Required Fields**: pv_name, application_name, field_type, locator_primary
- **Field Type**: Must be in valid field types list
- **Locator Syntax**: CSS, XPath, ID, text, role locators
- **Playwright Compatibility**: Selenium-specific patterns that won't work
- **Fallback Locators**: Proper configuration of fallback strategies
- **Table Elements**: table_column and table_key for table elements
- **Frame Context**: Valid frame locators

#### Locator Types

Supported locator types:
- `css=selector` - CSS selectors
- `xpath=//path` - XPath expressions
- `id=elementId` - ID locators
- `text=Button Text` - Text content
- `role=button` - ARIA roles
- `name=fieldName` - Name attribute
- `class=className` - Class name
- `tag=div` - Tag name

#### Compatibility Score

Elements receive a compatibility score from 0.0 to 1.0:

- **0.9-1.0**: Excellent - Ready for migration
- **0.7-0.89**: Good - Minor issues to address
- **0.5-0.69**: Fair - Several issues to fix
- **<0.5**: Poor - Significant work needed

### Compatibility Checker

#### Basic Usage

```python
from raptor.migration import CompatibilityChecker

# Initialize checker
checker = CompatibilityChecker()

# Check Java code
java_code = """
import org.openqa.selenium.WebDriver;

public class TestClass {
    public void testMethod() {
        WebDriver driver = new ChromeDriver();
        driver.get("https://example.com");
        click("css=#button");
    }
}
"""

result = checker.check_compatibility(java_code)

# Check compatibility
if result.is_compatible:
    print(f"Code is compatible! Level: {result.compatibility_level.value}")
else:
    print("Code has compatibility issues")

# View supported features
print(f"Supported features: {result.supported_features}")

# View unsupported features
print(f"Unsupported features: {result.unsupported_features}")

# View migration complexity
print(f"Migration complexity: {result.migration_complexity}")
print(f"Estimated effort: {result.estimated_effort_hours} hours")
```

#### Compatibility Summary

```python
summary = checker.get_compatibility_summary(result)
print(summary)
```

Output:
```
Compatibility Check Summary:
============================
Compatibility Level: Mostly Compatible
Is Compatible: Yes
Migration Complexity: Moderate
Estimated Effort: 4.5 hours

Supported Features (5):
  ✓ click
  ✓ type
  ✓ verify
  ✓ wait
  ✓ navigate

Issues (3):
  Major (2):
    - Pattern 'selenium_imports' needs modification
      Alternative: from playwright.async_api import Page, Browser
    - Pattern 'webdriver' needs modification
      Alternative: Use Playwright Page object
```

#### Migration Checklist

```python
checklist = checker.generate_migration_checklist(result)
for item in checklist:
    print(item)
```

Output:
```
Migration Checklist:
===================

1. [MAJOR] Pattern 'selenium_imports' needs modification
   → from playwright.async_api import Page, Browser
   Effort: low

2. [MAJOR] Pattern 'webdriver' needs modification
   → Use Playwright Page object
   Effort: medium

3. Update imports to use Playwright
4. Convert synchronous code to async/await
5. Update element locators if needed
6. Test converted code thoroughly
7. Update documentation
```

#### Compatibility Levels

- **FULLY_COMPATIBLE**: No issues, ready to convert
- **MOSTLY_COMPATIBLE**: Minor modifications needed
- **PARTIALLY_COMPATIBLE**: Significant modifications needed
- **INCOMPATIBLE**: Contains unsupported features

### Migration Reporter

#### Basic Usage

```python
from raptor.migration import MigrationReporter
from pathlib import Path

# Initialize reporter
reporter = MigrationReporter(project_name="Login Test Migration")

# Generate HTML report
html_report = reporter.generate_report(
    conversion_results=[conversion_result],
    validation_results=validation_results,
    compatibility_results=[compatibility_result],
    output_format='html',
    output_path=Path('reports/migration_report.html')
)

print("HTML report generated!")
```

#### Report Formats

The reporter supports multiple output formats:

1. **HTML** - Interactive, styled report with charts
2. **JSON** - Machine-readable format for automation
3. **Markdown** - Documentation-friendly format
4. **Text** - Console-friendly plain text

#### Generate Multiple Formats

```python
# HTML report
reporter.generate_report(
    conversion_results=conversions,
    validation_results=validations,
    compatibility_results=compatibility,
    output_format='html',
    output_path=Path('reports/report.html')
)

# JSON report
reporter.generate_report(
    conversion_results=conversions,
    validation_results=validations,
    compatibility_results=compatibility,
    output_format='json',
    output_path=Path('reports/report.json')
)

# Markdown report
reporter.generate_report(
    conversion_results=conversions,
    validation_results=validations,
    compatibility_results=compatibility,
    output_format='markdown',
    output_path=Path('reports/report.md')
)

# Text report (console)
text_report = reporter.generate_report(
    conversion_results=conversions,
    validation_results=validations,
    compatibility_results=compatibility,
    output_format='text'
)
print(text_report)
```

#### Report Contents

Reports include:

- **Summary Statistics**: Files converted, elements validated, compatibility checks
- **Conversion Results**: Methods converted, warnings, manual review items
- **Validation Results**: Valid/invalid elements, compatibility scores, issues
- **Compatibility Results**: Supported/unsupported features, migration complexity
- **Recommendations**: Actionable steps for successful migration

### Complete Migration Workflow

Here's a complete workflow for migrating a Java test:

```python
import asyncio
from pathlib import Path
from raptor.migration import (
    JavaToPythonConverter,
    DDFEValidator,
    CompatibilityChecker,
    MigrationReporter
)

async def migrate_test(java_file_path: Path, elements: list):
    """Complete migration workflow"""
    
    # Step 1: Read Java code
    java_code = java_file_path.read_text()
    
    # Step 2: Check compatibility
    print("Checking compatibility...")
    checker = CompatibilityChecker()
    compatibility_result = checker.check_compatibility(java_code)
    
    if not compatibility_result.is_compatible:
        print("WARNING: Code has compatibility issues!")
        print(checker.get_compatibility_summary(compatibility_result))
        
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Step 3: Validate DDFE elements
    print("Validating element definitions...")
    validator = DDFEValidator()
    validation_results = validator.validate_elements(elements)
    
    invalid_count = sum(1 for r in validation_results if not r.is_valid)
    if invalid_count > 0:
        print(f"WARNING: {invalid_count} invalid elements found!")
        print(validator.get_validation_summary(validation_results))
    
    # Step 4: Convert Java to Python
    print("Converting Java to Python...")
    converter = JavaToPythonConverter()
    conversion_result = converter.convert_file(java_code)
    
    # Save converted code
    output_path = Path(f"output/{java_file_path.stem}_converted.py")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(conversion_result.python_code)
    print(f"Converted code saved to: {output_path}")
    
    # Step 5: Generate migration report
    print("Generating migration report...")
    reporter = MigrationReporter(project_name=f"{java_file_path.stem} Migration")
    
    reporter.generate_report(
        conversion_results=[conversion_result],
        validation_results=validation_results,
        compatibility_results=[compatibility_result],
        output_format='html',
        output_path=Path(f'reports/{java_file_path.stem}_migration_report.html')
    )
    
    print("\nMigration complete!")
    print(f"  - Converted code: {output_path}")
    print(f"  - Report: reports/{java_file_path.stem}_migration_report.html")
    
    # Print summary
    print("\n" + converter.get_conversion_summary())
    print(checker.get_compatibility_summary(compatibility_result))

# Run migration
asyncio.run(migrate_test(
    java_file_path=Path("tests/LoginTest.java"),
    elements=[...]  # Your DDFE elements
))
```

### Best Practices

1. **Always Check Compatibility First**: Run compatibility check before conversion
2. **Validate Elements**: Ensure DDFE elements are Playwright-compatible
3. **Review Converted Code**: Always manually review converted code
4. **Test Thoroughly**: Run comprehensive tests after migration
5. **Update Documentation**: Document any manual changes made
6. **Use Reports**: Generate reports for tracking and auditing
7. **Iterate**: Migration is iterative - expect multiple passes

### Common Issues and Solutions

#### Issue: Selenium-specific CSS selectors

**Problem**: `:contains()` pseudo-selector not supported in Playwright

**Solution**: Use text locators instead
```python
# Instead of: css=button:contains('Login')
# Use: text=Login
```

#### Issue: WebDriver/WebElement references

**Problem**: Direct WebDriver/WebElement usage

**Solution**: Use Playwright Page and Locator objects
```python
# Instead of: WebDriver driver = new ChromeDriver()
# Use: page = await browser.new_page()
```

#### Issue: Explicit waits

**Problem**: WebDriverWait and ExpectedConditions

**Solution**: Use Playwright's auto-waiting
```python
# Instead of: WebDriverWait(driver, 10).until(...)
# Use: await page.wait_for_selector("css=.element")
```

#### Issue: Actions class

**Problem**: Actions class for complex interactions

**Solution**: Use Playwright's built-in methods
```python
# Instead of: Actions actions = new Actions(driver)
# Use: await page.hover("css=.element")
```

### Troubleshooting

#### Conversion produces incorrect code

- Check Java code syntax
- Verify method names match expected patterns
- Review conversion warnings
- Manually adjust converted code

#### Validation fails for valid elements

- Check locator syntax
- Ensure required fields are present
- Verify field type is in valid list
- Review validation suggestions

#### Compatibility check too strict

- Review compatibility issues
- Determine if issues are critical
- Consider manual workarounds
- Update compatibility patterns if needed

### Support

For issues or questions:
- Check documentation: `docs/`
- Review examples: `examples/migration_example.py`
- Run tests: `pytest tests/test_migration_utilities.py`
- Contact: RAPTOR support team

### Next Steps

After migration:
1. Run converted tests
2. Fix any runtime errors
3. Update test data if needed
4. Update CI/CD pipelines
5. Train team on Python/Playwright
6. Document migration process
7. Archive Java tests

---

**Note**: Migration utilities provide automated assistance but cannot handle all scenarios. Manual review and testing are essential for successful migration.
