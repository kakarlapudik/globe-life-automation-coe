# AI Visual Automation Quick Start Guide

## Overview

RAPTOR's AI Visual Automation provides AskUI-inspired capabilities for resilient UI testing using computer vision and OCR. This allows you to locate and interact with elements using natural language descriptions, visual characteristics, and text content - even when traditional selectors fail.

## Installation

### 1. Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr libtesseract-dev
```

#### macOS
```bash
brew install tesseract
```

#### Windows
Download and install Tesseract from:
https://github.com/UB-Mannheim/tesseract/wiki

### 2. Install Python Dependencies

```bash
cd raptor-python-playwright
pip install -r requirements_ai_visual.txt
```

### 3. Verify Installation

```python
import cv2
import pytesseract
import numpy as np

print(f"OpenCV version: {cv2.__version__}")
print(f"Tesseract version: {pytesseract.get_tesseract_version()}")
print("AI Visual Automation dependencies installed successfully!")
```

## Configuration

### Basic Configuration

Create or update your `config/settings.yaml`:

```yaml
ai_visual:
  enabled: true
  confidence_threshold: 0.8
  timeout: 30.0
  screenshot_on_action: true
  debug_mode: false
  fallback_to_playwright: true
  
  ocr:
    language: 'eng'
    preprocessing: true
    tesseract_config: '--psm 6'
    confidence_threshold: 0.6
  
  image:
    scale: 1.0
    quality: 90
    grayscale: false
    max_dimension: 1920
  
  performance:
    cache_screenshots: true
    max_cache_size: 100
    parallel_processing: true
    max_concurrent: 3
    retry_count: 2
    detection_timeout: 30.0
```

### Python Configuration

```python
from raptor.ai_visual import AIVisualConfig

# Create configuration
config = AIVisualConfig(
    enabled=True,
    confidence_threshold=0.85,
    debug_mode=True,
    fallback_to_playwright=True
)

# Validate configuration
config.validate()

# Ensure directories exist
config.ensure_directories()
```

## Basic Usage

### 1. Initialize AI Visual Manager

```python
from raptor.ai_visual import AIVisualManager, AIVisualConfig
from raptor.core import BrowserManager

# Create configuration
config = AIVisualConfig()

# Create browser and page
browser_manager = BrowserManager(config)
page = await browser_manager.create_page()

# Initialize AI visual manager
ai_manager = AIVisualManager(config, page)
await ai_manager.initialize()
```

### 2. Find Elements by Description

```python
# Find element by natural language description
elements = await ai_manager.visual_detector.find_by_description(
    "blue submit button",
    confidence_threshold=0.8
)

if elements:
    element = elements[0]
    print(f"Found element with {element.confidence:.2f} confidence")
    print(f"Location: {element.bounding_box.to_tuple()}")
```

### 3. Find Text Using OCR

```python
# Find text on page
text_elements = await ai_manager.ocr_engine.find_text(
    "Login",
    fuzzy_match=True,
    case_sensitive=False
)

for text_elem in text_elements:
    print(f"Found '{text_elem.text}' with {text_elem.confidence:.2f} confidence")
    print(f"Location: {text_elem.bounding_box.to_tuple()}")
```

### 4. Use Visual Selectors

```python
from raptor.ai_visual import VisualSelector

# Create selector by description
selector = VisualSelector.by_description("username input field")

# Create selector by text
selector = VisualSelector.by_text("Sign In")

# Create selector by template image
selector = VisualSelector.by_template("button_template.png")

# Use selector with hybrid engine
result = await hybrid_engine.click(selector)
print(f"Click {'succeeded' if result.success else 'failed'}")
```

### 5. Visual Assertions

```python
# Assert element is visible
result = await ai_manager.visual_assertions.assert_element_visible(
    "submit button",
    timeout=10.0
)

# Assert text is present
result = await ai_manager.visual_assertions.assert_text_visible(
    "Welcome",
    region=None
)

# Compare screenshots
diff_result = await ai_manager.visual_assertions.compare_screenshots(
    screenshot1,
    screenshot2
)
print(f"Similarity: {diff_result.similarity_score:.2f}")
```

## Advanced Usage

### Template Matching

```python
# Find elements by template image
elements = await ai_manager.visual_detector.find_by_template(
    template_image="templates/login_button.png",
    similarity_threshold=0.9
)
```

### Element Classification

```python
# Classify element type
classification = await ai_manager.element_classifier.classify_element(
    element_region=element_screenshot,
    context_screenshot=full_screenshot
)

print(f"Element type: {classification.element_type.value}")
print(f"Confidence: {classification.confidence:.2f}")
print(f"Recommended interaction: {classification.get_interaction_method().value}")
```

### Hybrid Automation

```python
from raptor.ai_visual import HybridAutomationEngine, SelectionStrategy

# Create hybrid engine
hybrid_engine = HybridAutomationEngine(page, ai_manager)

# Auto strategy (tries best method)
await hybrid_engine.click("#submit-btn", strategy=SelectionStrategy.AUTO)

# AI first, fallback to Playwright
await hybrid_engine.click(
    VisualSelector.by_description("submit button"),
    strategy=SelectionStrategy.AI_FIRST
)

# Playwright first, fallback to AI
await hybrid_engine.type(
    "#username",
    "testuser",
    strategy=SelectionStrategy.PLAYWRIGHT_FIRST
)
```

## Integration with RAPTOR Page Objects

```python
from raptor.pages import BasePage

class LoginPage(BasePage):
    async def login_with_ai(self, username: str, password: str):
        """Login using AI visual automation."""
        # Find username field by description
        await self.page.visual_type("username input", username)
        
        # Find password field by text label
        await self.page.visual_type("password field", password)
        
        # Click submit button by description
        await self.page.visual_click("blue submit button")
        
        # Assert success message visible
        await self.page.visual_assert_visible("Welcome message")
```

## Debug Mode

Enable debug mode to save annotated screenshots:

```python
config = AIVisualConfig(debug_mode=True)

# Debug screenshots will be saved to screenshots/ai_visual/
# with bounding boxes and confidence scores annotated
```

## Performance Tips

1. **Use Caching**: Enable screenshot caching for better performance
2. **Limit Region**: Specify region of interest to reduce processing time
3. **Adjust Confidence**: Lower confidence threshold if elements are hard to detect
4. **Use Grayscale**: Enable grayscale processing when color is not needed
5. **Parallel Processing**: Enable parallel processing for multiple detections

## Troubleshooting

### Tesseract Not Found
```bash
# Verify Tesseract installation
tesseract --version

# Set Tesseract path (if needed)
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

### Low Detection Accuracy
- Increase image quality in configuration
- Enable image preprocessing
- Adjust confidence threshold
- Use debug mode to see what's being detected

### Slow Performance
- Enable screenshot caching
- Reduce image scale
- Limit detection region
- Enable parallel processing

## Examples

See `examples/ai_visual_examples/` for complete working examples:
- `basic_detection.py` - Basic element detection
- `ocr_text_finding.py` - OCR text detection
- `template_matching.py` - Template matching
- `hybrid_automation.py` - Hybrid Playwright + AI
- `visual_assertions.py` - Visual assertions

## Next Steps

1. Read the full [AI Visual Automation Guide](AI_VISUAL_AUTOMATION_GUIDE.md)
2. Review [API Reference](API_REFERENCE_AI_VISUAL.md)
3. Check out [Best Practices](AI_VISUAL_BEST_PRACTICES.md)
4. Explore [Migration Guide](AI_VISUAL_MIGRATION_GUIDE.md)

## Support

For issues, questions, or contributions:
- GitHub Issues: [RAPTOR Issues](https://github.com/your-org/raptor/issues)
- Documentation: [Full Documentation](../docs/)
- Examples: [Example Tests](../examples/ai_visual_examples/)
