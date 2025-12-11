# RAPTOR AI Visual Automation Module

## Overview

The AI Visual Automation module provides AskUI-inspired capabilities for resilient UI testing using computer vision and OCR. This module enables test automation engineers to locate and interact with UI elements using:

- **Natural language descriptions** ("blue submit button")
- **Visual characteristics** (color, shape, size)
- **Text content** (OCR-based text detection)
- **Template images** (visual similarity matching)
- **Hybrid approaches** (combining Playwright selectors with AI visual detection)

## Key Features

### 🎯 AI-Powered Element Detection
- Locate elements by natural language descriptions
- Template matching for visual similarity
- Color-based element detection
- Shape detection (buttons, inputs, checkboxes)
- Multi-scale detection support

### 📝 OCR Text Detection
- Extract text from screenshots using Tesseract OCR
- Fuzzy text matching
- Multi-language support
- Confidence scoring
- Text bounding box detection

### 🔍 Visual Element Classification
- Automatic element type detection (button, input, checkbox, etc.)
- Visual feature extraction
- Rule-based classification heuristics
- Interactive element detection

### 🔄 Hybrid Automation
- Seamlessly combine Playwright and AI visual detection
- Automatic fallback strategies
- Configurable selector priorities
- Performance optimization

### ✅ Visual Assertions
- Element visibility verification
- Screenshot comparison
- Visual diff generation
- Baseline management
- Layout relationship verification

### ⚡ Performance Optimization
- Screenshot caching with LRU eviction
- Region-of-interest processing
- Parallel detection support
- Lazy loading of ML models

## Module Structure

```
raptor/ai_visual/
├── __init__.py                    # Module exports
├── config.py                      # Configuration management
├── models.py                      # Data models and enums
├── ai_visual_manager.py          # Main orchestrator
├── screenshot_manager.py         # Screenshot capture and caching
├── image_preprocessor.py         # Image preprocessing utilities
├── ocr_engine.py                 # OCR text detection
├── visual_element_detector.py    # Element detection
├── element_classifier.py         # Element classification
├── visual_assertions.py          # Visual assertions
├── hybrid_automation_engine.py   # Hybrid Playwright + AI
└── visual_interface.py           # Fluent API interface
```

## Quick Start

### Installation

```bash
# Install system dependencies
sudo apt-get install tesseract-ocr  # Ubuntu/Debian
brew install tesseract              # macOS

# Install Python dependencies
pip install -r requirements_ai_visual.txt
```

### Basic Usage

```python
from raptor.ai_visual import AIVisualManager, AIVisualConfig, VisualSelector

# Initialize
config = AIVisualConfig(enabled=True, confidence_threshold=0.8)
ai_manager = AIVisualManager(config, playwright_page)
await ai_manager.initialize()

# Find element by description
elements = await ai_manager.visual_detector.find_by_description("submit button")

# Find text using OCR
text_elements = await ai_manager.ocr_engine.find_text("Login")

# Use visual selector
selector = VisualSelector.by_description("username input")
await page.visual_click(selector)
```

## Configuration

### YAML Configuration

```yaml
ai_visual:
  enabled: true
  confidence_threshold: 0.8
  timeout: 30.0
  debug_mode: false
  
  ocr:
    language: 'eng'
    preprocessing: true
    confidence_threshold: 0.6
  
  image:
    scale: 1.0
    quality: 90
    grayscale: false
  
  performance:
    cache_screenshots: true
    max_cache_size: 100
    parallel_processing: true
```

### Python Configuration

```python
from raptor.ai_visual import AIVisualConfig

config = AIVisualConfig(
    enabled=True,
    confidence_threshold=0.85,
    debug_mode=True,
    fallback_to_playwright=True
)
```

## Core Components

### AIVisualManager
Main orchestrator for all AI visual operations. Manages lifecycle of all sub-components.

```python
ai_manager = AIVisualManager(config, page)
await ai_manager.initialize()
# Use ai_manager.visual_detector, ai_manager.ocr_engine, etc.
await ai_manager.shutdown()
```

### VisualElementDetector
Detects UI elements using computer vision techniques.

```python
# By description
elements = await detector.find_by_description("blue button")

# By template
elements = await detector.find_by_template("button_template.png")

# By color
elements = await detector.find_by_color((0, 0, 255))  # Blue

# By shape
elements = await detector.find_by_shape(ShapeType.RECTANGLE)
```

### OCREngine
Extracts and finds text using Tesseract OCR.

```python
# Extract all text
text_elements = await ocr_engine.extract_text(screenshot)

# Find specific text
text_elements = await ocr_engine.find_text("Login", fuzzy_match=True)

# Read text at location
text = await ocr_engine.read_text_at_location(Point(100, 200), screenshot)
```

### ElementClassifier
Classifies UI elements by type.

```python
# Classify element
classification = await classifier.classify_element(element_region)
print(f"Type: {classification.element_type.value}")
print(f"Confidence: {classification.confidence}")

# Detect all interactive elements
elements = await classifier.detect_interactive_elements(screenshot)
```

### VisualAssertions
Performs visual-based assertions.

```python
# Assert element visible
await assertions.assert_element_visible("submit button")

# Assert text visible
await assertions.assert_text_visible("Welcome")

# Compare screenshots
diff = await assertions.compare_screenshots(screenshot1, screenshot2)
```

### HybridAutomationEngine
Combines Playwright and AI visual detection.

```python
engine = HybridAutomationEngine(page, ai_manager)

# Auto strategy
await engine.click("#submit", strategy=SelectionStrategy.AUTO)

# AI first, fallback to Playwright
await engine.click(
    VisualSelector.by_description("submit button"),
    strategy=SelectionStrategy.AI_FIRST
)
```

## Data Models

### VisualElement
Represents a detected UI element with location, confidence, and properties.

### VisualSelector
Flexible selector supporting multiple detection methods.

### TextElement
OCR-detected text with location and confidence.

### ElementClassification
Element type classification with confidence scores.

### BoundingBox, Point, Region
Geometric primitives for element location.

## Performance Considerations

### Caching
- Screenshot caching with LRU eviction
- OCR result caching
- Template matching cache
- Configurable cache sizes

### Optimization
- Image downscaling for faster processing
- Region-of-interest extraction
- Parallel processing support
- Lazy loading of ML models

### Best Practices
1. Use caching for repeated operations
2. Limit detection region when possible
3. Adjust confidence thresholds appropriately
4. Enable parallel processing for multiple detections
5. Use grayscale when color is not needed

## Error Handling

### Custom Exceptions
- `VisualElementNotFoundError`: Element not detected
- `VisualConfidenceTooLowError`: Confidence below threshold
- `OCRExtractionError`: OCR failed
- `VisualAssertionError`: Visual assertion failed

### Debug Mode
Enable debug mode to save annotated screenshots showing detection attempts:

```python
config = AIVisualConfig(debug_mode=True)
```

## Testing

### Unit Tests
```bash
pytest tests/test_ai_visual/test_config.py
pytest tests/test_ai_visual/test_screenshot_manager.py
pytest tests/test_ai_visual/test_ocr_engine.py
```

### Integration Tests
```bash
pytest tests/test_ai_visual_integration.py
```

## Dependencies

### Required
- opencv-python-headless >= 4.8.0
- pytesseract >= 0.3.10
- numpy >= 1.24.0
- Pillow >= 10.0.0
- scikit-image >= 0.21.0

### Optional
- tensorflow >= 2.13.0 (for advanced ML models)
- boto3 (for AWS Rekognition)
- google-cloud-vision (for Google Cloud Vision)

## Limitations

1. **Accuracy**: AI detection may not achieve 100% accuracy
2. **Performance**: Image processing can be CPU-intensive
3. **Setup**: Requires Tesseract OCR system installation
4. **Learning Curve**: Understanding when to use AI vs traditional selectors

## Future Enhancements

- Custom ML models for element detection
- GPU acceleration support
- Video-based element tracking
- Advanced semantic understanding
- Multi-language OCR improvements

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md) for guidelines.

## License

See [LICENSE](../../LICENSE) for details.

## Support

- Documentation: [Full Documentation](../../docs/)
- Examples: [Example Tests](../../examples/ai_visual_examples/)
- Issues: [GitHub Issues](https://github.com/your-org/raptor/issues)

## References

- AskUI: https://github.com/askui/askui
- OpenCV: https://docs.opencv.org/
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- RAPTOR Framework: [Main README](../../README.md)
