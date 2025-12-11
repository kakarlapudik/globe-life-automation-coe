"""
V3-specific page objects for RAPTOR Python Playwright.

This module contains page object classes for V3 application pages.
"""

from raptor.pages.v3.home_page import HomePage
from raptor.pages.v3.user_maintenance import UserMaintenance
from raptor.pages.v3.system_setup import SystemSetup
from raptor.pages.v3.group_contact import GroupContact
from raptor.pages.v3.cert_profile import CertProfile
from raptor.pages.v3.sales_rep_profile import SalesRepProfile

__all__ = [
    "HomePage",
    "UserMaintenance",
    "SystemSetup",
    "GroupContact",
    "CertProfile",
    "SalesRepProfile",
]
