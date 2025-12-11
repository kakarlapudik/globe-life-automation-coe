# Pipeline Design Framework - Setup Guide

This guide walks you through setting up the Pipeline Design Framework for your application repository.

## Prerequisites

Before you begin, ensure you have:

### 1. Azure DevOps Access
- Access to your Azure DevOps project
- Permissions to create and modify pipelines
- Ability to create variable groups

### 2. AWS Account Setup
- AWS account with appropriate permissions
- IAM permissions boundary ARN from your organization
- AWS CLI installed and configured locally

### 3. Development Tools
- **Node.js 18+**: Required for AWS CDK CLI
- **AWS CDK CLI**: Install globally with `npm install -g aws-cdk`
- **Platform-specific tools**:
  - Python 3.9+ (for Python CDK apps)
  - TypeScript 4.x+ (for TypeScript CDK apps)
  - .NET 6+ (for .NET CDK apps)

## Step 1: Configure Azure DevOps

### 1.1 Create AWS Service Connection

1. Navigate to **Project Settings** → **Service connections**
2. Click **New service connection** → **AWS**
3. Configure the connection:
   - **Connection name**: `AWS-YourEnvironment` (e.g., `AWS-Production`)
   - **Access Key ID**: Your AWS access key
   - **Secret Access Key**: Your AWS secret key
   - **Assume Role ARN** (if applicable): Your deployment role ARN
4. Click **Save**

### 1.2 Create Checkmarx Service Connection

1. Navigate to **Project Settings** → **Service connections**
2. Click **New service connection** → **Checkmarx**
3. Configure the connection:
   - **Connection name**: `Checkmarx-Connection`
   - **Server URL**: Your Checkmarx server URL
   - **Username**: Your Checkmarx username
   - **Password**: Your Checkmarx password
4. Click **Save**

### 1.3 Create Variable Group

1. Navigate to **Pipelines** → **Library**
2. Click **+ Variable group**
3. Name it `{your-app}-deployment-variables`
4. Add the following variables:

| Variable Name | Value | Secret? |
|--------------|-------|---------|
| `APP_NAME` | Your application name (e.g., `my-app`) | No |
| `STACK_ID` | Environment identifier (e.g., `prod`, `dev`) | No |
| `PERMISSIONS_BOUNDARY` | Your IAM permissions boundary ARN | No |
| `AWS_SERVICE_CONNECTION` | Name of your AWS service connection | No |
| `CHECKMARX_TEAM` | Your Checkmarx team name | No |
| `CDK_DEFAULT_REGION` | AWS region (e.g., `us-west-2`) | No |
| `APPROVAL_SNS_TOPIC` | (Optional) SNS topic ARN for notifications | No |

5. Click **Save**

## Step 2: Set Up Your Repository

### 2.1 Add Framework Reference

Create or update your `azure-pipelines.yml`:

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop

resources:
  repositories:
    - repository: pipeline-framework
      type: git
      name: 'Pipeline-Design-Framework'
      ref: 'refs/heads/main'  # or pin to a version tag

variables:
  - group: '{your-app}-deployment-variables'

pool:
  vmImage: 'ubuntu-latest'
```

### 2.2 Create Infrastructure Directory

```bash
mkdir -p infrastructure
cd infrastructure
```

### 2.3 Initialize CDK Application

**For Python**:
```bash
cdk init app --language python
pip install -r requirements.txt
```

**For TypeScript**:
```bash
cdk init app --language typescript
npm install
```

**For .NET**:
```bash
cdk init app --language csharp
dotnet restore
```

### 2.4 Copy Framework Templates

Copy the appropriate stack templates from the framework:

**Python**:
```bash
cp ../pipeline-design-framework/cdk-templates/python/pipeline_stack.py ./
cp ../pipeline-design-framework/cdk-templates/python/application_stack.py ./
```

**TypeScript**:
```bash
cp ../pipeline-design-framework/cdk-templates/typescript/pipeline-stack.ts ./lib/
cp ../pipeline-design-framework/cdk-templates/typescript/application-stack.ts ./lib/
```

**. NET**:
```bash
cp ../pipeline-design-framework/cdk-templates/dotnet/PipelineStack.cs ./src/
cp ../pipeline-design-framework/cdk-templates/dotnet/ApplicationStack.cs ./src/
```

## Step 3: Configure Your CDK Application

### 3.1 Update CDK App Entry Point

**Python (`app.py`)**:
```python
#!/usr/bin/env python3
import os
import aws_cdk as cdk
from pipeline_stack import PipelineStack
from application_stack import ApplicationStack

app = cdk.App()

# Get configuration from environment variables
app_name = os.getenv('APP_NAME', 'my-app')
stack_id = os.getenv('STACK_ID', 'dev')
permissions_boundary = os.getenv('PERMISSIONS_BOUNDARY')

# Create pipeline stack
pipeline = PipelineStack(
    app, f"{app_name}-{stack_id}-pipeline",
    app_name=app_name,
    stack_id=stack_id,
    source_repo="your-repo-name",
    source_branch="main",
    permissions_boundary=permissions_boundary,
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION', 'us-west-2')
    )
)

# Create application stack
application = ApplicationStack(
    app, f"{app_name}-{stack_id}-app",
    app_name=app_name,
    stack_id=stack_id,
    environment_name=stack_id,
    permissions_boundary=permissions_boundary,
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION', 'us-west-2')
    )
)

app.synth()
```

### 3.2 Create requirements.txt (Python only)

```txt
aws-cdk-lib==2.100.0
constructs>=10.0.0,<11.0.0
```

### 3.3 Create cdk.json

```json
{
  "app": "python app.py",
  "watch": {
    "include": [
      "**"
    ],
    "exclude": [
      "README.md",
      "cdk*.json",
      "requirements*.txt",
      "source.bat",
      "**/__init__.py",
      "**/__pycache__",
      "tests"
    ]
  },
  "context": {
    "@aws-cdk/aws-lambda:recognizeLayerVersion": true,
    "@aws-cdk/core:checkSecretUsage": true,
    "@aws-cdk/core:target-partitions": [
      "aws",
      "aws-cn"
    ],
    "@aws-cdk-containers/ecs-service-extensions:enableDefaultLogDriver": true,
    "@aws-cdk/aws-ec2:uniqueImdsv2TemplateName": true,
    "@aws-cdk/aws-ecs:arnFormatIncludesClusterName": true,
    "@aws-cdk/aws-iam:minimizePolicies": true,
    "@aws-cdk/core:validateSnapshotRemovalPolicy": true,
    "@aws-cdk/aws-codepipeline:crossAccountKeyAliasStackSafeResourceName": true,
    "@aws-cdk/aws-s3:createDefaultLoggingPolicy": true,
    "@aws-cdk/aws-sns-subscriptions:restrictSqsDescryption": true,
    "@aws-cdk/aws-apigateway:disableCloudWatchRole": true,
    "@aws-cdk/core:enablePartitionLiterals": true,
    "@aws-cdk/aws-events:eventsTargetQueueSameAccount": true,
    "@aws-cdk/aws-iam:standardizedServicePrincipals": true,
    "@aws-cdk/aws-ecs:disableExplicitDeploymentControllerForCircuitBreaker": true,
    "@aws-cdk/aws-iam:importedRoleStackSafeDefaultPolicyName": true,
    "@aws-cdk/aws-s3:serverAccessLogsUseBucketPolicy": true,
    "@aws-cdk/aws-route53-patters:useCertificate": true,
    "@aws-cdk/customresources:installLatestAwsSdkDefault": false,
    "@aws-cdk/aws-rds:databaseProxyUniqueResourceName": true,
    "@aws-cdk/aws-codedeploy:removeAlarmsFromDeploymentGroup": true,
    "@aws-cdk/aws-apigateway:authorizerChangeDeploymentLogicalId": true,
    "@aws-cdk/aws-ec2:launchTemplateDefaultUserData": true,
    "@aws-cdk/aws-secretsmanager:useAttachedSecretResourcePolicyForSecretTargetAttachments": true,
    "@aws-cdk/aws-redshift:columnId": true,
    "@aws-cdk/aws-stepfunctions-tasks:enableEmrServicePolicyV2": true,
    "@aws-cdk/aws-ec2:restrictDefaultSecurityGroup": true,
    "@aws-cdk/aws-apigateway:requestValidatorUniqueId": true,
    "@aws-cdk/aws-kms:aliasNameRef": true,
    "@aws-cdk/aws-autoscaling:generateLaunchTemplateInsteadOfLaunchConfig": true,
    "@aws-cdk/core:includePrefixInUniqueNameGeneration": true,
    "@aws-cdk/aws-efs:denyAnonymousAccess": true,
    "@aws-cdk/aws-opensearchservice:enableOpensearchMultiAzWithStandby": true,
    "@aws-cdk/aws-lambda-nodejs:useLatestRuntimeVersion": true,
    "@aws-cdk/aws-efs:mountTargetOrderInsensitiveLogicalId": true,
    "@aws-cdk/aws-rds:auroraClusterChangeScopeOfInstanceParameterGroupWithEachParameters": true,
    "@aws-cdk/aws-appsync:useArnForSourceApiAssociationIdentifier": true,
    "@aws-cdk/aws-rds:preventRenderingDeprecatedCredentials": true,
    "@aws-cdk/aws-codepipeline-actions:useNewDefaultBranchForCodeCommitSource": true,
    "@aws-cdk/aws-cloudwatch-actions:changeLambdaPermissionLogicalIdForLambdaAction": true,
    "@aws-cdk/aws-codepipeline:crossAccountKeysDefaultValueToFalse": true,
    "@aws-cdk/aws-codepipeline:defaultPipelineTypeToV2": true,
    "@aws-cdk/aws-kms:reduceCrossAccountRegionPolicyScope": true,
    "@aws-cdk/aws-eks:nodegroupNameAttribute": true,
    "@aws-cdk/aws-ec2:ebsDefaultGp3Volume": true,
    "@aws-cdk/aws-ecs:removeDefaultDeploymentAlarm": true,
    "@aws-cdk/custom-resources:logApiResponseDataPropertyTrueDefault": false,
    "@aws-cdk/aws-s3:keepNotificationInImportedBucket": false
  }
}
```

## Step 4: Configure Your Pipeline

### 4.1 Add Deployment Stage

Add this to your `azure-pipelines.yml`:

```yaml
stages:
  # Security Scanning (on PR only)
  - stage: SecurityScan
    displayName: 'Security Scanning'
    condition: eq(variables['Build.Reason'], 'PullRequest')
    jobs:
      - template: azure-pipelines/security-scan-template.yml@pipeline-framework
        parameters:
          checkmarxTeam: $(CHECKMARX_TEAM)
          sourceDirectory: './'
          excludePatterns: '*.min.js,node_modules/**,*.log,venv/**'
  
  # Deployment
  - stage: Deploy
    displayName: 'Deploy Infrastructure'
    dependsOn: []
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - template: azure-pipelines/cdk-deploy-template.yml@pipeline-framework
        parameters:
          appName: $(APP_NAME)
          stackId: $(STACK_ID)
          appDir: './infrastructure'
          permissionsBoundary: $(PERMISSIONS_BOUNDARY)
          awsServiceConnection: $(AWS_SERVICE_CONNECTION)
          platform: 'python'  # or 'typescript' or 'dotnet'
          cdkDefaultRegion: $(CDK_DEFAULT_REGION)
          actionType: 'deploy'
          approvalNotification: $(APPROVAL_SNS_TOPIC)
```

## Step 5: Test Your Setup

### 5.1 Test Locally

```bash
cd infrastructure

# Set environment variables
export APP_NAME="my-app"
export STACK_ID="dev"
export PERMISSIONS_BOUNDARY="arn:aws:iam::123456789012:policy/BoundaryPolicy"
export CDK_DEFAULT_REGION="us-west-2"

# Synthesize CDK app
cdk synth

# (Optional) Deploy locally
cdk deploy --all
```

### 5.2 Commit and Push

```bash
git add .
git commit -m "Add Pipeline Design Framework integration"
git push origin main
```

### 5.3 Monitor Pipeline

1. Navigate to **Pipelines** in Azure DevOps
2. Find your pipeline
3. Monitor the execution
4. Check for any errors in the logs

## Step 6: Verify Deployment

### 6.1 Check CloudFormation Stacks

```bash
aws cloudformation list-stacks \
  --stack-status-filter CREATE_COMPLETE UPDATE_COMPLETE \
  --query "StackSummaries[?contains(StackName, 'my-app')].{Name:StackName,Status:StackStatus}" \
  --output table
```

### 6.2 Verify Resources

Check that your resources were created with correct naming:
- IAM roles follow pattern: `{appName}-{stackId}-{purpose}-role`
- S3 buckets follow pattern: `{appName}-{stackId}-{purpose}-{accountId}`
- Permissions boundaries are attached to all IAM roles

## Troubleshooting

### Common Issues

**Issue**: CDK bootstrap fails
- **Solution**: Ensure your AWS credentials have sufficient permissions
- Check that the permissions boundary allows CDK bootstrap operations

**Issue**: Pipeline fails with "Missing required parameters"
- **Solution**: Verify all required variables are set in your variable group
- Check variable names match exactly (case-sensitive)

**Issue**: IAM role creation fails
- **Solution**: Verify permissions boundary ARN is correct
- Ensure your AWS account allows role creation with boundaries

**Issue**: Security scan fails
- **Solution**: Check Checkmarx service connection is configured correctly
- Verify your code doesn't have critical vulnerabilities

For more troubleshooting help, see [Troubleshooting Guide](troubleshooting.md).

## Next Steps

- Review the [Epic Repository Example](../examples/epic-repository/) for a complete reference
- Read about [Security Integration](security-integration.md)
- Learn about [AWS Configuration](aws-configuration.md)
- Explore [Multi-Stack Deployments](multi-stack-deployments.md)

## Support

For questions or issues:
1. Check the troubleshooting guide
2. Review example implementations
3. Contact the DevOps team
