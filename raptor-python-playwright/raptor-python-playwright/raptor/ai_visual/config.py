"""
AI Visual Automation Configuration

This module provides configuration management for AI visual automation features.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import yaml
from pathlib import Path


@dataclass
class OCRConfig:
    """Configuration for OCR engine."""
    language: str = 'eng'
    preprocessing: bool = True
    tesseract_config: str = '--psm 6'
    confidence_threshold: float = 0.6
    
    
@dataclass
class ImageConfig:
    """Configuration for image processing."""
    scale: float = 1.0
    quality: int = 90
    grayscale: bool = False
    max_dimension: int = 1920
    

@dataclass
class PerformanceConfig:
    """Configuration for performance optimization."""
    cache_screenshots: bool = True
    max_cache_size: int = 100
    parallel_processing: bool = True
    max_concurrent: int = 3
    retry_count: int = 2
    detection_timeout: float = 30.0
    

@dataclass
class CloudAIConfig:
    """Configuration for optional cloud AI services."""
    enabled: bool = False
    provider: Optional[str] = None  # 'aws', 'google', 'azure'
    api_key: Optional[str] = None
    region: Optional[str] = None
    

@dataclass
class AIVisualConfig:
    """
    Main configuration for AI visual automation.
    
    This configuration controls all aspects of AI-powered visual automation
    including OCR, image processing, performance optimization, and optional
    cloud AI service integration.
    
    Attributes:
        enabled: Enable/disable AI visual automation
        confidence_threshold: Minimum confidence score for element detection (0.0-1.0)
        timeout: Maximum time to wait for element detection (seconds)
        screenshot_on_action: Capture screenshots for all actions
        debug_mode: Enable debug mode with annotated screenshots
        fallback_to_playwright: Fall back to Playwright selectors on AI failure
        
    Example:
        config = AIVisualConfig(
            enabled=True,
            confidence_threshold=0.85,
            debug_mode=True
        )
    """
    enabled: bool = True
    confidence_threshold: float = 0.8
    timeout: float = 30.0
    screenshot_on_action: bool = True
    debug_mode: bool = False
    fallback_to_playwright: bool = True
    
    # Sub-configurations
    ocr: OCRConfig = field(default_factory=OCRConfig)
    image: ImageConfig = field(default_factory=ImageConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    cloud: CloudAIConfig = field(default_factory=CloudAIConfig)
    
    # Additional settings
    screenshot_dir: str = "screenshots/ai_visual"
    baseline_dir: str = "baselines/ai_visual"
    cache_dir: str = ".cache/ai_visual"
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'AIVisualConfig':
        """
        Load configuration from YAML file.
        
        Args:
            yaml_path: Path to YAML configuration file
            
        Returns:
            AIVisualConfig instance
            
        Example:
            config = AIVisualConfig.from_yaml('config/ai_visual.yaml')
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
            
        ai_visual_data = data.get('ai_visual', {})
        
        return cls(
            enabled=ai_visual_data.get('enabled', True),
            confidence_threshold=ai_visual_data.get('confidence_threshold', 0.8),
            timeout=ai_visual_data.get('timeout', 30.0),
            screenshot_on_action=ai_visual_data.get('screenshot_on_action', True),
            debug_mode=ai_visual_data.get('debug_mode', False),
            fallback_to_playwright=ai_visual_data.get('fallback_to_playwright', True),
            ocr=OCRConfig(**ai_visual_data.get('ocr', {})),
            image=ImageConfig(**ai_visual_data.get('image', {})),
            performance=PerformanceConfig(**ai_visual_data.get('performance', {})),
            cloud=CloudAIConfig(**ai_visual_data.get('cloud', {})),
            screenshot_dir=ai_visual_data.get('screenshot_dir', 'screenshots/ai_visual'),
            baseline_dir=ai_visual_data.get('baseline_dir', 'baselines/ai_visual'),
            cache_dir=ai_visual_data.get('cache_dir', '.cache/ai_visual')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            'enabled': self.enabled,
            'confidence_threshold': self.confidence_threshold,
            'timeout': self.timeout,
            'screenshot_on_action': self.screenshot_on_action,
            'debug_mode': self.debug_mode,
            'fallback_to_playwright': self.fallback_to_playwright,
            'ocr': {
                'language': self.ocr.language,
                'preprocessing': self.ocr.preprocessing,
                'tesseract_config': self.ocr.tesseract_config,
                'confidence_threshold': self.ocr.confidence_threshold
            },
            'image': {
                'scale': self.image.scale,
                'quality': self.image.quality,
                'grayscale': self.image.grayscale,
                'max_dimension': self.image.max_dimension
            },
            'performance': {
                'cache_screenshots': self.performance.cache_screenshots,
                'max_cache_size': self.performance.max_cache_size,
                'parallel_processing': self.performance.parallel_processing,
                'max_concurrent': self.performance.max_concurrent,
                'retry_count': self.performance.retry_count,
                'detection_timeout': self.performance.detection_timeout
            },
            'cloud': {
                'enabled': self.cloud.enabled,
                'provider': self.cloud.provider,
                'region': self.cloud.region
            },
            'screenshot_dir': self.screenshot_dir,
            'baseline_dir': self.baseline_dir,
            'cache_dir': self.cache_dir
        }
    
    def validate(self) -> None:
        """
        Validate configuration values.
        
        Raises:
            ValueError: If configuration values are invalid
        """
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
        
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        
        if not 0.0 <= self.ocr.confidence_threshold <= 1.0:
            raise ValueError("OCR confidence_threshold must be between 0.0 and 1.0")
        
        if self.image.scale <= 0:
            raise ValueError("image scale must be positive")
        
        if not 0 < self.image.quality <= 100:
            raise ValueError("image quality must be between 1 and 100")
        
        if self.performance.max_cache_size < 0:
            raise ValueError("max_cache_size must be non-negative")
        
        if self.performance.max_concurrent < 1:
            raise ValueError("max_concurrent must be at least 1")
        
        if self.cloud.enabled and not self.cloud.provider:
            raise ValueError("cloud provider must be specified when cloud AI is enabled")
        
        if self.cloud.provider and self.cloud.provider not in ['aws', 'google', 'azure']:
            raise ValueError("cloud provider must be 'aws', 'google', or 'azure'")
    
    def ensure_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        Path(self.screenshot_dir).mkdir(parents=True, exist_ok=True)
        Path(self.baseline_dir).mkdir(parents=True, exist_ok=True)
        Path(self.cache_dir).mkdir(parents=True, exist_ok=True)
