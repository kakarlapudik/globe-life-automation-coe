"""
Core framework components for RAPTOR Python Playwright.

This module contains the fundamental building blocks of the framework:
- Browser management and lifecycle
- Element location and interaction
- Session persistence
- Configuration management
- Custom exceptions
"""

# Import implemented modules
from raptor.core.config_manager import ConfigManager
from raptor.core.browser_manager import BrowserManager
from raptor.core.session_manager import SessionManager
from raptor.core.soft_assertion_collector import SoftAssertionCollector, AssertionFailure
from raptor.core.exceptions import (
    RaptorException,
    ElementNotFoundException,
    ElementNotInteractableException,
    TimeoutException,
    DatabaseException,
    SessionException,
    ConfigurationException,
)

__all__ = [
    "ConfigManager",
    "BrowserManager",
    "SessionManager",
    "SoftAssertionCollector",
    "AssertionFailure",
    "RaptorException",
    "ElementNotFoundException",
    "ElementNotInteractableException",
    "TimeoutException",
    "DatabaseException",
    "SessionException",
    "ConfigurationException",
]

# TODO: Add imports as modules are implemented
# from raptor.core.element_manager import ElementManager
