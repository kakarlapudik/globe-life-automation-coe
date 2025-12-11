# AWS Credentials Quick Reference

## 🚀 Quick Setup (Choose One Method)

### Method 1: Automated Setup Script
```bash
# Linux/Mac
./scripts/setup-aws-credentials.sh

# Windows
.\scripts\setup-aws-credentials.ps1
```

### Method 2: Manual Configuration

#### Step 1: Create .env file
```bash
cp .env.example .env
```

#### Step 2: Add your credentials to .env
```bash
AWS_ACCOUNT_ID=123456789012
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

#### Step 3: Bootstrap CDK
```bash
# Load environment
source .env  # Linux/Mac

# Bootstrap
cdk bootstrap aws://${AWS_ACCOUNT_ID}/${AWS_REGION}
```

---

## 🔑 Credential Methods

| Method | Best For | Setup Command |
|--------|----------|---------------|
| **Access Keys** | Development, Testing | `aws configure` |
| **AWS SSO** | Enterprise, Production | `aws configure sso` |
| **IAM Role** | EC2, ECS, Lambda | Automatic (no config needed) |
| **Existing Config** | Already configured | Use existing `~/.aws/credentials` |

---

## ✅ Verification Commands

```bash
# Test AWS credentials
aws sts get-caller-identity

# Check CDK version
cdk --version

# List CDK stacks
cdk list

# Check bootstrap status
aws cloudformation describe-stacks --stack-name CDKToolkit
```

---

## 🔒 Security Checklist

- [ ] Never commit `.env` file to git
- [ ] Add `.env` to `.gitignore`
- [ ] Use IAM roles when possible (not access keys)
- [ ] Enable MFA for production accounts
- [ ] Rotate access keys every 90 days
- [ ] Use permissions boundaries in enterprise environments
- [ ] Review CloudTrail logs regularly

---

## 🐛 Common Issues & Fixes

### Issue: "Unable to locate credentials"
```bash
# Check configuration
aws configure list

# Verify environment variables
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

### Issue: "Access Denied"
```bash
# Check current identity
aws sts get-caller-identity

# Verify permissions
aws iam list-attached-user-policies --user-name YOUR_USERNAME
```

### Issue: "Region not specified"
```bash
# Set default region
export AWS_DEFAULT_REGION=us-east-1
echo "AWS_DEFAULT_REGION=us-east-1" >> .env
```

### Issue: CDK Bootstrap fails
```bash
# Check if already bootstrapped
aws cloudformation describe-stacks --stack-name CDKToolkit

# Re-bootstrap if needed
cdk bootstrap --force
```

---

## 📋 Required Environment Variables

### Minimum Required
```bash
AWS_ACCOUNT_ID=123456789012
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### For CDK Deployment
```bash
CDK_DEFAULT_ACCOUNT=${AWS_ACCOUNT_ID}
CDK_DEFAULT_REGION=${AWS_REGION}
CDK_QUALIFIER=pipeframe
```

### For Application
```bash
APP_NAME=my-application
STACK_ID=dev
ENVIRONMENT=development
```

### Optional (Enterprise)
```bash
PERMISSIONS_BOUNDARY_ARN=arn:aws:iam::123456789012:policy/BoundaryPolicy
AWS_PROFILE=your-sso-profile
```

---

## 🔄 Quick Commands Reference

### Setup
```bash
# Install AWS CLI
# Linux: curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
# Mac: brew install awscli
# Windows: Download from https://aws.amazon.com/cli/

# Install CDK CLI
npm install -g aws-cdk

# Configure AWS
aws configure
```

### Bootstrap
```bash
# Basic bootstrap
cdk bootstrap

# With custom qualifier
cdk bootstrap --qualifier pipeframe

# With permissions boundary
cdk bootstrap --custom-permissions-boundary arn:aws:iam::123456789012:policy/Boundary
```

### Deploy
```bash
# Synthesize (test)
cdk synth

# Deploy
cdk deploy

# Deploy with approval
cdk deploy --require-approval never

# Destroy
cdk destroy
```

---

## 📚 Additional Resources

- **Full Setup Guide**: [docs/aws-credentials-setup.md](docs/aws-credentials-setup.md)
- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)
- **AWS CLI Docs**: https://docs.aws.amazon.com/cli/
- **CDK Docs**: https://docs.aws.amazon.com/cdk/

---

## 🆘 Need Help?

1. Check the [Full Setup Guide](docs/aws-credentials-setup.md)
2. Review [Troubleshooting Guide](docs/troubleshooting.md)
3. Run the test script: `./scripts/setup-aws-credentials.sh`
4. Contact DevOps team

---

**Last Updated**: 2025-11-21
