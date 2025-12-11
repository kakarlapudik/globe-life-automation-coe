"""
Unit tests for BasePage class.

Tests cover:
- Navigation functionality
- Page load waiting
- Screenshot capture
- Title and URL retrieval
- JavaScript execution
- Browser history navigation (back, forward)
- Page reload
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from raptor.pages.base_page import BasePage
from raptor.core.element_manager import ElementManager
from raptor.core.config_manager import ConfigManager
from raptor.core.exceptions import TimeoutException, RaptorException


@pytest.fixture
def mock_page():
    """Create a mock Playwright Page."""
    page = AsyncMock(spec=Page)
    page.url = "https://example.com"
    page.title = AsyncMock(return_value="Example Page")
    page.goto = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.screenshot = AsyncMock()
    page.evaluate = AsyncMock()
    page.reload = AsyncMock()
    page.go_back = AsyncMock()
    page.go_forward = AsyncMock()
    page.is_closed = Mock(return_value=False)
    return page


@pytest.fixture
def mock_element_manager(mock_page):
    """Create a mock ElementManager."""
    return Mock(spec=ElementManager)


@pytest.fixture
def mock_config():
    """Create a mock ConfigManager."""
    config = Mock(spec=ConfigManager)
    config.get_timeout = Mock(return_value=30000)
    config.get = Mock(return_value="screenshots")
    return config


@pytest.fixture
def base_page(mock_page, mock_element_manager, mock_config):
    """Create a BasePage instance with mocked dependencies."""
    return BasePage(mock_page, mock_element_manager, mock_config)


class TestBasePageInitialization:
    """Tests for BasePage initialization."""
    
    def test_init_with_all_parameters(self, mock_page, mock_element_manager, mock_config):
        """Test initialization with all parameters provided."""
        page = BasePage(mock_page, mock_element_manager, mock_config)
        
        assert page.page == mock_page
        assert page.element_manager == mock_element_manager
        assert page.config == mock_config
        assert page._default_timeout == 30000
    
    def test_init_creates_element_manager_if_not_provided(self, mock_page, mock_config):
        """Test that ElementManager is created if not provided."""
        with patch('raptor.pages.base_page.ElementManager') as MockElementManager:
            page = BasePage(mock_page, config=mock_config)
            MockElementManager.assert_called_once()
    
    def test_init_creates_config_if_not_provided(self, mock_page, mock_element_manager):
        """Test that ConfigManager is created if not provided."""
        with patch('raptor.pages.base_page.ConfigManager') as MockConfigManager:
            page = BasePage(mock_page, mock_element_manager)
            MockConfigManager.assert_called_once()
    
    def test_screenshot_directory_created(self, mock_page, mock_element_manager, mock_config):
        """Test that screenshot directory is created during initialization."""
        with patch('raptor.pages.base_page.Path.mkdir') as mock_mkdir:
            page = BasePage(mock_page, mock_element_manager, mock_config)
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)


class TestNavigate:
    """Tests for navigate() method."""
    
    @pytest.mark.asyncio
    async def test_navigate_success(self, base_page, mock_page):
        """Test successful navigation to a URL."""
        mock_response = Mock()
        mock_response.status = 200
        mock_page.goto.return_value = mock_response
        
        await base_page.navigate("https://example.com")
        
        mock_page.goto.assert_called_once_with(
            "https://example.com",
            wait_until="load",
            timeout=30000
        )
    
    @pytest.mark.asyncio
    async def test_navigate_with_custom_wait_until(self, base_page, mock_page):
        """Test navigation with custom wait_until parameter."""
        mock_response = Mock()
        mock_response.status = 200
        mock_page.goto.return_value = mock_response
        
        await base_page.navigate("https://example.com", wait_until="networkidle")
        
        mock_page.goto.assert_called_once_with(
            "https://example.com",
            wait_until="networkidle",
            timeout=30000
        )
    
    @pytest.mark.asyncio
    async def test_navigate_with_custom_timeout(self, base_page, mock_page):
        """Test navigation with custom timeout."""
        mock_response = Mock()
        mock_response.status = 200
        mock_page.goto.return_value = mock_response
        
        await base_page.navigate("https://example.com", timeout=10000)
        
        mock_page.goto.assert_called_once_with(
            "https://example.com",
            wait_until="load",
            timeout=10000
        )
    
    @pytest.mark.asyncio
    async def test_navigate_timeout_raises_exception(self, base_page, mock_page):
        """Test that navigation timeout raises TimeoutException."""
        mock_page.goto.side_effect = PlaywrightTimeoutError("Navigation timeout")
        
        with pytest.raises(TimeoutException) as exc_info:
            await base_page.navigate("https://example.com")
        
        assert "navigate to https://example.com" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_navigate_error_raises_exception(self, base_page, mock_page):
        """Test that navigation error raises RaptorException."""
        mock_page.goto.side_effect = Exception("Network error")
        
        with pytest.raises(RaptorException) as exc_info:
            await base_page.navigate("https://example.com")
        
        assert "Failed to navigate" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_navigate_handles_http_errors(self, base_page, mock_page):
        """Test that navigation handles HTTP error status codes."""
        mock_response = Mock()
        mock_response.status = 404
        mock_page.goto.return_value = mock_response
        
        # Should not raise exception, just log warning
        await base_page.navigate("https://example.com/notfound")
        
        mock_page.goto.assert_called_once()


class TestWaitForLoad:
    """Tests for wait_for_load() method."""
    
    @pytest.mark.asyncio
    async def test_wait_for_load_default_state(self, base_page, mock_page):
        """Test waiting for default load state."""
        await base_page.wait_for_load()
        
        mock_page.wait_for_load_state.assert_called_once_with(
            state="load",
            timeout=30000
        )
    
    @pytest.mark.asyncio
    async def test_wait_for_load_custom_state(self, base_page, mock_page):
        """Test waiting for custom load state."""
        await base_page.wait_for_load(state="networkidle")
        
        mock_page.wait_for_load_state.assert_called_once_with(
            state="networkidle",
            timeout=30000
        )
    
    @pytest.mark.asyncio
    async def test_wait_for_load_custom_timeout(self, base_page, mock_page):
        """Test waiting with custom timeout."""
        await base_page.wait_for_load(timeout=10000)
        
        mock_page.wait_for_load_state.assert_called_once_with(
            state="load",
            timeout=10000
        )
    
    @pytest.mark.asyncio
    async def test_wait_for_load_timeout_raises_exception(self, base_page, mock_page):
        """Test that wait timeout raises TimeoutException."""
        mock_page.wait_for_load_state.side_effect = PlaywrightTimeoutError("Timeout")
        
        with pytest.raises(TimeoutException) as exc_info:
            await base_page.wait_for_load()
        
        assert "wait_for_load_state" in str(exc_info.value)


class TestTakeScreenshot:
    """Tests for take_screenshot() method."""
    
    @pytest.mark.asyncio
    async def test_take_screenshot_with_name(self, base_page, mock_page):
        """Test taking screenshot with custom name."""
        with patch('raptor.pages.base_page.Path.mkdir'):
            screenshot_path = await base_page.take_screenshot("test_screenshot")
        
        assert "test_screenshot.png" in screenshot_path
        mock_page.screenshot.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_take_screenshot_without_name(self, base_page, mock_page):
        """Test taking screenshot with auto-generated name."""
        with patch('raptor.pages.base_page.Path.mkdir'):
            screenshot_path = await base_page.take_screenshot()
        
        assert "screenshot_" in screenshot_path
        assert ".png" in screenshot_path
        mock_page.screenshot.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_take_screenshot_full_page(self, base_page, mock_page):
        """Test taking full page screenshot."""
        with patch('raptor.pages.base_page.Path.mkdir'):
            await base_page.take_screenshot("full_page", full_page=True)
        
        call_args = mock_page.screenshot.call_args
        assert call_args[1]['full_page'] is True
    
    @pytest.mark.asyncio
    async def test_take_screenshot_custom_path(self, base_page, mock_page):
        """Test taking screenshot with custom path."""
        custom_path = "/custom/path/screenshot.png"
        
        with patch('raptor.pages.base_page.Path.mkdir'):
            screenshot_path = await base_page.take_screenshot(path=custom_path)
        
        # Normalize paths for cross-platform comparison
        assert Path(screenshot_path) == Path(custom_path)
        mock_page.screenshot.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_take_screenshot_error_raises_exception(self, base_page, mock_page):
        """Test that screenshot error raises RaptorException."""
        mock_page.screenshot.side_effect = Exception("Screenshot failed")
        
        with patch('raptor.pages.base_page.Path.mkdir'):
            with pytest.raises(RaptorException) as exc_info:
                await base_page.take_screenshot()
        
        assert "Failed to capture screenshot" in str(exc_info.value)


class TestGetTitleAndUrl:
    """Tests for get_title() and get_url() methods."""
    
    @pytest.mark.asyncio
    async def test_get_title(self, base_page, mock_page):
        """Test getting page title."""
        mock_page.title.return_value = "Test Page"
        
        title = await base_page.get_title()
        
        assert title == "Test Page"
        mock_page.title.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_title_error_raises_exception(self, base_page, mock_page):
        """Test that title retrieval error raises RaptorException."""
        mock_page.title.side_effect = Exception("Title error")
        
        with pytest.raises(RaptorException) as exc_info:
            await base_page.get_title()
        
        assert "Failed to get page title" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_get_url(self, base_page, mock_page):
        """Test getting page URL."""
        mock_page.url = "https://test.com"
        
        url = await base_page.get_url()
        
        assert url == "https://test.com"


class TestExecuteScript:
    """Tests for execute_script() method."""
    
    @pytest.mark.asyncio
    async def test_execute_script_simple(self, base_page, mock_page):
        """Test executing simple JavaScript."""
        mock_page.evaluate.return_value = 42
        
        result = await base_page.execute_script("return 42")
        
        assert result == 42
        mock_page.evaluate.assert_called_once_with("return 42")
    
    @pytest.mark.asyncio
    async def test_execute_script_with_arguments(self, base_page, mock_page):
        """Test executing JavaScript with arguments."""
        mock_page.evaluate.return_value = 30
        
        result = await base_page.execute_script(
            "return arguments[0] + arguments[1]",
            10,
            20
        )
        
        assert result == 30
        mock_page.evaluate.assert_called_once_with(
            "return arguments[0] + arguments[1]",
            10,
            20
        )
    
    @pytest.mark.asyncio
    async def test_execute_script_returns_object(self, base_page, mock_page):
        """Test executing JavaScript that returns an object."""
        mock_page.evaluate.return_value = {"width": 1920, "height": 1080}
        
        result = await base_page.execute_script(
            "return {width: window.innerWidth, height: window.innerHeight}"
        )
        
        assert result == {"width": 1920, "height": 1080}
    
    @pytest.mark.asyncio
    async def test_execute_script_error_raises_exception(self, base_page, mock_page):
        """Test that script execution error raises RaptorException."""
        mock_page.evaluate.side_effect = Exception("Script error")
        
        with pytest.raises(RaptorException) as exc_info:
            await base_page.execute_script("invalid script")
        
        assert "Failed to execute JavaScript" in str(exc_info.value)


class TestBrowserNavigation:
    """Tests for browser navigation methods (reload, go_back, go_forward)."""
    
    @pytest.mark.asyncio
    async def test_reload(self, base_page, mock_page):
        """Test page reload."""
        await base_page.reload()
        
        mock_page.reload.assert_called_once_with(
            wait_until="load",
            timeout=30000
        )
    
    @pytest.mark.asyncio
    async def test_reload_with_custom_wait_until(self, base_page, mock_page):
        """Test page reload with custom wait_until."""
        await base_page.reload(wait_until="networkidle")
        
        mock_page.reload.assert_called_once_with(
            wait_until="networkidle",
            timeout=30000
        )
    
    @pytest.mark.asyncio
    async def test_reload_timeout_raises_exception(self, base_page, mock_page):
        """Test that reload timeout raises TimeoutException."""
        mock_page.reload.side_effect = PlaywrightTimeoutError("Timeout")
        
        with pytest.raises(TimeoutException):
            await base_page.reload()
    
    @pytest.mark.asyncio
    async def test_go_back(self, base_page, mock_page):
        """Test going back in browser history."""
        await base_page.go_back()
        
        mock_page.go_back.assert_called_once_with(
            wait_until="load",
            timeout=30000
        )
    
    @pytest.mark.asyncio
    async def test_go_back_timeout_raises_exception(self, base_page, mock_page):
        """Test that go_back timeout raises TimeoutException."""
        mock_page.go_back.side_effect = PlaywrightTimeoutError("Timeout")
        
        with pytest.raises(TimeoutException):
            await base_page.go_back()
    
    @pytest.mark.asyncio
    async def test_go_forward(self, base_page, mock_page):
        """Test going forward in browser history."""
        await base_page.go_forward()
        
        mock_page.go_forward.assert_called_once_with(
            wait_until="load",
            timeout=30000
        )
    
    @pytest.mark.asyncio
    async def test_go_forward_timeout_raises_exception(self, base_page, mock_page):
        """Test that go_forward timeout raises TimeoutException."""
        mock_page.go_forward.side_effect = PlaywrightTimeoutError("Timeout")
        
        with pytest.raises(TimeoutException):
            await base_page.go_forward()


class TestGetters:
    """Tests for getter methods."""
    
    def test_get_page(self, base_page, mock_page):
        """Test getting the Playwright Page object."""
        page = base_page.get_page()
        assert page == mock_page
    
    def test_get_element_manager(self, base_page, mock_element_manager):
        """Test getting the ElementManager."""
        element_manager = base_page.get_element_manager()
        assert element_manager == mock_element_manager
    
    def test_get_config(self, base_page, mock_config):
        """Test getting the ConfigManager."""
        config = base_page.get_config()
        assert config == mock_config


class TestCustomPageObject:
    """Tests for custom page objects inheriting from BasePage."""
    
    @pytest.mark.asyncio
    async def test_custom_page_object_inheritance(self, mock_page, mock_element_manager):
        """Test that custom page objects can inherit from BasePage."""
        
        class CustomPage(BasePage):
            def __init__(self, page, element_manager=None):
                super().__init__(page, element_manager)
                self.login_button = "css=#login"
            
            async def click_login(self):
                await self.element_manager.click(self.login_button)
        
        custom_page = CustomPage(mock_page, mock_element_manager)
        
        assert custom_page.login_button == "css=#login"
        assert custom_page.page == mock_page
        assert custom_page.element_manager == mock_element_manager
        
        # Test custom method
        await custom_page.click_login()
        mock_element_manager.click.assert_called_once_with("css=#login")
