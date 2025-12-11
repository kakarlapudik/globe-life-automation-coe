# AWS Credentials Setup Guide

This guide explains how to configure AWS credentials for deploying and testing the Pipeline Design Framework.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Credential Methods](#credential-methods)
3. [Setup Instructions](#setup-instructions)
4. [Testing Your Configuration](#testing-your-configuration)
5. [Security Best Practices](#security-best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before setting up AWS credentials, ensure you have:

- An AWS account with appropriate permissions
- AWS CLI installed (version 2.x recommended)
- Node.js 18+ or Python 3.9+ (depending on your CDK language)
- AWS CDK CLI installed: `npm install -g aws-cdk`

### Required AWS Permissions

Your AWS user/role needs the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:*",
        "s3:*",
        "iam:*",
        "codepipeline:*",
        "codebuild:*",
        "kms:*",
        "ec2:DescribeAvailabilityZones",
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets",
        "ec2:DescribeSecurityGroups",
        "ssm:GetParameter",
        "ssm:PutParameter"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Credential Methods

Choose the method that best fits your environment:

### Method 1: IAM User Access Keys (Development/Testing)

**Best for:** Local development, testing, CI/CD pipelines

**Steps:**

1. **Create IAM User:**
   ```bash
   # Via AWS Console
   # Navigate to: IAM > Users > Add User
   # Enable: Programmatic access
   # Attach policies: PowerUserAccess, IAMReadOnlyAccess
   ```

2. **Generate Access Keys:**
   - Go to IAM > Users > [Your User] > Security Credentials
   - Click "Create access key"
   - Download and save the credentials securely

3. **Configure locally:**
   ```bash
   # Option A: Using AWS CLI
   aws configure
   # Enter: Access Key ID, Secret Access Key, Region, Output format
   
   # Option B: Using environment variables
   export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   export AWS_DEFAULT_REGION=us-east-1
   ```

### Method 2: AWS SSO (Recommended for Enterprise)

**Best for:** Enterprise environments with centralized identity management

**Steps:**

1. **Configure SSO:**
   ```bash
   aws configure sso
   # Follow prompts to set up SSO profile
   ```

2. **Login:**
   ```bash
   aws sso login --profile your-profile-name
   ```

3. **Use profile:**
   ```bash
   export AWS_PROFILE=your-profile-name
   # Or add to .env file
   ```

### Method 3: IAM Role (For AWS Services)

**Best for:** EC2, ECS, Lambda, CodeBuild execution

**Steps:**

1. **Create IAM Role:**
   ```bash
   # Via AWS Console or CloudFormation
   # Attach trust policy for the service (EC2, ECS, etc.)
   # Attach required permissions
   ```

2. **Attach to service:**
   - EC2: Attach role when launching instance
   - ECS: Specify in task definition
   - Lambda: Specify in function configuration
   - CodeBuild: Specify in project configuration

3. **No credentials needed:**
   - AWS SDK automatically uses instance metadata service
   - No environment variables required

---

## Setup Instructions

### Step 1: Clone and Configure

```bash
# Navigate to the framework directory
cd pipeline-design-framework

# Copy the example environment file
cp .env.example .env

# Edit the .env file with your credentials
nano .env  # or use your preferred editor
```

### Step 2: Configure AWS Credentials

**Option A: Using .env file (Development)**

Edit `.env` and add your credentials:

```bash
AWS_ACCOUNT_ID=123456789012
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**Option B: Using AWS CLI profiles (Recommended)**

```bash
# Configure profile
aws configure --profile pipeline-dev

# Set profile in .env
echo "AWS_PROFILE=pipeline-dev" >> .env
```

**Option C: Using AWS SSO**

```bash
# Configure SSO
aws configure sso --profile pipeline-sso

# Login
aws sso login --profile pipeline-sso

# Set profile in .env
echo "AWS_PROFILE=pipeline-sso" >> .env
```

### Step 3: Bootstrap CDK

Bootstrap your AWS environment for CDK deployments:

```bash
# Load environment variables
source .env  # Linux/Mac
# or
set -a; source .env; set +a  # Linux/Mac (export all)

# Bootstrap CDK with custom qualifier
cdk bootstrap aws://${AWS_ACCOUNT_ID}/${AWS_REGION} \
  --qualifier ${CDK_QUALIFIER:-pipeframe} \
  --cloudformation-execution-policies arn:aws:iam::aws:policy/PowerUserAccess

# If using permissions boundary
cdk bootstrap aws://${AWS_ACCOUNT_ID}/${AWS_REGION} \
  --qualifier ${CDK_QUALIFIER:-pipeframe} \
  --cloudformation-execution-policies arn:aws:iam::aws:policy/PowerUserAccess \
  --custom-permissions-boundary ${PERMISSIONS_BOUNDARY_ARN}
```

### Step 4: Verify Configuration

```bash
# Test AWS credentials
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDAI...",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-user"
# }

# Test CDK
cdk --version

# List CDK stacks (should not error)
cdk list
```

---

## Testing Your Configuration

### Quick Test Script

Create a test script to verify your setup:

```bash
#!/bin/bash
# test-aws-setup.sh

echo "Testing AWS Configuration..."
echo "=============================="

# Test 1: AWS CLI
echo -n "1. AWS CLI installed: "
if command -v aws &> /dev/null; then
    echo "✓ $(aws --version)"
else
    echo "✗ Not found"
    exit 1
fi

# Test 2: Credentials
echo -n "2. AWS Credentials: "
if aws sts get-caller-identity &> /dev/null; then
    echo "✓ Valid"
    aws sts get-caller-identity --query 'Account' --output text
else
    echo "✗ Invalid or not configured"
    exit 1
fi

# Test 3: CDK CLI
echo -n "3. CDK CLI installed: "
if command -v cdk &> /dev/null; then
    echo "✓ $(cdk --version)"
else
    echo "✗ Not found"
    exit 1
fi

# Test 4: CDK Bootstrap
echo -n "4. CDK Bootstrap: "
ACCOUNT=$(aws sts get-caller-identity --query 'Account' --output text)
REGION=${AWS_REGION:-us-east-1}
if aws cloudformation describe-stacks --stack-name CDKToolkit --region $REGION &> /dev/null; then
    echo "✓ Bootstrapped in $REGION"
else
    echo "✗ Not bootstrapped in $REGION"
    echo "   Run: cdk bootstrap aws://$ACCOUNT/$REGION"
fi

# Test 5: Required permissions
echo -n "5. S3 Access: "
if aws s3 ls &> /dev/null; then
    echo "✓ Can list buckets"
else
    echo "✗ Cannot list buckets"
fi

echo ""
echo "Configuration test complete!"
```

Run the test:

```bash
chmod +x test-aws-setup.sh
./test-aws-setup.sh
```

### Deploy Test Stack

Deploy a minimal test stack:

```bash
# Navigate to Python example
cd cdk-templates/python

# Install dependencies
pip install -r requirements.txt

# Create test app
cat > test_app.py << 'EOF'
#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from pipeline_stack import PipelineStack

app = App()

PipelineStack(app, "TestPipelineStack",
    app_name="test-app",
    stack_id="test",
    source_repo="test-repo",
    env=Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION')
    )
)

app.synth()
EOF

# Synthesize (test without deploying)
cdk synth -a "python test_app.py"

# Deploy (if synthesis succeeds)
cdk deploy -a "python test_app.py" --require-approval never

# Clean up
cdk destroy -a "python test_app.py" --force
```

---

## Security Best Practices

### 1. Never Commit Credentials

```bash
# Ensure .env is in .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
echo "*.pem" >> .gitignore
echo "*.key" >> .gitignore
```

### 2. Use IAM Roles When Possible

- Prefer IAM roles over access keys
- Use temporary credentials (STS)
- Implement least privilege principle

### 3. Rotate Credentials Regularly

```bash
# Create new access key
aws iam create-access-key --user-name your-username

# Update .env with new credentials

# Delete old access key
aws iam delete-access-key --user-name your-username --access-key-id OLD_KEY_ID
```

### 4. Enable MFA

```bash
# Require MFA for sensitive operations
aws iam put-user-policy --user-name your-username \
  --policy-name RequireMFA \
  --policy-document file://require-mfa-policy.json
```

### 5. Use Permissions Boundaries

```bash
# Set permissions boundary in .env
PERMISSIONS_BOUNDARY_ARN=arn:aws:iam::123456789012:policy/DeveloperBoundary

# CDK will automatically apply to all created roles
```

### 6. Audit Access

```bash
# Check last used
aws iam get-access-key-last-used --access-key-id YOUR_KEY_ID

# Review CloudTrail logs
aws cloudtrail lookup-events --lookup-attributes AttributeKey=Username,AttributeValue=your-username
```

---

## Troubleshooting

### Issue: "Unable to locate credentials"

**Solution:**

```bash
# Check if credentials are set
aws configure list

# Verify environment variables
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY

# Try explicit profile
export AWS_PROFILE=default
aws sts get-caller-identity
```

### Issue: "Access Denied" errors

**Solution:**

```bash
# Check current identity
aws sts get-caller-identity

# Verify permissions
aws iam get-user-policy --user-name your-username --policy-name your-policy

# Check attached policies
aws iam list-attached-user-policies --user-name your-username
```

### Issue: CDK Bootstrap fails

**Solution:**

```bash
# Check if already bootstrapped
aws cloudformation describe-stacks --stack-name CDKToolkit

# Delete and re-bootstrap
aws cloudformation delete-stack --stack-name CDKToolkit
# Wait for deletion
aws cloudformation wait stack-delete-complete --stack-name CDKToolkit
# Re-bootstrap
cdk bootstrap
```

### Issue: "Region not specified"

**Solution:**

```bash
# Set default region
export AWS_DEFAULT_REGION=us-east-1
echo "AWS_DEFAULT_REGION=us-east-1" >> .env

# Or specify in commands
aws s3 ls --region us-east-1
cdk deploy --region us-east-1
```

### Issue: SSO session expired

**Solution:**

```bash
# Re-login
aws sso login --profile your-profile

# Check session
aws sts get-caller-identity --profile your-profile
```

---

## Additional Resources

- [AWS CLI Configuration Guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
- [AWS CDK Bootstrap](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [AWS SSO Configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)

---

## Support

For issues specific to this framework:
- Check the [Troubleshooting Guide](./troubleshooting.md)
- Review [Setup Guide](./setup-guide.md)
- Open an issue in the repository

For AWS-specific issues:
- AWS Support Console
- AWS Documentation
- AWS Forums
