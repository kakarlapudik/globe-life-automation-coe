"""V3 System Setup Page Object."""
from typing import Optional
from playwright.async_api import Page
from raptor.pages.base_page import BasePage
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
import logging

logger = logging.getLogger(__name__)

class SystemSetup(BasePage):
    """Page Object for V3 System Setup Module."""
    
    def __init__(self, page: Page, element_manager: Optional[ElementManager] = None, config: Optional[ConfigManager] = None):
        super().__init__(page, element_manager, config)
        self.locators = {"system_setup_menu": "css=a[href*='system-setup']"}
        logger.info("V3 SystemSetup page initialized")
    
    async def navigate_to_system_setup(self, base_url: Optional[str] = None) -> None:
        url = base_url or self.config.get("base_url", "")
        full_url = f"{url}/system-setup" if url else "/system-setup"
        await self.navigate(full_url)
