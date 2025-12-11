"""
Table Manager for RAPTOR Python Playwright Framework.

This module provides specialized operations for interacting with HTML tables,
including row location, cell reading/writing, and table navigation.
"""

from typing import Optional, List, Dict, Any, Union
from playwright.async_api import Page, Locator
from raptor.core.element_manager import ElementManager
from raptor.core.exceptions import (
    ElementNotFoundException,
    ElementNotInteractableException,
    RaptorException,
)
from raptor.core.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)


class TableManager:
    """
    Manages table-specific operations with robust error handling.
    
    This class provides:
    - Row location by key column values
    - Cell value reading and writing
    - Cell interaction (click, hover, etc.)
    - Table size and structure queries
    - Search functionality with partial matching
    - Pagination support for multi-page tables
    
    The TableManager works with standard HTML tables (<table>, <tr>, <td>/<th>)
    and can handle various table structures including nested tables and
    tables with complex cell content.
    
    Example:
        >>> table_manager = TableManager(page, element_manager)
        >>> 
        >>> # Find a row by key value
        >>> row_index = await table_manager.find_row_by_key(
        ...     "css=#users-table",
        ...     key_column=0,
        ...     key_value="john.doe"
        ... )
        >>> 
        >>> # Read a cell value
        >>> email = await table_manager.get_cell_value(
        ...     "css=#users-table",
        ...     row=row_index,
        ...     column=2
        ... )
        >>> 
        >>> # Click a cell (e.g., edit button)
        >>> await table_manager.click_cell(
        ...     "css=#users-table",
        ...     row=row_index,
        ...     column=3
        ... )
    """

    def __init__(
        self,
        page: Page,
        element_manager: ElementManager,
        config_manager: Optional[ConfigManager] = None,
    ):
        """
        Initialize the TableManager.

        Args:
            page: Playwright Page instance
            element_manager: ElementManager for element operations
            config_manager: Optional ConfigManager for configuration
        """
        self.page = page
        self.element_manager = element_manager
        self.config = config_manager or ConfigManager()
        self.default_timeout = self.config.get("timeouts.default", 20000)

    async def find_row_by_key(
        self,
        table_locator: str,
        key_column: int,
        key_value: str,
        timeout: Optional[int] = None,
    ) -> int:
        """
        Find a table row by searching for a key value in a specific column.

        Args:
            table_locator: Locator for the table element
            key_column: Zero-based column index to search in
            key_value: Value to search for
            timeout: Optional timeout in milliseconds

        Returns:
            Zero-based row index where the key was found

        Raises:
            ElementNotFoundException: If the table or key value is not found
            TimeoutException: If operation exceeds timeout

        Example:
            >>> row_idx = await table_manager.find_row_by_key(
            ...     "css=#users-table",
            ...     key_column=0,
            ...     key_value="john.doe"
            ... )
        """
        timeout = timeout or self.default_timeout

        try:
            # Wait for table to be visible
            table = await self.element_manager.locate_element(table_locator)
            await table.wait_for(state="visible", timeout=timeout)

            # Get all rows (excluding header)
            rows_locator = table.locator("tbody tr")
            rows = await rows_locator.all()

            if not rows:
                raise ElementNotFoundException(
                    f"No rows found in table: {table_locator}"
                )

            # Search for the key value in the specified column
            for idx, row in enumerate(rows):
                cells = await row.locator("td, th").all()

                if key_column >= len(cells):
                    logger.warning(
                        f"Row {idx} has only {len(cells)} cells, "
                        f"cannot access column {key_column}"
                    )
                    continue

                cell_text = await cells[key_column].inner_text()
                cell_text = cell_text.strip()

                if cell_text == key_value:
                    logger.info(
                        f"Found key '{key_value}' at row {idx}, column {key_column}"
                    )
                    return idx

            raise ElementNotFoundException(
                f"Key value '{key_value}' not found in column {key_column} "
                f"of table: {table_locator}"
            )

        except Exception as e:
            logger.error(f"Error finding row by key: {e}")
            raise

    async def get_cell_value(
        self,
        table_locator: str,
        row: int,
        column: int,
        timeout: Optional[int] = None,
    ) -> str:
        """
        Get the text value of a specific table cell.

        Args:
            table_locator: Locator for the table element
            row: Zero-based row index
            column: Zero-based column index
            timeout: Optional timeout in milliseconds

        Returns:
            Text content of the cell

        Raises:
            ElementNotFoundException: If the table or cell is not found
            TimeoutException: If operation exceeds timeout

        Example:
            >>> value = await table_manager.get_cell_value(
            ...     "css=#users-table",
            ...     row=2,
            ...     column=1
            ... )
        """
        timeout = timeout or self.default_timeout

        try:
            # Wait for table to be visible
            table = await self.element_manager.locate_element(table_locator)
            await table.wait_for(state="visible", timeout=timeout)

            # Locate the specific cell
            cell_locator = f"tbody tr:nth-child({row + 1}) td:nth-child({column + 1}), " \
                          f"tbody tr:nth-child({row + 1}) th:nth-child({column + 1})"

            cell = table.locator(cell_locator).first
            await cell.wait_for(state="visible", timeout=timeout)

            cell_text = await cell.inner_text()
            logger.info(
                f"Retrieved cell value at row {row}, column {column}: '{cell_text}'"
            )

            return cell_text.strip()

        except Exception as e:
            logger.error(
                f"Error getting cell value at row {row}, column {column}: {e}"
            )
            raise ElementNotFoundException(
                f"Cell not found at row {row}, column {column} in table: {table_locator}"
            )

    async def set_cell_value(
        self,
        table_locator: str,
        row: int,
        column: int,
        value: str,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Set the value of an editable table cell.

        Args:
            table_locator: Locator for the table element
            row: Zero-based row index
            column: Zero-based column index
            value: Value to set
            timeout: Optional timeout in milliseconds

        Raises:
            ElementNotFoundException: If the table or cell is not found
            ElementNotInteractableException: If the cell is not editable
            TimeoutException: If operation exceeds timeout

        Example:
            >>> await table_manager.set_cell_value(
            ...     "css=#users-table",
            ...     row=2,
            ...     column=1,
            ...     value="new.email@example.com"
            ... )
        """
        timeout = timeout or self.default_timeout

        try:
            # Wait for table to be visible
            table = await self.element_manager.locate_element(table_locator)
            await table.wait_for(state="visible", timeout=timeout)

            # Locate the specific cell
            cell_locator = f"tbody tr:nth-child({row + 1}) td:nth-child({column + 1})"
            cell = table.locator(cell_locator).first

            # Try to find an input or editable element within the cell
            input_element = cell.locator("input, textarea, [contenteditable='true']").first

            if await input_element.count() > 0:
                # Cell contains an input element
                await input_element.fill(value)
                logger.info(
                    f"Set cell value at row {row}, column {column} to: '{value}'"
                )
            else:
                # Try double-clicking to make cell editable
                await cell.dblclick(timeout=timeout)
                await self.page.wait_for_timeout(500)  # Wait for edit mode

                # Try again to find input element
                input_element = cell.locator("input, textarea, [contenteditable='true']").first

                if await input_element.count() > 0:
                    await input_element.fill(value)
                    logger.info(
                        f"Set cell value at row {row}, column {column} to: '{value}' "
                        f"after double-click"
                    )
                else:
                    raise ElementNotInteractableException(
                        f"Cell at row {row}, column {column} is not editable"
                    )

        except Exception as e:
            logger.error(
                f"Error setting cell value at row {row}, column {column}: {e}"
            )
            raise

    async def click_cell(
        self,
        table_locator: str,
        row: int,
        column: int,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Click on a specific table cell.

        Args:
            table_locator: Locator for the table element
            row: Zero-based row index
            column: Zero-based column index
            timeout: Optional timeout in milliseconds

        Raises:
            ElementNotFoundException: If the table or cell is not found
            TimeoutException: If operation exceeds timeout

        Example:
            >>> await table_manager.click_cell(
            ...     "css=#users-table",
            ...     row=2,
            ...     column=4  # Click edit button in column 4
            ... )
        """
        timeout = timeout or self.default_timeout

        try:
            # Wait for table to be visible
            table = await self.element_manager.locate_element(table_locator)
            await table.wait_for(state="visible", timeout=timeout)

            # Locate the specific cell
            cell_locator = f"tbody tr:nth-child({row + 1}) td:nth-child({column + 1}), " \
                          f"tbody tr:nth-child({row + 1}) th:nth-child({column + 1})"

            cell = table.locator(cell_locator).first
            await cell.click(timeout=timeout)

            logger.info(f"Clicked cell at row {row}, column {column}")

        except Exception as e:
            logger.error(f"Error clicking cell at row {row}, column {column}: {e}")
            raise

    async def get_row_count(
        self,
        table_locator: str,
        timeout: Optional[int] = None,
    ) -> int:
        """
        Get the number of rows in a table (excluding header).

        Args:
            table_locator: Locator for the table element
            timeout: Optional timeout in milliseconds

        Returns:
            Number of rows in the table body

        Raises:
            ElementNotFoundException: If the table is not found
            TimeoutException: If operation exceeds timeout

        Example:
            >>> count = await table_manager.get_row_count("css=#users-table")
            >>> print(f"Table has {count} rows")
        """
        timeout = timeout or self.default_timeout

        try:
            # Wait for table to be visible
            table = await self.element_manager.locate_element(table_locator)
            await table.wait_for(state="visible", timeout=timeout)

            # Count rows in tbody
            row_count = await table.locator("tbody tr").count()

            logger.info(f"Table has {row_count} rows")
            return row_count

        except Exception as e:
            logger.error(f"Error getting row count: {e}")
            raise ElementNotFoundException(
                f"Could not get row count for table: {table_locator}"
            )

    async def search_table(
        self,
        table_locator: str,
        search_text: str,
        case_sensitive: bool = False,
        partial_match: bool = True,
        timeout: Optional[int] = None,
    ) -> List[int]:
        """
        Search for text in a table and return matching row indices.

        Args:
            table_locator: Locator for the table element
            search_text: Text to search for
            case_sensitive: Whether search should be case-sensitive
            partial_match: Whether to allow partial matches
            timeout: Optional timeout in milliseconds

        Returns:
            List of zero-based row indices where matches were found

        Raises:
            ElementNotFoundException: If the table is not found
            TimeoutException: If operation exceeds timeout

        Example:
            >>> matching_rows = await table_manager.search_table(
            ...     "css=#users-table",
            ...     search_text="john",
            ...     case_sensitive=False
            ... )
            >>> print(f"Found matches in rows: {matching_rows}")
        """
        timeout = timeout or self.default_timeout
        matching_rows = []

        try:
            # Wait for table to be visible
            table = await self.element_manager.locate_element(table_locator)
            await table.wait_for(state="visible", timeout=timeout)

            # Get all rows
            rows = await table.locator("tbody tr").all()

            # Prepare search text
            search_compare = search_text if case_sensitive else search_text.lower()

            # Search through each row
            for idx, row in enumerate(rows):
                row_text = await row.inner_text()
                row_compare = row_text if case_sensitive else row_text.lower()

                if partial_match:
                    if search_compare in row_compare:
                        matching_rows.append(idx)
                else:
                    if search_compare == row_compare.strip():
                        matching_rows.append(idx)

            logger.info(
                f"Found {len(matching_rows)} rows matching '{search_text}': {matching_rows}"
            )

            return matching_rows

        except Exception as e:
            logger.error(f"Error searching table: {e}")
            raise

    async def navigate_pagination(
        self,
        next_button_locator: str,
        timeout: Optional[int] = None,
    ) -> bool:
        """
        Navigate to the next page in a paginated table.

        Args:
            next_button_locator: Locator for the "next page" button
            timeout: Optional timeout in milliseconds

        Returns:
            True if navigation succeeded, False if already on last page

        Raises:
            ElementNotFoundException: If the next button is not found
            TimeoutException: If operation exceeds timeout

        Example:
            >>> while await table_manager.navigate_pagination("css=.next-page"):
            ...     # Process current page
            ...     await process_table_data()
        """
        timeout = timeout or self.default_timeout

        try:
            # Locate the next button
            next_button = await self.element_manager.locate_element(next_button_locator)

            # Check if button is enabled
            is_enabled = await next_button.is_enabled()

            if not is_enabled:
                logger.info("Next button is disabled - already on last page")
                return False

            # Click the next button
            await next_button.click(timeout=timeout)

            # Wait for page to update (wait for network idle or a short delay)
            await self.page.wait_for_load_state("networkidle", timeout=timeout)

            logger.info("Navigated to next page")
            return True

        except ElementNotFoundException:
            logger.info("Next button not found - assuming last page")
            return False
        except Exception as e:
            logger.error(f"Error navigating pagination: {e}")
            raise

    async def get_column_values(
        self,
        table_locator: str,
        column: int,
        timeout: Optional[int] = None,
    ) -> List[str]:
        """
        Get all values from a specific column.

        Args:
            table_locator: Locator for the table element
            column: Zero-based column index
            timeout: Optional timeout in milliseconds

        Returns:
            List of cell values from the specified column

        Raises:
            ElementNotFoundException: If the table is not found
            TimeoutException: If operation exceeds timeout

        Example:
            >>> emails = await table_manager.get_column_values(
            ...     "css=#users-table",
            ...     column=2
            ... )
        """
        timeout = timeout or self.default_timeout
        column_values = []

        try:
            # Wait for table to be visible
            table = await self.element_manager.locate_element(table_locator)
            await table.wait_for(state="visible", timeout=timeout)

            # Get all rows
            rows = await table.locator("tbody tr").all()

            # Extract values from the specified column
            for row in rows:
                cells = await row.locator("td, th").all()

                if column < len(cells):
                    cell_text = await cells[column].inner_text()
                    column_values.append(cell_text.strip())
                else:
                    logger.warning(
                        f"Row has only {len(cells)} cells, cannot access column {column}"
                    )
                    column_values.append("")

            logger.info(
                f"Retrieved {len(column_values)} values from column {column}"
            )

            return column_values

        except Exception as e:
            logger.error(f"Error getting column values: {e}")
            raise

    async def wait_for_table_update(
        self,
        table_locator: str,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Wait for a dynamic table to finish updating/loading.

        This method waits for the table to stabilize by checking that the row count
        remains constant for a short period. Useful for tables that load data
        asynchronously or update dynamically.

        Args:
            table_locator: Locator for the table element
            timeout: Optional timeout in milliseconds

        Raises:
            ElementNotFoundException: If the table is not found
            TimeoutException: If operation exceeds timeout

        Example:
            >>> await table_manager.wait_for_table_update("css=#dynamic-table")
            >>> # Now safe to read table data
            >>> row_count = await table_manager.get_row_count("css=#dynamic-table")
        """
        timeout = timeout or self.default_timeout
        stabilization_time = 500  # Wait for 500ms of stability

        try:
            # Wait for table to be visible
            table = await self.element_manager.locate_element(table_locator)
            await table.wait_for(state="visible", timeout=timeout)

            # Wait for network idle first
            try:
                await self.page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                # Network idle might timeout, continue anyway
                pass

            # Check for loading indicators
            loading_indicators = [
                ".loading",
                ".spinner",
                "[data-loading='true']",
                ".table-loading",
            ]

            for indicator in loading_indicators:
                try:
                    loader = self.page.locator(indicator)
                    if await loader.count() > 0:
                        await loader.wait_for(state="hidden", timeout=timeout)
                        logger.info(f"Waited for loading indicator: {indicator}")
                except Exception:
                    # Indicator not found or already hidden
                    pass

            # Wait for row count to stabilize
            previous_count = -1
            stable_iterations = 0
            max_iterations = 10

            for _ in range(max_iterations):
                current_count = await table.locator("tbody tr").count()

                if current_count == previous_count:
                    stable_iterations += 1
                    if stable_iterations >= 2:  # Stable for 2 checks
                        logger.info(
                            f"Table stabilized with {current_count} rows"
                        )
                        return
                else:
                    stable_iterations = 0
                    previous_count = current_count

                await self.page.wait_for_timeout(stabilization_time)

            logger.info(
                f"Table update wait completed after {max_iterations} iterations"
            )

        except Exception as e:
            logger.error(f"Error waiting for table update: {e}")
            raise

    async def scroll_table_into_view(
        self,
        table_locator: str,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Scroll a table into view, useful for tables that load content on scroll.

        Args:
            table_locator: Locator for the table element
            timeout: Optional timeout in milliseconds

        Raises:
            ElementNotFoundException: If the table is not found
            TimeoutException: If operation exceeds timeout

        Example:
            >>> await table_manager.scroll_table_into_view("css=#lazy-table")
        """
        timeout = timeout or self.default_timeout

        try:
            table = await self.element_manager.locate_element(table_locator)
            await table.scroll_into_view_if_needed(timeout=timeout)
            logger.info("Scrolled table into view")

            # Wait a moment for any lazy-loaded content
            await self.page.wait_for_timeout(500)

        except Exception as e:
            logger.error(f"Error scrolling table into view: {e}")
            raise

    async def load_all_dynamic_rows(
        self,
        table_locator: str,
        scroll_container_locator: Optional[str] = None,
        max_scrolls: int = 50,
        timeout: Optional[int] = None,
    ) -> int:
        """
        Load all rows in a dynamically loading table (infinite scroll).

        This method repeatedly scrolls to the bottom of the table or scroll container
        until no new rows are loaded or max_scrolls is reached.

        Args:
            table_locator: Locator for the table element
            scroll_container_locator: Optional locator for scroll container
                                     (if different from table)
            max_scrolls: Maximum number of scroll attempts
            timeout: Optional timeout in milliseconds

        Returns:
            Total number of rows loaded

        Raises:
            ElementNotFoundException: If the table is not found
            TimeoutException: If operation exceeds timeout

        Example:
            >>> total_rows = await table_manager.load_all_dynamic_rows(
            ...     "css=#infinite-scroll-table",
            ...     max_scrolls=100
            ... )
            >>> print(f"Loaded {total_rows} rows")
        """
        timeout = timeout or self.default_timeout

        try:
            # Wait for table to be visible
            table = await self.element_manager.locate_element(table_locator)
            await table.wait_for(state="visible", timeout=timeout)

            # Determine scroll target
            if scroll_container_locator:
                scroll_target = await self.element_manager.locate_element(
                    scroll_container_locator
                )
            else:
                scroll_target = table

            previous_row_count = 0
            scroll_attempts = 0
            no_change_count = 0

            while scroll_attempts < max_scrolls:
                # Get current row count
                current_row_count = await table.locator("tbody tr").count()

                # Check if new rows were loaded
                if current_row_count == previous_row_count:
                    no_change_count += 1
                    if no_change_count >= 3:  # No change for 3 attempts
                        logger.info(
                            f"No new rows loaded after {scroll_attempts} scrolls. "
                            f"Total rows: {current_row_count}"
                        )
                        return current_row_count
                else:
                    no_change_count = 0
                    logger.info(
                        f"Loaded {current_row_count - previous_row_count} new rows. "
                        f"Total: {current_row_count}"
                    )

                previous_row_count = current_row_count

                # Scroll to bottom
                await scroll_target.evaluate(
                    "(element) => element.scrollTop = element.scrollHeight"
                )

                # Wait for potential new content to load
                await self.page.wait_for_timeout(500)

                # Check for loading indicators
                try:
                    loading_indicator = self.page.locator(
                        ".loading, .spinner, [data-loading='true']"
                    )
                    if await loading_indicator.count() > 0:
                        await loading_indicator.wait_for(
                            state="hidden",
                            timeout=5000
                        )
                except Exception:
                    # No loading indicator or already hidden
                    pass

                scroll_attempts += 1

            logger.warning(
                f"Reached max scrolls ({max_scrolls}). "
                f"Total rows: {previous_row_count}"
            )
            return previous_row_count

        except Exception as e:
            logger.error(f"Error loading dynamic rows: {e}")
            raise

    async def get_pagination_info(
        self,
        current_page_locator: Optional[str] = None,
        total_pages_locator: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get pagination information from a paginated table.

        Args:
            current_page_locator: Optional locator for current page indicator
            total_pages_locator: Optional locator for total pages indicator
            timeout: Optional timeout in milliseconds

        Returns:
            Dictionary with pagination info:
            {
                'current_page': int or None,
                'total_pages': int or None,
                'has_next': bool,
                'has_previous': bool
            }

        Example:
            >>> info = await table_manager.get_pagination_info(
            ...     current_page_locator="css=.current-page",
            ...     total_pages_locator="css=.total-pages"
            ... )
            >>> print(f"Page {info['current_page']} of {info['total_pages']}")
        """
        timeout = timeout or self.default_timeout
        pagination_info = {
            "current_page": None,
            "total_pages": None,
            "has_next": False,
            "has_previous": False,
        }

        try:
            # Get current page
            if current_page_locator:
                try:
                    current_page_element = await self.element_manager.locate_element(
                        current_page_locator
                    )
                    current_page_text = await current_page_element.inner_text()
                    pagination_info["current_page"] = int(current_page_text.strip())
                except Exception as e:
                    logger.warning(f"Could not get current page: {e}")

            # Get total pages
            if total_pages_locator:
                try:
                    total_pages_element = await self.element_manager.locate_element(
                        total_pages_locator
                    )
                    total_pages_text = await total_pages_element.inner_text()
                    pagination_info["total_pages"] = int(total_pages_text.strip())
                except Exception as e:
                    logger.warning(f"Could not get total pages: {e}")

            # Check for next/previous buttons
            next_button_selectors = [
                ".next-page",
                "[aria-label='Next']",
                "button:has-text('Next')",
                ".pagination-next",
            ]

            for selector in next_button_selectors:
                try:
                    next_button = self.page.locator(selector).first
                    if await next_button.count() > 0:
                        pagination_info["has_next"] = await next_button.is_enabled()
                        break
                except Exception:
                    continue

            previous_button_selectors = [
                ".previous-page",
                "[aria-label='Previous']",
                "button:has-text('Previous')",
                ".pagination-previous",
            ]

            for selector in previous_button_selectors:
                try:
                    prev_button = self.page.locator(selector).first
                    if await prev_button.count() > 0:
                        pagination_info["has_previous"] = await prev_button.is_enabled()
                        break
                except Exception:
                    continue

            logger.info(f"Pagination info: {pagination_info}")
            return pagination_info

        except Exception as e:
            logger.error(f"Error getting pagination info: {e}")
            return pagination_info

    async def navigate_to_page(
        self,
        page_number: int,
        page_input_locator: Optional[str] = None,
        page_button_locator_template: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> bool:
        """
        Navigate to a specific page in a paginated table.

        Args:
            page_number: Page number to navigate to (1-based)
            page_input_locator: Optional locator for page number input field
            page_button_locator_template: Optional template for page button locator
                                         (use {page} as placeholder)
            timeout: Optional timeout in milliseconds

        Returns:
            True if navigation succeeded, False otherwise

        Example:
            >>> # Using page input
            >>> await table_manager.navigate_to_page(
            ...     5,
            ...     page_input_locator="css=.page-input"
            ... )
            >>> 
            >>> # Using page button
            >>> await table_manager.navigate_to_page(
            ...     5,
            ...     page_button_locator_template="css=button[data-page='{page}']"
            ... )
        """
        timeout = timeout or self.default_timeout

        try:
            if page_input_locator:
                # Use input field to navigate
                page_input = await self.element_manager.locate_element(
                    page_input_locator
                )
                await page_input.fill(str(page_number))
                await page_input.press("Enter")

                # Wait for page to load
                await self.page.wait_for_load_state("networkidle", timeout=timeout)

                logger.info(f"Navigated to page {page_number} using input field")
                return True

            elif page_button_locator_template:
                # Use page button to navigate
                page_button_locator = page_button_locator_template.replace(
                    "{page}", str(page_number)
                )
                page_button = await self.element_manager.locate_element(
                    page_button_locator
                )
                await page_button.click(timeout=timeout)

                # Wait for page to load
                await self.page.wait_for_load_state("networkidle", timeout=timeout)

                logger.info(f"Navigated to page {page_number} using button")
                return True

            else:
                logger.error(
                    "Either page_input_locator or page_button_locator_template "
                    "must be provided"
                )
                return False

        except Exception as e:
            logger.error(f"Error navigating to page {page_number}: {e}")
            return False
