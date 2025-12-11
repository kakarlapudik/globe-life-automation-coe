"""
Example: Using the ConfigManager

This example demonstrates how to use the ConfigManager to load and access
configuration settings in the RAPTOR framework.
"""

from raptor.core.config_manager import ConfigManager


def main():
    """Demonstrate ConfigManager usage."""
    
    print("=" * 60)
    print("RAPTOR ConfigManager Example")
    print("=" * 60)
    
    # Initialize ConfigManager (uses default config/settings.yaml)
    config = ConfigManager()
    
    print("\n1. Default Configuration:")
    print(f"   Browser Type: {config.get('browser.type')}")
    print(f"   Headless Mode: {config.get('browser.headless')}")
    print(f"   Default Timeout: {config.get('timeouts.default')}ms")
    
    # Load development environment configuration
    print("\n2. Loading Development Environment:")
    config.load_config("dev")
    print(f"   Environment: {config.get_environment()}")
    print(f"   Browser Type: {config.get('browser.type')}")
    print(f"   Headless Mode: {config.get('browser.headless')}")
    print(f"   Default Timeout: {config.get('timeouts.default')}ms")
    print(f"   Logging Level: {config.get('logging.level')}")
    
    # Load staging environment configuration
    print("\n3. Loading Staging Environment:")
    config_staging = ConfigManager()
    config_staging.load_config("staging")
    print(f"   Environment: {config_staging.get_environment()}")
    print(f"   Browser Type: {config_staging.get('browser.type')}")
    print(f"   Headless Mode: {config_staging.get('browser.headless')}")
    print(f"   Default Timeout: {config_staging.get('timeouts.default')}ms")
    
    # Get browser options
    print("\n4. Browser Options:")
    browser_opts = config.get_browser_options()
    for key, value in browser_opts.items():
        print(f"   {key}: {value}")
    
    # Get timeout values
    print("\n5. Timeout Values:")
    print(f"   Default: {config.get_timeout('default')}ms")
    print(f"   Element: {config.get_timeout('element')}ms")
    print(f"   Page: {config.get_timeout('page')}ms")
    
    # Get database configuration
    print("\n6. Database Configuration:")
    db_config = config.get_database_config()
    print(f"   Host: {db_config.get('host')}")
    print(f"   Port: {db_config.get('port')}")
    print(f"   Database: {db_config.get('database')}")
    print(f"   User: {db_config.get('user')}")
    
    # Set custom values
    print("\n7. Setting Custom Values:")
    config.set("custom.setting", "my_value")
    print(f"   Custom Setting: {config.get('custom.setting')}")
    
    # Using default values
    print("\n8. Using Default Values:")
    print(f"   Nonexistent Key: {config.get('nonexistent.key', 'default_value')}")
    
    print("\n" + "=" * 60)
    print("Example Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
