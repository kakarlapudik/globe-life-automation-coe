# Permissions Boundary Setup Guide

## Overview

This guide explains how to set up and use IAM permissions boundaries with the Pipeline Design Framework. Permissions boundaries are a critical security control that sets the maximum permissions an IAM entity can have, regardless of the permissions granted by identity-based policies.

## What is a Permissions Boundary?

A permissions boundary is an advanced feature for using a managed policy to set the maximum permissions that an identity-based policy can grant to an IAM entity. When you set a permissions boundary for an entity, the entity can perform only the actions that are allowed by both its identity-based policies AND its permissions boundary.

## Prerequisites

Before implementing permissions boundaries, ensure you have:

1. AWS account with appropriate IAM permissions
2. Understanding of your organization's security requirements
3. Existing IAM managed policy to use as the boundary (or ability to create one)

## Creating a Permissions Boundary Policy

### Step 1: Define Your Boundary Policy

Create an IAM managed policy that defines the maximum permissions. Example:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowedServices",
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "dynamodb:*",
        "lambda:*",
        "cloudformation:*",
        "codepipeline:*",
        "codebuild:*",
        "logs:*",
        "kms:*"
      ],
      "Resource": "*"
    },
    {
      "Sid": "DenyDangerousActions",
      "Effect": "Deny",
      "Action": [
        "iam:CreateUser",
        "iam:DeleteUser",
        "iam:CreateAccessKey",
        "organizations:*",
        "account:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Step 2: Create the Policy in AWS

Using AWS CLI:

```bash
aws iam create-policy \
  --policy-name MyAppPermissionsBoundary \
  --policy-document file://permissions-boundary-policy.json \
  --description "Permissions boundary for MyApp CDK deployments"
```

Using AWS Console:
1. Navigate to IAM → Policies
2. Click "Create policy"
3. Use JSON editor to paste your policy
4. Name it (e.g., "MyAppPermissionsBoundary")
5. Create the policy

### Step 3: Note the Policy ARN

After creation, note the ARN:
```
arn:aws:iam::123456789012:policy/MyAppPermissionsBoundary
```

## Configuring Framework to Use Permissions Boundary

### Python CDK

```python
from pipeline_stack import PipelineStack

pipeline_stack = PipelineStack(
    app,
    "MyAppPipeline",
    app_name="myapp",
    stack_id="prod",
    source_repo="my-repo",
    permissions_boundary="arn:aws:iam::123456789012:policy/MyAppPermissionsBoundary",
    env=env
)
```

### TypeScript CDK

```typescript
import { PipelineStack } from './pipeline-stack';

new PipelineStack(app, 'MyAppPipeline', {
  appName: 'myapp',
  stackId: 'prod',
  sourceRepo: 'my-repo',
  permissionsBoundary: 'arn:aws:iam::123456789012:policy/MyAppPermissionsBoundary',
  env: env
});
```

### .NET CDK

```csharp
using PipelineDesignFramework;

new PipelineStack(app, "MyAppPipeline", new PipelineStackProps
{
    AppName = "myapp",
    StackId = "prod",
    SourceRepo = "my-repo",
    PermissionsBoundary = "arn:aws:iam::123456789012:policy/MyAppPermissionsBoundary",
    Env = env
});
```

### Azure DevOps Pipeline Variables

Add the permissions boundary ARN to your Azure DevOps variable group:

```yaml
variables:
  - group: myapp-deployment-variables
  - name: PERMISSIONS_BOUNDARY_ARN
    value: 'arn:aws:iam::123456789012:policy/MyAppPermissionsBoundary'
```

Then reference it in your pipeline:

```yaml
- template: azure-pipelines/cdk-deploy-template.yml@framework
  parameters:
    stackName: 'MyAppPipeline'
    cdkCommand: 'deploy'
    environmentVariables:
      PERMISSIONS_BOUNDARY: $(PERMISSIONS_BOUNDARY_ARN)
```

## How the Framework Applies Permissions Boundaries

The framework automatically applies permissions boundaries to all IAM roles created by your CDK stacks through the `RoleNamingConventionAspect`:

1. **Automatic Application**: When you provide a `permissionsBoundary` parameter, the framework's aspect automatically attaches it to every IAM role created in your stack.

2. **Naming Convention**: Roles are named following the pattern: `{app-name}-{stack-id}-{purpose}-role`

3. **Environment Variable**: The boundary ARN is also set as an environment variable (`PERMISSIONS_BOUNDARY`) for use in build processes.

## Validation and Testing

### Verify Boundary is Applied

After deployment, verify the boundary is attached:

```bash
# List roles with your app name
aws iam list-roles --query "Roles[?contains(RoleName, 'myapp')].RoleName"

# Check specific role for boundary
aws iam get-role --role-name myapp-prod-build-role \
  --query "Role.PermissionsBoundary.PermissionsBoundaryArn"
```

### Test Boundary Enforcement

Try to perform an action outside the boundary:

```bash
# This should fail if the boundary denies it
aws iam create-user --user-name test-user \
  --role-name myapp-prod-build-role
```

## Bootstrap Considerations

When bootstrapping CDK with permissions boundaries, use the `--custom-permissions-boundary` flag:

```bash
cdk bootstrap aws://123456789012/us-east-1 \
  --custom-permissions-boundary MyAppPermissionsBoundary \
  --qualifier myappprod
```

This ensures that even the CDK bootstrap roles respect the permissions boundary.

## Common Patterns

### Development vs Production Boundaries

Use different boundaries for different environments:

```python
# Development - more permissive
dev_boundary = "arn:aws:iam::123456789012:policy/DevPermissionsBoundary"

# Production - more restrictive
prod_boundary = "arn:aws:iam::123456789012:policy/ProdPermissionsBoundary"

PipelineStack(
    app,
    "MyAppPipeline",
    app_name="myapp",
    stack_id="dev" if is_dev else "prod",
    permissions_boundary=dev_boundary if is_dev else prod_boundary
)
```

### Service-Specific Boundaries

Create boundaries for specific AWS services:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LambdaOnly",
      "Effect": "Allow",
      "Action": [
        "lambda:*",
        "logs:*",
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "*"
    }
  ]
}
```

## Troubleshooting

### Error: "User is not authorized to perform: iam:PutRolePermissionsBoundary"

**Solution**: Ensure your deployment role has permission to attach permissions boundaries:

```json
{
  "Effect": "Allow",
  "Action": [
    "iam:PutRolePermissionsBoundary",
    "iam:DeleteRolePermissionsBoundary"
  ],
  "Resource": "*"
}
```

### Error: "Cannot exceed permissions boundary"

**Solution**: The action you're trying to perform is not allowed by the permissions boundary. Either:
1. Update the boundary policy to allow the action
2. Remove the action from your role's policies

### Boundary Not Applied to Existing Roles

**Solution**: Permissions boundaries are only applied during role creation. To apply to existing roles:

```bash
aws iam put-role-permissions-boundary \
  --role-name myapp-prod-build-role \
  --permissions-boundary arn:aws:iam::123456789012:policy/MyAppPermissionsBoundary
```

## Best Practices

1. **Start Restrictive**: Begin with a restrictive boundary and gradually add permissions as needed.

2. **Use Deny Statements**: Explicitly deny dangerous actions in your boundary policy.

3. **Environment-Specific**: Use different boundaries for dev, staging, and production.

4. **Regular Audits**: Periodically review and update boundary policies.

5. **Document Exceptions**: If you need to bypass the boundary, document why and get approval.

6. **Test in Dev First**: Always test boundary changes in development before applying to production.

7. **Monitor Denied Actions**: Use CloudTrail to monitor actions denied by the boundary.

## Security Considerations

- Permissions boundaries do NOT grant permissions; they only limit them
- The effective permissions are the intersection of identity policies AND the boundary
- Boundaries cannot be used to escalate privileges
- Only users with `iam:PutRolePermissionsBoundary` can attach boundaries
- Boundaries apply to roles, not to the users who assume them

## References

- [AWS IAM Permissions Boundaries](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_boundaries.html)
- [CDK Bootstrap with Permissions Boundary](https://docs.aws.amazon.com/cdk/v2/guide/bootstrapping.html)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

## Support

For questions or issues with permissions boundaries in the framework:
1. Check the troubleshooting section above
2. Review CloudTrail logs for denied actions
3. Consult with your security team
4. Contact the framework maintainers
