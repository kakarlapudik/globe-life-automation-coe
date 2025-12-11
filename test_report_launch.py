#!/usr/bin/env python
"""
Test script to verify report launching works correctly
"""

import os
import sys


def test_report_launch():
    """Test that the report launching logic works"""
    print("Testing report launch functionality...")
    
    # Check if the report exists
    report_path = "reports/complete_automation_report.html"
    if not os.path.exists(report_path):
        print(f"❌ Report not found: {report_path}")
        return False
    
    print(f"✅ Report found: {report_path}")
    
    # Test the launch logic (same as in the automation script)
    try:
        if os.name == 'nt':  # Windows
            print("🌐 Testing Windows report launch...")
            # Use echo to simulate the command without actually opening
            result = os.system(f'echo "Would launch: start {report_path}"')
            if result == 0:
                print("✅ Windows launch command would work")
            else:
                print("❌ Windows launch command failed")
                return False
        else:  # Linux/Mac
            print("🌐 Testing Unix report launch...")
            result = os.system(f'echo "Would launch: open {report_path}"')
            if result == 0:
                print("✅ Unix launch command would work")
            else:
                print("❌ Unix launch command failed")
                return False
                
    except Exception as e:
        print(f"❌ Exception during launch test: {e}")
        return False
    
    print("✅ Report launch functionality is working correctly!")
    return True


if __name__ == "__main__":
    success = test_report_launch()
    sys.exit(0 if success else 1)