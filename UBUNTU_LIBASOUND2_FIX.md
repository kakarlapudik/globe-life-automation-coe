# Ubuntu libasound2 Package Fix

## Problem
When running Playwright browser automation on Ubuntu (especially in GitHub Actions), you may encounter this error:

```
Package libasound2 is a virtual package provided by:libasound2t64 1.2.11-1ubuntu0.1 (= 1.2.11-1ubuntu0.1)
E: Package 'libasound2' has no installation candidate
```

## Root Cause
- Ubuntu 24.04+ replaced `libasound2` with `libasound2t64` as part of the time64 transition
- Playwright's `install-deps` command still tries to install the old `libasound2` package
- This causes the installation to fail when setting up browser dependencies

## Solution Applied

### 1. Install Correct Audio Package
Instead of letting Playwright install the virtual package, we explicitly install the actual package:

```bash
sudo apt-get install -y libasound2t64 libasound2-dev
```

### 2. Install Essential Browser Dependencies
We also install other common dependencies that browsers need:

```bash
sudo apt-get install -y \
  libatk-bridge2.0-0 \
  libdrm2 \
  libxkbcommon0 \
  libxrandr2 \
  libxss1 \
  libgtk-3-0 \
  libxshmfence1 \
  libgbm1
```

### 3. Graceful Fallback
We allow `playwright install-deps` to continue even if some packages fail:

```bash
playwright install-deps chromium || echo "⚠️ Some deps failed but continuing..."
```

## Files Updated
- `.github/workflows/linux-chrome-tests.yml`
- `.github/workflows/test-linux-chrome-simple.yml`
- `.github/workflows/test-suite.yml`

## Testing
After applying this fix, your GitHub Actions workflows should:
1. ✅ Install system dependencies successfully
2. ✅ Install Playwright browsers without audio package errors
3. ✅ Run headless browser tests normally

## Alternative Solutions
If you still encounter issues, you can also:

1. **Use Docker**: Run tests in a container with pre-installed dependencies
2. **Skip audio deps**: Use `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1` and install manually
3. **Use different runner**: Switch to a different Ubuntu version if needed

## Verification
To verify the fix works, check that:
- `libasound2t64` is installed: `dpkg -l | grep libasound`
- Playwright can launch browsers: `playwright --version`
- Tests run without dependency errors