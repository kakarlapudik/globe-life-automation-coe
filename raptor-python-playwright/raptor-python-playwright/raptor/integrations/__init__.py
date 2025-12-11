"""
External integrations for RAPTOR Framework

This package provides integrations with external test management systems:
- ALM (Application Lifecycle Management)
- JIRA (Issue Tracking and Project Management)
"""

from raptor.integrations.alm_integration import ALMIntegration
from raptor.integrations.jira_integration import JIRAIntegration

__all__ = ["ALMIntegration", "JIRAIntegration"]
