#!/usr/bin/env python3
"""
Build and Publish Script for RAPTOR Python Playwright Framework

This script automates the process of building and publishing the package to PyPI.
It performs the following steps:
1. Clean previous builds
2. Run tests
3. Build distributions (wheel and source)
4. Check distributions
5. Optionally publish to TestPyPI or PyPI
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_step(message):
    """Print a step message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def run_command(command, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {command}")
        print_error(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e


def clean_build_artifacts():
    """Remove previous build artifacts."""
    print_step("Cleaning Build Artifacts")
    
    dirs_to_remove = ['build', 'dist', '*.egg-info', '__pycache__', '.pytest_cache']
    
    for pattern in dirs_to_remove:
        if '*' in pattern:
            # Handle glob patterns
            for path in Path('.').rglob(pattern):
                if path.is_dir():
                    shutil.rmtree(path)
                    print_success(f"Removed: {path}")
        else:
            # Handle direct paths
            if os.path.exists(pattern):
                if os.path.isdir(pattern):
                    shutil.rmtree(pattern)
                else:
                    os.remove(pattern)
                print_success(f"Removed: {pattern}")
    
    print_success("Build artifacts cleaned")


def run_tests(skip_tests=False):
    """Run the test suite."""
    if skip_tests:
        print_warning("Skipping tests (--skip-tests flag)")
        return
    
    print_step("Running Tests")
    
    # Run unit tests
    print("Running unit tests...")
    result = run_command("pytest tests/ -v --cov=raptor", check=False)
    if result.returncode != 0:
        print_error("Unit tests failed!")
        sys.exit(1)
    print_success("Unit tests passed")
    
    # Run property-based tests
    print("\nRunning property-based tests...")
    result = run_command("pytest tests/test_property_*.py -v", check=False)
    if result.returncode != 0:
        print_error("Property-based tests failed!")
        sys.exit(1)
    print_success("Property-based tests passed")
    
    print_success("All tests passed")


def run_linting(skip_lint=False):
    """Run code quality checks."""
    if skip_lint:
        print_warning("Skipping linting (--skip-lint flag)")
        return
    
    print_step("Running Code Quality Checks")
    
    # Run black
    print("Checking code formatting with black...")
    result = run_command("black --check raptor/", check=False)
    if result.returncode != 0:
        print_warning("Code formatting issues found. Run 'black raptor/' to fix.")
    else:
        print_success("Code formatting OK")
    
    # Run flake8
    print("\nRunning flake8...")
    result = run_command("flake8 raptor/", check=False)
    if result.returncode != 0:
        print_warning("Linting issues found")
    else:
        print_success("Linting OK")
    
    # Run mypy
    print("\nRunning type checking with mypy...")
    result = run_command("mypy raptor/ --ignore-missing-imports", check=False)
    if result.returncode != 0:
        print_warning("Type checking issues found")
    else:
        print_success("Type checking OK")


def build_distributions():
    """Build wheel and source distributions."""
    print_step("Building Distributions")
    
    print("Building wheel and source distribution...")
    result = run_command("python -m build")
    
    if result.returncode == 0:
        print_success("Distributions built successfully")
        
        # List built files
        dist_files = list(Path('dist').glob('*'))
        print("\nBuilt files:")
        for file in dist_files:
            print(f"  - {file.name}")
    else:
        print_error("Build failed!")
        sys.exit(1)


def check_distributions():
    """Check distributions with twine."""
    print_step("Checking Distributions")
    
    print("Running twine check...")
    result = run_command("twine check dist/*")
    
    if result.returncode == 0:
        print_success("Distribution checks passed")
    else:
        print_error("Distribution checks failed!")
        sys.exit(1)


def test_installation():
    """Test package installation."""
    print_step("Testing Package Installation")
    
    print("Creating test virtual environment...")
    run_command("python -m venv test-venv")
    
    print("Installing package from wheel...")
    if sys.platform == "win32":
        activate_cmd = "test-venv\\Scripts\\activate"
        pip_cmd = "test-venv\\Scripts\\pip"
        python_cmd = "test-venv\\Scripts\\python"
    else:
        activate_cmd = ". test-venv/bin/activate"
        pip_cmd = "test-venv/bin/pip"
        python_cmd = "test-venv/bin/python"
    
    # Find wheel file
    wheel_files = list(Path('dist').glob('*.whl'))
    if not wheel_files:
        print_error("No wheel file found!")
        sys.exit(1)
    
    wheel_file = wheel_files[0]
    
    # Install wheel
    result = run_command(f"{pip_cmd} install {wheel_file}", check=False)
    if result.returncode != 0:
        print_error("Installation failed!")
        shutil.rmtree('test-venv')
        sys.exit(1)
    
    # Test import
    result = run_command(
        f'{python_cmd} -c "import raptor; print(\'Version:\', raptor.__version__)"',
        check=False
    )
    if result.returncode != 0:
        print_error("Import test failed!")
        shutil.rmtree('test-venv')
        sys.exit(1)
    
    print(result.stdout)
    
    # Cleanup
    shutil.rmtree('test-venv')
    print_success("Installation test passed")


def publish_to_testpypi():
    """Publish to TestPyPI."""
    print_step("Publishing to TestPyPI")
    
    print_warning("This will upload to TestPyPI. Continue? (y/n)")
    response = input().strip().lower()
    
    if response != 'y':
        print_warning("Upload cancelled")
        return
    
    print("Uploading to TestPyPI...")
    result = run_command("twine upload --repository testpypi dist/*", check=False)
    
    if result.returncode == 0:
        print_success("Successfully uploaded to TestPyPI")
        print("\nYou can install the package with:")
        print("  pip install --index-url https://test.pypi.org/simple/ raptor-playwright")
    else:
        print_error("Upload to TestPyPI failed!")


def publish_to_pypi():
    """Publish to PyPI."""
    print_step("Publishing to PyPI")
    
    print_warning("⚠️  WARNING: This will upload to PRODUCTION PyPI!")
    print_warning("Make sure you have:")
    print("  1. Updated the version number")
    print("  2. Updated CHANGELOG.md")
    print("  3. Created a git tag")
    print("  4. All tests are passing")
    print("\nContinue? (yes/no)")
    response = input().strip().lower()
    
    if response != 'yes':
        print_warning("Upload cancelled")
        return
    
    print("Uploading to PyPI...")
    result = run_command("twine upload dist/*", check=False)
    
    if result.returncode == 0:
        print_success("Successfully uploaded to PyPI")
        print("\nYou can install the package with:")
        print("  pip install raptor-playwright")
    else:
        print_error("Upload to PyPI failed!")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Build and publish RAPTOR Python Playwright Framework"
    )
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip running tests'
    )
    parser.add_argument(
        '--skip-lint',
        action='store_true',
        help='Skip linting checks'
    )
    parser.add_argument(
        '--skip-install-test',
        action='store_true',
        help='Skip installation test'
    )
    parser.add_argument(
        '--publish',
        choices=['testpypi', 'pypi'],
        help='Publish to TestPyPI or PyPI'
    )
    parser.add_argument(
        '--clean-only',
        action='store_true',
        help='Only clean build artifacts'
    )
    
    args = parser.parse_args()
    
    print(f"{Colors.HEADER}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   RAPTOR Python Playwright Framework Build Script         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    # Clean build artifacts
    clean_build_artifacts()
    
    if args.clean_only:
        print_success("Clean complete!")
        return
    
    # Run linting
    run_linting(args.skip_lint)
    
    # Run tests
    run_tests(args.skip_tests)
    
    # Build distributions
    build_distributions()
    
    # Check distributions
    check_distributions()
    
    # Test installation
    if not args.skip_install_test:
        test_installation()
    
    # Publish if requested
    if args.publish == 'testpypi':
        publish_to_testpypi()
    elif args.publish == 'pypi':
        publish_to_pypi()
    
    print(f"\n{Colors.OKGREEN}{Colors.BOLD}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                  Build Complete! ✓                         ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")


if __name__ == '__main__':
    main()
