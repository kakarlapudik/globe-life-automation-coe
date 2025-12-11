"""
Example usage of Locator Utilities.

This example demonstrates how to use the locator parsing, conversion,
validation, and generation utilities in the RAPTOR framework.
"""

import asyncio
from playwright.async_api import async_playwright
from raptor.utils.locator_utilities import (
    LocatorParser,
    LocatorConverter,
    LocatorValidator,
    LocatorGenerator,
    parse_locator,
    validate_locator,
    convert_locator,
)


async def example_locator_parser():
    """Demonstrate locator parsing."""
    print("\n=== Locator Parser Examples ===\n")
    
    parser = LocatorParser()
    
    # Parse different locator formats
    locators = [
        "css=#submit-button",
        "xpath=//button[@id='submit']",
        "text=Click Me",
        "role=button[name='Submit']",
        "#button",  # Defaults to CSS
    ]
    
    for locator in locators:
        strategy, value = parser.parse(locator)
        print(f"Locator: {locator}")
        print(f"  Strategy: {strategy}")
        print(f"  Value: {value}")
        print(f"  Valid: {parser.validate(locator)}\n")


async def example_locator_converter():
    """Demonstrate locator conversion."""
    print("\n=== Locator Converter Examples ===\n")
    
    converter = LocatorConverter()
    
    # CSS to XPath conversions
    css_selectors = [
        "#submit-button",
        ".btn-primary",
        "button",
        "div#container",
        "button.btn-primary",
        "div .button",
        "div > .button",
    ]
    
    print("CSS to XPath Conversions:")
    for css in css_selectors:
        xpath = converter.css_to_xpath(css)
        print(f"  {css:20} -> {xpath}")
    
    print("\nID/Class Conversions:")
    print(f"  ID 'button' to CSS:   {converter.id_to_css('button')}")
    print(f"  ID 'button' to XPath: {converter.id_to_xpath('button')}")
    print(f"  Class 'btn' to CSS:   {converter.class_to_css('btn')}")
    print(f"  Class 'btn' to XPath: {converter.class_to_xpath('btn')}")
    
    print("\nFull Locator Conversions:")
    conversions = [
        ("css=#button", "xpath"),
        ("id=submit", "css"),
        ("id=submit", "xpath"),
    ]
    
    for source, target in conversions:
        result = converter.convert(source, target)
        print(f"  {source} -> {target}: {result}")


async def example_locator_validator():
    """Demonstrate locator validation."""
    print("\n=== Locator Validator Examples ===\n")
    
    validator = LocatorValidator()
    
    # Validate various locators
    test_locators = [
        ("css=#button", True),
        ("xpath=//button", True),
        ("", False),
        ("css=", False),
        ("css==button", False),
        ("css=[name='test'", False),  # Unmatched bracket
    ]
    
    print("Locator Validation:")
    for locator, expected in test_locators:
        is_valid = validator.is_valid(locator)
        status = "✓" if is_valid == expected else "✗"
        print(f"  {status} {locator:30} Valid: {is_valid}")
        
        if not is_valid:
            errors = validator.get_validation_errors(locator)
            for error in errors:
                print(f"      Error: {error}")
    
    # Validate CSS selectors
    print("\nCSS Selector Validation:")
    css_selectors = [
        ("#button", True),
        ("", False),
        ("=button", False),
        ("[name='test'", False),
    ]
    
    for css, expected in css_selectors:
        is_valid, error = validator.validate_css(css)
        status = "✓" if is_valid == expected else "✗"
        print(f"  {status} {css:20} Valid: {is_valid}")
        if error:
            print(f"      Error: {error}")
    
    # Validate XPath expressions
    print("\nXPath Expression Validation:")
    xpath_expressions = [
        ("//button[@id='submit']", True),
        ("", False),
        ("button", False),
        ("//button[@id='test'", False),
    ]
    
    for xpath, expected in xpath_expressions:
        is_valid, error = validator.validate_xpath(xpath)
        status = "✓" if is_valid == expected else "✗"
        print(f"  {status} {xpath:30} Valid: {is_valid}")
        if error:
            print(f"      Error: {error}")


async def example_locator_generator():
    """Demonstrate locator generation."""
    print("\n=== Locator Generator Examples ===\n")
    
    generator = LocatorGenerator()
    
    # Generate by ID
    print("Generate by ID:")
    print(f"  CSS:   {generator.by_id('submit-button')}")
    print(f"  XPath: {generator.by_id('submit-button', use_xpath=True)}")
    
    # Generate by class
    print("\nGenerate by Class:")
    print(f"  CSS:   {generator.by_class('btn-primary')}")
    print(f"  XPath: {generator.by_class('btn-primary', use_xpath=True)}")
    
    # Generate by text
    print("\nGenerate by Text:")
    print(f"  {generator.by_text('Submit')}")
    print(f"  {generator.by_text('Click here')}")
    
    # Generate by role
    print("\nGenerate by Role:")
    print(f"  Simple:       {generator.by_role('button')}")
    print(f"  With name:    {generator.by_role('button', name='Submit')}")
    print(f"  With attrs:   {generator.by_role('checkbox', name='Accept', checked=True)}")
    
    # Generate by attribute
    print("\nGenerate by Attribute:")
    print(f"  CSS:          {generator.by_attribute('name', 'username')}")
    print(f"  CSS with tag: {generator.by_attribute('data-testid', 'submit-btn', tag='button')}")
    print(f"  XPath:        {generator.by_attribute('href', '/login', use_xpath=True)}")
    
    # Generate by other strategies
    print("\nGenerate by Other Strategies:")
    print(f"  Placeholder:  {generator.by_placeholder('Enter username')}")
    print(f"  Label:        {generator.by_label('Username')}")
    print(f"  Test ID CSS:  {generator.by_test_id('submit-button')}")
    print(f"  Test ID XPath:{generator.by_test_id('submit-button', use_xpath=True)}")
    
    # Combine locators
    print("\nCombine Locators:")
    print(f"  Descendant:   {generator.combine('#form', '.submit-button')}")
    print(f"  Child:        {generator.combine('div', '.container', combinator='>')}")
    print(f"  Adjacent:     {generator.combine('h1', 'p', combinator='+')}")
    print(f"  Sibling:      {generator.combine('h1', 'p', combinator='~')}")
    print(f"  Multiple:     {generator.combine('#container', 'div', '.button')}")


async def example_convenience_functions():
    """Demonstrate convenience functions."""
    print("\n=== Convenience Functions ===\n")
    
    # Parse locator
    strategy, value = parse_locator("css=#button")
    print(f"Parse: css=#button")
    print(f"  Strategy: {strategy}")
    print(f"  Value: {value}")
    
    # Validate locator
    print(f"\nValidate: css=#button")
    print(f"  Valid: {validate_locator('css=#button')}")
    
    print(f"\nValidate: (empty)")
    print(f"  Valid: {validate_locator('')}")
    
    # Convert locator
    print(f"\nConvert: css=#button to xpath")
    print(f"  Result: {convert_locator('css=#button', 'xpath')}")
    
    print(f"\nConvert: id=submit to css")
    print(f"  Result: {convert_locator('id=submit', 'css')}")


async def example_practical_usage():
    """Demonstrate practical usage with Playwright."""
    print("\n=== Practical Usage with Playwright ===\n")
    
    generator = LocatorGenerator()
    validator = LocatorValidator()
    
    # Generate locators for a login form
    print("Login Form Locators:")
    username_locator = generator.by_label("Username")
    password_locator = generator.by_placeholder("Enter password")
    remember_locator = generator.by_role("checkbox", name="Remember me")
    submit_locator = generator.by_role("button", name="Login")
    
    print(f"  Username field: {username_locator}")
    print(f"  Password field: {password_locator}")
    print(f"  Remember checkbox: {remember_locator}")
    print(f"  Submit button: {submit_locator}")
    
    # Validate all locators
    print("\nValidating locators:")
    locators = [username_locator, password_locator, remember_locator, submit_locator]
    for loc in locators:
        is_valid = validator.is_valid(loc)
        print(f"  {loc:40} Valid: {is_valid}")
    
    # Generate fallback locators
    print("\nGenerating fallback locators for submit button:")
    primary = generator.by_role("button", name="Login")
    fallback1 = generator.by_id("login-submit")
    fallback2 = generator.by_test_id("login-btn")
    fallback3 = generator.by_attribute("type", "submit", tag="button")
    
    print(f"  Primary:   {primary}")
    print(f"  Fallback 1: {fallback1}")
    print(f"  Fallback 2: {fallback2}")
    print(f"  Fallback 3: {fallback3}")
    
    # Generate complex combined locators
    print("\nGenerating complex combined locators:")
    form_button = generator.combine("#login-form", "button.submit")
    nested_input = generator.combine("div.container", "form", "input[name='email']")
    
    print(f"  Form button: {form_button}")
    print(f"  Nested input: {nested_input}")


async def example_dynamic_locators():
    """Demonstrate dynamic locator generation."""
    print("\n=== Dynamic Locator Generation ===\n")
    
    generator = LocatorGenerator()
    
    # Function to generate table cell locators
    def get_table_cell_locator(row: int, column: int) -> str:
        """Generate locator for table cell at specific row and column."""
        return generator.by_attribute("data-cell", f"{row}-{column}", tag="td")
    
    # Function to generate button locators by action
    def get_action_button_locator(action: str) -> str:
        """Generate locator for action button."""
        return generator.by_role("button", name=action.title())
    
    # Function to generate form field locators
    def get_form_field_locator(field_name: str) -> str:
        """Generate locator for form field by name."""
        return generator.by_attribute("name", field_name, tag="input")
    
    print("Dynamic Table Cell Locators:")
    for row in range(1, 4):
        for col in range(1, 4):
            locator = get_table_cell_locator(row, col)
            print(f"  Cell ({row},{col}): {locator}")
    
    print("\nDynamic Action Button Locators:")
    actions = ["save", "cancel", "delete", "edit"]
    for action in actions:
        locator = get_action_button_locator(action)
        print(f"  {action.title():10} button: {locator}")
    
    print("\nDynamic Form Field Locators:")
    fields = ["username", "email", "password", "confirm_password"]
    for field in fields:
        locator = get_form_field_locator(field)
        print(f"  {field:20} field: {locator}")


async def main():
    """Run all examples."""
    print("=" * 70)
    print("RAPTOR Locator Utilities Examples")
    print("=" * 70)
    
    await example_locator_parser()
    await example_locator_converter()
    await example_locator_validator()
    await example_locator_generator()
    await example_convenience_functions()
    await example_practical_usage()
    await example_dynamic_locators()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
