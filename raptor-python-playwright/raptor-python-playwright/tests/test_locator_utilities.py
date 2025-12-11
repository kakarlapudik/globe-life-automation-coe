"""
Tests for Locator Utilities.

This module tests the locator parsing, conversion, validation, and generation
utilities provided by the RAPTOR framework.
"""

import pytest
from raptor.utils.locator_utilities import (
    LocatorParser,
    LocatorConverter,
    LocatorValidator,
    LocatorGenerator,
    LocatorStrategy,
    parse_locator,
    validate_locator,
    convert_locator,
)


class TestLocatorParser:
    """Test the LocatorParser class."""
    
    def test_parse_css_with_prefix(self):
        """Test parsing CSS selector with explicit prefix."""
        parser = LocatorParser()
        strategy, value = parser.parse("css=#submit-button")
        
        assert strategy == "css"
        assert value == "#submit-button"
    
    def test_parse_xpath_with_prefix(self):
        """Test parsing XPath with explicit prefix."""
        parser = LocatorParser()
        strategy, value = parser.parse("xpath=//button[@id='submit']")
        
        assert strategy == "xpath"
        assert value == "//button[@id='submit']"
    
    def test_parse_text_locator(self):
        """Test parsing text locator."""
        parser = LocatorParser()
        strategy, value = parser.parse("text=Click Me")
        
        assert strategy == "text"
        assert value == "Click Me"
    
    def test_parse_role_locator(self):
        """Test parsing role locator."""
        parser = LocatorParser()
        strategy, value = parser.parse("role=button[name='Submit']")
        
        assert strategy == "role"
        assert value == "button[name='Submit']"
    
    def test_parse_without_prefix_defaults_to_css(self):
        """Test that locators without prefix default to CSS."""
        parser = LocatorParser()
        strategy, value = parser.parse("#submit-button")
        
        assert strategy == "css"
        assert value == "#submit-button"
    
    def test_parse_empty_string_raises_error(self):
        """Test that empty string raises ValueError."""
        parser = LocatorParser()
        
        with pytest.raises(ValueError, match="Locator string cannot be empty"):
            parser.parse("")
    
    def test_parse_whitespace_only_raises_error(self):
        """Test that whitespace-only string raises ValueError."""
        parser = LocatorParser()
        
        with pytest.raises(ValueError, match="Locator string cannot be empty"):
            parser.parse("   ")
    
    def test_parse_empty_value_raises_error(self):
        """Test that empty value after strategy raises ValueError."""
        parser = LocatorParser()
        
        with pytest.raises(ValueError, match="Locator value cannot be empty"):
            parser.parse("css=")
    
    def test_parse_unknown_strategy_defaults_to_css(self):
        """Test that unknown strategy defaults to CSS with warning."""
        parser = LocatorParser()
        strategy, value = parser.parse("unknown=#button")
        
        assert strategy == "css"
        assert value == "unknown=#button"
    
    def test_get_strategy(self):
        """Test extracting strategy from locator."""
        parser = LocatorParser()
        
        assert parser.get_strategy("css=#button") == "css"
        assert parser.get_strategy("xpath=//div") == "xpath"
        assert parser.get_strategy("#button") == "css"
    
    def test_get_value(self):
        """Test extracting value from locator."""
        parser = LocatorParser()
        
        assert parser.get_value("css=#button") == "#button"
        assert parser.get_value("xpath=//div") == "//div"
        assert parser.get_value("#button") == "#button"
    
    def test_validate_valid_locator(self):
        """Test validating a valid locator."""
        parser = LocatorParser()
        
        assert parser.validate("css=#button") is True
        assert parser.validate("xpath=//div") is True
        assert parser.validate("text=Click") is True
    
    def test_validate_invalid_locator(self):
        """Test validating an invalid locator."""
        parser = LocatorParser()
        
        assert parser.validate("") is False
        assert parser.validate("css=") is False


class TestLocatorConverter:
    """Test the LocatorConverter class."""
    
    def test_css_to_xpath_id_selector(self):
        """Test converting CSS ID selector to XPath."""
        converter = LocatorConverter()
        xpath = converter.css_to_xpath("#submit-button")
        
        assert xpath == "//*[@id='submit-button']"
    
    def test_css_to_xpath_class_selector(self):
        """Test converting CSS class selector to XPath."""
        converter = LocatorConverter()
        xpath = converter.css_to_xpath(".btn-primary")
        
        assert xpath == "//*[contains(@class, 'btn-primary')]"
    
    def test_css_to_xpath_tag_selector(self):
        """Test converting CSS tag selector to XPath."""
        converter = LocatorConverter()
        xpath = converter.css_to_xpath("button")
        
        assert xpath == "//button"

    def test_css_to_xpath_attribute_selector(self):
        """Test converting CSS attribute selector to XPath."""
        converter = LocatorConverter()
        xpath = converter.css_to_xpath("[name='username']")
        
        assert xpath == "//*[@name='username']"
    
    def test_css_to_xpath_tag_with_id(self):
        """Test converting CSS tag with ID to XPath."""
        converter = LocatorConverter()
        xpath = converter.css_to_xpath("div#container")
        
        assert xpath == "//div[@id='container']"
    
    def test_css_to_xpath_tag_with_class(self):
        """Test converting CSS tag with class to XPath."""
        converter = LocatorConverter()
        xpath = converter.css_to_xpath("button.btn-primary")
        
        assert xpath == "//button[contains(@class, 'btn-primary')]"
    
    def test_css_to_xpath_descendant_combinator(self):
        """Test converting CSS descendant combinator to XPath."""
        converter = LocatorConverter()
        xpath = converter.css_to_xpath("div .button")
        
        assert xpath == "//div//*[contains(@class, 'button')]"
    
    def test_css_to_xpath_child_combinator(self):
        """Test converting CSS child combinator to XPath."""
        converter = LocatorConverter()
        xpath = converter.css_to_xpath("div > .button")
        
        assert xpath == "//div/*[contains(@class, 'button')]"
    
    def test_css_to_xpath_empty_selector_raises_error(self):
        """Test that empty CSS selector raises ValueError."""
        converter = LocatorConverter()
        
        with pytest.raises(ValueError, match="CSS selector cannot be empty"):
            converter.css_to_xpath("")
    
    def test_id_to_css(self):
        """Test converting ID to CSS selector."""
        converter = LocatorConverter()
        css = converter.id_to_css("submit-button")
        
        assert css == "#submit-button"
    
    def test_id_to_xpath(self):
        """Test converting ID to XPath."""
        converter = LocatorConverter()
        xpath = converter.id_to_xpath("submit-button")
        
        assert xpath == "//*[@id='submit-button']"
    
    def test_class_to_css(self):
        """Test converting class to CSS selector."""
        converter = LocatorConverter()
        css = converter.class_to_css("btn-primary")
        
        assert css == ".btn-primary"
    
    def test_class_to_xpath(self):
        """Test converting class to XPath."""
        converter = LocatorConverter()
        xpath = converter.class_to_xpath("btn-primary")
        
        assert xpath == "//*[contains(@class, 'btn-primary')]"
    
    def test_convert_css_to_xpath(self):
        """Test converting locator string from CSS to XPath."""
        converter = LocatorConverter()
        result = converter.convert("css=#button", "xpath")
        
        assert result == "xpath=//*[@id='button']"
    
    def test_convert_id_to_css(self):
        """Test converting locator string from ID to CSS."""
        converter = LocatorConverter()
        result = converter.convert("id=submit", "css")
        
        assert result == "css=#submit"
    
    def test_convert_id_to_xpath(self):
        """Test converting locator string from ID to XPath."""
        converter = LocatorConverter()
        result = converter.convert("id=submit", "xpath")
        
        assert result == "xpath=//*[@id='submit']"
    
    def test_convert_same_strategy_returns_original(self):
        """Test that converting to same strategy returns original."""
        converter = LocatorConverter()
        result = converter.convert("css=#button", "css")
        
        assert result == "css=#button"
    
    def test_convert_unsupported_conversion_raises_error(self):
        """Test that unsupported conversion raises ValueError."""
        converter = LocatorConverter()
        
        with pytest.raises(ValueError, match="not supported"):
            converter.convert("text=Click", "xpath")


class TestLocatorValidator:
    """Test the LocatorValidator class."""
    
    def test_is_valid_with_valid_locator(self):
        """Test validating a valid locator."""
        validator = LocatorValidator()
        
        assert validator.is_valid("css=#button") is True
        assert validator.is_valid("xpath=//div") is True
        assert validator.is_valid("text=Click") is True
    
    def test_is_valid_with_invalid_locator(self):
        """Test validating an invalid locator."""
        validator = LocatorValidator()
        
        assert validator.is_valid("") is False
        assert validator.is_valid("css=") is False
    
    def test_validate_css_valid_selector(self):
        """Test validating a valid CSS selector."""
        validator = LocatorValidator()
        is_valid, error = validator.validate_css("#button")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_css_empty_selector(self):
        """Test validating an empty CSS selector."""
        validator = LocatorValidator()
        is_valid, error = validator.validate_css("")
        
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_validate_css_invalid_start_character(self):
        """Test validating CSS selector with invalid start character."""
        validator = LocatorValidator()
        is_valid, error = validator.validate_css("=button")
        
        assert is_valid is False
        assert "cannot start with" in error.lower()
    
    def test_validate_css_unmatched_brackets(self):
        """Test validating CSS selector with unmatched brackets."""
        validator = LocatorValidator()
        is_valid, error = validator.validate_css("[name='test'")
        
        assert is_valid is False
        assert "unmatched" in error.lower()
    
    def test_validate_xpath_valid_expression(self):
        """Test validating a valid XPath expression."""
        validator = LocatorValidator()
        is_valid, error = validator.validate_xpath("//button[@id='submit']")
        
        assert is_valid is True
        assert error is None
    
    def test_validate_xpath_empty_expression(self):
        """Test validating an empty XPath expression."""
        validator = LocatorValidator()
        is_valid, error = validator.validate_xpath("")
        
        assert is_valid is False
        assert "empty" in error.lower()
    
    def test_validate_xpath_invalid_start(self):
        """Test validating XPath expression with invalid start."""
        validator = LocatorValidator()
        is_valid, error = validator.validate_xpath("button")
        
        assert is_valid is False
        assert "should start with" in error.lower()
    
    def test_validate_xpath_unmatched_quotes(self):
        """Test validating XPath expression with unmatched quotes."""
        validator = LocatorValidator()
        is_valid, error = validator.validate_xpath("//button[@id='submit]")
        
        assert is_valid is False
        assert "unmatched" in error.lower()
    
    def test_get_validation_errors_valid_locator(self):
        """Test getting validation errors for valid locator."""
        validator = LocatorValidator()
        errors = validator.get_validation_errors("css=#button")
        
        assert len(errors) == 0
    
    def test_get_validation_errors_invalid_locator(self):
        """Test getting validation errors for invalid locator."""
        validator = LocatorValidator()
        errors = validator.get_validation_errors("css=")
        
        assert len(errors) > 0
        assert any("empty" in error.lower() for error in errors)


class TestLocatorGenerator:
    """Test the LocatorGenerator class."""
    
    def test_by_id_css(self):
        """Test generating CSS locator by ID."""
        generator = LocatorGenerator()
        locator = generator.by_id("submit-button")
        
        assert locator == "css=#submit-button"
    
    def test_by_id_xpath(self):
        """Test generating XPath locator by ID."""
        generator = LocatorGenerator()
        locator = generator.by_id("submit-button", use_xpath=True)
        
        assert locator == "xpath=//*[@id='submit-button']"
    
    def test_by_id_empty_raises_error(self):
        """Test that empty ID raises ValueError."""
        generator = LocatorGenerator()
        
        with pytest.raises(ValueError, match="ID value cannot be empty"):
            generator.by_id("")
    
    def test_by_class_css(self):
        """Test generating CSS locator by class."""
        generator = LocatorGenerator()
        locator = generator.by_class("btn-primary")
        
        assert locator == "css=.btn-primary"
    
    def test_by_class_xpath(self):
        """Test generating XPath locator by class."""
        generator = LocatorGenerator()
        locator = generator.by_class("btn-primary", use_xpath=True)
        
        assert locator == "xpath=//*[contains(@class, 'btn-primary')]"
    
    def test_by_text(self):
        """Test generating text locator."""
        generator = LocatorGenerator()
        locator = generator.by_text("Submit")
        
        assert locator == "text=Submit"
    
    def test_by_text_empty_raises_error(self):
        """Test that empty text raises ValueError."""
        generator = LocatorGenerator()
        
        with pytest.raises(ValueError, match="Text value cannot be empty"):
            generator.by_text("")
    
    def test_by_role_simple(self):
        """Test generating simple role locator."""
        generator = LocatorGenerator()
        locator = generator.by_role("button")
        
        assert locator == "role=button"
    
    def test_by_role_with_name(self):
        """Test generating role locator with name."""
        generator = LocatorGenerator()
        locator = generator.by_role("button", name="Submit")
        
        assert locator == "role=button[name='Submit']"
    
    def test_by_role_with_attributes(self):
        """Test generating role locator with attributes."""
        generator = LocatorGenerator()
        locator = generator.by_role("checkbox", name="Accept", checked=True)
        
        assert "role=checkbox" in locator
        assert "name='Accept'" in locator
        assert "checked='True'" in locator
    
    def test_by_attribute_css(self):
        """Test generating CSS locator by attribute."""
        generator = LocatorGenerator()
        locator = generator.by_attribute("name", "username")
        
        assert locator == "css=[name='username']"
    
    def test_by_attribute_with_tag_css(self):
        """Test generating CSS locator by attribute with tag."""
        generator = LocatorGenerator()
        locator = generator.by_attribute("data-testid", "submit-btn", tag="button")
        
        assert locator == "css=button[data-testid='submit-btn']"
    
    def test_by_attribute_xpath(self):
        """Test generating XPath locator by attribute."""
        generator = LocatorGenerator()
        locator = generator.by_attribute("href", "/login", use_xpath=True)
        
        assert locator == "xpath=//*[@href='/login']"
    
    def test_by_placeholder(self):
        """Test generating placeholder locator."""
        generator = LocatorGenerator()
        locator = generator.by_placeholder("Enter username")
        
        assert locator == "placeholder=Enter username"
    
    def test_by_label(self):
        """Test generating label locator."""
        generator = LocatorGenerator()
        locator = generator.by_label("Username")
        
        assert locator == "label=Username"
    
    def test_by_test_id_css(self):
        """Test generating CSS locator by test ID."""
        generator = LocatorGenerator()
        locator = generator.by_test_id("submit-button")
        
        assert locator == "css=[data-testid='submit-button']"
    
    def test_by_test_id_xpath(self):
        """Test generating XPath locator by test ID."""
        generator = LocatorGenerator()
        locator = generator.by_test_id("submit-button", use_xpath=True)
        
        assert locator == "xpath=//*[@data-testid='submit-button']"
    
    def test_combine_descendant(self):
        """Test combining locators with descendant combinator."""
        generator = LocatorGenerator()
        locator = generator.combine("#form", ".submit-button")
        
        assert locator == "css=#form .submit-button"
    
    def test_combine_child(self):
        """Test combining locators with child combinator."""
        generator = LocatorGenerator()
        locator = generator.combine("div", ".container", combinator=">")
        
        assert locator == "css=div > .container"
    
    def test_combine_empty_raises_error(self):
        """Test that combining with no locators raises ValueError."""
        generator = LocatorGenerator()
        
        with pytest.raises(ValueError, match="At least one locator"):
            generator.combine()
    
    def test_combine_invalid_combinator_raises_error(self):
        """Test that invalid combinator raises ValueError."""
        generator = LocatorGenerator()
        
        with pytest.raises(ValueError, match="Invalid combinator"):
            generator.combine("#form", ".button", combinator="*")


class TestConvenienceFunctions:
    """Test the convenience functions."""
    
    def test_parse_locator_function(self):
        """Test parse_locator convenience function."""
        strategy, value = parse_locator("css=#button")
        
        assert strategy == "css"
        assert value == "#button"
    
    def test_validate_locator_function(self):
        """Test validate_locator convenience function."""
        assert validate_locator("css=#button") is True
        assert validate_locator("") is False
    
    def test_convert_locator_function(self):
        """Test convert_locator convenience function."""
        result = convert_locator("css=#button", "xpath")
        
        assert result == "xpath=//*[@id='button']"


class TestLocatorStrategy:
    """Test the LocatorStrategy enum."""
    
    def test_locator_strategy_values(self):
        """Test that LocatorStrategy enum has expected values."""
        assert LocatorStrategy.CSS.value == "css"
        assert LocatorStrategy.XPATH.value == "xpath"
        assert LocatorStrategy.TEXT.value == "text"
        assert LocatorStrategy.ROLE.value == "role"
        assert LocatorStrategy.ID.value == "id"
