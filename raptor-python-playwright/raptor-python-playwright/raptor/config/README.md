# RAPTOR Configuration System

This directory contains the configuration files for the RAPTOR framework.

## Structure

```
config/
├── settings.yaml           # Default configuration (base settings)
└── environments/           # Environment-specific configurations
    ├── dev.yaml           # Development environment
    ├── staging.yaml       # Staging environment
    └── prod.yaml          # Production environment
```

## Configuration Files

### settings.yaml

The `settings.yaml` file contains default configuration values that apply to all environments. These settings serve as the base configuration and can be overridden by environment-specific files.

### Environment Files

Environment-specific configuration files (dev.yaml, staging.yaml, prod.yaml) override the default settings for their respective environments. Values in these files take precedence over the defaults.

## Usage

### Basic Usage

```python
from raptor.core.config_manager import ConfigManager

# Initialize with default configuration
config = ConfigManager()

# Load environment-specific configuration
config.load_config("dev")  # or "staging", "prod"

# Access configuration values
browser_type = config.get("browser.type")
timeout = config.get("timeouts.default")
```

### Accessing Nested Values

Use dot notation to access nested configuration values:

```python
# Get nested value
headless = config.get("browser.headless")
db_host = config.get("database.host")

# Get with default value
custom = config.get("custom.setting", "default_value")
```

### Helper Methods

```python
# Get browser options
browser_opts = config.get_browser_options()

# Get timeout values
default_timeout = config.get_timeout("default")
element_timeout = config.get_timeout("element")

# Get database configuration
db_config = config.get_database_config()

# Get current environment
env = config.get_environment()

# Get all configuration
all_config = config.get_all()
```

### Setting Values

```python
# Set configuration value
config.set("browser.type", "firefox")
config.set("custom.nested.value", "test")
```

## Environment Variables

Configuration values can be overridden using environment variables. The following environment variables are supported:

### Browser Settings
- `RAPTOR_BROWSER_TYPE` - Browser type (chromium, firefox, webkit)
- `RAPTOR_HEADLESS` - Headless mode (true/false)

### Timeout Settings
- `RAPTOR_DEFAULT_TIMEOUT` - Default timeout in milliseconds

### Database Settings
- `RAPTOR_DB_HOST` - Database host
- `RAPTOR_DB_PORT` - Database port
- `RAPTOR_DB_USER` - Database username
- `RAPTOR_DB_PASSWORD` - Database password
- `RAPTOR_DB_NAME` - Database name

### ALM Settings
- `RAPTOR_ALM_URL` - ALM server URL
- `RAPTOR_ALM_USERNAME` - ALM username
- `RAPTOR_ALM_PASSWORD` - ALM password
- `RAPTOR_ALM_DOMAIN` - ALM domain
- `RAPTOR_ALM_PROJECT` - ALM project

### JIRA Settings
- `RAPTOR_JIRA_URL` - JIRA server URL
- `RAPTOR_JIRA_USERNAME` - JIRA username
- `RAPTOR_JIRA_API_TOKEN` - JIRA API token
- `RAPTOR_JIRA_PROJECT_KEY` - JIRA project key

### Environment Selection
- `RAPTOR_ENVIRONMENT` - Environment to load (dev, staging, prod)

## .env File

Create a `.env` file in the project root to set environment variables:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your values
RAPTOR_BROWSER_TYPE=chromium
RAPTOR_HEADLESS=false
RAPTOR_DB_HOST=localhost
RAPTOR_DB_USER=your_username
RAPTOR_DB_PASSWORD=your_password
```

**Note:** The `.env` file is automatically loaded by the ConfigManager and should never be committed to version control.

## Configuration Validation

The ConfigManager automatically validates configuration values:

- **Browser Type**: Must be one of: chromium, firefox, webkit
- **Timeouts**: Must be positive numbers
- **Database**: Must include required fields (host, user)

Invalid configurations will raise a `ConfigurationException`.

## Adding New Configuration

To add new configuration options:

1. Add the default value to `settings.yaml`
2. Override in environment files as needed (dev.yaml, staging.yaml, prod.yaml)
3. Access using `config.get("your.new.setting")`

Example:

```yaml
# settings.yaml
my_feature:
  enabled: true
  timeout: 5000
  options:
    - option1
    - option2
```

```python
# Access in code
enabled = config.get("my_feature.enabled")
timeout = config.get("my_feature.timeout")
options = config.get("my_feature.options")
```

## Best Practices

1. **Use Environment Variables for Secrets**: Never store passwords or API tokens in YAML files. Use environment variables instead.

2. **Environment-Specific Settings**: Keep environment-specific settings in their respective files (dev.yaml, staging.yaml, prod.yaml).

3. **Default Values**: Always provide sensible defaults in settings.yaml.

4. **Validation**: Add validation for critical configuration values.

5. **Documentation**: Document new configuration options in this README.

## Troubleshooting

### Configuration File Not Found

If you see "Default configuration file not found", ensure:
- The `config/settings.yaml` file exists
- The file path is correct
- You have read permissions

### Invalid Configuration

If you see "Invalid browser type" or similar validation errors:
- Check the configuration value matches allowed values
- Verify the data type is correct (string, number, boolean)
- Review the validation rules in `config_manager.py`

### Environment Variables Not Working

If environment variables aren't being applied:
- Ensure the `.env` file exists in the project root
- Check variable names match the expected format (RAPTOR_*)
- Verify the `.env` file is being loaded before configuration

## Examples

See `examples/config_example.py` for a complete working example of the configuration system.
