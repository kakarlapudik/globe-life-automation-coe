"""
Tests for Screenshot Utilities

This module tests the screenshot and visual comparison functionality.
"""

import pytest
import os
from pathlib import Path
from PIL import Image, ImageDraw
from raptor.utils.screenshot_utilities import (
    ScreenshotUtilities,
    ScreenshotFormat,
    ComparisonResult,
    capture_full_page_screenshot,
    capture_element_screenshot,
    compare_images
)


@pytest.fixture
def screenshot_utils(tmp_path):
    """Create ScreenshotUtilities instance with temporary directories."""
    screenshot_dir = tmp_path / "screenshots"
    baseline_dir = tmp_path / "baseline"
    diff_dir = tmp_path / "diff"
    
    return ScreenshotUtilities(
        screenshot_dir=str(screenshot_dir),
        baseline_dir=str(baseline_dir),
        diff_dir=str(diff_dir)
    )


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample test image."""
    img_path = tmp_path / "sample.png"
    img = Image.new("RGB", (800, 600), color="white")
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 300, 300], fill="blue")
    img.save(img_path)
    return str(img_path)


@pytest.fixture
def sample_image_modified(tmp_path):
    """Create a modified version of the sample image."""
    img_path = tmp_path / "sample_modified.png"
    img = Image.new("RGB", (800, 600), color="white")
    draw = ImageDraw.Draw(img)
    draw.rectangle([100, 100, 300, 300], fill="red")  # Different color
    img.save(img_path)
    return str(img_path)


@pytest.mark.asyncio
class TestFullPageScreenshot:
    """Test full-page screenshot capture."""
    
    async def test_capture_full_page_default(self, screenshot_utils, page):
        """Test capturing full page with default settings."""
        await page.goto("https://example.com")
        
        metadata = await screenshot_utils.capture_full_page(page)
        
        assert metadata is not None
        assert os.path.exists(metadata.path)
        assert metadata.width > 0
        assert metadata.height > 0
        assert metadata.format == ScreenshotFormat.PNG
        assert metadata.page_url == "https://example.com/"
    
    async def test_capture_full_page_custom_filename(self, screenshot_utils, page):
        """Test capturing full page with custom filename."""
        await page.goto("https://example.com")
        
        metadata = await screenshot_utils.capture_full_page(
            page,
            filename="custom_screenshot.png"
        )
        
        assert "custom_screenshot.png" in metadata.path
        assert os.path.exists(metadata.path)
    
    async def test_capture_full_page_jpeg_format(self, screenshot_utils, page):
        """Test capturing full page in JPEG format."""
        await page.goto("https://example.com")
        
        metadata = await screenshot_utils.capture_full_page(
            page,
            format=ScreenshotFormat.JPEG,
            quality=85
        )
        
        assert metadata.format == ScreenshotFormat.JPEG
        assert metadata.path.endswith(".jpeg")
        assert os.path.exists(metadata.path)
    
    async def test_capture_full_page_with_test_name(self, screenshot_utils, page):
        """Test capturing full page with test name metadata."""
        await page.goto("https://example.com")
        
        metadata = await screenshot_utils.capture_full_page(
            page,
            test_name="test_homepage_layout"
        )
        
        assert metadata.test_name == "test_homepage_layout"


@pytest.mark.asyncio
class TestElementScreenshot:
    """Test element-specific screenshot capture."""
    
    async def test_capture_element(self, screenshot_utils, page):
        """Test capturing element screenshot."""
        await page.goto("https://example.com")
        
        metadata = await screenshot_utils.capture_element(
            page,
            selector="h1"
        )
        
        assert metadata is not None
        assert os.path.exists(metadata.path)
        assert metadata.element_selector == "h1"
        assert metadata.width > 0
        assert metadata.height > 0
    
    async def test_capture_element_with_padding(self, screenshot_utils, page):
        """Test capturing element with padding."""
        await page.goto("https://example.com")
        
        # Capture without padding
        metadata1 = await screenshot_utils.capture_element(
            page,
            selector="h1",
            padding=0
        )
        
        # Capture with padding
        metadata2 = await screenshot_utils.capture_element(
            page,
            selector="h1",
            padding=20
        )
        
        # Image with padding should be larger
        assert metadata2.width > metadata1.width
        assert metadata2.height > metadata1.height
    
    async def test_capture_element_custom_filename(self, screenshot_utils, page):
        """Test capturing element with custom filename."""
        await page.goto("https://example.com")
        
        metadata = await screenshot_utils.capture_element(
            page,
            selector="h1",
            filename="heading_screenshot.png"
        )
        
        assert "heading_screenshot.png" in metadata.path


@pytest.mark.asyncio
class TestViewportScreenshot:
    """Test viewport screenshot capture."""
    
    async def test_capture_viewport(self, screenshot_utils, page):
        """Test capturing viewport screenshot."""
        await page.goto("https://example.com")
        
        metadata = await screenshot_utils.capture_viewport(page)
        
        assert metadata is not None
        assert os.path.exists(metadata.path)
        assert metadata.width > 0
        assert metadata.height > 0


class TestScreenshotComparison:
    """Test screenshot comparison functionality."""
    
    def test_compare_identical_images(self, screenshot_utils, sample_image):
        """Test comparing identical images."""
        diff = screenshot_utils.compare_screenshots(
            baseline_path=sample_image,
            current_path=sample_image,
            threshold=0.1
        )
        
        assert diff.result == ComparisonResult.IDENTICAL
        assert diff.difference_percentage == 0.0
        assert diff.different_pixels == 0
    
    def test_compare_different_images(self, screenshot_utils, sample_image, sample_image_modified):
        """Test comparing different images."""
        diff = screenshot_utils.compare_screenshots(
            baseline_path=sample_image,
            current_path=sample_image_modified,
            threshold=0.1,
            generate_diff=True
        )
        
        assert diff.result == ComparisonResult.DIFFERENT
        assert diff.difference_percentage > 0
        assert diff.different_pixels > 0
        assert diff.diff_image_path is not None
        assert os.path.exists(diff.diff_image_path)
    
    def test_compare_with_threshold(self, screenshot_utils, sample_image, sample_image_modified):
        """Test comparison with high threshold."""
        diff = screenshot_utils.compare_screenshots(
            baseline_path=sample_image,
            current_path=sample_image_modified,
            threshold=50.0  # High threshold
        )
        
        # With high threshold, might be considered similar
        assert diff.result in [ComparisonResult.SIMILAR, ComparisonResult.DIFFERENT]
    
    def test_compare_without_diff_generation(self, screenshot_utils, sample_image, sample_image_modified):
        """Test comparison without generating diff image."""
        diff = screenshot_utils.compare_screenshots(
            baseline_path=sample_image,
            current_path=sample_image_modified,
            generate_diff=False
        )
        
        assert diff.diff_image_path is None


class TestBaselineManagement:
    """Test baseline image management."""
    
    def test_save_as_baseline(self, screenshot_utils, sample_image):
        """Test saving screenshot as baseline."""
        baseline_path = screenshot_utils.save_as_baseline(
            screenshot_path=sample_image,
            baseline_name="test_baseline.png"
        )
        
        assert os.path.exists(baseline_path)
        assert "baseline" in baseline_path
    
    def test_get_baseline_path_exists(self, screenshot_utils, sample_image):
        """Test getting path to existing baseline."""
        # Save baseline first
        screenshot_utils.save_as_baseline(
            screenshot_path=sample_image,
            baseline_name="test_baseline.png"
        )
        
        # Get baseline path
        baseline_path = screenshot_utils.get_baseline_path("test_baseline.png")
        
        assert baseline_path is not None
        assert os.path.exists(baseline_path)
    
    def test_get_baseline_path_not_exists(self, screenshot_utils):
        """Test getting path to non-existent baseline."""
        baseline_path = screenshot_utils.get_baseline_path("nonexistent.png")
        
        assert baseline_path is None


class TestImageManipulation:
    """Test image manipulation utilities."""
    
    def test_calculate_image_hash(self, screenshot_utils, sample_image):
        """Test calculating image hash."""
        hash1 = screenshot_utils.calculate_image_hash(sample_image)
        hash2 = screenshot_utils.calculate_image_hash(sample_image)
        
        assert hash1 == hash2
        assert len(hash1) == 32  # MD5 hash length
    
    def test_crop_screenshot(self, screenshot_utils, sample_image):
        """Test cropping screenshot."""
        cropped_path = screenshot_utils.crop_screenshot(
            image_path=sample_image,
            x=100,
            y=100,
            width=200,
            height=200
        )
        
        assert os.path.exists(cropped_path)
        
        # Verify dimensions
        img = Image.open(cropped_path)
        assert img.size == (200, 200)
    
    def test_resize_screenshot(self, screenshot_utils, sample_image):
        """Test resizing screenshot."""
        resized_path = screenshot_utils.resize_screenshot(
            image_path=sample_image,
            width=400,
            height=300,
            maintain_aspect=False
        )
        
        assert os.path.exists(resized_path)
        
        # Verify dimensions
        img = Image.open(resized_path)
        assert img.size == (400, 300)
    
    def test_resize_screenshot_maintain_aspect(self, screenshot_utils, sample_image):
        """Test resizing screenshot with aspect ratio maintained."""
        resized_path = screenshot_utils.resize_screenshot(
            image_path=sample_image,
            width=400,
            height=400,
            maintain_aspect=True
        )
        
        assert os.path.exists(resized_path)
        
        # Verify dimensions (should be smaller than 400x400 due to aspect ratio)
        img = Image.open(resized_path)
        assert img.size[0] <= 400
        assert img.size[1] <= 400
    
    def test_annotate_screenshot(self, screenshot_utils, sample_image):
        """Test annotating screenshot."""
        annotations = [
            {
                "type": "rectangle",
                "x": 50,
                "y": 50,
                "width": 100,
                "height": 100,
                "color": "red",
                "thickness": 3
            },
            {
                "type": "text",
                "x": 50,
                "y": 30,
                "text": "Test Annotation",
                "color": "blue"
            }
        ]
        
        annotated_path = screenshot_utils.annotate_screenshot(
            image_path=sample_image,
            annotations=annotations
        )
        
        assert os.path.exists(annotated_path)


class TestImageInfo:
    """Test image information utilities."""
    
    def test_get_image_info(self, screenshot_utils, sample_image):
        """Test getting image information."""
        info = screenshot_utils.get_image_info(sample_image)
        
        assert info["width"] == 800
        assert info["height"] == 600
        assert info["size"] == (800, 600)
        assert "file_size_bytes" in info
        assert "file_size_kb" in info
        assert "file_size_mb" in info
    
    def test_convert_to_base64(self, screenshot_utils, sample_image):
        """Test converting image to base64."""
        base64_str = screenshot_utils.convert_to_base64(sample_image)
        
        assert base64_str is not None
        assert len(base64_str) > 0
        assert isinstance(base64_str, str)


class TestCleanup:
    """Test cleanup functionality."""
    
    def test_cleanup_old_screenshots(self, screenshot_utils, sample_image, tmp_path):
        """Test cleaning up old screenshots."""
        # Copy sample image to screenshot directory
        import shutil
        screenshot_path = screenshot_utils.screenshot_dir / "old_screenshot.png"
        shutil.copy(sample_image, screenshot_path)
        
        # Modify file time to be old
        import time
        old_time = time.time() - (8 * 24 * 60 * 60)  # 8 days ago
        os.utime(screenshot_path, (old_time, old_time))
        
        # Clean up screenshots older than 7 days
        deleted_count = screenshot_utils.cleanup_old_screenshots(days=7)
        
        assert deleted_count == 1
        assert not screenshot_path.exists()


@pytest.mark.asyncio
class TestConvenienceFunctions:
    """Test convenience functions."""
    
    async def test_capture_full_page_screenshot_function(self, page, tmp_path):
        """Test convenience function for full page screenshot."""
        await page.goto("https://example.com")
        
        screenshot_path = await capture_full_page_screenshot(
            page,
            screenshot_dir=str(tmp_path)
        )
        
        assert os.path.exists(screenshot_path)
    
    async def test_capture_element_screenshot_function(self, page, tmp_path):
        """Test convenience function for element screenshot."""
        await page.goto("https://example.com")
        
        screenshot_path = await capture_element_screenshot(
            page,
            selector="h1",
            screenshot_dir=str(tmp_path)
        )
        
        assert os.path.exists(screenshot_path)
    
    def test_compare_images_function(self, sample_image, sample_image_modified):
        """Test convenience function for image comparison."""
        # Identical images
        result = compare_images(sample_image, sample_image, threshold=0.1)
        assert result is True
        
        # Different images
        result = compare_images(sample_image, sample_image_modified, threshold=0.1)
        assert result is False


class TestMetadata:
    """Test metadata handling."""
    
    @pytest.mark.asyncio
    async def test_metadata_to_dict(self, screenshot_utils, page):
        """Test converting metadata to dictionary."""
        await page.goto("https://example.com")
        
        metadata = await screenshot_utils.capture_full_page(page)
        metadata_dict = metadata.to_dict()
        
        assert isinstance(metadata_dict, dict)
        assert "filename" in metadata_dict
        assert "path" in metadata_dict
        assert "timestamp" in metadata_dict
        assert "width" in metadata_dict
        assert "height" in metadata_dict
    
    def test_visual_difference_to_dict(self, screenshot_utils, sample_image):
        """Test converting visual difference to dictionary."""
        diff = screenshot_utils.compare_screenshots(
            baseline_path=sample_image,
            current_path=sample_image
        )
        
        diff_dict = diff.to_dict()
        
        assert isinstance(diff_dict, dict)
        assert "result" in diff_dict
        assert "difference_percentage" in diff_dict
        assert "total_pixels" in diff_dict
        assert "different_pixels" in diff_dict


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling in screenshot utilities."""
    
    async def test_capture_element_not_found(self, screenshot_utils, page):
        """Test capturing screenshot of non-existent element."""
        await page.goto("https://example.com")
        
        with pytest.raises(Exception):
            await screenshot_utils.capture_element(
                page,
                selector="#nonexistent-element-12345"
            )
    
    def test_compare_nonexistent_files(self, screenshot_utils):
        """Test comparing non-existent files."""
        with pytest.raises(Exception):
            screenshot_utils.compare_screenshots(
                baseline_path="nonexistent1.png",
                current_path="nonexistent2.png"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
