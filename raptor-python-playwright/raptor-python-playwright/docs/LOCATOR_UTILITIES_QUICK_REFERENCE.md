# Locator Utilities Quick Reference

## Import

```python
from raptor.utils.locator_utilities import (
    LocatorParser,
    LocatorConverter,
    LocatorValidator,
    LocatorGenerator,
    parse_locator,
    validate_locator,
    convert_locator
)
```

## Locator Parser

```python
parser = LocatorParser()

# Parse locator
strategy, value = parser.parse("css=#button")

# Get strategy only
strategy = parser.get_strategy("xpath=//div")

# Get value only
value = parser.get_value("text=Click")

# Validate
is_valid = parser.validate("css=#button")
```

## Locator Converter

```python
converter = LocatorConverter()

# CSS to XPath
xpath = converter.css_to_xpath("#button")           # //*[@id='button']
xpath = converter.css_to_xpath(".class")            # //*[contains(@class, 'class')]
xpath = converter.css_to_xpath("button")            # //button
xpath = converter.css_to_xpath("div#id")            # //div[@id='id']
xpath = converter.css_to_xpath("button.class")      # //button[contains(@class, 'class')]

# ID/Class conversions
css = converter.id_to_css("button")                 # #button
xpath = converter.id_to_xpath("button")             # //*[@id='button']
css = converter.class_to_css("btn")                 # .btn
xpath = converter.class_to_xpath("btn")             # //*[contains(@class, 'btn')]

# Full locator conversion
result = converter.convert("css=#button", "xpath")  # xpath=//*[@id='button']
result = converter.convert("id=submit", "css")      # css=#submit
```

## Locator Validator

```python
validator = LocatorValidator()

# Validate locator
is_valid = validator.is_valid("css=#button")

# Validate CSS
is_valid, error = validator.validate_css("#button")

# Validate XPath
is_valid, error = validator.validate_xpath("//button")

# Get all errors
errors = validator.get_validation_errors("css=")
```

## Locator Generator

```python
generator = LocatorGenerator()

# By ID
generator.by_id("button")                           # css=#button
generator.by_id("button", use_xpath=True)           # xpath=//*[@id='button']

# By class
generator.by_class("btn")                           # css=.btn
generator.by_class("btn", use_xpath=True)           # xpath=//*[contains(@class, 'btn')]

# By text
generator.by_text("Submit")                         # text=Submit

# By role
generator.by_role("button")                         # role=button
generator.by_role("button", name="Submit")          # role=button[name='Submit']
generator.by_role("checkbox", checked=True)         # role=checkbox[checked='True']

# By attribute
generator.by_attribute("name", "user")              # css=[name='user']
generator.by_attribute("name", "user", tag="input") # css=input[name='user']
generator.by_attribute("href", "/", use_xpath=True) # xpath=//*[@href='/']

# By placeholder
generator.by_placeholder("Enter name")              # placeholder=Enter name

# By label
generator.by_label("Username")                      # label=Username

# By test ID
generator.by_test_id("submit-btn")                  # css=[data-testid='submit-btn']
generator.by_test_id("submit-btn", use_xpath=True)  # xpath=//*[@data-testid='submit-btn']

# Combine locators
generator.combine("#form", ".button")               # css=#form .button
generator.combine("div", ".btn", combinator=">")    # css=div > .btn
```

## Convenience Functions

```python
# Parse
strategy, value = parse_locator("css=#button")

# Validate
is_valid = validate_locator("css=#button")

# Convert
xpath = convert_locator("css=#button", "xpath")
```

## Common Patterns

### Generate with Fallbacks

```python
primary = generator.by_id("submit")
fallback1 = generator.by_test_id("submit-btn")
fallback2 = generator.by_role("button", name="Submit")

await element_manager.click(primary, fallback_locators=[fallback1, fallback2])
```

### Dynamic Locators

```python
def get_row_locator(row_id: str) -> str:
    return generator.by_attribute("data-row-id", row_id)

await element_manager.click(get_row_locator("123"))
```

### Validate Before Use

```python
locator = "css=#button"
if validate_locator(locator):
    await element_manager.click(locator)
```

### Convert for Compatibility

```python
css_locator = "css=#button"
xpath_locator = convert_locator(css_locator, "xpath")
```

## Supported Strategies

| Strategy | Format | Example |
|----------|--------|---------|
| CSS | `css=selector` | `css=#button` |
| XPath | `xpath=expression` | `xpath=//button` |
| Text | `text=content` | `text=Click Me` |
| Role | `role=name[attrs]` | `role=button[name='Submit']` |
| ID | `id=value` | `id=submit-button` |
| Placeholder | `placeholder=text` | `placeholder=Enter name` |
| Label | `label=text` | `label=Username` |
| Test ID | `test-id=value` | `test-id=submit-btn` |

## CSS to XPath Conversions

| CSS | XPath |
|-----|-------|
| `#id` | `//*[@id='id']` |
| `.class` | `//*[contains(@class, 'class')]` |
| `tag` | `//tag` |
| `[attr='val']` | `//*[@attr='val']` |
| `tag#id` | `//tag[@id='id']` |
| `tag.class` | `//tag[contains(@class, 'class')]` |
| `parent child` | `//parent//child` |
| `parent > child` | `//parent/child` |

## Error Messages

| Error | Cause |
|-------|-------|
| "Locator string cannot be empty" | Empty or whitespace-only locator |
| "Locator value cannot be empty" | Strategy prefix without value |
| "CSS selector cannot start with '='" | Invalid CSS syntax |
| "Unmatched square brackets" | Mismatched brackets in selector |
| "XPath expression should start with '/'" | Invalid XPath syntax |
| "ID value cannot be empty" | Empty ID in generator |
| "At least one locator must be provided" | Empty combine() call |
| "Invalid combinator" | Unsupported combinator in combine() |
