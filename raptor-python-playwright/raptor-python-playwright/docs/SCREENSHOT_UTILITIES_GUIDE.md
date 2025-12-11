# Screenshot and Visual Utilities Guide

## Overview

The Screenshot Utilities module provides comprehensive screenshot capture and visual comparison capabilities for the RAPTOR framework. This guide covers all features including full-page screenshots, element-specific captures, visual regression testing, and image manipulation.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Screenshot Capture](#screenshot-capture)
4. [Visual Comparison](#visual-comparison)
5. [Image Manipulation](#image-manipulation)
6. [Visual Regression Testing](#visual-regression-testing)
7. [Advanced Features](#advanced-features)
8. [Best Practices](#best-practices)
9. [API Reference](#api-reference)

## Installation

The screenshot utilities are included in the RAPTOR framework. Ensure you have the required dependencies:

```bash
pip install playwright pillow
playwright install
```

## Basic Usage

### Initialize Screenshot Utilities

```python
from raptor.utils.screenshot_utilities import ScreenshotUtilities

# Initialize with default directories
screenshot_utils = ScreenshotUtilities()

# Or specify custom directories
screenshot_utils = ScreenshotUtilities(
    screenshot_dir="screenshots",
    baseline_dir="screenshots/baseline",
    diff_dir="screenshots/diff"
)
```

### Quick Screenshot Capture

```python
from raptor.utils.screenshot_utilities import capture_full_page_screenshot

# Capture full page
screenshot_path = await capture_full_page_screenshot(page)
print(f"Screenshot saved: {screenshot_path}")
```

## Screenshot Capture

### Full Page Screenshots

Capture the entire page including content below the fold:

```python
# Basic full page capture
metadata = await screenshot_utils.capture_full_page(page)

# With custom filename
metadata = await screenshot_utils.capture_full_page(
    page,
    filename="homepage_full.png"
)

# With test name for tracking
metadata = await screenshot_utils.capture_full_page(
    page,
    filename="homepage.png",
    test_name="test_homepage_layout"
)

# Access metadata
print(f"Path: {metadata.path}")
print(f"Dimensions: {metadata.width}x{metadata.height}")
print(f"Size: {metadata.size_bytes} bytes")
print(f"URL: {metadata.page_url}")
```

### Element Screenshots

Capture specific elements on the page:

```python
# Capture element by selector
metadata = await screenshot_utils.capture_element(
    page,
    selector="#login-form"
)

# With padding around element
metadata = await screenshot_utils.capture_element(
    page,
    selector=".header",
    padding=20  # 20px padding on all sides
)

# Custom filename
metadata = await screenshot_utils.capture_element(
    page,
    selector="button.submit",
    filename="submit_button.png"
)
```

### Viewport Screenshots

Capture only the visible viewport:

```python
# Capture current viewport
metadata = await screenshot_utils.capture_viewport(page)

# With custom settings
metadata = await screenshot_utils.capture_viewport(
    page,
    filename="viewport_snapshot.png",
    format=ScreenshotFormat.JPEG,
    quality=90
)
```

### Screenshot Formats

Support for multiple image formats:

```python
from raptor.utils.screenshot_utilities import ScreenshotFormat

# PNG (lossless, larger file size)
metadata = await screenshot_utils.capture_full_page(
    page,
    format=ScreenshotFormat.PNG
)

# JPEG (lossy, smaller file size)
metadata = await screenshot_utils.capture_full_page(
    page,
    format=ScreenshotFormat.JPEG,
    quality=85  # 1-100
)

# WebP (modern, efficient)
metadata = await screenshot_utils.capture_full_page(
    page,
    format=ScreenshotFormat.WEBP,
    quality=90
)
```

## Visual Comparison

### Basic Comparison

Compare two screenshots to detect visual differences:

```python
from raptor.utils.screenshot_utilities import ComparisonResult

# Compare screenshots
diff = screenshot_utils.compare_screenshots(
    baseline_path="baseline/homepage.png",
    current_path="screenshots/homepage.png",
    threshold=0.5  # 0.5% difference threshold
)

# Check results
if diff.result == ComparisonResult.IDENTICAL:
    print("Images are identical")
elif diff.result == ComparisonResult.SIMILAR:
    print(f"Images are similar ({diff.difference_percentage:.2f}% difference)")
else:
    print(f"Images are different ({diff.difference_percentage:.2f}% difference)")

# Access detailed metrics
print(f"Different pixels: {diff.different_pixels:,}")
print(f"Total pixels: {diff.total_pixels:,}")
```

### Difference Visualization

Generate visual representation of differences:

```python
# Compare with diff image generation
diff = screenshot_utils.compare_screenshots(
    baseline_path="baseline/homepage.png",
    current_path="screenshots/homepage.png",
    threshold=1.0,
    generate_diff=True,
    diff_filename="homepage_diff.png"
)

if diff.diff_image_path:
    print(f"Diff image saved: {diff.diff_image_path}")
    # Diff image shows baseline, current, and highlighted differences
```

### Baseline Management

Manage baseline images for regression testing:

```python
# Save screenshot as baseline
baseline_path = screenshot_utils.save_as_baseline(
    screenshot_path="screenshots/homepage.png",
    baseline_name="homepage_baseline.png"
)

# Check if baseline exists
baseline_path = screenshot_utils.get_baseline_path("homepage_baseline.png")
if baseline_path:
    print(f"Baseline found: {baseline_path}")
else:
    print("Baseline not found - creating new baseline")
```

## Image Manipulation

### Cropping

Crop screenshots to specific regions:

```python
# Crop to specific coordinates
cropped_path = screenshot_utils.crop_screenshot(
    image_path="screenshots/fullpage.png",
    x=100,
    y=100,
    width=400,
    height=300
)
```

### Resizing

Resize screenshots while maintaining or ignoring aspect ratio:

```python
# Resize with aspect ratio maintained
resized_path = screenshot_utils.resize_screenshot(
    image_path="screenshots/fullpage.png",
    width=800,
    height=600,
    maintain_aspect=True
)

# Resize to exact dimensions
resized_path = screenshot_utils.resize_screenshot(
    image_path="screenshots/fullpage.png",
    width=800,
    height=600,
    maintain_aspect=False
)
```

### Annotations

Add visual annotations to screenshots:

```python
# Define annotations
annotations = [
    {
        "type": "rectangle",
        "x": 100,
        "y": 100,
        "width": 200,
        "height": 150,
        "color": "red",
        "thickness": 3
    },
    {
        "type": "text",
        "x": 100,
        "y": 80,
        "text": "Error Location",
        "color": "red",
        "size": 20
    }
]

# Apply annotations
annotated_path = screenshot_utils.annotate_screenshot(
    image_path="screenshots/error_page.png",
    annotations=annotations
)
```

### Image Information

Get detailed information about images:

```python
# Get image info
info = screenshot_utils.get_image_info("screenshots/homepage.png")

print(f"Format: {info['format']}")
print(f"Dimensions: {info['width']}x{info['height']}")
print(f"File size: {info['file_size_kb']:.2f} KB")
print(f"Mode: {info['mode']}")
```

### Image Hashing

Calculate image hashes for quick comparison:

```python
# Calculate hash
hash1 = screenshot_utils.calculate_image_hash("image1.png")
hash2 = screenshot_utils.calculate_image_hash("image2.png")

if hash1 == hash2:
    print("Images are identical (byte-for-byte)")
else:
    print("Images are different")
```

## Visual Regression Testing

### Complete Workflow

Implement visual regression testing in your test suite:

```python
import pytest
from raptor.utils.screenshot_utilities import ScreenshotUtilities, ComparisonResult

@pytest.fixture
def screenshot_utils():
    return ScreenshotUtilities(
        screenshot_dir="screenshots/tests",
        baseline_dir="screenshots/baseline",
        diff_dir="screenshots/diff"
    )

@pytest.mark.asyncio
async def test_homepage_visual_regression(page, screenshot_utils):
    """Test homepage for visual regressions."""
    test_name = "homepage_visual"
    baseline_name = f"{test_name}_baseline.png"
    
    # Navigate to page
    await page.goto("https://example.com")
    
    # Check for baseline
    baseline_path = screenshot_utils.get_baseline_path(baseline_name)
    
    if baseline_path is None:
        # First run - create baseline
        metadata = await screenshot_utils.capture_full_page(
            page,
            test_name=test_name
        )
        screenshot_utils.save_as_baseline(
            screenshot_path=metadata.path,
            baseline_name=baseline_name
        )
        pytest.skip("Baseline created - run test again to compare")
    
    # Capture current screenshot
    current_metadata = await screenshot_utils.capture_full_page(
        page,
        test_name=test_name
    )
    
    # Compare with baseline
    diff = screenshot_utils.compare_screenshots(
        baseline_path=baseline_path,
        current_path=current_metadata.path,
        threshold=1.0,  # 1% threshold
        generate_diff=True
    )
    
    # Assert no significant differences
    assert diff.result in [ComparisonResult.IDENTICAL, ComparisonResult.SIMILAR], \
        f"Visual regression detected: {diff.difference_percentage:.2f}% difference. " \
        f"Review diff: {diff.diff_image_path}"
```

### Updating Baselines

When intentional changes are made:

```python
@pytest.mark.asyncio
async def test_update_baseline(page, screenshot_utils):
    """Update baseline after intentional UI changes."""
    await page.goto("https://example.com")
    
    # Capture new screenshot
    metadata = await screenshot_utils.capture_full_page(page)
    
    # Update baseline
    baseline_path = screenshot_utils.save_as_baseline(
        screenshot_path=metadata.path,
        baseline_name="homepage_baseline.png"
    )
    
    print(f"Baseline updated: {baseline_path}")
```

## Advanced Features

### Base64 Encoding

Convert screenshots to base64 for embedding in reports:

```python
# Convert to base64
base64_str = screenshot_utils.convert_to_base64("screenshots/error.png")

# Use in HTML reports
html = f'<img src="data:image/png;base64,{base64_str}" />'
```

### Cleanup Old Screenshots

Automatically clean up old screenshots:

```python
# Delete screenshots older than 7 days
deleted_count = screenshot_utils.cleanup_old_screenshots(days=7)
print(f"Deleted {deleted_count} old screenshots")
```

### Custom Screenshot Directories

Organize screenshots by test suite or feature:

```python
# Feature-specific directories
login_utils = ScreenshotUtilities(
    screenshot_dir="screenshots/login",
    baseline_dir="screenshots/baseline/login"
)

checkout_utils = ScreenshotUtilities(
    screenshot_dir="screenshots/checkout",
    baseline_dir="screenshots/baseline/checkout"
)
```

## Best Practices

### 1. Organize Screenshots

```python
# Use descriptive filenames
metadata = await screenshot_utils.capture_full_page(
    page,
    filename=f"{test_name}_{timestamp}.png"
)

# Organize by feature/module
screenshot_utils = ScreenshotUtilities(
    screenshot_dir=f"screenshots/{feature_name}"
)
```

### 2. Set Appropriate Thresholds

```python
# Strict comparison for critical UI
diff = screenshot_utils.compare_screenshots(
    baseline_path=baseline,
    current_path=current,
    threshold=0.1  # 0.1% threshold
)

# Relaxed comparison for dynamic content
diff = screenshot_utils.compare_screenshots(
    baseline_path=baseline,
    current_path=current,
    threshold=5.0  # 5% threshold
)
```

### 3. Handle Dynamic Content

```python
# Wait for dynamic content to load
await page.wait_for_load_state("networkidle")
await page.wait_for_timeout(1000)  # Additional wait if needed

# Then capture screenshot
metadata = await screenshot_utils.capture_full_page(page)
```

### 4. Use Element Screenshots for Stability

```python
# More stable than full page for specific components
metadata = await screenshot_utils.capture_element(
    page,
    selector=".main-content",  # Exclude dynamic headers/footers
    padding=10
)
```

### 5. Version Control Baselines

```
# Commit baselines to version control
screenshots/
  baseline/
    homepage_baseline.png
    login_baseline.png
    checkout_baseline.png
```

### 6. CI/CD Integration

```python
# In CI environment, fail on differences
if diff.result == ComparisonResult.DIFFERENT:
    # Save artifacts for review
    print(f"Visual regression detected!")
    print(f"Diff image: {diff.diff_image_path}")
    raise AssertionError(f"Visual regression: {diff.difference_percentage:.2f}%")
```

## API Reference

### ScreenshotUtilities Class

#### Constructor

```python
ScreenshotUtilities(
    screenshot_dir: str = "screenshots",
    baseline_dir: str = "screenshots/baseline",
    diff_dir: str = "screenshots/diff"
)
```

#### Methods

**capture_full_page(page, filename=None, format=ScreenshotFormat.PNG, quality=90, test_name=None)**
- Capture full-page screenshot
- Returns: `ScreenshotMetadata`

**capture_element(page, selector, filename=None, format=ScreenshotFormat.PNG, quality=90, test_name=None, padding=0)**
- Capture element-specific screenshot
- Returns: `ScreenshotMetadata`

**capture_viewport(page, filename=None, format=ScreenshotFormat.PNG, quality=90, test_name=None)**
- Capture viewport screenshot
- Returns: `ScreenshotMetadata`

**compare_screenshots(baseline_path, current_path, threshold=0.1, generate_diff=True, diff_filename=None)**
- Compare two screenshots
- Returns: `VisualDifference`

**save_as_baseline(screenshot_path, baseline_name=None)**
- Save screenshot as baseline
- Returns: `str` (baseline path)

**get_baseline_path(baseline_name)**
- Get path to baseline image
- Returns: `Optional[str]`

**calculate_image_hash(image_path)**
- Calculate MD5 hash of image
- Returns: `str`

**crop_screenshot(image_path, x, y, width, height, output_path=None)**
- Crop screenshot to region
- Returns: `str` (output path)

**resize_screenshot(image_path, width, height, output_path=None, maintain_aspect=True)**
- Resize screenshot
- Returns: `str` (output path)

**annotate_screenshot(image_path, annotations, output_path=None)**
- Add annotations to screenshot
- Returns: `str` (output path)

**convert_to_base64(image_path)**
- Convert image to base64
- Returns: `str`

**get_image_info(image_path)**
- Get image information
- Returns: `Dict[str, Any]`

**cleanup_old_screenshots(days=7)**
- Clean up old screenshots
- Returns: `int` (deleted count)

### Convenience Functions

**capture_full_page_screenshot(page, filename=None, screenshot_dir="screenshots")**
- Quick full page capture
- Returns: `str` (screenshot path)

**capture_element_screenshot(page, selector, filename=None, screenshot_dir="screenshots")**
- Quick element capture
- Returns: `str` (screenshot path)

**compare_images(baseline_path, current_path, threshold=0.1)**
- Quick image comparison
- Returns: `bool` (True if similar)

### Data Classes

**ScreenshotMetadata**
- filename: str
- path: str
- timestamp: datetime
- width: int
- height: int
- format: ScreenshotFormat
- size_bytes: int
- element_selector: Optional[str]
- page_url: Optional[str]
- test_name: Optional[str]

**VisualDifference**
- result: ComparisonResult
- difference_percentage: float
- total_pixels: int
- different_pixels: int
- diff_image_path: Optional[str]
- threshold: float
- metadata: Dict[str, Any]

### Enums

**ScreenshotFormat**
- PNG
- JPEG
- WEBP

**ComparisonResult**
- IDENTICAL
- SIMILAR
- DIFFERENT

## Troubleshooting

### Issue: Screenshots are too large

**Solution**: Use JPEG or WebP format with lower quality:

```python
metadata = await screenshot_utils.capture_full_page(
    page,
    format=ScreenshotFormat.JPEG,
    quality=75
)
```

### Issue: Comparison always shows differences

**Solution**: Increase threshold or wait for page to stabilize:

```python
# Wait for animations to complete
await page.wait_for_timeout(1000)

# Use higher threshold
diff = screenshot_utils.compare_screenshots(
    baseline_path=baseline,
    current_path=current,
    threshold=2.0  # More lenient
)
```

### Issue: Element not found

**Solution**: Wait for element to be visible:

```python
# Wait for element
await page.wait_for_selector(selector, state="visible")

# Then capture
metadata = await screenshot_utils.capture_element(page, selector)
```

## Examples

See `examples/screenshot_utilities_example.py` for complete working examples.

## Related Documentation

- [Test Reporter Guide](TEST_REPORTER_GUIDE.md)
- [Base Page Guide](BASE_PAGE_QUICK_REFERENCE.md)
- [Element Manager Guide](ELEMENT_MANAGER_IMPLEMENTATION.md)
