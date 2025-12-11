# Selenium Grid Integration Guide

## Overview
The test automation framework now supports both local Playwright execution and remote Selenium Grid execution for distributed testing across multiple machines and browsers.

## Configuration

### Environment Variables
Set these environment variables to enable Selenium Grid mode:

```bash
# Enable Selenium Grid
export USE_SELENIUM_GRID=true

# Set Grid Hub URL (default: http://192.168.1.33:4444)
export SELENIUM_HUB_URL=http://192.168.1.33:4444

# Set Browser (default: chrome)
export SELENIUM_BROWSER=chrome
```

### Windows PowerShell
```powershell
$env:USE_SELENIUM_GRID = "true"
$env:SELENIUM_HUB_URL = "http://192.168.1.33:4444"
$env:SELENIUM_BROWSER = "chrome"
```

## Usage

### Automatic Detection
The automation scripts automatically detect the environment variables and switch between modes:

```bash
# Local Playwright execution (default)
python run_complete_automation.py

# Selenium Grid execution (when environment variables are set)
USE_SELENIUM_GRID=true python run_complete_automation.py
```

### Manual pytest Execution
```bash
# Local Playwright
pytest generated_tests/ -v --html=report.html

# Selenium Grid
USE_SELENIUM_GRID=true pytest generated_tests/ -v --html=report.html --confcutdir=. -p conftest_selenium_grid
```

## Selenium Grid Setup

### Hub Configuration
Ensure your Selenium Grid hub is running at the specified URL:
- Default: `http://192.168.1.33:4444`
- Grid console: `http://192.168.1.33:4444/grid/console`

### Node Requirements
Grid nodes should have:
- Chrome/Firefox browsers installed
- Appropriate WebDriver versions
- Network connectivity to hub

## Features

### Parallel Execution
- Works with both Playwright and Selenium Grid
- Automatic worker distribution across grid nodes
- Dynamic load balancing with worksteal

### Browser Support
- **Chrome**: Default browser for grid execution
- **Firefox**: Alternative browser option
- **Edge**: Can be configured via capabilities

### Reporting
- Same HTML reporting for both modes
- Screenshots captured on test failures
- Grid execution details in reports

## Configuration Files

### conftest_selenium_grid.py
- Selenium-specific pytest configuration
- WebDriver setup and teardown
- Grid connection management
- Screenshot capture for failures

### pytest.ini
- Environment variable documentation
- Parallel execution settings
- Logging configuration

## Troubleshooting

### Connection Issues
```bash
# Test grid connectivity
curl http://192.168.1.33:4444/wd/hub/status

# Check grid console
open http://192.168.1.33:4444/grid/console
```

### Browser Compatibility
- Ensure grid nodes have required browser versions
- Update WebDriver versions if needed
- Check browser capabilities in grid console

### Network Configuration
- Verify firewall settings allow grid communication
- Ensure hub and nodes are on same network
- Check port 4444 accessibility

## Performance Comparison

| Mode | Execution Speed | Resource Usage | Scalability |
|------|----------------|----------------|-------------|
| Local Playwright | Fast | High (local CPU) | Limited to local cores |
| Selenium Grid | Variable | Distributed | High (multiple machines) |

## Best Practices

1. **Use Grid for Large Test Suites**: Distribute load across multiple machines
2. **Local for Development**: Use Playwright for faster local development
3. **Monitor Grid Health**: Check node availability before test runs
4. **Browser Consistency**: Use same browser versions across grid nodes
5. **Network Stability**: Ensure reliable network connection to grid

## Migration Guide

### From Playwright to Grid
1. Set environment variables
2. No code changes required
3. Run same automation scripts

### From Grid to Playwright
1. Unset environment variables
2. Scripts automatically use Playwright
3. Faster local execution

## Example Configurations

### CI/CD Pipeline
```yaml
# GitHub Actions with Selenium Grid
env:
  USE_SELENIUM_GRID: true
  SELENIUM_HUB_URL: http://selenium-hub:4444
  SELENIUM_BROWSER: chrome
```

### Local Development
```bash
# Quick local testing
unset USE_SELENIUM_GRID
python run_complete_automation.py
```

### Production Testing
```bash
# Distributed grid testing
export USE_SELENIUM_GRID=true
export SELENIUM_HUB_URL=http://prod-grid:4444
python run_complete_automation.py
```