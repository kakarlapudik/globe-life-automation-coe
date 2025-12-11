"""
Base Page for RAPTOR Python Playwright Framework.

This module provides the base page object class that all page objects should inherit from.
It includes common functionality for navigation, waiting, screenshots, and JavaScript execution.
"""

from typing import Optional, Any, Dict
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError
from raptor.core.element_manager import ElementManager
from raptor.core.exceptions import RaptorException, TimeoutException
from raptor.core.config_manager import ConfigManager
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class BasePage:
    """
    Base class for all page objects with common functionality.
    
    This class provides:
    - URL navigation with wait for load completion
    - Page load state management
    - Screenshot capture for debugging
    - Page title and URL retrieval
    - JavaScript execution capabilities
    - Integration with ElementManager for element interactions
    
    All page objects should inherit from this class to gain access to
    common page operations and maintain consistency across the framework.
    
    Example:
        >>> class LoginPage(BasePage):
        ...     def __init__(self, page: Page, element_manager: ElementManager):
        ...         super().__init__(page, element_manager)
        ...         self.username_field = "css=#username"
        ...         self.password_field = "css=#password"
        ...         self.submit_button = "css=#login-button"
        ...     
        ...     async def login(self, username: str, password: str):
        ...         await self.navigate("https://example.com/login")
        ...         await self.element_manager.fill(self.username_field, username)
        ...         await self.element_manager.fill(self.password_field, password)
        ...         await self.element_manager.click(self.submit_button)
        ...         await self.wait_for_load()
    """

    def __init__(
        self,
        page: Page,
        element_manager: Optional[ElementManager] = None,
        config: Optional[ConfigManager] = None,
    ):
        """
        Initialize the Base Page.

        Args:
            page: Playwright Page instance to interact with
            element_manager: Optional ElementManager instance. If not provided,
                           a new instance will be created.
            config: Optional ConfigManager instance for configuration access.
                   If not provided, default configuration will be used.
        """
        self.page = page
        self.element_manager = element_manager or ElementManager(page, config)
        self.config = config or ConfigManager()
        self._default_timeout = self.config.get_timeout("page")
        self._screenshot_dir = Path(self.config.get("screenshots.directory", "screenshots"))
        
        # Ensure screenshot directory exists
        self._screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(
            f"BasePage initialized for page: {page.url if page.url != 'about:blank' else 'new page'}"
        )

    async def navigate(
        self,
        url: str,
        wait_until: str = "load",
        timeout: Optional[int] = None,
    ) -> None:
        """
        Navigate to a URL and wait for page load completion.
        
        This method navigates to the specified URL and waits for the page to reach
        the desired load state. By default, it waits for the 'load' event, but can
        be configured to wait for different states.
        
        Args:
            url: URL to navigate to (must include protocol, e.g., https://)
            wait_until: Load state to wait for. Options:
                       - "load": Wait for load event (default)
                       - "domcontentloaded": Wait for DOMContentLoaded event
                       - "networkidle": Wait for network to be idle
                       - "commit": Wait for navigation to commit
            timeout: Optional timeout in milliseconds (uses default if not provided)
            
        Raises:
            TimeoutException: If navigation times out
            RaptorException: If navigation fails
            
        Example:
            >>> await page.navigate("https://example.com")
            >>> await page.navigate("https://example.com/slow", wait_until="networkidle")
            >>> await page.navigate("https://example.com/fast", timeout=5000)
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.info(
                f"Navigating to URL: {url} (wait_until={wait_until}, timeout={timeout_ms}ms)"
            )
            
            # Validate URL format
            if not url.startswith(("http://", "https://", "file://", "about:")):
                logger.warning(
                    f"URL '{url}' does not start with a protocol. "
                    "This may cause navigation to fail."
                )
            
            # Navigate to URL
            response = await self.page.goto(
                url,
                wait_until=wait_until,
                timeout=timeout_ms
            )
            
            # Check response status
            if response:
                status = response.status
                if status >= 400:
                    logger.warning(
                        f"Navigation completed with HTTP status {status}: {url}"
                    )
                else:
                    logger.info(
                        f"Navigation successful (HTTP {status}): {url}"
                    )
            else:
                logger.info(f"Navigation completed: {url}")
            
        except PlaywrightTimeoutError as e:
            logger.error(
                f"Navigation timeout after {timeout_ms}ms: {url}"
            )
            raise TimeoutException(
                operation=f"navigate to {url}",
                timeout_seconds=timeout_ms / 1000,
                additional_info={
                    "url": url,
                    "wait_until": wait_until,
                    "current_url": self.page.url
                }
            )
        except Exception as e:
            logger.error(f"Navigation failed: {url} - {str(e)}")
            raise RaptorException(
                f"Failed to navigate to {url}: {str(e)}",
                context={
                    "url": url,
                    "wait_until": wait_until,
                    "timeout_ms": timeout_ms,
                    "current_url": self.page.url
                },
                cause=e
            )

    async def wait_for_load(
        self,
        state: str = "load",
        timeout: Optional[int] = None,
    ) -> None:
        """
        Wait for page to reach a specific load state.
        
        This method is useful when you need to wait for the page to finish loading
        after an action that triggers navigation or dynamic content loading.
        
        Args:
            state: Load state to wait for. Options:
                  - "load": Wait for load event (default)
                  - "domcontentloaded": Wait for DOMContentLoaded event
                  - "networkidle": Wait for network to be idle
            timeout: Optional timeout in milliseconds (uses default if not provided)
            
        Raises:
            TimeoutException: If page doesn't reach desired state within timeout
            RaptorException: If wait operation fails
            
        Example:
            >>> await page.wait_for_load()
            >>> await page.wait_for_load(state="networkidle")
            >>> await page.wait_for_load(state="domcontentloaded", timeout=10000)
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.debug(
                f"Waiting for page load state '{state}' (timeout={timeout_ms}ms)"
            )
            
            await self.page.wait_for_load_state(
                state=state,
                timeout=timeout_ms
            )
            
            logger.info(f"Page reached load state: {state}")
            
        except PlaywrightTimeoutError as e:
            logger.error(
                f"Timeout waiting for load state '{state}' after {timeout_ms}ms"
            )
            raise TimeoutException(
                operation=f"wait_for_load_state({state})",
                timeout_seconds=timeout_ms / 1000,
                additional_info={
                    "state": state,
                    "page_url": self.page.url
                }
            )
        except Exception as e:
            logger.error(f"Error waiting for load state '{state}': {str(e)}")
            raise RaptorException(
                f"Failed to wait for load state '{state}': {str(e)}",
                context={
                    "state": state,
                    "timeout_ms": timeout_ms,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def take_screenshot(
        self,
        name: Optional[str] = None,
        full_page: bool = False,
        path: Optional[str] = None,
    ) -> str:
        """
        Capture a screenshot of the current page for debugging.
        
        Screenshots are automatically saved with timestamps and can be used for
        debugging test failures or documenting test execution.
        
        Args:
            name: Optional name for the screenshot file (without extension).
                 If not provided, uses timestamp.
            full_page: Whether to capture the full scrollable page (default: False)
            path: Optional custom path for the screenshot. If not provided,
                 uses the configured screenshot directory.
            
        Returns:
            Path to the saved screenshot file
            
        Raises:
            RaptorException: If screenshot capture fails
            
        Example:
            >>> screenshot_path = await page.take_screenshot("login_page")
            >>> screenshot_path = await page.take_screenshot("full_page", full_page=True)
            >>> screenshot_path = await page.take_screenshot(path="/custom/path/screenshot.png")
        """
        try:
            # Generate filename if not provided
            if path is None:
                if name is None:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    name = f"screenshot_{timestamp}"
                
                # Ensure name doesn't have extension
                if name.endswith(".png"):
                    name = name[:-4]
                
                # Create full path
                screenshot_path = self._screenshot_dir / f"{name}.png"
            else:
                screenshot_path = Path(path)
                # Ensure parent directory exists
                screenshot_path.parent.mkdir(parents=True, exist_ok=True)
            
            logger.debug(
                f"Capturing screenshot: {screenshot_path} (full_page={full_page})"
            )
            
            # Capture screenshot
            await self.page.screenshot(
                path=str(screenshot_path),
                full_page=full_page
            )
            
            logger.info(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {str(e)}")
            raise RaptorException(
                f"Failed to capture screenshot: {str(e)}",
                context={
                    "name": name,
                    "full_page": full_page,
                    "path": path,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def get_title(self) -> str:
        """
        Get the current page title.
        
        Returns:
            Page title as a string
            
        Raises:
            RaptorException: If title retrieval fails
            
        Example:
            >>> title = await page.get_title()
            >>> assert "Login" in title
        """
        try:
            title = await self.page.title()
            logger.debug(f"Page title: {title}")
            return title
        except Exception as e:
            logger.error(f"Failed to get page title: {str(e)}")
            raise RaptorException(
                f"Failed to get page title: {str(e)}",
                context={"page_url": self.page.url},
                cause=e
            )

    async def get_url(self) -> str:
        """
        Get the current page URL.
        
        Returns:
            Current page URL as a string
            
        Example:
            >>> url = await page.get_url()
            >>> assert url == "https://example.com/dashboard"
        """
        try:
            url = self.page.url
            logger.debug(f"Current page URL: {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to get page URL: {str(e)}")
            raise RaptorException(
                f"Failed to get page URL: {str(e)}",
                cause=e
            )

    async def execute_script(
        self,
        script: str,
        *args: Any,
    ) -> Any:
        """
        Execute JavaScript code in the page context.
        
        This method allows you to run custom JavaScript code in the browser,
        which is useful for:
        - Manipulating the DOM directly
        - Accessing browser APIs
        - Performing actions not directly supported by Playwright
        - Retrieving computed values or page state
        
        Args:
            script: JavaScript code to execute
            *args: Arguments to pass to the JavaScript function
            
        Returns:
            Result of the JavaScript execution (serializable values only)
            
        Raises:
            RaptorException: If script execution fails
            
        Example:
            >>> # Scroll to bottom of page
            >>> await page.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            
            >>> # Get element text via JavaScript
            >>> text = await page.execute_script(
            ...     "return document.querySelector(arguments[0]).textContent",
            ...     "#my-element"
            ... )
            
            >>> # Set local storage
            >>> await page.execute_script(
            ...     "localStorage.setItem(arguments[0], arguments[1])",
            ...     "key",
            ...     "value"
            ... )
            
            >>> # Get page dimensions
            >>> dimensions = await page.execute_script(
            ...     "return {width: window.innerWidth, height: window.innerHeight}"
            ... )
        """
        try:
            logger.debug(
                f"Executing JavaScript: {script[:100]}{'...' if len(script) > 100 else ''}"
            )
            
            result = await self.page.evaluate(script, *args)
            
            logger.debug(f"JavaScript execution completed. Result type: {type(result)}")
            return result
            
        except Exception as e:
            logger.error(f"JavaScript execution failed: {str(e)}")
            raise RaptorException(
                f"Failed to execute JavaScript: {str(e)}",
                context={
                    "script": script[:200],  # Truncate long scripts
                    "args": args,
                    "page_url": self.page.url
                },
                cause=e
            )

    async def reload(
        self,
        wait_until: str = "load",
        timeout: Optional[int] = None,
    ) -> None:
        """
        Reload the current page.
        
        Args:
            wait_until: Load state to wait for after reload
            timeout: Optional timeout in milliseconds
            
        Raises:
            TimeoutException: If reload times out
            RaptorException: If reload fails
            
        Example:
            >>> await page.reload()
            >>> await page.reload(wait_until="networkidle")
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.info(f"Reloading page: {self.page.url}")
            
            await self.page.reload(
                wait_until=wait_until,
                timeout=timeout_ms
            )
            
            logger.info("Page reloaded successfully")
            
        except PlaywrightTimeoutError as e:
            logger.error(f"Page reload timeout after {timeout_ms}ms")
            raise TimeoutException(
                operation="reload page",
                timeout_seconds=timeout_ms / 1000,
                additional_info={
                    "page_url": self.page.url,
                    "wait_until": wait_until
                }
            )
        except Exception as e:
            logger.error(f"Page reload failed: {str(e)}")
            raise RaptorException(
                f"Failed to reload page: {str(e)}",
                context={
                    "page_url": self.page.url,
                    "wait_until": wait_until,
                    "timeout_ms": timeout_ms
                },
                cause=e
            )

    async def go_back(
        self,
        wait_until: str = "load",
        timeout: Optional[int] = None,
    ) -> None:
        """
        Navigate back in browser history.
        
        Args:
            wait_until: Load state to wait for after navigation
            timeout: Optional timeout in milliseconds
            
        Raises:
            TimeoutException: If navigation times out
            RaptorException: If navigation fails
            
        Example:
            >>> await page.go_back()
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.info("Navigating back in browser history")
            
            await self.page.go_back(
                wait_until=wait_until,
                timeout=timeout_ms
            )
            
            logger.info(f"Navigated back to: {self.page.url}")
            
        except PlaywrightTimeoutError as e:
            logger.error(f"Go back timeout after {timeout_ms}ms")
            raise TimeoutException(
                operation="go_back",
                timeout_seconds=timeout_ms / 1000,
                additional_info={
                    "page_url": self.page.url,
                    "wait_until": wait_until
                }
            )
        except Exception as e:
            logger.error(f"Go back failed: {str(e)}")
            raise RaptorException(
                f"Failed to go back: {str(e)}",
                context={
                    "page_url": self.page.url,
                    "wait_until": wait_until,
                    "timeout_ms": timeout_ms
                },
                cause=e
            )

    async def go_forward(
        self,
        wait_until: str = "load",
        timeout: Optional[int] = None,
    ) -> None:
        """
        Navigate forward in browser history.
        
        Args:
            wait_until: Load state to wait for after navigation
            timeout: Optional timeout in milliseconds
            
        Raises:
            TimeoutException: If navigation times out
            RaptorException: If navigation fails
            
        Example:
            >>> await page.go_forward()
        """
        timeout_ms = timeout or self._default_timeout
        
        try:
            logger.info("Navigating forward in browser history")
            
            await self.page.go_forward(
                wait_until=wait_until,
                timeout=timeout_ms
            )
            
            logger.info(f"Navigated forward to: {self.page.url}")
            
        except PlaywrightTimeoutError as e:
            logger.error(f"Go forward timeout after {timeout_ms}ms")
            raise TimeoutException(
                operation="go_forward",
                timeout_seconds=timeout_ms / 1000,
                additional_info={
                    "page_url": self.page.url,
                    "wait_until": wait_until
                }
            )
        except Exception as e:
            logger.error(f"Go forward failed: {str(e)}")
            raise RaptorException(
                f"Failed to go forward: {str(e)}",
                context={
                    "page_url": self.page.url,
                    "wait_until": wait_until,
                    "timeout_ms": timeout_ms
                },
                cause=e
            )

    def get_page(self) -> Page:
        """
        Get the underlying Playwright Page object.
        
        This provides direct access to the Playwright Page API for advanced
        operations not covered by the BasePage abstraction.
        
        Returns:
            Playwright Page instance
            
        Example:
            >>> playwright_page = page.get_page()
            >>> await playwright_page.set_viewport_size({"width": 1920, "height": 1080})
        """
        return self.page

    def get_element_manager(self) -> ElementManager:
        """
        Get the ElementManager instance.
        
        Returns:
            ElementManager instance for element interactions
            
        Example:
            >>> element_manager = page.get_element_manager()
            >>> await element_manager.click("css=#button")
        """
        return self.element_manager

    def get_config(self) -> ConfigManager:
        """
        Get the ConfigManager instance.
        
        Returns:
            ConfigManager instance for configuration access
            
        Example:
            >>> config = page.get_config()
            >>> timeout = config.get_timeout("element")
        """
        return self.config
