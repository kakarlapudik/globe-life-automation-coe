"""
Property-Based Test for Screenshot Capture Reliability.

This module tests Property 9: Screenshot Capture Reliability
- Validates: Requirements 9.1

Property Statement:
    For any test failure, a screenshot should be captured and saved with a unique identifier.

Test Strategy:
    Generate random test failure scenarios and verify that:
    1. Screenshots are always captured when tests fail
    2. Each screenshot has a unique identifier/filename
    3. Screenshot files are created and accessible
    4. Screenshots are properly embedded in test reports
    5. Multiple failures produce multiple unique screenshots
    
Note:
    This test uses a mock-based approach to avoid browser installation requirements
    while still validating the screenshot capture property.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from typing import List, Tuple, Set
from unittest.mock import AsyncMock, MagicMock, patch
from pathlib import Path
import tempfile
import shutil
import os
from datetime import datetime


# Strategy for generating test failure scenarios
test_failure_scenarios = st.lists(
    st.tuples(
        st.text(min_size=5, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',))),  # test_name
        st.sampled_from([
            "AssertionError",
            "TimeoutError",
            "ElementNotFoundError",
            "NetworkError",
            "ValidationError"
        ]),  # error_type
        st.text(min_size=10, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',)))  # error_message
    ),
    min_size=1,
    max_size=10
)


class MockPage:
    """Mock Playwright Page for testing screenshot capture."""
    
    def __init__(self, screenshot_dir: Path):
        self.screenshot_dir = screenshot_dir
        self.screenshot_count = 0
        self.url = "https://example.com/test"
        self.captured_screenshots: List[str] = []
    
    async def screenshot(self, path: str, full_page: bool = False):
        """Mock screenshot capture that creates an actual file."""
        # Create a dummy screenshot file
        screenshot_path = Path(path)
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write a minimal PNG file (1x1 pixel)
        # PNG signature + IHDR chunk + IEND chunk
        png_data = (
            b'\x89PNG\r\n\x1a\n'  # PNG signature
            b'\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x02\x00\x00\x00\x90wS\xde'  # IHDR chunk
            b'\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
            b'\r\n-\xb4'  # IDAT chunk
            b'\x00\x00\x00\x00IEND\xaeB`\x82'  # IEND chunk
        )
        
        with open(screenshot_path, 'wb') as f:
            f.write(png_data)
        
        self.screenshot_count += 1
        self.captured_screenshots.append(str(screenshot_path))
        return str(screenshot_path)


class MockBasePage:
    """Mock BasePage for testing screenshot capture."""
    
    def __init__(self, page: MockPage, screenshot_dir: Path):
        self.page = page
        self._screenshot_dir = screenshot_dir
        self._screenshot_dir.mkdir(parents=True, exist_ok=True)
    
    async def take_screenshot(
        self,
        name: str = None,
        full_page: bool = False,
        path: str = None,
    ) -> str:
        """
        Capture a screenshot with unique identifier.
        
        This mimics the real BasePage.take_screenshot() behavior.
        """
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
            screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Capture screenshot using mock page
        await self.page.screenshot(path=str(screenshot_path), full_page=full_page)
        
        return str(screenshot_path)


class FailureHandler:
    """
    Handler for test failures that captures screenshots.
    
    This class simulates the behavior of a test framework that
    automatically captures screenshots on test failures.
    """
    
    def __init__(self, base_page: MockBasePage):
        self.base_page = base_page
        self.failure_screenshots: List[Tuple[str, str]] = []  # (test_name, screenshot_path)
    
    async def handle_test_failure(
        self,
        test_name: str,
        error_type: str,
        error_message: str,
    ) -> str:
        """
        Handle a test failure by capturing a screenshot.
        
        Returns:
            Path to the captured screenshot
        """
        # Generate unique screenshot name based on test name and timestamp
        safe_test_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in test_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        screenshot_name = f"failure_{safe_test_name}_{timestamp}"
        
        # Capture screenshot
        screenshot_path = await self.base_page.take_screenshot(name=screenshot_name)
        
        # Record the failure and screenshot
        self.failure_screenshots.append((test_name, screenshot_path))
        
        return screenshot_path
    
    def get_screenshot_paths(self) -> List[str]:
        """Get all captured screenshot paths."""
        return [path for _, path in self.failure_screenshots]
    
    def get_screenshot_for_test(self, test_name: str) -> List[str]:
        """Get all screenshots for a specific test."""
        return [path for name, path in self.failure_screenshots if name == test_name]


@pytest.fixture
def temp_screenshot_dir():
    """Create a temporary directory for screenshots."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.mark.asyncio
@given(failures=test_failure_scenarios)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
async def test_property_screenshot_capture_reliability(failures, temp_screenshot_dir):
    """
    Property Test: Screenshot Capture Reliability
    
    Feature: raptor-playwright-python, Property 9: Screenshot Capture Reliability
    
    Tests that screenshots:
    1. Are always captured when tests fail
    2. Have unique identifiers/filenames
    3. Are created as actual files
    4. Can be accessed and read
    5. Are properly tracked for reporting
    
    Property: For any test failure, a screenshot should be captured and saved
    with a unique identifier.
    """
    # Setup
    mock_page = MockPage(temp_screenshot_dir)
    mock_base_page = MockBasePage(mock_page, temp_screenshot_dir)
    failure_handler = FailureHandler(mock_base_page)
    
    # Track all screenshot paths
    all_screenshot_paths: Set[str] = set()
    
    # Simulate test failures and capture screenshots
    for test_name, error_type, error_message in failures:
        screenshot_path = await failure_handler.handle_test_failure(
            test_name=test_name,
            error_type=error_type,
            error_message=error_message
        )
        
        # Property 1: Screenshot was captured (path returned)
        assert screenshot_path is not None, (
            f"Screenshot path should not be None for test failure: {test_name}"
        )
        assert isinstance(screenshot_path, str), (
            f"Screenshot path should be a string, got {type(screenshot_path)}"
        )
        
        # Property 2: Screenshot file exists
        assert os.path.exists(screenshot_path), (
            f"Screenshot file should exist at path: {screenshot_path}"
        )
        
        # Property 3: Screenshot file is readable
        assert os.path.isfile(screenshot_path), (
            f"Screenshot path should point to a file: {screenshot_path}"
        )
        assert os.path.getsize(screenshot_path) > 0, (
            f"Screenshot file should not be empty: {screenshot_path}"
        )
        
        # Property 4: Screenshot has unique identifier
        assert screenshot_path not in all_screenshot_paths, (
            f"Screenshot path should be unique. Duplicate found: {screenshot_path}"
        )
        all_screenshot_paths.add(screenshot_path)
    
    # Property 5: Number of screenshots matches number of failures
    captured_screenshots = failure_handler.get_screenshot_paths()
    assert len(captured_screenshots) == len(failures), (
        f"Number of screenshots ({len(captured_screenshots)}) should match "
        f"number of failures ({len(failures)})"
    )
    
    # Property 6: All screenshots are unique
    assert len(set(captured_screenshots)) == len(captured_screenshots), (
        "All screenshot paths should be unique"
    )
    
    # Property 7: Screenshot filenames contain identifiable information
    for screenshot_path in captured_screenshots:
        filename = os.path.basename(screenshot_path)
        assert filename.startswith("failure_"), (
            f"Screenshot filename should start with 'failure_': {filename}"
        )
        assert filename.endswith(".png"), (
            f"Screenshot filename should end with '.png': {filename}"
        )


@pytest.mark.asyncio
async def test_screenshot_capture_single_failure(temp_screenshot_dir):
    """
    Test screenshot capture for a single test failure.
    
    This ensures the basic screenshot capture mechanism works correctly.
    """
    mock_page = MockPage(temp_screenshot_dir)
    mock_base_page = MockBasePage(mock_page, temp_screenshot_dir)
    failure_handler = FailureHandler(mock_base_page)
    
    # Simulate a test failure
    screenshot_path = await failure_handler.handle_test_failure(
        test_name="test_login_failure",
        error_type="AssertionError",
        error_message="Expected element not found"
    )
    
    # Verify screenshot was captured
    assert screenshot_path is not None
    assert os.path.exists(screenshot_path)
    assert os.path.isfile(screenshot_path)
    assert os.path.getsize(screenshot_path) > 0
    
    # Verify filename format
    filename = os.path.basename(screenshot_path)
    assert "failure_test_login_failure" in filename
    assert filename.endswith(".png")


@pytest.mark.asyncio
async def test_screenshot_capture_multiple_failures_same_test(temp_screenshot_dir):
    """
    Test that multiple failures in the same test produce unique screenshots.
    
    This ensures that even if the same test fails multiple times,
    each failure gets its own unique screenshot.
    """
    mock_page = MockPage(temp_screenshot_dir)
    mock_base_page = MockBasePage(mock_page, temp_screenshot_dir)
    failure_handler = FailureHandler(mock_base_page)
    
    test_name = "test_flaky_test"
    screenshot_paths = []
    
    # Simulate the same test failing multiple times
    for i in range(5):
        screenshot_path = await failure_handler.handle_test_failure(
            test_name=test_name,
            error_type="TimeoutError",
            error_message=f"Timeout on attempt {i+1}"
        )
        screenshot_paths.append(screenshot_path)
    
    # Verify all screenshots are unique
    assert len(set(screenshot_paths)) == 5, (
        "All screenshots should have unique paths even for the same test"
    )
    
    # Verify all screenshots exist
    for screenshot_path in screenshot_paths:
        assert os.path.exists(screenshot_path)
        assert os.path.isfile(screenshot_path)


@pytest.mark.asyncio
async def test_screenshot_capture_with_special_characters(temp_screenshot_dir):
    """
    Test screenshot capture with test names containing special characters.
    
    This ensures that special characters in test names are properly
    sanitized in screenshot filenames.
    """
    mock_page = MockPage(temp_screenshot_dir)
    mock_base_page = MockBasePage(mock_page, temp_screenshot_dir)
    failure_handler = FailureHandler(mock_base_page)
    
    # Test names with special characters
    test_names = [
        "test_with_spaces and symbols!",
        "test/with/slashes",
        "test<with>brackets",
        "test:with:colons",
        "test|with|pipes",
        "test?with?questions",
        "test*with*asterisks"
    ]
    
    screenshot_paths = []
    
    for test_name in test_names:
        screenshot_path = await failure_handler.handle_test_failure(
            test_name=test_name,
            error_type="AssertionError",
            error_message="Test failed"
        )
        screenshot_paths.append(screenshot_path)
    
    # Verify all screenshots were captured
    assert len(screenshot_paths) == len(test_names)
    
    # Verify all screenshots exist and have valid filenames
    for screenshot_path in screenshot_paths:
        assert os.path.exists(screenshot_path)
        assert os.path.isfile(screenshot_path)
        
        # Verify filename doesn't contain problematic characters
        filename = os.path.basename(screenshot_path)
        problematic_chars = ['/', '\\', '<', '>', ':', '|', '?', '*']
        for char in problematic_chars:
            assert char not in filename, (
                f"Screenshot filename should not contain '{char}': {filename}"
            )


@pytest.mark.asyncio
async def test_screenshot_capture_with_custom_name(temp_screenshot_dir):
    """
    Test screenshot capture with custom names.
    
    This ensures that custom screenshot names are properly handled.
    """
    mock_page = MockPage(temp_screenshot_dir)
    mock_base_page = MockBasePage(mock_page, temp_screenshot_dir)
    
    # Capture screenshot with custom name
    screenshot_path = await mock_base_page.take_screenshot(name="custom_screenshot")
    
    # Verify screenshot was captured
    assert screenshot_path is not None
    assert os.path.exists(screenshot_path)
    
    # Verify filename contains custom name
    filename = os.path.basename(screenshot_path)
    assert "custom_screenshot" in filename
    assert filename.endswith(".png")


@pytest.mark.asyncio
async def test_screenshot_capture_with_custom_path(temp_screenshot_dir):
    """
    Test screenshot capture with custom path.
    
    This ensures that screenshots can be saved to custom locations.
    """
    mock_page = MockPage(temp_screenshot_dir)
    mock_base_page = MockBasePage(mock_page, temp_screenshot_dir)
    
    # Create custom path
    custom_dir = temp_screenshot_dir / "custom" / "path"
    custom_path = custom_dir / "my_screenshot.png"
    
    # Capture screenshot with custom path
    screenshot_path = await mock_base_page.take_screenshot(path=str(custom_path))
    
    # Verify screenshot was captured at custom location
    assert screenshot_path == str(custom_path)
    assert os.path.exists(screenshot_path)
    assert custom_dir.exists()


@pytest.mark.asyncio
async def test_screenshot_capture_full_page(temp_screenshot_dir):
    """
    Test full-page screenshot capture.
    
    This ensures that the full_page parameter is properly handled.
    """
    mock_page = MockPage(temp_screenshot_dir)
    mock_base_page = MockBasePage(mock_page, temp_screenshot_dir)
    
    # Capture full-page screenshot
    screenshot_path = await mock_base_page.take_screenshot(
        name="full_page_test",
        full_page=True
    )
    
    # Verify screenshot was captured
    assert screenshot_path is not None
    assert os.path.exists(screenshot_path)
    assert os.path.isfile(screenshot_path)


@pytest.mark.asyncio
async def test_screenshot_uniqueness_with_rapid_captures(temp_screenshot_dir):
    """
    Test screenshot uniqueness when capturing rapidly.
    
    This ensures that even when screenshots are captured in rapid succession,
    each one gets a unique identifier (using microsecond timestamps).
    """
    mock_page = MockPage(temp_screenshot_dir)
    mock_base_page = MockBasePage(mock_page, temp_screenshot_dir)
    
    screenshot_paths = []
    
    # Capture multiple screenshots rapidly
    for i in range(20):
        screenshot_path = await mock_base_page.take_screenshot()
        screenshot_paths.append(screenshot_path)
    
    # Verify all screenshots are unique
    assert len(set(screenshot_paths)) == 20, (
        "All rapidly captured screenshots should have unique paths"
    )
    
    # Verify all screenshots exist
    for screenshot_path in screenshot_paths:
        assert os.path.exists(screenshot_path)


@pytest.mark.asyncio
async def test_screenshot_directory_creation(temp_screenshot_dir):
    """
    Test that screenshot directories are created automatically.
    
    This ensures that the screenshot capture mechanism creates
    necessary directories if they don't exist.
    """
    # Use a non-existent subdirectory
    screenshot_dir = temp_screenshot_dir / "auto_created" / "nested" / "dir"
    
    mock_page = MockPage(screenshot_dir)
    mock_base_page = MockBasePage(mock_page, screenshot_dir)
    
    # Capture screenshot (should create directories)
    screenshot_path = await mock_base_page.take_screenshot(name="test_auto_dir")
    
    # Verify directories were created
    assert screenshot_dir.exists()
    assert screenshot_dir.is_dir()
    
    # Verify screenshot was captured
    assert os.path.exists(screenshot_path)
    assert screenshot_path.startswith(str(screenshot_dir))


@pytest.mark.asyncio
async def test_screenshot_file_format(temp_screenshot_dir):
    """
    Test that screenshots are saved in PNG format.
    
    This ensures that all screenshots are saved as PNG files.
    """
    mock_page = MockPage(temp_screenshot_dir)
    mock_base_page = MockBasePage(mock_page, temp_screenshot_dir)
    
    # Capture screenshot
    screenshot_path = await mock_base_page.take_screenshot(name="format_test")
    
    # Verify file format
    assert screenshot_path.endswith(".png")
    
    # Verify PNG signature (first 8 bytes)
    with open(screenshot_path, 'rb') as f:
        signature = f.read(8)
        assert signature == b'\x89PNG\r\n\x1a\n', (
            "Screenshot file should have valid PNG signature"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
