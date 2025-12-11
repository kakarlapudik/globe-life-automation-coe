# RAPTOR CLI Quick Reference

## Installation

```bash
pip install -e .
raptor --version
```

## Test Execution

```bash
# Basic
raptor run                                    # Run all tests
raptor run tests/test_login.py               # Run specific file
raptor run tests/smoke/                      # Run directory

# Browser
raptor run --browser chromium                # Chromium (default)
raptor run --browser firefox                 # Firefox
raptor run --browser webkit                  # WebKit
raptor run --headless                        # Headless mode

# Environment
raptor run --env dev                         # Dev (default)
raptor run --env staging                     # Staging
raptor run --env prod                        # Production

# Filtering
raptor run --markers smoke                   # By marker
raptor run --test-id TC-001                  # By test ID
raptor run --iteration 2                     # By iteration
raptor run --tag login                       # By tag

# Parallel
raptor run --parallel 4                      # 4 workers
raptor run --parallel auto                   # Auto-detect CPUs

# Reporting
raptor run --report html                     # HTML report (default)
raptor run --report json                     # JSON report
raptor run --report allure                   # Allure report
raptor run --report-dir custom/              # Custom directory

# Other
raptor run --screenshot-on-failure           # Screenshots (default)
raptor run --video                           # Record video
raptor run --retry 3                         # Retry failed tests
raptor run --verbose                         # Verbose output
```

## Session Management

```bash
# List
raptor session list                          # List all sessions
raptor session list --verbose                # Detailed info

# Save
raptor session save my-session               # Create session
raptor session save auth --url https://...   # With URL
raptor session save test --browser firefox   # Specific browser

# Restore
raptor session restore my-session            # Restore session
raptor session restore auth --url https://...# Restore + navigate

# Delete
raptor session delete old-session            # Delete (with confirm)
raptor session delete old-session --force    # Delete (no confirm)
```

## Configuration

```bash
# Show
raptor config show                           # Show all (dev)
raptor config show --env prod                # Show for environment
raptor config show --key browser.timeout     # Show specific key

# Set
raptor config set browser.timeout 30000      # Set value
raptor config set browser.headless true      # Set boolean
raptor config set key value --env prod       # Set for environment

# Validate
raptor config validate                       # Validate dev
raptor config validate --env prod            # Validate environment
```

## Common Commands

```bash
# Development
raptor run --markers smoke --verbose
raptor run tests/test_login.py --browser firefox --verbose

# CI/CD
raptor run --headless --parallel 4 --env staging --report html

# Debugging
raptor run tests/failing.py --video --verbose --screenshot-on-failure

# Session Workflow
raptor session save auth --url https://app.example.com/login
raptor run tests/authenticated/ --session auth
raptor session delete auth
```

## Options Summary

### Global Options
- `--verbose, -v`: Verbose output
- `--version`: Show version
- `--help`: Show help

### Run Command Options
- `--browser, -b`: Browser type (chromium, firefox, webkit)
- `--headless`: Headless mode
- `--env, -e`: Environment (dev, staging, prod)
- `--parallel, -n`: Parallel workers
- `--markers, -m`: Pytest markers
- `--test-id`: Specific test ID
- `--iteration`: Specific iteration
- `--tag`: Test tags (multiple)
- `--report`: Report format (html, json, allure)
- `--report-dir`: Report directory
- `--screenshot-on-failure`: Capture screenshots
- `--video`: Record video
- `--retry`: Retry count

### Session Command Options
- `--verbose, -v`: Detailed info (list)
- `--browser, -b`: Browser type (save)
- `--headless`: Headless mode (save)
- `--url`: Navigate to URL (save, restore)
- `--force, -f`: Skip confirmation (delete)

### Config Command Options
- `--env, -e`: Environment
- `--key`: Configuration key (show)

## Exit Codes

- `0`: Success
- `1`: Failure
- `2`: Invalid usage
- `130`: Interrupted

## Environment Variables

```bash
export RAPTOR_ENV=staging
export RAPTOR_BROWSER=firefox
export RAPTOR_HEADLESS=true
export RAPTOR_PARALLEL=4
export RAPTOR_REPORT_DIR=reports/
```

## Examples

### Run smoke tests in staging
```bash
raptor run --markers smoke --env staging --headless
```

### Run with parallel execution and retries
```bash
raptor run --parallel 4 --retry 2 --report html
```

### Create and use authenticated session
```bash
raptor session save auth --url https://app.example.com
raptor run tests/authenticated/ --session auth
```

### Validate production configuration
```bash
raptor config validate --env prod
```

### Run specific test with video
```bash
raptor run tests/test_checkout.py --video --verbose
```

## Tips

1. Use `--verbose` for debugging
2. Use `--parallel auto` for optimal performance
3. Save sessions for authenticated tests
4. Validate config before deployment
5. Use markers for test organization
6. Check exit codes in CI/CD scripts

## See Also

- [Full CLI Guide](CLI_GUIDE.md)
- [Test Execution Control](TEST_EXECUTION_CONTROL_GUIDE.md)
- [Configuration Management](CONFIG_MANAGER_IMPLEMENTATION.md)
- [Session Management](SESSION_MANAGER_IMPLEMENTATION.md)
