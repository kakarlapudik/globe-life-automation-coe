"""
Data models for AI Visual Automation

This module defines all data structures used in AI visual automation.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple, Union
from enum import Enum
from datetime import datetime
import numpy as np


class ElementType(Enum):
    """UI element types that can be classified."""
    BUTTON = "button"
    INPUT = "input"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    DROPDOWN = "dropdown"
    LINK = "link"
    TEXT = "text"
    IMAGE = "image"
    ICON = "icon"
    MENU = "menu"
    DIALOG = "dialog"
    UNKNOWN = "unknown"


class DetectionMethod(Enum):
    """Methods used for element detection."""
    TEMPLATE_MATCHING = "template_matching"
    OCR = "ocr"
    COLOR_DETECTION = "color_detection"
    SHAPE_DETECTION = "shape_detection"
    FEATURE_MATCHING = "feature_matching"
    DESCRIPTION = "description"
    HYBRID = "hybrid"
    PLAYWRIGHT = "playwright"


class SelectionStrategy(Enum):
    """Strategy for element selection."""
    AUTO = "auto"  # Automatically choose best method
    PLAYWRIGHT_ONLY = "playwright_only"  # Use only Playwright selectors
    AI_ONLY = "ai_only"  # Use only AI visual detection
    PLAYWRIGHT_FIRST = "playwright_first"  # Try Playwright, fallback to AI
    AI_FIRST = "ai_first"  # Try AI, fallback to Playwright


class ShapeType(Enum):
    """Geometric shapes for detection."""
    RECTANGLE = "rectangle"
    CIRCLE = "circle"
    ROUNDED_RECTANGLE = "rounded_rectangle"
    TRIANGLE = "triangle"
    POLYGON = "polygon"


class InteractionMethod(Enum):
    """Recommended interaction methods for elements."""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    SELECT = "select"
    HOVER = "hover"
    DRAG = "drag"


@dataclass
class Point:
    """Represents a 2D point."""
    x: int
    y: int
    
    def distance_to(self, other: 'Point') -> float:
        """Calculate Euclidean distance to another point."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5
    
    def to_tuple(self) -> Tuple[int, int]:
        """Convert to tuple."""
        return (self.x, self.y)


@dataclass
class Region:
    """Represents a rectangular region."""
    x: int
    y: int
    width: int
    height: int
    
    def contains(self, point: Point) -> bool:
        """Check if point is inside region."""
        return (self.x <= point.x <= self.x + self.width and
                self.y <= point.y <= self.y + self.height)
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Convert to tuple (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)


@dataclass
class BoundingBox:
    """
    Represents element bounding box.
    
    Attributes:
        x: X coordinate of top-left corner
        y: Y coordinate of top-left corner
        width: Width of bounding box
        height: Height of bounding box
    """
    x: int
    y: int
    width: int
    height: int
    
    def center(self) -> Point:
        """Get center point of bounding box."""
        return Point(
            x=self.x + self.width // 2,
            y=self.y + self.height // 2
        )
    
    def contains(self, point: Point) -> bool:
        """Check if point is inside bounding box."""
        return (self.x <= point.x <= self.x + self.width and
                self.y <= point.y <= self.y + self.height)
    
    def overlaps(self, other: 'BoundingBox') -> bool:
        """Check if this box overlaps with another."""
        return not (self.x + self.width < other.x or
                   other.x + other.width < self.x or
                   self.y + self.height < other.y or
                   other.y + other.height < self.y)
    
    def to_region(self) -> Region:
        """Convert to Region."""
        return Region(self.x, self.y, self.width, self.height)
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Convert to tuple (x, y, width, height)."""
        return (self.x, self.y, self.width, self.height)
    
    def area(self) -> int:
        """Calculate area of bounding box."""
        return self.width * self.height


@dataclass
class VisualElement:
    """
    Represents a visually detected UI element.
    
    Attributes:
        id: Unique identifier for element
        description: Human-readable description
        confidence: Detection confidence score (0.0-1.0)
        bounding_box: Element location and size
        element_type: Classified element type
        screenshot_region: Image data of element region
        detection_method: Method used to detect element
        properties: Additional element properties
        timestamp: When element was detected
    """
    id: str
    description: str
    confidence: float
    bounding_box: BoundingBox
    element_type: Optional[ElementType] = None
    screenshot_region: Optional[np.ndarray] = None
    detection_method: DetectionMethod = DetectionMethod.DESCRIPTION
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_playwright_locator(self) -> Optional[str]:
        """
        Convert to Playwright locator if possible.
        
        Returns:
            Playwright locator string or None if not convertible
        """
        # This would require additional logic to map visual elements
        # to Playwright selectors based on properties
        return None
    
    def get_center_point(self) -> Point:
        """Get center point of element."""
        return self.bounding_box.center()
    
    def get_click_point(self) -> Point:
        """
        Get optimal click point for element.
        
        For most elements, this is the center. For specific element types,
        this might be adjusted (e.g., checkbox click point).
        """
        return self.get_center_point()


@dataclass
class TextElement:
    """
    Represents OCR-detected text.
    
    Attributes:
        text: Extracted text content
        confidence: OCR confidence score (0.0-1.0)
        bounding_box: Text location and size
        language: Detected language
        font_size: Estimated font size
        color: Estimated text color (RGB)
    """
    text: str
    confidence: float
    bounding_box: BoundingBox
    language: str = 'eng'
    font_size: Optional[int] = None
    color: Optional[Tuple[int, int, int]] = None
    
    def contains(self, search_text: str, fuzzy: bool = False, case_sensitive: bool = False) -> bool:
        """
        Check if text contains search string.
        
        Args:
            search_text: Text to search for
            fuzzy: Allow fuzzy matching
            case_sensitive: Perform case-sensitive search
            
        Returns:
            True if text contains search string
        """
        text = self.text if case_sensitive else self.text.lower()
        search = search_text if case_sensitive else search_text.lower()
        
        if fuzzy:
            # Simple fuzzy matching - could be enhanced with Levenshtein distance
            return any(search in word for word in text.split())
        else:
            return search in text


@dataclass
class ElementClassification:
    """
    Result of element type classification.
    
    Attributes:
        element_type: Primary classified type
        confidence: Classification confidence (0.0-1.0)
        alternative_types: Other possible types with confidence scores
        visual_features: Extracted visual features used for classification
    """
    element_type: ElementType
    confidence: float
    alternative_types: List[Tuple[ElementType, float]] = field(default_factory=list)
    visual_features: Dict[str, Any] = field(default_factory=dict)
    
    def is_interactive(self) -> bool:
        """Check if element is interactive."""
        interactive_types = {
            ElementType.BUTTON,
            ElementType.INPUT,
            ElementType.CHECKBOX,
            ElementType.RADIO,
            ElementType.DROPDOWN,
            ElementType.LINK
        }
        return self.element_type in interactive_types
    
    def get_interaction_method(self) -> InteractionMethod:
        """Get recommended interaction method for element type."""
        interaction_map = {
            ElementType.BUTTON: InteractionMethod.CLICK,
            ElementType.INPUT: InteractionMethod.TYPE,
            ElementType.CHECKBOX: InteractionMethod.CLICK,
            ElementType.RADIO: InteractionMethod.CLICK,
            ElementType.DROPDOWN: InteractionMethod.SELECT,
            ElementType.LINK: InteractionMethod.CLICK,
            ElementType.MENU: InteractionMethod.HOVER
        }
        return interaction_map.get(self.element_type, InteractionMethod.CLICK)


@dataclass
class VisualSelector:
    """
    Represents a visual-based element selector.
    
    This selector can use various methods to locate elements:
    - Natural language description
    - Template image matching
    - Text content (OCR)
    - Color characteristics
    - Shape detection
    
    Example:
        # By description
        selector = VisualSelector.by_description("blue submit button")
        
        # By template
        selector = VisualSelector.by_template("button_template.png")
        
        # By text
        selector = VisualSelector.by_text("Login")
    """
    description: Optional[str] = None
    template_image: Optional[Union[str, bytes, np.ndarray]] = None
    text_content: Optional[str] = None
    color: Optional[Tuple[int, int, int]] = None
    shape: Optional[ShapeType] = None
    region: Optional[Region] = None
    confidence_threshold: float = 0.8
    timeout: float = 30.0
    fallback_selector: Optional[str] = None
    
    @classmethod
    def by_description(cls, description: str, **kwargs) -> 'VisualSelector':
        """Create selector by natural language description."""
        return cls(description=description, **kwargs)
    
    @classmethod
    def by_template(cls, template_image: Union[str, bytes, np.ndarray], **kwargs) -> 'VisualSelector':
        """Create selector by template image."""
        return cls(template_image=template_image, **kwargs)
    
    @classmethod
    def by_text(cls, text: str, **kwargs) -> 'VisualSelector':
        """Create selector by text content."""
        return cls(text_content=text, **kwargs)
    
    @classmethod
    def by_color(cls, color: Tuple[int, int, int], **kwargs) -> 'VisualSelector':
        """Create selector by color."""
        return cls(color=color, **kwargs)


@dataclass
class ActionResult:
    """
    Result of an action performed on an element.
    
    Attributes:
        success: Whether action succeeded
        action_type: Type of action performed
        description: Description of what was done
        confidence: Confidence in action success
        detection_method: Method used to find element
        execution_time: Time taken to execute action
        fallback_used: Whether fallback method was used
        screenshot_before: Screenshot before action
        screenshot_after: Screenshot after action
        error_message: Error message if action failed
    """
    success: bool
    action_type: str
    description: str
    confidence: float = 1.0
    detection_method: DetectionMethod = DetectionMethod.PLAYWRIGHT
    execution_time: float = 0.0
    fallback_used: bool = False
    screenshot_before: Optional[bytes] = None
    screenshot_after: Optional[bytes] = None
    error_message: Optional[str] = None


@dataclass
class AssertionResult:
    """
    Result of a visual assertion.
    
    Attributes:
        passed: Whether assertion passed
        assertion_type: Type of assertion
        expected: Expected value
        actual: Actual value
        confidence: Confidence in result
        screenshot: Screenshot at time of assertion
        error_message: Error message if assertion failed
    """
    passed: bool
    assertion_type: str
    expected: Any
    actual: Any
    confidence: float = 1.0
    screenshot: Optional[bytes] = None
    error_message: Optional[str] = None


@dataclass
class VisualDiffResult:
    """
    Result of visual screenshot comparison.
    
    Attributes:
        similarity_score: Similarity score (0.0-1.0)
        differences_found: Whether differences were detected
        diff_image: Image highlighting differences
        changed_regions: List of regions with changes
        pixel_diff_count: Number of different pixels
        structural_similarity: SSIM score
    """
    similarity_score: float
    differences_found: bool
    diff_image: Optional[np.ndarray] = None
    changed_regions: List[BoundingBox] = field(default_factory=list)
    pixel_diff_count: int = 0
    structural_similarity: float = 1.0


@dataclass
class InteractiveElement:
    """
    Represents an interactive UI element detected in screenshot.
    
    Attributes:
        visual_element: Base visual element information
        classification: Element type classification
        interaction_method: Recommended interaction method
    """
    visual_element: VisualElement
    classification: ElementClassification
    interaction_method: InteractionMethod
