"""
Tests for Code Generation Tools

Tests the page object generator, test template generator,
locator suggester, and code formatter.
"""

import pytest
from pathlib import Path
from raptor.codegen.page_object_generator import (
    PageObjectGenerator,
    ElementDefinition,
    GeneratedPageObject
)
from raptor.codegen.test_template_generator import (
    TestTemplateGenerator,
    TestScenario,
    TestType
)
from raptor.codegen.locator_suggester import (
    LocatorSuggester,
    ElementInfo,
    LocatorStrategy,
    LocatorPriority
)
from raptor.codegen.code_formatter import (
    CodeFormatter,
    FormatterConfig,
    FormatterType
)


class TestPageObjectGenerator:
    """Tests for PageObjectGenerator"""
    
    def test_generate_class_name(self):
        """Test class name generation"""
        generator = PageObjectGenerator()
        
        assert generator._generate_class_name("Login") == "LoginPage"
        assert generator._generate_class_name("User Management") == "UserManagementPage"
        assert generator._generate_class_name("home-page") == "HomePage"
        assert generator._generate_class_name("LoginPage") == "LoginPage"
    
    def test_generate_file_name(self):
        """Test file name generation"""
        generator = PageObjectGenerator()
        
        assert generator._generate_file_name("Login") == "login_page.py"
        assert generator._generate_file_name("User Management") == "user_management_page.py"
        assert generator._generate_file_name("HomePage") == "home_page.py"
    
    def test_generate_method_name(self):
        """Test method name generation"""
        generator = PageObjectGenerator()
        
        assert generator._generate_method_name("LoginButton") == "login_button"
        assert generator._generate_method_name("user_name_field") == "user_name_field"
        assert generator._generate_method_name("Submit-Form") == "submit_form"
    
    def test_generate_page_object_basic(self):
        """Test basic page object generation"""
        generator = PageObjectGenerator()
        
        elements = [
            ElementDefinition(
                pv_name="LoginButton",
                application_name="Login",
                field_type="button",
                locator_primary="css=#login-btn"
            )
        ]
        
        result = generator.generate_page_object("Login", elements)
        
        assert isinstance(result, GeneratedPageObject)
        assert result.class_name == "LoginPage"
        assert result.file_name == "login_page.py"
        assert "class LoginPage(BasePage):" in result.code
        assert "async def get_login_button_locator" in result.code
        assert "async def click_login_button" in result.code
    
    def test_generate_page_object_with_fallbacks(self):
        """Test page object generation with fallback locators"""
        generator = PageObjectGenerator()
        
        elements = [
            ElementDefinition(
                pv_name="SubmitButton",
                application_name="Form",
                field_type="button",
                locator_primary="css=#submit",
                locator_fallback1="xpath=//button[@type='submit']",
                locator_fallback2="text=Submit"
            )
        ]
        
        result = generator.generate_page_object("Form", elements)
        
        assert 'fallback_locators=' in result.code
        assert 'xpath=//button[@type=\'submit\']' in result.code
    
    def test_generate_page_object_input_field(self):
        """Test page object generation for input fields"""
        generator = PageObjectGenerator()
        
        elements = [
            ElementDefinition(
                pv_name="UsernameField",
                application_name="Login",
                field_type="textbox",
                locator_primary="css=#username"
            )
        ]
        
        result = generator.generate_page_object("Login", elements)
        
        assert "async def fill_username_field" in result.code
        assert "async def get_username_field_value" in result.code
    
    def test_generate_page_object_table(self):
        """Test page object generation for tables"""
        generator = PageObjectGenerator()
        
        elements = [
            ElementDefinition(
                pv_name="UsersTable",
                application_name="Admin",
                field_type="table",
                locator_primary="css=#users-table",
                table_column=2,
                table_key=0
            )
        ]
        
        result = generator.generate_page_object("Admin", elements)
        
        assert "async def find_users_table_row" in result.code
        assert "async def get_users_table_cell_value" in result.code
        assert "TableManager" in result.code


class TestTestTemplateGenerator:
    """Tests for TestTemplateGenerator"""
    
    def test_generate_test_file_basic(self):
        """Test basic test file generation"""
        generator = TestTemplateGenerator()
        
        scenario = TestScenario(
            name="verify_login_success",
            description="Verify successful login",
            test_type=TestType.FUNCTIONAL,
            page_object="LoginPage",
            steps=["Enter username", "Enter password", "Click login"],
            assertions=["User is logged in", "Dashboard is visible"]
        )
        
        result = generator.generate_test_file("LoginPage", [scenario])
        
        assert result.file_name == "test_login_page.py"
        assert "async def test_verify_login_success" in result.code
        assert "@pytest.mark.asyncio" in result.code
        assert "# Arrange" in result.code
        assert "# Act" in result.code
        assert "# Assert" in result.code
    
    def test_generate_test_with_tags(self):
        """Test test generation with tags"""
        generator = TestTemplateGenerator()
        
        scenario = TestScenario(
            name="smoke_test",
            description="Smoke test",
            test_type=TestType.SMOKE,
            page_object="HomePage",
            steps=["Load page"],
            assertions=["Page loads"],
            tags=["smoke", "critical"]
        )
        
        result = generator.generate_test_file("HomePage", [scenario])
        
        assert "@pytest.mark.smoke" in result.code
        assert "@pytest.mark.critical" in result.code
    
    def test_generate_fixtures(self):
        """Test fixture generation"""
        generator = TestTemplateGenerator()
        
        scenario = TestScenario(
            name="test_example",
            description="Example test",
            test_type=TestType.FUNCTIONAL,
            page_object="TestPage",
            steps=["Step 1"],
            assertions=["Assert 1"]
        )
        
        result = generator.generate_test_file("TestPage", [scenario], include_fixtures=True)
        
        assert "@pytest.fixture" in result.code
        assert "async def browser():" in result.code
        assert "async def page(browser):" in result.code
    
    def test_class_to_snake_case(self):
        """Test class name to snake_case conversion"""
        generator = TestTemplateGenerator()
        
        assert generator._class_to_snake_case("LoginPage") == "login_page"
        assert generator._class_to_snake_case("UserManagementPage") == "user_management_page"
        assert generator._class_to_snake_case("HomePage") == "home_page"


class TestLocatorSuggester:
    """Tests for LocatorSuggester"""
    
    def test_suggest_role_locator(self):
        """Test role-based locator suggestion"""
        suggester = LocatorSuggester()
        
        element_info = ElementInfo(
            tag_name="button",
            role="button",
            text="Submit",
            aria_label="Submit Form"
        )
        
        suggestions = suggester.suggest_locators(element_info)
        
        assert len(suggestions) > 0
        assert suggestions[0].strategy == LocatorStrategy.ROLE
        assert suggestions[0].priority == LocatorPriority.EXCELLENT
        assert "get_by_role" in suggestions[0].playwright_syntax
    
    def test_suggest_test_id_locator(self):
        """Test test-id locator suggestion"""
        suggester = LocatorSuggester()
        
        element_info = ElementInfo(
            tag_name="button",
            test_id="submit-button"
        )
        
        suggestions = suggester.suggest_locators(element_info)
        
        # Test ID should be high priority
        test_id_suggestions = [s for s in suggestions if s.strategy == LocatorStrategy.TEST_ID]
        assert len(test_id_suggestions) > 0
        assert test_id_suggestions[0].priority == LocatorPriority.EXCELLENT
    
    def test_suggest_id_locator(self):
        """Test ID-based locator suggestion"""
        suggester = LocatorSuggester()
        
        element_info = ElementInfo(
            tag_name="input",
            id="username"
        )
        
        suggestions = suggester.suggest_locators(element_info)
        
        id_suggestions = [s for s in suggestions if s.strategy == LocatorStrategy.ID]
        assert len(id_suggestions) > 0
        assert id_suggestions[0].priority in [LocatorPriority.GOOD, LocatorPriority.EXCELLENT]
    
    def test_suggest_text_locator(self):
        """Test text-based locator suggestion"""
        suggester = LocatorSuggester()
        
        element_info = ElementInfo(
            tag_name="button",
            text="Click Me"
        )
        
        suggestions = suggester.suggest_locators(element_info)
        
        text_suggestions = [s for s in suggestions if s.strategy == LocatorStrategy.TEXT]
        assert len(text_suggestions) > 0
        assert "get_by_text" in text_suggestions[0].playwright_syntax
    
    def test_infer_role_from_tag(self):
        """Test role inference from HTML tag"""
        suggester = LocatorSuggester()
        
        # Button
        assert suggester._infer_role(ElementInfo(tag_name="button")) == "button"
        
        # Link
        assert suggester._infer_role(ElementInfo(tag_name="a")) == "link"
        
        # Input with type
        assert suggester._infer_role(
            ElementInfo(tag_name="input", type="checkbox")
        ) == "checkbox"
    
    def test_looks_auto_generated(self):
        """Test auto-generated ID detection"""
        suggester = LocatorSuggester()
        
        # Auto-generated patterns
        assert suggester._looks_auto_generated("abc123def456789012") == True
        assert suggester._looks_auto_generated("12345678901234") == True
        assert suggester._looks_auto_generated("ember12345") == True
        
        # Normal IDs
        assert suggester._looks_auto_generated("username") == False
        assert suggester._looks_auto_generated("submit-button") == False
    
    def test_generate_locator_report(self):
        """Test locator report generation"""
        suggester = LocatorSuggester()
        
        element_info = ElementInfo(
            tag_name="button",
            id="submit",
            text="Submit"
        )
        
        suggestions = suggester.suggest_locators(element_info)
        report = suggester.generate_locator_report(suggestions)
        
        assert "Locator Suggestions" in report
        assert "Priority:" in report
        assert "Confidence:" in report


class TestCodeFormatter:
    """Tests for CodeFormatter"""
    
    def test_format_code_basic(self):
        """Test basic code formatting"""
        formatter = CodeFormatter()
        
        unformatted_code = """
def hello(  ):
    print(  "Hello"  )
"""
        
        result = formatter.format_code(unformatted_code)
        
        # Should succeed even if formatter not available
        assert result.formatted_code is not None
    
    def test_format_code_with_imports(self):
        """Test code formatting with import sorting"""
        formatter = CodeFormatter()
        
        code_with_imports = """
import os
import sys
from pathlib import Path
import asyncio
"""
        
        result = formatter.format_code(code_with_imports, sort_imports=True)
        
        assert result.formatted_code is not None
    
    def test_formatter_config(self):
        """Test formatter configuration"""
        config = FormatterConfig(
            formatter_type=FormatterType.BLACK,
            line_length=100,
            skip_string_normalization=True
        )
        
        formatter = CodeFormatter(config)
        
        assert formatter.config.line_length == 100
        assert formatter.config.skip_string_normalization == True
    
    def test_get_available_formatters(self):
        """Test getting available formatters"""
        formatter = CodeFormatter()
        
        available = formatter.get_available_formatters()
        
        # Should return a list (may be empty if no formatters installed)
        assert isinstance(available, list)
    
    def test_is_formatter_available(self):
        """Test checking formatter availability"""
        formatter = CodeFormatter()
        
        # Check each formatter type
        for formatter_type in FormatterType:
            result = formatter.is_formatter_available(formatter_type)
            assert isinstance(result, bool)


# Integration tests
class TestCodegenIntegration:
    """Integration tests for code generation tools"""
    
    def test_generate_and_format_page_object(self):
        """Test generating and formatting a page object"""
        # Generate page object
        generator = PageObjectGenerator()
        
        elements = [
            ElementDefinition(
                pv_name="LoginButton",
                application_name="Login",
                field_type="button",
                locator_primary="css=#login"
            )
        ]
        
        page_object = generator.generate_page_object("Login", elements)
        
        # Format the generated code
        formatter = CodeFormatter()
        result = formatter.format_code(page_object.code)
        
        assert result.formatted_code is not None
        assert "class LoginPage" in result.formatted_code
    
    def test_suggest_locators_and_generate_page_object(self):
        """Test suggesting locators and using them in page object generation"""
        # Suggest locators
        suggester = LocatorSuggester()
        
        element_info = ElementInfo(
            tag_name="button",
            id="submit",
            role="button",
            text="Submit"
        )
        
        suggestions = suggester.suggest_locators(element_info, max_suggestions=3)
        
        # Use best suggestion in page object
        best_locator = suggestions[0].locator
        
        element = ElementDefinition(
            pv_name="SubmitButton",
            application_name="Form",
            field_type="button",
            locator_primary=best_locator
        )
        
        generator = PageObjectGenerator()
        page_object = generator.generate_page_object("Form", [element])
        
        assert best_locator in page_object.code
