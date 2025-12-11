"""
Element Manager for RAPTOR Python Playwright Framework.

This module provides robust element location and interaction capabilities with:
- Multiple locator strategies (CSS, XPath, text, role, ID)
- Automatic fallback locator mechanism
- Configurable wait and timeout handling
- Comprehensive error handling and logging
"""

from typing import Optional, List, Union, Dict, Any
from playwright.async_api import Page, Locator, TimeoutError as PlaywrightTimeoutError
from raptor.core.exceptions import (
    ElementNotFoundException,
    ElementNotInteractableException,
    TimeoutException,
    RaptorException,
)
from raptor.core.config_manager import ConfigManager
from raptor.core.soft_assertion_collector import SoftAssertionCollector
import logging
import asyncio

logger = logging.getLogger(__name__)


class ElementManager:
    """
    Manages element location and interaction with fallback strategies.
    
    This class provides:
    - Multiple locator strategy support (CSS, XPath, text, role, ID)
    - Automatic fallback when primary locator fails
    - Configurable timeouts and wait conditions
    - Comprehensive error handling with context preservation
    
    Example:
        >>> element_manager = ElementManager(page)
        >>> element = await element_manager.locate_element(
        ...     "css=#submit-button",
        ...     fallback_locators=["xpath=//button[@id='submit-button']", "text=Submit"]
        ... )
        >>> await element_manager.click("css=#submit-button")
    """

    def __init__(self, page: Page, config: Optional[ConfigManager] = None):
        """
        Initialize the Element Manager.

        Args:
            page: Playwright Page instance to interact with
            config: Optional ConfigManager instance for timeout configuration.
                   If not provided, default configuration will be used.
        """
        self.page = page
        self.config = config or ConfigManager()
        self._default_timeout = self.config.get_timeout("element")
        
        logger.info(f"ElementManager initialized with default timeout: {self._default_timeout}ms")

    def _parse_locator_strategy(self, locator_string: str) -> tuple[str, str]:
        """
        Parse a locator string into strategy and value.
        
        Supports formats:
        - "css=#element-id"
        - "xpath=//div[@class='test']"
        - "text=Click Me"
        - "role=button[name='Submit']"
        - "#element-id" (defaults to CSS)
        
        Args:
            locator_string: Locator string with optional strategy prefix
            
        Returns:
            Tuple of (strategy, value)
        """
        # Check for explicit strategy prefix
        if "=" in locator_string:
            parts = locator_string.split("=", 1)
            strategy = parts[0].lower().strip()
            value = parts[1].strip()
            
            # Validate strategy
            valid_strategies = ["css", "xpath", "text", "role", "id"]
            if strategy not in valid_strategies:
                logger.warning(
                    f"Unknown locator strategy '{strategy}', defaulting to CSS. "
                    f"Valid strategies: {valid_strategies}"
                )
                return "css", locator_string
            
            return strategy, value
        else:
            # Default to CSS selector
            return "css", locator_string

    def _create_playwright_locator(self, strategy: str, value: str) -> Locator:
        """
        Create a Playwright Locator object from strategy and value.
        
        Args:
            strategy: Locator strategy (css, xpath, text, role, id)
            value: Locator value
            
        Returns:
            Playwright Locator object
            
        Raises:
            RaptorException: If locator creation fails
        """
        try:
            if strategy == "css":
                return self.page.locator(f"css={value}")
            elif strategy == "xpath":
                return self.page.locator(f"xpath={value}")
            elif strategy == "text":
                return self.page.get_by_text(value)
            elif strategy == "role":
                # Parse role locator: role=button[name='Submit']
                if "[" in value:
                    role_type = value.split("[")[0].strip()
                    # Extract attributes from brackets
                    attrs_str = value.split("[")[1].rstrip("]")
                    attrs = {}
                    for attr in attrs_str.split(","):
                        if "=" in attr:
                            key, val = attr.split("=", 1)
                            attrs[key.strip()] = val.strip().strip("'\"")
                    return self.page.get_by_role(role_type, **attrs)
                else:
                    return self.page.get_by_role(value)
            elif strategy == "id":
                return self.page.locator(f"#{value}")
            else:
                raise RaptorException(
                    f"Unsupported locator strategy: {strategy}",
                    context={"strategy": strategy, "value": value}
                )
        except Exception as e:
            raise RaptorException(
                f"Failed to create locator with strategy '{strategy}': {str(e)}",
                context={"strategy": strategy, "value": value},
                cause=e
            )

    async def locate_element(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> Locator:
        """
        Locate an element using primary locator with automatic fallback.
        
        Attempts to locate element using the primary locator first. If that fails,
        tries each fallback locator in order until one succeeds or all fail.
        
        Args:
            locator: Primary locator string (e.g., "css=#submit", "xpath=//button")
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds (uses default if not provided)
            
        Returns:
            Playwright Locator object for the found element
            
        Raises:
            ElementNotFoundException: If element cannot be found with any locator
            
        Example:
            >>> element = await element_manager.locate_element(
            ...     "css=#submit-button",
            ...     fallback_locators=["xpath=//button[@id='submit-button']", "text=Submit"],
            ...     timeout=10000
            ... )
        """
        timeout_ms = timeout or self._default_timeout
        fallback_locators = fallback_locators or []
        
        # Try primary locator
        all_locators = [locator] + fallback_locators
        errors = []
        
        logger.debug(
            f"Attempting to locate element with {len(all_locators)} strategies. "
            f"Primary: {locator}, Fallbacks: {fallback_locators}"
        )
        
        for idx, loc_string in enumerate(all_locators):
            try:
                strategy, value = self._parse_locator_strategy(loc_string)
                playwright_locator = self._create_playwright_locator(strategy, value)
                
                logger.debug(
                    f"Trying locator {idx + 1}/{len(all_locators)}: "
                    f"strategy={strategy}, value={value}"
                )
                
                # Wait for element to be visible
                await playwright_locator.wait_for(
                    state="visible",
                    timeout=timeout_ms
                )
                
                logger.info(
                    f"Element located successfully using "
                    f"{'primary' if idx == 0 else f'fallback #{idx}'} locator: {loc_string}"
                )
                return playwright_locator
                
            except PlaywrightTimeoutError as e:
                error_msg = f"Locator {idx + 1} timed out: {loc_string}"
                errors.append(error_msg)
                logger.debug(error_msg)
                continue
            except Exception as e:
                error_msg = f"Locator {idx + 1} failed: {loc_string} - {str(e)}"
                errors.append(error_msg)
                logger.debug(error_msg)
                continue
        
        # All locators failed
        logger.error(
            f"Failed to locate element after trying {len(all_locators)} strategies. "
            f"Errors: {errors}"
        )
        
        raise ElementNotFoundException(
            locator=locator,
            fallback_locators=fallback_locators,
            timeout=timeout_ms,
            page_url=self.page.url
        )

    async def wait_for_element(
        self,
        locator: str,
        state: str = "visible",
        timeout: Optional[int] = None,
    ) -> Locator:
        """
        Wait for an element to reach a specific state.
        
        Args:
            locator: Locator string (e.g., "css=#submit", "xpath=//button")
            state: Element state to wait for ("visible", "hidden", "attached", "detached")
            timeout: Optional timeout in milliseconds (uses default if not provided)
            
        Returns:
            Playwright Locator object
            
        Raises:
            TimeoutException: If element doesn't reach desired state within timeout
            
        Example:
            >>> element = await element_manager.wait_for_element(
            ...     "css=#loading-spinner",
            ...     state="hidden",
            ...     timeout=5000
            ... )
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            strategy, value = self._parse_locator_strategy(locator)
            playwright_locator = self._create_playwright_locator(strategy, value)
            
            logger.debug(
                f"Waiting for element to be '{state}': {locator} "
                f"(timeout: {timeout_ms}ms)"
            )
            
            await playwright_locator.wait_for(state=state, timeout=timeout_ms)
            
            logger.info(f"Element reached '{state}' state: {locator}")
            return playwright_locator
            
        except PlaywrightTimeoutError as e:
            logger.error(
                f"Timeout waiting for element to be '{state}': {locator} "
                f"(timeout: {timeout_ms}ms)"
            )
            raise TimeoutException(
                operation=f"wait_for_element (state={state})",
                timeout_seconds=timeout_ms / 1000,
                additional_info={
                    "locator": locator,
                    "state": state,
                    "page_url": self.page.url
                }
            )
        except Exception as e:
            logger.error(f"Error waiting for element: {locator} - {str(e)}")
            raise RaptorException(
                f"Failed to wait for element: {str(e)}",
                context={
                    "locator": locator,
                    "state": state,
                    "timeout_ms": timeout_ms,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def is_visible(self, locator: str, timeout: Optional[int] = None) -> bool:
        """
        Check if an element is visible.
        
        Args:
            locator: Locator string
            timeout: Optional timeout in milliseconds
            
        Returns:
            True if element is visible, False otherwise
        """
        try:
            await self.wait_for_element(locator, state="visible", timeout=timeout)
            return True
        except (TimeoutException, ElementNotFoundException):
            return False

    async def is_hidden(self, locator: str, timeout: Optional[int] = None) -> bool:
        """
        Check if an element is hidden.
        
        Args:
            locator: Locator string
            timeout: Optional timeout in milliseconds
            
        Returns:
            True if element is hidden, False otherwise
        """
        try:
            await self.wait_for_element(locator, state="hidden", timeout=timeout)
            return True
        except (TimeoutException, ElementNotFoundException):
            return False

    async def get_element_count(self, locator: str) -> int:
        """
        Get the count of elements matching the locator.
        
        Args:
            locator: Locator string
            
        Returns:
            Number of matching elements
        """
        try:
            strategy, value = self._parse_locator_strategy(locator)
            playwright_locator = self._create_playwright_locator(strategy, value)
            count = await playwright_locator.count()
            logger.debug(f"Found {count} elements matching: {locator}")
            return count
        except Exception as e:
            logger.error(f"Error counting elements: {locator} - {str(e)}")
            return 0

    def get_default_timeout(self) -> int:
        """
        Get the default timeout value.
        
        Returns:
            Default timeout in milliseconds
        """
        return self._default_timeout

    def set_default_timeout(self, timeout_ms: int) -> None:
        """
        Set the default timeout value.
        
        Args:
            timeout_ms: Timeout in milliseconds
        """
        if timeout_ms < 0:
            raise ValueError("Timeout must be a positive number")
        
        self._default_timeout = timeout_ms
        logger.info(f"Default timeout updated to: {timeout_ms}ms")

    async def click(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        **options
    ) -> None:
        """
        Click on an element.
        
        Locates the element and performs a click action. Supports fallback locators
        if the primary locator fails.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            **options: Additional Playwright click options (button, click_count, delay, etc.)
            
        Raises:
            ElementNotFoundException: If element cannot be found
            ElementNotInteractableException: If element cannot be clicked
            
        Example:
            >>> await element_manager.click("css=#submit-button")
            >>> await element_manager.click("text=Submit", button="right")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Attempting to click element: {locator}")
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Perform the click
            await element.click(timeout=timeout_ms, **options)
            
            logger.info(f"Successfully clicked element: {locator}")
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except Exception as e:
            logger.error(f"Failed to click element: {locator} - {str(e)}")
            raise ElementNotInteractableException(
                locator=locator,
                action="click",
                reason=str(e),
                page_url=self.page.url
            )

    async def fill(
        self,
        locator: str,
        text: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        **options
    ) -> None:
        """
        Fill text into an input element.
        
        Clears the existing value and types the new text into the element.
        
        Args:
            locator: Primary locator string
            text: Text to fill into the element
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            **options: Additional Playwright fill options (force, no_wait_after, etc.)
            
        Raises:
            ElementNotFoundException: If element cannot be found
            ElementNotInteractableException: If element cannot be filled
            
        Example:
            >>> await element_manager.fill("css=#username", "john.doe")
            >>> await element_manager.fill("xpath=//input[@name='email']", "test@example.com")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Attempting to fill element: {locator} with text: {text}")
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Fill the text
            await element.fill(text, timeout=timeout_ms, **options)
            
            logger.info(f"Successfully filled element: {locator}")
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except Exception as e:
            logger.error(f"Failed to fill element: {locator} - {str(e)}")
            raise ElementNotInteractableException(
                locator=locator,
                action="fill",
                reason=str(e),
                page_url=self.page.url
            )

    async def select_option(
        self,
        locator: str,
        value: Optional[Union[str, List[str]]] = None,
        label: Optional[Union[str, List[str]]] = None,
        index: Optional[Union[int, List[int]]] = None,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        **options
    ) -> List[str]:
        """
        Select option(s) from a dropdown/select element.
        
        Can select by value, label, or index. Returns the list of selected option values.
        
        Args:
            locator: Primary locator string
            value: Option value(s) to select
            label: Option label(s) to select
            index: Option index(es) to select
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            **options: Additional Playwright select options (force, no_wait_after, etc.)
            
        Returns:
            List of selected option values
            
        Raises:
            ElementNotFoundException: If element cannot be found
            ElementNotInteractableException: If option cannot be selected
            ValueError: If no selection criteria provided
            
        Example:
            >>> await element_manager.select_option("css=#country", value="US")
            >>> await element_manager.select_option("css=#colors", label=["Red", "Blue"])
            >>> await element_manager.select_option("css=#priority", index=0)
        """
        timeout_ms = timeout or self._default_timeout
        
        # Validate that at least one selection criteria is provided
        if value is None and label is None and index is None:
            raise ValueError("Must provide at least one of: value, label, or index")
        
        try:
            logger.debug(
                f"Attempting to select option in element: {locator} "
                f"(value={value}, label={label}, index={index})"
            )
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Select the option(s)
            selected_values = await element.select_option(
                value=value,
                label=label,
                index=index,
                timeout=timeout_ms,
                **options
            )
            
            logger.info(
                f"Successfully selected option(s) in element: {locator} "
                f"(selected: {selected_values})"
            )
            
            return selected_values
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except Exception as e:
            logger.error(f"Failed to select option in element: {locator} - {str(e)}")
            raise ElementNotInteractableException(
                locator=locator,
                action="select_option",
                reason=str(e),
                page_url=self.page.url
            )

    async def hover(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        **options
    ) -> None:
        """
        Hover over an element.
        
        Moves the mouse cursor over the element, triggering hover effects.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            **options: Additional Playwright hover options (position, force, etc.)
            
        Raises:
            ElementNotFoundException: If element cannot be found
            ElementNotInteractableException: If element cannot be hovered
            
        Example:
            >>> await element_manager.hover("css=#menu-item")
            >>> await element_manager.hover("text=Products", position={"x": 10, "y": 10})
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Attempting to hover over element: {locator}")
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Perform the hover
            await element.hover(timeout=timeout_ms, **options)
            
            logger.info(f"Successfully hovered over element: {locator}")
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except Exception as e:
            logger.error(f"Failed to hover over element: {locator} - {str(e)}")
            raise ElementNotInteractableException(
                locator=locator,
                action="hover",
                reason=str(e),
                page_url=self.page.url
            )

    async def is_enabled(self, locator: str, timeout: Optional[int] = None) -> bool:
        """
        Check if an element is enabled (not disabled).
        
        Args:
            locator: Locator string
            timeout: Optional timeout in milliseconds
            
        Returns:
            True if element is enabled, False if disabled or not found
            
        Example:
            >>> enabled = await element_manager.is_enabled("css=#submit-button")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            strategy, value = self._parse_locator_strategy(locator)
            playwright_locator = self._create_playwright_locator(strategy, value)
            
            # Wait for element to be attached
            await playwright_locator.wait_for(state="attached", timeout=timeout_ms)
            
            # Check if enabled
            is_enabled = await playwright_locator.is_enabled(timeout=timeout_ms)
            
            logger.debug(f"Element enabled check: {locator} = {is_enabled}")
            return is_enabled
            
        except Exception as e:
            logger.debug(f"Element enabled check failed: {locator} - {str(e)}")
            return False

    async def click_at_position(
        self,
        locator: str,
        x: int,
        y: int,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        **options
    ) -> None:
        """
        Click at a specific position within an element (equivalent to clickXY).
        
        Useful when you need to click at a specific coordinate within an element,
        such as clicking on a specific point in a canvas or map.
        
        Args:
            locator: Primary locator string
            x: X coordinate relative to the element's top-left corner
            y: Y coordinate relative to the element's top-left corner
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            **options: Additional Playwright click options (button, click_count, delay, etc.)
            
        Raises:
            ElementNotFoundException: If element cannot be found
            ElementNotInteractableException: If element cannot be clicked
            
        Example:
            >>> await element_manager.click_at_position("css=#canvas", x=100, y=50)
            >>> await element_manager.click_at_position("css=#map", x=200, y=150, button="right")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(
                f"Attempting to click element at position ({x}, {y}): {locator}"
            )
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Perform the click at the specified position
            await element.click(
                position={"x": x, "y": y},
                timeout=timeout_ms,
                **options
            )
            
            logger.info(
                f"Successfully clicked element at position ({x}, {y}): {locator}"
            )
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except Exception as e:
            logger.error(
                f"Failed to click element at position ({x}, {y}): {locator} - {str(e)}"
            )
            raise ElementNotInteractableException(
                locator=locator,
                action=f"click_at_position(x={x}, y={y})",
                reason=str(e),
                page_url=self.page.url
            )

    async def double_click(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        **options
    ) -> None:
        """
        Double-click on an element.
        
        Performs two rapid clicks on the element, useful for actions like
        selecting text or opening items.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            **options: Additional Playwright click options (button, delay, position, etc.)
            
        Raises:
            ElementNotFoundException: If element cannot be found
            ElementNotInteractableException: If element cannot be double-clicked
            
        Example:
            >>> await element_manager.double_click("css=#file-item")
            >>> await element_manager.double_click("text=Document.txt")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Attempting to double-click element: {locator}")
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Perform the double-click
            await element.dblclick(timeout=timeout_ms, **options)
            
            logger.info(f"Successfully double-clicked element: {locator}")
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except Exception as e:
            logger.error(f"Failed to double-click element: {locator} - {str(e)}")
            raise ElementNotInteractableException(
                locator=locator,
                action="double_click",
                reason=str(e),
                page_url=self.page.url
            )

    async def right_click(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        **options
    ) -> None:
        """
        Right-click (context click) on an element.
        
        Opens the context menu for the element, equivalent to clicking with
        the right mouse button.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            **options: Additional Playwright click options (delay, position, etc.)
            
        Raises:
            ElementNotFoundException: If element cannot be found
            ElementNotInteractableException: If element cannot be right-clicked
            
        Example:
            >>> await element_manager.right_click("css=#context-menu-target")
            >>> await element_manager.right_click("text=File Item")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Attempting to right-click element: {locator}")
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Perform the right-click (context click)
            await element.click(button="right", timeout=timeout_ms, **options)
            
            logger.info(f"Successfully right-clicked element: {locator}")
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except Exception as e:
            logger.error(f"Failed to right-click element: {locator} - {str(e)}")
            raise ElementNotInteractableException(
                locator=locator,
                action="right_click",
                reason=str(e),
                page_url=self.page.url
            )

    async def click_if_exists(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        **options
    ) -> bool:
        """
        Conditionally click an element if it exists.
        
        Attempts to click the element but does not raise an exception if the
        element is not found. Returns True if clicked, False if not found.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds (shorter timeout recommended)
            **options: Additional Playwright click options (button, click_count, delay, etc.)
            
        Returns:
            True if element was found and clicked, False if element not found
            
        Raises:
            ElementNotInteractableException: If element exists but cannot be clicked
            
        Example:
            >>> clicked = await element_manager.click_if_exists("css=#optional-popup-close")
            >>> if clicked:
            ...     print("Popup was closed")
            >>> else:
            ...     print("No popup to close")
        """
        # Use shorter timeout for conditional operations (default 5 seconds)
        timeout_ms = timeout if timeout is not None else 5000
        
        try:
            logger.debug(f"Attempting conditional click on element: {locator}")
            
            # Try to locate the element
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Perform the click
            await element.click(timeout=timeout_ms, **options)
            
            logger.info(f"Successfully clicked element (conditional): {locator}")
            return True
            
        except ElementNotFoundException:
            logger.debug(f"Element not found (conditional click): {locator}")
            return False
        except Exception as e:
            # Element exists but cannot be clicked - this is an error
            logger.error(
                f"Element found but failed to click (conditional): {locator} - {str(e)}"
            )
            raise ElementNotInteractableException(
                locator=locator,
                action="click_if_exists",
                reason=str(e),
                page_url=self.page.url
            )

    async def click_with_retry(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        timeout: Optional[int] = None,
        **options
    ) -> None:
        """
        Click an element with exponential backoff retry logic.
        
        Attempts to click the element multiple times with increasing delays
        between attempts. Useful for handling transient failures or elements
        that may be temporarily obscured.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            max_retries: Maximum number of retry attempts (default: 3)
            initial_delay: Initial delay in seconds before first retry (default: 1.0)
            timeout: Optional timeout in milliseconds for each attempt
            **options: Additional Playwright click options (button, click_count, delay, etc.)
            
        Raises:
            ElementNotFoundException: If element cannot be found after all retries
            ElementNotInteractableException: If element cannot be clicked after all retries
            
        Example:
            >>> await element_manager.click_with_retry("css=#flaky-button")
            >>> await element_manager.click_with_retry(
            ...     "css=#submit",
            ...     max_retries=5,
            ...     initial_delay=0.5
            ... )
        """
        timeout_ms = timeout or self._default_timeout
        
        if max_retries < 1:
            raise ValueError("max_retries must be at least 1")
        if initial_delay < 0:
            raise ValueError("initial_delay must be non-negative")
        
        last_exception = None
        delay = initial_delay
        
        for attempt in range(max_retries):
            try:
                logger.debug(
                    f"Attempting to click element (attempt {attempt + 1}/{max_retries}): "
                    f"{locator}"
                )
                
                # Locate the element with fallback support
                element = await self.locate_element(
                    locator,
                    fallback_locators=fallback_locators,
                    timeout=timeout_ms
                )
                
                # Perform the click
                await element.click(timeout=timeout_ms, **options)
                
                logger.info(
                    f"Successfully clicked element on attempt {attempt + 1}: {locator}"
                )
                return
                
            except (ElementNotFoundException, ElementNotInteractableException) as e:
                last_exception = e
                
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Click attempt {attempt + 1} failed: {locator} - {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    await asyncio.sleep(delay)
                    # Exponential backoff: double the delay for next attempt
                    delay *= 2
                else:
                    logger.error(
                        f"All {max_retries} click attempts failed: {locator}"
                    )
            except Exception as e:
                # Unexpected error - don't retry
                logger.error(
                    f"Unexpected error during click attempt {attempt + 1}: "
                    f"{locator} - {str(e)}"
                )
                raise ElementNotInteractableException(
                    locator=locator,
                    action="click_with_retry",
                    reason=str(e),
                    page_url=self.page.url
                )
        
        # All retries exhausted - raise the last exception
        if last_exception:
            raise last_exception

    async def get_text(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """
        Retrieve the text content of an element.
        
        Gets the inner text of the element, which is the text that would be
        visible to a user (excludes hidden elements and script/style content).
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            
        Returns:
            Text content of the element
            
        Raises:
            ElementNotFoundException: If element cannot be found
            RaptorException: If text cannot be retrieved
            
        Example:
            >>> text = await element_manager.get_text("css=#message")
            >>> print(f"Message: {text}")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Attempting to get text from element: {locator}")
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Get the text content
            text = await element.inner_text(timeout=timeout_ms)
            
            logger.info(
                f"Successfully retrieved text from element: {locator} "
                f"(length: {len(text)} chars)"
            )
            
            return text
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except Exception as e:
            logger.error(f"Failed to get text from element: {locator} - {str(e)}")
            raise RaptorException(
                f"Failed to retrieve text from element: {str(e)}",
                context={
                    "locator": locator,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def get_attribute(
        self,
        locator: str,
        attribute: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> Optional[str]:
        """
        Retrieve an attribute value from an element.
        
        Gets the value of the specified HTML attribute. Returns None if the
        attribute doesn't exist.
        
        Args:
            locator: Primary locator string
            attribute: Name of the attribute to retrieve (e.g., "href", "class", "id")
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            
        Returns:
            Attribute value as string, or None if attribute doesn't exist
            
        Raises:
            ElementNotFoundException: If element cannot be found
            RaptorException: If attribute cannot be retrieved
            
        Example:
            >>> href = await element_manager.get_attribute("css=#link", "href")
            >>> class_name = await element_manager.get_attribute("css=#button", "class")
            >>> disabled = await element_manager.get_attribute("css=#input", "disabled")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(
                f"Attempting to get attribute '{attribute}' from element: {locator}"
            )
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Get the attribute value
            value = await element.get_attribute(attribute, timeout=timeout_ms)
            
            logger.info(
                f"Successfully retrieved attribute '{attribute}' from element: {locator} "
                f"(value: {value})"
            )
            
            return value
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except Exception as e:
            logger.error(
                f"Failed to get attribute '{attribute}' from element: {locator} - {str(e)}"
            )
            raise RaptorException(
                f"Failed to retrieve attribute '{attribute}' from element: {str(e)}",
                context={
                    "locator": locator,
                    "attribute": attribute,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def get_value(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """
        Retrieve the value of an input element.
        
        Gets the current value of input, textarea, or select elements.
        This is equivalent to getting the "value" attribute but works
        consistently across different input types.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            
        Returns:
            Current value of the input element
            
        Raises:
            ElementNotFoundException: If element cannot be found
            RaptorException: If value cannot be retrieved
            
        Example:
            >>> username = await element_manager.get_value("css=#username")
            >>> email = await element_manager.get_value("xpath=//input[@name='email']")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Attempting to get value from element: {locator}")
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Get the input value
            value = await element.input_value(timeout=timeout_ms)
            
            logger.info(
                f"Successfully retrieved value from element: {locator} "
                f"(length: {len(value)} chars)"
            )
            
            return value
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except Exception as e:
            logger.error(f"Failed to get value from element: {locator} - {str(e)}")
            raise RaptorException(
                f"Failed to retrieve value from element: {str(e)}",
                context={
                    "locator": locator,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def get_location(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, float]:
        """
        Retrieve the coordinates and dimensions of an element.
        
        Gets the bounding box of the element, including its position (x, y)
        and size (width, height) relative to the viewport.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            
        Returns:
            Dictionary with keys: x, y, width, height
            
        Raises:
            ElementNotFoundException: If element cannot be found
            RaptorException: If location cannot be retrieved
            
        Example:
            >>> location = await element_manager.get_location("css=#button")
            >>> print(f"Button at ({location['x']}, {location['y']})")
            >>> print(f"Size: {location['width']}x{location['height']}")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Attempting to get location of element: {locator}")
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Get the bounding box
            bounding_box = await element.bounding_box(timeout=timeout_ms)
            
            if bounding_box is None:
                raise RaptorException(
                    "Element has no bounding box (may be hidden or not rendered)",
                    context={
                        "locator": locator,
                        "page_url": self.page.url
                    }
                )
            
            logger.info(
                f"Successfully retrieved location of element: {locator} "
                f"(x={bounding_box['x']}, y={bounding_box['y']}, "
                f"width={bounding_box['width']}, height={bounding_box['height']})"
            )
            
            return bounding_box
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except RaptorException:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to get location of element: {locator} - {str(e)}")
            raise RaptorException(
                f"Failed to retrieve location of element: {str(e)}",
                context={
                    "locator": locator,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def is_selected(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> bool:
        """
        Check if a checkbox or radio button is selected/checked.
        
        Determines whether the element (checkbox or radio button) is currently
        in a checked/selected state.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            
        Returns:
            True if element is checked/selected, False otherwise
            
        Raises:
            ElementNotFoundException: If element cannot be found
            RaptorException: If selection state cannot be determined
            
        Example:
            >>> is_checked = await element_manager.is_selected("css=#terms-checkbox")
            >>> if is_checked:
            ...     print("Terms accepted")
            >>> 
            >>> is_selected = await element_manager.is_selected("css=#option-radio")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Attempting to check selection state of element: {locator}")
            
            # Locate the element with fallback support
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Check if the element is checked
            is_checked = await element.is_checked(timeout=timeout_ms)
            
            logger.info(
                f"Successfully checked selection state of element: {locator} "
                f"(selected: {is_checked})"
            )
            
            return is_checked
            
        except ElementNotFoundException:
            # Re-raise element not found errors
            raise
        except Exception as e:
            logger.error(
                f"Failed to check selection state of element: {locator} - {str(e)}"
            )
            raise RaptorException(
                f"Failed to determine selection state of element: {str(e)}",
                context={
                    "locator": locator,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def wait_for_load_state(
        self,
        state: str = "load",
        timeout: Optional[int] = None,
    ) -> None:
        """
        Wait for the page to reach a specific load state.
        
        Waits for the page to reach one of the following states:
        - "load": Page load event fired (default)
        - "domcontentloaded": DOMContentLoaded event fired
        - "networkidle": No network connections for at least 500ms
        
        Args:
            state: Load state to wait for ("load", "domcontentloaded", "networkidle")
            timeout: Optional timeout in milliseconds (uses default if not provided)
            
        Raises:
            TimeoutException: If page doesn't reach desired state within timeout
            ValueError: If invalid state is provided
            
        Example:
            >>> await element_manager.wait_for_load_state("load")
            >>> await element_manager.wait_for_load_state("networkidle", timeout=30000)
        """
        timeout_ms = timeout or self._default_timeout
        
        valid_states = ["load", "domcontentloaded", "networkidle"]
        if state not in valid_states:
            raise ValueError(
                f"Invalid load state: {state}. Valid states: {valid_states}"
            )
        
        try:
            logger.debug(
                f"Waiting for page load state '{state}' (timeout: {timeout_ms}ms)"
            )
            
            await self.page.wait_for_load_state(state=state, timeout=timeout_ms)
            
            logger.info(f"Page reached load state: {state}")
            
        except PlaywrightTimeoutError as e:
            logger.error(
                f"Timeout waiting for page load state '{state}' "
                f"(timeout: {timeout_ms}ms)"
            )
            raise TimeoutException(
                operation=f"wait_for_load_state (state={state})",
                timeout_seconds=timeout_ms / 1000,
                additional_info={
                    "state": state,
                    "page_url": self.page.url
                }
            )
        except Exception as e:
            logger.error(f"Error waiting for page load state '{state}': {str(e)}")
            raise RaptorException(
                f"Failed to wait for page load state: {str(e)}",
                context={
                    "state": state,
                    "timeout_ms": timeout_ms,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def wait_for_spinner(
        self,
        spinner_locator: str,
        timeout: Optional[int] = None,
        check_interval: float = 0.5,
    ) -> None:
        """
        Wait for a loading spinner or indicator to disappear.
        
        Waits for the specified loading indicator element to become hidden or
        detached from the DOM. This is useful for waiting for page content to
        finish loading after an action.
        
        Args:
            spinner_locator: Locator string for the loading spinner/indicator
            timeout: Optional timeout in milliseconds (uses default if not provided)
            check_interval: Interval in seconds between visibility checks (default: 0.5)
            
        Raises:
            TimeoutException: If spinner doesn't disappear within timeout
            
        Example:
            >>> await element_manager.wait_for_spinner("css=#loading-spinner")
            >>> await element_manager.wait_for_spinner("css=.loading-overlay", timeout=10000)
            >>> await element_manager.wait_for_spinner("xpath=//div[@class='spinner']")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(
                f"Waiting for spinner to disappear: {spinner_locator} "
                f"(timeout: {timeout_ms}ms)"
            )
            
            strategy, value = self._parse_locator_strategy(spinner_locator)
            playwright_locator = self._create_playwright_locator(strategy, value)
            
            # First check if spinner exists at all
            count = await playwright_locator.count()
            
            if count == 0:
                logger.debug(f"Spinner not found (already gone): {spinner_locator}")
                return
            
            # Wait for spinner to be hidden or detached
            try:
                await playwright_locator.wait_for(state="hidden", timeout=timeout_ms)
                logger.info(f"Spinner disappeared: {spinner_locator}")
            except PlaywrightTimeoutError:
                # Try waiting for detached state as fallback
                try:
                    await playwright_locator.wait_for(state="detached", timeout=1000)
                    logger.info(f"Spinner detached from DOM: {spinner_locator}")
                except PlaywrightTimeoutError:
                    # Spinner still visible/attached - raise timeout
                    raise
            
        except PlaywrightTimeoutError as e:
            logger.error(
                f"Timeout waiting for spinner to disappear: {spinner_locator} "
                f"(timeout: {timeout_ms}ms)"
            )
            raise TimeoutException(
                operation="wait_for_spinner",
                timeout_seconds=timeout_ms / 1000,
                additional_info={
                    "spinner_locator": spinner_locator,
                    "page_url": self.page.url
                }
            )
        except Exception as e:
            logger.error(
                f"Error waiting for spinner to disappear: {spinner_locator} - {str(e)}"
            )
            raise RaptorException(
                f"Failed to wait for spinner: {str(e)}",
                context={
                    "spinner_locator": spinner_locator,
                    "timeout_ms": timeout_ms,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def wait_for_disabled_pane(
        self,
        pane_locator: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Wait for a disabled pane or modal dialog to disappear.
        
        Waits for modal dialogs, overlays, or disabled panes to be removed from
        the page. If no locator is provided, waits for common modal patterns.
        
        Args:
            pane_locator: Optional locator string for the disabled pane/modal.
                         If not provided, waits for common modal patterns.
            timeout: Optional timeout in milliseconds (uses default if not provided)
            
        Raises:
            TimeoutException: If pane doesn't disappear within timeout
            
        Example:
            >>> await element_manager.wait_for_disabled_pane("css=.modal-overlay")
            >>> await element_manager.wait_for_disabled_pane("css=#loading-modal")
            >>> await element_manager.wait_for_disabled_pane()  # Wait for any modal
        """
        timeout_ms = timeout or self._default_timeout
        
        # Default modal/overlay selectors if none provided
        default_selectors = [
            "css=.modal-backdrop",
            "css=.modal-overlay",
            "css=.overlay",
            "css=[role='dialog']",
            "css=.disabled-pane",
            "css=.loading-overlay",
        ]
        
        locators_to_check = [pane_locator] if pane_locator else default_selectors
        
        try:
            logger.debug(
                f"Waiting for disabled pane/modal to disappear "
                f"(timeout: {timeout_ms}ms)"
            )
            
            # Check each locator
            for loc in locators_to_check:
                try:
                    strategy, value = self._parse_locator_strategy(loc)
                    playwright_locator = self._create_playwright_locator(strategy, value)
                    
                    # Check if element exists
                    count = await playwright_locator.count()
                    
                    if count > 0:
                        logger.debug(f"Found disabled pane, waiting for it to hide: {loc}")
                        
                        # Wait for it to be hidden or detached
                        try:
                            await playwright_locator.wait_for(
                                state="hidden",
                                timeout=timeout_ms
                            )
                            logger.info(f"Disabled pane disappeared: {loc}")
                            return
                        except PlaywrightTimeoutError:
                            # Try detached state
                            try:
                                await playwright_locator.wait_for(
                                    state="detached",
                                    timeout=1000
                                )
                                logger.info(f"Disabled pane detached: {loc}")
                                return
                            except PlaywrightTimeoutError:
                                # Continue to next locator or raise
                                if loc == locators_to_check[-1]:
                                    raise
                                continue
                    else:
                        logger.debug(f"No disabled pane found with locator: {loc}")
                        
                except Exception as e:
                    if loc == locators_to_check[-1]:
                        raise
                    logger.debug(f"Error checking locator {loc}: {str(e)}")
                    continue
            
            # If we get here, no panes were found (which is good)
            logger.info("No disabled panes found (page is ready)")
            
        except PlaywrightTimeoutError as e:
            logger.error(
                f"Timeout waiting for disabled pane to disappear "
                f"(timeout: {timeout_ms}ms)"
            )
            raise TimeoutException(
                operation="wait_for_disabled_pane",
                timeout_seconds=timeout_ms / 1000,
                additional_info={
                    "pane_locator": pane_locator,
                    "checked_locators": locators_to_check,
                    "page_url": self.page.url
                }
            )
        except Exception as e:
            logger.error(f"Error waiting for disabled pane: {str(e)}")
            raise RaptorException(
                f"Failed to wait for disabled pane: {str(e)}",
                context={
                    "pane_locator": pane_locator,
                    "timeout_ms": timeout_ms,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def wait_for_network_idle(
        self,
        timeout: Optional[int] = None,
        idle_time: int = 500,
    ) -> None:
        """
        Wait for network activity to become idle.
        
        Waits until there are no network connections for at least the specified
        idle time. This is useful for ensuring all AJAX requests and resources
        have finished loading.
        
        Args:
            timeout: Optional timeout in milliseconds (uses default if not provided)
            idle_time: Minimum idle time in milliseconds (default: 500ms)
            
        Raises:
            TimeoutException: If network doesn't become idle within timeout
            
        Example:
            >>> await element_manager.wait_for_network_idle()
            >>> await element_manager.wait_for_network_idle(timeout=30000, idle_time=1000)
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(
                f"Waiting for network idle (timeout: {timeout_ms}ms, "
                f"idle_time: {idle_time}ms)"
            )
            
            # Playwright's networkidle waits for no network connections for 500ms
            await self.page.wait_for_load_state(
                state="networkidle",
                timeout=timeout_ms
            )
            
            logger.info("Network became idle")
            
        except PlaywrightTimeoutError as e:
            logger.error(
                f"Timeout waiting for network idle "
                f"(timeout: {timeout_ms}ms)"
            )
            raise TimeoutException(
                operation="wait_for_network_idle",
                timeout_seconds=timeout_ms / 1000,
                additional_info={
                    "idle_time_ms": idle_time,
                    "page_url": self.page.url
                }
            )
        except Exception as e:
            logger.error(f"Error waiting for network idle: {str(e)}")
            raise RaptorException(
                f"Failed to wait for network idle: {str(e)}",
                context={
                    "timeout_ms": timeout_ms,
                    "idle_time_ms": idle_time,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def verify_exists(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Verify that an element exists on the page.
        
        Asserts that the element can be located and is present in the DOM.
        Raises an assertion error if the element is not found.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            message: Optional custom error message
            
        Raises:
            AssertionError: If element does not exist
            
        Example:
            >>> await element_manager.verify_exists("css=#submit-button")
            >>> await element_manager.verify_exists(
            ...     "css=#error-message",
            ...     message="Error message should be displayed"
            ... )
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Verifying element exists: {locator}")
            
            # Try to locate the element
            await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            logger.info(f"Verification passed: Element exists - {locator}")
            
        except ElementNotFoundException as e:
            error_msg = message or f"Element does not exist: {locator}"
            logger.error(f"Verification failed: {error_msg}")
            raise AssertionError(error_msg) from e

    async def verify_not_exists(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Verify that an element does not exist on the page.
        
        Asserts that the element cannot be located or is not present in the DOM.
        Raises an assertion error if the element is found.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds (shorter timeout recommended)
            message: Optional custom error message
            
        Raises:
            AssertionError: If element exists
            
        Example:
            >>> await element_manager.verify_not_exists("css=#error-message")
            >>> await element_manager.verify_not_exists(
            ...     "css=#loading-spinner",
            ...     timeout=5000,
            ...     message="Loading spinner should not be visible"
            ... )
        """
        # Use shorter timeout for negative assertions (default 5 seconds)
        timeout_ms = timeout if timeout is not None else 5000
        
        try:
            logger.debug(f"Verifying element does not exist: {locator}")
            
            # Try to locate the element
            await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # If we get here, element was found - verification failed
            error_msg = message or f"Element exists but should not: {locator}"
            logger.error(f"Verification failed: {error_msg}")
            raise AssertionError(error_msg)
            
        except ElementNotFoundException:
            # Element not found - this is what we want
            logger.info(f"Verification passed: Element does not exist - {locator}")

    async def verify_enabled(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Verify that an element is enabled (not disabled).
        
        Asserts that the element exists and is in an enabled state.
        Raises an assertion error if the element is disabled or not found.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            message: Optional custom error message
            
        Raises:
            AssertionError: If element is disabled or does not exist
            
        Example:
            >>> await element_manager.verify_enabled("css=#submit-button")
            >>> await element_manager.verify_enabled(
            ...     "css=#save-button",
            ...     message="Save button should be enabled"
            ... )
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Verifying element is enabled: {locator}")
            
            # Locate the element
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Check if enabled
            is_enabled = await element.is_enabled(timeout=timeout_ms)
            
            if not is_enabled:
                error_msg = message or f"Element is disabled but should be enabled: {locator}"
                logger.error(f"Verification failed: {error_msg}")
                raise AssertionError(error_msg)
            
            logger.info(f"Verification passed: Element is enabled - {locator}")
            
        except ElementNotFoundException as e:
            error_msg = message or f"Element does not exist: {locator}"
            logger.error(f"Verification failed: {error_msg}")
            raise AssertionError(error_msg) from e
        except AssertionError:
            raise
        except Exception as e:
            error_msg = message or f"Failed to verify element is enabled: {locator} - {str(e)}"
            logger.error(f"Verification failed: {error_msg}")
            raise AssertionError(error_msg) from e

    async def verify_disabled(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Verify that an element is disabled (not enabled).
        
        Asserts that the element exists and is in a disabled state.
        Raises an assertion error if the element is enabled or not found.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            message: Optional custom error message
            
        Raises:
            AssertionError: If element is enabled or does not exist
            
        Example:
            >>> await element_manager.verify_disabled("css=#submit-button")
            >>> await element_manager.verify_disabled(
            ...     "css=#delete-button",
            ...     message="Delete button should be disabled"
            ... )
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Verifying element is disabled: {locator}")
            
            # Locate the element
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Check if enabled
            is_enabled = await element.is_enabled(timeout=timeout_ms)
            
            if is_enabled:
                error_msg = message or f"Element is enabled but should be disabled: {locator}"
                logger.error(f"Verification failed: {error_msg}")
                raise AssertionError(error_msg)
            
            logger.info(f"Verification passed: Element is disabled - {locator}")
            
        except ElementNotFoundException as e:
            error_msg = message or f"Element does not exist: {locator}"
            logger.error(f"Verification failed: {error_msg}")
            raise AssertionError(error_msg) from e
        except AssertionError:
            raise
        except Exception as e:
            error_msg = message or f"Failed to verify element is disabled: {locator} - {str(e)}"
            logger.error(f"Verification failed: {error_msg}")
            raise AssertionError(error_msg) from e

    async def verify_text(
        self,
        locator: str,
        expected_text: str,
        exact_match: bool = True,
        case_sensitive: bool = True,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Verify that an element contains the expected text.
        
        Asserts that the element's text content matches the expected value.
        Supports both exact and partial matching, with optional case sensitivity.
        
        Args:
            locator: Primary locator string
            expected_text: Expected text content
            exact_match: If True, requires exact match; if False, allows partial match (default: True)
            case_sensitive: If True, comparison is case-sensitive (default: True)
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            message: Optional custom error message
            
        Raises:
            AssertionError: If text does not match or element does not exist
            
        Example:
            >>> await element_manager.verify_text("css=#message", "Success!")
            >>> await element_manager.verify_text(
            ...     "css=#status",
            ...     "processing",
            ...     exact_match=False,
            ...     case_sensitive=False
            ... )
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(
                f"Verifying element text: {locator} "
                f"(expected: '{expected_text}', exact: {exact_match}, "
                f"case_sensitive: {case_sensitive})"
            )
            
            # Get the element's text
            actual_text = await self.get_text(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Prepare texts for comparison
            compare_actual = actual_text if case_sensitive else actual_text.lower()
            compare_expected = expected_text if case_sensitive else expected_text.lower()
            
            # Perform comparison
            if exact_match:
                match = compare_actual == compare_expected
            else:
                match = compare_expected in compare_actual
            
            if not match:
                if message:
                    error_msg = message
                else:
                    match_type = "exact" if exact_match else "partial"
                    error_msg = (
                        f"Text mismatch ({match_type} match, "
                        f"case_sensitive={case_sensitive}): {locator}\n"
                        f"Expected: '{expected_text}'\n"
                        f"Actual: '{actual_text}'"
                    )
                logger.error(f"Verification failed: {error_msg}")
                raise AssertionError(error_msg)
            
            logger.info(
                f"Verification passed: Element text matches - {locator} "
                f"(text: '{actual_text}')"
            )
            
        except ElementNotFoundException as e:
            error_msg = message or f"Element does not exist: {locator}"
            logger.error(f"Verification failed: {error_msg}")
            raise AssertionError(error_msg) from e
        except AssertionError:
            raise
        except Exception as e:
            error_msg = message or f"Failed to verify element text: {locator} - {str(e)}"
            logger.error(f"Verification failed: {error_msg}")
            raise AssertionError(error_msg) from e

    async def verify_visible(
        self,
        locator: str,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Verify that an element is visible on the page.
        
        Asserts that the element exists and is visible to the user.
        Raises an assertion error if the element is hidden or not found.
        
        Args:
            locator: Primary locator string
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            message: Optional custom error message
            
        Raises:
            AssertionError: If element is not visible or does not exist
            
        Example:
            >>> await element_manager.verify_visible("css=#success-message")
            >>> await element_manager.verify_visible(
            ...     "css=#notification",
            ...     message="Notification should be visible"
            ... )
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Verifying element is visible: {locator}")
            
            # Locate the element (this waits for it to be visible)
            await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            logger.info(f"Verification passed: Element is visible - {locator}")
            
        except ElementNotFoundException as e:
            error_msg = message or f"Element is not visible or does not exist: {locator}"
            logger.error(f"Verification failed: {error_msg}")
            raise AssertionError(error_msg) from e

    # ========================================================================
    # Soft Assertion Methods
    # ========================================================================
    
    async def soft_verify_exists(
        self,
        locator: str,
        collector: SoftAssertionCollector,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> bool:
        """
        Soft assertion: Verify that an element exists on the page.
        
        Unlike verify_exists(), this method does not raise an exception on failure.
        Instead, it records the failure in the collector and returns False.
        
        Args:
            locator: Primary locator string
            collector: SoftAssertionCollector instance to record failures
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            message: Optional custom error message
            
        Returns:
            True if verification passed, False if failed
            
        Example:
            >>> collector = SoftAssertionCollector()
            >>> await element_manager.soft_verify_exists("css=#submit-button", collector)
            >>> await element_manager.soft_verify_exists(
            ...     "css=#error-message",
            ...     collector,
            ...     message="Error message should be displayed"
            ... )
            >>> collector.assert_all()  # Raises if any failures
        """
        collector.increment_count()
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Soft verifying element exists: {locator}")
            
            # Try to locate the element
            await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            logger.info(f"Soft verification passed: Element exists - {locator}")
            return True
            
        except ElementNotFoundException as e:
            error_msg = message or f"Element does not exist: {locator}"
            logger.warning(f"Soft verification failed: {error_msg}")
            
            collector.add_failure(
                locator=locator,
                verification_type="verify_exists",
                expected="element exists",
                actual="element not found",
                message=error_msg,
                page_url=self.page.url,
                timeout_ms=timeout_ms,
                fallback_locators=fallback_locators
            )
            return False
    
    async def soft_verify_not_exists(
        self,
        locator: str,
        collector: SoftAssertionCollector,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> bool:
        """
        Soft assertion: Verify that an element does not exist on the page.
        
        Unlike verify_not_exists(), this method does not raise an exception on failure.
        Instead, it records the failure in the collector and returns False.
        
        Args:
            locator: Primary locator string
            collector: SoftAssertionCollector instance to record failures
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds (shorter timeout recommended)
            message: Optional custom error message
            
        Returns:
            True if verification passed, False if failed
            
        Example:
            >>> collector = SoftAssertionCollector()
            >>> await element_manager.soft_verify_not_exists("css=#error-message", collector)
            >>> collector.assert_all()
        """
        collector.increment_count()
        # Use shorter timeout for negative assertions (default 5 seconds)
        timeout_ms = timeout if timeout is not None else 5000
        
        try:
            logger.debug(f"Soft verifying element does not exist: {locator}")
            
            # Try to locate the element
            await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # If we get here, element was found - verification failed
            error_msg = message or f"Element exists but should not: {locator}"
            logger.warning(f"Soft verification failed: {error_msg}")
            
            collector.add_failure(
                locator=locator,
                verification_type="verify_not_exists",
                expected="element does not exist",
                actual="element found",
                message=error_msg,
                page_url=self.page.url,
                timeout_ms=timeout_ms
            )
            return False
            
        except ElementNotFoundException:
            # Element not found - this is what we want
            logger.info(f"Soft verification passed: Element does not exist - {locator}")
            return True
    
    async def soft_verify_enabled(
        self,
        locator: str,
        collector: SoftAssertionCollector,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> bool:
        """
        Soft assertion: Verify that an element is enabled (not disabled).
        
        Unlike verify_enabled(), this method does not raise an exception on failure.
        Instead, it records the failure in the collector and returns False.
        
        Args:
            locator: Primary locator string
            collector: SoftAssertionCollector instance to record failures
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            message: Optional custom error message
            
        Returns:
            True if verification passed, False if failed
            
        Example:
            >>> collector = SoftAssertionCollector()
            >>> await element_manager.soft_verify_enabled("css=#submit-button", collector)
            >>> collector.assert_all()
        """
        collector.increment_count()
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Soft verifying element is enabled: {locator}")
            
            # Locate the element
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Check if enabled
            is_enabled = await element.is_enabled(timeout=timeout_ms)
            
            if not is_enabled:
                error_msg = message or f"Element is disabled but should be enabled: {locator}"
                logger.warning(f"Soft verification failed: {error_msg}")
                
                collector.add_failure(
                    locator=locator,
                    verification_type="verify_enabled",
                    expected="enabled",
                    actual="disabled",
                    message=error_msg,
                    page_url=self.page.url
                )
                return False
            
            logger.info(f"Soft verification passed: Element is enabled - {locator}")
            return True
            
        except ElementNotFoundException as e:
            error_msg = message or f"Element does not exist: {locator}"
            logger.warning(f"Soft verification failed: {error_msg}")
            
            collector.add_failure(
                locator=locator,
                verification_type="verify_enabled",
                expected="element exists and is enabled",
                actual="element not found",
                message=error_msg,
                page_url=self.page.url
            )
            return False
        except Exception as e:
            error_msg = message or f"Failed to verify element is enabled: {locator} - {str(e)}"
            logger.warning(f"Soft verification failed: {error_msg}")
            
            collector.add_failure(
                locator=locator,
                verification_type="verify_enabled",
                expected="enabled",
                actual=f"error: {str(e)}",
                message=error_msg,
                page_url=self.page.url
            )
            return False
    
    async def soft_verify_disabled(
        self,
        locator: str,
        collector: SoftAssertionCollector,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> bool:
        """
        Soft assertion: Verify that an element is disabled (not enabled).
        
        Unlike verify_disabled(), this method does not raise an exception on failure.
        Instead, it records the failure in the collector and returns False.
        
        Args:
            locator: Primary locator string
            collector: SoftAssertionCollector instance to record failures
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            message: Optional custom error message
            
        Returns:
            True if verification passed, False if failed
            
        Example:
            >>> collector = SoftAssertionCollector()
            >>> await element_manager.soft_verify_disabled("css=#submit-button", collector)
            >>> collector.assert_all()
        """
        collector.increment_count()
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Soft verifying element is disabled: {locator}")
            
            # Locate the element
            element = await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Check if enabled
            is_enabled = await element.is_enabled(timeout=timeout_ms)
            
            if is_enabled:
                error_msg = message or f"Element is enabled but should be disabled: {locator}"
                logger.warning(f"Soft verification failed: {error_msg}")
                
                collector.add_failure(
                    locator=locator,
                    verification_type="verify_disabled",
                    expected="disabled",
                    actual="enabled",
                    message=error_msg,
                    page_url=self.page.url
                )
                return False
            
            logger.info(f"Soft verification passed: Element is disabled - {locator}")
            return True
            
        except ElementNotFoundException as e:
            error_msg = message or f"Element does not exist: {locator}"
            logger.warning(f"Soft verification failed: {error_msg}")
            
            collector.add_failure(
                locator=locator,
                verification_type="verify_disabled",
                expected="element exists and is disabled",
                actual="element not found",
                message=error_msg,
                page_url=self.page.url
            )
            return False
        except Exception as e:
            error_msg = message or f"Failed to verify element is disabled: {locator} - {str(e)}"
            logger.warning(f"Soft verification failed: {error_msg}")
            
            collector.add_failure(
                locator=locator,
                verification_type="verify_disabled",
                expected="disabled",
                actual=f"error: {str(e)}",
                message=error_msg,
                page_url=self.page.url
            )
            return False
    
    async def soft_verify_text(
        self,
        locator: str,
        expected_text: str,
        collector: SoftAssertionCollector,
        exact_match: bool = True,
        case_sensitive: bool = True,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> bool:
        """
        Soft assertion: Verify that an element contains the expected text.
        
        Unlike verify_text(), this method does not raise an exception on failure.
        Instead, it records the failure in the collector and returns False.
        
        Args:
            locator: Primary locator string
            expected_text: Expected text content
            collector: SoftAssertionCollector instance to record failures
            exact_match: If True, requires exact match; if False, allows partial match (default: True)
            case_sensitive: If True, comparison is case-sensitive (default: True)
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            message: Optional custom error message
            
        Returns:
            True if verification passed, False if failed
            
        Example:
            >>> collector = SoftAssertionCollector()
            >>> await element_manager.soft_verify_text("css=#message", "Success!", collector)
            >>> await element_manager.soft_verify_text(
            ...     "css=#status",
            ...     "processing",
            ...     collector,
            ...     exact_match=False,
            ...     case_sensitive=False
            ... )
            >>> collector.assert_all()
        """
        collector.increment_count()
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(
                f"Soft verifying element text: {locator} "
                f"(expected: '{expected_text}', exact: {exact_match}, "
                f"case_sensitive: {case_sensitive})"
            )
            
            # Get the element's text
            actual_text = await self.get_text(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            # Prepare texts for comparison
            compare_actual = actual_text if case_sensitive else actual_text.lower()
            compare_expected = expected_text if case_sensitive else expected_text.lower()
            
            # Perform comparison
            if exact_match:
                match = compare_actual == compare_expected
            else:
                match = compare_expected in compare_actual
            
            if not match:
                if message:
                    error_msg = message
                else:
                    match_type = "exact" if exact_match else "partial"
                    error_msg = (
                        f"Text mismatch ({match_type} match, "
                        f"case_sensitive={case_sensitive}): {locator}"
                    )
                
                logger.warning(f"Soft verification failed: {error_msg}")
                
                collector.add_failure(
                    locator=locator,
                    verification_type="verify_text",
                    expected=expected_text,
                    actual=actual_text,
                    message=error_msg,
                    page_url=self.page.url,
                    exact_match=exact_match,
                    case_sensitive=case_sensitive
                )
                return False
            
            logger.info(
                f"Soft verification passed: Element text matches - {locator} "
                f"(text: '{actual_text}')"
            )
            return True
            
        except ElementNotFoundException as e:
            error_msg = message or f"Element does not exist: {locator}"
            logger.warning(f"Soft verification failed: {error_msg}")
            
            collector.add_failure(
                locator=locator,
                verification_type="verify_text",
                expected=expected_text,
                actual="element not found",
                message=error_msg,
                page_url=self.page.url
            )
            return False
        except Exception as e:
            error_msg = message or f"Failed to verify element text: {locator} - {str(e)}"
            logger.warning(f"Soft verification failed: {error_msg}")
            
            collector.add_failure(
                locator=locator,
                verification_type="verify_text",
                expected=expected_text,
                actual=f"error: {str(e)}",
                message=error_msg,
                page_url=self.page.url
            )
            return False
    
    async def soft_verify_visible(
        self,
        locator: str,
        collector: SoftAssertionCollector,
        fallback_locators: Optional[List[str]] = None,
        timeout: Optional[int] = None,
        message: Optional[str] = None,
    ) -> bool:
        """
        Soft assertion: Verify that an element is visible on the page.
        
        Unlike verify_visible(), this method does not raise an exception on failure.
        Instead, it records the failure in the collector and returns False.
        
        Args:
            locator: Primary locator string
            collector: SoftAssertionCollector instance to record failures
            fallback_locators: Optional list of fallback locator strings
            timeout: Optional timeout in milliseconds
            message: Optional custom error message
            
        Returns:
            True if verification passed, False if failed
            
        Example:
            >>> collector = SoftAssertionCollector()
            >>> await element_manager.soft_verify_visible("css=#success-message", collector)
            >>> collector.assert_all()
        """
        collector.increment_count()
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(f"Soft verifying element is visible: {locator}")
            
            # Locate the element (this waits for it to be visible)
            await self.locate_element(
                locator,
                fallback_locators=fallback_locators,
                timeout=timeout_ms
            )
            
            logger.info(f"Soft verification passed: Element is visible - {locator}")
            return True
            
        except ElementNotFoundException as e:
            error_msg = message or f"Element is not visible or does not exist: {locator}"
            logger.warning(f"Soft verification failed: {error_msg}")
            
            collector.add_failure(
                locator=locator,
                verification_type="verify_visible",
                expected="visible",
                actual="not visible or not found",
                message=error_msg,
                page_url=self.page.url
            )
            return False

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        return False
