"""
Unit tests for ConfigManager

Tests configuration loading, validation, and environment-specific settings.
"""

import pytest
import os
import tempfile
import yaml
from pathlib import Path
from hypothesis import given, strategies as st, settings

from raptor.core.config_manager import ConfigManager
from raptor.core.exceptions import ConfigurationException


class TestConfigManager:
    """Test suite for ConfigManager class."""
    
    @pytest.fixture
    def temp_config_dir(self):
        """Create a temporary configuration directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            
            # Create environments subdirectory
            env_dir = config_dir / "environments"
            env_dir.mkdir()
            
            # Create default settings.yaml
            default_config = {
                "browser": {
                    "type": "chromium",
                    "headless": False
                },
                "timeouts": {
                    "default": 20000,
                    "element": 20000
                },
                "database": {
                    "host": "localhost",
                    "user": "test_user"
                }
            }
            
            with open(config_dir / "settings.yaml", 'w') as f:
                yaml.dump(default_config, f)
            
            # Create dev environment config
            dev_config = {
                "browser": {
                    "headless": False,
                    "slow_mo": 100
                },
                "timeouts": {
                    "default": 30000
                },
                "logging": {
                    "level": "DEBUG"
                }
            }
            
            with open(env_dir / "dev.yaml", 'w') as f:
                yaml.dump(dev_config, f)
            
            # Create staging environment config
            staging_config = {
                "browser": {
                    "headless": True
                },
                "timeouts": {
                    "default": 25000
                }
            }
            
            with open(env_dir / "staging.yaml", 'w') as f:
                yaml.dump(staging_config, f)
            
            yield config_dir
    
    def test_init_loads_default_config(self, temp_config_dir):
        """Test that initialization loads the default configuration."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        assert manager.get("browser.type") == "chromium"
        assert manager.get("browser.headless") is False
        assert manager.get("timeouts.default") == 20000
    
    def test_load_environment_config(self, temp_config_dir):
        """Test loading environment-specific configuration."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        config = manager.load_config("dev")
        
        # Check merged values
        assert config["browser"]["type"] == "chromium"  # From default
        assert config["browser"]["headless"] is False  # From dev
        assert config["browser"]["slow_mo"] == 100  # From dev
        assert config["timeouts"]["default"] == 30000  # Overridden by dev
        assert config["logging"]["level"] == "DEBUG"  # From dev
    
    def test_environment_isolation(self, temp_config_dir):
        """Test that different environments have isolated configurations."""
        config_path = temp_config_dir / "settings.yaml"
        
        # Load dev config
        manager_dev = ConfigManager(config_path=str(config_path))
        dev_config = manager_dev.load_config("dev")
        
        # Load staging config
        manager_staging = ConfigManager(config_path=str(config_path))
        staging_config = manager_staging.load_config("staging")
        
        # Verify isolation
        assert dev_config["browser"]["headless"] is False
        assert staging_config["browser"]["headless"] is True
        assert dev_config["timeouts"]["default"] == 30000
        assert staging_config["timeouts"]["default"] == 25000
    
    def test_get_with_dot_notation(self, temp_config_dir):
        """Test getting values using dot notation."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        assert manager.get("browser.type") == "chromium"
        assert manager.get("timeouts.default") == 20000
        assert manager.get("database.host") == "localhost"
    
    def test_get_with_default(self, temp_config_dir):
        """Test getting values with default fallback."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        assert manager.get("nonexistent.key", "default_value") == "default_value"
        assert manager.get("browser.nonexistent", 123) == 123
    
    def test_set_value(self, temp_config_dir):
        """Test setting configuration values."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        manager.set("browser.type", "firefox")
        assert manager.get("browser.type") == "firefox"
        
        manager.set("new.nested.value", "test")
        assert manager.get("new.nested.value") == "test"
    
    def test_get_browser_options(self, temp_config_dir):
        """Test getting browser options."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        browser_options = manager.get_browser_options()
        
        assert browser_options["type"] == "chromium"
        assert browser_options["headless"] is False
    
    def test_get_timeout(self, temp_config_dir):
        """Test getting timeout values."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        assert manager.get_timeout("default") == 20000
        assert manager.get_timeout("element") == 20000
        assert manager.get_timeout("nonexistent") == 20000  # Falls back to default
    
    def test_get_database_config(self, temp_config_dir):
        """Test getting database configuration."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        db_config = manager.get_database_config()
        
        assert db_config["host"] == "localhost"
        assert db_config["user"] == "test_user"
    
    def test_get_environment(self, temp_config_dir):
        """Test getting current environment name."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        manager.load_config("dev")
        assert manager.get_environment() == "dev"
        
        manager.load_config("staging")
        assert manager.get_environment() == "staging"
    
    def test_validate_invalid_browser_type(self, temp_config_dir):
        """Test validation fails for invalid browser type."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        manager.set("browser.type", "invalid_browser")
        
        with pytest.raises(ConfigurationException) as exc_info:
            manager._validate_config()
        
        assert "Invalid browser type" in str(exc_info.value)
    
    def test_validate_invalid_timeout(self, temp_config_dir):
        """Test validation fails for invalid timeout values."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        manager.set("timeouts.default", -100)
        
        with pytest.raises(ConfigurationException) as exc_info:
            manager._validate_config()
        
        assert "Invalid timeout value" in str(exc_info.value)
    
    def test_validate_missing_database_fields(self, temp_config_dir):
        """Test validation fails for missing required database fields."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        # Remove required field
        manager.set("database", {"host": "localhost"})
        
        with pytest.raises(ConfigurationException) as exc_info:
            manager._validate_config()
        
        assert "Missing required database field" in str(exc_info.value)
    
    def test_missing_default_config_file(self):
        """Test error when default config file is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.yaml"
            
            with pytest.raises(ConfigurationException) as exc_info:
                ConfigManager(config_path=str(config_path))
            
            assert "Default configuration file not found" in str(exc_info.value)
    
    def test_missing_environment_config_file(self, temp_config_dir):
        """Test error when environment config file is missing."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        with pytest.raises(ConfigurationException) as exc_info:
            manager.load_config("nonexistent_env")
        
        assert "Environment configuration file not found" in str(exc_info.value)
    
    def test_env_variable_overrides(self, temp_config_dir, monkeypatch):
        """Test that environment variables override configuration."""
        config_path = temp_config_dir / "settings.yaml"
        
        # Set environment variables
        monkeypatch.setenv("RAPTOR_BROWSER_TYPE", "firefox")
        monkeypatch.setenv("RAPTOR_HEADLESS", "true")
        monkeypatch.setenv("RAPTOR_DEFAULT_TIMEOUT", "15000")
        
        manager = ConfigManager(config_path=str(config_path))
        manager.load_config("dev")
        
        assert manager.get("browser.type") == "firefox"
        assert manager.get("browser.headless") is True
        assert manager.get("timeouts.default") == 15000
    
    def test_get_all_returns_copy(self, temp_config_dir):
        """Test that get_all returns a copy of the configuration."""
        config_path = temp_config_dir / "settings.yaml"
        manager = ConfigManager(config_path=str(config_path))
        
        config1 = manager.get_all()
        config2 = manager.get_all()
        
        # Modify one copy
        config1["browser"]["type"] = "modified"
        
        # Verify the other copy is unchanged
        assert config2["browser"]["type"] == "chromium"
        assert manager.get("browser.type") == "chromium"
    
    @given(
        env1_headless=st.booleans(),
        env1_timeout=st.integers(min_value=1000, max_value=60000),
        env1_log_level=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR"]),
        env2_headless=st.booleans(),
        env2_timeout=st.integers(min_value=1000, max_value=60000),
        env2_log_level=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR"]),
    )
    @settings(max_examples=100, deadline=None)
    def test_property_configuration_environment_isolation(
        self,
        env1_headless,
        env1_timeout,
        env1_log_level,
        env2_headless,
        env2_timeout,
        env2_log_level,
    ):
        """
        **Feature: raptor-playwright-python, Property 10: Configuration Environment Isolation**
        
        Property: For any environment configuration, loading a specific environment 
        should not affect other environment settings.
        
        **Validates: Requirements 10.2**
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir)
            env_dir = config_dir / "environments"
            env_dir.mkdir()
            
            # Create default settings.yaml
            default_config = {
                "browser": {
                    "type": "chromium",
                    "headless": False
                },
                "timeouts": {
                    "default": 20000,
                    "element": 20000
                },
                "logging": {
                    "level": "INFO"
                },
                "database": {
                    "host": "localhost",
                    "user": "test_user"
                }
            }
            
            with open(config_dir / "settings.yaml", 'w') as f:
                yaml.dump(default_config, f)
            
            # Create env1 configuration with random values
            env1_config = {
                "browser": {
                    "headless": env1_headless
                },
                "timeouts": {
                    "default": env1_timeout
                },
                "logging": {
                    "level": env1_log_level
                }
            }
            
            with open(env_dir / "env1.yaml", 'w') as f:
                yaml.dump(env1_config, f)
            
            # Create env2 configuration with different random values
            env2_config = {
                "browser": {
                    "headless": env2_headless
                },
                "timeouts": {
                    "default": env2_timeout
                },
                "logging": {
                    "level": env2_log_level
                }
            }
            
            with open(env_dir / "env2.yaml", 'w') as f:
                yaml.dump(env2_config, f)
            
            config_path = config_dir / "settings.yaml"
            
            # Load env1 configuration
            manager1 = ConfigManager(config_path=str(config_path))
            config1 = manager1.load_config("env1")
            
            # Load env2 configuration
            manager2 = ConfigManager(config_path=str(config_path))
            config2 = manager2.load_config("env2")
            
            # Verify env1 has its own values
            assert config1["browser"]["headless"] == env1_headless, \
                "env1 should have its own headless setting"
            assert config1["timeouts"]["default"] == env1_timeout, \
                "env1 should have its own timeout setting"
            assert config1["logging"]["level"] == env1_log_level, \
                "env1 should have its own log level"
            
            # Verify env2 has its own values
            assert config2["browser"]["headless"] == env2_headless, \
                "env2 should have its own headless setting"
            assert config2["timeouts"]["default"] == env2_timeout, \
                "env2 should have its own timeout setting"
            assert config2["logging"]["level"] == env2_log_level, \
                "env2 should have its own log level"
            
            # Verify isolation: env1 values should not affect env2
            if env1_headless != env2_headless:
                assert config1["browser"]["headless"] != config2["browser"]["headless"], \
                    "Different environments should have isolated headless settings"
            
            if env1_timeout != env2_timeout:
                assert config1["timeouts"]["default"] != config2["timeouts"]["default"], \
                    "Different environments should have isolated timeout settings"
            
            if env1_log_level != env2_log_level:
                assert config1["logging"]["level"] != config2["logging"]["level"], \
                    "Different environments should have isolated log level settings"
            
            # Verify both environments inherit from default config
            assert config1["browser"]["type"] == "chromium", \
                "env1 should inherit default browser type"
            assert config2["browser"]["type"] == "chromium", \
                "env2 should inherit default browser type"
            assert config1["database"]["host"] == "localhost", \
                "env1 should inherit default database host"
            assert config2["database"]["host"] == "localhost", \
                "env2 should inherit default database host"
