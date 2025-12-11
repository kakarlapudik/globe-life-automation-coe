"""
RAPTOR Python Playwright Framework
A modern Python-based test automation framework using Playwright,
converted from the original Java Selenium RAPTOR framework.

This framework provides:
- Multi-browser support (Chromium, Firefox, WebKit)
- Element location with fallback strategies
- Session persistence and reuse
- Database integration for test data
- Page Object Model support
- Comprehensive reporting
"""

__version__ = "1.0.0"
__author__ = "RAPTOR Team"

# Import only implemented modules
from raptor.core.config_manager import ConfigManager
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
    "RaptorException",
    "ElementNotFoundException",
    "ElementNotInteractableException",
    "TimeoutException",
    "DatabaseException",
    "SessionException",
    "ConfigurationException",
]

# TODO: Add imports as modules are implemented
# from raptor.core.browser_manager import BrowserManager
# from raptor.core.element_manager import ElementManager
# from raptor.core.session_manager import SessionManager
# from raptor.database.database_manager import DatabaseManager
# from raptor.pages.base_page import BasePage
# from raptor.pages.table_manager import TableManager
