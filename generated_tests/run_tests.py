#!/usr/bin/env python
"""
Quick start script to run Globe Life link validation tests
"""

import subprocess
import sys
import os


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import playwright
        import pytest
        import requests
        print("✓ All dependencies installed")
        return True
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nInstall dependencies with:")
        print("  pip install pytest playwright pytest-html requests")
        print("  playwright install chromium")
        return False


def run_tests(test_type="all"):
    """Run tests based on type"""
    
    if not check_dependencies():
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"Globe Life Investor Relations - Link Validation Tests")
    print(f"{'='*60}\n")
    
    test_commands = {
        "all": ["pytest", ".", "-v", "--html=reports/test_report.html", "--self-contained-html"],
        "quick": ["pytest", "test_homepage_links.py", "-v"],
        "navigation": ["pytest", "test_navigation_menu.py", "-v"],
        "footer": ["pytest", "test_footer_links.py", "-v"],
        "crawl": ["pytest", "test_sitewide_crawl.py", "-v"],
        "dynamic": ["pytest", "test_dynamic_content.py", "-v"]
    }
    
    if test_type not in test_commands:
        print(f"Unknown test type: {test_type}")
        print(f"Available types: {', '.join(test_commands.keys())}")
        sys.exit(1)
    
    cmd = test_commands[test_type]
    
    print(f"Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print(f"\n✅ All tests passed!")
        else:
            print(f"\n❌ Some tests failed. Check output above.")
        
        if test_type == "all":
            print(f"\n📊 HTML Report generated: report.html")
        
        return result.returncode
    
    except Exception as e:
        print(f"\n✗ Error running tests: {e}")
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Globe Life link validation tests")
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "quick", "navigation", "footer", "crawl", "dynamic"],
        help="Type of tests to run (default: all)"
    )
    
    args = parser.parse_args()
    
    sys.exit(run_tests(args.test_type))
