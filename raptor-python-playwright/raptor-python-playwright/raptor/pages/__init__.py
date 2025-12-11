"""
Page Object Model components for RAPTOR Python Playwright.

This module contains page object classes and utilities:
- Base page class with common functionality
- Table management for data tables
- V3-specific page objects
"""

from raptor.pages.base_page import BasePage

__all__ = ["BasePage"]

# TableManager import causes circular dependency - import directly when needed
# from raptor.pages.table_manager import TableManager
