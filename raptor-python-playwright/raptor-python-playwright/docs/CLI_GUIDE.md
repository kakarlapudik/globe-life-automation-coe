# RAPTOR CLI Guide

## Overview

The RAPTOR Command-Line Interface (CLI) provides a comprehensive set of commands for test execution, session management, and configuration operations. The CLI is built using Click and provides an intuitive interface for all framework operations.

## Installation

After installing the RAPTOR framework, the CLI is automatically available:

```bash
pip install -e .
```

Verify installation:

```bash
raptor --version
```

## Command Structure

The CLI follows a hierarchical command structure:

```
raptor
├── run          # Execute tests
├── session      # Manage browser sessions
│   ├── list     # List saved sessions
│   ├── save     # Create new session
│   ├── restore  # Restore saved session
│   └── delete   # Delete session
└── config       # Manage configuration
    ├── show     # Display configuration
    ├── set      # Set configuration value
    └── validate # Validate configuration
```

## Global Options

Available for all commands:

- `--verbose, -v`: Enable verbose output
- `--version`: Show version information
- `--help`: Show help message

## Test Execution

### Basic Usage

```bash
# Run all tests
raptor run

# Run specific test file
raptor run tests/test_login.py

# Run tests in specific directory
raptor run tests/smoke/
```

### Browser Options

```bash
# Specify browser
raptor run --browser chromium
raptor run --browser firefox
raptor run --browser webkit

# Run in headless mode
raptor run --headless

# Combine options
raptor run --browser firefox --headless
```

### Environment Configuration

```bash
# Run with specific environment
raptor run --env dev
raptor run --env staging
raptor run --env prod

# Verbose output
raptor run --env prod --verbose
```

### Test Filtering

```bash
# Run tests by marker
raptor run --markers smoke
raptor run --markers "smoke and not slow"
raptor run --markers "integration or regression"

# Run specific test by ID
raptor run --test-id TC-001

# Run specific iteration
raptor run --iteration 2

# Run tests with specific tags
raptor run --tag login --tag authentication
```

### Parallel Execution

```bash
# Run with 4 parallel workers
raptor run --parallel 4

# Auto-detect CPU count
raptor run --parallel auto

# Combine with other options
raptor run --parallel 4 --env staging --headless
```

### Reporting

```bash
# Generate HTML report (default)
raptor run --report html

# Generate JSON report
raptor run --report json

# Generate Allure report
raptor run --report allure

# Specify report directory
raptor run --report html --report-dir custom_reports/
```

### Screenshots and Video

```bash
# Capture screenshots on failure (default)
raptor run --screenshot-on-failure

# Record video
raptor run --video

# Combine both
raptor run --screenshot-on-failure --video
```

### Retry Failed Tests

```bash
# Retry failed tests once
raptor run --retry 1

# Retry failed tests up to 3 times
raptor run --retry 3
```

### Complete Example

```bash
raptor run tests/smoke/ \
  --browser chromium \
  --headless \
  --env staging \
  --parallel 4 \
  --markers smoke \
  --report html \
  --report-dir reports/smoke \
  --screenshot-on-failure \
  --retry 1 \
  --verbose
```

## Session Management

### List Sessions

```bash
# List all saved sessions
raptor session list

# List with detailed information
raptor session list --verbose
```

Output example:
```
Found 2 session(s):

  • auth-session
    Browser: chromium
    Created: 2024-01-15 10:30:00
    Last accessed: 2024-01-15 14:20:00

  • test-session
    Browser: firefox
    Created: 2024-01-14 09:15:00
    Last accessed: 2024-01-15 11:45:00
```

### Save Session

```bash
# Create new session
raptor session save my-session

# Create session with specific browser
raptor session save auth-session --browser firefox

# Create session and navigate to URL
raptor session save login-session --url https://example.com/login

# Create session in headless mode
raptor session save bg-session --headless
```

**Interactive Session Creation:**

When you save a session, the browser remains open for manual interaction:

1. The browser launches
2. Navigate to the URL (if provided)
3. Perform manual actions (login, navigate, etc.)
4. Press Ctrl+C when done
5. Session is saved with current state

### Restore Session

```bash
# Restore saved session
raptor session restore my-session

# Restore and navigate to URL
raptor session restore auth-session --url https://example.com/dashboard

# Restore with verbose output
raptor session restore test-session --verbose
```

The browser will open with the saved state (cookies, storage, etc.).

### Delete Session

```bash
# Delete session (with confirmation)
raptor session delete old-session

# Delete without confirmation
raptor session delete old-session --force
```

## Configuration Management

### Show Configuration

```bash
# Show all configuration for dev environment
raptor config show

# Show configuration for specific environment
raptor config show --env prod

# Show specific configuration key
raptor config show --key browser.timeout

# Show with verbose output
raptor config show --env staging --verbose
```

Output example:
```json
{
  "browser": {
    "type": "chromium",
    "headless": false,
    "timeout": 30000
  },
  "timeouts": {
    "default": 20000,
    "element_wait": 10000,
    "page_load": 30000
  }
}
```

### Set Configuration

```bash
# Set simple value
raptor config set browser.timeout 30000

# Set boolean value
raptor config set browser.headless true

# Set for specific environment
raptor config set browser.timeout 60000 --env prod

# Set complex value (JSON)
raptor config set browser.args '["--disable-gpu", "--no-sandbox"]'
```

### Validate Configuration

```bash
# Validate dev environment
raptor config validate

# Validate specific environment
raptor config validate --env prod

# Validate with verbose output
raptor config validate --env staging --verbose
```

Output example:
```
✓ Configuration is valid for 'dev'!
```

Or if errors exist:
```
✗ Configuration validation failed for 'prod':
  • Missing required key: browser.timeout
  • Invalid timeout value for timeouts.default: -1
```

## Common Workflows

### Development Workflow

```bash
# Run smoke tests locally
raptor run tests/smoke/ --markers smoke --verbose

# Run with specific browser for debugging
raptor run tests/test_login.py --browser firefox --verbose

# Run single test with video recording
raptor run tests/test_checkout.py --video --verbose
```

### CI/CD Workflow

```bash
# Run all tests in headless mode with parallel execution
raptor run \
  --headless \
  --parallel 4 \
  --env staging \
  --report html \
  --report-dir reports/ \
  --screenshot-on-failure \
  --retry 1
```

### Session Reuse Workflow

```bash
# 1. Create authenticated session
raptor session save auth-session --url https://app.example.com/login
# (Manually login in the browser, then Ctrl+C)

# 2. Run tests using the session
raptor run tests/authenticated/ --session auth-session

# 3. List sessions to verify
raptor session list --verbose

# 4. Clean up old sessions
raptor session delete auth-session
```

### Configuration Management Workflow

```bash
# 1. Check current configuration
raptor config show --env prod

# 2. Update timeout for production
raptor config set browser.timeout 60000 --env prod

# 3. Validate changes
raptor config validate --env prod

# 4. Run tests with new configuration
raptor run --env prod
```

## Environment Variables

The CLI respects the following environment variables:

- `RAPTOR_ENV`: Default environment (dev, staging, prod)
- `RAPTOR_BROWSER`: Default browser (chromium, firefox, webkit)
- `RAPTOR_HEADLESS`: Run in headless mode (true, false)
- `RAPTOR_PARALLEL`: Default number of parallel workers
- `RAPTOR_REPORT_DIR`: Default report directory

Example:
```bash
export RAPTOR_ENV=staging
export RAPTOR_BROWSER=firefox
export RAPTOR_HEADLESS=true

raptor run  # Uses environment variables
```

## Exit Codes

The CLI uses standard exit codes:

- `0`: Success (all tests passed)
- `1`: Failure (tests failed or error occurred)
- `2`: Invalid usage (incorrect arguments)
- `130`: Interrupted (Ctrl+C)

## Tips and Best Practices

### 1. Use Markers for Test Organization

```bash
# Define markers in pytest.ini
[pytest]
markers =
    smoke: Quick smoke tests
    regression: Full regression suite
    slow: Slow-running tests

# Run specific test suites
raptor run --markers smoke
raptor run --markers "regression and not slow"
```

### 2. Leverage Parallel Execution

```bash
# Use auto-detection for optimal performance
raptor run --parallel auto

# Or specify based on your CI environment
raptor run --parallel 4
```

### 3. Session Management for Authentication

```bash
# Save time by reusing authenticated sessions
raptor session save prod-auth --url https://prod.example.com
# (Login manually)

# Run tests without re-authenticating
raptor run --session prod-auth
```

### 4. Environment-Specific Configuration

```bash
# Keep separate configs for each environment
raptor config show --env dev > config-dev.json
raptor config show --env prod > config-prod.json

# Validate before deployment
raptor config validate --env prod
```

### 5. Debugging Failed Tests

```bash
# Run with video and verbose output
raptor run tests/test_failing.py \
  --video \
  --verbose \
  --screenshot-on-failure

# Check the reports directory for artifacts
ls -la reports/
```

## Troubleshooting

### Command Not Found

If `raptor` command is not found:

```bash
# Reinstall in editable mode
pip install -e .

# Or use python module syntax
python -m raptor.cli --help
```

### Browser Not Launching

```bash
# Install Playwright browsers
playwright install

# Or install specific browser
playwright install chromium
```

### Configuration Errors

```bash
# Validate configuration
raptor config validate --env dev

# Check configuration file
cat raptor/config/settings.yaml
```

### Session Restore Fails

```bash
# List available sessions
raptor session list --verbose

# Delete corrupted session
raptor session delete problematic-session --force

# Create new session
raptor session save new-session
```

## Advanced Usage

### Custom pytest Arguments

You can pass additional pytest arguments after `--`:

```bash
raptor run tests/ -- --maxfail=1 --tb=short
```

### Integration with CI/CD

**GitHub Actions:**
```yaml
- name: Run RAPTOR Tests
  run: |
    raptor run \
      --headless \
      --parallel 4 \
      --env staging \
      --report html \
      --report-dir ${{ github.workspace }}/reports
```

**Jenkins:**
```groovy
stage('Test') {
    steps {
        sh '''
            raptor run \
              --headless \
              --parallel 4 \
              --env staging \
              --report html \
              --report-dir reports/
        '''
    }
}
```

**Azure DevOps:**
```yaml
- script: |
    raptor run \
      --headless \
      --parallel 4 \
      --env staging \
      --report html \
      --report-dir $(Build.ArtifactStagingDirectory)/reports
  displayName: 'Run RAPTOR Tests'
```

## See Also

- [Test Execution Control Guide](TEST_EXECUTION_CONTROL_GUIDE.md)
- [Configuration Guide](CONFIG_MANAGER_IMPLEMENTATION.md)
- [Session Management Guide](SESSION_MANAGER_IMPLEMENTATION.md)
- [Reporting Guide](TEST_REPORTER_GUIDE.md)
