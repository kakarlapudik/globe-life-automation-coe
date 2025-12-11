"""
Compatibility Checker for Java Tests

Checks Java test compatibility with Python Playwright framework.
"""

import re
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from enum import Enum


class CompatibilityLevel(Enum):
    """Compatibility levels"""
    FULLY_COMPATIBLE = "fully_compatible"
    MOSTLY_COMPATIBLE = "mostly_compatible"
    PARTIALLY_COMPATIBLE = "partially_compatible"
    INCOMPATIBLE = "incompatible"


@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue"""
    category: str
    severity: str  # 'critical', 'major', 'minor'
    description: str
    java_pattern: str
    python_alternative: Optional[str] = None
    migration_effort: str = "low"  # 'low', 'medium', 'high'


@dataclass
class CompatibilityCheckResult:
    """Result of compatibility check"""
    is_compatible: bool
    compatibility_level: CompatibilityLevel
    issues: List[CompatibilityIssue]
    supported_features: List[str]
    unsupported_features: List[str]
    migration_complexity: str  # 'simple', 'moderate', 'complex'
    estimated_effort_hours: float


class CompatibilityChecker:
    """
    Checks Java test compatibility with Python Playwright framework.
    
    Analyzes Java test code to identify:
    - Supported features
    - Unsupported features
    - Required modifications
    - Migration complexity
    - Estimated effort
    """
    
    # Patterns that are fully supported
    SUPPORTED_PATTERNS = {
        'click': r'click\(',
        'type': r'type\(|sendKeys\(',
        'select': r'selectOption\(',
        'wait': r'waitFor',
        'verify': r'verify',
        'navigate': r'navigate\(|\.get\(',
        'screenshot': r'takeScreenshot\(',
        'table': r'findRowByKey\(|getCellValue\(',
        'database': r'databaseImport\(|databaseExport\(',
    }
    
    # Patterns that need modification
    NEEDS_MODIFICATION = {
        'selenium_imports': {
            'pattern': r'import\s+org\.openqa\.selenium',
            'severity': 'major',
            'alternative': 'from playwright.async_api import Page, Browser',
            'effort': 'low'
        },
        'webdriver': {
            'pattern': r'WebDriver|driver\.',
            'severity': 'major',
            'alternative': 'Use Playwright Page object',
            'effort': 'medium'
        },
        'webelement': {
            'pattern': r'WebElement',
            'severity': 'major',
            'alternative': 'Use Playwright Locator',
            'effort': 'medium'
        },
        'explicit_wait': {
            'pattern': r'WebDriverWait|ExpectedConditions',
            'severity': 'minor',
            'alternative': 'Use Playwright auto-waiting',
            'effort': 'low'
        },
        'actions_class': {
            'pattern': r'Actions\s+actions\s*=',
            'severity': 'minor',
            'alternative': 'Use Playwright hover/click methods',
            'effort': 'low'
        },
        'javascript_executor': {
            'pattern': r'JavascriptExecutor|executeScript',
            'severity': 'minor',
            'alternative': 'page.evaluate()',
            'effort': 'low'
        },
        'select_class': {
            'pattern': r'Select\s+select\s*=',
            'severity': 'minor',
            'alternative': 'element_manager.select_option()',
            'effort': 'low'
        },
    }
    
    # Patterns that are not supported
    UNSUPPORTED_PATTERNS = {
        'robot_class': {
            'pattern': r'Robot\s+robot\s*=|java\.awt\.Robot',
            'severity': 'critical',
            'alternative': 'Use Playwright keyboard/mouse methods or OS-level automation',
            'effort': 'high'
        },
        'sikuli': {
            'pattern': r'import\s+org\.sikuli|Screen\s+screen',
            'severity': 'critical',
            'alternative': 'Use Playwright or consider image-based testing tools',
            'effort': 'high'
        },
        'appium': {
            'pattern': r'import\s+io\.appium|AppiumDriver',
            'severity': 'critical',
            'alternative': 'Playwright does not support mobile apps',
            'effort': 'high'
        },
    }
    
    def __init__(self):
        """Initialize the compatibility checker"""
        self.issues = []
        self.supported_features = []
        self.unsupported_features = []
    
    def check_compatibility(self, java_code: str) -> CompatibilityCheckResult:
        """
        Check compatibility of Java test code.
        
        Args:
            java_code: Java source code as string
            
        Returns:
            CompatibilityCheckResult with detailed analysis
        """
        self.issues = []
        self.supported_features = []
        self.unsupported_features = []
        
        # Check for supported patterns
        self._check_supported_patterns(java_code)
        
        # Check for patterns needing modification
        self._check_modification_patterns(java_code)
        
        # Check for unsupported patterns
        self._check_unsupported_patterns(java_code)
        
        # Determine compatibility level
        compatibility_level = self._determine_compatibility_level()
        
        # Calculate migration complexity
        migration_complexity = self._calculate_migration_complexity()
        
        # Estimate effort
        estimated_effort = self._estimate_effort()
        
        # Determine if compatible
        is_compatible = compatibility_level in [
            CompatibilityLevel.FULLY_COMPATIBLE,
            CompatibilityLevel.MOSTLY_COMPATIBLE
        ]
        
        return CompatibilityCheckResult(
            is_compatible=is_compatible,
            compatibility_level=compatibility_level,
            issues=self.issues,
            supported_features=self.supported_features,
            unsupported_features=self.unsupported_features,
            migration_complexity=migration_complexity,
            estimated_effort_hours=estimated_effort
        )
    
    def check_file_compatibility(self, file_path: str) -> CompatibilityCheckResult:
        """
        Check compatibility of a Java test file.
        
        Args:
            file_path: Path to Java file
            
        Returns:
            CompatibilityCheckResult
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            java_code = f.read()
        
        return self.check_compatibility(java_code)
    
    def _check_supported_patterns(self, java_code: str):
        """Check for supported patterns"""
        for feature, pattern in self.SUPPORTED_PATTERNS.items():
            if re.search(pattern, java_code, re.IGNORECASE):
                self.supported_features.append(feature)
    
    def _check_modification_patterns(self, java_code: str):
        """Check for patterns that need modification"""
        for name, config in self.NEEDS_MODIFICATION.items():
            if re.search(config['pattern'], java_code):
                self.issues.append(CompatibilityIssue(
                    category='needs_modification',
                    severity=config['severity'],
                    description=f"Pattern '{name}' needs modification",
                    java_pattern=config['pattern'],
                    python_alternative=config['alternative'],
                    migration_effort=config['effort']
                ))
    
    def _check_unsupported_patterns(self, java_code: str):
        """Check for unsupported patterns"""
        for name, config in self.UNSUPPORTED_PATTERNS.items():
            if re.search(config['pattern'], java_code):
                self.unsupported_features.append(name)
                self.issues.append(CompatibilityIssue(
                    category='unsupported',
                    severity=config['severity'],
                    description=f"Pattern '{name}' is not supported",
                    java_pattern=config['pattern'],
                    python_alternative=config['alternative'],
                    migration_effort=config['effort']
                ))
    
    def _determine_compatibility_level(self) -> CompatibilityLevel:
        """Determine overall compatibility level"""
        critical_issues = sum(
            1 for issue in self.issues
            if issue.severity == 'critical'
        )
        major_issues = sum(
            1 for issue in self.issues
            if issue.severity == 'major'
        )
        
        if critical_issues > 0:
            return CompatibilityLevel.INCOMPATIBLE
        elif major_issues > 5:
            return CompatibilityLevel.PARTIALLY_COMPATIBLE
        elif major_issues > 0:
            return CompatibilityLevel.MOSTLY_COMPATIBLE
        else:
            return CompatibilityLevel.FULLY_COMPATIBLE
    
    def _calculate_migration_complexity(self) -> str:
        """Calculate migration complexity"""
        high_effort_count = sum(
            1 for issue in self.issues
            if issue.migration_effort == 'high'
        )
        medium_effort_count = sum(
            1 for issue in self.issues
            if issue.migration_effort == 'medium'
        )
        
        if high_effort_count > 0:
            return 'complex'
        elif medium_effort_count > 3:
            return 'moderate'
        else:
            return 'simple'
    
    def _estimate_effort(self) -> float:
        """Estimate migration effort in hours"""
        effort_map = {
            'low': 0.5,
            'medium': 2.0,
            'high': 8.0
        }
        
        total_hours = sum(
            effort_map.get(issue.migration_effort, 1.0)
            for issue in self.issues
        )
        
        # Add base effort for setup and testing
        base_effort = 2.0
        
        return round(base_effort + total_hours, 1)
    
    def get_compatibility_summary(self, result: CompatibilityCheckResult) -> str:
        """Get a summary of compatibility check"""
        summary = f"""
Compatibility Check Summary:
============================
Compatibility Level: {result.compatibility_level.value.replace('_', ' ').title()}
Is Compatible: {'Yes' if result.is_compatible else 'No'}
Migration Complexity: {result.migration_complexity.title()}
Estimated Effort: {result.estimated_effort_hours} hours

Supported Features ({len(result.supported_features)}):
"""
        for feature in result.supported_features:
            summary += f"  ✓ {feature}\n"
        
        if result.unsupported_features:
            summary += f"\nUnsupported Features ({len(result.unsupported_features)}):\n"
            for feature in result.unsupported_features:
                summary += f"  ✗ {feature}\n"
        
        if result.issues:
            summary += f"\nIssues ({len(result.issues)}):\n"
            
            # Group by severity
            critical = [i for i in result.issues if i.severity == 'critical']
            major = [i for i in result.issues if i.severity == 'major']
            minor = [i for i in result.issues if i.severity == 'minor']
            
            if critical:
                summary += f"\n  Critical ({len(critical)}):\n"
                for issue in critical:
                    summary += f"    - {issue.description}\n"
                    if issue.python_alternative:
                        summary += f"      Alternative: {issue.python_alternative}\n"
            
            if major:
                summary += f"\n  Major ({len(major)}):\n"
                for issue in major:
                    summary += f"    - {issue.description}\n"
                    if issue.python_alternative:
                        summary += f"      Alternative: {issue.python_alternative}\n"
            
            if minor:
                summary += f"\n  Minor ({len(minor)}):\n"
                for issue in minor:
                    summary += f"    - {issue.description}\n"
        
        summary += "\n" + "="*60 + "\n"
        
        return summary
    
    def generate_migration_checklist(self, result: CompatibilityCheckResult) -> List[str]:
        """Generate a migration checklist"""
        checklist = [
            "Migration Checklist:",
            "===================",
            ""
        ]
        
        # Add items based on issues
        for i, issue in enumerate(result.issues, 1):
            checklist.append(
                f"{i}. [{issue.severity.upper()}] {issue.description}"
            )
            if issue.python_alternative:
                checklist.append(f"   → {issue.python_alternative}")
            checklist.append(f"   Effort: {issue.migration_effort}")
            checklist.append("")
        
        # Add general items
        checklist.extend([
            f"{len(result.issues) + 1}. Update imports to use Playwright",
            f"{len(result.issues) + 2}. Convert synchronous code to async/await",
            f"{len(result.issues) + 3}. Update element locators if needed",
            f"{len(result.issues) + 4}. Test converted code thoroughly",
            f"{len(result.issues) + 5}. Update documentation",
        ])
        
        return checklist
