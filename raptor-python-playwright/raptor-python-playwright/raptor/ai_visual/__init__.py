"""
RAPTOR AI Visual Automation Module

This module provides AI-powered visual automation capabilities inspired by AskUI,
using Python-native computer vision libraries (OpenCV, Tesseract OCR) for resilient
UI testing that works even when traditional selectors fail.

Key Features:
- AI-powered element detection using computer vision
- OCR-based text detection and interaction
- Visual element classification (button, input, checkbox, etc.)
- Hybrid automation combining Playwright and AI visual detection
- Visual assertions and screenshot comparison
- Template matching for visual element detection
- Performance optimization with caching and parallel processing

Example Usage:
    from raptor.ai_visual import AIVisualManager, VisualSelector
    
    # Initialize AI visual manager
    ai_manager = AIVisualManager(config, playwright_page)
    await ai_manager.initialize()
    
    # Find element by description
    elements = await ai_manager.visual_detector.find_by_description("blue submit button")
    
    # Find text using OCR
    text_elements = await ai_manager.ocr_engine.find_text("Login")
    
    # Use visual selector
    selector = VisualSelector.by_description("username input field")
    await page.visual_click(selector)
"""

from raptor.ai_visual.ai_visual_manager import AIVisualManager
from raptor.ai_visual.config import AIVisualConfig
from raptor.ai_visual.models import (
    VisualElement,
    VisualSelector,
    TextElement,
    ElementClassification,
    BoundingBox,
    Point,
    Region,
    ElementType,
    DetectionMethod,
    SelectionStrategy,
    ActionResult,
    AssertionResult,
    VisualDiffResult
)
from raptor.ai_visual.visual_element_detector import VisualElementDetector
from raptor.ai_visual.ocr_engine import OCREngine
from raptor.ai_visual.element_classifier import ElementClassifier
from raptor.ai_visual.visual_assertions import VisualAssertions
from raptor.ai_visual.hybrid_automation_engine import HybridAutomationEngine
from raptor.ai_visual.screenshot_manager import ScreenshotManager
from raptor.ai_visual.image_preprocessor import ImagePreprocessor

__all__ = [
    'AIVisualManager',
    'AIVisualConfig',
    'VisualElement',
    'VisualSelector',
    'TextElement',
    'ElementClassification',
    'BoundingBox',
    'Point',
    'Region',
    'ElementType',
    'DetectionMethod',
    'SelectionStrategy',
    'ActionResult',
    'AssertionResult',
    'VisualDiffResult',
    'VisualElementDetector',
    'OCREngine',
    'ElementClassifier',
    'VisualAssertions',
    'HybridAutomationEngine',
    'ScreenshotManager',
    'ImagePreprocessor',
]

__version__ = '1.0.0'
