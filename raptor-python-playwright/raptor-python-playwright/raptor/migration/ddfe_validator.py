"""
DDFE Element Definition Validator

Validates DDFE element definitions for compatibility with Python Playwright.
"""

import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


class LocatorType(Enum):
    """Supported locator types"""
    CSS = "css"
    XPATH = "xpath"
    ID = "id"
    TEXT = "text"
    ROLE = "role"
    NAME = "name"
    CLASS = "class"
    TAG = "tag"


class ValidationSeverity(Enum):
    """Validation issue severity"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue"""
    severity: ValidationSeverity
    field: str
    message: str
    suggestion: Optional[str] = None


@dataclass
class ElementDefinition:
    """DDFE Element Definition"""
    pv_name: str
    application_name: str
    field_type: str
    locator_primary: str
    locator_fallback1: Optional[str] = None
    locator_fallback2: Optional[str] = None
    frame: Optional[str] = None
    table_column: Optional[int] = None
    table_key: Optional[int] = None
    analyst: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of element definition validation"""
    is_valid: bool
    issues: List[ValidationIssue]
    element: ElementDefinition
    compatibility_score: float  # 0.0 to 1.0


class DDFEValidator:
    """
    Validates DDFE element definitions for Playwright compatibility.
    
    Checks:
    - Locator syntax and compatibility
    - Required fields presence
    - Field type validity
    - Fallback locator configuration
    - Playwright-specific requirements
    """
    
    VALID_FIELD_TYPES = {
        'button', 'textbox', 'link', 'dropdown', 'checkbox', 'radio',
        'table', 'label', 'image', 'div', 'span', 'input', 'textarea',
        'select', 'iframe', 'frame', 'dialog', 'menu', 'tab'
    }
    
    REQUIRED_FIELDS = {'pv_name', 'application_name', 'field_type', 'locator_primary'}
    
    def __init__(self):
        """Initialize the validator"""
        self.validation_issues = []
    
    def validate_element(self, element: ElementDefinition) -> ValidationResult:
        """
        Validate a single element definition.
        
        Args:
            element: ElementDefinition to validate
            
        Returns:
            ValidationResult with validation details
        """
        self.validation_issues = []
        
        # Validate required fields
        self._validate_required_fields(element)
        
        # Validate field type
        self._validate_field_type(element)
        
        # Validate primary locator
        self._validate_locator(element.locator_primary, 'locator_primary', is_primary=True)
        
        # Validate fallback locators
        if element.locator_fallback1:
            self._validate_locator(element.locator_fallback1, 'locator_fallback1')
        
        if element.locator_fallback2:
            self._validate_locator(element.locator_fallback2, 'locator_fallback2')
        
        # Validate table-specific fields
        if element.field_type == 'table':
            self._validate_table_fields(element)
        
        # Validate frame context
        if element.frame:
            self._validate_frame(element)
        
        # Calculate compatibility score
        compatibility_score = self._calculate_compatibility_score()
        
        # Determine if valid (no errors)
        is_valid = not any(
            issue.severity == ValidationSeverity.ERROR
            for issue in self.validation_issues
        )
        
        return ValidationResult(
            is_valid=is_valid,
            issues=self.validation_issues.copy(),
            element=element,
            compatibility_score=compatibility_score
        )
    
    def validate_elements(
        self,
        elements: List[ElementDefinition]
    ) -> List[ValidationResult]:
        """
        Validate multiple element definitions.
        
        Args:
            elements: List of ElementDefinitions to validate
            
        Returns:
            List of ValidationResults
        """
        results = []
        for element in elements:
            result = self.validate_element(element)
            results.append(result)
        
        return results
    
    def _validate_required_fields(self, element: ElementDefinition):
        """Validate that all required fields are present"""
        for field in self.REQUIRED_FIELDS:
            value = getattr(element, field, None)
            if not value or (isinstance(value, str) and not value.strip()):
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field=field,
                    message=f"Required field '{field}' is missing or empty",
                    suggestion=f"Provide a valid value for '{field}'"
                ))
    
    def _validate_field_type(self, element: ElementDefinition):
        """Validate field type"""
        if element.field_type.lower() not in self.VALID_FIELD_TYPES:
            self.validation_issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                field='field_type',
                message=f"Field type '{element.field_type}' is not in standard list",
                suggestion=f"Consider using one of: {', '.join(sorted(self.VALID_FIELD_TYPES))}"
            ))
    
    def _validate_locator(
        self,
        locator: str,
        field_name: str,
        is_primary: bool = False
    ):
        """Validate a locator string"""
        if not locator or not locator.strip():
            if is_primary:
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field=field_name,
                    message="Primary locator cannot be empty"
                ))
            return
        
        # Detect locator type
        locator_type = self._detect_locator_type(locator)
        
        if not locator_type:
            self.validation_issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                field=field_name,
                message=f"Unable to determine locator type for: {locator}",
                suggestion="Use format: 'css=selector', 'xpath=//path', 'id=elementId', etc."
            ))
            return
        
        # Validate locator syntax
        self._validate_locator_syntax(locator, locator_type, field_name)
        
        # Check Playwright compatibility
        self._check_playwright_compatibility(locator, locator_type, field_name)
    
    def _detect_locator_type(self, locator: str) -> Optional[LocatorType]:
        """Detect the type of locator"""
        locator = locator.strip()
        
        # Check for explicit type prefix
        if locator.startswith('css='):
            return LocatorType.CSS
        elif locator.startswith('xpath=') or locator.startswith('//') or locator.startswith('(//'):
            return LocatorType.XPATH
        elif locator.startswith('id='):
            return LocatorType.ID
        elif locator.startswith('text='):
            return LocatorType.TEXT
        elif locator.startswith('role='):
            return LocatorType.ROLE
        elif locator.startswith('name='):
            return LocatorType.NAME
        elif locator.startswith('class='):
            return LocatorType.CLASS
        elif locator.startswith('tag='):
            return LocatorType.TAG
        
        # Try to infer type
        if locator.startswith('#'):
            return LocatorType.ID
        elif locator.startswith('.'):
            return LocatorType.CLASS
        elif locator.startswith('//') or locator.startswith('(//'):
            return LocatorType.XPATH
        elif re.match(r'^[a-zA-Z][a-zA-Z0-9]*$', locator):
            return LocatorType.TAG
        
        # Default to CSS if it looks like a CSS selector
        if any(char in locator for char in ['>', '+', '~', '[', ']', ':', ' ']):
            return LocatorType.CSS
        
        return None
    
    def _validate_locator_syntax(
        self,
        locator: str,
        locator_type: LocatorType,
        field_name: str
    ):
        """Validate locator syntax based on type"""
        # Remove type prefix if present
        clean_locator = re.sub(r'^(css|xpath|id|text|role|name|class|tag)=', '', locator)
        
        if locator_type == LocatorType.XPATH:
            # Basic XPath validation
            if not (clean_locator.startswith('//') or clean_locator.startswith('(//') or clean_locator.startswith('/')):
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    field=field_name,
                    message=f"XPath locator should start with '/' or '//': {locator}",
                    suggestion="Ensure XPath is valid and starts with '/' or '//'"
                ))
            
            # Check for common XPath issues
            if 'contains(@class' in clean_locator and not 'normalize-space' in clean_locator:
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    field=field_name,
                    message="Consider using normalize-space() for class matching",
                    suggestion="Use: contains(normalize-space(@class), 'classname')"
                ))
        
        elif locator_type == LocatorType.CSS:
            # Check for Selenium-specific CSS that won't work in Playwright
            if ':contains(' in clean_locator:
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field=field_name,
                    message=":contains() is not supported in Playwright CSS selectors",
                    suggestion="Use text= locator or XPath instead"
                ))
        
        elif locator_type == LocatorType.ID:
            # Validate ID format
            if not re.match(r'^[a-zA-Z][\w\-:\.]*$', clean_locator):
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    field=field_name,
                    message=f"ID contains unusual characters: {clean_locator}",
                    suggestion="Verify the ID is correct"
                ))
    
    def _check_playwright_compatibility(
        self,
        locator: str,
        locator_type: LocatorType,
        field_name: str
    ):
        """Check for Playwright-specific compatibility issues"""
        # Check for Selenium-specific patterns
        selenium_patterns = [
            (r'By\.', 'Selenium By. syntax not needed in Playwright'),
            (r'driver\.findElement', 'Use Playwright locator methods instead'),
            (r'WebElement', 'Use Playwright Locator instead'),
        ]
        
        for pattern, message in selenium_patterns:
            if re.search(pattern, locator):
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    field=field_name,
                    message=message,
                    suggestion="Convert to Playwright locator syntax"
                ))
    
    def _validate_table_fields(self, element: ElementDefinition):
        """Validate table-specific fields"""
        if element.table_column is None:
            self.validation_issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                field='table_column',
                message="Table element should have table_column defined",
                suggestion="Specify the column index for table operations"
            ))
        
        if element.table_key is None:
            self.validation_issues.append(ValidationIssue(
                severity=ValidationSeverity.INFO,
                field='table_key',
                message="Consider defining table_key for row identification",
                suggestion="Specify the key column index for finding rows"
            ))
    
    def _validate_frame(self, element: ElementDefinition):
        """Validate frame context"""
        if element.frame:
            # Check if frame locator is valid
            if not element.frame.strip():
                self.validation_issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    field='frame',
                    message="Frame field is empty",
                    suggestion="Remove frame field or provide valid frame locator"
                ))
    
    def _calculate_compatibility_score(self) -> float:
        """Calculate compatibility score based on issues"""
        if not self.validation_issues:
            return 1.0
        
        # Weight by severity
        error_weight = 0.3
        warning_weight = 0.1
        info_weight = 0.05
        
        total_deduction = 0.0
        for issue in self.validation_issues:
            if issue.severity == ValidationSeverity.ERROR:
                total_deduction += error_weight
            elif issue.severity == ValidationSeverity.WARNING:
                total_deduction += warning_weight
            elif issue.severity == ValidationSeverity.INFO:
                total_deduction += info_weight
        
        score = max(0.0, 1.0 - total_deduction)
        return round(score, 2)
    
    def get_validation_summary(self, results: List[ValidationResult]) -> str:
        """Get a summary of validation results"""
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        invalid = total - valid
        
        total_errors = sum(
            sum(1 for issue in r.issues if issue.severity == ValidationSeverity.ERROR)
            for r in results
        )
        total_warnings = sum(
            sum(1 for issue in r.issues if issue.severity == ValidationSeverity.WARNING)
            for r in results
        )
        total_info = sum(
            sum(1 for issue in r.issues if issue.severity == ValidationSeverity.INFO)
            for r in results
        )
        
        avg_score = sum(r.compatibility_score for r in results) / total if total > 0 else 0.0
        
        summary = f"""
DDFE Validation Summary:
========================
Total Elements: {total}
Valid Elements: {valid}
Invalid Elements: {invalid}

Issues:
  Errors: {total_errors}
  Warnings: {total_warnings}
  Info: {total_info}

Average Compatibility Score: {avg_score:.2f}

Elements by Score:
  Excellent (0.9-1.0): {sum(1 for r in results if r.compatibility_score >= 0.9)}
  Good (0.7-0.89): {sum(1 for r in results if 0.7 <= r.compatibility_score < 0.9)}
  Fair (0.5-0.69): {sum(1 for r in results if 0.5 <= r.compatibility_score < 0.7)}
  Poor (<0.5): {sum(1 for r in results if r.compatibility_score < 0.5)}
"""
        
        return summary
