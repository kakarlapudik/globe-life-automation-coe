"""
RAPTOR Accessibility Testing Module

This module provides comprehensive accessibility testing capabilities using
open-source tools like axe-core and pa11y. It enables automated detection of
accessibility violations (WCAG 2.1, Section 508, etc.) and provides detailed
reporting for remediation.

Key Features:
- Automated accessibility scanning using axe-core
- WCAG 2.1 Level A, AA, AAA compliance checking
- Section 508 compliance testing
- Detailed violation reporting with remediation guidance
- Integration with RAPTOR reporting system
- Support for custom accessibility rules
- Continuous accessibility monitoring

Example Usage:
    from raptor.accessibility import AccessibilityScanner, AccessibilityConfig
    
    # Initialize scanner
    config = AccessibilityConfig(standard='wcag21aa')
    scanner = AccessibilityScanner(config, page)
    
    # Scan page for violations
    results = await scanner.scan()
    
    # Generate report
    report = scanner.generate_report(results)
"""

from raptor.accessibility.config import AccessibilityConfig, AccessibilityStandard
from raptor.accessibility.scanner import AccessibilityScanner
from raptor.accessibility.models import (
    AccessibilityViolation,
    AccessibilityResult,
    ViolationSeverity,
    ViolationImpact,
    WCAGLevel,
    AccessibilityReport
)
from raptor.accessibility.reporter import AccessibilityReporter
from raptor.accessibility.rules import AccessibilityRuleManager

__all__ = [
    'AccessibilityConfig',
    'AccessibilityStandard',
    'AccessibilityScanner',
    'AccessibilityViolation',
    'AccessibilityResult',
    'ViolationSeverity',
    'ViolationImpact',
    'WCAGLevel',
    'AccessibilityReport',
    'AccessibilityReporter',
    'AccessibilityRuleManager',
]

__version__ = '1.0.0'
