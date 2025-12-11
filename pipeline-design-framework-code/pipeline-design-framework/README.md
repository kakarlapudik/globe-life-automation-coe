# Pipeline Design Framework

A modular, reusable framework for AWS CDK deployments via Azure DevOps pipelines with built-in security scanning and compliance enforcement.

## Overview

This framework provides standardized, reusable Azure Pipeline templates and CDK stack templates that enable teams to quickly set up secure, compliant CI/CD pipelines for AWS deployments. The framework enforces organizational standards while remaining flexible enough to accommodate application-specific requirements.

## Key Features

- **Modular Azure Pipeline Templates**: Reusable YAML templates for CDK deployment, security scanning, and multi-stack deployments
- **Multi-Platform CDK Support**: Templates for Python, TypeScript, and .NET CDK applications
- **Security Integration**: Built-in Checkmarx SAST/SCA scanning with configurable policies
- **Compliance Enforcement**: Automatic IAM permissions boundary and naming convention enforcement
- **Multi-Stack Support**: Deploy complex applications with multiple interdependent stacks
- **Version Control**: Git-based versioning allows teams to pin to specific framework versions

## Quick Start

### Prerequisites

1. **Azure DevOps**:
   - Azure DevOps project with pipeline permissions
   - AWS service connection configured
   - Checkmarx service connection (for security scanning)

2. **AWS Account**:
   - AWS account with appropriate permissions
   - IAM permissions boundary ARN
   - CDK bootstrap completed (framework can handle this)
   - **AWS credentials configured** - See [AWS Credentials Setup Guide](docs/aws-credentials-setup.md)

3. **Development Environment**:
   - Node.js 18+ (for CDK CLI)
   - Python 3.9+ / TypeScript 4.x / .NET 6+ (depending on your platform)
   - AWS CDK CLI installed globally
   - AWS CLI v2 installed and configured

### AWS Credentials Setup

Before deploying, configure your AWS credentials:

**Automated Setup (Recommended):**
```bash
# Linux/Mac
./scripts/setup-aws-credentials.sh

# Windows PowerShell
.\scripts\setup-aws-credentials.ps1
```

**Manual Setup:**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your AWS credentials
# See docs/aws-credentials-setup.md for detailed instructions
```

**Verify Configuration:**
```bash
# Test AWS credentials
aws sts get-caller-identity

# Test CDK
cdk --version
```

For detailed instructions, see the [AWS Credentials Setup Guide](docs/aws-credentials-setup.md)

### Basic Setup

1. **Reference the framework in your repository**:

```yaml
# azure-pipelines.yml
resources:
  repositories:
    - repository: pipeline-framework
      type: git
      name: 'Pipeline-Design-Framework'
      ref: 'refs/heads/main'  # or pin to a specific version tag
```

2. **Use framework templates**:

```yaml
stages:
  - stage: Deploy
    jobs:
      - template: azure-pipelines/cdk-deploy-template.yml@pipeline-framework
        parameters:
          appName: 'my-app'
          stackId: 'production'
          appDir: './infrastructure'
          permissionsBoundary: $(PERMISSIONS_BOUNDARY)
          awsServiceConnection: $(AWS_SERVICE_CONNECTION)
          platform: 'python'
```

3. **Configure your CDK app** using framework templates (see examples/)

## Framework Structure

```
pipeline-design-framework/
├── azure-pipelines/          # Reusable Azure Pipeline templates
│   ├── cdk-deploy-template.yml
│   ├── security-scan-template.yml
│   └── multi-stack-template.yml
├── cdk-templates/            # CDK stack templates by platform
│   ├── python/
│   │   ├── pipeline_stack.py
│   │   └── application_stack.py
│   ├── typescript/
│   │   ├── pipeline-stack.ts
│   │   └── application-stack.ts
│   └── dotnet/
│       ├── PipelineStack.cs
│       └── ApplicationStack.cs
├── docs/                     # Comprehensive documentation
│   ├── setup-guide.md
│   ├── aws-configuration.md
│   ├── security-integration.md
│   └── troubleshooting.md
└── examples/                 # Reference implementations
    ├── eServiceCenter-repository/  # Primary reference (eServiceCenter V2 Test Automation)
    ├── python-app/
    ├── typescript-app/
    └── dotnet-app/
```

## Core Concepts

### 1. Modular Templates

The framework uses Azure DevOps template references to provide reusable pipeline logic:

- **cdk-deploy-template.yml**: Handles CDK deployment/destruction with parameter validation
- **security-scan-template.yml**: Integrates Checkmarx security scanning
- **multi-stack-template.yml**: Orchestrates deployment of multiple interdependent stacks

### 2. Naming Conventions

All resources follow standardized naming patterns:

- **Stacks**: `{appName}-{stackId}`
- **IAM Roles**: `{appName}-{stackId}-{purpose}-role`
- **S3 Buckets**: `{appName}-{stackId}-{purpose}-{accountId}`
- **CDK Qualifier**: `{appname}{stackid}` (lowercase, no hyphens)

### 3. Permissions Boundary

All IAM roles created by the framework automatically attach the specified permissions boundary, ensuring compliance with organizational security policies.

### 4. Security Scanning

Security scans run automatically on pull requests and can be configured to break builds on policy violations.

## Usage Examples

### Single Stack Deployment

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main

resources:
  repositories:
    - repository: pipeline-framework
      type: git
      name: 'Pipeline-Design-Framework'
      ref: 'refs/tags/v1.0.0'

stages:
  - stage: Deploy
    jobs:
      - template: azure-pipelines/cdk-deploy-template.yml@pipeline-framework
        parameters:
          appName: $(APP_NAME)
          stackId: $(STACK_ID)
          appDir: './infrastructure'
          permissionsBoundary: $(PERMISSIONS_BOUNDARY)
          awsServiceConnection: $(AWS_SERVICE_CONNECTION)
          platform: 'python'
          cdkDefaultRegion: 'us-west-2'
```

### Multi-Stack Deployment

```yaml
stages:
  - template: azure-pipelines/multi-stack-template.yml@pipeline-framework
    parameters:
      appName: 'my-app'
      permissionsBoundary: $(PERMISSIONS_BOUNDARY)
      awsServiceConnection: $(AWS_SERVICE_CONNECTION)
      platform: 'python'
      stacks:
        - stackId: 'pipeline'
          appDir: './infrastructure/pipeline'
          dependsOn: []
        - stackId: 'application'
          appDir: './infrastructure/application'
          dependsOn: ['pipeline']
```

### With Security Scanning

```yaml
stages:
  - stage: SecurityScan
    condition: eq(variables['Build.Reason'], 'PullRequest')
    jobs:
      - template: azure-pipelines/security-scan-template.yml@pipeline-framework
        parameters:
          checkmarxTeam: $(CHECKMARX_TEAM)
          sourceDirectory: './'
          enableSonarQube: true
          sonarQubeConnection: $(SONARQUBE_CONNECTION)
  
  - stage: Deploy
    dependsOn: SecurityScan
    jobs:
      - template: azure-pipelines/cdk-deploy-template.yml@pipeline-framework
        parameters:
          # ... deployment parameters
```

## Configuration

### Required Variables

Configure these in Azure DevOps variable groups:

```yaml
variables:
  - group: 'deployment-variables'
  # Required:
  - APP_NAME: 'your-app-name'
  - STACK_ID: 'environment-identifier'
  - PERMISSIONS_BOUNDARY: 'arn:aws:iam::123456789012:policy/BoundaryPolicy'
  - AWS_SERVICE_CONNECTION: 'AWS-Connection-Name'
  - CHECKMARX_TEAM: 'Your-Team-Name'
  # Optional:
  - CDK_DEFAULT_REGION: 'us-west-2'
  - APPROVAL_SNS_TOPIC: 'arn:aws:sns:...'
```

### CDK Application Setup

Your CDK application should use the framework templates:

**Python Example**:
```python
from pipeline_stack import PipelineStack
from application_stack import ApplicationStack

app = cdk.App()

# Use framework templates
pipeline = PipelineStack(
    app, f"{app_name}-{stack_id}-pipeline",
    app_name=app_name,
    stack_id=stack_id,
    # ... other parameters
)

application = ApplicationStack(
    app, f"{app_name}-{stack_id}-app",
    app_name=app_name,
    stack_id=stack_id,
    # ... other parameters
)

app.synth()
```

## Versioning

The framework uses semantic versioning (v1.0.0, v1.1.0, v2.0.0):

- **Major versions**: Breaking changes requiring application updates
- **Minor versions**: New features, backward compatible
- **Patch versions**: Bug fixes, backward compatible

### Pinning to a Version

```yaml
resources:
  repositories:
    - repository: pipeline-framework
      type: git
      name: 'Pipeline-Design-Framework'
      ref: 'refs/tags/v1.0.0'  # Pin to specific version
```

### Upgrading

1. Review release notes for breaking changes
2. Update your `ref` to the new version
3. Test in a non-production environment
4. Update application code if needed
5. Deploy to production

## Examples

See the `examples/` directory for complete reference implementations:

- **eServiceCenter-repository/**: Primary reference implementation (eServiceCenter V2 Test Automation platform)
- **python-app/**: Simple Python CDK application
- **typescript-app/**: TypeScript CDK application
- **dotnet-app/**: .NET CDK application

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [Setup Guide](docs/setup-guide.md): Detailed setup instructions
- [AWS Configuration](docs/aws-configuration.md): AWS account and permissions setup
- [Security Integration](docs/security-integration.md): Checkmarx and security scanning
- [Troubleshooting](docs/troubleshooting.md): Common issues and solutions

## Support

For questions or issues:

1. Check the [Troubleshooting Guide](docs/troubleshooting.md)
2. Review the [eServiceCenter V2 Repository Example](examples/eServiceCenter-repository/)
3. Contact the DevOps team

## Contributing

To contribute to the framework:

1. Create a feature branch
2. Make your changes
3. Test with example applications
4. Submit a pull request
5. Update documentation as needed

## License

Internal use only - Globe Life Inc.

## Changelog

### v1.0.0 (Initial Release)
- Core Azure Pipeline templates
- Python, TypeScript, and .NET CDK templates
- Security scanning integration
- Multi-stack deployment support
- eServiceCenter V2 repository pilot implementation
- Comprehensive documentation
