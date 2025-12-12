#!/bin/bash
# Local Selenium Grid Testing - Unix/Linux Shell Script
# Simulates the GitHub Actions selenium-grid-tests.yml workflow

echo "========================================"
echo "Local Selenium Grid Testing"
echo "========================================"

# Set environment variables
export USE_SELENIUM_GRID=true
export SELENIUM_HUB_URL=http://192.168.1.33:4444
export SELENIUM_BROWSER=chrome
export PYTHONHTTPSVERIFY=0

echo "Environment Variables Set:"
echo "  USE_SELENIUM_GRID=$USE_SELENIUM_GRID"
echo "  SELENIUM_HUB_URL=$SELENIUM_HUB_URL"
echo "  SELENIUM_BROWSER=$SELENIUM_BROWSER"

echo ""
echo "========================================"
echo "Running Local Selenium Grid Tests"
echo "========================================"

# Run the local test script
python test_selenium_grid_locally.py

echo ""
echo "========================================"
echo "Local Testing Complete"
echo "========================================"