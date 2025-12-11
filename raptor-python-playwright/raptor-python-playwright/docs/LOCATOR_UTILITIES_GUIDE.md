# Locator Utilities Guide

## Overview

The RAPTOR Locator Utilities provide a comprehensive set of tools for working with element locators in your test automation. These utilities support parsing, converting, validating, and generating locators across multiple strategies.

## Features

- **Locator Parsing**: Parse locator strings into strategy and value components
- **Strategy Conversion**: Convert locators between different strategies (CSS to XPath, etc.)
- **Locator Validation**: Validate locator syntax and structure
- **Dynamic Generation**: Generate locators programmatically from element properties

## Supported Locator Strategies

The framework supports the following locator strategies:

- **CSS**: CSS selectors (`css=#button`, `.class`, `[name='value']`)
- **XPath**: XPath expressions (`xpath=//button[@id='submit']`)
- **Text**: Text content matching (`text=Click Me`)
- **Role**: ARIA role matching (`role=button[name='Submit']`)
- **ID**: Element ID (`id=submit-button`)
- **Placeholder**: Placeholder text (`placeholder=Enter username`)
- **Label**: Label text (`label=Username`)
- **Test ID**: Data-testid attribute (`test-id=submit-btn`)

## Locator Parser

### Basic Usage

```python
from raptor.utils.locator_utilities import LocatorParser

parser = LocatorParser()

# Parse a locator string
strategy, value = parser.parse("css=#submit-button")
print(f"Strategy: {strategy}, Value: {value}")
# Output: Strategy: css, Value: #submit-button

# Extract just the strategy
strategy = parser.get_strategy("xpath=//button")
print(strategy)  # Output: xpath

# Extract just the value
value = parser.get_value("text=Click Me")
print(value)  # Output: Click Me

# Validate a locator
is_valid = parser.validate("css=#button")
print(is_valid)  # Output: True
```

### Supported Formats

The parser supports multiple locator formats:

```python
# Explicit strategy prefix
parser.parse("css=#element-id")          # ('css', '#element-id')
parser.parse("xpath=//div[@class='test']")  # ('xpath', "//div[@class='test']")
parser.parse("text=Click Me")            # ('text', 'Click Me')
parser.parse("role=button[name='Submit']")  # ('role', "button[name='Submit']")

# Default to CSS when no prefix
parser.parse("#element-id")              # ('css', '#element-id')
parser.parse(".btn-primary")             # ('css', '.btn-primary')
```

## Locator Converter

### CSS to XPath Conversion

```python
from raptor.utils.locator_utilities import LocatorConverter

converter = LocatorConverter()

# Convert CSS selectors to XPath
xpath = converter.css_to_xpath("#submit-button")
print(xpath)  # Output: //*[@id='submit-button']

xpath = converter.css_to_xpath(".btn-primary")
print(xpath)  # Output: //*[contains(@class, 'btn-primary')]

xpath = converter.css_to_xpath("button")
print(xpath)  # Output: //button

xpath = converter.css_to_xpath("div#container")
print(xpath)  # Output: //div[@id='container']

xpath = converter.css_to_xpath("button.btn-primary")
print(xpath)  # Output: //button[contains(@class, 'btn-primary')]

# Descendant combinator
xpath = converter.css_to_xpath("div .button")
print(xpath)  # Output: //div//*[contains(@class, 'button')]

# Child combinator
xpath = converter.css_to_xpath("div > .button")
print(xpath)  # Output: //div/*[contains(@class, 'button')]
```

### ID and Class Conversions

```python
# Convert ID to CSS
css = converter.id_to_css("submit-button")
print(css)  # Output: #submit-button

# Convert ID to XPath
xpath = converter.id_to_xpath("submit-button")
print(xpath)  # Output: //*[@id='submit-button']

# Convert class to CSS
css = converter.class_to_css("btn-primary")
print(css)  # Output: .btn-primary

# Convert class to XPath
xpath = converter.class_to_xpath("btn-primary")
print(xpath)  # Output: //*[contains(@class, 'btn-primary')]
```

### Full Locator String Conversion

```python
# Convert complete locator strings
result = converter.convert("css=#button", "xpath")
print(result)  # Output: xpath=//*[@id='button']

result = converter.convert("id=submit", "css")
print(result)  # Output: css=#submit

result = converter.convert("id=submit", "xpath")
print(result)  # Output: xpath=//*[@id='submit']
```

## Locator Validator

### Validation Methods

```python
from raptor.utils.locator_utilities import LocatorValidator

validator = LocatorValidator()

# Validate complete locator strings
is_valid = validator.is_valid("css=#button")
print(is_valid)  # Output: True

is_valid = validator.is_valid("")
print(is_valid)  # Output: False

# Validate CSS selectors
is_valid, error = validator.validate_css("#button")
print(f"Valid: {is_valid}, Error: {error}")
# Output: Valid: True, Error: None

is_valid, error = validator.validate_css("=button")
print(f"Valid: {is_valid}, Error: {error}")
# Output: Valid: False, Error: CSS selector cannot start with '='

# Validate XPath expressions
is_valid, error = validator.validate_xpath("//button[@id='submit']")
print(f"Valid: {is_valid}, Error: {error}")
# Output: Valid: True, Error: None

is_valid, error = validator.validate_xpath("button")
print(f"Valid: {is_valid}, Error: {error}")
# Output: Valid: False, Error: XPath expression should start with '/' or '//'
```

### Get All Validation Errors

```python
# Get all validation errors for a locator
errors = validator.get_validation_errors("css=")
print(errors)
# Output: ['Locator value cannot be empty for strategy 'css'']

errors = validator.get_validation_errors("css=[name='test'")
print(errors)
# Output: ['Unmatched square brackets in CSS selector']

errors = validator.get_validation_errors("css=#button")
print(errors)
# Output: []  # No errors
```

## Locator Generator

### Generate by Element Properties

```python
from raptor.utils.locator_utilities import LocatorGenerator

generator = LocatorGenerator()

# Generate by ID
locator = generator.by_id("submit-button")
print(locator)  # Output: css=#submit-button

locator = generator.by_id("submit-button", use_xpath=True)
print(locator)  # Output: xpath=//*[@id='submit-button']

# Generate by class
locator = generator.by_class("btn-primary")
print(locator)  # Output: css=.btn-primary

locator = generator.by_class("btn-primary", use_xpath=True)
print(locator)  # Output: xpath=//*[contains(@class, 'btn-primary')]

# Generate by text
locator = generator.by_text("Submit")
print(locator)  # Output: text=Submit

# Generate by role
locator = generator.by_role("button")
print(locator)  # Output: role=button

locator = generator.by_role("button", name="Submit")
print(locator)  # Output: role=button[name='Submit']

locator = generator.by_role("checkbox", name="Accept", checked=True)
print(locator)  # Output: role=checkbox[name='Accept',checked='True']
```

### Generate by Attributes

```python
# Generate by any attribute
locator = generator.by_attribute("name", "username")
print(locator)  # Output: css=[name='username']

locator = generator.by_attribute("data-testid", "submit-btn", tag="button")
print(locator)  # Output: css=button[data-testid='submit-btn']

locator = generator.by_attribute("href", "/login", use_xpath=True)
print(locator)  # Output: xpath=//*[@href='/login']

# Generate by placeholder
locator = generator.by_placeholder("Enter username")
print(locator)  # Output: placeholder=Enter username

# Generate by label
locator = generator.by_label("Username")
print(locator)  # Output: label=Username

# Generate by test ID
locator = generator.by_test_id("submit-button")
print(locator)  # Output: css=[data-testid='submit-button']

locator = generator.by_test_id("submit-button", use_xpath=True)
print(locator)  # Output: xpath=//*[@data-testid='submit-button']
```

### Combine Locators

```python
# Combine with descendant combinator (space)
locator = generator.combine("#form", ".submit-button")
print(locator)  # Output: css=#form .submit-button

# Combine with child combinator (>)
locator = generator.combine("div", ".container", combinator=">")
print(locator)  # Output: css=div > .container

# Combine with adjacent sibling combinator (+)
locator = generator.combine("h1", "p", combinator="+")
print(locator)  # Output: css=h1 + p

# Combine with general sibling combinator (~)
locator = generator.combine("h1", "p", combinator="~")
print(locator)  # Output: css=h1 ~ p

# Combine multiple locators
locator = generator.combine("#container", "div", ".button")
print(locator)  # Output: css=#container div .button
```

## Convenience Functions

For quick access, the module provides convenience functions:

```python
from raptor.utils.locator_utilities import (
    parse_locator,
    validate_locator,
    convert_locator
)

# Parse a locator
strategy, value = parse_locator("css=#button")

# Validate a locator
is_valid = validate_locator("css=#button")

# Convert a locator
xpath_locator = convert_locator("css=#button", "xpath")
```

## Integration with Element Manager

The locator utilities integrate seamlessly with the Element Manager:

```python
from raptor.core.element_manager import ElementManager
from raptor.utils.locator_utilities import LocatorGenerator

# Create element manager
element_manager = ElementManager(page)

# Generate locators dynamically
generator = LocatorGenerator()

# Use generated locators with element manager
await element_manager.click(generator.by_id("submit-button"))
await element_manager.fill(generator.by_placeholder("Enter username"), "john.doe")
await element_manager.hover(generator.by_role("button", name="Menu"))

# Combine locators for complex selections
form_button = generator.combine("#login-form", "button.submit")
await element_manager.click(form_button)
```

## Best Practices

### 1. Use Appropriate Strategies

Choose the most stable and maintainable locator strategy:

```python
# Prefer ID when available (most stable)
locator = generator.by_id("submit-button")

# Use test IDs for test-specific elements
locator = generator.by_test_id("login-submit")

# Use role for accessibility-friendly locators
locator = generator.by_role("button", name="Submit")

# Use CSS for simple selectors
locator = "css=.btn-primary"

# Use XPath only when necessary (complex hierarchies)
locator = "xpath=//div[@class='container']//button[text()='Submit']"
```

### 2. Validate Locators Before Use

```python
validator = LocatorValidator()

locator = "css=#submit-button"
if validator.is_valid(locator):
    await element_manager.click(locator)
else:
    errors = validator.get_validation_errors(locator)
    print(f"Invalid locator: {errors}")
```

### 3. Convert Strategically

```python
converter = LocatorConverter()

# Convert CSS to XPath when needed for complex selections
css_locator = "css=#button"
xpath_locator = converter.convert(css_locator, "xpath")

# Use the converted locator
await element_manager.click(xpath_locator)
```

### 4. Generate Dynamically

```python
generator = LocatorGenerator()

# Generate locators based on runtime data
def get_button_locator(button_id: str) -> str:
    return generator.by_id(button_id)

# Use in tests
await element_manager.click(get_button_locator("submit-button"))
await element_manager.click(get_button_locator("cancel-button"))
```

## Common Patterns

### Pattern 1: Fallback Locators

```python
generator = LocatorGenerator()

# Generate primary and fallback locators
primary = generator.by_id("submit-button")
fallback1 = generator.by_test_id("submit-btn")
fallback2 = generator.by_role("button", name="Submit")

# Use with element manager
await element_manager.click(
    primary,
    fallback_locators=[fallback1, fallback2]
)
```

### Pattern 2: Dynamic Table Locators

```python
generator = LocatorGenerator()

def get_table_cell_locator(row: int, column: int) -> str:
    """Generate locator for table cell."""
    return generator.by_attribute(
        "data-row", str(row),
        tag="td"
    )

# Use in tests
cell_locator = get_table_cell_locator(2, 3)
await element_manager.click(cell_locator)
```

### Pattern 3: Form Field Locators

```python
generator = LocatorGenerator()

# Generate locators for form fields
username_field = generator.by_label("Username")
password_field = generator.by_placeholder("Enter password")
submit_button = generator.by_role("button", name="Login")

# Fill form
await element_manager.fill(username_field, "john.doe")
await element_manager.fill(password_field, "password123")
await element_manager.click(submit_button)
```

## Error Handling

The locator utilities provide clear error messages:

```python
from raptor.utils.locator_utilities import LocatorGenerator

generator = LocatorGenerator()

try:
    # This will raise ValueError
    locator = generator.by_id("")
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: ID value cannot be empty

try:
    # This will raise ValueError
    locator = generator.combine()
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: At least one locator must be provided
```

## Performance Considerations

- **Parsing**: Locator parsing is lightweight and can be done frequently
- **Conversion**: CSS to XPath conversion is fast for simple selectors
- **Validation**: Validation is quick and recommended before using locators
- **Generation**: Dynamic generation has minimal overhead

## See Also

- [Element Manager Guide](ELEMENT_MANAGER_IMPLEMENTATION.md)
- [Element Interaction Methods](ELEMENT_INTERACTION_QUICK_REFERENCE.md)
- [Test Execution Control](TEST_EXECUTION_CONTROL_GUIDE.md)
