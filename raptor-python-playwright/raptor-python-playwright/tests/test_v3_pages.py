"""
Tests for V3 Page Objects.

This module contains basic tests to verify V3 page objects are properly
implemented and can be instantiated.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from playwright.async_api import Page
from raptor.pages.v3 import (
    HomePage,
    UserMaintenance,
    SystemSetup,
    GroupContact,
    CertProfile,
    SalesRepProfile,
)
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager


@pytest.fixture
def mock_page():
    """Create a mock Playwright Page."""
    page = Mock(spec=Page)
    page.url = "https://example.com"
    page.wait_for_timeout = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    return page


@pytest.fixture
def mock_element_manager():
    """Create a mock ElementManager."""
    em = Mock(spec=ElementManager)
    em.wait_for_element = AsyncMock()
    em.click = AsyncMock()
    em.fill = AsyncMock()
    em.select_option = AsyncMock()
    em.is_visible = AsyncMock(return_value=True)
    em.is_selected = AsyncMock(return_value=False)
    em.get_text = AsyncMock(return_value="Test Message")
    em.get_value = AsyncMock(return_value="test_value")
    return em


@pytest.fixture
def mock_config():
    """Create a mock ConfigManager."""
    config = Mock(spec=ConfigManager)
    config.get = Mock(return_value="https://v3.example.com")
    config.get_timeout = Mock(return_value=20000)
    return config


class TestHomePage:
    """Tests for HomePage class."""

    def test_home_page_initialization(self, mock_page, mock_element_manager, mock_config):
        """Test that HomePage can be instantiated."""
        home_page = HomePage(mock_page, mock_element_manager, mock_config)
        
        assert home_page is not None
        assert home_page.page == mock_page
        assert home_page.element_manager == mock_element_manager
        assert home_page.config == mock_config
        assert "nav_menu" in home_page.locators
        assert "user_menu" in home_page.locators
        assert "logout_button" in home_page.locators

    def test_home_page_has_navigation_methods(self, mock_page, mock_element_manager, mock_config):
        """Test that HomePage has required navigation methods."""
        home_page = HomePage(mock_page, mock_element_manager, mock_config)
        
        assert hasattr(home_page, "navigate_to_home")
        assert hasattr(home_page, "navigate_to_user_maintenance")
        assert hasattr(home_page, "navigate_to_system_setup")
        assert hasattr(home_page, "navigate_to_group_contact")
        assert hasattr(home_page, "navigate_to_cert_profile")
        assert hasattr(home_page, "navigate_to_sales_rep_profile")
        assert hasattr(home_page, "logout")

    @pytest.mark.asyncio
    async def test_home_page_is_logged_in(self, mock_page, mock_element_manager, mock_config):
        """Test is_logged_in method."""
        home_page = HomePage(mock_page, mock_element_manager, mock_config)
        
        mock_element_manager.is_visible.return_value = True
        result = await home_page.is_logged_in()
        
        assert result is True
        mock_element_manager.is_visible.assert_called_once()


class TestUserMaintenance:
    """Tests for UserMaintenance class."""

    def test_user_maintenance_initialization(self, mock_page, mock_element_manager, mock_config):
        """Test that UserMaintenance can be instantiated."""
        user_maint = UserMaintenance(mock_page, mock_element_manager, mock_config)
        
        assert user_maint is not None
        assert user_maint.page == mock_page
        assert user_maint.element_manager == mock_element_manager
        assert user_maint.config == mock_config
        assert user_maint.table_manager is not None
        assert "user_grid" in user_maint.locators
        assert "create_user_button" in user_maint.locators
        assert "search_box" in user_maint.locators

    def test_user_maintenance_has_crud_methods(self, mock_page, mock_element_manager, mock_config):
        """Test that UserMaintenance has CRUD methods."""
        user_maint = UserMaintenance(mock_page, mock_element_manager, mock_config)
        
        assert hasattr(user_maint, "create_user")
        assert hasattr(user_maint, "edit_user")
        assert hasattr(user_maint, "delete_user")
        assert hasattr(user_maint, "search_user")
        assert hasattr(user_maint, "get_user_details")
        assert hasattr(user_maint, "refresh_user_grid")


class TestSystemSetup:
    """Tests for SystemSetup class."""

    def test_system_setup_initialization(self, mock_page, mock_element_manager, mock_config):
        """Test that SystemSetup can be instantiated."""
        system_setup = SystemSetup(mock_page, mock_element_manager, mock_config)
        
        assert system_setup is not None
        assert system_setup.page == mock_page
        assert system_setup.element_manager == mock_element_manager
        assert system_setup.config == mock_config
        assert system_setup.table_manager is not None
        assert "settings_panel" in system_setup.locators
        assert "general_tab" in system_setup.locators
        assert "security_tab" in system_setup.locators

    def test_system_setup_has_configuration_methods(self, mock_page, mock_element_manager, mock_config):
        """Test that SystemSetup has configuration methods."""
        system_setup = SystemSetup(mock_page, mock_element_manager, mock_config)
        
        assert hasattr(system_setup, "switch_to_tab")
        assert hasattr(system_setup, "update_general_setting")
        assert hasattr(system_setup, "update_security_setting")
        assert hasattr(system_setup, "configure_email_settings")
        assert hasattr(system_setup, "test_email_connection")
        assert hasattr(system_setup, "add_lookup_value")
        assert hasattr(system_setup, "save_configuration")
        assert hasattr(system_setup, "reset_configuration")
        assert hasattr(system_setup, "export_configuration")
        assert hasattr(system_setup, "import_configuration")
        assert hasattr(system_setup, "get_setting_value")

    @pytest.mark.asyncio
    async def test_system_setup_get_setting_value(self, mock_page, mock_element_manager, mock_config):
        """Test get_setting_value method."""
        system_setup = SystemSetup(mock_page, mock_element_manager, mock_config)
        
        mock_element_manager.get_value.return_value = "Test App"
        result = await system_setup.get_setting_value("app_name")
        
        assert result == "Test App"
        mock_element_manager.get_value.assert_called_once()


class TestGroupContact:
    """Tests for GroupContact class."""

    def test_group_contact_initialization(self, mock_page, mock_element_manager, mock_config):
        """Test that GroupContact can be instantiated."""
        group_contact = GroupContact(mock_page, mock_element_manager, mock_config)
        
        assert group_contact is not None
        assert group_contact.page == mock_page
        assert group_contact.element_manager == mock_element_manager
        assert group_contact.config == mock_config
        assert group_contact.table_manager is not None
        assert "groups_grid" in group_contact.locators
        assert "contacts_grid" in group_contact.locators
        assert "create_group_button" in group_contact.locators

    def test_group_contact_has_group_methods(self, mock_page, mock_element_manager, mock_config):
        """Test that GroupContact has group management methods."""
        group_contact = GroupContact(mock_page, mock_element_manager, mock_config)
        
        assert hasattr(group_contact, "create_group")
        assert hasattr(group_contact, "edit_group")
        assert hasattr(group_contact, "delete_group")
        assert hasattr(group_contact, "search_group")
        assert hasattr(group_contact, "add_contact_to_group")
        assert hasattr(group_contact, "remove_contact_from_group")
        assert hasattr(group_contact, "get_group_members")


class TestCertProfile:
    """Tests for CertProfile class."""

    def test_cert_profile_initialization(self, mock_page, mock_element_manager, mock_config):
        """Test that CertProfile can be instantiated."""
        cert_profile = CertProfile(mock_page, mock_element_manager, mock_config)
        
        assert cert_profile is not None
        assert cert_profile.page == mock_page
        assert cert_profile.element_manager == mock_element_manager
        assert cert_profile.config == mock_config
        assert cert_profile.table_manager is not None
        assert "certificates_grid" in cert_profile.locators
        assert "create_cert_button" in cert_profile.locators
        assert "upload_cert_button" in cert_profile.locators

    def test_cert_profile_has_certificate_methods(self, mock_page, mock_element_manager, mock_config):
        """Test that CertProfile has certificate management methods."""
        cert_profile = CertProfile(mock_page, mock_element_manager, mock_config)
        
        assert hasattr(cert_profile, "create_certificate_profile")
        assert hasattr(cert_profile, "upload_certificate")
        assert hasattr(cert_profile, "validate_certificate")
        assert hasattr(cert_profile, "download_certificate")
        assert hasattr(cert_profile, "renew_certificate")
        assert hasattr(cert_profile, "revoke_certificate")
        assert hasattr(cert_profile, "delete_certificate")
        assert hasattr(cert_profile, "get_certificate_details")
        assert hasattr(cert_profile, "check_expiration_status")


class TestSalesRepProfile:
    """Tests for SalesRepProfile class."""

    def test_sales_rep_profile_initialization(self, mock_page, mock_element_manager, mock_config):
        """Test that SalesRepProfile can be instantiated."""
        sales_rep = SalesRepProfile(mock_page, mock_element_manager, mock_config)
        
        assert sales_rep is not None
        assert sales_rep.page == mock_page
        assert sales_rep.element_manager == mock_element_manager
        assert sales_rep.config == mock_config
        assert sales_rep.table_manager is not None
        assert "sales_reps_grid" in sales_rep.locators
        assert "create_rep_button" in sales_rep.locators
        assert "territory_dropdown" in sales_rep.locators

    def test_sales_rep_profile_has_management_methods(self, mock_page, mock_element_manager, mock_config):
        """Test that SalesRepProfile has sales rep management methods."""
        sales_rep = SalesRepProfile(mock_page, mock_element_manager, mock_config)
        
        assert hasattr(sales_rep, "create_sales_rep")
        assert hasattr(sales_rep, "edit_sales_rep")
        assert hasattr(sales_rep, "delete_sales_rep")
        assert hasattr(sales_rep, "search_sales_rep")
        assert hasattr(sales_rep, "assign_territory")
        assert hasattr(sales_rep, "update_quota")
        assert hasattr(sales_rep, "view_performance")
        assert hasattr(sales_rep, "generate_performance_report")
        assert hasattr(sales_rep, "get_assigned_territories")


class TestV3PageImports:
    """Test that V3 page objects can be imported from the package."""

    def test_import_from_v3_package(self):
        """Test importing page objects from raptor.pages.v3."""
        from raptor.pages.v3 import (
            HomePage,
            UserMaintenance,
            SystemSetup,
            GroupContact,
            CertProfile,
            SalesRepProfile,
        )
        
        assert HomePage is not None
        assert UserMaintenance is not None
        assert SystemSetup is not None
        assert GroupContact is not None
        assert CertProfile is not None
        assert SalesRepProfile is not None

    def test_v3_package_all_exports(self):
        """Test that __all__ exports are correct."""
        import raptor.pages.v3 as v3
        
        assert "HomePage" in v3.__all__
        assert "UserMaintenance" in v3.__all__
        assert "SystemSetup" in v3.__all__
        assert "GroupContact" in v3.__all__
        assert "CertProfile" in v3.__all__
        assert "SalesRepProfile" in v3.__all__
        assert len(v3.__all__) == 6
