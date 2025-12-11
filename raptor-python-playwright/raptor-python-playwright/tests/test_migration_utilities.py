"""
Tests for Migration Utilities

Tests for Java to Python conversion, DDFE validation, compatibility checking,
and migration reporting.
"""

import pytest
from pathlib import Path

from raptor.migration import (
    JavaToPythonConverter,
    DDFEValidator,
    CompatibilityChecker,
    MigrationReporter
)
from raptor.migration.ddfe_validator import (
    ElementDefinition,
    ValidationSeverity,
    LocatorType
)
from raptor.migration.compatibility_checker import CompatibilityLevel


class TestJavaToPythonConverter:
    """Tests for JavaToPythonConverter"""
    
    def test_converter_initialization(self):
        """Test converter initializes correctly"""
        converter = JavaToPythonConverter()
        assert converter is not None
        assert converter.warnings == []
        assert converter.manual_review_needed == []
    
    def test_convert_simple_method(self):
        """Test converting a simple Java method"""
        converter = JavaToPythonConverter()
        java_code = """
        public void testClick() {
            click("css=#button");
        }
        """
        
        result = converter.convert_method(java_code)
        assert 'await element_manager.click(' in result
        assert 'async def' in result
    
    def test_convert_file_with_class(self):
        """Test converting a complete Java file"""
        converter = JavaToPythonConverter()
        java_code = """
        public class TestClass {
            public void testMethod() {
                click("css=#button");
                type("css=#input", "text");
            }
        }
        """
        
        result = converter.convert_file(java_code)
        assert result.python_code is not None
        assert 'class TestClass' in result.python_code
        assert 'import pytest' in result.python_code
    
    def test_method_mappings(self):
        """Test that method mappings are applied"""
        converter = JavaToPythonConverter()
        
        # Test click mapping
        assert 'click(' in converter.METHOD_MAPPINGS
        assert 'await element_manager.click(' in converter.METHOD_MAPPINGS['click(']
        
        # Test type mapping
        assert 'type(' in converter.METHOD_MAPPINGS
        
        # Test verify mapping
        assert 'verifyExists(' in converter.METHOD_MAPPINGS
    
    def test_type_mappings(self):
        """Test that type mappings are correct"""
        converter = JavaToPythonConverter()
        
        assert converter.TYPE_MAPPINGS['String'] == 'str'
        assert converter.TYPE_MAPPINGS['Integer'] == 'int'
        assert converter.TYPE_MAPPINGS['Boolean'] == 'bool'
        assert converter.TYPE_MAPPINGS['void'] == 'None'
    
    def test_conversion_stats(self):
        """Test that conversion stats are tracked"""
        converter = JavaToPythonConverter()
        java_code = """
        public class TestClass {
            public void testMethod() {
                click("css=#button");
            }
        }
        """
        
        result = converter.convert_file(java_code)
        assert result.conversion_stats['imports_added'] > 0


class TestDDFEValidator:
    """Tests for DDFEValidator"""
    
    def test_validator_initialization(self):
        """Test validator initializes correctly"""
        validator = DDFEValidator()
        assert validator is not None
        assert len(validator.VALID_FIELD_TYPES) > 0
        assert len(validator.REQUIRED_FIELDS) > 0
    
    def test_validate_valid_element(self):
        """Test validating a valid element"""
        validator = DDFEValidator()
        element = ElementDefinition(
            pv_name="test_button",
            application_name="TestApp",
            field_type="button",
            locator_primary="css=#button"
        )
        
        result = validator.validate_element(element)
        assert result.is_valid
        assert result.compatibility_score > 0.8
    
    def test_validate_missing_required_field(self):
        """Test validation fails for missing required field"""
        validator = DDFEValidator()
        element = ElementDefinition(
            pv_name="test_button",
            application_name="TestApp",
            field_type="",  # Missing
            locator_primary="css=#button"
        )
        
        result = validator.validate_element(element)
        assert not result.is_valid
        assert any(
            issue.severity == ValidationSeverity.ERROR
            for issue in result.issues
        )
    
    def test_validate_invalid_locator(self):
        """Test validation catches invalid locators"""
        validator = DDFEValidator()
        element = ElementDefinition(
            pv_name="test_button",
            application_name="TestApp",
            field_type="button",
            locator_primary=""  # Empty locator
        )
        
        result = validator.validate_element(element)
        assert not result.is_valid
    
    def test_detect_locator_type_css(self):
        """Test CSS locator detection"""
        validator = DDFEValidator()
        
        assert validator._detect_locator_type("css=#button") == LocatorType.CSS
        assert validator._detect_locator_type("#button") == LocatorType.ID
        assert validator._detect_locator_type(".button") == LocatorType.CLASS
    
    def test_detect_locator_type_xpath(self):
        """Test XPath locator detection"""
        validator = DDFEValidator()
        
        assert validator._detect_locator_type("xpath=//button") == LocatorType.XPATH
        assert validator._detect_locator_type("//button") == LocatorType.XPATH
    
    def test_validate_fallback_locators(self):
        """Test validation of fallback locators"""
        validator = DDFEValidator()
        element = ElementDefinition(
            pv_name="test_button",
            application_name="TestApp",
            field_type="button",
            locator_primary="css=#button",
            locator_fallback1="xpath=//button[@id='button']",
            locator_fallback2="id=button"
        )
        
        result = validator.validate_element(element)
        assert result.is_valid
    
    def test_validate_table_element(self):
        """Test validation of table elements"""
        validator = DDFEValidator()
        element = ElementDefinition(
            pv_name="test_table",
            application_name="TestApp",
            field_type="table",
            locator_primary="css=table.data",
            table_column=1,
            table_key=0
        )
        
        result = validator.validate_element(element)
        assert result.is_valid
    
    def test_validation_summary(self):
        """Test validation summary generation"""
        validator = DDFEValidator()
        elements = [
            ElementDefinition(
                pv_name="valid_element",
                application_name="TestApp",
                field_type="button",
                locator_primary="css=#button"
            ),
            ElementDefinition(
                pv_name="invalid_element",
                application_name="TestApp",
                field_type="",
                locator_primary="css=#button"
            ),
        ]
        
        results = validator.validate_elements(elements)
        summary = validator.get_validation_summary(results)
        
        assert 'Total Elements: 2' in summary
        assert 'Valid Elements: 1' in summary
        assert 'Invalid Elements: 1' in summary


class TestCompatibilityChecker:
    """Tests for CompatibilityChecker"""
    
    def test_checker_initialization(self):
        """Test checker initializes correctly"""
        checker = CompatibilityChecker()
        assert checker is not None
        assert len(checker.SUPPORTED_PATTERNS) > 0
        assert len(checker.NEEDS_MODIFICATION) > 0
    
    def test_check_fully_compatible_code(self):
        """Test checking fully compatible code"""
        checker = CompatibilityChecker()
        java_code = """
        public void testMethod() {
            click("css=#button");
            type("css=#input", "text");
            verifyExists("css=.message");
        }
        """
        
        result = checker.check_compatibility(java_code)
        assert result.is_compatible
        assert len(result.supported_features) > 0
    
    def test_check_code_needing_modification(self):
        """Test checking code that needs modification"""
        checker = CompatibilityChecker()
        java_code = """
        import org.openqa.selenium.WebDriver;
        
        public void testMethod() {
            WebDriver driver = new ChromeDriver();
            driver.get("https://example.com");
        }
        """
        
        result = checker.check_compatibility(java_code)
        assert len(result.issues) > 0
        assert any(
            issue.category == 'needs_modification'
            for issue in result.issues
        )
    
    def test_check_unsupported_code(self):
        """Test checking unsupported code"""
        checker = CompatibilityChecker()
        java_code = """
        import org.sikuli.script.Screen;
        
        public void testMethod() {
            Screen screen = new Screen();
            screen.click("image.png");
        }
        """
        
        result = checker.check_compatibility(java_code)
        assert not result.is_compatible
        assert len(result.unsupported_features) > 0
        assert result.compatibility_level == CompatibilityLevel.INCOMPATIBLE
    
    def test_supported_patterns_detection(self):
        """Test detection of supported patterns"""
        checker = CompatibilityChecker()
        java_code = """
        click("css=#button");
        type("css=#input", "text");
        waitForElement("css=.loading");
        """
        
        result = checker.check_compatibility(java_code)
        assert 'click' in result.supported_features
        assert 'type' in result.supported_features
        assert 'wait' in result.supported_features
    
    def test_migration_complexity_calculation(self):
        """Test migration complexity calculation"""
        checker = CompatibilityChecker()
        
        # Simple code
        simple_code = "click('css=#button');"
        result = checker.check_compatibility(simple_code)
        assert result.migration_complexity in ['simple', 'moderate']
        
        # Complex code with unsupported features
        complex_code = """
        import org.sikuli.script.Screen;
        Robot robot = new Robot();
        """
        result = checker.check_compatibility(complex_code)
        assert result.migration_complexity == 'complex'
    
    def test_effort_estimation(self):
        """Test effort estimation"""
        checker = CompatibilityChecker()
        java_code = """
        import org.openqa.selenium.WebDriver;
        WebDriver driver = new ChromeDriver();
        """
        
        result = checker.check_compatibility(java_code)
        assert result.estimated_effort_hours > 0
    
    def test_compatibility_summary(self):
        """Test compatibility summary generation"""
        checker = CompatibilityChecker()
        java_code = """
        click("css=#button");
        type("css=#input", "text");
        """
        
        result = checker.check_compatibility(java_code)
        summary = checker.get_compatibility_summary(result)
        
        assert 'Compatibility Level' in summary
        assert 'Supported Features' in summary
    
    def test_migration_checklist(self):
        """Test migration checklist generation"""
        checker = CompatibilityChecker()
        java_code = """
        import org.openqa.selenium.WebDriver;
        WebDriver driver = new ChromeDriver();
        """
        
        result = checker.check_compatibility(java_code)
        checklist = checker.generate_migration_checklist(result)
        
        assert len(checklist) > 0
        assert any('Migration Checklist' in item for item in checklist)


class TestMigrationReporter:
    """Tests for MigrationReporter"""
    
    def test_reporter_initialization(self):
        """Test reporter initializes correctly"""
        reporter = MigrationReporter(project_name="Test Project")
        assert reporter.project_name == "Test Project"
        assert reporter.timestamp is not None
    
    def test_generate_text_report(self):
        """Test generating text report"""
        reporter = MigrationReporter()
        report = reporter.generate_report(
            conversion_results=[],
            validation_results=[],
            compatibility_results=[],
            output_format='text'
        )
        
        assert 'SUMMARY' in report
        assert 'Conversion:' in report
        assert 'Validation:' in report
    
    def test_generate_json_report(self):
        """Test generating JSON report"""
        reporter = MigrationReporter()
        report = reporter.generate_report(
            conversion_results=[],
            validation_results=[],
            compatibility_results=[],
            output_format='json'
        )
        
        assert '{' in report
        assert 'timestamp' in report
        assert 'project_name' in report
    
    def test_generate_markdown_report(self):
        """Test generating Markdown report"""
        reporter = MigrationReporter()
        report = reporter.generate_report(
            conversion_results=[],
            validation_results=[],
            compatibility_results=[],
            output_format='markdown'
        )
        
        assert '# ' in report
        assert '## Summary' in report
        assert '### Conversion' in report
    
    def test_generate_html_report(self):
        """Test generating HTML report"""
        reporter = MigrationReporter()
        report = reporter.generate_report(
            conversion_results=[],
            validation_results=[],
            compatibility_results=[],
            output_format='html'
        )
        
        assert '<!DOCTYPE html>' in report
        assert '<html' in report
        assert '</html>' in report
    
    def test_save_report_to_file(self, tmp_path):
        """Test saving report to file"""
        reporter = MigrationReporter()
        output_path = tmp_path / "report.html"
        
        reporter.generate_report(
            conversion_results=[],
            validation_results=[],
            compatibility_results=[],
            output_format='html',
            output_path=output_path
        )
        
        assert output_path.exists()
        content = output_path.read_text()
        assert '<!DOCTYPE html>' in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
