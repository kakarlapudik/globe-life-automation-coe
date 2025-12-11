"""
Accessibility Testing Configuration

Configuration management for accessibility testing features.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import yaml
from pathlib import Path


class AccessibilityStandard(Enum):
    """Accessibility standards to test against."""
    WCAG21A = "wcag21a"
    WCAG21AA = "wcag21aa"
    WCAG21AAA = "wcag21aaa"
    WCAG22A = "wcag22a"
    WCAG22AA = "wcag22aa"
    WCAG22AAA = "wcag22aaa"
    SECTION508 = "section508"
    EN301549 = "en301549"
    BEST_PRACTICE = "best-practice"


class WCAGLevel(Enum):
    """WCAG conformance levels."""
    A = "A"
    AA = "AA"
    AAA = "AAA"


@dataclass
class AccessibilityConfig:
    """
    Configuration for accessibility testing.
    
    This configuration controls all aspects of accessibility testing including
    standards compliance, violation reporting, and integration with the framework.
    
    Attributes:
        enabled: Enable/disable accessibility testing
        standard: Accessibility standard to test against
        include_best_practices: Include best practice checks
        fail_on_violations: Fail tests when violations are found
        severity_threshold: Minimum severity to report (critical, serious, moderate, minor)
        
    Example:
        config = AccessibilityConfig(
            enabled=True,
            standard=AccessibilityStandard.WCAG21AA,
            fail_on_violations=True
        )
    """
    enabled: bool = True
    standard: AccessibilityStandard = AccessibilityStandard.WCAG21AA
    include_best_practices: bool = True
    fail_on_violations: bool = False
    severity_threshold: str = "moderate"  # critical, serious, moderate, minor
    
    # Scanning options
    scan_on_page_load: bool = False
    scan_on_navigation: bool = False
    scan_on_interaction: bool = False
    
    # Reporting options
    generate_html_report: bool = True
    generate_json_report: bool = True
    generate_csv_report: bool = False
    include_screenshots: bool = True
    include_remediation_guidance: bool = True
    
    # Rule configuration
    enabled_rules: List[str] = field(default_factory=list)
    disabled_rules: List[str] = field(default_factory=list)
    custom_rules: List[Dict[str, Any]] = field(default_factory=list)
    
    # Integration options
    integrate_with_reporter: bool = True
    integrate_with_ci: bool = True
    
    # Directories
    report_dir: str = "reports/accessibility"
    baseline_dir: str = "baselines/accessibility"
    
    # Advanced options
    timeout: int = 30000
    context_selector: Optional[str] = None  # Limit scan to specific element
    exclude_selectors: List[str] = field(default_factory=list)
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'AccessibilityConfig':
        """
        Load configuration from YAML file.
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            AccessibilityConfig instance
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
            
        a11y_data = data.get('accessibility', {})
        
        return cls(
            enabled=a11y_data.get('enabled', True),
            standard=AccessibilityStandard(a11y_data.get('standard', 'wcag21aa')),
            include_best_practices=a11y_data.get('include_best_practices', True),
            fail_on_violations=a11y_data.get('fail_on_violations', False),
            severity_threshold=a11y_data.get('severity_threshold', 'moderate'),
            scan_on_page_load=a11y_data.get('scan_on_page_load', False),
            scan_on_navigation=a11y_data.get('scan_on_navigation', False),
            scan_on_interaction=a11y_data.get('scan_on_interaction', False),
            generate_html_report=a11y_data.get('generate_html_report', True),
            generate_json_report=a11y_data.get('generate_json_report', True),
            generate_csv_report=a11y_data.get('generate_csv_report', False),
            include_screenshots=a11y_data.get('include_screenshots', True),
            include_remediation_guidance=a11y_data.get('include_remediation_guidance', True),
            enabled_rules=a11y_data.get('enabled_rules', []),
            disabled_rules=a11y_data.get('disabled_rules', []),
            custom_rules=a11y_data.get('custom_rules', []),
            integrate_with_reporter=a11y_data.get('integrate_with_reporter', True),
            integrate_with_ci=a11y_data.get('integrate_with_ci', True),
            report_dir=a11y_data.get('report_dir', 'reports/accessibility'),
            baseline_dir=a11y_data.get('baseline_dir', 'baselines/accessibility'),
            timeout=a11y_data.get('timeout', 30000),
            context_selector=a11y_data.get('context_selector'),
            exclude_selectors=a11y_data.get('exclude_selectors', [])
        )
    
    def validate(self) -> None:
        """
        Validate configuration values.
        
        Raises:
            ValueError: If configuration values are invalid
        """
        valid_severities = ['critical', 'serious', 'moderate', 'minor']
        if self.severity_threshold not in valid_severities:
            raise ValueError(f"severity_threshold must be one of {valid_severities}")
        
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        Path(self.report_dir).mkdir(parents=True, exist_ok=True)
        Path(self.baseline_dir).mkdir(parents=True, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'enabled': self.enabled,
            'standard': self.standard.value,
            'include_best_practices': self.include_best_practices,
            'fail_on_violations': self.fail_on_violations,
            'severity_threshold': self.severity_threshold,
            'scan_on_page_load': self.scan_on_page_load,
            'scan_on_navigation': self.scan_on_navigation,
            'scan_on_interaction': self.scan_on_interaction,
            'generate_html_report': self.generate_html_report,
            'generate_json_report': self.generate_json_report,
            'generate_csv_report': self.generate_csv_report,
            'include_screenshots': self.include_screenshots,
            'include_remediation_guidance': self.include_remediation_guidance,
            'enabled_rules': self.enabled_rules,
            'disabled_rules': self.disabled_rules,
            'integrate_with_reporter': self.integrate_with_reporter,
            'integrate_with_ci': self.integrate_with_ci,
            'report_dir': self.report_dir,
            'baseline_dir': self.baseline_dir,
            'timeout': self.timeout,
            'context_selector': self.context_selector,
            'exclude_selectors': self.exclude_selectors
        }
