# RAPTOR User Guide - Quick Reference

This quick reference helps you find the right documentation for your needs.

## 📚 Documentation Overview

| Document | Purpose | When to Use |
|----------|---------|-------------|
| [Getting Started](getting_started.rst) | Quick setup and first test | Starting with RAPTOR |
| [Installation Guide](INSTALLATION_GUIDE.md) | Detailed installation | Platform-specific setup |
| [Configuration Guide](CONFIGURATION_GUIDE.md) | All configuration options | Customizing RAPTOR |
| [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md) | Problem solutions | When issues occur |
| [FAQ](FAQ.md) | Common questions | Quick answers |
| [User Guide](user_guide.rst) | Comprehensive guide | In-depth learning |
| [API Reference](api_reference.rst) | API documentation | Code reference |
| [Examples](examples.rst) | Code samples | Learning by example |
| [Migration Guide](migration_guide.rst) | Java/Selenium migration | Converting tests |

## 🚀 Quick Start Path

### For New Users

1. **Start Here**: [Getting Started](getting_started.rst)
   - Quick installation
   - First test
   - Basic concepts

2. **Then**: [Installation Guide](INSTALLATION_GUIDE.md)
   - Platform-specific setup
   - Verification
   - Post-installation

3. **Next**: [Configuration Guide](CONFIGURATION_GUIDE.md)
   - Basic configuration
   - Environment setup
   - Best practices

4. **Finally**: [Examples](examples.rst)
   - Working code samples
   - Common patterns
   - Advanced usage

### For Experienced Users

1. **Configuration**: [Configuration Guide](CONFIGURATION_GUIDE.md)
2. **Advanced Features**: [User Guide](user_guide.rst)
3. **API Details**: [API Reference](api_reference.rst)
4. **Optimization**: [Performance Section](user_guide.rst#performance-optimization)

### For Troubleshooting

1. **First**: [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md)
2. **Then**: [FAQ](FAQ.md)
3. **Finally**: Community support

## 🔍 Find Information By Topic

### Installation & Setup

- **Installing RAPTOR**: [Installation Guide](INSTALLATION_GUIDE.md#installation-methods)
- **Installing Browsers**: [Installation Guide](INSTALLATION_GUIDE.md#post-installation-setup)
- **Platform-Specific**: [Installation Guide](INSTALLATION_GUIDE.md#platform-specific-instructions)
- **Verification**: [Installation Guide](INSTALLATION_GUIDE.md#verification)

### Configuration

- **Browser Settings**: [Configuration Guide](CONFIGURATION_GUIDE.md#browser-configuration)
- **Database Setup**: [Configuration Guide](CONFIGURATION_GUIDE.md#database-configuration)
- **Logging**: [Configuration Guide](CONFIGURATION_GUIDE.md#logging-configuration)
- **Reporting**: [Configuration Guide](CONFIGURATION_GUIDE.md#reporting-configuration)
- **Environment Variables**: [Configuration Guide](CONFIGURATION_GUIDE.md#environment-variables)

### Browser & Elements

- **Browser Management**: [User Guide](user_guide.rst#browser-management)
- **Element Location**: [User Guide](user_guide.rst#element-interactions)
- **Locator Strategies**: [User Guide](user_guide.rst#locator-strategies)
- **Waiting**: [User Guide](user_guide.rst#synchronization)
- **Iframes**: [FAQ](FAQ.md#how-do-i-handle-elements-in-iframes)

### Testing

- **Writing Tests**: [Getting Started](getting_started.rst#your-first-test)
- **Page Objects**: [Getting Started](getting_started.rst#using-page-objects)
- **Data-Driven**: [Getting Started](getting_started.rst#data-driven-testing)
- **Running Tests**: [Getting Started](getting_started.rst#running-tests)
- **Parallel Execution**: [FAQ](FAQ.md#how-do-i-run-tests-in-parallel)

### Database

- **Connection Setup**: [Configuration Guide](CONFIGURATION_GUIDE.md#database-configuration)
- **DDDB Integration**: [User Guide](user_guide.rst#data-driven-testing)
- **Connection Issues**: [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#database-issues)
- **Multiple Databases**: [FAQ](FAQ.md#can-i-use-different-databases)

### Session Management

- **Saving Sessions**: [FAQ](FAQ.md#how-do-i-save-a-browser-session)
- **Restoring Sessions**: [FAQ](FAQ.md#how-do-i-restore-a-saved-session)
- **Session Issues**: [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#session-management-issues)
- **Configuration**: [Configuration Guide](CONFIGURATION_GUIDE.md#session-management-configuration)

### Reporting & Debugging

- **HTML Reports**: [FAQ](FAQ.md#how-do-i-generate-html-reports)
- **Screenshots**: [FAQ](FAQ.md#can-i-take-screenshots-during-test-execution)
- **Debug Logging**: [FAQ](FAQ.md#how-do-i-enable-debug-logging)
- **Debugging Tests**: [FAQ](FAQ.md#how-do-i-debug-failing-tests)
- **Video Recording**: [FAQ](FAQ.md#how-do-i-capture-video-recordings)

### Performance

- **Optimization**: [User Guide](user_guide.rst#performance-optimization)
- **Slow Tests**: [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-slow-test-execution)
- **Memory Usage**: [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-high-memory-usage)
- **Best Practices**: [FAQ](FAQ.md#how-can-i-make-my-tests-faster)

### Migration

- **From Java/Selenium**: [Migration Guide](migration_guide.rst)
- **DDFE Compatibility**: [FAQ](FAQ.md#are-ddfe-element-definitions-compatible)
- **Method Mapping**: [Migration Guide](migration_guide.rst#method-mapping)
- **Migration Tools**: [Migration Guide](migration_guide.rst#migration-utilities)

## 🆘 Common Problems

### Installation Issues

| Problem | Solution |
|---------|----------|
| pip install fails | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-pip-install-fails-with-permission-error) |
| Browsers won't install | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-playwright-browsers-fail-to-install) |
| Import errors | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-import-errors-after-installation) |

### Browser Issues

| Problem | Solution |
|---------|----------|
| Browser won't launch | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-browser-fails-to-launch) |
| Browser crashes | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-browser-crashes-during-test-execution) |
| Headless differences | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-headless-mode-behaves-differently-than-headed) |

### Element Issues

| Problem | Solution |
|---------|----------|
| Element not found | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-element-not-found) |
| Element not interactable | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-element-found-but-not-interactable) |
| Stale element | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-stale-element-reference) |

### Timeout Issues

| Problem | Solution |
|---------|----------|
| Tests timing out | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-tests-timing-out) |
| Slow execution | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-slow-test-execution) |

### Database Issues

| Problem | Solution |
|---------|----------|
| Connection fails | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-database-connection-fails) |
| Query fails | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-query-execution-fails) |
| Pool exhausted | [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md#issue-connection-pool-exhausted) |

## 💡 Quick Tips

### Installation
```bash
# Quick install
pip install raptor-playwright
playwright install
```

### Configuration
```yaml
# Minimal config
browser:
  type: chromium
  headless: true
```

### First Test
```python
@pytest.mark.asyncio
async def test_example():
    browser_manager = BrowserManager()
    await browser_manager.launch_browser("chromium")
    page = await browser_manager.create_page()
    await page.goto("https://example.com")
    await browser_manager.close_browser()
```

### Running Tests
```bash
# Run all tests
pytest

# Run in parallel
pytest -n 4

# Generate report
pytest --html=report.html
```

## 📖 Learning Path

### Beginner (Week 1)
- [ ] Read [Getting Started](getting_started.rst)
- [ ] Complete [Installation Guide](INSTALLATION_GUIDE.md)
- [ ] Write first test
- [ ] Configure basic settings

### Intermediate (Week 2-3)
- [ ] Read [User Guide](user_guide.rst)
- [ ] Implement Page Objects
- [ ] Set up data-driven tests
- [ ] Configure reporting

### Advanced (Week 4+)
- [ ] Study [API Reference](api_reference.rst)
- [ ] Implement session management
- [ ] Optimize performance
- [ ] Set up CI/CD integration

## 🔗 External Resources

- **Playwright Documentation**: https://playwright.dev/python/
- **pytest Documentation**: https://docs.pytest.org/
- **GitHub Repository**: https://github.com/your-org/raptor-playwright
- **Community Forum**: https://community.raptor-framework.org
- **Issue Tracker**: https://github.com/your-org/raptor-playwright/issues

## 📞 Getting Help

1. **Check Documentation**: Start with relevant guide above
2. **Search FAQ**: [FAQ](FAQ.md) has 60+ answered questions
3. **Troubleshooting**: [Troubleshooting Guide](TROUBLESHOOTING_GUIDE.md) for specific issues
4. **Community**: Join the community forum
5. **Support**: Contact support@raptor-framework.org

## 🎯 Quick Links

- [Installation](INSTALLATION_GUIDE.md)
- [Configuration](CONFIGURATION_GUIDE.md)
- [Troubleshooting](TROUBLESHOOTING_GUIDE.md)
- [FAQ](FAQ.md)
- [Examples](examples.rst)
- [API Reference](api_reference.rst)

---

**Need something specific?** Use the search function or check the table of contents in each guide.
