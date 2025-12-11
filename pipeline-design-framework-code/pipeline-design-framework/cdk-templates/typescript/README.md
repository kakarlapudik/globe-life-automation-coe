# TypeScript PipelineStack Template

This directory contains the TypeScript CDK PipelineStack template for the Pipeline Design Framework.

## Overview

The `PipelineStack` class provides a reusable CDK stack that creates AWS CodePipeline infrastructure with integrated security, naming conventions, and permissions boundaries.

## Features

- ✅ **DefaultStackSynthesizer**: Uses custom qualifier based on app name
- ✅ **Environment Variable Validation**: Validates required APP_NAME and STACK_ID
- ✅ **RoleNamingConventionAspect**: Enforces consistent IAM role naming
- ✅ **Permissions Boundaries**: Automatically applies IAM permissions boundaries
- ✅ **Encryption**: KMS encryption for pipeline artifacts
- ✅ **Tagging**: Automatic resource tagging for governance

## Requirements

- Node.js 18.x or later
- AWS CDK 2.x
- TypeScript 4.x or later

## Installation

```bash
npm install aws-cdk-lib constructs
```

## Usage

### Basic Example

```typescript
import * as cdk from 'aws-cdk-lib';
import { PipelineStack } from './pipeline-stack';

const app = new cdk.App();

new PipelineStack(app, 'MyPipeline', {
  appName: 'myapp',
  stackId: 'dev',
  sourceRepo: 'my-repo',
  sourceBranch: 'main',
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
});

app.synth();
```

### With Permissions Boundary

```typescript
new PipelineStack(app, 'MyPipeline', {
  appName: 'myapp',
  stackId: 'dev',
  sourceRepo: 'my-repo',
  permissionsBoundary: 'arn:aws:iam::123456789012:policy/PermissionsBoundary',
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
});
```

### With Custom Environment Variables

```typescript
new PipelineStack(app, 'MyPipeline', {
  appName: 'myapp',
  stackId: 'dev',
  sourceRepo: 'my-repo',
  environmentVariables: {
    NODE_ENV: 'production',
    BUILD_VERSION: '1.0.0',
    CUSTOM_VAR: 'custom-value'
  },
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION
  }
});
```

## Configuration

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| `appName` | string | Application name (used as qualifier) |
| `stackId` | string | Stack identifier for naming |
| `sourceRepo` | string | Source repository name |

### Optional Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `sourceBranch` | string | `'main'` | Source branch name |
| `buildSpecPath` | string | `'buildspec.yml'` | Path to buildspec file |
| `permissionsBoundary` | string | `undefined` | IAM permissions boundary ARN |
| `environmentVariables` | object | `{}` | Additional environment variables |

## Naming Conventions

The stack follows these naming conventions:

- **Stack Name**: `PipelineStack{appName}{stackId}`
- **IAM Roles**: `{appName}-{stackId}-{purpose}-role`
- **CDK Qualifier**: First 10 chars of `{appName}{stackId}` (lowercase, no hyphens)
- **Pipeline Name**: `{appName}-{stackId}-pipeline`
- **Build Project**: `{appName}-{stackId}-build`
- **Artifact Bucket**: `{appName}-{stackId}-pipeline-artifacts-{accountId}`

## Environment Variables

The following environment variables are automatically set for CodeBuild:

- `APP_NAME`: Application name
- `STACK_ID`: Stack identifier
- `CDK_DEFAULT_REGION`: AWS region
- `PERMISSIONS_BOUNDARY`: Permissions boundary ARN (if provided)

## RoleNamingConventionAspect

The `RoleNamingConventionAspect` automatically:

1. Enforces naming convention on all IAM roles
2. Applies permissions boundaries to all roles (if provided)
3. Ensures consistent role naming across the stack

## Synthesizer Configuration

The stack uses `DefaultStackSynthesizer` with custom configuration:

- **Qualifier**: Derived from app name and stack ID
- **Asset Buckets**: Named with qualifier for uniqueness
- **Execution Roles**: Named with qualifier for cross-account support

## Example Project Structure

```
my-cdk-app/
├── bin/
│   └── app.ts                 # CDK app entry point
├── lib/
│   ├── pipeline-stack.ts      # Import from framework
│   └── application-stack.ts   # Your application stack
├── buildspec.yml              # CodeBuild build specification
├── cdk.json                   # CDK configuration
├── package.json               # Node.js dependencies
└── tsconfig.json              # TypeScript configuration
```

## Deployment

### Bootstrap CDK

```bash
export APP_NAME=myapp
export STACK_ID=dev
export PERMISSIONS_BOUNDARY=arn:aws:iam::123456789012:policy/PermissionsBoundary

cdk bootstrap \
  --qualifier $(echo "${APP_NAME}${STACK_ID}" | tr '[:upper:]' '[:lower:]' | tr -d '-' | cut -c1-10) \
  --cloudformation-execution-policies "${PERMISSIONS_BOUNDARY}"
```

### Deploy Pipeline

```bash
export APP_NAME=myapp
export STACK_ID=dev
export CDK_DEFAULT_ACCOUNT=123456789012
export CDK_DEFAULT_REGION=us-west-2

cdk deploy
```

## Validation

The stack validates:

- ✅ APP_NAME is provided
- ✅ STACK_ID is provided
- ✅ Qualifier is valid (max 10 characters)
- ✅ All IAM roles follow naming convention
- ✅ Permissions boundaries are applied (if configured)

## Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `APP_NAME is required in PipelineStackProps` | Missing appName property | Provide appName in stack props |
| `STACK_ID is required in PipelineStackProps` | Missing stackId property | Provide stackId in stack props |

## Integration with Framework

This template is part of the Pipeline Design Framework and integrates with:

- Azure Pipeline templates (`azure-pipelines/cdk-deploy-template.yml`)
- Security scanning templates (`azure-pipelines/security-scan-template.yml`)
- Application stack templates (`cdk-templates/typescript/application-stack.ts`)

## Best Practices

1. **Use Environment Variables**: Pass configuration via environment variables
2. **Pin CDK Version**: Use specific CDK version in package.json
3. **Test Locally**: Use `cdk synth` to validate before deployment
4. **Version Control**: Commit cdk.out to track CloudFormation changes
5. **Permissions Boundaries**: Always use permissions boundaries in production

## Troubleshooting

### Stack Name Too Long

If your stack name exceeds AWS limits, shorten the appName or stackId.

### Qualifier Conflicts

If you get qualifier conflicts, ensure each app+stack combination is unique.

### Role Creation Failures

Check that your permissions boundary allows the required IAM actions.

## Support

For issues or questions:

1. Check the main framework documentation
2. Review the example applications
3. Contact the DevOps team

## Version History

- **1.0.0** (2024-01): Initial release with core functionality
