# AWS Credentials Setup Script for Pipeline Design Framework (PowerShell)
# This script helps configure AWS credentials for deployment and testing on Windows

param(
    [switch]$SkipPrerequisites,
    [switch]$UseExisting,
    [string]$ProfileName = "default"
)

$ErrorActionPreference = "Stop"

# Script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

###############################################################################
# Helper Functions
###############################################################################

function Write-Header {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Blue
    Write-Host $Message -ForegroundColor Blue
    Write-Host "========================================`n" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Cyan
}

function Test-Command {
    param([string]$Command)
    
    try {
        $null = Get-Command $Command -ErrorAction Stop
        Write-Success "$Command is installed"
        return $true
    }
    catch {
        Write-ErrorMsg "$Command is not installed"
        return $false
    }
}

###############################################################################
# Prerequisites Check
###############################################################################

function Test-Prerequisites {
    Write-Header "Checking Prerequisites"
    
    $allGood = $true
    
    # Check AWS CLI
    if (Test-Command "aws") {
        $awsVersion = (aws --version 2>&1) -replace "aws-cli/", "" -replace " .*", ""
        Write-Info "AWS CLI version: $awsVersion"
    }
    else {
        Write-ErrorMsg "AWS CLI is required. Install from: https://aws.amazon.com/cli/"
        $allGood = $false
    }
    
    # Check CDK CLI
    if (Test-Command "cdk") {
        $cdkVersion = cdk --version 2>&1
        Write-Info "CDK version: $cdkVersion"
    }
    else {
        Write-Warning "CDK CLI not found. Install with: npm install -g aws-cdk"
        $allGood = $false
    }
    
    # Check Node.js or Python
    if (Test-Command "node") {
        $nodeVersion = node --version
        Write-Info "Node.js version: $nodeVersion"
    }
    elseif (Test-Command "python") {
        $pythonVersion = python --version
        Write-Info "Python version: $pythonVersion"
    }
    else {
        Write-Warning "Neither Node.js nor Python found"
    }
    
    if (-not $allGood) {
        Write-ErrorMsg "Please install missing prerequisites before continuing"
        exit 1
    }
}

###############################################################################
# Credential Configuration
###############################################################################

function Get-CredentialMethod {
    Write-Header "AWS Credentials Configuration"
    
    Write-Host "Choose your credential method:"
    Write-Host "1) IAM User Access Keys (Development/Testing)"
    Write-Host "2) AWS SSO (Enterprise/Recommended)"
    Write-Host "3) IAM Role (For AWS Services)"
    Write-Host "4) Use existing AWS CLI configuration"
    Write-Host ""
    
    $choice = Read-Host "Enter choice [1-4]"
    
    switch ($choice) {
        "1" { Set-AccessKeys }
        "2" { Set-SSO }
        "3" { Set-IAMRole }
        "4" { Use-ExistingConfig }
        default {
            Write-ErrorMsg "Invalid choice"
            exit 1
        }
    }
}

function Set-AccessKeys {
    Write-Info "Configuring IAM User Access Keys"
    Write-Host ""
    
    $accountId = Read-Host "AWS Account ID"
    $region = Read-Host "AWS Region [us-east-1]"
    if ([string]::IsNullOrWhiteSpace($region)) { $region = "us-east-1" }
    
    $accessKeyId = Read-Host "AWS Access Key ID"
    $secretAccessKey = Read-Host "AWS Secret Access Key" -AsSecureString
    $secretAccessKeyPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secretAccessKey)
    )
    
    # Create .env file
    $envContent = @"
# AWS Credentials Configuration
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

AWS_ACCOUNT_ID=$accountId
AWS_REGION=$region
AWS_DEFAULT_REGION=$region

AWS_ACCESS_KEY_ID=$accessKeyId
AWS_SECRET_ACCESS_KEY=$secretAccessKeyPlain

CDK_DEFAULT_ACCOUNT=$accountId
CDK_DEFAULT_REGION=$region
CDK_QUALIFIER=pipeframe

APP_NAME=my-application
STACK_ID=dev
ENVIRONMENT=development
"@
    
    $envPath = Join-Path $ProjectRoot ".env"
    $envContent | Out-File -FilePath $envPath -Encoding UTF8
    
    Write-Success "Credentials saved to .env file"
    
    # Test credentials
    Test-Credentials
}

function Set-SSO {
    Write-Info "Configuring AWS SSO"
    Write-Host ""
    
    $profileName = Read-Host "SSO Profile Name [default]"
    if ([string]::IsNullOrWhiteSpace($profileName)) { $profileName = "default" }
    
    Write-Info "Running AWS SSO configuration..."
    aws configure sso --profile $profileName
    
    Write-Info "Logging in to AWS SSO..."
    aws sso login --profile $profileName
    
    # Get account and region from profile
    $accountId = aws sts get-caller-identity --profile $profileName --query Account --output text
    $region = aws configure get region --profile $profileName
    
    # Create .env file
    $envContent = @"
# AWS SSO Configuration
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

AWS_PROFILE=$profileName
AWS_ACCOUNT_ID=$accountId
AWS_REGION=$region
AWS_DEFAULT_REGION=$region

CDK_DEFAULT_ACCOUNT=$accountId
CDK_DEFAULT_REGION=$region
CDK_QUALIFIER=pipeframe

APP_NAME=my-application
STACK_ID=dev
ENVIRONMENT=development
"@
    
    $envPath = Join-Path $ProjectRoot ".env"
    $envContent | Out-File -FilePath $envPath -Encoding UTF8
    
    Write-Success "SSO configuration saved to .env file"
    
    # Test credentials
    Test-Credentials
}

function Set-IAMRole {
    Write-Info "Configuring IAM Role"
    Write-Host ""
    
    $accountId = Read-Host "AWS Account ID"
    $region = Read-Host "AWS Region [us-east-1]"
    if ([string]::IsNullOrWhiteSpace($region)) { $region = "us-east-1" }
    
    $roleArn = Read-Host "IAM Role ARN (optional)"
    
    # Create .env file
    $envContent = @"
# IAM Role Configuration
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

AWS_ACCOUNT_ID=$accountId
AWS_REGION=$region
AWS_DEFAULT_REGION=$region
AWS_ROLE_ARN=$roleArn

CDK_DEFAULT_ACCOUNT=$accountId
CDK_DEFAULT_REGION=$region
CDK_QUALIFIER=pipeframe

APP_NAME=my-application
STACK_ID=dev
ENVIRONMENT=development
"@
    
    $envPath = Join-Path $ProjectRoot ".env"
    $envContent | Out-File -FilePath $envPath -Encoding UTF8
    
    Write-Success "IAM Role configuration saved to .env file"
    Write-Info "Note: IAM roles work automatically when running on AWS services (EC2, ECS, Lambda, etc.)"
}

function Use-ExistingConfig {
    Write-Info "Using existing AWS CLI configuration"
    Write-Host ""
    
    # Get current identity
    try {
        $identity = aws sts get-caller-identity 2>&1
        $accountId = aws sts get-caller-identity --query Account --output text
        $region = aws configure get region
        if ([string]::IsNullOrWhiteSpace($region)) { $region = "us-east-1" }
        
        Write-Success "Found existing AWS configuration"
        Write-Info "Account: $accountId"
        Write-Info "Region: $region"
        
        # Create .env file
        $envContent = @"
# AWS Configuration (Using existing AWS CLI config)
# Generated on $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

AWS_ACCOUNT_ID=$accountId
AWS_REGION=$region
AWS_DEFAULT_REGION=$region

CDK_DEFAULT_ACCOUNT=$accountId
CDK_DEFAULT_REGION=$region
CDK_QUALIFIER=pipeframe

APP_NAME=my-application
STACK_ID=dev
ENVIRONMENT=development
"@
        
        $envPath = Join-Path $ProjectRoot ".env"
        $envContent | Out-File -FilePath $envPath -Encoding UTF8
        
        Write-Success "Configuration saved to .env file"
    }
    catch {
        Write-ErrorMsg "No valid AWS credentials found"
        Write-Info "Please run 'aws configure' first"
        exit 1
    }
}

###############################################################################
# Test Credentials
###############################################################################

function Test-Credentials {
    Write-Header "Testing AWS Credentials"
    
    # Load .env file
    $envPath = Join-Path $ProjectRoot ".env"
    if (Test-Path $envPath) {
        Get-Content $envPath | ForEach-Object {
            if ($_ -match '^([^=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                if (-not $name.StartsWith('#') -and $name -ne '') {
                    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
                }
            }
        }
    }
    
    # Test AWS CLI
    Write-Info "Testing AWS CLI access..."
    try {
        $identity = aws sts get-caller-identity 2>&1 | ConvertFrom-Json
        
        Write-Success "AWS credentials are valid"
        Write-Info "Account: $($identity.Account)"
        Write-Info "Identity: $($identity.Arn)"
    }
    catch {
        Write-ErrorMsg "AWS credentials test failed"
        return
    }
    
    # Test S3 access
    Write-Info "Testing S3 access..."
    try {
        $null = aws s3 ls 2>&1
        Write-Success "S3 access confirmed"
    }
    catch {
        Write-Warning "S3 access test failed (may need additional permissions)"
    }
    
    Write-Host ""
}

###############################################################################
# Bootstrap CDK
###############################################################################

function Invoke-CDKBootstrap {
    Write-Header "CDK Bootstrap"
    
    # Load .env file
    $envPath = Join-Path $ProjectRoot ".env"
    if (Test-Path $envPath) {
        Get-Content $envPath | ForEach-Object {
            if ($_ -match '^([^=]+)=(.*)$') {
                $name = $matches[1].Trim()
                $value = $matches[2].Trim()
                if (-not $name.StartsWith('#') -and $name -ne '') {
                    [Environment]::SetEnvironmentVariable($name, $value, 'Process')
                }
            }
        }
    }
    
    $bootstrap = Read-Host "Do you want to bootstrap CDK in your AWS account? [y/N]"
    
    if ($bootstrap -match '^[Yy]$') {
        Write-Info "Bootstrapping CDK..."
        
        $accountId = $env:AWS_ACCOUNT_ID
        $region = $env:AWS_REGION
        $qualifier = if ($env:CDK_QUALIFIER) { $env:CDK_QUALIFIER } else { "pipeframe" }
        
        try {
            if ($env:PERMISSIONS_BOUNDARY_ARN) {
                Write-Info "Using permissions boundary: $($env:PERMISSIONS_BOUNDARY_ARN)"
                cdk bootstrap "aws://$accountId/$region" `
                    --qualifier $qualifier `
                    --cloudformation-execution-policies "arn:aws:iam::aws:policy/PowerUserAccess" `
                    --custom-permissions-boundary $env:PERMISSIONS_BOUNDARY_ARN
            }
            else {
                cdk bootstrap "aws://$accountId/$region" `
                    --qualifier $qualifier `
                    --cloudformation-execution-policies "arn:aws:iam::aws:policy/PowerUserAccess"
            }
            
            Write-Success "CDK bootstrap completed successfully"
        }
        catch {
            Write-ErrorMsg "CDK bootstrap failed: $_"
        }
    }
    else {
        Write-Info "Skipping CDK bootstrap"
    }
    
    Write-Host ""
}

###############################################################################
# Summary
###############################################################################

function Show-Summary {
    Write-Header "Setup Complete!"
    
    Write-Host ""
    Write-Success "AWS credentials have been configured"
    Write-Info "Configuration file: $ProjectRoot\.env"
    Write-Host ""
    
    Write-Info "Next steps:"
    Write-Host "  1. Review the .env file and adjust settings as needed"
    Write-Host "  2. Read the documentation: docs\aws-credentials-setup.md"
    Write-Host "  3. Deploy a test stack: cd cdk-templates\python && cdk deploy"
    Write-Host ""
    
    Write-Warning "Security reminder:"
    Write-Host "  - Never commit .env file to version control"
    Write-Host "  - Rotate credentials regularly"
    Write-Host "  - Use IAM roles when possible"
    Write-Host "  - Enable MFA for production accounts"
    Write-Host ""
}

###############################################################################
# Main Execution
###############################################################################

function Main {
    Clear-Host
    Write-Header "Pipeline Design Framework - AWS Setup"
    
    # Check prerequisites
    if (-not $SkipPrerequisites) {
        Test-Prerequisites
    }
    
    # Configure credentials
    if ($UseExisting) {
        Use-ExistingConfig
    }
    else {
        Get-CredentialMethod
    }
    
    # Bootstrap CDK
    Invoke-CDKBootstrap
    
    # Print summary
    Show-Summary
}

# Run main function
Main
