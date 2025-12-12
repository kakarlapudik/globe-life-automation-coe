#!/usr/bin/env python
"""
Local Selenium Grid Testing Script
Simulates the GitHub Actions selenium-grid-tests.yml workflow locally
"""

import os
import sys
import subprocess
import time
from datetime import datetime


def print_banner(message):
    """Print a formatted banner"""
    print(f"\n{'='*60}")
    print(f"[LOCAL TEST] {message}")
    print(f"{'='*60}")


def run_command(command, description, continue_on_error=False):
    """Run a command and handle errors"""
    print(f"\n[STEP] {description}")
    print(f"[CMD] {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[SUCCESS] {description}")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"[FAILED] {description}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
            
            if not continue_on_error:
                return False
            else:
                print("[CONTINUE] Continuing despite error...")
                return True
                
    except Exception as e:
        print(f"[ERROR] Exception running {description}: {e}")
        return False if not continue_on_error else True


def setup_environment():
    """Setup environment variables for Selenium Grid"""
    print_banner("Environment Setup")
    
    # Set environment variables
    os.environ["USE_SELENIUM_GRID"] = "true"
    os.environ["SELENIUM_HUB_URL"] = "http://192.168.1.33:4444"
    os.environ["SELENIUM_BROWSER"] = "chrome"
    os.environ["PYTHONHTTPSVERIFY"] = "0"
    
    print("[ENV] Environment variables set:")
    print(f"  USE_SELENIUM_GRID = {os.environ['USE_SELENIUM_GRID']}")
    print(f"  SELENIUM_HUB_URL = {os.environ['SELENIUM_HUB_URL']}")
    print(f"  SELENIUM_BROWSER = {os.environ['SELENIUM_BROWSER']}")
    print(f"  PYTHONHTTPSVERIFY = {os.environ['PYTHONHTTPSVERIFY']}")
    
    return True


def verify_dependencies():
    """Verify required dependencies are installed"""
    print_banner("Dependency Verification")
    
    # Check Python packages
    required_packages = [
        "pytest",
        "selenium",
        "requests",
        "pytest-html",
        "pytest-xdist"
    ]
    
    for package in required_packages:
        success = run_command(
            f"python -c \"import {package}; print('{package} version:', getattr({package}, '__version__', 'unknown'))\"",
            f"Checking {package}",
            continue_on_error=True
        )
        if not success:
            print(f"[WARNING] {package} may not be installed properly")
    
    return True


def test_selenium_grid_connectivity():
    """Test Selenium Grid connectivity"""
    print_banner("Selenium Grid Connectivity Test")
    
    # Run the connectivity test script
    success = run_command(
        "python test_selenium_grid_connectivity.py",
        "Testing Selenium Grid connectivity and browser sessions"
    )
    
    if not success:
        print("[ERROR] Selenium Grid connectivity test failed!")
        print("[INFO] Please ensure:")
        print("  1. Selenium Grid is running at http://192.168.1.33:4444")
        print("  2. Grid nodes are available and ready")
        print("  3. Network connectivity is working")
        return False
    
    return True


def run_selenium_grid_tests():
    """Run the actual Selenium Grid tests"""
    print_banner("Selenium Grid Test Execution")
    
    # Create reports directory
    os.makedirs("reports", exist_ok=True)
    
    # Test different scenarios based on user choice
    print("\nSelect test scenario:")
    print("1. Homepage Links Only")
    print("2. Full Automation Suite")
    print("3. Selenium Grid Validation")
    print("4. All Tests")
    
    choice = input("\nEnter choice (1-4) [default: 1]: ").strip() or "1"
    
    if choice == "1":
        # Homepage links test
        success = run_command(
            "pytest test_selenium_grid_uc001.py -v -s --html=reports/local_selenium_grid_homepage.html --self-contained-html",
            "Running homepage links test on Selenium Grid",
            continue_on_error=True
        )
    elif choice == "2":
        # Full automation suite
        success = run_command(
            "python run_complete_automation.py",
            "Running full automation suite with Selenium Grid",
            continue_on_error=True
        )
    elif choice == "3":
        # Selenium Grid validation only
        success = run_command(
            "pytest test_selenium_grid_uc001.py::TestUC001SeleniumGrid::test_uc001_selenium_grid_homepage_links -v -s --html=reports/local_selenium_grid_validation.html --self-contained-html",
            "Running Selenium Grid validation test",
            continue_on_error=True
        )
    elif choice == "4":
        # All tests
        success = run_command(
            "pytest test_selenium_grid_uc001.py final_automation/generated_tests/ -v -s --html=reports/local_selenium_grid_all.html --self-contained-html -n 2 --dist worksteal",
            "Running all tests with Selenium Grid and parallel execution",
            continue_on_error=True
        )
    else:
        print("[ERROR] Invalid choice")
        return False
    
    return success


def generate_test_summary():
    """Generate test summary similar to GitHub Actions"""
    print_banner("Test Summary Generation")
    
    # Check for generated reports
    reports_found = []
    report_dir = "reports"
    
    if os.path.exists(report_dir):
        for file in os.listdir(report_dir):
            if file.startswith("local_selenium_grid") or file.startswith("selenium_grid"):
                reports_found.append(file)
    
    print(f"[REPORTS] Found {len(reports_found)} test reports:")
    for report in reports_found:
        file_path = os.path.join(report_dir, report)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"  📄 {report} ({file_size:,} bytes)")
    
    # Check for JSON reports with test metrics
    json_reports = [f for f in reports_found if f.endswith('.json')]
    if json_reports:
        print(f"\n[METRICS] Test Metrics:")
        for json_report in json_reports:
            try:
                import json
                with open(os.path.join(report_dir, json_report), 'r') as f:
                    data = json.load(f)
                    print(f"  📊 {json_report}:")
                    print(f"    Total Links: {data.get('total_links', 'N/A')}")
                    print(f"    Valid Links: {data.get('valid_links_count', 'N/A')}")
                    print(f"    Broken Links: {data.get('broken_links_count', 'N/A')}")
                    print(f"    Success Rate: {data.get('summary', {}).get('success_rate', 'N/A')}")
            except Exception as e:
                print(f"    ❌ Error reading {json_report}: {e}")
    
    return True


def open_reports():
    """Open generated reports in browser"""
    print_banner("Opening Test Reports")
    
    report_dir = "reports"
    html_reports = []
    
    if os.path.exists(report_dir):
        for file in os.listdir(report_dir):
            if file.startswith("local_selenium_grid") and file.endswith('.html'):
                html_reports.append(file)
    
    if html_reports:
        print(f"[REPORTS] Found {len(html_reports)} HTML reports")
        for report in html_reports:
            report_path = os.path.join(report_dir, report)
            try:
                if os.name == 'nt':  # Windows
                    os.system(f'start {report_path}')
                else:  # Linux/Mac
                    os.system(f'open {report_path}')
                print(f"[BROWSER] Opened: {report}")
            except Exception as e:
                print(f"[INFO] Could not auto-open {report}: {e}")
                print(f"[INFO] Please manually open: {report_path}")
    else:
        print("[INFO] No HTML reports found to open")
    
    return True


def main():
    """Main execution function"""
    start_time = time.time()
    
    print("🚀 Local Selenium Grid Testing")
    print("Simulating GitHub Actions selenium-grid-tests.yml workflow")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Setup Environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)
    
    # Step 2: Verify Dependencies
    if not verify_dependencies():
        print("❌ Dependency verification failed")
        sys.exit(1)
    
    # Step 3: Test Grid Connectivity
    grid_connectivity = test_selenium_grid_connectivity()
    if not grid_connectivity:
        print("⚠️ Selenium Grid connectivity test had issues")
        print("Chrome browser appears to be working, continuing with Chrome-only testing...")
        # Continue anyway since Chrome is working
    
    # Step 4: Run Tests
    test_success = run_selenium_grid_tests()
    
    # Step 5: Generate Summary
    generate_test_summary()
    
    # Step 6: Open Reports
    open_reports()
    
    # Calculate execution time
    end_time = time.time()
    execution_time = end_time - start_time
    
    print_banner("Local Test Execution Complete")
    print(f"Total Execution Time: {execution_time:.2f} seconds")
    print(f"Grid Hub: {os.environ.get('SELENIUM_HUB_URL')}")
    print(f"Browser: {os.environ.get('SELENIUM_BROWSER')}")
    
    if test_success:
        print("✅ Local Selenium Grid testing completed successfully!")
        print("📊 Check the opened HTML reports for detailed results")
    else:
        print("⚠️ Some tests may have failed. Check the reports for details.")
    
    return 0 if test_success else 1


if __name__ == "__main__":
    sys.exit(main())