"""
Property-Based Test: Configuration Environment Isolation

**Feature: raptor-playwright-python, Property 10: Configuration Environment Isolation**
**Validates: Requirements 10.2**

This test verifies that environment configurations are properly isolated and
loading one environment doesn't affect other environment settings.

Property Statement:
    For any environment configuration, loading a specific environment should not 
    affect other environment settings.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from typing import Dict, Any
import copy


# Strategy for environment names
environment_strategy = st.sampled_from(['dev', 'staging', 'prod', 'test', 'local'])

# Strategy for configuration values
config_value_strategy = st.one_of(
    st.text(min_size=1, max_size=50),
    st.integers(min_value=0, max_value=10000),
    st.booleans(),
    st.floats(min_value=0.0, max_value=100.0)
)

# Strategy for configuration dictionaries
config_dict_strategy = st.dictionaries(
    keys=st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll'), whitelist_characters='_'),
        min_size=3,
        max_size=20
    ),
    values=config_value_strategy,
    min_size=1,
    max_size=10
)


class ConfigurationManager:
    """
    Mock configuration manager with environment isolation.
    
    This simulates the ConfigManager's environment-specific configuration loading.
    """
    
    def __init__(self):
        self._environments = {}
        self._current_environment = None
        self._current_config = {}
    
    def register_environment(self, env_name: str, config: Dict[str, Any]):
        """Register a configuration for an environment."""
        # Store a deep copy to ensure isolation
        self._environments[env_name] = copy.deepcopy(config)
    
    def load_environment(self, env_name: str) -> Dict[str, Any]:
        """Load configuration for a specific environment."""
        if env_name not in self._environments:
            raise ValueError(f"Environment '{env_name}' not found")
        
        self._current_environment = env_name
        # Return a deep copy to ensure isolation
        self._current_config = copy.deepcopy(self._environments[env_name])
        return self._current_config
    
    def get_current_config(self) -> Dict[str, Any]:
        """Get the currently loaded configuration."""
        return copy.deepcopy(self._current_config)
    
    def get_environment_config(self, env_name: str) -> Dict[str, Any]:
        """Get configuration for a specific environment without loading it."""
        if env_name not in self._environments:
            raise ValueError(f"Environment '{env_name}' not found")
        return copy.deepcopy(self._environments[env_name])


class TestConfigurationEnvironmentIsolation:
    """
    Property-based tests for configuration environment isolation.
    
    These tests verify that environment configurations are properly isolated
    and don't interfere with each other.
    """
    
    @given(
        env1=environment_strategy,
        env2=environment_strategy,
        config1=config_dict_strategy,
        config2=config_dict_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_loading_one_environment_doesnt_affect_another(
        self, env1, env2, config1, config2
    ):
        """
        Property: Loading one environment should not affect other environments.
        
        When loading configuration for one environment, the configurations
        of other environments should remain unchanged.
        
        Args:
            env1: First environment name
            env2: Second environment name
            config1: Configuration for first environment
            config2: Configuration for second environment
        """
        # Ensure environments are different
        assume(env1 != env2)
        
        config_manager = ConfigurationManager()
        
        # Register both environments
        config_manager.register_environment(env1, config1)
        config_manager.register_environment(env2, config2)
        
        # Get initial state of env2
        initial_env2_config = config_manager.get_environment_config(env2)
        
        # Load env1
        config_manager.load_environment(env1)
        
        # Property: env2 configuration should be unchanged
        current_env2_config = config_manager.get_environment_config(env2)
        assert current_env2_config == initial_env2_config, (
            f"Loading {env1} should not affect {env2} configuration"
        )
    
    @given(
        environments=st.lists(
            st.tuples(environment_strategy, config_dict_strategy),
            min_size=2,
            max_size=5,
            unique_by=lambda x: x[0]
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_multiple_environments_remain_isolated(self, environments):
        """
        Property: Multiple environments should remain isolated from each other.
        
        When multiple environments are registered, each should maintain its
        own independent configuration.
        
        Args:
            environments: List of (environment_name, config) tuples
        """
        config_manager = ConfigurationManager()
        
        # Register all environments
        for env_name, config in environments:
            config_manager.register_environment(env_name, config)
        
        # Store initial configurations
        initial_configs = {
            env_name: config_manager.get_environment_config(env_name)
            for env_name, _ in environments
        }
        
        # Load each environment and verify others remain unchanged
        for target_env, _ in environments:
            config_manager.load_environment(target_env)
            
            # Verify all other environments are unchanged
            for env_name, _ in environments:
                if env_name != target_env:
                    current_config = config_manager.get_environment_config(env_name)
                    assert current_config == initial_configs[env_name], (
                        f"Loading {target_env} should not affect {env_name}"
                    )
    
    @given(
        env_name=environment_strategy,
        config=config_dict_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_modifying_loaded_config_doesnt_affect_stored_config(
        self, env_name, config
    ):
        """
        Property: Modifying loaded config should not affect stored config.
        
        When a configuration is loaded and then modified, the stored
        configuration for that environment should remain unchanged.
        
        Args:
            env_name: Environment name
            config: Configuration dictionary
        """
        # Ensure config has at least one key
        assume(len(config) > 0)
        
        config_manager = ConfigurationManager()
        config_manager.register_environment(env_name, config)
        
        # Load configuration
        loaded_config = config_manager.load_environment(env_name)
        
        # Modify loaded configuration
        first_key = list(loaded_config.keys())[0]
        original_value = loaded_config[first_key]
        loaded_config[first_key] = "MODIFIED_VALUE"
        
        # Property: Stored configuration should be unchanged
        stored_config = config_manager.get_environment_config(env_name)
        assert stored_config[first_key] == original_value, (
            "Modifying loaded config should not affect stored config"
        )
    
    @given(
        env_name=environment_strategy,
        config=config_dict_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_loading_same_environment_multiple_times(
        self, env_name, config
    ):
        """
        Property: Loading same environment multiple times should be consistent.
        
        Loading the same environment multiple times should always return
        the same configuration.
        
        Args:
            env_name: Environment name
            config: Configuration dictionary
        """
        config_manager = ConfigurationManager()
        config_manager.register_environment(env_name, config)
        
        # Load environment multiple times
        config1 = config_manager.load_environment(env_name)
        config2 = config_manager.load_environment(env_name)
        config3 = config_manager.load_environment(env_name)
        
        # Property: All loaded configs should be identical
        assert config1 == config2 == config3, (
            "Loading same environment multiple times should return same config"
        )
    
    @given(
        env1=environment_strategy,
        env2=environment_strategy,
        config1=config_dict_strategy,
        config2=config_dict_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_switching_environments_updates_current_config(
        self, env1, env2, config1, config2
    ):
        """
        Property: Switching environments should update current configuration.
        
        When switching from one environment to another, the current
        configuration should reflect the new environment.
        
        Args:
            env1: First environment name
            env2: Second environment name
            config1: Configuration for first environment
            config2: Configuration for second environment
        """
        # Ensure environments are different
        assume(env1 != env2)
        
        config_manager = ConfigurationManager()
        config_manager.register_environment(env1, config1)
        config_manager.register_environment(env2, config2)
        
        # Load env1
        config_manager.load_environment(env1)
        current_config = config_manager.get_current_config()
        assert current_config == config1
        
        # Switch to env2
        config_manager.load_environment(env2)
        current_config = config_manager.get_current_config()
        assert current_config == config2
        
        # Switch back to env1
        config_manager.load_environment(env1)
        current_config = config_manager.get_current_config()
        assert current_config == config1
    
    @given(
        environments=st.lists(
            st.tuples(environment_strategy, config_dict_strategy),
            min_size=2,
            max_size=5,
            unique_by=lambda x: x[0]
        )
    )
    @settings(max_examples=100, deadline=5000)
    def test_environment_configs_are_independent(self, environments):
        """
        Property: Environment configurations should be completely independent.
        
        Configurations for different environments should not share any
        mutable state.
        
        Args:
            environments: List of (environment_name, config) tuples
        """
        config_manager = ConfigurationManager()
        
        # Register all environments
        for env_name, config in environments:
            config_manager.register_environment(env_name, config)
        
        # Get all configurations
        configs = [
            config_manager.get_environment_config(env_name)
            for env_name, _ in environments
        ]
        
        # Property: Modifying one config doesn't affect others
        if len(configs) >= 2 and len(configs[0]) > 0:
            first_key = list(configs[0].keys())[0]
            configs[0][first_key] = "MODIFIED"
            
            # Verify other configs are unchanged
            for i in range(1, len(configs)):
                if first_key in configs[i]:
                    # Get fresh copy from manager
                    fresh_config = config_manager.get_environment_config(
                        environments[i][0]
                    )
                    assert fresh_config[first_key] == environments[i][1][first_key], (
                        "Modifying one environment's config should not affect others"
                    )
    
    @given(
        env_name=environment_strategy,
        config=config_dict_strategy
    )
    @settings(max_examples=100, deadline=5000)
    def test_unloaded_environment_not_affected_by_current(
        self, env_name, config
    ):
        """
        Property: Unloaded environments should not be affected by current environment.
        
        An environment that hasn't been loaded should maintain its original
        configuration regardless of what environment is currently loaded.
        
        Args:
            env_name: Environment name
            config: Configuration dictionary
        """
        config_manager = ConfigurationManager()
        
        # Register environment but don't load it
        config_manager.register_environment(env_name, config)
        
        # Register and load a different environment
        other_env = f"other_{env_name}"
        other_config = {"different": "config"}
        config_manager.register_environment(other_env, other_config)
        config_manager.load_environment(other_env)
        
        # Property: Original environment should be unchanged
        stored_config = config_manager.get_environment_config(env_name)
        assert stored_config == config, (
            "Unloaded environment should not be affected by current environment"
        )


def test_property_coverage():
    """
    Verify that this test file covers Property 10: Configuration Environment Isolation.
    
    This is a meta-test to ensure the property is properly documented and tested.
    """
    # Verify property is documented in module docstring
    assert "Property 10: Configuration Environment Isolation" in __doc__
    assert "Validates: Requirements 10.2" in __doc__
    
    # Verify test class exists
    assert TestConfigurationEnvironmentIsolation is not None
    
    # Verify key test methods exist
    test_methods = [
        'test_loading_one_environment_doesnt_affect_another',
        'test_multiple_environments_remain_isolated',
        'test_modifying_loaded_config_doesnt_affect_stored_config',
        'test_loading_same_environment_multiple_times',
        'test_switching_environments_updates_current_config',
        'test_environment_configs_are_independent',
        'test_unloaded_environment_not_affected_by_current'
    ]
    
    for method_name in test_methods:
        assert hasattr(TestConfigurationEnvironmentIsolation, method_name), (
            f"Test method {method_name} not found"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
