#!/bin/bash

###############################################################################
# AWS Credentials Setup Script for Pipeline Design Framework
# This script helps configure AWS credentials for deployment and testing
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 is installed"
        return 0
    else
        print_error "$1 is not installed"
        return 1
    fi
}

###############################################################################
# Prerequisites Check
###############################################################################

check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local all_good=true
    
    # Check AWS CLI
    if check_command "aws"; then
        AWS_VERSION=$(aws --version 2>&1 | cut -d' ' -f1 | cut -d'/' -f2)
        print_info "AWS CLI version: $AWS_VERSION"
    else
        print_error "AWS CLI is required. Install from: https://aws.amazon.com/cli/"
        all_good=false
    fi
    
    # Check CDK CLI
    if check_command "cdk"; then
        CDK_VERSION=$(cdk --version 2>&1)
        print_info "CDK version: $CDK_VERSION"
    else
        print_warning "CDK CLI not found. Install with: npm install -g aws-cdk"
        all_good=false
    fi
    
    # Check Node.js or Python
    if check_command "node"; then
        NODE_VERSION=$(node --version)
        print_info "Node.js version: $NODE_VERSION"
    elif check_command "python3"; then
        PYTHON_VERSION=$(python3 --version)
        print_info "Python version: $PYTHON_VERSION"
    else
        print_warning "Neither Node.js nor Python found"
    fi
    
    echo ""
    
    if [ "$all_good" = false ]; then
        print_error "Please install missing prerequisites before continuing"
        exit 1
    fi
}

###############################################################################
# Credential Configuration
###############################################################################

configure_credentials() {
    print_header "AWS Credentials Configuration"
    
    echo "Choose your credential method:"
    echo "1) IAM User Access Keys (Development/Testing)"
    echo "2) AWS SSO (Enterprise/Recommended)"
    echo "3) IAM Role (For AWS Services)"
    echo "4) Use existing AWS CLI configuration"
    echo ""
    read -p "Enter choice [1-4]: " choice
    
    case $choice in
        1)
            configure_access_keys
            ;;
        2)
            configure_sso
            ;;
        3)
            configure_iam_role
            ;;
        4)
            use_existing_config
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

configure_access_keys() {
    print_info "Configuring IAM User Access Keys"
    echo ""
    
    read -p "AWS Account ID: " AWS_ACCOUNT_ID
    read -p "AWS Region [us-east-1]: " AWS_REGION
    AWS_REGION=${AWS_REGION:-us-east-1}
    read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
    read -sp "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
    echo ""
    
    # Create .env file
    cat > "$PROJECT_ROOT/.env" << EOF
# AWS Credentials Configuration
# Generated on $(date)

AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID
AWS_REGION=$AWS_REGION
AWS_DEFAULT_REGION=$AWS_REGION

AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

CDK_DEFAULT_ACCOUNT=$AWS_ACCOUNT_ID
CDK_DEFAULT_REGION=$AWS_REGION
CDK_QUALIFIER=pipeframe

APP_NAME=my-application
STACK_ID=dev
ENVIRONMENT=development
EOF
    
    print_success "Credentials saved to .env file"
    
    # Test credentials
    test_credentials
}

configure_sso() {
    print_info "Configuring AWS SSO"
    echo ""
    
    read -p "SSO Profile Name [default]: " PROFILE_NAME
    PROFILE_NAME=${PROFILE_NAME:-default}
    
    print_info "Running AWS SSO configuration..."
    aws configure sso --profile "$PROFILE_NAME"
    
    print_info "Logging in to AWS SSO..."
    aws sso login --profile "$PROFILE_NAME"
    
    # Get account and region from profile
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile "$PROFILE_NAME" --query Account --output text)
    AWS_REGION=$(aws configure get region --profile "$PROFILE_NAME")
    
    # Create .env file
    cat > "$PROJECT_ROOT/.env" << EOF
# AWS SSO Configuration
# Generated on $(date)

AWS_PROFILE=$PROFILE_NAME
AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID
AWS_REGION=$AWS_REGION
AWS_DEFAULT_REGION=$AWS_REGION

CDK_DEFAULT_ACCOUNT=$AWS_ACCOUNT_ID
CDK_DEFAULT_REGION=$AWS_REGION
CDK_QUALIFIER=pipeframe

APP_NAME=my-application
STACK_ID=dev
ENVIRONMENT=development
EOF
    
    print_success "SSO configuration saved to .env file"
    
    # Test credentials
    test_credentials
}

configure_iam_role() {
    print_info "Configuring IAM Role"
    echo ""
    
    read -p "AWS Account ID: " AWS_ACCOUNT_ID
    read -p "AWS Region [us-east-1]: " AWS_REGION
    AWS_REGION=${AWS_REGION:-us-east-1}
    read -p "IAM Role ARN (optional): " AWS_ROLE_ARN
    
    # Create .env file
    cat > "$PROJECT_ROOT/.env" << EOF
# IAM Role Configuration
# Generated on $(date)

AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID
AWS_REGION=$AWS_REGION
AWS_DEFAULT_REGION=$AWS_REGION
AWS_ROLE_ARN=$AWS_ROLE_ARN

CDK_DEFAULT_ACCOUNT=$AWS_ACCOUNT_ID
CDK_DEFAULT_REGION=$AWS_REGION
CDK_QUALIFIER=pipeframe

APP_NAME=my-application
STACK_ID=dev
ENVIRONMENT=development
EOF
    
    print_success "IAM Role configuration saved to .env file"
    print_info "Note: IAM roles work automatically when running on AWS services (EC2, ECS, Lambda, etc.)"
}

use_existing_config() {
    print_info "Using existing AWS CLI configuration"
    echo ""
    
    # Get current identity
    if aws sts get-caller-identity &> /dev/null; then
        AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
        AWS_REGION=$(aws configure get region)
        AWS_REGION=${AWS_REGION:-us-east-1}
        
        print_success "Found existing AWS configuration"
        print_info "Account: $AWS_ACCOUNT_ID"
        print_info "Region: $AWS_REGION"
        
        # Create .env file
        cat > "$PROJECT_ROOT/.env" << EOF
# AWS Configuration (Using existing AWS CLI config)
# Generated on $(date)

AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID
AWS_REGION=$AWS_REGION
AWS_DEFAULT_REGION=$AWS_REGION

CDK_DEFAULT_ACCOUNT=$AWS_ACCOUNT_ID
CDK_DEFAULT_REGION=$AWS_REGION
CDK_QUALIFIER=pipeframe

APP_NAME=my-application
STACK_ID=dev
ENVIRONMENT=development
EOF
        
        print_success "Configuration saved to .env file"
    else
        print_error "No valid AWS credentials found"
        print_info "Please run 'aws configure' first"
        exit 1
    fi
}

###############################################################################
# Test Credentials
###############################################################################

test_credentials() {
    print_header "Testing AWS Credentials"
    
    # Source .env file
    if [ -f "$PROJECT_ROOT/.env" ]; then
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
    fi
    
    # Test AWS CLI
    print_info "Testing AWS CLI access..."
    if aws sts get-caller-identity &> /dev/null; then
        IDENTITY=$(aws sts get-caller-identity)
        ACCOUNT=$(echo "$IDENTITY" | grep -o '"Account": "[^"]*' | cut -d'"' -f4)
        USER_ARN=$(echo "$IDENTITY" | grep -o '"Arn": "[^"]*' | cut -d'"' -f4)
        
        print_success "AWS credentials are valid"
        print_info "Account: $ACCOUNT"
        print_info "Identity: $USER_ARN"
    else
        print_error "AWS credentials test failed"
        return 1
    fi
    
    # Test S3 access
    print_info "Testing S3 access..."
    if aws s3 ls &> /dev/null; then
        print_success "S3 access confirmed"
    else
        print_warning "S3 access test failed (may need additional permissions)"
    fi
    
    echo ""
}

###############################################################################
# Bootstrap CDK
###############################################################################

bootstrap_cdk() {
    print_header "CDK Bootstrap"
    
    # Source .env file
    if [ -f "$PROJECT_ROOT/.env" ]; then
        set -a
        source "$PROJECT_ROOT/.env"
        set +a
    fi
    
    read -p "Do you want to bootstrap CDK in your AWS account? [y/N]: " bootstrap_choice
    
    if [[ $bootstrap_choice =~ ^[Yy]$ ]]; then
        print_info "Bootstrapping CDK..."
        
        QUALIFIER=${CDK_QUALIFIER:-pipeframe}
        
        if [ -n "$PERMISSIONS_BOUNDARY_ARN" ]; then
            print_info "Using permissions boundary: $PERMISSIONS_BOUNDARY_ARN"
            cdk bootstrap "aws://${AWS_ACCOUNT_ID}/${AWS_REGION}" \
                --qualifier "$QUALIFIER" \
                --cloudformation-execution-policies arn:aws:iam::aws:policy/PowerUserAccess \
                --custom-permissions-boundary "$PERMISSIONS_BOUNDARY_ARN"
        else
            cdk bootstrap "aws://${AWS_ACCOUNT_ID}/${AWS_REGION}" \
                --qualifier "$QUALIFIER" \
                --cloudformation-execution-policies arn:aws:iam::aws:policy/PowerUserAccess
        fi
        
        if [ $? -eq 0 ]; then
            print_success "CDK bootstrap completed successfully"
        else
            print_error "CDK bootstrap failed"
            return 1
        fi
    else
        print_info "Skipping CDK bootstrap"
    fi
    
    echo ""
}

###############################################################################
# Additional Configuration
###############################################################################

additional_config() {
    print_header "Additional Configuration"
    
    read -p "Do you want to configure additional settings? [y/N]: " config_choice
    
    if [[ $config_choice =~ ^[Yy]$ ]]; then
        read -p "Application Name [my-application]: " APP_NAME
        APP_NAME=${APP_NAME:-my-application}
        
        read -p "Stack ID [dev]: " STACK_ID
        STACK_ID=${STACK_ID:-dev}
        
        read -p "Permissions Boundary ARN (optional): " PERMISSIONS_BOUNDARY_ARN
        
        read -p "Enable Security Scanning? [y/N]: " ENABLE_SECURITY
        if [[ $ENABLE_SECURITY =~ ^[Yy]$ ]]; then
            ENABLE_SECURITY_SCANNING=true
        else
            ENABLE_SECURITY_SCANNING=false
        fi
        
        # Append to .env
        cat >> "$PROJECT_ROOT/.env" << EOF

# Additional Configuration
APP_NAME=$APP_NAME
STACK_ID=$STACK_ID
PERMISSIONS_BOUNDARY_ARN=$PERMISSIONS_BOUNDARY_ARN
ENABLE_SECURITY_SCANNING=$ENABLE_SECURITY_SCANNING
EOF
        
        print_success "Additional configuration saved"
    fi
    
    echo ""
}

###############################################################################
# Summary
###############################################################################

print_summary() {
    print_header "Setup Complete!"
    
    echo ""
    print_success "AWS credentials have been configured"
    print_info "Configuration file: $PROJECT_ROOT/.env"
    echo ""
    
    print_info "Next steps:"
    echo "  1. Review the .env file and adjust settings as needed"
    echo "  2. Read the documentation: docs/aws-credentials-setup.md"
    echo "  3. Deploy a test stack: cd cdk-templates/python && cdk deploy"
    echo ""
    
    print_warning "Security reminder:"
    echo "  - Never commit .env file to version control"
    echo "  - Rotate credentials regularly"
    echo "  - Use IAM roles when possible"
    echo "  - Enable MFA for production accounts"
    echo ""
}

###############################################################################
# Main Execution
###############################################################################

main() {
    clear
    print_header "Pipeline Design Framework - AWS Setup"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Configure credentials
    configure_credentials
    
    # Bootstrap CDK
    bootstrap_cdk
    
    # Additional configuration
    additional_config
    
    # Print summary
    print_summary
}

# Run main function
main
