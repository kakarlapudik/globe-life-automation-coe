# RAPTOR Configuration Guide

This guide covers all configuration options available in the RAPTOR Python Playwright Framework.

## Table of Contents

- [Configuration Overview](#configuration-overview)
- [Configuration File Structure](#configuration-file-structure)
- [Browser Configuration](#browser-configuration)
- [Database Configuration](#database-configuration)
- [Logging Configuration](#logging-configuration)
- [Reporting Configuration](#reporting-configuration)
- [Session Management Configuration](#session-management-configuration)
- [Test Execution Configuration](#test-execution-configuration)
- [Environment-Specific Configuration](#environment-specific-configuration)
- [Environment Variables](#environment-variables)
- [Advanced Configuration](#advanced-configuration)

## Configuration Overview

RAPTOR uses a hierarchical configuration system that supports:

- **YAML configuration files** for structured settings
- **Environment-specific overrides** for dev/staging/prod
- **Environment variables** for sensitive data
- **Programmatic configuration** for dynamic settings

### Configuration Priority

Configuration is loaded in the following order (later overrides earlier):

1. Default settings (built-in)
2. `config/settings.yaml` (base configuration)
3. `config/environments/{env}.yaml` (environment-specific)
4. Environment variables
5. Command-line arguments
6. Programmatic overrides

## Configuration File Structure

### Base Configuration File

Create `config/settings.yaml`:

```yaml
# ============================================================================
# RAPTOR Framework Configuration
# ============================================================================

# Browser Configuration
browser:
  type: chromium                    # chromium, firefox, webkit
  headless: false                   # Run in headless mode
  timeout: 30000                    # Default timeout in milliseconds
  slow_mo: 0                        # Slow down operations (ms)
  
  viewport:
    width: 1920
    height: 1080
  
  args:                             # Browser launch arguments
    - --disable-dev-shm-usage
    - --no-sandbox
    - --disable-setuid-sandbox
  
  ignore_https_errors: false        # Ignore HTTPS certificate errors
  downloads_path: downloads         # Download directory
  
  context:
    accept_downloads: true
    ignore_https_errors: false
    java_script_enabled: true
    bypass_csp: false
    locale: en-US
    timezone_id: America/New_York
    geolocation:
      latitude: 40.7128
      longitude: -74.0060
    permissions:
      - geolocation
      - notifications
    
  recording:
    video: false                    # Record video
    video_size:
      width: 1920
      height: 1080
    screenshots: true               # Capture screenshots

# Database Configuration
database:
  type: sqlserver                   # sqlserver, postgresql, mysql, oracle
  server: localhost
  port: 1433
  database: test_db
  user: test_user
  password: ${DB_PASSWORD}          # Use environment variable
  
  connection_pool:
    min_size: 2
    max_size: 10
    timeout: 30
    max_overflow: 5
  
  options:
    driver: ODBC Driver 17 for SQL Server
    trusted_connection: false
    encrypt: true
    trust_server_certificate: false
  
  dddb:
    enabled: true
    table_prefix: DDDB_
    auto_export: true

# Logging Configuration
logging:
  level: INFO                       # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  date_format: "%Y-%m-%d %H:%M:%S"
  
  console:
    enabled: true
    level: INFO
    colored: true
  
  file:
    enabled: true
    path: logs/raptor.log
    level: DEBUG
    rotation: daily                 # daily, size, time
    retention: 30                   # days
    max_bytes: 10485760            # 10MB
    backup_count: 10
  
  structured:
    enabled: false
    format: json                    # json, logfmt
    include_context: true

# Reporting Configuration
reporting:
  enabled: true
  output_dir: reports
  
  html:
    enabled: true
    template: default               # default, detailed, minimal
    include_screenshots: true
    include_logs: true
    include_timing: true
  
  junit:
    enabled: false
    output_file: reports/junit.xml
  
  allure:
    enabled: false
    results_dir: allure-results
  
  screenshots:
    on_failure: true
    on_success: false
    full_page: true
    path: screenshots
    format: png                     # png, jpeg
    quality: 90
  
  video:
    on_failure: false
    on_success: false
    path: videos
    size:
      width: 1920
      height: 1080

# Session Management Configuration
session:
  enabled: true
  storage_dir: .sessions
  expiration_hours: 24
  auto_cleanup: true
  cleanup_interval: 3600            # seconds
  max_sessions: 100
  
  persistence:
    save_cookies: true
    save_local_storage: true
    save_session_storage: true
    save_cache: false

# Test Execution Configuration
execution:
  retry:
    enabled: true
    max_attempts: 2
    delay: 1                        # seconds
    exponential_backoff: true
    backoff_factor: 2
  
  timeout:
    default: 300                    # seconds
    element: 30
    page_load: 60
    network_idle: 30
  
  parallel:
    enabled: false
    workers: 4
    worker_timeout: 600
  
  data_driven:
    enabled: true
    batch_size: 10
    parallel_iterations: false
  
  soft_assertions:
    enabled: true
    fail_at_end: true

# Element Location Configuration
elements:
  wait_timeout: 20000               # milliseconds
  poll_interval: 100                # milliseconds
  
  locator_strategies:
    - css
    - xpath
    - text
    - role
    - id
  
  fallback:
    enabled: true
    max_attempts: 3
  
  retry:
    enabled: true
    max_attempts: 3
    delay: 500                      # milliseconds

# Integration Configuration
integrations:
  alm:
    enabled: false
    url: https://alm.example.com
    domain: DEFAULT
    project: TestProject
    api_key: ${ALM_API_KEY}
    
  jira:
    enabled: false
    url: https://jira.example.com
    username: ${JIRA_USERNAME}
    api_token: ${JIRA_API_TOKEN}
    project_key: TEST
    
  slack:
    enabled: false
    webhook_url: ${SLACK_WEBHOOK_URL}
    channel: #test-results
    
  email:
    enabled: false
    smtp_server: smtp.example.com
    smtp_port: 587
    username: ${EMAIL_USERNAME}
    password: ${EMAIL_PASSWORD}
    from_address: noreply@example.com
    to_addresses:
      - team@example.com

# Performance Configuration
performance:
  monitoring:
    enabled: false
    metrics:
      - cpu
      - memory
      - network
    interval: 5                     # seconds
  
  optimization:
    cache_elements: true
    cache_config: true
    lazy_load: true
    connection_pooling: true

# Security Configuration
security:
  credentials:
    storage: env                    # env, file, vault
    encryption: true
  
  ssl:
    verify: true
    cert_path: null
  
  secrets:
    vault_url: ${VAULT_URL}
    vault_token: ${VAULT_TOKEN}
```

## Browser Configuration

### Browser Types

```yaml
browser:
  type: chromium  # Options: chromium, firefox, webkit
```

### Headless Mode

```yaml
browser:
  headless: true  # Run without GUI
```

### Browser Arguments

```yaml
browser:
  args:
    - --disable-dev-shm-usage      # Overcome limited resource problems
    - --no-sandbox                 # Required for Docker
    - --disable-setuid-sandbox
    - --disable-gpu                # Disable GPU hardware acceleration
    - --window-size=1920,1080      # Set window size
    - --start-maximized            # Start maximized
    - --incognito                  # Start in incognito mode
    - --disable-extensions         # Disable extensions
    - --disable-blink-features=AutomationControlled  # Hide automation
```

### Viewport Configuration

```yaml
browser:
  viewport:
    width: 1920
    height: 1080
    device_scale_factor: 1
    is_mobile: false
    has_touch: false
```

### Context Options

```yaml
browser:
  context:
    accept_downloads: true
    ignore_https_errors: false
    java_script_enabled: true
    bypass_csp: false                # Bypass Content-Security-Policy
    locale: en-US
    timezone_id: America/New_York
    
    geolocation:
      latitude: 40.7128
      longitude: -74.0060
      accuracy: 100
    
    permissions:
      - geolocation
      - notifications
      - camera
      - microphone
    
    user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    extra_http_headers:
      X-Custom-Header: value
```

## Database Configuration

### SQL Server

```yaml
database:
  type: sqlserver
  server: localhost
  port: 1433
  database: test_db
  user: test_user
  password: ${DB_PASSWORD}
  
  options:
    driver: ODBC Driver 17 for SQL Server
    trusted_connection: false
    encrypt: true
    trust_server_certificate: false
```

### PostgreSQL

```yaml
database:
  type: postgresql
  server: localhost
  port: 5432
  database: test_db
  user: test_user
  password: ${DB_PASSWORD}
  
  options:
    sslmode: require
    connect_timeout: 10
```

### MySQL

```yaml
database:
  type: mysql
  server: localhost
  port: 3306
  database: test_db
  user: test_user
  password: ${DB_PASSWORD}
  
  options:
    charset: utf8mb4
    use_unicode: true
```

### Connection Pooling

```yaml
database:
  connection_pool:
    min_size: 2                     # Minimum connections
    max_size: 10                    # Maximum connections
    timeout: 30                     # Connection timeout (seconds)
    max_overflow: 5                 # Max connections beyond max_size
    pool_recycle: 3600              # Recycle connections after (seconds)
    echo: false                     # Log SQL statements
```

## Logging Configuration

### Log Levels

```yaml
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Console Logging

```yaml
logging:
  console:
    enabled: true
    level: INFO
    colored: true                   # Use colored output
    format: "%(levelname)s: %(message)s"
```

### File Logging

```yaml
logging:
  file:
    enabled: true
    path: logs/raptor.log
    level: DEBUG
    rotation: daily                 # daily, size, time
    retention: 30                   # Keep logs for 30 days
    max_bytes: 10485760            # 10MB per file
    backup_count: 10               # Keep 10 backup files
```

### Structured Logging

```yaml
logging:
  structured:
    enabled: true
    format: json                    # json, logfmt
    include_context: true
    include_timestamp: true
    include_level: true
    include_logger: true
```

## Reporting Configuration

### HTML Reports

```yaml
reporting:
  html:
    enabled: true
    template: detailed              # default, detailed, minimal
    output_file: reports/report.html
    include_screenshots: true
    include_logs: true
    include_timing: true
    include_system_info: true
    theme: light                    # light, dark
```

### JUnit XML Reports

```yaml
reporting:
  junit:
    enabled: true
    output_file: reports/junit.xml
    include_properties: true
    include_system_out: true
    include_system_err: true
```

### Allure Reports

```yaml
reporting:
  allure:
    enabled: true
    results_dir: allure-results
    clean_results: true
    categories_file: allure-categories.json
```

### Screenshot Configuration

```yaml
reporting:
  screenshots:
    on_failure: true
    on_success: false
    full_page: true
    path: screenshots
    format: png                     # png, jpeg
    quality: 90                     # JPEG quality (1-100)
    naming: timestamp               # timestamp, sequential, test_name
```

## Session Management Configuration

```yaml
session:
  enabled: true
  storage_dir: .sessions
  expiration_hours: 24
  auto_cleanup: true
  cleanup_interval: 3600            # seconds
  max_sessions: 100
  
  persistence:
    save_cookies: true
    save_local_storage: true
    save_session_storage: true
    save_cache: false
    save_service_workers: false
  
  restore:
    verify_url: true
    verify_cookies: true
    timeout: 30                     # seconds
```

## Test Execution Configuration

### Retry Configuration

```yaml
execution:
  retry:
    enabled: true
    max_attempts: 3
    delay: 1                        # seconds
    exponential_backoff: true
    backoff_factor: 2
    retry_on:
      - TimeoutException
      - ElementNotFoundException
```

### Timeout Configuration

```yaml
execution:
  timeout:
    default: 300                    # Default test timeout (seconds)
    element: 30                     # Element wait timeout
    page_load: 60                   # Page load timeout
    network_idle: 30                # Network idle timeout
    action: 10                      # Action timeout (click, fill, etc.)
```

### Parallel Execution

```yaml
execution:
  parallel:
    enabled: true
    workers: 4                      # Number of parallel workers
    worker_timeout: 600             # Worker timeout (seconds)
    distribute: loadscope           # loadscope, loadfile, loadgroup
```

## Environment-Specific Configuration

### Development Environment

Create `config/environments/dev.yaml`:

```yaml
browser:
  headless: false
  slow_mo: 100                      # Slow down for debugging

database:
  server: localhost
  database: test_db_dev

logging:
  level: DEBUG
  console:
    enabled: true

reporting:
  screenshots:
    on_success: true                # Capture all screenshots in dev
```

### Staging Environment

Create `config/environments/staging.yaml`:

```yaml
browser:
  headless: true

database:
  server: staging-db.example.com
  database: test_db_staging

logging:
  level: INFO

reporting:
  html:
    enabled: true
  junit:
    enabled: true
```

### Production Environment

Create `config/environments/prod.yaml`:

```yaml
browser:
  headless: true
  args:
    - --disable-dev-shm-usage
    - --no-sandbox

database:
  server: prod-db.example.com
  database: test_db_prod
  connection_pool:
    max_size: 20

logging:
  level: WARNING
  file:
    retention: 90

reporting:
  html:
    enabled: true
  junit:
    enabled: true
  allure:
    enabled: true

integrations:
  jira:
    enabled: true
  slack:
    enabled: true
```

## Environment Variables

### Database Credentials

```bash
# .env file
DB_SERVER=localhost
DB_NAME=test_db
DB_USER=test_user
DB_PASSWORD=secure_password
```

### Integration Credentials

```bash
# ALM Integration
ALM_URL=https://alm.example.com
ALM_API_KEY=your_api_key

# JIRA Integration
JIRA_URL=https://jira.example.com
JIRA_USERNAME=your_username
JIRA_API_TOKEN=your_api_token

# Slack Integration
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email Integration
EMAIL_USERNAME=noreply@example.com
EMAIL_PASSWORD=email_password
```

### Environment Selection

```bash
# Set test environment
TEST_ENVIRONMENT=dev  # dev, staging, prod
```

## Advanced Configuration

### Programmatic Configuration

```python
from raptor.core import ConfigManager

# Load configuration
config = ConfigManager()
config.load_config(environment="dev")

# Override settings programmatically
config.set("browser.headless", True)
config.set("logging.level", "DEBUG")
config.set("execution.parallel.workers", 8)

# Get configuration values
browser_type = config.get("browser.type")
timeout = config.get("browser.timeout", default=30000)
```

### Dynamic Configuration

```python
import os
from raptor.core import ConfigManager

# Load configuration based on environment variable
env = os.getenv("TEST_ENVIRONMENT", "dev")
config = ConfigManager()
config.load_config(environment=env)

# Override based on CI/CD environment
if os.getenv("CI"):
    config.set("browser.headless", True)
    config.set("execution.parallel.enabled", True)
    config.set("reporting.video.on_failure", True)
```

### Configuration Validation

```python
from raptor.core import ConfigManager

config = ConfigManager()

# Validate configuration
try:
    config.validate()
    print("Configuration is valid")
except ConfigurationException as e:
    print(f"Configuration error: {e}")
```

## Configuration Best Practices

1. **Use Environment Variables for Secrets**: Never commit passwords or API keys
2. **Environment-Specific Configs**: Maintain separate configs for each environment
3. **Default Values**: Provide sensible defaults in base configuration
4. **Documentation**: Comment your configuration files
5. **Validation**: Validate configuration on startup
6. **Version Control**: Commit configuration templates, not actual credentials
7. **Encryption**: Encrypt sensitive configuration data
8. **Centralized Management**: Use configuration management tools for large deployments

## Configuration Examples

### Minimal Configuration

```yaml
browser:
  type: chromium
  headless: true

logging:
  level: INFO
```

### CI/CD Configuration

```yaml
browser:
  type: chromium
  headless: true
  args:
    - --disable-dev-shm-usage
    - --no-sandbox

execution:
  parallel:
    enabled: true
    workers: 4
  retry:
    enabled: true
    max_attempts: 2

reporting:
  junit:
    enabled: true
  html:
    enabled: true
  screenshots:
    on_failure: true
```

### Full-Featured Configuration

See the complete example in `config/settings.yaml` above.

## Next Steps

- Review [Installation Guide](INSTALLATION_GUIDE.md)
- Read [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
- Check [FAQ](FAQ.md)
- Explore [Examples](examples.rst)
