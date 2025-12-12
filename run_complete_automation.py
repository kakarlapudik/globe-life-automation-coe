#!/usr/bin/env python
"""
Complete AI Test Automation Script
Generates tests from requirements and runs comprehensive link validation
"""

import subprocess
import sys
import os
import time
from datetime import datetime


def print_banner(message):
    """Print a formatted banner"""
    print(f"\n{'='*60}")
    print(f"[AUTOMATION] {message}")
    print(f"{'='*60}")


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n[TASK] {description}")
    print(f"[CMD] Command: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=False, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[SUCCESS] {description}")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"[FAILED] {description}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
        
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] Exception running {description}: {e}")
        return False


def main():
    """Main execution function"""
    start_time = time.time()
    
    print_banner("AI Test Automation Complete Workflow")
    print(f"[TIME] Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Generate tests from requirements
    print_banner("Step 1: Generate AI Tests from Requirements")
    success = run_command(
        "python run_agent.py test_case_reqs.txt --output ./final_automation --verbose",
        "Generating comprehensive test scripts from requirements"
    )
    
    if not success:
        print("[ERROR] Failed to generate tests. Exiting.")
        sys.exit(1)
    
    # Step 2: Run all generated tests with HTML reporting (parallel execution)
    print_banner("Step 2: Execute All Generated Tests in Parallel with Playwright")
    
    print("[INFO] Using local Playwright execution (Chrome browser)")
    success = run_command(
        "pytest ./final_automation/generated_tests/ -v -s --html=reports/complete_automation_report.html --self-contained-html -n auto --dist worksteal",
        "Running all AI-generated link validation tests in parallel with Playwright"
    )
    
    # Step 3: Generate summary report
    print_banner("Step 3: Generate Summary Report")
    
    # Check if reports directory exists and list generated reports
    if os.path.exists("reports"):
        print("[REPORTS] Generated Reports:")
        for file in os.listdir("reports"):
            if file.endswith(('.html', '.json')):
                file_path = os.path.join("reports", file)
                file_size = os.path.getsize(file_path)
                print(f"   [FILE] {file} ({file_size:,} bytes)")
    
    # Calculate execution time
    end_time = time.time()
    execution_time = end_time - start_time
    
    print_banner("Execution Summary")
    print(f"[TIME] Total Execution Time: {execution_time:.2f} seconds")
    print(f"[REPORT] Main HTML Report: reports/complete_automation_report.html")
    print(f"[DATA] JSON Reports: reports/*_links_report.json")
    
    if success:
        print("[SUCCESS] All tests completed successfully!")
    else:
        print("[WARNING] Some tests may have failed. Check the reports for details.")
    
    # Step 4: Commit and push changes to remote repository
    print_banner("Step 4: Commit and Push Changes to Remote Repository")
    
    # Add all changes to git
    git_add_success = run_command(
        "git add .",
        "Adding all changes to git staging area"
    )
    
    if git_add_success:
        # Create commit message with timestamp and test results
        commit_message = f"Automated test execution - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {'PASSED' if success else 'PARTIAL'}"
        
        # Commit changes
        git_commit_success = run_command(
            f'git commit -m "{commit_message}"',
            "Committing changes to local repository"
        )
        
        if git_commit_success:
            # Push to remote repository
            git_push_success = run_command(
                "git push origin HEAD",
                "Pushing changes to remote repository (https://github.com/kakarlapudik/globe-life-automation-coe)"
            )
            
            if git_push_success:
                print("[SUCCESS] Changes successfully pushed to remote repository!")
            else:
                print("[WARNING] Failed to push to remote repository. Check network connection and credentials.")
        else:
            print("[INFO] No changes to commit or commit failed.")
    else:
        print("[WARNING] Failed to add changes to git staging area.")
    
    # Always try to open the main report (regardless of test results)
    try:
        if os.name == 'nt':  # Windows
            os.system("start reports\\complete_automation_report.html")
        else:  # Linux/Mac
            os.system("open reports/complete_automation_report.html")
        print("[BROWSER] Opening HTML report in browser...")
    except Exception as e:
        print(f"[INFO] Could not auto-open report: {e}")
        print("[INFO] Please manually open: reports/complete_automation_report.html")
    
    print_banner("Workflow Complete")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())