"""
V3 User Maintenance Page Object for RAPTOR Python Playwright Framework.

This module provides the page object for the V3 User Maintenance module,
including user creation, editing, searching, and management operations.
"""

from typing import Optional, Dict, List, Any
from playwright.async_api import Page
from raptor.pages.base_page import BasePage
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.core.exceptions import RaptorException
from raptor.pages.table_manager import TableManager
import logging

logger = logging.getLogger(__name__)


class UserMaintenance(BasePage):
    """
    Page Object for V3 User Maintenance Module.
    
    This class provides methods to interact with the User Maintenance module,
    including:
    - Creating new users
    - Editing existing users
    - Searching for users
    - Deleting users
    - Managing user roles and permissions
    - Activating/deactivating users
    
    Example:
        >>> user_maint = UserMaintenance(page, element_manager)
        >>> await user_maint.navigate_to_user_maintenance()
        >>> await user_maint.create_user({
        ...     "username": "testuser",
        ...     "email": "test@example.com",
        ...     "role": "Admin"
        ... })
        >>> await user_maint.search_user("testuser")
    """

    def __init__(
        self,
        page: Page,
        element_manager: Optional[ElementManager] = None,
        config: Optional[ConfigManager] = None,
    ):
        """
        Initialize the User Maintenance Page.

        Args:
            page: Playwright Page instance
            element_manager: Optional ElementManager instance
            config: Optional ConfigManager instance
        """
        super().__init__(page, element_manager, config)
        
        # Initialize table manager for user grid
        self.table_manager = TableManager(page, self.element_manager)
        
        # Define locators for user maintenance elements
        self.locators = {
            # Page elements
            "page_title": "css=.page-title",
            "user_grid": "css=#user-grid",
            
            # Search elements
            "search_box": "css=#user-search",
            "search_button": "css=#search-button",
            "clear_search_button": "css=#clear-search",
            "advanced_search_toggle": "css=#advanced-search-toggle",
            
            # Action buttons
            "create_user_button": "css=#create-user-button",
            "edit_user_button": "css=#edit-user-button",
            "delete_user_button": "css=#delete-user-button",
            "refresh_button": "css=#refresh-button",
            "export_button": "css=#export-button",
            
            # User form elements
            "user_form": "css=#user-form",
            "username_field": "css=#username",
            "email_field": "css=#email",
            "first_name_field": "css=#first-name",
            "last_name_field": "css=#last-name",
            "role_dropdown": "css=#role",
            "status_dropdown": "css=#status",
            "department_field": "css=#department",
            "phone_field": "css=#phone",
            
            # Form buttons
            "save_button": "css=#save-button",
            "cancel_button": "css=#cancel-button",
            "reset_button": "css=#reset-button",
            
            # Confirmation dialogs
            "confirm_dialog": "css=.confirm-dialog",
            "confirm_yes_button": "css=.confirm-yes",
            "confirm_no_button": "css=.confirm-no",
            
            # Status messages
            "success_message": "css=.success-message",
            "error_message": "css=.error-message",
            "warning_message": "css=.warning-message",
            
            # User grid columns (for table operations)
            "grid_username_column": "css=.grid-username",
            "grid_email_column": "css=.grid-email",
            "grid_role_column": "css=.grid-role",
            "grid_status_column": "css=.grid-status",
            "grid_actions_column": "css=.grid-actions",
        }
        
        logger.info("V3 UserMaintenance page initialized")

    async def navigate_to_user_maintenance(
        self,
        base_url: Optional[str] = None,
    ) -> None:
        """
        Navigate directly to the User Maintenance page.
        
        Args:
            base_url: Optional base URL. If not provided, uses config.
            
        Raises:
            RaptorException: If navigation fails
            
        Example:
            >>> await user_maint.navigate_to_user_maintenance()
        """
        try:
            base = base_url or self.config.get("v3.base_url", "")
            url = f"{base}/user-maintenance"
            
            logger.info(f"Navigating to User Maintenance: {url}")
            await self.navigate(url)
            await self.wait_for_page_load()
            
            logger.info("Successfully navigated to User Maintenance")
            
        except Exception as e:
            logger.error(f"Failed to navigate to User Maintenance: {str(e)}")
            raise RaptorException(
                f"Failed to navigate to User Maintenance: {str(e)}",
                context={"base_url": base_url},
                cause=e
            )

    async def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """
        Wait for User Maintenance page to fully load.
        
        Args:
            timeout: Optional timeout in milliseconds
            
        Raises:
            TimeoutException: If page doesn't load within timeout
        """
        try:
            logger.debug("Waiting for User Maintenance page to load")
            
            await self.wait_for_load(state="load", timeout=timeout)
            
            # Wait for key elements
            await self.element_manager.wait_for_element(
                self.locators["page_title"],
                timeout=timeout or self.config.get_timeout("element")
            )
            
            await self.element_manager.wait_for_element(
                self.locators["user_grid"],
                timeout=timeout or self.config.get_timeout("element")
            )
            
            logger.info("User Maintenance page loaded successfully")
            
        except Exception as e:
            logger.error(f"User Maintenance page load failed: {str(e)}")
            raise

    async def create_user(self, user_data: Dict[str, Any]) -> None:
        """
        Create a new user with the provided data.
        
        Args:
            user_data: Dictionary containing user information:
                - username: User's login name (required)
                - email: User's email address (required)
                - first_name: User's first name
                - last_name: User's last name
                - role: User's role/permission level
                - status: User's status (Active/Inactive)
                - department: User's department
                - phone: User's phone number
                
        Raises:
            RaptorException: If user creation fails
            
        Example:
            >>> await user_maint.create_user({
            ...     "username": "jdoe",
            ...     "email": "jdoe@example.com",
            ...     "first_name": "John",
            ...     "last_name": "Doe",
            ...     "role": "Admin",
            ...     "status": "Active"
            ... })
        """
        try:
            logger.info(f"Creating user: {user_data.get('username')}")
            
            # Click create user button
            await self.element_manager.click(self.locators["create_user_button"])
            
            # Wait for form to appear
            await self.element_manager.wait_for_element(self.locators["user_form"])
            
            # Fill in user data
            await self._fill_user_form(user_data)
            
            # Click save button
            await self.element_manager.click(self.locators["save_button"])
            
            # Wait for success message
            await self._wait_for_success_message()
            
            logger.info(f"User created successfully: {user_data.get('username')}")
            
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise RaptorException(
                f"Failed to create user: {str(e)}",
                context={"user_data": user_data},
                cause=e
            )

    async def edit_user(
        self,
        username: str,
        updated_data: Dict[str, Any],
    ) -> None:
        """
        Edit an existing user's information.
        
        Args:
            username: Username of the user to edit
            updated_data: Dictionary containing fields to update
            
        Raises:
            RaptorException: If user edit fails
            
        Example:
            >>> await user_maint.edit_user("jdoe", {
            ...     "email": "john.doe@example.com",
            ...     "role": "Super Admin"
            ... })
        """
        try:
            logger.info(f"Editing user: {username}")
            
            # Search for and select the user
            await self.search_user(username)
            await self._select_user_in_grid(username)
            
            # Click edit button
            await self.element_manager.click(self.locators["edit_user_button"])
            
            # Wait for form to appear
            await self.element_manager.wait_for_element(self.locators["user_form"])
            
            # Fill in updated data
            await self._fill_user_form(updated_data)
            
            # Click save button
            await self.element_manager.click(self.locators["save_button"])
            
            # Wait for success message
            await self._wait_for_success_message()
            
            logger.info(f"User edited successfully: {username}")
            
        except Exception as e:
            logger.error(f"Failed to edit user: {str(e)}")
            raise RaptorException(
                f"Failed to edit user: {str(e)}",
                context={"username": username, "updated_data": updated_data},
                cause=e
            )

    async def delete_user(self, username: str, confirm: bool = True) -> None:
        """
        Delete a user from the system.
        
        Args:
            username: Username of the user to delete
            confirm: Whether to confirm the deletion (default: True)
            
        Raises:
            RaptorException: If user deletion fails
            
        Example:
            >>> await user_maint.delete_user("jdoe")
        """
        try:
            logger.info(f"Deleting user: {username}")
            
            # Search for and select the user
            await self.search_user(username)
            await self._select_user_in_grid(username)
            
            # Click delete button
            await self.element_manager.click(self.locators["delete_user_button"])
            
            # Wait for confirmation dialog
            await self.element_manager.wait_for_element(
                self.locators["confirm_dialog"]
            )
            
            # Confirm or cancel deletion
            if confirm:
                await self.element_manager.click(self.locators["confirm_yes_button"])
                await self._wait_for_success_message()
                logger.info(f"User deleted successfully: {username}")
            else:
                await self.element_manager.click(self.locators["confirm_no_button"])
                logger.info(f"User deletion cancelled: {username}")
            
        except Exception as e:
            logger.error(f"Failed to delete user: {str(e)}")
            raise RaptorException(
                f"Failed to delete user: {str(e)}",
                context={"username": username},
                cause=e
            )

    async def search_user(self, search_term: str) -> None:
        """
        Search for users using the search box.
        
        Args:
            search_term: Search term (username, email, name, etc.)
            
        Raises:
            RaptorException: If search fails
            
        Example:
            >>> await user_maint.search_user("john")
        """
        try:
            logger.info(f"Searching for user: {search_term}")
            
            # Clear existing search
            await self.element_manager.fill(self.locators["search_box"], "")
            
            # Enter search term
            await self.element_manager.fill(
                self.locators["search_box"],
                search_term
            )
            
            # Click search button
            await self.element_manager.click(self.locators["search_button"])
            
            # Wait for grid to update
            await self.page.wait_for_timeout(1000)  # Wait for search results
            
            logger.info(f"Search completed for: {search_term}")
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise RaptorException(
                f"Failed to search for user: {str(e)}",
                context={"search_term": search_term},
                cause=e
            )

    async def clear_search(self) -> None:
        """
        Clear the search and show all users.
        
        Raises:
            RaptorException: If clear search fails
            
        Example:
            >>> await user_maint.clear_search()
        """
        try:
            logger.info("Clearing search")
            
            await self.element_manager.click(self.locators["clear_search_button"])
            
            # Wait for grid to refresh
            await self.page.wait_for_timeout(1000)
            
            logger.info("Search cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear search: {str(e)}")
            raise RaptorException(
                f"Failed to clear search: {str(e)}",
                cause=e
            )

    async def get_user_details(self, username: str) -> Dict[str, str]:
        """
        Get details of a user from the grid.
        
        Args:
            username: Username to retrieve details for
            
        Returns:
            Dictionary containing user details from the grid
            
        Raises:
            RaptorException: If unable to retrieve user details
            
        Example:
            >>> details = await user_maint.get_user_details("jdoe")
            >>> print(details["email"])
        """
        try:
            logger.info(f"Getting details for user: {username}")
            
            # Search for the user
            await self.search_user(username)
            
            # Find the row in the grid
            row_index = await self.table_manager.find_row_by_key(
                self.locators["user_grid"],
                key_column=0,  # Assuming username is in first column
                key_value=username
            )
            
            if row_index == -1:
                raise RaptorException(
                    f"User not found in grid: {username}",
                    context={"username": username}
                )
            
            # Extract user details from the row
            details = {
                "username": await self.table_manager.get_cell_value(
                    self.locators["user_grid"],
                    row_index,
                    0
                ),
                "email": await self.table_manager.get_cell_value(
                    self.locators["user_grid"],
                    row_index,
                    1
                ),
                "role": await self.table_manager.get_cell_value(
                    self.locators["user_grid"],
                    row_index,
                    2
                ),
                "status": await self.table_manager.get_cell_value(
                    self.locators["user_grid"],
                    row_index,
                    3
                ),
            }
            
            logger.info(f"Retrieved details for user: {username}")
            return details
            
        except Exception as e:
            logger.error(f"Failed to get user details: {str(e)}")
            raise RaptorException(
                f"Failed to get user details: {str(e)}",
                context={"username": username},
                cause=e
            )

    async def refresh_user_grid(self) -> None:
        """
        Refresh the user grid to show latest data.
        
        Raises:
            RaptorException: If refresh fails
            
        Example:
            >>> await user_maint.refresh_user_grid()
        """
        try:
            logger.info("Refreshing user grid")
            
            await self.element_manager.click(self.locators["refresh_button"])
            
            # Wait for grid to refresh
            await self.page.wait_for_timeout(1000)
            
            logger.info("User grid refreshed")
            
        except Exception as e:
            logger.error(f"Failed to refresh user grid: {str(e)}")
            raise RaptorException(
                f"Failed to refresh user grid: {str(e)}",
                cause=e
            )

    async def _fill_user_form(self, user_data: Dict[str, Any]) -> None:
        """
        Fill in the user form with provided data.
        
        This is a helper method that fills in form fields based on
        the provided user data dictionary.
        
        Args:
            user_data: Dictionary containing user information
            
        Raises:
            RaptorException: If form filling fails
        """
        try:
            logger.debug("Filling user form")
            
            # Fill username if provided
            if "username" in user_data:
                await self.element_manager.fill(
                    self.locators["username_field"],
                    user_data["username"]
                )
            
            # Fill email if provided
            if "email" in user_data:
                await self.element_manager.fill(
                    self.locators["email_field"],
                    user_data["email"]
                )
            
            # Fill first name if provided
            if "first_name" in user_data:
                await self.element_manager.fill(
                    self.locators["first_name_field"],
                    user_data["first_name"]
                )
            
            # Fill last name if provided
            if "last_name" in user_data:
                await self.element_manager.fill(
                    self.locators["last_name_field"],
                    user_data["last_name"]
                )
            
            # Select role if provided
            if "role" in user_data:
                await self.element_manager.select_option(
                    self.locators["role_dropdown"],
                    user_data["role"]
                )
            
            # Select status if provided
            if "status" in user_data:
                await self.element_manager.select_option(
                    self.locators["status_dropdown"],
                    user_data["status"]
                )
            
            # Fill department if provided
            if "department" in user_data:
                await self.element_manager.fill(
                    self.locators["department_field"],
                    user_data["department"]
                )
            
            # Fill phone if provided
            if "phone" in user_data:
                await self.element_manager.fill(
                    self.locators["phone_field"],
                    user_data["phone"]
                )
            
            logger.debug("User form filled successfully")
            
        except Exception as e:
            logger.error(f"Failed to fill user form: {str(e)}")
            raise RaptorException(
                f"Failed to fill user form: {str(e)}",
                context={"user_data": user_data},
                cause=e
            )

    async def _select_user_in_grid(self, username: str) -> None:
        """
        Select a user row in the grid by username.
        
        Args:
            username: Username to select
            
        Raises:
            RaptorException: If user selection fails
        """
        try:
            logger.debug(f"Selecting user in grid: {username}")
            
            # Find the row
            row_index = await self.table_manager.find_row_by_key(
                self.locators["user_grid"],
                key_column=0,
                key_value=username
            )
            
            if row_index == -1:
                raise RaptorException(
                    f"User not found in grid: {username}",
                    context={"username": username}
                )
            
            # Click the row to select it
            await self.table_manager.click_cell(
                self.locators["user_grid"],
                row_index,
                0
            )
            
            logger.debug(f"User selected: {username}")
            
        except Exception as e:
            logger.error(f"Failed to select user in grid: {str(e)}")
            raise RaptorException(
                f"Failed to select user in grid: {str(e)}",
                context={"username": username},
                cause=e
            )

    async def _wait_for_success_message(self, timeout: Optional[int] = None) -> None:
        """
        Wait for success message to appear after an operation.
        
        Args:
            timeout: Optional timeout in milliseconds
            
        Raises:
            TimeoutException: If success message doesn't appear
        """
        try:
            logger.debug("Waiting for success message")
            
            await self.element_manager.wait_for_element(
                self.locators["success_message"],
                timeout=timeout or 5000
            )
            
            # Get the message text for logging
            message = await self.element_manager.get_text(
                self.locators["success_message"]
            )
            
            logger.info(f"Success message: {message}")
            
        except Exception as e:
            logger.error(f"Success message not found: {str(e)}")
            raise
