@echo off
REM Local Selenium Grid Testing - Windows Batch Script
REM Simulates the GitHub Actions selenium-grid-tests.yml workflow

echo ========================================
echo Local Selenium Grid Testing
echo ========================================

REM Set environment variables
set USE_SELENIUM_GRID=true
set SELENIUM_HUB_URL=http://192.168.1.33:4444
set SELENIUM_BROWSER=chrome
set PYTHONHTTPSVERIFY=0

echo Environment Variables Set:
echo   USE_SELENIUM_GRID=%USE_SELENIUM_GRID%
echo   SELENIUM_HUB_URL=%SELENIUM_HUB_URL%
echo   SELENIUM_BROWSER=%SELENIUM_BROWSER%

echo.
echo ========================================
echo Running Local Selenium Grid Tests
echo ========================================

REM Run the local test script
python test_selenium_grid_locally.py

echo.
echo ========================================
echo Local Testing Complete
echo ========================================

pause