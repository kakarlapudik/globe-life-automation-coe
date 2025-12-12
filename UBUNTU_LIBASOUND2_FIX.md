# GitHub Actions Linux Runner Chrome Setup

## Problem
When running Playwright browser automation in GitHub Actions on Ubuntu runners, you may encounter this error:

```
Package libasound2 is a virtual package provided by:libasound2t64 1.2.11-1ubuntu0.1 (= 1.2.11-1ubuntu0.1)
E: Package 'libasound2' has no installation candidate
```

## Root Cause
- Ubuntu 24.04+ replaced `libasound2` with `libasound2t64` as part of the time64 transition
- Playwright's `install-deps` command still tries to install the old `libasound2` package
- This causes the installation to fail when setting up browser dependencies

## Solution Applied (Linux GitHub Actions Only)

### 1. Install Correct Audio Package
Instead of letting Playwright install the virtual package, we explicitly install the actual package:

```bash
sudo apt-get install -y libasound2t64 libasound2-dev
```

### 2. Install Google Chrome (Linux Runners)
We now install Google Chrome directly instead of using Playwright's Chromium:

```bash
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable
```

### 3. Configure Playwright to Use System Chrome
Set the Chrome executable path for Playwright:

```bash
export PLAYWRIGHT_CHROME_EXECUTABLE=$(which google-chrome)
```

### 4. Install Essential Browser Dependencies
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

## Files Updated
- `.github/workflows/linux-chrome-tests.yml`
- `.github/workflows/test-linux-chrome-simple.yml`
- `.github/workflows/test-suite.yml`

## Important: Linux GitHub Actions Runners Only

**This configuration is specifically for GitHub Actions Linux runners (`ubuntu-latest`)**

### For Local Development
- **Windows**: Uses system Chrome if available, otherwise Playwright's Chromium
- **Mac**: Uses system Chrome if available, otherwise Playwright's Chromium  
- **Linux (local)**: Will use system Chrome/Chromium if available

### For GitHub Actions
- **Linux runners**: Now installs and uses Google Chrome directly
- **Windows/Mac runners**: Would use default Playwright setup (not covered here)

## Testing
After applying this fix, your GitHub Actions workflows should:
1. ✅ Install system dependencies successfully
2. ✅ Install Playwright browsers without audio package errors  
3. ✅ Run headless browser tests normally

## Next Steps
1. Commit and push your changes to trigger the GitHub Actions
2. Monitor the workflow runs to confirm the dependency installation succeeds
3. Your tests should now run without the `libasound2` package errors

## Alternative Solutions
If you still encounter issues in GitHub Actions:

1. **Use Docker**: Run tests in a container with pre-installed dependencies
2. **Different Ubuntu version**: Use `runs-on: ubuntu-20.04` instead of `ubuntu-latest`
3. **Skip problematic deps**: Add `|| true` to continue on dependency failures