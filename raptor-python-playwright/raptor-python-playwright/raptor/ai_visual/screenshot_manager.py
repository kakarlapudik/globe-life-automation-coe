"""
Screenshot Manager for AI Visual Automation

Handles efficient screenshot capture, caching, and management.
"""

import hashlib
import time
from typing import Optional, Dict, Tuple
from pathlib import Path
import numpy as np
from PIL import Image
import io
from collections import OrderedDict

from raptor.ai_visual.config import AIVisualConfig
from raptor.ai_visual.models import Region


class ScreenshotCache:
    """LRU cache for screenshots."""
    
    def __init__(self, max_size: int = 100):
        """
        Initialize screenshot cache.
        
        Args:
            max_size: Maximum number of screenshots to cache
        """
        self.max_size = max_size
        self.cache: OrderedDict[str, Tuple[np.ndarray, float]] = OrderedDict()
    
    def get(self, key: str) -> Optional[np.ndarray]:
        """
        Get screenshot from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached screenshot or None if not found
        """
        if key in self.cache:
            # Move to end (most recently used)
            screenshot, timestamp = self.cache.pop(key)
            self.cache[key] = (screenshot, timestamp)
            return screenshot
        return None
    
    def put(self, key: str, screenshot: np.ndarray) -> None:
        """
        Add screenshot to cache.
        
        Args:
            key: Cache key
            screenshot: Screenshot to cache
        """
        if key in self.cache:
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            # Remove oldest item
            self.cache.popitem(last=False)
        
        self.cache[key] = (screenshot, time.time())
    
    def clear(self) -> None:
        """Clear all cached screenshots."""
        self.cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)


class ScreenshotManager:
    """
    Manages screenshot capture, caching, and storage.
    
    This class provides efficient screenshot management with:
    - Automatic caching to avoid redundant captures
    - Region-of-interest extraction
    - Screenshot preprocessing
    - Persistent storage with metadata
    
    Example:
        manager = ScreenshotManager(config)
        screenshot = await manager.capture_screenshot(page)
        region = manager.extract_region(screenshot, Region(100, 100, 200, 200))
    """
    
    def __init__(self, config: AIVisualConfig):
        """
        Initialize screenshot manager.
        
        Args:
            config: AI visual configuration
        """
        self.config = config
        self.cache = ScreenshotCache(config.performance.max_cache_size) if config.performance.cache_screenshots else None
        self.screenshot_dir = Path(config.screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self._last_screenshot: Optional[np.ndarray] = None
        self._last_screenshot_hash: Optional[str] = None
    
    async def capture_screenshot(
        self,
        page,
        full_page: bool = False,
        region: Optional[Region] = None,
        use_cache: bool = True
    ) -> np.ndarray:
        """
        Capture screenshot from page.
        
        Args:
            page: Playwright page object
            full_page: Capture full scrollable page
            region: Specific region to capture
            use_cache: Use cached screenshot if available
            
        Returns:
            Screenshot as numpy array (BGR format)
        """
        # Generate cache key based on page URL and region
        cache_key = self._generate_cache_key(page.url, region)
        
        # Check cache if enabled
        if use_cache and self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        
        # Capture screenshot
        screenshot_bytes = await page.screenshot(
            full_page=full_page,
            type='png'
        )
        
        # Convert to numpy array
        image = Image.open(io.BytesIO(screenshot_bytes))
        screenshot = np.array(image)
        
        # Convert RGB to BGR for OpenCV
        if len(screenshot.shape) == 3 and screenshot.shape[2] == 3:
            screenshot = screenshot[:, :, ::-1]
        
        # Extract region if specified
        if region:
            screenshot = self.extract_region(screenshot, region)
        
        # Apply image configuration
        screenshot = self._apply_image_config(screenshot)
        
        # Cache screenshot
        if use_cache and self.cache:
            self.cache.put(cache_key, screenshot)
        
        # Store as last screenshot
        self._last_screenshot = screenshot
        self._last_screenshot_hash = self._compute_hash(screenshot)
        
        return screenshot
    
    def extract_region(self, screenshot: np.ndarray, region: Region) -> np.ndarray:
        """
        Extract region of interest from screenshot.
        
        Args:
            screenshot: Full screenshot
            region: Region to extract
            
        Returns:
            Extracted region as numpy array
        """
        x, y, w, h = region.to_tuple()
        
        # Ensure region is within bounds
        height, width = screenshot.shape[:2]
        x = max(0, min(x, width))
        y = max(0, min(y, height))
        w = min(w, width - x)
        h = min(h, height - y)
        
        return screenshot[y:y+h, x:x+w].copy()
    
    def save_screenshot(
        self,
        screenshot: np.ndarray,
        filename: str,
        metadata: Optional[Dict] = None
    ) -> Path:
        """
        Save screenshot to disk.
        
        Args:
            screenshot: Screenshot to save
            filename: Filename (without extension)
            metadata: Optional metadata to save alongside
            
        Returns:
            Path to saved screenshot
        """
        # Convert BGR to RGB for saving
        if len(screenshot.shape) == 3 and screenshot.shape[2] == 3:
            screenshot_rgb = screenshot[:, :, ::-1]
        else:
            screenshot_rgb = screenshot
        
        # Save image
        filepath = self.screenshot_dir / f"{filename}.png"
        image = Image.fromarray(screenshot_rgb)
        image.save(filepath, quality=self.config.image.quality)
        
        # Save metadata if provided
        if metadata:
            import json
            metadata_path = self.screenshot_dir / f"{filename}_metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
        
        return filepath
    
    def get_last_screenshot(self) -> Optional[np.ndarray]:
        """
        Get the last captured screenshot.
        
        Returns:
            Last screenshot or None if no screenshot captured
        """
        return self._last_screenshot
    
    def clear_cache(self) -> None:
        """Clear screenshot cache."""
        if self.cache:
            self.cache.clear()
        self._last_screenshot = None
        self._last_screenshot_hash = None
    
    def _generate_cache_key(self, url: str, region: Optional[Region]) -> str:
        """Generate cache key from URL and region."""
        key_parts = [url]
        if region:
            key_parts.append(f"{region.x},{region.y},{region.width},{region.height}")
        return hashlib.md5('|'.join(key_parts).encode()).hexdigest()
    
    def _compute_hash(self, screenshot: np.ndarray) -> str:
        """Compute hash of screenshot for change detection."""
        return hashlib.md5(screenshot.tobytes()).hexdigest()
    
    def _apply_image_config(self, screenshot: np.ndarray) -> np.ndarray:
        """Apply image configuration settings."""
        # Apply scaling
        if self.config.image.scale != 1.0:
            import cv2
            height, width = screenshot.shape[:2]
            new_width = int(width * self.config.image.scale)
            new_height = int(height * self.config.image.scale)
            screenshot = cv2.resize(screenshot, (new_width, new_height))
        
        # Apply grayscale conversion
        if self.config.image.grayscale and len(screenshot.shape) == 3:
            import cv2
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Limit maximum dimension
        if self.config.image.max_dimension > 0:
            import cv2
            height, width = screenshot.shape[:2]
            max_dim = max(height, width)
            if max_dim > self.config.image.max_dimension:
                scale = self.config.image.max_dimension / max_dim
                new_width = int(width * scale)
                new_height = int(height * scale)
                screenshot = cv2.resize(screenshot, (new_width, new_height))
        
        return screenshot
    
    def has_page_changed(self, current_screenshot: np.ndarray) -> bool:
        """
        Check if page has changed since last screenshot.
        
        Args:
            current_screenshot: Current screenshot to compare
            
        Returns:
            True if page has changed
        """
        if self._last_screenshot_hash is None:
            return True
        
        current_hash = self._compute_hash(current_screenshot)
        return current_hash != self._last_screenshot_hash
