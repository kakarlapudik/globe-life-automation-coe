# Complete AI Test Automation Script - PowerShell Version
# Generates tests from requirements and runs comprehensive link validation

function Write-Banner {
    param([string]$Message)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "🚀 $Message" -ForegroundColor Yellow
    Write-Host "=" * 60 -ForegroundColor Cyan
}

function Run-Command {
    param(
        [string]$Command,
        [string]$Description
    )
    
    Write-Host ""
    Write-Host "📋 $Description" -ForegroundColor Green
    Write-Host "💻 Command: $Command" -ForegroundColor Gray
    
    try {
        $result = Invoke-Expression $Command
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Success: $Description" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed: $Description" -ForegroundColor Red
            return $false
        }
        return $true
    }
    catch {
        Write-Host "❌ Exception running $Description`: $_" -ForegroundColor Red
        return $false
    }
}

# Main execution
$startTime = Get-Date

Write-Banner "AI Test Automation Complete Workflow"
Write-Host "🕐 Started at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan

# Step 1: Generate tests from requirements
Write-Banner "Step 1: Generate AI Tests from Requirements"
$success = Run-Command -Command "python run_agent.py test_case_reqs.txt --output ./final_automation --verbose" -Description "Generating comprehensive test scripts from requirements"

if (-not $success) {
    Write-Host "❌ Failed to generate tests. Exiting." -ForegroundColor Red
    exit 1
}

# Step 2: Run all generated tests with HTML reporting (parallel execution)
Write-Banner "Step 2: Execute All Generated Tests in Parallel with Playwright"

Write-Host "🎭 Using local Playwright execution (Chrome browser)" -ForegroundColor Cyan
$success = Run-Command -Command "pytest ./final_automation/generated_tests/ -v -s --html=reports/complete_automation_report.html --self-contained-html -n auto --dist worksteal" -Description "Running all AI-generated link validation tests in parallel with Playwright"

# Step 3: Generate summary report
Write-Banner "Step 3: Generate Summary Report"

# Check if reports directory exists and list generated reports
if (Test-Path "reports") {
    Write-Host "📊 Generated Reports:" -ForegroundColor Yellow
    Get-ChildItem "reports" -Filter "*.html", "*.json" | ForEach-Object {
        $size = [math]::Round($_.Length / 1KB, 2)
        Write-Host "   📄 $($_.Name) ($size KB)" -ForegroundColor White
    }
}

# Calculate execution time
$endTime = Get-Date
$executionTime = ($endTime - $startTime).TotalSeconds

Write-Banner "Execution Summary"
Write-Host "🕐 Total Execution Time: $([math]::Round($executionTime, 2)) seconds" -ForegroundColor Cyan
Write-Host "📊 Main HTML Report: reports/complete_automation_report.html" -ForegroundColor Yellow
Write-Host "📋 JSON Reports: reports/*_links_report.json" -ForegroundColor Yellow

if ($success) {
    Write-Host "✅ All tests completed successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some tests may have failed. Check the reports for details." -ForegroundColor Yellow
}

# Step 4: Commit and push changes to remote repository
Write-Banner "Step 4: Commit and Push Changes to Remote Repository"

# Add all changes to git
$gitAddSuccess = Run-Command -Command "git add ." -Description "Adding all changes to git staging area"

if ($gitAddSuccess) {
    # Create commit message with timestamp and test results
    $commitMessage = "Automated test execution - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $(if ($success) { 'PASSED' } else { 'PARTIAL' })"
    
    # Commit changes
    $gitCommitSuccess = Run-Command -Command "git commit -m `"$commitMessage`"" -Description "Committing changes to local repository"
    
    if ($gitCommitSuccess) {
        # Push to remote repository
        $gitPushSuccess = Run-Command -Command "git push origin HEAD" -Description "Pushing changes to remote repository (https://github.com/kakarlapudik/globe-life-automation-coe)"
        
        if ($gitPushSuccess) {
            Write-Host "✅ Changes successfully pushed to remote repository!" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Failed to push to remote repository. Check network connection and credentials." -ForegroundColor Yellow
        }
    } else {
        Write-Host "ℹ️  No changes to commit or commit failed." -ForegroundColor Blue
    }
} else {
    Write-Host "⚠️  Failed to add changes to git staging area." -ForegroundColor Yellow
}

# Always try to open the main report (regardless of test results)
try {
    Start-Process "reports\complete_automation_report.html"
    Write-Host "🌐 Opening HTML report in browser..." -ForegroundColor Cyan
}
catch {
    Write-Host "📁 Could not auto-open report: $_" -ForegroundColor Yellow
    Write-Host "📁 Please manually open: reports/complete_automation_report.html" -ForegroundColor Yellow
}

Write-Banner "Workflow Complete"

if ($success) { exit 0 } else { exit 1 }