# Post-Build Selenium Grid Testing Guide

## Overview
Automated post-build testing workflow that triggers Selenium Grid tests after successful completion of main test suites. This ensures comprehensive testing across distributed browser environments.

## Workflow Triggers

### 1. Automatic Post-Build Trigger
```yaml
workflow_run:
  workflows: ["Test Suite", "Comprehensive Test Suite"]
  types: [completed]
  branches: [main, develop, feature/*]
```

**When it runs:**
- After "Test Suite" workflow completes successfully
- After "Comprehensive Test Suite" workflow completes successfully
- Only on specified branches (main, develop, feature/*)

### 2. Manual Dispatch
```yaml
workflow_dispatch:
  inputs:
    grid_hub_url: 'http://192.168.1.33:4444'
    test_target: 'homepage-links'
    browser_matrix: 'chrome'
    parallel_execution: true
```

**Manual trigger options:**
- Custom grid hub URL
- Specific test targets
- Browser selection (chrome, firefox, both)
- Parallel execution control

### 3. Scheduled Execution
```yaml
schedule:
  - cron: '0 6 * * *'  # Daily at 6 AM UTC
```

## Test Targets

### Homepage Links (`homepage-links`)
- Validates all links on Globe Life investor relations homepage
- Uses Selenium Grid for cross-browser testing
- Generates detailed link validation reports

### Full Automation Suite (`full-automation-suite`)
- Runs complete automation workflow on Selenium Grid
- Includes all generated test cases
- Comprehensive end-to-end validation

### Selenium Grid Validation (`selenium-grid-validation`)
- Tests Selenium Grid connectivity and functionality
- Validates browser capabilities
- Grid health check and performance testing

### All Tests (`all-tests`)
- Combines Selenium Grid tests with generated test suite
- Maximum coverage across all test scenarios
- Parallel execution across multiple browsers

## Grid Configuration

### Default Settings
```bash
SELENIUM_HUB_URL=http://192.168.1.33:4444
USE_SELENIUM_GRID=true
PYTHONHTTPSVERIFY=0
```

### Browser Matrix
- **Chrome**: Default browser for grid testing
- **Firefox**: Alternative browser option
- **Both**: Runs tests on both browsers in parallel

### Parallel Execution
- Configurable parallel workers (default: 2)
- Dynamic load balancing with worksteal
- Optimized for grid resource utilization

## Workflow Jobs

### 1. Preflight Checks (`preflight`)
**Purpose:** Validate grid availability before test execution

**Checks:**
- Grid hub accessibility
- Grid status and readiness
- Browser matrix configuration
- Network connectivity

**Outputs:**
- `grid-available`: Boolean indicating grid status
- `browsers`: JSON array of browsers to test

### 2. Selenium Grid Tests (`selenium-grid-tests`)
**Purpose:** Execute tests on Selenium Grid

**Features:**
- Multi-browser testing (Chrome, Firefox)
- Parallel execution support
- Comprehensive error handling
- Detailed reporting and artifacts

**Matrix Strategy:**
```yaml
strategy:
  matrix:
    browser: ['chrome', 'firefox']
    python-version: ['3.11']
  fail-fast: false
  max-parallel: 2
```

### 3. Results Summary (`results-summary`)
**Purpose:** Consolidate results and generate final report

**Outputs:**
- Test execution summary
- Grid status information
- Performance metrics
- Artifact links

### 4. Grid Unavailable Handler (`grid-unavailable`)
**Purpose:** Handle scenarios when grid is not accessible

**Actions:**
- Skip test execution gracefully
- Provide troubleshooting guidance
- Generate informative summary

## Artifacts and Reports

### Test Reports
- **HTML Reports**: Interactive test results with screenshots
- **JSON Reports**: Structured data for programmatic analysis
- **JUnit XML**: CI/CD integration and test result parsing

### Screenshots
- **Success Screenshots**: Documentation of successful test runs
- **Failure Screenshots**: Debug information for failed tests
- **Grid Console Screenshots**: Grid status and configuration

### Retention Policy
- **Test Reports**: 30 days retention
- **Screenshots**: 7 days retention for failures
- **Logs**: Available in workflow run details

## Connectivity Testing

### Grid Connectivity Script
```bash
python test_selenium_grid_connectivity.py
```

**Tests:**
- Grid hub status and readiness
- Browser session creation
- Basic navigation functionality
- Grid information retrieval

### Manual Grid Verification
```bash
# Check grid status
curl http://192.168.1.33:4444/wd/hub/status

# View grid console
open http://192.168.1.33:4444/grid/console

# Test connectivity
python test_selenium_grid_connectivity.py
```

## Troubleshooting

### Common Issues

#### Grid Not Available
**Symptoms:**
- Workflow skips test execution
- "Grid Unavailable" message in summary

**Solutions:**
1. Verify grid hub is running
2. Check network connectivity
3. Validate firewall settings
4. Confirm grid hub URL

#### Browser Session Failures
**Symptoms:**
- Tests fail during browser initialization
- WebDriver connection errors

**Solutions:**
1. Check grid node availability
2. Verify browser versions on nodes
3. Review grid node logs
4. Restart grid nodes if needed

#### Test Execution Timeouts
**Symptoms:**
- Tests timeout during execution
- Incomplete test results

**Solutions:**
1. Increase test timeouts
2. Check grid node resources
3. Reduce parallel execution
4. Optimize test scenarios

### Debugging Commands

```bash
# Check grid status
curl -f http://192.168.1.33:4444/wd/hub/status

# List active sessions
curl http://192.168.1.33:4444/wd/hub/sessions

# View grid configuration
curl http://192.168.1.33:4444/grid/api/hub

# Test browser capabilities
python -c "
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
options = Options()
options.add_argument('--headless')
driver = webdriver.Remote('http://192.168.1.33:4444/wd/hub', options=options)
print(driver.capabilities)
driver.quit()
"
```

## Performance Optimization

### Grid Configuration
- **Node Resources**: Ensure adequate CPU and memory
- **Browser Instances**: Limit concurrent sessions per node
- **Network Bandwidth**: Optimize for test data transfer

### Test Optimization
- **Parallel Execution**: Balance workers with grid capacity
- **Test Isolation**: Ensure tests don't interfere with each other
- **Resource Cleanup**: Proper session termination

### Monitoring
- **Grid Console**: Monitor node status and utilization
- **Test Metrics**: Track execution times and success rates
- **Resource Usage**: Monitor CPU, memory, and network

## Integration Examples

### GitHub Actions Integration
```yaml
# Trigger from another workflow
- name: Trigger Selenium Grid Tests
  uses: ./.github/workflows/post-build-selenium-grid.yml
  with:
    test_target: 'all-tests'
    browser_matrix: 'both'
```

### Local Development
```bash
# Run grid tests locally
export USE_SELENIUM_GRID=true
export SELENIUM_HUB_URL=http://192.168.1.33:4444
python run_complete_automation.py
```

### CI/CD Pipeline Integration
```yaml
# Add to existing pipeline
jobs:
  selenium-grid:
    needs: [build, test]
    uses: ./.github/workflows/post-build-selenium-grid.yml
    secrets: inherit
```

## Best Practices

1. **Grid Maintenance**: Regular grid health checks and updates
2. **Test Stability**: Ensure tests are reliable across browsers
3. **Resource Management**: Monitor and optimize grid resource usage
4. **Error Handling**: Implement robust error handling and recovery
5. **Documentation**: Keep grid configuration and procedures documented
6. **Monitoring**: Set up alerts for grid availability and test failures

## Security Considerations

- **Network Access**: Secure grid hub access with appropriate firewall rules
- **Authentication**: Implement grid authentication if required
- **Data Privacy**: Ensure test data doesn't contain sensitive information
- **Resource Limits**: Prevent resource exhaustion attacks on grid nodes