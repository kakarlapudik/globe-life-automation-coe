"""
Configuration Manager for RAPTOR Framework

This module provides centralized configuration management with support for:
- YAML configuration file loading
- Environment-specific configurations (dev, staging, prod)
- Configuration validation
- Secure credential management
"""

import os
import yaml
import copy
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv

from raptor.core.exceptions import ConfigurationException


class ConfigManager:
    """
    Manages configuration settings for the RAPTOR framework.
    
    Supports loading configuration from YAML files with environment-specific
    overrides and validation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the ConfigManager.
        
        Args:
            config_path: Optional path to the configuration file.
                        If not provided, uses default config/settings.yaml
        """
        self._config: Dict[str, Any] = {}
        self._environment: str = "dev"
        self._config_path = config_path
        
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        # Determine config directory
        if config_path:
            self._config_dir = Path(config_path).parent
        else:
            # Default to raptor/config directory
            self._config_dir = Path(__file__).parent.parent / "config"
        
        # Load default configuration
        self._load_default_config()
    
    def _load_default_config(self) -> None:
        """Load the default configuration file."""
        default_config_path = self._config_dir / "settings.yaml"
        
        if not default_config_path.exists():
            raise ConfigurationException(
                f"Default configuration file not found: {default_config_path}"
            )
        
        try:
            with open(default_config_path, 'r') as f:
                self._config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationException(
                f"Error parsing default configuration file: {e}"
            )
        except Exception as e:
            raise ConfigurationException(
                f"Error loading default configuration: {e}"
            )
    
    def load_config(self, environment: str = "dev") -> Dict[str, Any]:
        """
        Load environment-specific configuration.
        
        Args:
            environment: Environment name (dev, staging, prod)
            
        Returns:
            Complete configuration dictionary
            
        Raises:
            ConfigurationException: If configuration cannot be loaded
        """
        self._environment = environment
        
        # Load environment-specific config
        env_config_path = self._config_dir / "environments" / f"{environment}.yaml"
        
        if not env_config_path.exists():
            raise ConfigurationException(
                f"Environment configuration file not found: {env_config_path}"
            )
        
        try:
            with open(env_config_path, 'r') as f:
                env_config = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationException(
                f"Error parsing environment configuration file: {e}"
            )
        except Exception as e:
            raise ConfigurationException(
                f"Error loading environment configuration: {e}"
            )
        
        # Merge environment config with default config
        self._config = self._merge_configs(self._config, env_config)
        
        # Override with environment variables
        self._apply_env_overrides()
        
        # Validate configuration
        self._validate_config()
        
        return self._config
    
    def _merge_configs(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two configuration dictionaries.
        
        Args:
            base: Base configuration dictionary
            override: Override configuration dictionary
            
        Returns:
            Merged configuration dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to configuration."""
        # Browser settings
        if os.getenv("RAPTOR_BROWSER_TYPE"):
            self._config.setdefault("browser", {})["type"] = os.getenv("RAPTOR_BROWSER_TYPE")
        
        if os.getenv("RAPTOR_HEADLESS"):
            self._config.setdefault("browser", {})["headless"] = os.getenv("RAPTOR_HEADLESS").lower() == "true"
        
        # Timeout settings
        if os.getenv("RAPTOR_DEFAULT_TIMEOUT"):
            self._config.setdefault("timeouts", {})["default"] = int(os.getenv("RAPTOR_DEFAULT_TIMEOUT"))
        
        # Database settings
        if os.getenv("RAPTOR_DB_HOST"):
            self._config.setdefault("database", {})["host"] = os.getenv("RAPTOR_DB_HOST")
        
        if os.getenv("RAPTOR_DB_USER"):
            self._config.setdefault("database", {})["user"] = os.getenv("RAPTOR_DB_USER")
        
        if os.getenv("RAPTOR_DB_PASSWORD"):
            self._config.setdefault("database", {})["password"] = os.getenv("RAPTOR_DB_PASSWORD")
    
    def _validate_config(self) -> None:
        """
        Validate the loaded configuration.
        
        Raises:
            ConfigurationException: If configuration is invalid
        """
        # Validate browser settings
        if "browser" in self._config:
            browser_type = self._config["browser"].get("type")
            if browser_type and browser_type not in ["chromium", "firefox", "webkit"]:
                raise ConfigurationException(
                    f"Invalid browser type: {browser_type}. "
                    "Must be one of: chromium, firefox, webkit"
                )
        
        # Validate timeout settings
        if "timeouts" in self._config:
            for timeout_key, timeout_value in self._config["timeouts"].items():
                if not isinstance(timeout_value, (int, float)) or timeout_value < 0:
                    raise ConfigurationException(
                        f"Invalid timeout value for '{timeout_key}': {timeout_value}. "
                        "Must be a positive number"
                    )
        
        # Validate database settings if present
        if "database" in self._config:
            required_db_fields = ["host", "user"]
            for field in required_db_fields:
                if field not in self._config["database"]:
                    raise ConfigurationException(
                        f"Missing required database field: {field}"
                    )
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.
        
        Supports nested keys using dot notation (e.g., "browser.type").
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split(".")
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Supports nested keys using dot notation (e.g., "browser.type").
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split(".")
        config = self._config
        
        # Navigate to the nested location
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_browser_options(self) -> Dict[str, Any]:
        """
        Get browser-specific options.
        
        Returns:
            Dictionary of browser options
        """
        return self._config.get("browser", {})
    
    def get_timeout(self, timeout_type: str = "default") -> int:
        """
        Get timeout value for a specific type.
        
        Args:
            timeout_type: Type of timeout (default, element, page, network)
            
        Returns:
            Timeout value in milliseconds
        """
        timeouts = self._config.get("timeouts", {})
        return timeouts.get(timeout_type, timeouts.get("default", 20000))
    
    def get_database_config(self) -> Dict[str, Any]:
        """
        Get database configuration.
        
        Returns:
            Dictionary of database configuration
        """
        return self._config.get("database", {})
    
    def get_environment(self) -> str:
        """
        Get the current environment name.
        
        Returns:
            Environment name (dev, staging, prod)
        """
        return self._environment
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get the complete configuration dictionary.
        
        Returns:
            Complete configuration (deep copy)
        """
        return copy.deepcopy(self._config)
