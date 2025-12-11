"""
V3 Sales Rep Profile Page Object for RAPTOR Python Playwright Framework.

This module provides the page object for the V3 Sales Rep Profile module,
including sales representative management, profile configuration, and performance tracking.
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


class SalesRepProfile(BasePage):
    """
    Page Object for V3 Sales Rep Profile Module.
    
    This class provides methods to interact with the Sales Rep Profile module,
    including:
    - Creating and managing sales representative profiles
    - Configuring sales territories
    - Managing commission structures
    - Tracking sales performance
    - Assigning customers to sales reps
    - Viewing sales history and metrics
    
    Example:
        >>> sales_rep = SalesRepProfile(page, element_manager)
        >>> await sales_rep.navigate_to_sales_rep_profile()
        >>> await sales_rep.create_sales_rep({
        ...     "name": "John Smith",
        ...     "email": "jsmith@example.com",
        ...     "territory": "Northeast",
        ...     "commission_rate": "5.5"
        ... })
    """

    def __init__(
        self,
        page: Page,
        element_manager: Optional[ElementManager] = None,
        config: Optional[ConfigManager] = None,
    ):
        """
        Initialize the Sales Rep Profile Page.

        Args:
            page: Playwright Page instance
            element_manager: Optional ElementManager instance
            config: Optional ConfigManager instance
        """
        super().__init__(page, element_manager, config)
        
        # Initialize table manager for sales rep grid
        self.table_manager = TableManager(page, self.element_manager)
        
        # Define locators for sales rep profile elements
        self.locators = {
            # Page elements
            "page_title": "css=.page-title",
            "sales_rep_grid": "css=#sales-rep-grid",
            "performance_panel": "css=#performance-panel",
            "territory_map": "css=#territory-map",
            
            # Search elements
            "search_box": "css=#sales-rep-search",
            "search_button": "css=#search-button",
            "clear_search_button": "css=#clear-search",
            "territory_filter": "css=#territory-filter",
            "status_filter": "css=#status-filter",
            
            # Action buttons
            "create_rep_button": "css=#create-rep-button",
            "edit_rep_button": "css=#edit-rep-button",
            "delete_rep_button": "css=#delete-rep-button",
            "assign_customer_button": "css=#assign-customer-button",
            "view_performance_button": "css=#view-performance-button",
            "refresh_button": "css=#refresh-button",
            "export_button": "css=#export-button",
            
            # Sales rep form elements
            "rep_form": "css=#rep-form",
            "rep_name_field": "css=#rep-name",
            "rep_email_field": "css=#rep-email",
            "rep_phone_field": "css=#rep-phone",
            "territory_dropdown": "css=#territory",
            "manager_dropdown": "css=#manager",
            "commission_rate_field": "css=#commission-rate",
            "quota_field": "css=#quota",
            "start_date_field": "css=#start-date",
            "status_dropdown": "css=#status",
            
            # Customer assignment
            "customer_assignment_form": "css=#customer-assignment-form",
            "customer_search": "css=#customer-search",
            "available_customers_list": "css=#available-customers",
            "assigned_customers_list": "css=#assigned-customers",
            "assign_button": "css=#assign-button",
            "unassign_button": "css=#unassign-button",
            
            # Performance metrics
            "total_sales": "css=#total-sales",
            "quota_achievement": "css=#quota-achievement",
            "customer_count": "css=#customer-count",
            "avg_deal_size": "css=#avg-deal-size",
            "performance_chart": "css=#performance-chart",
            
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
            
            # Grid columns
            "grid_rep_name_column": "css=.grid-rep-name",
            "grid_territory_column": "css=.grid-territory",
            "grid_quota_column": "css=.grid-quota",
            "grid_sales_column": "css=.grid-sales",
            "grid_status_column": "css=.grid-status",
        }
        
        logger.info("V3 SalesRepProfile page initialized")

    async def navigate_to_sales_rep_profile(
        self,
        base_url: Optional[str] = None,
    ) -> None:
        """
        Navigate directly to the Sales Rep Profile page.
        
        Args:
            base_url: Optional base URL. If not provided, uses config.
            
        Raises:
            RaptorException: If navigation fails
            
        Example:
            >>> await sales_rep.navigate_to_sales_rep_profile()
        """
        try:
            base = base_url or self.config.get("v3.base_url", "")
            url = f"{base}/sales-rep-profile"
            
            logger.info(f"Navigating to Sales Rep Profile: {url}")
            await self.navigate(url)
            await self.wait_for_page_load()
            
            logger.info("Successfully navigated to Sales Rep Profile")
            
        except Exception as e:
            logger.error(f"Failed to navigate to Sales Rep Profile: {str(e)}")
            raise RaptorException(
                f"Failed to navigate to Sales Rep Profile: {str(e)}",
                context={"base_url": base_url},
                cause=e
            )

    async def wait_for_page_load(self, timeout: Optional[int] = None) -> None:
        """
        Wait for Sales Rep Profile page to fully load.
        
        Args:
            timeout: Optional timeout in milliseconds
            
        Raises:
            TimeoutException: If page doesn't load within timeout
        """
        try:
            logger.debug("Waiting for Sales Rep Profile page to load")
            
            await self.wait_for_load(state="load", timeout=timeout)
            
            # Wait for key elements
            await self.element_manager.wait_for_element(
                self.locators["page_title"],
                timeout=timeout or self.config.get_timeout("element")
            )
            
            await self.element_manager.wait_for_element(
                self.locators["sales_rep_grid"],
                timeout=timeout or self.config.get_timeout("element")
            )
            
            logger.info("Sales Rep Profile page loaded successfully")
            
        except Exception as e:
            logger.error(f"Sales Rep Profile page load failed: {str(e)}")
            raise

    async def create_sales_rep(self, rep_data: Dict[str, Any]) -> None:
        """
        Create a new sales representative profile with the provided data.
        
        Args:
            rep_data: Dictionary containing sales rep information:
                - name: Sales rep name (required)
                - email: Sales rep email (required)
                - phone: Phone number
                - territory: Sales territory
                - manager: Manager name
                - commission_rate: Commission percentage
                - quota: Sales quota
                - start_date: Start date
                - status: Status (Active/Inactive)
                
        Raises:
            RaptorException: If sales rep creation fails
            
        Example:
            >>> await sales_rep.create_sales_rep({
            ...     "name": "Jane Doe",
            ...     "email": "jdoe@example.com",
            ...     "territory": "West Coast",
            ...     "commission_rate": "6.0",
            ...     "quota": "500000"
            ... })
        """
        try:
            logger.info(f"Creating sales rep: {rep_data.get('name')}")
            
            # Click create sales rep button
            await self.element_manager.click(self.locators["create_rep_button"])
            
            # Wait for form to appear
            await self.element_manager.wait_for_element(self.locators["rep_form"])
            
            # Fill in sales rep data
            await self._fill_sales_rep_form(rep_data)
            
            # Click save button
            await self.element_manager.click(self.locators["save_button"])
            
            # Wait for success message
            await self._wait_for_success_message()
            
            logger.info(f"Sales rep created successfully: {rep_data.get('name')}")
            
        except Exception as e:
            logger.error(f"Failed to create sales rep: {str(e)}")
            raise RaptorException(
                f"Failed to create sales rep: {str(e)}",
                context={"rep_data": rep_data},
                cause=e
            )

    async def edit_sales_rep(
        self,
        rep_name: str,
        updated_data: Dict[str, Any],
    ) -> None:
        """
        Edit an existing sales representative's information.
        
        Args:
            rep_name: Name of the sales rep to edit
            updated_data: Dictionary containing fields to update
            
        Raises:
            RaptorException: If sales rep edit fails
            
        Example:
            >>> await sales_rep.edit_sales_rep("Jane Doe", {
            ...     "commission_rate": "7.0",
            ...     "quota": "600000"
            ... })
        """
        try:
            logger.info(f"Editing sales rep: {rep_name}")
            
            # Search for and select the sales rep
            await self.search_sales_rep(rep_name)
            await self._select_sales_rep_in_grid(rep_name)
            
            # Click edit button
            await self.element_manager.click(self.locators["edit_rep_button"])
            
            # Wait for form to appear
            await self.element_manager.wait_for_element(self.locators["rep_form"])
            
            # Fill in updated data
            await self._fill_sales_rep_form(updated_data)
            
            # Click save button
            await self.element_manager.click(self.locators["save_button"])
            
            # Wait for success message
            await self._wait_for_success_message()
            
            logger.info(f"Sales rep edited successfully: {rep_name}")
            
        except Exception as e:
            logger.error(f"Failed to edit sales rep: {str(e)}")
            raise RaptorException(
                f"Failed to edit sales rep: {str(e)}",
                context={"rep_name": rep_name, "updated_data": updated_data},
                cause=e
            )

    async def delete_sales_rep(self, rep_name: str, confirm: bool = True) -> None:
        """
        Delete a sales representative from the system.
        
        Args:
            rep_name: Name of the sales rep to delete
            confirm: Whether to confirm the deletion (default: True)
            
        Raises:
            RaptorException: If sales rep deletion fails
            
        Example:
            >>> await sales_rep.delete_sales_rep("Old Rep")
        """
        try:
            logger.info(f"Deleting sales rep: {rep_name}")
            
            # Search for and select the sales rep
            await self.search_sales_rep(rep_name)
            await self._select_sales_rep_in_grid(rep_name)
            
            # Click delete button
            await self.element_manager.click(self.locators["delete_rep_button"])
            
            # Wait for confirmation dialog
            await self.element_manager.wait_for_element(
                self.locators["confirm_dialog"]
            )
            
            # Confirm or cancel deletion
            if confirm:
                await self.element_manager.click(self.locators["confirm_yes_button"])
                await self._wait_for_success_message()
                logger.info(f"Sales rep deleted successfully: {rep_name}")
            else:
                await self.element_manager.click(self.locators["confirm_no_button"])
                logger.info(f"Sales rep deletion cancelled: {rep_name}")
            
        except Exception as e:
            logger.error(f"Failed to delete sales rep: {str(e)}")
            raise RaptorException(
                f"Failed to delete sales rep: {str(e)}",
                context={"rep_name": rep_name},
                cause=e
            )

    async def assign_customer_to_rep(
        self,
        rep_name: str,
        customer_name: str,
    ) -> None:
        """
        Assign a customer to a sales representative.
        
        Args:
            rep_name: Name of the sales rep
            customer_name: Name of the customer to assign
            
        Raises:
            RaptorException: If customer assignment fails
            
        Example:
            >>> await sales_rep.assign_customer_to_rep(
            ...     "Jane Doe",
            ...     "Acme Corporation"
            ... )
        """
        try:
            logger.info(f"Assigning customer {customer_name} to rep {rep_name}")
            
            # Select the sales rep
            await self.search_sales_rep(rep_name)
            await self._select_sales_rep_in_grid(rep_name)
            
            # Click assign customer button
            await self.element_manager.click(self.locators["assign_customer_button"])
            
            # Wait for assignment form
            await self.element_manager.wait_for_element(
                self.locators["customer_assignment_form"]
            )
            
            # Search for customer
            await self.element_manager.fill(
                self.locators["customer_search"],
                customer_name
            )
            
            # Wait for search results
            await self.page.wait_for_timeout(1000)
            
            # Select customer from available list and assign
            # (Simplified - actual implementation would interact with list)
            await self.element_manager.click(self.locators["assign_button"])
            
            # Wait for success message
            await self._wait_for_success_message()
            
            logger.info(f"Customer assigned successfully: {customer_name}")
            
        except Exception as e:
            logger.error(f"Failed to assign customer: {str(e)}")
            raise RaptorException(
                f"Failed to assign customer: {str(e)}",
                context={"rep_name": rep_name, "customer_name": customer_name},
                cause=e
            )

    async def search_sales_rep(self, search_term: str) -> None:
        """
        Search for sales representatives using the search box.
        
        Args:
            search_term: Search term (name, territory, etc.)
            
        Raises:
            RaptorException: If search fails
            
        Example:
            >>> await sales_rep.search_sales_rep("Jane")
        """
        try:
            logger.info(f"Searching for sales rep: {search_term}")
            
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
            await self.page.wait_for_timeout(1000)
            
            logger.info(f"Search completed for: {search_term}")
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise RaptorException(
                f"Failed to search for sales rep: {str(e)}",
                context={"search_term": search_term},
                cause=e
            )

    async def get_sales_rep_details(self, rep_name: str) -> Dict[str, str]:
        """
        Get details of a sales representative from the grid.
        
        Args:
            rep_name: Sales rep name to retrieve details for
            
        Returns:
            Dictionary containing sales rep details from the grid
            
        Raises:
            RaptorException: If unable to retrieve sales rep details
            
        Example:
            >>> details = await sales_rep.get_sales_rep_details("Jane Doe")
            >>> print(details["territory"])
        """
        try:
            logger.info(f"Getting details for sales rep: {rep_name}")
            
            # Search for the sales rep
            await self.search_sales_rep(rep_name)
            
            # Find the row in the grid
            row_index = await self.table_manager.find_row_by_key(
                self.locators["sales_rep_grid"],
                key_column=0,
                key_value=rep_name
            )
            
            if row_index == -1:
                raise RaptorException(
                    f"Sales rep not found in grid: {rep_name}",
                    context={"rep_name": rep_name}
                )
            
            # Extract sales rep details from the row
            details = {
                "name": await self.table_manager.get_cell_value(
                    self.locators["sales_rep_grid"],
                    row_index,
                    0
                ),
                "territory": await self.table_manager.get_cell_value(
                    self.locators["sales_rep_grid"],
                    row_index,
                    1
                ),
                "quota": await self.table_manager.get_cell_value(
                    self.locators["sales_rep_grid"],
                    row_index,
                    2
                ),
                "sales": await self.table_manager.get_cell_value(
                    self.locators["sales_rep_grid"],
                    row_index,
                    3
                ),
                "status": await self.table_manager.get_cell_value(
                    self.locators["sales_rep_grid"],
                    row_index,
                    4
                ),
            }
            
            logger.info(f"Retrieved details for sales rep: {rep_name}")
            return details
            
        except Exception as e:
            logger.error(f"Failed to get sales rep details: {str(e)}")
            raise RaptorException(
                f"Failed to get sales rep details: {str(e)}",
                context={"rep_name": rep_name},
                cause=e
            )

    async def get_performance_metrics(self, rep_name: str) -> Dict[str, Any]:
        """
        Get performance metrics for a sales representative.
        
        Args:
            rep_name: Name of the sales rep
            
        Returns:
            Dictionary containing performance metrics:
                - total_sales: Total sales amount
                - quota_achievement: Percentage of quota achieved
                - customer_count: Number of assigned customers
                - avg_deal_size: Average deal size
                
        Raises:
            RaptorException: If unable to retrieve metrics
            
        Example:
            >>> metrics = await sales_rep.get_performance_metrics("Jane Doe")
            >>> print(f"Quota achievement: {metrics['quota_achievement']}%")
        """
        try:
            logger.info(f"Getting performance metrics for: {rep_name}")
            
            # Select the sales rep
            await self.search_sales_rep(rep_name)
            await self._select_sales_rep_in_grid(rep_name)
            
            # Click view performance button
            await self.element_manager.click(self.locators["view_performance_button"])
            
            # Wait for performance panel
            await self.element_manager.wait_for_element(
                self.locators["performance_panel"]
            )
            
            # Extract metrics
            metrics = {
                "total_sales": await self.element_manager.get_text(
                    self.locators["total_sales"]
                ),
                "quota_achievement": await self.element_manager.get_text(
                    self.locators["quota_achievement"]
                ),
                "customer_count": await self.element_manager.get_text(
                    self.locators["customer_count"]
                ),
                "avg_deal_size": await self.element_manager.get_text(
                    self.locators["avg_deal_size"]
                ),
            }
            
            logger.info(f"Retrieved performance metrics for: {rep_name}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get performance metrics: {str(e)}")
            raise RaptorException(
                f"Failed to get performance metrics: {str(e)}",
                context={"rep_name": rep_name},
                cause=e
            )

    async def filter_by_territory(self, territory: str) -> None:
        """
        Filter sales representatives by territory.
        
        Args:
            territory: Territory name to filter by
            
        Raises:
            RaptorException: If filtering fails
            
        Example:
            >>> await sales_rep.filter_by_territory("West Coast")
        """
        try:
            logger.info(f"Filtering by territory: {territory}")
            
            await self.element_manager.select_option(
                self.locators["territory_filter"],
                territory
            )
            
            # Wait for grid to update
            await self.page.wait_for_timeout(1000)
            
            logger.info(f"Filtered by territory: {territory}")
            
        except Exception as e:
            logger.error(f"Failed to filter by territory: {str(e)}")
            raise RaptorException(
                f"Failed to filter by territory: {str(e)}",
                context={"territory": territory},
                cause=e
            )

    async def _fill_sales_rep_form(self, rep_data: Dict[str, Any]) -> None:
        """
        Fill in the sales rep form with provided data.
        
        Args:
            rep_data: Dictionary containing sales rep information
            
        Raises:
            RaptorException: If form filling fails
        """
        try:
            logger.debug("Filling sales rep form")
            
            if "name" in rep_data:
                await self.element_manager.fill(
                    self.locators["rep_name_field"],
                    rep_data["name"]
                )
            
            if "email" in rep_data:
                await self.element_manager.fill(
                    self.locators["rep_email_field"],
                    rep_data["email"]
                )
            
            if "phone" in rep_data:
                await self.element_manager.fill(
                    self.locators["rep_phone_field"],
                    rep_data["phone"]
                )
            
            if "territory" in rep_data:
                await self.element_manager.select_option(
                    self.locators["territory_dropdown"],
                    rep_data["territory"]
                )
            
            if "manager" in rep_data:
                await self.element_manager.select_option(
                    self.locators["manager_dropdown"],
                    rep_data["manager"]
                )
            
            if "commission_rate" in rep_data:
                await self.element_manager.fill(
                    self.locators["commission_rate_field"],
                    rep_data["commission_rate"]
                )
            
            if "quota" in rep_data:
                await self.element_manager.fill(
                    self.locators["quota_field"],
                    rep_data["quota"]
                )
            
            if "start_date" in rep_data:
                await self.element_manager.fill(
                    self.locators["start_date_field"],
                    rep_data["start_date"]
                )
            
            if "status" in rep_data:
                await self.element_manager.select_option(
                    self.locators["status_dropdown"],
                    rep_data["status"]
                )
            
            logger.debug("Sales rep form filled successfully")
            
        except Exception as e:
            logger.error(f"Failed to fill sales rep form: {str(e)}")
            raise

    async def _select_sales_rep_in_grid(self, rep_name: str) -> None:
        """
        Select a sales rep row in the grid by name.
        
        Args:
            rep_name: Sales rep name to select
            
        Raises:
            RaptorException: If sales rep selection fails
        """
        try:
            logger.debug(f"Selecting sales rep in grid: {rep_name}")
            
            row_index = await self.table_manager.find_row_by_key(
                self.locators["sales_rep_grid"],
                key_column=0,
                key_value=rep_name
            )
            
            if row_index == -1:
                raise RaptorException(
                    f"Sales rep not found in grid: {rep_name}",
                    context={"rep_name": rep_name}
                )
            
            await self.table_manager.click_cell(
                self.locators["sales_rep_grid"],
                row_index,
                0
            )
            
            logger.debug(f"Sales rep selected: {rep_name}")
            
        except Exception as e:
            logger.error(f"Failed to select sales rep in grid: {str(e)}")
            raise

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
            
            message = await self.element_manager.get_text(
                self.locators["success_message"]
            )
            
            logger.info(f"Success message: {message}")
            
        except Exception as e:
            logger.error(f"Success message not found: {str(e)}")
            raise
