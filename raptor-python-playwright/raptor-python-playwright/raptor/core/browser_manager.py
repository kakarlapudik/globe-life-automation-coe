"""
Browser Manager for RAPTOR Python Playwright Framework.

This module provides browser lifecycle management including launching browsers,
creating contexts and pages, and proper cleanup. Supports Chromium, Firefox,
and WebKit browsers in both headless and headed modes.
"""

from typing import Optional, Dict, Any, List
from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
    BrowserType,
)
from raptor.core.exceptions import RaptorException, SessionException
from raptor.core.config_manager import ConfigManager
import asyncio
import logging

logger = logging.getLogger(__name__)


class BrowserManager:
    """
    Manages browser lifecycle, contexts, and pages for test automation.
    
    This class handles:
    - Browser launching for Chromium, Firefox, and WebKit
    - Browser context creation with custom options
    - Page creation and management
    - Proper cleanup and resource management
    - Support for headless and headed modes
    
    Example:
        >>> browser_manager = BrowserManager()
        >>> await browser_manager.launch_browser("chromium", headless=True)
        >>> context = await browser_manager.create_context()
        >>> page = await browser_manager.create_page(context)
        >>> # ... perform test actions ...
        >>> await browser_manager.close_browser()
    """

    def __init__(self, config: Optional[ConfigManager] = None):
        """
        Initialize the Browser Manager.

        Args:
            config: Optional ConfigManager instance for browser configuration.
                   If not provided, default configuration will be used.
        """
        self.config = config or ConfigManager()
        self._playwright: Optional[Playwright] = None
        self._browser: Optional[Browser] = None
        self._browser_type: Optional[str] = None
        self._contexts: List[BrowserContext] = []
        self._pages: List[Page] = []
        
        logger.info("BrowserManager initialized")

    async def launch_browser(
        self,
        browser_type: str = "chromium",
        headless: bool = False,
        **launch_options: Any,
    ) -> Browser:
        """
        Launch a browser instance.

        Supports Chromium, Firefox, and WebKit browsers. The browser can be
        launched in headless or headed mode with custom launch options.

        Args:
            browser_type: Browser to launch ("chromium", "firefox", or "webkit")
            headless: Whether to run browser in headless mode (default: False)
            **launch_options: Additional browser launch options passed to Playwright

        Returns:
            Browser instance

        Raises:
            RaptorException: If browser launch fails or invalid browser type
            
        Example:
            >>> browser = await browser_manager.launch_browser(
            ...     "chromium",
            ...     headless=True,
            ...     args=["--start-maximized"]
            ... )
        """
        try:
            # Validate browser type
            valid_browsers = ["chromium", "firefox", "webkit"]
            if browser_type.lower() not in valid_browsers:
                raise RaptorException(
                    f"Invalid browser type: {browser_type}. "
                    f"Must be one of: {', '.join(valid_browsers)}",
                    context={"browser_type": browser_type, "valid_types": valid_browsers},
                )

            # Close existing browser if any
            if self._browser:
                logger.warning("Closing existing browser before launching new one")
                await self.close_browser()

            # Initialize Playwright
            if not self._playwright:
                self._playwright = await async_playwright().start()
                logger.debug("Playwright instance started")

            # Get browser type handler
            browser_type_lower = browser_type.lower()
            browser_handler: BrowserType = getattr(self._playwright, browser_type_lower)

            # Merge configuration with provided options
            default_options = self.config.get_browser_options()
            
            # Filter out options that are not valid for Playwright's launch method
            # Only include valid Playwright browser launch options
            valid_launch_options = {
                'args', 'channel', 'chromium_sandbox', 'devtools', 'downloads_path',
                'env', 'executable_path', 'firefox_user_prefs', 'handle_sighup',
                'handle_sigint', 'handle_sigterm', 'headless', 'proxy', 'slow_mo',
                'timeout', 'traces_dir'
            }
            
            filtered_options = {
                k: v for k, v in default_options.items() 
                if k in valid_launch_options
            }
            
            merged_options = {**filtered_options, **launch_options, "headless": headless}

            # Launch browser
            logger.info(
                f"Launching {browser_type} browser (headless={headless}) "
                f"with options: {merged_options}"
            )
            self._browser = await browser_handler.launch(**merged_options)
            self._browser_type = browser_type_lower

            logger.info(
                f"{browser_type} browser launched successfully. "
                f"Connected: {self._browser.is_connected()}"
            )
            return self._browser

        except Exception as e:
            error_context = {
                "browser_type": browser_type,
                "headless": headless,
                "launch_options": launch_options,
            }
            logger.error(f"Failed to launch browser: {str(e)}", extra=error_context)
            raise RaptorException(
                f"Failed to launch {browser_type} browser: {str(e)}",
                context=error_context,
                cause=e,
            )

    async def create_context(
        self, **context_options: Any
    ) -> BrowserContext:
        """
        Create a new browser context.

        Browser contexts provide isolated browser sessions with separate cookies,
        storage, and cache. This is useful for parallel test execution and
        maintaining test isolation.

        Args:
            **context_options: Browser context options (viewport, user_agent, etc.)

        Returns:
            BrowserContext instance

        Raises:
            RaptorException: If no browser is launched or context creation fails
            
        Example:
            >>> context = await browser_manager.create_context(
            ...     viewport={"width": 1920, "height": 1080},
            ...     user_agent="Custom User Agent"
            ... )
        """
        if not self._browser:
            raise RaptorException(
                "Cannot create context: No browser is currently launched. "
                "Call launch_browser() first.",
                context={"browser_launched": False},
            )

        try:
            # Get default context options from config
            default_options = self.config.get("browser.context_options", {})
            merged_options = {**default_options, **context_options}

            logger.debug(f"Creating browser context with options: {merged_options}")
            context = await self._browser.new_context(**merged_options)
            
            # Track context for cleanup
            self._contexts.append(context)
            
            logger.info(
                f"Browser context created successfully. "
                f"Total contexts: {len(self._contexts)}"
            )
            return context

        except Exception as e:
            error_context = {
                "browser_type": self._browser_type,
                "context_options": context_options,
            }
            logger.error(f"Failed to create browser context: {str(e)}", extra=error_context)
            raise RaptorException(
                f"Failed to create browser context: {str(e)}",
                context=error_context,
                cause=e,
            )

    async def create_page(
        self, context: Optional[BrowserContext] = None
    ) -> Page:
        """
        Create a new page in the specified context.

        If no context is provided, creates a new context first. Pages are
        tracked for proper cleanup.

        Args:
            context: Optional browser context. If None, creates a new context.

        Returns:
            Page instance

        Raises:
            RaptorException: If page creation fails
            
        Example:
            >>> page = await browser_manager.create_page()
            >>> await page.goto("https://example.com")
        """
        try:
            # Create context if not provided
            if context is None:
                logger.debug("No context provided, creating new context")
                context = await self.create_context()

            logger.debug("Creating new page in context")
            page = await context.new_page()
            
            # Track page for cleanup
            self._pages.append(page)
            
            logger.info(
                f"Page created successfully. Total pages: {len(self._pages)}"
            )
            return page

        except Exception as e:
            error_context = {
                "browser_type": self._browser_type,
                "has_context": context is not None,
            }
            logger.error(f"Failed to create page: {str(e)}", extra=error_context)
            raise RaptorException(
                f"Failed to create page: {str(e)}",
                context=error_context,
                cause=e,
            )

    async def close_browser(self) -> None:
        """
        Close the browser and clean up all resources.

        This method:
        1. Closes all tracked pages
        2. Closes all tracked contexts
        3. Closes the browser
        4. Stops the Playwright instance
        
        This ensures proper cleanup and prevents resource leaks.

        Raises:
            RaptorException: If cleanup fails (logged but not raised)
            
        Example:
            >>> await browser_manager.close_browser()
        """
        errors = []

        try:
            # Close all pages
            if self._pages:
                logger.debug(f"Closing {len(self._pages)} pages")
                for page in self._pages:
                    try:
                        if not page.is_closed():
                            await page.close()
                    except Exception as e:
                        errors.append(f"Failed to close page: {str(e)}")
                        logger.warning(f"Error closing page: {str(e)}")
                self._pages.clear()

            # Close all contexts
            if self._contexts:
                logger.debug(f"Closing {len(self._contexts)} contexts")
                for context in self._contexts:
                    try:
                        await context.close()
                    except Exception as e:
                        errors.append(f"Failed to close context: {str(e)}")
                        logger.warning(f"Error closing context: {str(e)}")
                self._contexts.clear()

            # Close browser
            if self._browser:
                logger.debug("Closing browser")
                try:
                    await self._browser.close()
                    logger.info(f"{self._browser_type} browser closed successfully")
                except Exception as e:
                    errors.append(f"Failed to close browser: {str(e)}")
                    logger.warning(f"Error closing browser: {str(e)}")
                finally:
                    self._browser = None
                    self._browser_type = None

            # Stop Playwright
            if self._playwright:
                logger.debug("Stopping Playwright instance")
                try:
                    await self._playwright.stop()
                    logger.info("Playwright instance stopped")
                except Exception as e:
                    errors.append(f"Failed to stop Playwright: {str(e)}")
                    logger.warning(f"Error stopping Playwright: {str(e)}")
                finally:
                    self._playwright = None

            if errors:
                logger.warning(
                    f"Browser cleanup completed with {len(errors)} errors: {errors}"
                )
            else:
                logger.info("Browser cleanup completed successfully")

        except Exception as e:
            logger.error(f"Unexpected error during browser cleanup: {str(e)}")
            # Don't raise exception during cleanup to ensure best-effort cleanup

    @property
    def browser(self) -> Optional[Browser]:
        """Get the current browser instance."""
        return self._browser

    @property
    def browser_type(self) -> Optional[str]:
        """Get the current browser type."""
        return self._browser_type

    @property
    def is_browser_launched(self) -> bool:
        """Check if a browser is currently launched and connected."""
        return self._browser is not None and self._browser.is_connected()

    def get_contexts(self) -> List[BrowserContext]:
        """Get all tracked browser contexts."""
        return self._contexts.copy()

    def get_pages(self) -> List[Page]:
        """Get all tracked pages."""
        return self._pages.copy()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensures cleanup."""
        await self.close_browser()
        return False
