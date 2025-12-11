# CI/CD Quick Reference

## Quick Start

### GitHub Actions

**Status**: ✅ Configured in `.github/workflows/ci.yml`

**Triggers**:
- Push to `main` or `develop`
- Pull requests to `main` or `develop`
- Release published

**Required Secrets**:
```
TEST_PYPI_API_TOKEN
PYPI_API_TOKEN
```

**View Results**: GitHub → Actions tab

---

### Jenkins

**Status**: ✅ Configured in `Jenkinsfile`

**Triggers**:
- Push to repository
- Pull request created
- Tag pushed

**Required Credentials**:
```
pypi-credentials
test-pypi-credentials
```

**View Results**: Jenkins Dashboard → Your Job

---

### Azure DevOps

**Status**: ✅ Configured in `azure-pipelines.yml`

**Triggers**:
- Push to `main` or `develop`
- Pull requests
- Tag pushed (v*)

**Required Service Connections**:
```
TestPyPI
PyPI
```

**View Results**: Pipelines → Your Pipeline

---

## Test Execution Commands

### Run All Tests
```bash
pytest tests/ -v
```

### Run Unit Tests Only
```bash
pytest tests/ -v --ignore=tests/test_integration.py --ignore=tests/test_e2e.py --ignore=tests/test_performance.py
```

### Run Property-Based Tests
```bash
pytest tests/test_property_*.py -v
```

### Run Integration Tests
```bash
pytest tests/test_integration.py -v
```

### Run E2E Tests
```bash
pytest tests/test_e2e.py -v
```

### Run Performance Tests
```bash
pytest tests/test_performance.py -v
```

### Run with Coverage
```bash
pytest tests/ -v --cov=raptor --cov-report=html
```

### Run in Parallel
```bash
pytest tests/ -v -n auto
```

---

## Pipeline Stages

### All Platforms Execute:

1. ✅ **Linting** - black, flake8
2. ✅ **Type Checking** - mypy
3. ✅ **Unit Tests** - pytest with coverage
4. ✅ **Property Tests** - Hypothesis-based tests
5. ✅ **Integration Tests** - Component integration
6. ✅ **E2E Tests** - Full workflow tests
7. ✅ **Performance Tests** - Benchmarking
8. ✅ **Security Scans** - safety, bandit
9. ✅ **Build** - Create distributions
10. ✅ **Documentation** - Build Sphinx docs
11. ✅ **Publish** - Upload to PyPI

---

## Common Commands

### Local Testing (Before Push)

```bash
# Run linting
black raptor/
flake8 raptor/

# Run type checking
mypy raptor/ --ignore-missing-imports

# Run all tests
pytest tests/ -v --cov=raptor

# Build package
python -m build

# Check distribution
twine check dist/*
```

### Trigger Release

```bash
# Create tag
git tag -a v1.0.0 -m "Release 1.0.0"

# Push tag
git push origin v1.0.0

# Create GitHub release (triggers PyPI publish)
gh release create v1.0.0 --title "v1.0.0" --notes "Release notes"
```

---

## Platform-Specific Features

### GitHub Actions

| Feature | Status |
|---------|--------|
| Multi-OS Testing | ✅ Ubuntu, Windows, macOS |
| Multi-Python Testing | ✅ 3.8, 3.9, 3.10, 3.11 |
| Code Coverage | ✅ Codecov integration |
| Artifact Storage | ✅ Test results, distributions |
| Auto-publish | ✅ TestPyPI (develop), PyPI (release) |

### Jenkins

| Feature | Status |
|---------|--------|
| HTML Reports | ✅ Coverage, test results |
| Email Notifications | ✅ Success/failure emails |
| Manual Approval | ✅ PyPI publish requires approval |
| Artifact Archiving | ✅ All test results |
| Build History | ✅ Last 10 builds retained |

### Azure DevOps

| Feature | Status |
|---------|--------|
| Test Reporting | ✅ Integrated test results |
| Code Coverage | ✅ Built-in coverage reports |
| Deployment Environments | ✅ test-pypi, production-pypi |
| Approval Gates | ✅ Environment approvals |
| Multi-stage Pipeline | ✅ Organized stages |

---

## Troubleshooting

### Tests Failing Locally But Pass in CI

**Check**:
- Python version matches CI
- Dependencies are up to date
- Playwright browsers installed

```bash
python --version
pip install -e ".[dev]"
playwright install chromium firefox webkit
```

### CI Build Timeout

**Solutions**:
- Increase timeout in pipeline config
- Run tests in parallel: `pytest -n auto`
- Skip slow tests: `pytest -m "not slow"`

### PyPI Publish Fails

**Check**:
- API token is valid and not expired
- Package version is unique (not already published)
- Distribution files are valid: `twine check dist/*`

### Coverage Drops Below Threshold

**Solutions**:
- Add tests for new code
- Remove dead code
- Check coverage report: `open htmlcov/index.html`

---

## Quick Links

### Documentation
- [Full CI/CD Guide](CI_CD_INTEGRATION_GUIDE.md)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Jenkins Docs](https://www.jenkins.io/doc/)
- [Azure DevOps Docs](https://docs.microsoft.com/en-us/azure/devops/)

### Test Documentation
- [Unit Tests Guide](../tests/README.md)
- [Property Tests Guide](PROPERTY_TESTS_GUIDE.md)
- [Integration Tests Guide](INTEGRATION_TESTS_QUICK_REFERENCE.md)
- [E2E Tests Guide](E2E_TESTS_GUIDE.md)
- [Performance Tests Guide](PERFORMANCE_QUICK_REFERENCE.md)

### Package Distribution
- [Package Distribution Guide](PACKAGE_DISTRIBUTION_GUIDE.md)
- [PyPI Publishing](https://pypi.org/project/raptor-playwright/)
- [TestPyPI](https://test.pypi.org/project/raptor-playwright/)

---

## Status Dashboard

### Current Build Status

| Platform | Status | Last Run | Coverage |
|----------|--------|----------|----------|
| GitHub Actions | ![CI](https://github.com/your-org/raptor-playwright/workflows/CI/badge.svg) | - | [![codecov](https://codecov.io/gh/your-org/raptor-playwright/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/raptor-playwright) |
| Jenkins | - | - | - |
| Azure DevOps | - | - | - |

### Test Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Test Pass Rate | >95% | - |
| Code Coverage | >80% | - |
| Build Time | <30min | - |
| Flaky Tests | <5% | - |

---

## Support

**Issues**: Open an issue in the repository
**Questions**: Check the [FAQ](FAQ.md)
**Documentation**: See [docs/](../docs/)
