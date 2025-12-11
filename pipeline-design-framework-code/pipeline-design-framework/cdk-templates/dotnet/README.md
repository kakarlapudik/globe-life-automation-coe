# .NET PipelineStack Template

This directory contains the .NET CDK PipelineStack template for the Pipeline Design Framework.

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

- .NET 6.0 or later
- AWS CDK 2.x for .NET
- AWS CLI configured

## Installation

```bash
dotnet add package Amazon.CDK.Lib
dotnet add package Constructs
```

## Usage

### Basic Example

```csharp
using Amazon.CDK;
using PipelineFramework;

var app = new App();

new PipelineStack(app, "MyPipeline", new PipelineStackProps
{
    AppName = "myapp",
    StackId = "dev",
    SourceRepo = "my-repo",
    SourceBranch = "main",
    Env = new Environment
    {
        Account = System.Environment.GetEnvironmentVariable("CDK_DEFAULT_ACCOUNT"),
        Region = System.Environment.GetEnvironmentVariable("CDK_DEFAULT_REGION")
    }
});

app.Synth();
```

### With Permissions Boundary

```csharp
new PipelineStack(app, "MyPipeline", new PipelineStackProps
{
    AppName = "myapp",
    StackId = "dev",
    SourceRepo = "my-repo",
    PermissionsBoundary = "arn:aws:iam::123456789012:policy/PermissionsBoundary",
    Env = new Environment
    {
        Account = System.Environment.GetEnvironmentVariable("CDK_DEFAULT_ACCOUNT"),
        Region = System.Environment.GetEnvironmentVariable("CDK_DEFAULT_REGION")
    }
});
```

### With Custom Environment Variables

```csharp
new PipelineStack(app, "MyPipeline", new PipelineStackProps
{
    AppName = "myapp",
    StackId = "dev",
    SourceRepo = "my-repo",
    EnvironmentVariables = new Dictionary<string, string>
    {
        ["DOTNET_VERSION"] = "6.0",
        ["BUILD_CONFIGURATION"] = "Release",
        ["CUSTOM_VAR"] = "custom-value"
    },
    Env = new Environment
    {
        Account = System.Environment.GetEnvironmentVariable("CDK_DEFAULT_ACCOUNT"),
        Region = System.Environment.GetEnvironmentVariable("CDK_DEFAULT_REGION")
    }
});
```

## Configuration

### Required Properties

| Property | Type | Description |
|----------|------|-------------|
| `AppName` | string | Application name (used as qualifier) |
| `StackId` | string | Stack identifier for naming |
| `SourceRepo` | string | Source repository name |

### Optional Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SourceBranch` | string | `"main"` | Source branch name |
| `BuildSpecPath` | string | `"buildspec.yml"` | Path to buildspec file |
| `PermissionsBoundary` | string | `null` | IAM permissions boundary ARN |
| `EnvironmentVariables` | Dictionary<string, string> | `null` | Additional environment variables |

## Naming Conventions

The stack follows these naming conventions:

- **Stack Name**: `PipelineStack{AppName}{StackId}`
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
├── src/
│   ├── Program.cs             # CDK app entry point
│   ├── PipelineStack.cs       # Import from framework
│   └── ApplicationStack.cs    # Your application stack
├── buildspec.yml              # CodeBuild build specification
├── cdk.json                   # CDK configuration
└── MyApp.csproj               # .NET project file
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
| `APP_NAME is required in PipelineStackProps` | Missing AppName property | Provide AppName in stack props |
| `STACK_ID is required in PipelineStackProps` | Missing StackId property | Provide StackId in stack props |

## Integration with Framework

This template is part of the Pipeline Design Framework and integrates with:

- Azure Pipeline templates (`azure-pipelines/cdk-deploy-template.yml`)
- Security scanning templates (`azure-pipelines/security-scan-template.yml`)
- Application stack templates (`cdk-templates/dotnet/ApplicationStack.cs`)

## Best Practices

1. **Use Environment Variables**: Pass configuration via environment variables
2. **Pin CDK Version**: Use specific CDK version in .csproj
3. **Test Locally**: Use `cdk synth` to validate before deployment
4. **Version Control**: Commit cdk.out to track CloudFormation changes
5. **Permissions Boundaries**: Always use permissions boundaries in production

## Troubleshooting

### Stack Name Too Long

If your stack name exceeds AWS limits, shorten the AppName or StackId.

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
