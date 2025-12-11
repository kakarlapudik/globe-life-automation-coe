# Code Generation Quick Reference

Quick reference for RAPTOR code generation tools.

## Page Object Generator

### Generate Single Page Object

```python
from raptor.codegen import PageObjectGenerator, ElementDefinition

generator = PageObjectGenerator()
page_object = generator.generate_page_object(
    application_name="Login",
    elements=[
        ElementDefinition(
            pv_name="UsernameField",
            application_name="Login",
            field_type="textbox",
            locator_primary="css=#username"
        )
    ]
)

print(page_object.code)
```

### Generate Multiple Page Objects

```python
page_objects = generator.generate_multiple_page_objects(
    elements=all_elements,
    output_dir=Path("raptor/pages/generated")
)
```

## Test Template Generator

### Generate Test File

```python
from raptor.codegen import TestTemplateGenerator, TestScenario, TestType

generator = TestTemplateGenerator()
test_file = generator.generate_test_file(
    page_object_name="LoginPage",
    scenarios=[
        TestScenario(
            name="verify_login",
            description="Verify login works",
            test_type=TestType.FUNCTIONAL,
            page_object="LoginPage",
            steps=["Enter credentials", "Click login"],
            assertions=["User is logged in"],
            tags=["smoke"]
        )
    ]
)
```

### Generate Smoke Test Suite

```python
test_files = generator.generate_smoke_test_suite(
    page_objects=["LoginPage", "DashboardPage"],
    output_dir=Path("tests/smoke")
)
```

## Locator Suggester

### Suggest Locators

```python
from raptor.codegen import LocatorSuggester, ElementInfo

suggester = LocatorSuggester()
suggestions = suggester.suggest_locators(
    ElementInfo(
        tag_name="button",
        id="submit",
        role="button",
        text="Submit"
    ),
    max_suggestions=5
)

for s in suggestions:
    print(f"{s.priority.name}: {s.playwright_syntax}")
```

### Generate Report

```python
report = suggester.generate_locator_report(suggestions)
print(report)
```

## Code Formatter

### Format Code

```python
from raptor.codegen import CodeFormatter, FormatterConfig, FormatterType

formatter = CodeFormatter(
    FormatterConfig(
        formatter_type=FormatterType.BLACK,
        line_length=88
    )
)

result = formatter.format_code(code, sort_imports=True)
print(result.formatted_code)
```

### Format File

```python
result = formatter.format_file(
    file_path=Path("page.py"),
    in_place=True
)
```

## Element Types

| Type | Generated Methods |
|------|-------------------|
| button | `get_*_locator()`, `click_*()`, `is_*_visible()` |
| textbox | `get_*_locator()`, `fill_*()`, `get_*_value()`, `is_*_visible()` |
| dropdown | `get_*_locator()`, `select_*()`, `is_*_visible()` |
| checkbox | `get_*_locator()`, `check_*()`, `is_*_checked()`, `is_*_visible()` |
| table | `get_*_locator()`, `find_*_row()`, `get_*_cell_value()`, `is_*_visible()` |

## Locator Priority

- 🟢 **EXCELLENT** - Role, Test ID
- 🟡 **GOOD** - ID, Text
- 🟠 **ACCEPTABLE** - CSS
- 🔴 **POOR** - XPath

## Complete Workflow

```python
# 1. Suggest locator
suggester = LocatorSuggester()
suggestions = suggester.suggest_locators(element_info)
best_locator = suggestions[0].locator

# 2. Generate page object
page_generator = PageObjectGenerator()
page_object = page_generator.generate_page_object(app_name, elements)

# 3. Generate tests
test_generator = TestTemplateGenerator()
test_file = test_generator.generate_test_file(page_name, scenarios)

# 4. Format code
formatter = CodeFormatter()
page_result = formatter.format_code(page_object.code)
test_result = formatter.format_code(test_file.code)

# 5. Write files
Path("page.py").write_text(page_result.formatted_code)
Path("test.py").write_text(test_result.formatted_code)
```

## CLI Usage

```bash
# Generate page object
raptor codegen page-object --app Login --elements elements.json

# Generate tests
raptor codegen tests --page LoginPage --scenarios scenarios.json

# Suggest locators
raptor codegen suggest-locator --element element.json

# Format code
raptor codegen format --file page.py
```

## Common Patterns

### From DDFE Database

```python
# Load from database
elements = load_elements_from_ddfe(application="Login")

# Generate page object
page_object = generator.generate_page_object("Login", elements)

# Write to file
Path(f"raptor/pages/{page_object.file_name}").write_text(page_object.code)
```

### Batch Generation

```python
# Generate for all applications
apps = ["Login", "Dashboard", "Settings", "Admin"]

for app in apps:
    elements = load_elements_from_ddfe(application=app)
    page_object = generator.generate_page_object(app, elements)
    
    # Format
    result = formatter.format_code(page_object.code)
    
    # Write
    Path(f"raptor/pages/{page_object.file_name}").write_text(result.formatted_code)
```

### With Validation

```python
from raptor.migration.ddfe_validator import DDFEValidator

validator = DDFEValidator()

# Validate before generation
for element in elements:
    result = validator.validate_element(element)
    if not result.is_valid:
        print(f"Invalid element: {element.pv_name}")
        for issue in result.issues:
            print(f"  {issue.message}")
        continue
    
    # Generate if valid
    page_object = generator.generate_page_object(app, [element])
```

## See Also

- [Code Generation Guide](CODE_GENERATION_GUIDE.md) - Detailed documentation
- [Migration Guide](MIGRATION_UTILITIES_GUIDE.md) - Migration tools
- [CLI Guide](CLI_GUIDE.md) - Command-line interface
