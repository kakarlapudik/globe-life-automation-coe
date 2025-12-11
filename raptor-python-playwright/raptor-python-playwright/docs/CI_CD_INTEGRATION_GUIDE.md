# CI/CD Integration Guide

## Overview

The RAPTOR Python Playwright Framework includes comprehensive CI/CD pipeline configurations for three major platforms:

1. **GitHub Actions** - Cloud-based CI/CD for GitHub repositories
2. **Jenkins** - Self-hosted CI/CD automation server
3. **Azure DevOps** - Microsoft's cloud-based DevOps platform

All pipelines are configured to run automated tests, perform security scans, build distributions, and publish to PyPI.

## GitHub Actions

### Configuration File

Location: `.github/workflows/ci.yml`

### Features

- **Multi-platform testing**: Tests run on Ubuntu, Windows, and macOS
- **Multi-version Python**: Tests against Python 3.8, 3.9, 3.10, and 3.11
- **Automated testing**: Unit tests, property-based tests, integration tests, E2E tests
- **Code coverage**: Uploads coverage reports to Codecov
- **Security scanning**: Runs safety and bandit security checks
- **Documentation**: Builds Sphinx documentation
- **Package publishing**: Publishes to TestPyPI (develop branch) and PyPI (releases)

### Triggers

- **Push**: Triggers on pushes to `main` and `develop` branches
- **Pull Request**: Triggers on PRs to `main` and `develop` branches
- **Release**: Triggers when a new release is published

### Required Secrets

Configure these secrets in your GitHub repository settings:

```
TEST_PYPI_API_TOKEN  # Token for TestPyPI publishing
PYPI_API_TOKEN       # Token for PyPI publishing
```

### Workflow Jobs

1. **test**: Runs on matrix of OS and Python versions
   - Checkout code
   - Install dependencies
   - Run linting (black, flake8)
   - Run type checking (mypy)
   - Run unit tests with coverage
   - Run property-based tests
   - Upload coverage to Codecov

2. **integration-test**: Runs integration and E2E tests
   - Installs all browsers (Chromium, Firefox, WebKit)
   - Runs integration tests
   - Runs E2E tests

3. **performance-test**: Runs performance benchmarks
   - Measures framework initialization time
   - Measures element location performance
   - Archives performance results

4. **build**: Builds distribution packages
   - Creates wheel and source distributions
   - Validates distributions with twine
   - Tests installation from wheel

5. **publish-test-pypi**: Publishes to TestPyPI (develop branch only)

6. **publish-pypi**: Publishes to PyPI (releases only)

7. **documentation**: Builds Sphinx documentation

8. **security-scan**: Runs security checks
   - Safety check for vulnerable dependencies
   - Bandit scan for security issues in code

### Usage

The pipeline runs automatically on push and PR events. No manual intervention required.

To trigger a release:
```bash
# Create and push a tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Create a GitHub release from the tag
# This will trigger the publish-pypi job
```

## Jenkins

### Configuration File

Location: `Jenkinsfile`

### Features

- **Declarative pipeline**: Easy to read and maintain
- **Comprehensive testing**: All test types included
- **Security scanning**: Integrated safety and bandit checks
- **Build artifacts**: Archives test results, coverage, and distributions
- **Email notifications**: Sends build status emails
- **Manual approval**: Requires approval before PyPI publishing

### Prerequisites

1. **Jenkins Plugins Required**:
   - Pipeline
   - Git
   - HTML Publisher
   - JUnit
   - Email Extension

2. **Jenkins Credentials**:
   - `pypi-credentials`: PyPI API token
   - `test-pypi-credentials`: TestPyPI API token

3. **System Requirements**:
   - Python 3.10 installed on Jenkins agent
   - Playwright browsers installed

### Pipeline Stages

1. **Setup**: Creates virtual environment and installs dependencies
2. **Lint**: Runs code quality checks
3. **Unit Tests**: Runs unit tests with coverage
4. **Property-Based Tests**: Runs property tests
5. **Integration Tests**: Runs integration tests
6. **E2E Tests**: Runs end-to-end tests
7. **Performance Tests**: Runs performance benchmarks
8. **Security Scan**: Runs security checks
9. **Build Distribution**: Builds wheel and source distributions
10. **Test Installation**: Verifies package installation
11. **Publish to TestPyPI**: Publishes to TestPyPI (develop branch)
12. **Publish to PyPI**: Publishes to PyPI (tags only, requires approval)
13. **Build Documentation**: Builds Sphinx documentation

### Configuration

1. **Create Jenkins Pipeline Job**:
   ```
   New Item → Pipeline → OK
   ```

2. **Configure Pipeline**:
   - Definition: Pipeline script from SCM
   - SCM: Git
   - Repository URL: Your repository URL
   - Script Path: Jenkinsfile

3. **Configure Credentials**:
   ```
   Manage Jenkins → Manage Credentials → Add Credentials
   Kind: Secret text
   ID: pypi-credentials
   Secret: Your PyPI API token
   ```

4. **Configure Email Notifications**:
   ```
   Manage Jenkins → Configure System → Extended E-mail Notification
   ```

### Usage

The pipeline runs automatically when:
- Code is pushed to the repository
- A pull request is created
- A tag is pushed

To manually trigger:
```
Jenkins Dashboard → Your Job → Build Now
```

## Azure DevOps

### Configuration File

Location: `azure-pipelines.yml`

### Features

- **Multi-stage pipeline**: Organized into logical stages
- **Matrix testing**: Tests across multiple OS and Python versions
- **Test result publishing**: Integrates with Azure DevOps test reporting
- **Code coverage**: Publishes coverage reports
- **Deployment environments**: Uses Azure DevOps environments for approvals
- **Artifact management**: Stores build artifacts

### Prerequisites

1. **Azure DevOps Project**: Create a project in Azure DevOps

2. **Service Connections**:
   - Create service connections for TestPyPI and PyPI
   - Go to: Project Settings → Service connections → New service connection
   - Type: Python package upload
   - Connection name: `TestPyPI` and `PyPI`

3. **Environments**:
   - Create environments for deployment approvals
   - Go to: Pipelines → Environments → New environment
   - Names: `test-pypi` and `production-pypi`

### Pipeline Stages

1. **Test**: Runs tests on matrix of platforms
   - Linux (Python 3.8, 3.9, 3.10, 3.11)
   - Windows (Python 3.10)
   - macOS (Python 3.10)

2. **IntegrationTest**: Runs integration and E2E tests

3. **PerformanceTest**: Runs performance benchmarks

4. **SecurityScan**: Runs security checks

5. **Build**: Builds distribution packages

6. **Documentation**: Builds Sphinx documentation

7. **PublishTestPyPI**: Publishes to TestPyPI (develop branch)

8. **PublishPyPI**: Publishes to PyPI (tags only)

### Configuration

1. **Create Pipeline**:
   ```
   Pipelines → New pipeline → Azure Repos Git → Select repository
   → Existing Azure Pipelines YAML file → Select azure-pipelines.yml
   ```

2. **Configure Service Connections**:
   ```
   Project Settings → Service connections → New service connection
   → Python package upload (Twine)
   
   For TestPyPI:
   - Connection name: TestPyPI
   - Repository URL: https://test.pypi.org/legacy/
   - Username: __token__
   - Password: Your TestPyPI API token
   
   For PyPI:
   - Connection name: PyPI
   - Repository URL: https://upload.pypi.org/legacy/
   - Username: __token__
   - Password: Your PyPI API token
   ```

3. **Configure Environments**:
   ```
   Pipelines → Environments → New environment
   
   Create two environments:
   - test-pypi (for TestPyPI deployments)
   - production-pypi (for PyPI deployments)
   
   Add approvals if desired:
   Environment → Approvals and checks → Approvals
   ```

### Usage

The pipeline runs automatically when:
- Code is pushed to main or develop branches
- A pull request is created
- A tag is pushed

To manually trigger:
```
Pipelines → Your Pipeline → Run pipeline
```

## Automated Test Execution

All three CI/CD platforms execute the following test suites automatically:

### 1. Unit Tests

```bash
pytest tests/ -v --cov=raptor --cov-report=xml --cov-report=html
```

- Tests all core framework components
- Generates code coverage reports
- Fails if coverage drops below threshold

### 2. Property-Based Tests

```bash
pytest tests/test_property_*.py -v
```

- Runs all 12 correctness properties
- Each property runs 100+ iterations
- Tests edge cases and invariants

### 3. Integration Tests

```bash
pytest tests/test_integration.py -v
```

- Tests component interactions
- Verifies browser + element manager integration
- Tests database + configuration integration

### 4. End-to-End Tests

```bash
pytest tests/test_e2e.py -v
```

- Tests complete workflows
- Verifies login flow
- Tests data-driven execution
- Tests multi-page navigation

### 5. Performance Tests

```bash
pytest tests/test_performance.py -v
```

- Measures framework initialization time
- Measures element location performance
- Compares against baseline metrics

### 6. Security Scans

```bash
safety check --json
bandit -r raptor/ -f json
```

- Checks for vulnerable dependencies
- Scans code for security issues

## Test Failure Handling

### GitHub Actions

- Failed tests are reported in the Actions tab
- Test results are uploaded as artifacts
- Coverage reports are uploaded to Codecov
- PR checks fail if tests fail

### Jenkins

- Failed tests are reported in the build console
- JUnit test results are published
- HTML coverage reports are published
- Email notifications sent on failure

### Azure DevOps

- Failed tests are reported in the Tests tab
- Test results are published to Azure DevOps
- Coverage reports are published
- Build status is updated

## Best Practices

### 1. Branch Protection

Configure branch protection rules:

**GitHub**:
```
Settings → Branches → Add rule
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Include administrators
```

**Azure DevOps**:
```
Repos → Branches → main → Branch policies
- Require a minimum number of reviewers
- Check for linked work items
- Build validation (select your pipeline)
```

### 2. Test Coverage Requirements

Set minimum coverage thresholds:

```yaml
# pytest.ini or pyproject.toml
[tool:pytest]
addopts = --cov=raptor --cov-fail-under=80
```

### 3. Parallel Test Execution

Enable parallel testing for faster builds:

```yaml
# GitHub Actions
- name: Run tests
  run: pytest -n auto

# Jenkins
sh 'pytest -n auto'

# Azure DevOps
- script: pytest -n auto
```

### 4. Caching Dependencies

Cache dependencies to speed up builds:

**GitHub Actions**:
```yaml
- uses: actions/setup-python@v4
  with:
    cache: 'pip'
```

**Azure DevOps**:
```yaml
- task: Cache@2
  inputs:
    key: 'python | "$(Agent.OS)" | requirements.txt'
    path: $(PIP_CACHE_DIR)
```

### 5. Artifact Retention

Configure artifact retention policies:

- Keep test results for 30 days
- Keep distributions for 90 days
- Keep coverage reports for 30 days

## Troubleshooting

### Common Issues

#### 1. Playwright Installation Fails

**Solution**: Ensure Playwright browsers are installed:
```bash
playwright install chromium firefox webkit
```

#### 2. Tests Timeout

**Solution**: Increase timeout in pipeline configuration:
```yaml
timeout: time: 2, unit: 'HOURS'  # Jenkins
timeout-minutes: 120              # GitHub Actions
timeoutInMinutes: 120             # Azure DevOps
```

#### 3. PyPI Publishing Fails

**Solution**: Verify API tokens are correctly configured:
- Check token has upload permissions
- Verify token is not expired
- Ensure package name is available

#### 4. Coverage Upload Fails

**Solution**: Check Codecov token:
```yaml
- uses: codecov/codecov-action@v3
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
```

### Debug Mode

Enable debug logging:

**GitHub Actions**:
```yaml
- name: Run tests
  run: pytest -vv --log-cli-level=DEBUG
```

**Jenkins**:
```groovy
sh 'pytest -vv --log-cli-level=DEBUG'
```

**Azure DevOps**:
```yaml
- script: pytest -vv --log-cli-level=DEBUG
```

## Monitoring and Metrics

### Key Metrics to Track

1. **Build Success Rate**: Percentage of successful builds
2. **Test Pass Rate**: Percentage of passing tests
3. **Code Coverage**: Percentage of code covered by tests
4. **Build Duration**: Time taken for complete pipeline
5. **Deployment Frequency**: How often releases are deployed

### Dashboards

**GitHub Actions**:
- View in Actions tab
- Use GitHub Insights for metrics

**Jenkins**:
- Use Blue Ocean for visual pipeline view
- Install Dashboard View plugin

**Azure DevOps**:
- Use built-in Analytics
- Create custom dashboards

## Security Considerations

### 1. Secret Management

- Never commit secrets to repository
- Use platform-specific secret management
- Rotate secrets regularly

### 2. Dependency Scanning

- Run safety check on every build
- Update vulnerable dependencies promptly
- Use Dependabot/Renovate for automated updates

### 3. Code Scanning

- Run bandit on every build
- Address high-severity issues immediately
- Configure custom bandit rules if needed

### 4. Access Control

- Limit who can approve deployments
- Use environment protection rules
- Enable audit logging

## Continuous Improvement

### 1. Pipeline Optimization

- Identify slow stages
- Parallelize independent stages
- Cache dependencies
- Use faster runners when available

### 2. Test Optimization

- Remove redundant tests
- Parallelize test execution
- Use test markers for selective execution
- Profile slow tests

### 3. Feedback Loop

- Monitor build times
- Track test flakiness
- Collect team feedback
- Iterate on improvements

## Support

For issues with CI/CD pipelines:

1. Check pipeline logs for error messages
2. Review this documentation
3. Check platform-specific documentation:
   - [GitHub Actions Docs](https://docs.github.com/en/actions)
   - [Jenkins Docs](https://www.jenkins.io/doc/)
   - [Azure DevOps Docs](https://docs.microsoft.com/en-us/azure/devops/)
4. Open an issue in the repository

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Azure Pipelines Documentation](https://docs.microsoft.com/en-us/azure/devops/pipelines/)
- [pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/python/)
