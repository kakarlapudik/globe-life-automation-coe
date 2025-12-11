# Troubleshooting Guide

This guide helps you resolve common issues when using the Pipeline Design Framework.

## Table of Contents

- [Account ID Issues](#account-id-issues)
- [Permission Errors](#permission-errors)
- [CDK Synthesis Failures](#cdk-synthesis-failures)
- [Azure DevOps Agent Connectivity](#azure-devops-agent-connectivity)
- [Bootstrap Failures](#bootstrap-failures)
- [Deployment Failures](#deployment-failures)
- [Security Scanning Issues](#security-scanning-issues)

---

## Account ID Issues

### Problem: Incorrect Account ID in Stack

**Symptoms:**
- Stack deploys to wrong AWS account
- Error: "Account mismatch"
- Resources created in unexpected account

**Solutions:**

1. **Verify Environment Variables**
   ```bash
   echo $CDK_DEFAULT_ACCOUNT
   echo $AWS_ACCOUNT_ID
   ```

2. **Check Azure DevOps Service Connection**
   - Navigate to Project Settings → Service Connections
   - Verify AWS service connection points to correct account
   - Test connection

3. **Validate CDK Context**
   ```bash
   cdk context --clear
   cdk synth
   ```

4. **Check cdk.json Configuration**
   ```json
   {
     "context": {
       "@aws-cdk/core:target-partitions": ["aws"]
     }
   }
   ```

### Problem: Account ID Not Resolved

**Symptoms:**
- Error: "Unable to resolve AWS account"
- Stack synthesis fails with account placeholder

**Solutions:**

1. **Set Environment Variables Explicitly**
   ```bash
   export CDK_DEFAULT_ACCOUNT=123456789012
   export CDK_DEFAULT_REGION=us-west-2
   ```

2. **Use AWS CLI to Get Account ID**
   ```bash
   export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
   ```

3. **Verify AWS Credentials**
   ```bash
   aws sts get-caller-identity
   ```

---

## Permission Errors

### Problem: Insufficient IAM Permissions

**Symptoms:**
- Error: "User is not authorized to perform: iam:CreateRole"
- Error: "Access Denied"
- Deployment fails during resource creation

**Solutions:**

1. **Check Permissions Boundary**
   ```bash
   # Verify boundary exists
   aws iam get-policy --policy-arn arn:aws:iam::ACCOUNT_ID:policy/PermissionsBoundary
   ```

2. **Verify Service Connection Permissions**
   - Service connection role must have:
     - `sts:AssumeRole`
     - `cloudformation:*`
     - `s3:*` (for CDK assets)
     - `iam:PassRole`

3. **Check CDK Bootstrap Permissions**
   ```bash
   # Bootstrap with explicit permissions
   cdk bootstrap \
     --cloudformation-execution-policies arn:aws:iam::ACCOUNT_ID:policy/PermissionsBoundary
   ```

4. **Review IAM Role Trust Relationships**
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [{
       "Effect": "Allow",
       "Principal": {
         "Service": "codebuild.amazonaws.com"
       },
       "Action": "sts:AssumeRole"
     }]
   }
   ```

### Problem: Permissions Boundary Violations

**Symptoms:**
- Error: "Cannot exceed permissions boundary"
- Role creation fails
- Policy attachment denied

**Solutions:**

1. **Verify Boundary Allows Required Actions**
   ```bash
   aws iam get-policy-version \
     --policy-arn arn:aws:iam::ACCOUNT_ID:policy/PermissionsBoundary \
     --version-id v1
   ```

2. **Update Permissions Boundary**
   - Add required permissions to boundary policy
   - Ensure boundary allows CDK operations

3. **Check Role Naming**
   - Roles must follow naming convention
   - Boundary may restrict role names

---

## CDK Synthesis Failures

### Problem: Stack Synthesis Fails

**Symptoms:**
- Error: "Synthesis failed"
- Error: "Unable to resolve"
- CloudFormation template not generated

**Solutions:**

1. **Clear CDK Cache**
   ```bash
   rm -rf cdk.out
   cdk synth
   ```

2. **Verify Dependencies**
   ```bash
   # TypeScript
   npm install
   
   # Python
   pip install -r requirements.txt
   
   # .NET
   dotnet restore
   ```

3. **Check for Circular Dependencies**
   - Review stack dependencies
   - Ensure no circular references

4. **Validate Construct IDs**
   - IDs must be unique within scope
   - No special characters except hyphens

### Problem: Qualifier Too Long

**Symptoms:**
- Error: "Qualifier must be <= 10 characters"
- Bootstrap fails

**Solutions:**

1. **Shorten App Name or Stack ID**
   ```typescript
   // Before
   appName: 'my-very-long-application-name'
   
   // After
   appName: 'myapp'
   ```

2. **Use Abbreviations**
   ```typescript
   appName: 'epic'  // Instead of 'epic-test-automation'
   stackId: 'dev'   // Instead of 'development'
   ```

### Problem: Missing Environment Variables

**Symptoms:**
- Error: "APP_NAME is required"
- Error: "STACK_ID is required"

**Solutions:**

1. **Set Required Variables**
   ```bash
   export APP_NAME=myapp
   export STACK_ID=dev
   ```

2. **Use .env File**
   ```bash
   # .env
   APP_NAME=myapp
   STACK_ID=dev
   CDK_DEFAULT_ACCOUNT=123456789012
   CDK_DEFAULT_REGION=us-west-2
   ```

3. **Pass via CDK Context**
   ```bash
   cdk synth -c appName=myapp -c stackId=dev
   ```

---

## Azure DevOps Agent Connectivity

### Problem: Agent Cannot Connect to AWS

**Symptoms:**
- Pipeline fails at AWS authentication step
- Error: "Unable to locate credentials"
- Timeout connecting to AWS

**Solutions:**

1. **Verify Service Connection**
   - Test connection in Azure DevOps
   - Check credentials are valid
   - Verify IAM role exists

2. **Check Agent Network Access**
   - Ensure agent can reach AWS endpoints
   - Verify firewall rules
   - Check proxy settings

3. **Validate Agent Pool**
   ```yaml
   pool:
     vmImage: 'ubuntu-latest'  # Or your self-hosted pool
   ```

4. **Test AWS CLI on Agent**
   ```yaml
   - script: |
       aws sts get-caller-identity
     displayName: 'Test AWS Connection'
   ```

### Problem: Agent Missing Dependencies

**Symptoms:**
- Error: "cdk: command not found"
- Error: "Node.js not found"
- Build tools missing

**Solutions:**

1. **Install Node.js**
   ```yaml
   - task: NodeTool@0
     inputs:
       versionSpec: '20.x'
   ```

2. **Install CDK CLI**
   ```yaml
   - script: npm install -g aws-cdk
     displayName: 'Install CDK CLI'
   ```

3. **Install AWS CLI**
   ```yaml
   - task: AWSShellScript@1
     inputs:
       awsCredentials: '$(AWS_SERVICE_CONNECTION)'
       regionName: '$(CDK_DEFAULT_REGION)'
   ```

---

## Bootstrap Failures

### Problem: Bootstrap Stack Already Exists

**Symptoms:**
- Error: "Stack already exists"
- Bootstrap fails with conflict

**Solutions:**

1. **Update Existing Bootstrap**
   ```bash
   cdk bootstrap --force
   ```

2. **Use Different Qualifier**
   ```bash
   cdk bootstrap --qualifier myapp2dev
   ```

3. **Delete and Recreate**
   ```bash
   # Caution: This deletes existing bootstrap resources
   aws cloudformation delete-stack --stack-name CDKToolkitmyapp
   cdk bootstrap
   ```

### Problem: Bootstrap Permissions Denied

**Symptoms:**
- Error: "Access denied during bootstrap"
- CloudFormation stack creation fails

**Solutions:**

1. **Check Bootstrap Permissions**
   - User/role needs:
     - `cloudformation:CreateStack`
     - `s3:CreateBucket`
     - `iam:CreateRole`
     - `ecr:CreateRepository`

2. **Use Administrator Access (Temporarily)**
   ```bash
   # For initial bootstrap only
   aws sts assume-role --role-arn arn:aws:iam::ACCOUNT_ID:role/Admin
   ```

3. **Bootstrap with Explicit Policies**
   ```bash
   cdk bootstrap \
     --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess
   ```

### Problem: S3 Bucket Name Conflict

**Symptoms:**
- Error: "Bucket already exists"
- Bootstrap fails on S3 creation

**Solutions:**

1. **Use Different Qualifier**
   ```bash
   cdk bootstrap --qualifier myapp2
   ```

2. **Delete Existing Bucket**
   ```bash
   aws s3 rb s3://cdk-myappdev-assets-ACCOUNT_ID-REGION --force
   ```

---

## Deployment Failures

### Problem: CloudFormation Rollback

**Symptoms:**
- Stack enters ROLLBACK_COMPLETE state
- Resources partially created
- Deployment fails midway

**Solutions:**

1. **Check CloudFormation Events**
   ```bash
   aws cloudformation describe-stack-events \
     --stack-name PipelineStackmyappdev \
     --max-items 20
   ```

2. **Review Error Messages**
   - Look for specific resource failures
   - Check resource limits
   - Verify resource names are unique

3. **Delete Failed Stack**
   ```bash
   aws cloudformation delete-stack --stack-name PipelineStackmyappdev
   ```

4. **Retry Deployment**
   ```bash
   cdk deploy --force
   ```

### Problem: Resource Already Exists

**Symptoms:**
- Error: "Resource already exists"
- Deployment fails on resource creation

**Solutions:**

1. **Import Existing Resource**
   ```typescript
   const bucket = s3.Bucket.fromBucketName(this, 'ExistingBucket', 'my-bucket-name');
   ```

2. **Use Different Resource Name**
   ```typescript
   bucketName: `${appName}-${stackId}-v2-artifacts`
   ```

3. **Delete Existing Resource**
   ```bash
   aws s3 rb s3://my-bucket-name --force
   ```

### Problem: Dependency Errors

**Symptoms:**
- Error: "Resource depends on"
- Circular dependency detected
- Deployment order issues

**Solutions:**

1. **Explicit Dependencies**
   ```typescript
   resource2.node.addDependency(resource1);
   ```

2. **Review Stack Dependencies**
   ```bash
   cdk ls --long
   ```

3. **Split into Multiple Stacks**
   - Separate infrastructure concerns
   - Deploy in correct order

---

## Security Scanning Issues

### Problem: Checkmarx Scan Fails

**Symptoms:**
- Security scan times out
- Error: "Unable to connect to Checkmarx"
- Scan results not available

**Solutions:**

1. **Verify Checkmarx Service Connection**
   - Check credentials in Azure DevOps
   - Test connection to Checkmarx server

2. **Check Network Access**
   - Ensure agent can reach Checkmarx server
   - Verify firewall rules

3. **Increase Timeout**
   ```yaml
   - task: CheckmarxSAST@2
     inputs:
       scanTimeout: 120  # minutes
   ```

### Problem: Vulnerabilities Block Deployment

**Symptoms:**
- Build fails due to security issues
- High severity vulnerabilities detected

**Solutions:**

1. **Review Vulnerability Report**
   - Check Checkmarx dashboard
   - Identify specific issues

2. **Fix Vulnerabilities**
   - Update dependencies
   - Apply security patches
   - Refactor vulnerable code

3. **Request Exception (If Appropriate)**
   - Document false positives
   - Get security team approval

4. **Adjust Threshold (Temporary)**
   ```yaml
   failBuildOnNewSeverity: 'Critical'  # Instead of 'High'
   ```

---

## Common Error Messages

### "Stack is in UPDATE_ROLLBACK_FAILED state"

**Solution:**
```bash
aws cloudformation continue-update-rollback --stack-name STACK_NAME
# Or
aws cloudformation delete-stack --stack-name STACK_NAME
```

### "Rate exceeded"

**Solution:**
```bash
# Wait and retry
sleep 60
cdk deploy --force
```

### "Token has expired"

**Solution:**
```bash
# Refresh AWS credentials
aws sso login
# Or
aws sts get-session-token
```

### "No default VPC"

**Solution:**
```typescript
// Explicitly specify VPC
vpc: ec2.Vpc.fromLookup(this, 'VPC', {
  vpcId: 'vpc-xxxxx'
})
```

---

## Getting Help

If you continue to experience issues:

1. **Check Framework Documentation**
   - Review README.md
   - Check setup-guide.md
   - Review examples/

2. **Search Existing Issues**
   - Check Azure DevOps work items
   - Review framework repository issues

3. **Contact Support**
   - DevOps team: devops@company.com
   - Teams channel: #pipeline-framework
   - Create work item with:
     - Error message
     - Stack trace
     - Steps to reproduce
     - Environment details

4. **Enable Debug Logging**
   ```bash
   # CDK
   cdk synth --verbose
   
   # Azure DevOps
   system.debug: true
   ```

---

## Prevention Tips

1. **Always Test in Dev First**
   - Never deploy directly to production
   - Validate changes in test environment

2. **Use Version Control**
   - Commit cdk.out for review
   - Track infrastructure changes

3. **Monitor Deployments**
   - Watch CloudFormation events
   - Check CloudWatch logs

4. **Keep Dependencies Updated**
   - Regular CDK updates
   - Security patches

5. **Follow Naming Conventions**
   - Use framework standards
   - Avoid special characters

6. **Document Custom Changes**
   - Note deviations from framework
   - Explain customizations
