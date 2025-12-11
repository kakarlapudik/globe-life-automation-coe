"""
Data models for accessibility testing

Defines all data structures used in accessibility testing.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime


class ViolationSeverity(Enum):
    """Severity levels for accessibility violations."""
    CRITICAL = "critical"
    SERIOUS = "serious"
    MODERATE = "moderate"
    MINOR = "minor"


class ViolationImpact(Enum):
    """Impact levels for accessibility violations."""
    CRITICAL = "critical"
    SERIOUS = "serious"
    MODERATE = "moderate"
    MINOR = "minor"


class WCAGLevel(Enum):
    """WCAG conformance levels."""
    A = "A"
    AA = "AA"
    AAA = "AAA"


@dataclass
class AccessibilityNode:
    """Represents a DOM node with accessibility violation."""
    html: str
    target: List[str]
    xpath: Optional[str] = None
    ancestry: Optional[str] = None
    
    
@dataclass
class AccessibilityViolation:
    """
    Represents an accessibility violation.
    
    Attributes:
        id: Unique identifier for the violation rule
        description: Human-readable description of the violation
        help: Help text explaining the issue
        help_url: URL to detailed documentation
        impact: Impact level of the violation
        tags: Tags categorizing the violation (wcag2a, wcag21aa, etc.)
        nodes: List of DOM nodes with this violation
    """
    id: str
    description: str
    help: str
    help_url: str
    impact: ViolationImpact
    tags: List[str]
    nodes: List[AccessibilityNode]
    
    def get_wcag_level(self) -> Optional[WCAGLevel]:
        """Determine WCAG level from tags."""
        if 'wcag2aaa' in self.tags or 'wcag21aaa' in self.tags or 'wcag22aaa' in self.tags:
            return WCAGLevel.AAA
        elif 'wcag2aa' in self.tags or 'wcag21aa' in self.tags or 'wcag22aa' in self.tags:
            return WCAGLevel.AA
        elif 'wcag2a' in self.tags or 'wcag21a' in self.tags or 'wcag22a' in self.tags:
            return WCAGLevel.A
        return None
    
    def is_wcag_violation(self) -> bool:
        """Check if this is a WCAG violation."""
        wcag_tags = ['wcag2a', 'wcag2aa', 'wcag2aaa', 'wcag21a', 'wcag21aa', 'wcag21aaa', 
                     'wcag22a', 'wcag22aa', 'wcag22aaa']
        return any(tag in self.tags for tag in wcag_tags)
    
    def is_section508_violation(self) -> bool:
        """Check if this is a Section 508 violation."""
        return 'section508' in self.tags
    
    def get_severity(self) -> ViolationSeverity:
        """Map impact to severity."""
        severity_map = {
            ViolationImpact.CRITICAL: ViolationSeverity.CRITICAL,
            ViolationImpact.SERIOUS: ViolationSeverity.SERIOUS,
            ViolationImpact.MODERATE: ViolationSeverity.MODERATE,
            ViolationImpact.MINOR: ViolationSeverity.MINOR
        }
        return severity_map.get(self.impact, ViolationSeverity.MODERATE)


@dataclass
class AccessibilityPass:
    """Represents a passed accessibility check."""
    id: str
    description: str
    help: str
    help_url: str
    impact: ViolationImpact
    tags: List[str]
    nodes: List[AccessibilityNode]


@dataclass
class AccessibilityIncomplete:
    """Represents an incomplete accessibility check."""
    id: str
    description: str
    help: str
    help_url: str
    impact: ViolationImpact
    tags: List[str]
    nodes: List[AccessibilityNode]


@dataclass
class AccessibilityResult:
    """
    Complete accessibility scan result.
    
    Attributes:
        url: URL of the scanned page
        timestamp: When the scan was performed
        violations: List of accessibility violations found
        passes: List of passed checks
        incomplete: List of incomplete checks
        inapplicable: List of inapplicable checks
        test_engine: Information about the testing engine used
    """
    url: str
    timestamp: datetime
    violations: List[AccessibilityViolation]
    passes: List[AccessibilityPass] = field(default_factory=list)
    incomplete: List[AccessibilityIncomplete] = field(default_factory=list)
    inapplicable: List[Dict[str, Any]] = field(default_factory=list)
    test_engine: Dict[str, str] = field(default_factory=dict)
    
    def get_violation_count(self) -> int:
        """Get total number of violations."""
        return len(self.violations)
    
    def get_violations_by_severity(self, severity: ViolationSeverity) -> List[AccessibilityViolation]:
        """Get violations filtered by severity."""
        return [v for v in self.violations if v.get_severity() == severity]
    
    def get_violations_by_wcag_level(self, level: WCAGLevel) -> List[AccessibilityViolation]:
        """Get violations filtered by WCAG level."""
        return [v for v in self.violations if v.get_wcag_level() == level]
    
    def get_critical_violations(self) -> List[AccessibilityViolation]:
        """Get critical violations."""
        return self.get_violations_by_severity(ViolationSeverity.CRITICAL)
    
    def get_serious_violations(self) -> List[AccessibilityViolation]:
        """Get serious violations."""
        return self.get_violations_by_severity(ViolationSeverity.SERIOUS)
    
    def has_violations(self) -> bool:
        """Check if any violations were found."""
        return len(self.violations) > 0
    
    def get_summary(self) -> Dict[str, int]:
        """Get summary statistics."""
        return {
            'total_violations': len(self.violations),
            'critical': len(self.get_critical_violations()),
            'serious': len(self.get_serious_violations()),
            'moderate': len(self.get_violations_by_severity(ViolationSeverity.MODERATE)),
            'minor': len(self.get_violations_by_severity(ViolationSeverity.MINOR)),
            'passes': len(self.passes),
            'incomplete': len(self.incomplete),
            'inapplicable': len(self.inapplicable)
        }


@dataclass
class AccessibilityReport:
    """
    Comprehensive accessibility report.
    
    Attributes:
        results: List of accessibility scan results
        summary: Overall summary statistics
        generated_at: When the report was generated
        standard: Accessibility standard tested against
        metadata: Additional metadata
    """
    results: List[AccessibilityResult]
    summary: Dict[str, Any]
    generated_at: datetime
    standard: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_total_violations(self) -> int:
        """Get total violations across all results."""
        return sum(r.get_violation_count() for r in self.results)
    
    def get_all_violations(self) -> List[AccessibilityViolation]:
        """Get all violations from all results."""
        all_violations = []
        for result in self.results:
            all_violations.extend(result.violations)
        return all_violations
    
    def get_unique_violation_types(self) -> List[str]:
        """Get unique violation rule IDs."""
        return list(set(v.id for v in self.get_all_violations()))
    
    def has_critical_violations(self) -> bool:
        """Check if any critical violations exist."""
        return any(r.get_critical_violations() for r in self.results)
