# Screenshot Utilities - Quick Reference

## Import

```python
from raptor.utils.screenshot_utilities import (
    ScreenshotUtilities,
    ScreenshotFormat,
    ComparisonResult,
    capture_full_page_screenshot,
    capture_element_screenshot,
    compare_images
)
```

## Initialization

```python
screenshot_utils = ScreenshotUtilities(
    screenshot_dir="screenshots",
    baseline_dir="screenshots/baseline",
    diff_dir="screenshots/diff"
)
```

## Screenshot Capture

### Full Page

```python
# Basic
metadata = await screenshot_utils.capture_full_page(page)

# With options
metadata = await screenshot_utils.capture_full_page(
    page,
    filename="homepage.png",
    format=ScreenshotFormat.PNG,
    quality=90,
    test_name="test_homepage"
)
```

### Element

```python
# Basic
metadata = await screenshot_utils.capture_element(page, selector="#login-form")

# With padding
metadata = await screenshot_utils.capture_element(
    page,
    selector=".header",
    padding=20
)
```

### Viewport

```python
metadata = await screenshot_utils.capture_viewport(page)
```

## Visual Comparison

### Compare Screenshots

```python
diff = screenshot_utils.compare_screenshots(
    baseline_path="baseline/homepage.png",
    current_path="screenshots/homepage.png",
    threshold=0.5,
    generate_diff=True
)

# Check result
if diff.result == ComparisonResult.IDENTICAL:
    print("Identical")
elif diff.result == ComparisonResult.SIMILAR:
    print(f"Similar: {diff.difference_percentage:.2f}%")
else:
    print(f"Different: {diff.difference_percentage:.2f}%")
```

### Baseline Management

```python
# Save as baseline
baseline_path = screenshot_utils.save_as_baseline(
    screenshot_path="screenshots/homepage.png",
    baseline_name="homepage_baseline.png"
)

# Get baseline path
baseline_path = screenshot_utils.get_baseline_path("homepage_baseline.png")
```

## Image Manipulation

### Crop

```python
cropped_path = screenshot_utils.crop_screenshot(
    image_path="screenshot.png",
    x=100, y=100,
    width=400, height=300
)
```

### Resize

```python
resized_path = screenshot_utils.resize_screenshot(
    image_path="screenshot.png",
    width=800, height=600,
    maintain_aspect=True
)
```

### Annotate

```python
annotations = [
    {"type": "rectangle", "x": 100, "y": 100, "width": 200, "height": 150, "color": "red"},
    {"type": "text", "x": 100, "y": 80, "text": "Error", "color": "red"}
]

annotated_path = screenshot_utils.annotate_screenshot(
    image_path="screenshot.png",
    annotations=annotations
)
```

## Utilities

### Image Hash

```python
hash_value = screenshot_utils.calculate_image_hash("screenshot.png")
```

### Image Info

```python
info = screenshot_utils.get_image_info("screenshot.png")
print(f"{info['width']}x{info['height']}, {info['file_size_kb']:.2f} KB")
```

### Base64 Encoding

```python
base64_str = screenshot_utils.convert_to_base64("screenshot.png")
```

### Cleanup

```python
deleted_count = screenshot_utils.cleanup_old_screenshots(days=7)
```

## Convenience Functions

### Quick Capture

```python
# Full page
path = await capture_full_page_screenshot(page, filename="test.png")

# Element
path = await capture_element_screenshot(page, selector="#form")
```

### Quick Compare

```python
are_similar = compare_images(
    baseline_path="baseline.png",
    current_path="current.png",
    threshold=0.5
)
```

## Screenshot Formats

```python
# PNG (lossless)
format=ScreenshotFormat.PNG

# JPEG (lossy, smaller)
format=ScreenshotFormat.JPEG, quality=85

# WebP (modern, efficient)
format=ScreenshotFormat.WEBP, quality=90
```

## Visual Regression Test Pattern

```python
@pytest.mark.asyncio
async def test_visual_regression(page, screenshot_utils):
    baseline_name = "test_baseline.png"
    
    await page.goto("https://example.com")
    
    # Check for baseline
    baseline_path = screenshot_utils.get_baseline_path(baseline_name)
    
    if baseline_path is None:
        # Create baseline
        metadata = await screenshot_utils.capture_full_page(page)
        screenshot_utils.save_as_baseline(metadata.path, baseline_name)
        pytest.skip("Baseline created")
    
    # Compare
    current = await screenshot_utils.capture_full_page(page)
    diff = screenshot_utils.compare_screenshots(
        baseline_path=baseline_path,
        current_path=current.path,
        threshold=1.0
    )
    
    assert diff.result in [ComparisonResult.IDENTICAL, ComparisonResult.SIMILAR]
```

## Common Patterns

### Capture on Failure

```python
try:
    # Test code
    assert condition
except AssertionError:
    await screenshot_utils.capture_full_page(
        page,
        filename=f"failure_{test_name}.png"
    )
    raise
```

### Multiple Elements

```python
selectors = ["#header", "#content", "#footer"]

for selector in selectors:
    await screenshot_utils.capture_element(
        page,
        selector=selector,
        filename=f"{selector.replace('#', '')}.png"
    )
```

### Before/After Comparison

```python
# Before action
before = await screenshot_utils.capture_full_page(page, filename="before.png")

# Perform action
await page.click("button")

# After action
after = await screenshot_utils.capture_full_page(page, filename="after.png")

# Compare
diff = screenshot_utils.compare_screenshots(before.path, after.path)
```

## Metadata Access

```python
metadata = await screenshot_utils.capture_full_page(page)

# Access properties
print(metadata.filename)
print(metadata.path)
print(metadata.timestamp)
print(metadata.width)
print(metadata.height)
print(metadata.format)
print(metadata.size_bytes)
print(metadata.page_url)
print(metadata.test_name)

# Convert to dict
metadata_dict = metadata.to_dict()
```

## Comparison Results

```python
diff = screenshot_utils.compare_screenshots(baseline, current)

# Access properties
print(diff.result)                    # ComparisonResult enum
print(diff.difference_percentage)     # float
print(diff.total_pixels)              # int
print(diff.different_pixels)          # int
print(diff.diff_image_path)           # Optional[str]
print(diff.threshold)                 # float

# Convert to dict
diff_dict = diff.to_dict()
```

## Tips

- Use PNG for lossless quality
- Use JPEG/WebP for smaller file sizes
- Set appropriate thresholds (0.1-2.0% typical)
- Wait for page stability before capturing
- Use element screenshots for focused testing
- Clean up old screenshots regularly
- Version control baseline images
- Generate diff images for debugging
