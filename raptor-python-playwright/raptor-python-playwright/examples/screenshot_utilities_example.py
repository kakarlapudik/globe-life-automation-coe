"""
Screenshot Utilities Example

This example demonstrates how to use the screenshot and visual comparison utilities
in the RAPTOR framework.
"""

import asyncio
from playwright.async_api import async_playwright
from raptor.utils.screenshot_utilities import (
    ScreenshotUtilities,
    ScreenshotFormat,
    ComparisonResult,
    capture_full_page_screenshot,
    capture_element_screenshot,
    compare_images
)


async def example_basic_screenshots():
    """Example: Basic screenshot capture."""
    print("\n=== Basic Screenshot Capture ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Initialize screenshot utilities
        screenshot_utils = ScreenshotUtilities(
            screenshot_dir="screenshots/examples",
            baseline_dir="screenshots/baseline",
            diff_dir="screenshots/diff"
        )
        
        # Navigate to a page
        await page.goto("https://example.com")
        
        # Capture full page screenshot
        print("Capturing full page screenshot...")
        metadata = await screenshot_utils.capture_full_page(
            page,
            filename="example_fullpage.png",
            test_name="example_basic_test"
        )
        print(f"✓ Full page screenshot saved: {metadata.path}")
        print(f"  Dimensions: {metadata.width}x{metadata.height}")
        print(f"  Size: {metadata.size_bytes / 1024:.2f} KB")
        
        # Capture viewport screenshot
        print("\nCapturing viewport screenshot...")
        viewport_metadata = await screenshot_utils.capture_viewport(
            page,
            filename="example_viewport.png"
        )
        print(f"✓ Viewport screenshot saved: {viewport_metadata.path}")
        
        # Capture element screenshot
        print("\nCapturing element screenshot...")
        element_metadata = await screenshot_utils.capture_element(
            page,
            selector="h1",
            filename="example_heading.png",
            padding=10
        )
        print(f"✓ Element screenshot saved: {element_metadata.path}")
        print(f"  Element: {element_metadata.element_selector}")
        
        await browser.close()


async def example_visual_comparison():
    """Example: Visual comparison and regression testing."""
    print("\n=== Visual Comparison ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        screenshot_utils = ScreenshotUtilities(
            screenshot_dir="screenshots/examples",
            baseline_dir="screenshots/baseline",
            diff_dir="screenshots/diff"
        )
        
        # Navigate and capture baseline
        await page.goto("https://example.com")
        
        print("Capturing baseline screenshot...")
        baseline_metadata = await screenshot_utils.capture_full_page(
            page,
            filename="comparison_baseline.png"
        )
        
        # Save as baseline
        baseline_path = screenshot_utils.save_as_baseline(
            screenshot_path=baseline_metadata.path,
            baseline_name="example_baseline.png"
        )
        print(f"✓ Baseline saved: {baseline_path}")
        
        # Capture current screenshot
        print("\nCapturing current screenshot...")
        current_metadata = await screenshot_utils.capture_full_page(
            page,
            filename="comparison_current.png"
        )
        
        # Compare screenshots
        print("\nComparing screenshots...")
        diff = screenshot_utils.compare_screenshots(
            baseline_path=baseline_path,
            current_path=current_metadata.path,
            threshold=0.5,
            generate_diff=True
        )
        
        print(f"✓ Comparison complete:")
        print(f"  Result: {diff.result.value}")
        print(f"  Difference: {diff.difference_percentage:.2f}%")
        print(f"  Different pixels: {diff.different_pixels:,} / {diff.total_pixels:,}")
        
        if diff.diff_image_path:
            print(f"  Diff image: {diff.diff_image_path}")
        
        # Interpret results
        if diff.result == ComparisonResult.IDENTICAL:
            print("\n✓ Images are identical - No visual changes detected")
        elif diff.result == ComparisonResult.SIMILAR:
            print(f"\n⚠ Images are similar - Minor differences within {diff.threshold}% threshold")
        else:
            print(f"\n✗ Images are different - Changes exceed {diff.threshold}% threshold")
        
        await browser.close()


async def example_image_manipulation():
    """Example: Image manipulation utilities."""
    print("\n=== Image Manipulation ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        screenshot_utils = ScreenshotUtilities(
            screenshot_dir="screenshots/examples"
        )
        
        await page.goto("https://example.com")
        
        # Capture screenshot
        metadata = await screenshot_utils.capture_full_page(
            page,
            filename="manipulation_source.png"
        )
        
        # Crop screenshot
        print("Cropping screenshot...")
        cropped_path = screenshot_utils.crop_screenshot(
            image_path=metadata.path,
            x=100,
            y=100,
            width=400,
            height=300,
            output_path="screenshots/examples/cropped_example.png"
        )
        print(f"✓ Cropped screenshot: {cropped_path}")
        
        # Resize screenshot
        print("\nResizing screenshot...")
        resized_path = screenshot_utils.resize_screenshot(
            image_path=metadata.path,
            width=800,
            height=600,
            maintain_aspect=True,
            output_path="screenshots/examples/resized_example.png"
        )
        print(f"✓ Resized screenshot: {resized_path}")
        
        # Annotate screenshot
        print("\nAnnotating screenshot...")
        annotations = [
            {
                "type": "rectangle",
                "x": 50,
                "y": 50,
                "width": 200,
                "height": 150,
                "color": "red",
                "thickness": 3
            },
            {
                "type": "text",
                "x": 50,
                "y": 30,
                "text": "Important Area",
                "color": "red",
                "size": 20
            }
        ]
        
        annotated_path = screenshot_utils.annotate_screenshot(
            image_path=metadata.path,
            annotations=annotations,
            output_path="screenshots/examples/annotated_example.png"
        )
        print(f"✓ Annotated screenshot: {annotated_path}")
        
        # Get image info
        print("\nGetting image information...")
        info = screenshot_utils.get_image_info(metadata.path)
        print(f"✓ Image info:")
        print(f"  Format: {info['format']}")
        print(f"  Dimensions: {info['width']}x{info['height']}")
        print(f"  File size: {info['file_size_kb']:.2f} KB")
        
        # Calculate hash
        print("\nCalculating image hash...")
        hash_value = screenshot_utils.calculate_image_hash(metadata.path)
        print(f"✓ Image hash: {hash_value}")
        
        await browser.close()


async def example_convenience_functions():
    """Example: Using convenience functions."""
    print("\n=== Convenience Functions ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto("https://example.com")
        
        # Quick full page screenshot
        print("Quick full page screenshot...")
        screenshot_path = await capture_full_page_screenshot(
            page,
            filename="quick_fullpage.png",
            screenshot_dir="screenshots/examples"
        )
        print(f"✓ Screenshot saved: {screenshot_path}")
        
        # Quick element screenshot
        print("\nQuick element screenshot...")
        element_path = await capture_element_screenshot(
            page,
            selector="h1",
            filename="quick_element.png",
            screenshot_dir="screenshots/examples"
        )
        print(f"✓ Element screenshot saved: {element_path}")
        
        # Quick comparison
        print("\nQuick image comparison...")
        are_similar = compare_images(
            baseline_path=screenshot_path,
            current_path=screenshot_path,
            threshold=0.1
        )
        print(f"✓ Images are {'similar' if are_similar else 'different'}")
        
        await browser.close()


async def example_visual_regression_workflow():
    """Example: Complete visual regression testing workflow."""
    print("\n=== Visual Regression Testing Workflow ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        screenshot_utils = ScreenshotUtilities(
            screenshot_dir="screenshots/examples",
            baseline_dir="screenshots/baseline",
            diff_dir="screenshots/diff"
        )
        
        # Test scenario: Homepage visual regression
        test_name = "homepage_visual_regression"
        baseline_name = f"{test_name}_baseline.png"
        
        print(f"Running visual regression test: {test_name}")
        
        # Navigate to page
        await page.goto("https://example.com")
        
        # Check if baseline exists
        baseline_path = screenshot_utils.get_baseline_path(baseline_name)
        
        if baseline_path is None:
            # First run - create baseline
            print("\n✓ First run - Creating baseline...")
            metadata = await screenshot_utils.capture_full_page(
                page,
                test_name=test_name
            )
            baseline_path = screenshot_utils.save_as_baseline(
                screenshot_path=metadata.path,
                baseline_name=baseline_name
            )
            print(f"  Baseline created: {baseline_path}")
            print("\n✓ Test passed - Baseline established")
        else:
            # Subsequent run - compare with baseline
            print("\n✓ Baseline found - Running comparison...")
            
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
            
            print(f"\n  Comparison results:")
            print(f"    Status: {diff.result.value}")
            print(f"    Difference: {diff.difference_percentage:.2f}%")
            
            if diff.result == ComparisonResult.IDENTICAL:
                print("\n✓ Test passed - No visual changes detected")
            elif diff.result == ComparisonResult.SIMILAR:
                print(f"\n⚠ Test passed with warnings - Minor changes within threshold")
            else:
                print(f"\n✗ Test failed - Visual changes exceed threshold")
                print(f"  Review diff image: {diff.diff_image_path}")
        
        await browser.close()


async def example_multiple_formats():
    """Example: Capturing screenshots in different formats."""
    print("\n=== Multiple Screenshot Formats ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        screenshot_utils = ScreenshotUtilities(
            screenshot_dir="screenshots/examples"
        )
        
        await page.goto("https://example.com")
        
        # PNG format (lossless, larger file)
        print("Capturing PNG screenshot...")
        png_metadata = await screenshot_utils.capture_full_page(
            page,
            filename="format_example.png",
            format=ScreenshotFormat.PNG
        )
        print(f"✓ PNG: {png_metadata.size_bytes / 1024:.2f} KB")
        
        # JPEG format (lossy, smaller file)
        print("\nCapturing JPEG screenshot...")
        jpeg_metadata = await screenshot_utils.capture_full_page(
            page,
            filename="format_example.jpeg",
            format=ScreenshotFormat.JPEG,
            quality=85
        )
        print(f"✓ JPEG: {jpeg_metadata.size_bytes / 1024:.2f} KB")
        
        # WebP format (modern, efficient)
        print("\nCapturing WebP screenshot...")
        webp_metadata = await screenshot_utils.capture_full_page(
            page,
            filename="format_example.webp",
            format=ScreenshotFormat.WEBP,
            quality=85
        )
        print(f"✓ WebP: {webp_metadata.size_bytes / 1024:.2f} KB")
        
        print("\nFormat comparison:")
        print(f"  PNG:  {png_metadata.size_bytes / 1024:.2f} KB (baseline)")
        print(f"  JPEG: {jpeg_metadata.size_bytes / 1024:.2f} KB ({jpeg_metadata.size_bytes / png_metadata.size_bytes * 100:.1f}%)")
        print(f"  WebP: {webp_metadata.size_bytes / 1024:.2f} KB ({webp_metadata.size_bytes / png_metadata.size_bytes * 100:.1f}%)")
        
        await browser.close()


async def main():
    """Run all examples."""
    print("=" * 60)
    print("RAPTOR Screenshot Utilities Examples")
    print("=" * 60)
    
    try:
        await example_basic_screenshots()
        await example_visual_comparison()
        await example_image_manipulation()
        await example_convenience_functions()
        await example_visual_regression_workflow()
        await example_multiple_formats()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
