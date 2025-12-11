"""
Screenshot and Visual Utilities for RAPTOR Framework

This module provides comprehensive screenshot and visual testing capabilities including:
- Full-page screenshot capture
- Element-specific screenshot capture
- Screenshot comparison utilities
- Visual regression helpers
- Image manipulation and analysis
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from PIL import Image, ImageChops, ImageDraw, ImageFont
import io
import base64


class ScreenshotFormat(Enum):
    """Supported screenshot formats."""
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"


class ComparisonResult(Enum):
    """Visual comparison result status."""
    IDENTICAL = "identical"
    SIMILAR = "similar"
    DIFFERENT = "different"


@dataclass
class ScreenshotMetadata:
    """
    Metadata for captured screenshots.
    
    Attributes:
        filename: Screenshot filename
        path: Full path to screenshot file
        timestamp: Capture timestamp
        width: Image width in pixels
        height: Image height in pixels
        format: Image format
        size_bytes: File size in bytes
        element_selector: Element selector if element screenshot
        page_url: URL of the page when captured
        test_name: Associated test name
    """
    filename: str
    path: str
    timestamp: datetime
    width: int
    height: int
    format: ScreenshotFormat
    size_bytes: int
    element_selector: Optional[str] = None
    page_url: Optional[str] = None
    test_name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "filename": self.filename,
            "path": self.path,
            "timestamp": self.timestamp.isoformat(),
            "width": self.width,
            "height": self.height,
            "format": self.format.value,
            "size_bytes": self.size_bytes,
            "element_selector": self.element_selector,
            "page_url": self.page_url,
            "test_name": self.test_name,
        }


@dataclass
class VisualDifference:
    """
    Represents visual differences between two images.
    
    Attributes:
        result: Comparison result status
        difference_percentage: Percentage of different pixels
        total_pixels: Total number of pixels compared
        different_pixels: Number of different pixels
        diff_image_path: Path to difference visualization image
        threshold: Threshold used for comparison
        metadata: Additional comparison metadata
    """
    result: ComparisonResult
    difference_percentage: float
    total_pixels: int
    different_pixels: int
    diff_image_path: Optional[str] = None
    threshold: float = 0.0
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert visual difference to dictionary."""
        return {
            "result": self.result.value,
            "difference_percentage": self.difference_percentage,
            "total_pixels": self.total_pixels,
            "different_pixels": self.different_pixels,
            "diff_image_path": self.diff_image_path,
            "threshold": self.threshold,
            "metadata": self.metadata or {},
        }


class ScreenshotUtilities:
    """
    Provides screenshot capture and visual comparison utilities.
    
    This class handles all screenshot-related operations including:
    - Full-page and element-specific captures
    - Visual comparison and regression testing
    - Image manipulation and analysis
    """
    
    def __init__(
        self,
        screenshot_dir: str = "screenshots",
        baseline_dir: str = "screenshots/baseline",
        diff_dir: str = "screenshots/diff"
    ):
        """
        Initialize ScreenshotUtilities.
        
        Args:
            screenshot_dir: Directory for storing screenshots
            baseline_dir: Directory for baseline images
            diff_dir: Directory for difference images
        """
        self.screenshot_dir = Path(screenshot_dir)
        self.baseline_dir = Path(baseline_dir)
        self.diff_dir = Path(diff_dir)
        
        # Create directories
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self.diff_dir.mkdir(parents=True, exist_ok=True)
        
        self.screenshot_counter = 0
    
    async def capture_full_page(
        self,
        page,
        filename: Optional[str] = None,
        format: ScreenshotFormat = ScreenshotFormat.PNG,
        quality: int = 90,
        test_name: Optional[str] = None
    ) -> ScreenshotMetadata:
        """
        Capture a full-page screenshot.
        
        Args:
            page: Playwright Page object
            filename: Optional custom filename
            format: Screenshot format (PNG, JPEG, WEBP)
            quality: Image quality (1-100, for JPEG/WEBP)
            test_name: Associated test name
            
        Returns:
            ScreenshotMetadata object with capture details
            
        Example:
            >>> metadata = await screenshot_utils.capture_full_page(
            ...     page,
            ...     filename="homepage_full.png",
            ...     test_name="test_homepage_layout"
            ... )
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.screenshot_counter += 1
            filename = f"fullpage_{timestamp}_{self.screenshot_counter}.{format.value}"
        
        screenshot_path = self.screenshot_dir / filename
        
        # Capture full page screenshot
        screenshot_options = {
            "path": str(screenshot_path),
            "full_page": True,
            "type": format.value,
        }
        
        if format in [ScreenshotFormat.JPEG, ScreenshotFormat.WEBP]:
            screenshot_options["quality"] = quality
        
        await page.screenshot(**screenshot_options)
        
        # Get image dimensions and metadata
        with Image.open(screenshot_path) as img:
            width, height = img.size
        
        file_size = os.path.getsize(screenshot_path)
        page_url = page.url
        
        metadata = ScreenshotMetadata(
            filename=filename,
            path=str(screenshot_path),
            timestamp=datetime.now(),
            width=width,
            height=height,
            format=format,
            size_bytes=file_size,
            page_url=page_url,
            test_name=test_name
        )
        
        return metadata
    
    async def capture_element(
        self,
        page,
        selector: str,
        filename: Optional[str] = None,
        format: ScreenshotFormat = ScreenshotFormat.PNG,
        quality: int = 90,
        test_name: Optional[str] = None,
        padding: int = 0
    ) -> ScreenshotMetadata:
        """
        Capture a screenshot of a specific element.
        
        Args:
            page: Playwright Page object
            selector: Element selector
            filename: Optional custom filename
            format: Screenshot format
            quality: Image quality (1-100)
            test_name: Associated test name
            padding: Padding around element in pixels
            
        Returns:
            ScreenshotMetadata object with capture details
            
        Example:
            >>> metadata = await screenshot_utils.capture_element(
            ...     page,
            ...     selector="#login-form",
            ...     filename="login_form.png",
            ...     padding=10
            ... )
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.screenshot_counter += 1
            safe_selector = selector.replace("#", "").replace(".", "").replace(" ", "_")[:30]
            filename = f"element_{safe_selector}_{timestamp}_{self.screenshot_counter}.{format.value}"
        
        screenshot_path = self.screenshot_dir / filename
        
        # Locate element
        element = page.locator(selector).first
        
        # Wait for element to be visible
        await element.wait_for(state="visible", timeout=10000)
        
        # Capture element screenshot
        screenshot_options = {
            "path": str(screenshot_path),
            "type": format.value,
        }
        
        if format in [ScreenshotFormat.JPEG, ScreenshotFormat.WEBP]:
            screenshot_options["quality"] = quality
        
        await element.screenshot(**screenshot_options)
        
        # Add padding if requested
        if padding > 0:
            self._add_padding_to_image(screenshot_path, padding)
        
        # Get image dimensions and metadata
        with Image.open(screenshot_path) as img:
            width, height = img.size
        
        file_size = os.path.getsize(screenshot_path)
        page_url = page.url
        
        metadata = ScreenshotMetadata(
            filename=filename,
            path=str(screenshot_path),
            timestamp=datetime.now(),
            width=width,
            height=height,
            format=format,
            size_bytes=file_size,
            element_selector=selector,
            page_url=page_url,
            test_name=test_name
        )
        
        return metadata
    
    async def capture_viewport(
        self,
        page,
        filename: Optional[str] = None,
        format: ScreenshotFormat = ScreenshotFormat.PNG,
        quality: int = 90,
        test_name: Optional[str] = None
    ) -> ScreenshotMetadata:
        """
        Capture a screenshot of the current viewport only.
        
        Args:
            page: Playwright Page object
            filename: Optional custom filename
            format: Screenshot format
            quality: Image quality (1-100)
            test_name: Associated test name
            
        Returns:
            ScreenshotMetadata object with capture details
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.screenshot_counter += 1
            filename = f"viewport_{timestamp}_{self.screenshot_counter}.{format.value}"
        
        screenshot_path = self.screenshot_dir / filename
        
        # Capture viewport screenshot
        screenshot_options = {
            "path": str(screenshot_path),
            "full_page": False,
            "type": format.value,
        }
        
        if format in [ScreenshotFormat.JPEG, ScreenshotFormat.WEBP]:
            screenshot_options["quality"] = quality
        
        await page.screenshot(**screenshot_options)
        
        # Get image dimensions and metadata
        with Image.open(screenshot_path) as img:
            width, height = img.size
        
        file_size = os.path.getsize(screenshot_path)
        page_url = page.url
        
        metadata = ScreenshotMetadata(
            filename=filename,
            path=str(screenshot_path),
            timestamp=datetime.now(),
            width=width,
            height=height,
            format=format,
            size_bytes=file_size,
            page_url=page_url,
            test_name=test_name
        )
        
        return metadata
    
    def compare_screenshots(
        self,
        baseline_path: str,
        current_path: str,
        threshold: float = 0.1,
        generate_diff: bool = True,
        diff_filename: Optional[str] = None
    ) -> VisualDifference:
        """
        Compare two screenshots and detect visual differences.
        
        Args:
            baseline_path: Path to baseline image
            current_path: Path to current image
            threshold: Difference threshold percentage (0-100)
            generate_diff: Whether to generate difference image
            diff_filename: Optional custom diff filename
            
        Returns:
            VisualDifference object with comparison results
            
        Example:
            >>> diff = screenshot_utils.compare_screenshots(
            ...     baseline_path="baseline/homepage.png",
            ...     current_path="screenshots/homepage.png",
            ...     threshold=0.5
            ... )
            >>> if diff.result == ComparisonResult.DIFFERENT:
            ...     print(f"Images differ by {diff.difference_percentage}%")
        """
        # Load images
        baseline_img = Image.open(baseline_path).convert("RGB")
        current_img = Image.open(current_path).convert("RGB")
        
        # Ensure images are same size
        if baseline_img.size != current_img.size:
            # Resize current to match baseline
            current_img = current_img.resize(baseline_img.size, Image.Resampling.LANCZOS)
        
        # Calculate pixel differences
        diff_img = ImageChops.difference(baseline_img, current_img)
        
        # Count different pixels
        diff_pixels = 0
        total_pixels = baseline_img.size[0] * baseline_img.size[1]
        
        # Convert to grayscale for easier comparison
        diff_gray = diff_img.convert("L")
        pixels = list(diff_gray.getdata())
        
        # Count pixels that differ (non-zero values)
        diff_pixels = sum(1 for pixel in pixels if pixel > 10)  # Threshold of 10 to ignore minor variations
        
        # Calculate difference percentage
        difference_percentage = (diff_pixels / total_pixels) * 100
        
        # Determine result
        if difference_percentage == 0:
            result = ComparisonResult.IDENTICAL
        elif difference_percentage <= threshold:
            result = ComparisonResult.SIMILAR
        else:
            result = ComparisonResult.DIFFERENT
        
        # Generate difference visualization
        diff_image_path = None
        if generate_diff and difference_percentage > 0:
            if diff_filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                diff_filename = f"diff_{timestamp}.png"
            
            diff_image_path = str(self.diff_dir / diff_filename)
            self._create_diff_visualization(
                baseline_img,
                current_img,
                diff_img,
                diff_image_path,
                difference_percentage
            )
        
        return VisualDifference(
            result=result,
            difference_percentage=difference_percentage,
            total_pixels=total_pixels,
            different_pixels=diff_pixels,
            diff_image_path=diff_image_path,
            threshold=threshold,
            metadata={
                "baseline_path": baseline_path,
                "current_path": current_path,
                "baseline_size": baseline_img.size,
                "current_size": current_img.size,
            }
        )
    
    def save_as_baseline(
        self,
        screenshot_path: str,
        baseline_name: Optional[str] = None
    ) -> str:
        """
        Save a screenshot as a baseline for future comparisons.
        
        Args:
            screenshot_path: Path to screenshot to save as baseline
            baseline_name: Optional custom baseline name
            
        Returns:
            Path to saved baseline image
            
        Example:
            >>> baseline_path = screenshot_utils.save_as_baseline(
            ...     screenshot_path="screenshots/homepage.png",
            ...     baseline_name="homepage_baseline.png"
            ... )
        """
        if baseline_name is None:
            baseline_name = os.path.basename(screenshot_path)
        
        baseline_path = self.baseline_dir / baseline_name
        
        # Copy image to baseline directory
        img = Image.open(screenshot_path)
        img.save(baseline_path)
        
        return str(baseline_path)
    
    def get_baseline_path(self, baseline_name: str) -> Optional[str]:
        """
        Get the path to a baseline image.
        
        Args:
            baseline_name: Name of baseline image
            
        Returns:
            Path to baseline image or None if not found
        """
        baseline_path = self.baseline_dir / baseline_name
        if baseline_path.exists():
            return str(baseline_path)
        return None
    
    def calculate_image_hash(self, image_path: str) -> str:
        """
        Calculate a hash of an image for quick comparison.
        
        Args:
            image_path: Path to image file
            
        Returns:
            MD5 hash of the image
            
        Example:
            >>> hash1 = screenshot_utils.calculate_image_hash("image1.png")
            >>> hash2 = screenshot_utils.calculate_image_hash("image2.png")
            >>> if hash1 == hash2:
            ...     print("Images are identical")
        """
        with open(image_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def crop_screenshot(
        self,
        image_path: str,
        x: int,
        y: int,
        width: int,
        height: int,
        output_path: Optional[str] = None
    ) -> str:
        """
        Crop a screenshot to a specific region.
        
        Args:
            image_path: Path to source image
            x: X coordinate of crop region
            y: Y coordinate of crop region
            width: Width of crop region
            height: Height of crop region
            output_path: Optional output path
            
        Returns:
            Path to cropped image
        """
        img = Image.open(image_path)
        cropped = img.crop((x, y, x + width, y + height))
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.screenshot_dir / f"cropped_{timestamp}.png")
        
        cropped.save(output_path)
        return output_path
    
    def resize_screenshot(
        self,
        image_path: str,
        width: int,
        height: int,
        output_path: Optional[str] = None,
        maintain_aspect: bool = True
    ) -> str:
        """
        Resize a screenshot.
        
        Args:
            image_path: Path to source image
            width: Target width
            height: Target height
            output_path: Optional output path
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Path to resized image
        """
        img = Image.open(image_path)
        
        if maintain_aspect:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
        else:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.screenshot_dir / f"resized_{timestamp}.png")
        
        img.save(output_path)
        return output_path
    
    def annotate_screenshot(
        self,
        image_path: str,
        annotations: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> str:
        """
        Add annotations (rectangles, text) to a screenshot.
        
        Args:
            image_path: Path to source image
            annotations: List of annotation dictionaries
            output_path: Optional output path
            
        Returns:
            Path to annotated image
            
        Example:
            >>> annotations = [
            ...     {"type": "rectangle", "x": 100, "y": 100, "width": 200, "height": 150, "color": "red"},
            ...     {"type": "text", "x": 100, "y": 80, "text": "Error here", "color": "red"}
            ... ]
            >>> annotated_path = screenshot_utils.annotate_screenshot(
            ...     "screenshot.png",
            ...     annotations
            ... )
        """
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        for annotation in annotations:
            ann_type = annotation.get("type")
            
            if ann_type == "rectangle":
                x = annotation.get("x", 0)
                y = annotation.get("y", 0)
                width = annotation.get("width", 100)
                height = annotation.get("height", 100)
                color = annotation.get("color", "red")
                thickness = annotation.get("thickness", 2)
                
                # Draw rectangle
                for i in range(thickness):
                    draw.rectangle(
                        [x + i, y + i, x + width - i, y + height - i],
                        outline=color
                    )
            
            elif ann_type == "text":
                x = annotation.get("x", 0)
                y = annotation.get("y", 0)
                text = annotation.get("text", "")
                color = annotation.get("color", "red")
                size = annotation.get("size", 20)
                
                # Draw text (using default font)
                draw.text((x, y), text, fill=color)
        
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = str(self.screenshot_dir / f"annotated_{timestamp}.png")
        
        img.save(output_path)
        return output_path
    
    def convert_to_base64(self, image_path: str) -> str:
        """
        Convert an image to base64 string.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded string
        """
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    
    def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """
        Get detailed information about an image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with image information
        """
        img = Image.open(image_path)
        
        return {
            "path": image_path,
            "filename": os.path.basename(image_path),
            "format": img.format,
            "mode": img.mode,
            "size": img.size,
            "width": img.size[0],
            "height": img.size[1],
            "file_size_bytes": os.path.getsize(image_path),
            "file_size_kb": os.path.getsize(image_path) / 1024,
            "file_size_mb": os.path.getsize(image_path) / (1024 * 1024),
        }
    
    def _add_padding_to_image(self, image_path: str, padding: int) -> None:
        """Add padding around an image."""
        img = Image.open(image_path)
        width, height = img.size
        
        new_width = width + (padding * 2)
        new_height = height + (padding * 2)
        
        new_img = Image.new("RGB", (new_width, new_height), "white")
        new_img.paste(img, (padding, padding))
        new_img.save(image_path)
    
    def _create_diff_visualization(
        self,
        baseline_img: Image.Image,
        current_img: Image.Image,
        diff_img: Image.Image,
        output_path: str,
        difference_percentage: float
    ) -> None:
        """Create a visual representation of differences."""
        # Create a side-by-side comparison with diff
        width, height = baseline_img.size
        
        # Create new image with 3 columns
        comparison_img = Image.new("RGB", (width * 3, height + 50), "white")
        
        # Paste images
        comparison_img.paste(baseline_img, (0, 50))
        comparison_img.paste(current_img, (width, 50))
        
        # Highlight differences in red
        diff_highlighted = Image.new("RGB", (width, height), "white")
        diff_highlighted.paste(current_img, (0, 0))
        
        # Overlay differences in red
        pixels_baseline = baseline_img.load()
        pixels_current = current_img.load()
        pixels_diff = diff_highlighted.load()
        
        for y in range(height):
            for x in range(width):
                if pixels_baseline[x, y] != pixels_current[x, y]:
                    # Highlight difference in red
                    pixels_diff[x, y] = (255, 0, 0)
        
        comparison_img.paste(diff_highlighted, (width * 2, 50))
        
        # Add labels
        draw = ImageDraw.Draw(comparison_img)
        draw.text((10, 10), "Baseline", fill="black")
        draw.text((width + 10, 10), "Current", fill="black")
        draw.text((width * 2 + 10, 10), f"Diff ({difference_percentage:.2f}%)", fill="red")
        
        comparison_img.save(output_path)
    
    def cleanup_old_screenshots(self, days: int = 7) -> int:
        """
        Clean up screenshots older than specified days.
        
        Args:
            days: Number of days to keep screenshots
            
        Returns:
            Number of files deleted
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        for screenshot_file in self.screenshot_dir.glob("*"):
            if screenshot_file.is_file():
                file_time = datetime.fromtimestamp(screenshot_file.stat().st_mtime)
                if file_time < cutoff_time:
                    screenshot_file.unlink()
                    deleted_count += 1
        
        return deleted_count


# Convenience functions for quick access
async def capture_full_page_screenshot(
    page,
    filename: Optional[str] = None,
    screenshot_dir: str = "screenshots"
) -> str:
    """
    Quick function to capture a full-page screenshot.
    
    Args:
        page: Playwright Page object
        filename: Optional custom filename
        screenshot_dir: Screenshot directory
        
    Returns:
        Path to captured screenshot
    """
    utils = ScreenshotUtilities(screenshot_dir=screenshot_dir)
    metadata = await utils.capture_full_page(page, filename=filename)
    return metadata.path


async def capture_element_screenshot(
    page,
    selector: str,
    filename: Optional[str] = None,
    screenshot_dir: str = "screenshots"
) -> str:
    """
    Quick function to capture an element screenshot.
    
    Args:
        page: Playwright Page object
        selector: Element selector
        filename: Optional custom filename
        screenshot_dir: Screenshot directory
        
    Returns:
        Path to captured screenshot
    """
    utils = ScreenshotUtilities(screenshot_dir=screenshot_dir)
    metadata = await utils.capture_element(page, selector, filename=filename)
    return metadata.path


def compare_images(
    baseline_path: str,
    current_path: str,
    threshold: float = 0.1
) -> bool:
    """
    Quick function to compare two images.
    
    Args:
        baseline_path: Path to baseline image
        current_path: Path to current image
        threshold: Difference threshold percentage
        
    Returns:
        True if images are similar, False otherwise
    """
    utils = ScreenshotUtilities()
    diff = utils.compare_screenshots(baseline_path, current_path, threshold)
    return diff.result in [ComparisonResult.IDENTICAL, ComparisonResult.SIMILAR]
