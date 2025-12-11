"""
V3 Home Page Object for RAPTOR Python Playwright Framework.

This module provides the page object for the V3 application home page,
including navigation to various modules and common home page operations.
"""

from typing import Optional
from playwright.async_api import Page
from raptor.pages.base_page import BasePage
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.core.exceptions import RaptorException
import logging

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """
    Page Object for V3 Application Home Page.
    
    This class provides methods to interact with the V3 home page,
    including navigation to different modules, user menu operations,
    and common home page functionality.
    
    Typical V3 home page elements include:
    - Navigation menu
    - User profile menu
    - Quick access links
    - Dashboard widgets
    - Module shortcuts
    
    Example:
        >>> home_page = HomePage(page, element_manager)
        >>> await home_page.navigate_to_home()
        >>> await home_page.navigate_to_user_maintenance()
        >>> await home_page.logout()
    """

    def __init__(
        self,
        page: Page,
        element_manager: Optional[ElementManager] = None,
        config: Optional[ConfigManager] = None,
    ):
        """
        Initialize the V3 Home Page.

        Args:
            page: Playwright Page instance
            element_manager: Optional ElementManager instance
            config: Optional ConfigManager instance
        """
        super().__init__(page, element_manager, config)
        
        # Define locators for home page elements
        # These would be customized based on actual V3 application structure
        self.locators = {
            # Navigation menu
            "nav_menu": "css=#navigation-menu",
            "nav_menu_toggle": "css=.nav-toggle",
            
            # User menu
            "user_menu": "css=#user-menu",
            "user_menu_toggle": "css=.user-menu-toggle",
            "logout_button": "css=#logout-button",
            "user_profile": "css=#user-profile",
            
            # Module navigation
            "admin_module": "css=a[href*='admin']",
            "user_maintenance": "css=a[href*='user-maintenance']",
            "system_setup": "css=a[href*='system-setup']",
            "group_contact": "css=a[href*='group-contact']",
            "cert_profile": "css=a[href*='cert-profile']",
            "sales_rep_profile": "css=a[href*='sales-rep']",
            
            # Dashboard elements
            "dashboard_title": "css=.dashboard-title",
            "welcome_message": "css=.welcome-message",
            "quick_links": "css=.quick-links",
            
            # Common elements
            "page_header": "css=.page-header",
            "breadcrumb": "css=.breadcrumb",
            "notification_icon": "css=.notification-icon",
            "help_icon": "css=.help-icon",
        }
        
        logger.info("V3 HomePage initialized")

    async def navigate_to_home(
        self,
        base_url: Optional[str] = None,
        wait_for_load: bool = True,
    ) -> None:
        """
        Navigate to the V3 home page.
        
        Args:
            base_url: Optional base URL. If not provided, uses config.
            wait_for_load: Whether to wait for page load completion
            
        Raises:
            RaptorException: If navigation fails
            
        Example:
            >>> await home_page.navigate_to_home()
            >>> await home_page.navigate_to_home("https://v3.example.com")
        """
        try:
            url = base_url or self.config.get("v3.base_url", "")
            
            if not url:
                raise RaptorException(
                    "V3 base URL not configured",
                    context={"config_key": "v3.base_url"}
                )
            
            logger.info(f"Navigating to V3 home page: {url}")
            await self.navigate(url)
            
            if wait_for_load:
                await self.wait_for_home_page_load()
            
            logger.info("Successfully navigated to V3 home page")
            
        except Exception as e:
            logger.error(f"Failed to navigate to V3 home page: {str(e)}")
            raise RaptorException(
                f"Failed to navigate to V3 home page: {str(e)}",
                context={"base_url": base_url},
                cause=e
            )

    async def wait_for_home_page_load(self, timeout: Optional[int] = None) -> None:
        """
        Wait for home page to fully load.
        
        This method waits for key home page elements to be visible,
        indicating the page has loaded successfully.
        
        Args:
            timeout: Optional timeout in milliseconds
            
        Raises:
            TimeoutException: If page doesn't load within timeout
            
        Example:
            >>> await home_page.wait_for_home_page_load()
        """
        try:
            logger.debug("Waiting for home page to load")
            
            # Wait for page load state
            await self.wait_for_load(state="load", timeout=timeout)
            
            # Wait for key elements to be visible
            await self.element_manager.wait_for_element(
                self.locators["page_header"],
                timeout=timeout or self.config.get_timeout("element")
            )
            
            logger.info("Home page loaded successfully")
            
        except Exception as e:
            logger.error(f"Home page load failed: {str(e)}")
            raise

    async def navigate_to_user_maintenance(self) -> None:
        """
        Navigate to User Maintenance module from home page.
        
        This method clicks the User Maintenance link in the navigation menu
        and waits for the page to load.
        
        Raises:
            RaptorException: If navigation fails
            
        Example:
            >>> await home_page.navigate_to_user_maintenance()
        """
        try:
            logger.info("Navigating to User Maintenance")
            
            # Ensure navigation menu is visible
            await self._ensure_nav_menu_visible()
            
            # Click User Maintenance link
            await self.element_manager.click(self.locators["user_maintenance"])
            
            # Wait for navigation
            await self.wait_for_load(state="load")
            
            logger.info("Successfully navigated to User Maintenance")
            
        except Exception as e:
            logger.error(f"Failed to navigate to User Maintenance: {str(e)}")
            raise RaptorException(
                f"Failed to navigate to User Maintenance: {str(e)}",
                context={"current_url": self.page.url},
                cause=e
            )

    async def navigate_to_system_setup(self) -> None:
        """
        Navigate to System Setup module from home page.
        
        This method clicks the System Setup link in the navigation menu
        and waits for the page to load.
        
        Raises:
            RaptorException: If navigation fails
            
        Example:
            >>> await home_page.navigate_to_system_setup()
        """
        try:
            logger.info("Navigating to System Setup")
            
            # Ensure navigation menu is visible
            await self._ensure_nav_menu_visible()
            
            # Click System Setup link
            await self.element_manager.click(self.locators["system_setup"])
            
            # Wait for navigation
            await self.wait_for_load(state="load")
            
            logger.info("Successfully navigated to System Setup")
            
        except Exception as e:
            logger.error(f"Failed to navigate to System Setup: {str(e)}")
            raise RaptorException(
                f"Failed to navigate to System Setup: {str(e)}",
                context={"current_url": self.page.url},
                cause=e
            )

    async def navigate_to_group_contact(self) -> None:
        """
        Navigate to Group Contact module from home page.
        
        Raises:
            RaptorException: If navigation fails
            
        Example:
            >>> await home_page.navigate_to_group_contact()
        """
        try:
            logger.info("Navigating to Group Contact")
            
            await self._ensure_nav_menu_visible()
            await self.element_manager.click(self.locators["group_contact"])
            await self.wait_for_load(state="load")
            
            logger.info("Successfully navigated to Group Contact")
            
        except Exception as e:
            logger.error(f"Failed to navigate to Group Contact: {str(e)}")
            raise RaptorException(
                f"Failed to navigate to Group Contact: {str(e)}",
                context={"current_url": self.page.url},
                cause=e
            )

    async def navigate_to_cert_profile(self) -> None:
        """
        Navigate to Certificate Profile module from home page.
        
        Raises:
            RaptorException: If navigation fails
            
        Example:
            >>> await home_page.navigate_to_cert_profile()
        """
        try:
            logger.info("Navigating to Certificate Profile")
            
            await self._ensure_nav_menu_visible()
            await self.element_manager.click(self.locators["cert_profile"])
            await self.wait_for_load(state="load")
            
            logger.info("Successfully navigated to Certificate Profile")
            
        except Exception as e:
            logger.error(f"Failed to navigate to Certificate Profile: {str(e)}")
            raise RaptorException(
                f"Failed to navigate to Certificate Profile: {str(e)}",
                context={"current_url": self.page.url},
                cause=e
            )

    async def navigate_to_sales_rep_profile(self) -> None:
        """
        Navigate to Sales Rep Profile module from home page.
        
        Raises:
            RaptorException: If navigation fails
            
        Example:
            >>> await home_page.navigate_to_sales_rep_profile()
        """
        try:
            logger.info("Navigating to Sales Rep Profile")
            
            await self._ensure_nav_menu_visible()
            await self.element_manager.click(self.locators["sales_rep_profile"])
            await self.wait_for_load(state="load")
            
            logger.info("Successfully navigated to Sales Rep Profile")
            
        except Exception as e:
            logger.error(f"Failed to navigate to Sales Rep Profile: {str(e)}")
            raise RaptorException(
                f"Failed to navigate to Sales Rep Profile: {str(e)}",
                context={"current_url": self.page.url},
                cause=e
            )

    async def logout(self) -> None:
        """
        Logout from the V3 application.
        
        This method opens the user menu and clicks the logout button.
        
        Raises:
            RaptorException: If logout fails
            
        Example:
            >>> await home_page.logout()
        """
        try:
            logger.info("Logging out from V3 application")
            
            # Open user menu if not already open
            await self._ensure_user_menu_visible()
            
            # Click logout button
            await self.element_manager.click(self.locators["logout_button"])
            
            # Wait for logout to complete (usually redirects to login page)
            await self.wait_for_load(state="load")
            
            logger.info("Successfully logged out")
            
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            raise RaptorException(
                f"Failed to logout: {str(e)}",
                context={"current_url": self.page.url},
                cause=e
            )

    async def get_welcome_message(self) -> str:
        """
        Get the welcome message displayed on the home page.
        
        Returns:
            Welcome message text
            
        Raises:
            RaptorException: If unable to retrieve message
            
        Example:
            >>> message = await home_page.get_welcome_message()
            >>> assert "Welcome" in message
        """
        try:
            logger.debug("Getting welcome message")
            
            message = await self.element_manager.get_text(
                self.locators["welcome_message"]
            )
            
            logger.info(f"Welcome message: {message}")
            return message
            
        except Exception as e:
            logger.error(f"Failed to get welcome message: {str(e)}")
            raise RaptorException(
                f"Failed to get welcome message: {str(e)}",
                context={"current_url": self.page.url},
                cause=e
            )

    async def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in.
        
        This method checks for the presence of user menu elements
        to determine if the user is logged in.
        
        Returns:
            True if logged in, False otherwise
            
        Example:
            >>> if await home_page.is_logged_in():
            ...     await home_page.logout()
        """
        try:
            logger.debug("Checking if user is logged in")
            
            is_visible = await self.element_manager.is_visible(
                self.locators["user_menu"]
            )
            
            logger.info(f"User logged in: {is_visible}")
            return is_visible
            
        except Exception as e:
            logger.warning(f"Error checking login status: {str(e)}")
            return False

    async def _ensure_nav_menu_visible(self) -> None:
        """
        Ensure navigation menu is visible (expand if collapsed).
        
        This is a helper method to handle responsive navigation menus
        that may be collapsed on smaller screens.
        
        Raises:
            RaptorException: If unable to make menu visible
        """
        try:
            # Check if menu is already visible
            is_visible = await self.element_manager.is_visible(
                self.locators["nav_menu"]
            )
            
            if not is_visible:
                logger.debug("Navigation menu not visible, attempting to expand")
                
                # Try to click toggle button if it exists
                toggle_exists = await self.element_manager.is_visible(
                    self.locators["nav_menu_toggle"]
                )
                
                if toggle_exists:
                    await self.element_manager.click(
                        self.locators["nav_menu_toggle"]
                    )
                    
                    # Wait for menu to become visible
                    await self.element_manager.wait_for_element(
                        self.locators["nav_menu"]
                    )
                    
                    logger.debug("Navigation menu expanded")
            
        except Exception as e:
            logger.error(f"Failed to ensure nav menu visible: {str(e)}")
            raise RaptorException(
                f"Failed to ensure navigation menu is visible: {str(e)}",
                context={"current_url": self.page.url},
                cause=e
            )

    async def _ensure_user_menu_visible(self) -> None:
        """
        Ensure user menu is visible (expand if collapsed).
        
        This is a helper method to handle user menus that may be
        hidden in a dropdown.
        
        Raises:
            RaptorException: If unable to make menu visible
        """
        try:
            # Check if logout button is already visible
            is_visible = await self.element_manager.is_visible(
                self.locators["logout_button"]
            )
            
            if not is_visible:
                logger.debug("User menu not visible, attempting to expand")
                
                # Click user menu toggle
                await self.element_manager.click(
                    self.locators["user_menu_toggle"]
                )
                
                # Wait for logout button to become visible
                await self.element_manager.wait_for_element(
                    self.locators["logout_button"]
                )
                
                logger.debug("User menu expanded")
            
        except Exception as e:
            logger.error(f"Failed to ensure user menu visible: {str(e)}")
            raise RaptorException(
                f"Failed to ensure user menu is visible: {str(e)}",
                context={"current_url": self.page.url},
                cause=e
            )

    async def open_notifications(self) -> None:
        """
        Open the notifications panel.
        
        Raises:
            RaptorException: If unable to open notifications
            
        Example:
            >>> await home_page.open_notifications()
        """
        try:
            logger.info("Opening notifications")
            
            await self.element_manager.click(self.locators["notification_icon"])
            
            # Wait for notifications panel to appear
            await self.page.wait_for_timeout(500)  # Brief wait for animation
            
            logger.info("Notifications opened")
            
        except Exception as e:
            logger.error(f"Failed to open notifications: {str(e)}")
            raise RaptorException(
                f"Failed to open notifications: {str(e)}",
                context={"current_url": self.page.url},
                cause=e
            )

    async def open_help(self) -> None:
        """
        Open the help panel or documentation.
        
        Raises:
            RaptorException: If unable to open help
            
        Example:
            >>> await home_page.open_help()
        """
        try:
            logger.info("Opening help")
            
            await self.element_manager.click(self.locators["help_icon"])
            
            # Wait for help panel to appear
            await self.page.wait_for_timeout(500)
            
            logger.info("Help opened")
            
        except Exception as e:
            logger.error(f"Failed to open help: {str(e)}")
            raise RaptorException(
                f"Failed to open help: {str(e)}",
                context={"current_url": self.page.url},
                cause=e
            )
