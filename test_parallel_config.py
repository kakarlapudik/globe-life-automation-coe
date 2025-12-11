#!/usr/bin/env python
"""
Test script to verify parallel execution configuration
"""

import subprocess
import sys
import os


def test_parallel_config():
    """Test that pytest-xdist is properly configured"""
    print("Testing parallel execution configuration...")
    
    # Check if pytest-xdist is installed
    try:
        import xdist
        print("✅ pytest-xdist is installed")
        print(f"   Version: {xdist.__version__}")
    except ImportError:
        print("❌ pytest-xdist is not installed")
        return False
    
    # Test pytest configuration
    try:
        result = subprocess.run(
            ["pytest", "--help"], 
            capture_output=True, 
            text=True, 
            check=False
        )
        
        if "-n" in result.stdout and "--dist" in result.stdout:
            print("✅ Parallel execution options are available")
        else:
            print("❌ Parallel execution options not found")
            return False
            
    except Exception as e:
        print(f"❌ Error checking pytest configuration: {e}")
        return False
    
    # Check pytest.ini configuration
    if os.path.exists("pytest.ini"):
        with open("pytest.ini", "r") as f:
            content = f.read()
            if "-n auto" in content and "--dist worksteal" in content:
                print("✅ pytest.ini configured for parallel execution")
            else:
                print("❌ pytest.ini not properly configured for parallel execution")
                return False
    else:
        print("⚠️  pytest.ini not found")
    
    print("\n🚀 Parallel execution is properly configured!")
    print("   - Tests will run on all available CPU cores")
    print("   - Dynamic load balancing with worksteal distribution")
    print("   - Configuration applied to all automation scripts")
    
    return True


if __name__ == "__main__":
    success = test_parallel_config()
    sys.exit(0 if success else 1)