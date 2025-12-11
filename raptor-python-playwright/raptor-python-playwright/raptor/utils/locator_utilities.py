"""
Locator Utilities for RAPTOR Python Playwright Framework.

This module provides utilities for working with element locators:
- Locator string parsing
- Locator strategy conversion (CSS to XPath, etc.)
- Locator validation
- Dynamic locator generation

These utilities support the Element Manager and provide flexible locator handling.
"""

from typing import Optional, Dict, List, Tuple, Union
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class LocatorStrategy(Enum):
    """Supported locator strategies."""
    CSS = "css"
    XPATH = "xpath"
    TEXT = "text"
    ROLE = "role"
    ID = "id"
    PLACEHOLDER = "placeholder"
    LABEL = "label"
    ALT_TEXT = "alt"
    TITLE = "title"
    TEST_ID = "test-id"


class LocatorParser:
    """
    Parse and validate locator strings.
    
    Supports multiple locator formats:
    - "css=#element-id"
    - "xpath=//div[@class='test']"
    - "text=Click Me"
    - "role=button[name='Submit']"
    - "#element-id" (defaults to CSS)
    
    Example:
        >>> parser = LocatorParser()
        >>> strategy, value = parser.parse("css=#submit-button")
        >>> print(f"Strategy: {strategy}, Value: {value}")
        Strategy: css, Value: #submit-button
    """
    
    def __init__(self):
        """Initialize the locator parser."""
        self.valid_strategies = [s.value for s in LocatorStrategy]

    def parse(self, locator_string: str) -> Tuple[str, str]:
        """
        Parse a locator string into strategy and value.
        
        Args:
            locator_string: Locator string with optional strategy prefix
            
        Returns:
            Tuple of (strategy, value)
            
        Raises:
            ValueError: If locator string is empty or invalid
            
        Example:
            >>> parser = LocatorParser()
            >>> strategy, value = parser.parse("xpath=//button[@id='submit']")
            >>> print(strategy, value)
            xpath //button[@id='submit']
        """
        if not locator_string or not locator_string.strip():
            raise ValueError("Locator string cannot be empty")
        
        locator_string = locator_string.strip()
        
        # Check for explicit strategy prefix
        if "=" in locator_string:
            parts = locator_string.split("=", 1)
            strategy = parts[0].lower().strip()
            value = parts[1].strip()
            
            # Validate strategy
            if strategy not in self.valid_strategies:
                logger.warning(
                    f"Unknown locator strategy '{strategy}', defaulting to CSS. "
                    f"Valid strategies: {self.valid_strategies}"
                )
                return LocatorStrategy.CSS.value, locator_string
            
            if not value:
                raise ValueError(f"Locator value cannot be empty for strategy '{strategy}'")
            
            return strategy, value
        else:
            # Default to CSS selector
            return LocatorStrategy.CSS.value, locator_string
    
    def validate(self, locator_string: str) -> bool:
        """
        Validate a locator string.
        
        Args:
            locator_string: Locator string to validate
            
        Returns:
            True if valid, False otherwise
            
        Example:
            >>> parser = LocatorParser()
            >>> parser.validate("css=#button")
            True
            >>> parser.validate("")
            False
        """
        try:
            strategy, value = self.parse(locator_string)
            return bool(strategy and value)
        except (ValueError, Exception) as e:
            logger.debug(f"Locator validation failed: {locator_string} - {str(e)}")
            return False
    
    def get_strategy(self, locator_string: str) -> str:
        """
        Extract the strategy from a locator string.
        
        Args:
            locator_string: Locator string
            
        Returns:
            Strategy name (e.g., "css", "xpath", "text")
            
        Example:
            >>> parser = LocatorParser()
            >>> parser.get_strategy("xpath=//div")
            'xpath'
            >>> parser.get_strategy("#button")
            'css'
        """
        strategy, _ = self.parse(locator_string)
        return strategy
    
    def get_value(self, locator_string: str) -> str:
        """
        Extract the value from a locator string.
        
        Args:
            locator_string: Locator string
            
        Returns:
            Locator value
            
        Example:
            >>> parser = LocatorParser()
            >>> parser.get_value("css=#submit-button")
            '#submit-button'
        """
        _, value = self.parse(locator_string)
        return value


class LocatorConverter:
    """
    Convert locators between different strategies.
    
    Provides conversion utilities for transforming locators from one
    strategy to another (e.g., CSS to XPath, ID to CSS).
    
    Example:
        >>> converter = LocatorConverter()
        >>> xpath = converter.css_to_xpath("#submit-button")
        >>> print(xpath)
        //*[@id='submit-button']
    """
    
    def __init__(self):
        """Initialize the locator converter."""
        pass

    def css_to_xpath(self, css_selector: str) -> str:
        """
        Convert a CSS selector to XPath.
        
        Supports common CSS patterns:
        - ID: #id -> //*[@id='id']
        - Class: .class -> //*[contains(@class, 'class')]
        - Tag: div -> //div
        - Attribute: [name='value'] -> //*[@name='value']
        - Descendant: div .class -> //div//*[contains(@class, 'class')]
        - Child: div > .class -> //div/*[contains(@class, 'class')]
        
        Args:
            css_selector: CSS selector string
            
        Returns:
            Equivalent XPath expression
            
        Example:
            >>> converter = LocatorConverter()
            >>> converter.css_to_xpath("#submit-button")
            "//*[@id='submit-button']"
            >>> converter.css_to_xpath(".btn-primary")
            "//*[contains(@class, 'btn-primary')]"
        """
        if not css_selector or not css_selector.strip():
            raise ValueError("CSS selector cannot be empty")
        
        css_selector = css_selector.strip()
        
        # ID selector: #id
        if css_selector.startswith("#") and " " not in css_selector and ">" not in css_selector:
            id_value = css_selector[1:]
            return f"//*[@id='{id_value}']"
        
        # Class selector: .class
        if css_selector.startswith(".") and " " not in css_selector and ">" not in css_selector:
            class_value = css_selector[1:]
            return f"//*[contains(@class, '{class_value}')]"
        
        # Tag selector: div, button, etc.
        if css_selector.isalpha() or (css_selector.isalnum() and not css_selector[0].isdigit()):
            if " " not in css_selector and ">" not in css_selector and "[" not in css_selector:
                return f"//{css_selector}"
        
        # Attribute selector: [name='value']
        attr_match = re.match(r'\[([^=]+)=["\']([^"\']+)["\']\]', css_selector)
        if attr_match:
            attr_name = attr_match.group(1)
            attr_value = attr_match.group(2)
            return f"//*[@{attr_name}='{attr_value}']"
        
        # Tag with ID: div#id
        tag_id_match = re.match(r'(\w+)#(\w+)', css_selector)
        if tag_id_match:
            tag = tag_id_match.group(1)
            id_value = tag_id_match.group(2)
            return f"//{tag}[@id='{id_value}']"
        
        # Tag with class: div.class
        tag_class_match = re.match(r'(\w+)\.([\w-]+)', css_selector)
        if tag_class_match:
            tag = tag_class_match.group(1)
            class_value = tag_class_match.group(2)
            return f"//{tag}[contains(@class, '{class_value}')]"
        
        # Descendant combinator: div .class
        if " " in css_selector and ">" not in css_selector:
            parts = css_selector.split()
            if len(parts) == 2:
                parent_xpath = self.css_to_xpath(parts[0])
                child_xpath = self.css_to_xpath(parts[1])
                # Remove leading // from child
                child_xpath = child_xpath.lstrip("/")
                return f"{parent_xpath}//{child_xpath}"
        
        # Child combinator: div > .class
        if ">" in css_selector:
            parts = [p.strip() for p in css_selector.split(">")]
            if len(parts) == 2:
                parent_xpath = self.css_to_xpath(parts[0])
                child_xpath = self.css_to_xpath(parts[1])
                # Remove leading // from child and use single /
                child_xpath = child_xpath.lstrip("/")
                return f"{parent_xpath}/{child_xpath}"
        
        # Complex selector - log warning and return best effort
        logger.warning(
            f"Complex CSS selector may not convert accurately: {css_selector}. "
            "Consider using XPath directly for complex selectors."
        )
        return f"//*[contains(@class, '{css_selector}')]"

    def id_to_css(self, id_value: str) -> str:
        """
        Convert an ID value to CSS selector.
        
        Args:
            id_value: ID attribute value
            
        Returns:
            CSS selector string
            
        Example:
            >>> converter = LocatorConverter()
            >>> converter.id_to_css("submit-button")
            '#submit-button'
        """
        if not id_value or not id_value.strip():
            raise ValueError("ID value cannot be empty")
        
        return f"#{id_value.strip()}"
    
    def id_to_xpath(self, id_value: str) -> str:
        """
        Convert an ID value to XPath.
        
        Args:
            id_value: ID attribute value
            
        Returns:
            XPath expression
            
        Example:
            >>> converter = LocatorConverter()
            >>> converter.id_to_xpath("submit-button")
            "//*[@id='submit-button']"
        """
        if not id_value or not id_value.strip():
            raise ValueError("ID value cannot be empty")
        
        return f"//*[@id='{id_value.strip()}']"
    
    def class_to_css(self, class_value: str) -> str:
        """
        Convert a class value to CSS selector.
        
        Args:
            class_value: Class attribute value
            
        Returns:
            CSS selector string
            
        Example:
            >>> converter = LocatorConverter()
            >>> converter.class_to_css("btn-primary")
            '.btn-primary'
        """
        if not class_value or not class_value.strip():
            raise ValueError("Class value cannot be empty")
        
        return f".{class_value.strip()}"
    
    def class_to_xpath(self, class_value: str) -> str:
        """
        Convert a class value to XPath.
        
        Args:
            class_value: Class attribute value
            
        Returns:
            XPath expression
            
        Example:
            >>> converter = LocatorConverter()
            >>> converter.class_to_xpath("btn-primary")
            "//*[contains(@class, 'btn-primary')]"
        """
        if not class_value or not class_value.strip():
            raise ValueError("Class value cannot be empty")
        
        return f"//*[contains(@class, '{class_value.strip()}')]"
    
    def convert(self, locator_string: str, target_strategy: str) -> str:
        """
        Convert a locator string to a different strategy.
        
        Args:
            locator_string: Source locator string
            target_strategy: Target strategy ("css", "xpath", "id")
            
        Returns:
            Converted locator string with strategy prefix
            
        Raises:
            ValueError: If conversion is not supported
            
        Example:
            >>> converter = LocatorConverter()
            >>> converter.convert("css=#button", "xpath")
            "xpath=//*[@id='button']"
            >>> converter.convert("id=submit", "css")
            "css=#submit"
        """
        parser = LocatorParser()
        source_strategy, value = parser.parse(locator_string)
        
        target_strategy = target_strategy.lower()
        
        # No conversion needed
        if source_strategy == target_strategy:
            return locator_string
        
        # CSS to XPath
        if source_strategy == "css" and target_strategy == "xpath":
            xpath = self.css_to_xpath(value)
            return f"xpath={xpath}"
        
        # ID to CSS
        if source_strategy == "id" and target_strategy == "css":
            css = self.id_to_css(value)
            return f"css={css}"
        
        # ID to XPath
        if source_strategy == "id" and target_strategy == "xpath":
            xpath = self.id_to_xpath(value)
            return f"xpath={xpath}"
        
        # XPath to CSS (limited support)
        if source_strategy == "xpath" and target_strategy == "css":
            logger.warning(
                "XPath to CSS conversion has limited support. "
                "Complex XPath expressions may not convert accurately."
            )
            # Try to extract ID or class from simple XPath
            id_match = re.search(r"@id='([^']+)'", value)
            if id_match:
                return f"css=#{id_match.group(1)}"
            
            class_match = re.search(r"@class[,\s]+'([^']+)'", value)
            if class_match:
                return f"css=.{class_match.group(1)}"
            
            raise ValueError(
                f"Cannot convert complex XPath to CSS: {value}. "
                "Please use CSS selector directly."
            )
        
        raise ValueError(
            f"Conversion from '{source_strategy}' to '{target_strategy}' is not supported"
        )


class LocatorValidator:
    """
    Validate locator strings and strategies.
    
    Provides validation utilities to ensure locators are well-formed
    and follow best practices.
    
    Example:
        >>> validator = LocatorValidator()
        >>> validator.is_valid("css=#submit-button")
        True
        >>> validator.is_valid("")
        False
    """
    
    def __init__(self):
        """Initialize the locator validator."""
        self.parser = LocatorParser()

    def is_valid(self, locator_string: str) -> bool:
        """
        Check if a locator string is valid.
        
        Args:
            locator_string: Locator string to validate
            
        Returns:
            True if valid, False otherwise
            
        Example:
            >>> validator = LocatorValidator()
            >>> validator.is_valid("css=#button")
            True
            >>> validator.is_valid("invalid=")
            False
        """
        return self.parser.validate(locator_string)
    
    def validate_css(self, css_selector: str) -> Tuple[bool, Optional[str]]:
        """
        Validate a CSS selector.
        
        Args:
            css_selector: CSS selector to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Example:
            >>> validator = LocatorValidator()
            >>> valid, error = validator.validate_css("#button")
            >>> print(valid, error)
            True None
        """
        if not css_selector or not css_selector.strip():
            return False, "CSS selector cannot be empty"
        
        css_selector = css_selector.strip()
        
        # Check for common CSS selector patterns
        # This is a basic validation - complex selectors may pass even if invalid
        
        # Empty selector
        if not css_selector:
            return False, "CSS selector is empty"
        
        # Starts with invalid character
        if css_selector[0] in ["=", ">", "+", "~", ",", ")", "]"]:
            return False, f"CSS selector cannot start with '{css_selector[0]}'"
        
        # Unmatched brackets
        if css_selector.count("[") != css_selector.count("]"):
            return False, "Unmatched square brackets in CSS selector"
        
        if css_selector.count("(") != css_selector.count(")"):
            return False, "Unmatched parentheses in CSS selector"
        
        return True, None
    
    def validate_xpath(self, xpath_expression: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an XPath expression.
        
        Args:
            xpath_expression: XPath expression to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Example:
            >>> validator = LocatorValidator()
            >>> valid, error = validator.validate_xpath("//button[@id='submit']")
            >>> print(valid, error)
            True None
        """
        if not xpath_expression or not xpath_expression.strip():
            return False, "XPath expression cannot be empty"
        
        xpath_expression = xpath_expression.strip()
        
        # Basic XPath validation
        # This is a simple check - complex XPath may pass even if invalid
        
        # Should start with / or //
        if not xpath_expression.startswith("/") and not xpath_expression.startswith("("):
            return False, "XPath expression should start with '/' or '//'"
        
        # Unmatched brackets
        if xpath_expression.count("[") != xpath_expression.count("]"):
            return False, "Unmatched square brackets in XPath expression"
        
        if xpath_expression.count("(") != xpath_expression.count(")"):
            return False, "Unmatched parentheses in XPath expression"
        
        # Unmatched quotes
        single_quotes = xpath_expression.count("'")
        double_quotes = xpath_expression.count('"')
        
        if single_quotes % 2 != 0:
            return False, "Unmatched single quotes in XPath expression"
        
        if double_quotes % 2 != 0:
            return False, "Unmatched double quotes in XPath expression"
        
        return True, None
    
    def get_validation_errors(self, locator_string: str) -> List[str]:
        """
        Get all validation errors for a locator string.
        
        Args:
            locator_string: Locator string to validate
            
        Returns:
            List of error messages (empty if valid)
            
        Example:
            >>> validator = LocatorValidator()
            >>> errors = validator.get_validation_errors("css=")
            >>> print(errors)
            ['Locator value cannot be empty for strategy 'css'']
        """
        errors = []
        
        try:
            strategy, value = self.parser.parse(locator_string)
            
            # Validate based on strategy
            if strategy == "css":
                is_valid, error = self.validate_css(value)
                if not is_valid:
                    errors.append(error)
            
            elif strategy == "xpath":
                is_valid, error = self.validate_xpath(value)
                if not is_valid:
                    errors.append(error)
            
            elif strategy == "text":
                if not value:
                    errors.append("Text value cannot be empty")
            
            elif strategy == "id":
                if not value:
                    errors.append("ID value cannot be empty")
                elif " " in value:
                    errors.append("ID value should not contain spaces")
            
        except ValueError as e:
            errors.append(str(e))
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")
        
        return errors


class LocatorGenerator:
    """
    Generate locators dynamically based on element properties.
    
    Provides utilities to create locator strings from element attributes,
    text content, and other properties.
    
    Example:
        >>> generator = LocatorGenerator()
        >>> locator = generator.by_id("submit-button")
        >>> print(locator)
        css=#submit-button
    """
    
    def __init__(self):
        """Initialize the locator generator."""
        pass

    def by_id(self, id_value: str, use_xpath: bool = False) -> str:
        """
        Generate a locator by ID.
        
        Args:
            id_value: ID attribute value
            use_xpath: If True, generate XPath instead of CSS (default: False)
            
        Returns:
            Locator string with strategy prefix
            
        Example:
            >>> generator = LocatorGenerator()
            >>> generator.by_id("submit-button")
            'css=#submit-button'
            >>> generator.by_id("submit-button", use_xpath=True)
            "xpath=//*[@id='submit-button']"
        """
        if not id_value or not id_value.strip():
            raise ValueError("ID value cannot be empty")
        
        id_value = id_value.strip()
        
        if use_xpath:
            return f"xpath=//*[@id='{id_value}']"
        else:
            return f"css=#{id_value}"
    
    def by_class(self, class_value: str, use_xpath: bool = False) -> str:
        """
        Generate a locator by class name.
        
        Args:
            class_value: Class attribute value
            use_xpath: If True, generate XPath instead of CSS (default: False)
            
        Returns:
            Locator string with strategy prefix
            
        Example:
            >>> generator = LocatorGenerator()
            >>> generator.by_class("btn-primary")
            'css=.btn-primary'
            >>> generator.by_class("btn-primary", use_xpath=True)
            "xpath=//*[contains(@class, 'btn-primary')]"
        """
        if not class_value or not class_value.strip():
            raise ValueError("Class value cannot be empty")
        
        class_value = class_value.strip()
        
        if use_xpath:
            return f"xpath=//*[contains(@class, '{class_value}')]"
        else:
            return f"css=.{class_value}"
    
    def by_text(self, text: str, exact: bool = False) -> str:
        """
        Generate a locator by text content.
        
        Args:
            text: Text content to match
            exact: If True, match exact text; if False, match partial text (default: False)
            
        Returns:
            Locator string with strategy prefix
            
        Example:
            >>> generator = LocatorGenerator()
            >>> generator.by_text("Submit")
            'text=Submit'
            >>> generator.by_text("Click here", exact=True)
            'text=Click here'
        """
        if not text:
            raise ValueError("Text value cannot be empty")
        
        # Playwright's text locator supports both exact and partial matching
        # For exact match, we can use the text= prefix directly
        return f"text={text}"
    
    def by_role(self, role: str, name: Optional[str] = None, **attributes) -> str:
        """
        Generate a locator by ARIA role.
        
        Args:
            role: ARIA role (e.g., "button", "link", "textbox")
            name: Optional accessible name
            **attributes: Additional role attributes (e.g., checked=True, disabled=False)
            
        Returns:
            Locator string with strategy prefix
            
        Example:
            >>> generator = LocatorGenerator()
            >>> generator.by_role("button")
            'role=button'
            >>> generator.by_role("button", name="Submit")
            "role=button[name='Submit']"
            >>> generator.by_role("checkbox", name="Accept", checked=True)
            "role=checkbox[name='Accept',checked='True']"
        """
        if not role or not role.strip():
            raise ValueError("Role value cannot be empty")
        
        role = role.strip()
        
        # Build role locator with attributes
        if name or attributes:
            attrs = []
            if name:
                attrs.append(f"name='{name}'")
            for key, value in attributes.items():
                attrs.append(f"{key}='{value}'")
            
            attrs_str = ",".join(attrs)
            return f"role={role}[{attrs_str}]"
        else:
            return f"role={role}"
    
    def by_attribute(
        self,
        attribute: str,
        value: str,
        tag: Optional[str] = None,
        use_xpath: bool = False
    ) -> str:
        """
        Generate a locator by attribute.
        
        Args:
            attribute: Attribute name (e.g., "name", "data-testid", "href")
            value: Attribute value
            tag: Optional tag name to narrow the search
            use_xpath: If True, generate XPath instead of CSS (default: False)
            
        Returns:
            Locator string with strategy prefix
            
        Example:
            >>> generator = LocatorGenerator()
            >>> generator.by_attribute("name", "username")
            "css=[name='username']"
            >>> generator.by_attribute("data-testid", "submit-btn", tag="button")
            "css=button[data-testid='submit-btn']"
            >>> generator.by_attribute("href", "/login", use_xpath=True)
            "xpath=//*[@href='/login']"
        """
        if not attribute or not attribute.strip():
            raise ValueError("Attribute name cannot be empty")
        if not value:
            raise ValueError("Attribute value cannot be empty")
        
        attribute = attribute.strip()
        
        if use_xpath:
            if tag:
                return f"xpath=//{tag}[@{attribute}='{value}']"
            else:
                return f"xpath=//*[@{attribute}='{value}']"
        else:
            if tag:
                return f"css={tag}[{attribute}='{value}']"
            else:
                return f"css=[{attribute}='{value}']"
    
    def by_placeholder(self, placeholder: str) -> str:
        """
        Generate a locator by placeholder text.
        
        Args:
            placeholder: Placeholder text
            
        Returns:
            Locator string with strategy prefix
            
        Example:
            >>> generator = LocatorGenerator()
            >>> generator.by_placeholder("Enter username")
            'placeholder=Enter username'
        """
        if not placeholder:
            raise ValueError("Placeholder value cannot be empty")
        
        return f"placeholder={placeholder}"
    
    def by_label(self, label: str) -> str:
        """
        Generate a locator by label text.
        
        Args:
            label: Label text
            
        Returns:
            Locator string with strategy prefix
            
        Example:
            >>> generator = LocatorGenerator()
            >>> generator.by_label("Username")
            'label=Username'
        """
        if not label:
            raise ValueError("Label value cannot be empty")
        
        return f"label={label}"
    
    def by_test_id(self, test_id: str, use_xpath: bool = False) -> str:
        """
        Generate a locator by test ID (data-testid attribute).
        
        Args:
            test_id: Test ID value
            use_xpath: If True, generate XPath instead of CSS (default: False)
            
        Returns:
            Locator string with strategy prefix
            
        Example:
            >>> generator = LocatorGenerator()
            >>> generator.by_test_id("submit-button")
            "css=[data-testid='submit-button']"
            >>> generator.by_test_id("submit-button", use_xpath=True)
            "xpath=//*[@data-testid='submit-button']"
        """
        if not test_id or not test_id.strip():
            raise ValueError("Test ID value cannot be empty")
        
        return self.by_attribute("data-testid", test_id.strip(), use_xpath=use_xpath)
    
    def combine(self, *locators: str, combinator: str = " ") -> str:
        """
        Combine multiple locators with a combinator.
        
        Args:
            *locators: Locator strings to combine (without strategy prefix)
            combinator: Combinator to use (" " for descendant, ">" for child)
            
        Returns:
            Combined CSS locator string with strategy prefix
            
        Raises:
            ValueError: If locators are empty or invalid combinator
            
        Example:
            >>> generator = LocatorGenerator()
            >>> generator.combine("#form", ".submit-button")
            'css=#form .submit-button'
            >>> generator.combine("div", ".container", combinator=">")
            'css=div > .container'
        """
        if not locators:
            raise ValueError("At least one locator must be provided")
        
        if combinator not in [" ", ">", "+", "~"]:
            raise ValueError(f"Invalid combinator: {combinator}. Valid: ' ', '>', '+', '~'")
        
        # Remove strategy prefixes if present
        clean_locators = []
        parser = LocatorParser()
        
        for loc in locators:
            if "=" in loc:
                _, value = parser.parse(loc)
                clean_locators.append(value)
            else:
                clean_locators.append(loc)
        
        # Join with combinator, preserving spaces for readability
        if combinator == " ":
            combined = " ".join(clean_locators)
        else:
            combined = f" {combinator} ".join(clean_locators)
        
        return f"css={combined}"


# Convenience functions for quick access
def parse_locator(locator_string: str) -> Tuple[str, str]:
    """
    Parse a locator string into strategy and value.
    
    Convenience function that creates a LocatorParser and parses the string.
    
    Args:
        locator_string: Locator string to parse
        
    Returns:
        Tuple of (strategy, value)
        
    Example:
        >>> strategy, value = parse_locator("css=#button")
        >>> print(strategy, value)
        css #button
    """
    parser = LocatorParser()
    return parser.parse(locator_string)


def validate_locator(locator_string: str) -> bool:
    """
    Validate a locator string.
    
    Convenience function that creates a LocatorValidator and validates the string.
    
    Args:
        locator_string: Locator string to validate
        
    Returns:
        True if valid, False otherwise
        
    Example:
        >>> validate_locator("css=#button")
        True
        >>> validate_locator("")
        False
    """
    validator = LocatorValidator()
    return validator.is_valid(locator_string)


def convert_locator(locator_string: str, target_strategy: str) -> str:
    """
    Convert a locator to a different strategy.
    
    Convenience function that creates a LocatorConverter and converts the locator.
    
    Args:
        locator_string: Source locator string
        target_strategy: Target strategy ("css", "xpath", "id")
        
    Returns:
        Converted locator string
        
    Example:
        >>> convert_locator("css=#button", "xpath")
        "xpath=//*[@id='button']"
    """
    converter = LocatorConverter()
    return converter.convert(locator_string, target_strategy)
