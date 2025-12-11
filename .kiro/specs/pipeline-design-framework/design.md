# Design Document

## Introduction

This document outlines the technical design for the Pipeline Design Framework, a comprehensive solution for standardizing CI/CD pipelines across the organization using Azure DevOps, AWS CDK, and AWS CodePipeline. The framework provides reusable pipeline templates, CDK stack templates, and standardized deployment workflows for multi-account AWS deployments with integrated security scanning and compliance controls.

The framework is designed to be **modular and reusable** across multiple application-specific repositories, with the **Epic repository** (https://devops.globelifeinc.com/projects/Test%20Automation/_git/Epic) serving as the **pilot implementation** to validate the approach before organization-wide rollout.

## Architecture Overview

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Developer     │    │   Azure         │    │   Test/Dev      │
│   Repository    │───▶│   DevOps        │───▶│   Account       │
│   (Azure DevOps)│    │   Pipelines     │    │   (AWS)         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture (Modular)

```
Pipeline Design Framework (Central Repository)
├── Azure Pipeline Templates (azure-pipelines/)
│   ├── cdk-deploy-template.yml (reusable template)
│   ├── security-scan-template.yml
│   └── multi-stack-template.yml
├── CDK Stack Templates (cdk-templates/)
│   ├── python/
│   │   ├── pipeline_stack.py
│   │   └── application_stack.py
│   ├── typescript/
│   │   ├── pipeline-stack.ts
│   │   └── application-stack.ts
│   └── dotnet/
│       ├── PipelineStack.cs
│       └── ApplicationStack.cs
├── Documentation (docs/)
│   ├── setup-guide.md
│   ├── configuration-examples.md
│   ├── epic-pilot-guide.md
│   └── troubleshooting.md
└── Examples (examples/)
    ├── epic-repository/ (pilot implementation)
    ├── python-app/
    ├── typescript-app/
    └── dotnet-app/

Application Repositories (Consumers)
├── Epic Repository (Pilot)
│   ├── azure-pipelines.yml (references framework)
│   ├── cdk/ (application-specific CDK code)
│   └── pipeline-config.yml (app-specific config)
└── Other Application Repositories
    ├── azure-pipelines.yml
    ├── cdk/
    └── pipeline-config.yml
```


## Component Design

### 1. Azure Pipeline Template (azure-pipelines.yml)

#### Purpose
Provides a reusable Azure Pipeline template that encapsulates the entire CDK deployment process, ensuring consistency across all repositories.

#### Template Parameters
```yaml
parameters:
  - name: appName
    type: string
    displayName: 'Application name (lowercase, used as CDK qualifier)'
  - name: stackId
    type: string
    displayName: 'Stack identifier for naming'
  - name: appDir
    type: string
    displayName: 'Application directory path'
    default: './'
  - name: permissionsBoundary
    type: string
    displayName: 'IAM permissions boundary ARN'
  - name: awsServiceConnection
    type: string
    displayName: 'AWS service connection name'
  - name: platform
    type: string
    displayName: 'Platform type'
    default: 'python'
    values:
      - python
      - typescript
      - dotnet
  - name: approvalNotification
    type: string
    displayName: 'SNS topic for approval notifications'
    default: ''
  - name: nodeVersion
    type: string
    displayName: 'Node.js version'
    default: '20'
  - name: cdkDefaultRegion
    type: string
    displayName: 'Default AWS region'
    default: 'us-west-2'
  - name: actionType
    type: string
    displayName: 'Action type'
    default: 'deploy'
    values:
      - deploy
      - destroy
```

#### Implementation Steps
1. **Input Validation**: Validate all required parameters and provide clear error messages
2. **Environment Setup**: Configure Node.js, AWS CLI, and CDK CLI using Azure DevOps tasks
3. **AWS Authentication**: Use Azure DevOps AWS service connection for secure authentication
4. **CDK Bootstrap**: Ensure CDK toolkit is properly configured with custom permissions boundaries
5. **Stack Operations**: Support both deployment and destruction of CDK stacks


### 2. PipelineStack Templates

#### Purpose
Provides standardized CDK stack templates that define the AWS CodePipeline infrastructure for each supported platform.

#### TypeScript PipelineStack
```typescript
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import { DefaultStackSynthesizer } from 'aws-cdk-lib';
import { RoleNamingConventionAspect } from './aspects/role-naming-aspect';

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    const appName = process.env.APP_NAME;
    const stackId = process.env.STACK_ID;
    
    if (!appName || !stackId) {
      throw new Error('APP_NAME and STACK_ID environment variables are required');
    }

    super(scope, `PipelineStack${appName}${stackId}`, {
      ...props,
      synthesizer: new DefaultStackSynthesizer({
        qualifier: appName.toLowerCase()
      })
    });

    // Apply naming convention aspect
    cdk.Aspects.of(this).add(new RoleNamingConventionAspect(appName, stackId));

    // Pipeline infrastructure components
    this.createCodePipeline();
    this.createCodeBuildProjects();
  }

  private createCodePipeline() {
    // CodePipeline implementation with source, build, and deploy stages
  }

  private createCodeBuildProjects() {
    // CodeBuild projects for build and deploy stages
  }
}
```


#### Python PipelineStack
```python
from aws_cdk import (
    Stack,
    DefaultStackSynthesizer,
    Aspects
)
from constructs import Construct
import os

class PipelineStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        app_name = os.environ.get('APP_NAME')
        stack_id = os.environ.get('STACK_ID')
        
        if not app_name or not stack_id:
            raise ValueError('APP_NAME and STACK_ID environment variables are required')
        
        super().__init__(
            scope, 
            f'PipelineStack{app_name}{stack_id}',
            synthesizer=DefaultStackSynthesizer(
                qualifier=app_name.lower()
            ),
            **kwargs
        )
        
        # Apply naming convention aspect
        Aspects.of(self).add(RoleNamingConventionAspect(app_name, stack_id))
        
        # Pipeline infrastructure components
        self._create_code_pipeline()
        self._create_code_build_projects()
```

#### .NET PipelineStack
```csharp
using Amazon.CDK;
using Constructs;
using System;

namespace PipelineFramework
{
    public class PipelineStack : Stack
    {
        public PipelineStack(Construct scope, string id, IStackProps props = null) : base(scope, id, props)
        {
            var appName = Environment.GetEnvironmentVariable("APP_NAME");
            var stackId = Environment.GetEnvironmentVariable("STACK_ID");
            
            if (string.IsNullOrEmpty(appName) || string.IsNullOrEmpty(stackId))
            {
                throw new ArgumentException("APP_NAME and STACK_ID environment variables are required");
            }

            var stackProps = new StackProps
            {
                Synthesizer = new DefaultStackSynthesizer(new DefaultStackSynthesizerProps
                {
                    Qualifier = appName.ToLower()
                })
            };

            // Apply naming convention aspect
            Aspects.Of(this).Add(new RoleNamingConventionAspect(appName, stackId));

            // Pipeline infrastructure components
            CreateCodePipeline();
            CreateCodeBuildProjects();
        }
    }
}
```


### 3. ApplicationStack Templates

#### Purpose
Provides standardized application stack templates that developers can use as starting points for their CDK applications.

#### Common Structure (TypeScript Example)
```typescript
export class ApplicationStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    const appName = process.env.APP_NAME;
    const stackId = process.env.STACK_ID;
    
    if (!appName || !stackId) {
      throw new Error('APP_NAME and STACK_ID environment variables are required');
    }
    
    super(scope, `AppStack${appName}${stackId}`, {
      ...props,
      synthesizer: new DefaultStackSynthesizer({
        qualifier: appName.toLowerCase()
      }),
      env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: process.env.CDK_DEFAULT_REGION
      }
    });

    // Application-specific resources
    // Lambda functions, API Gateway, DynamoDB tables, etc.
  }
}
```

#### Key Features
- Uses lowercase app-name as CDK qualifier
- Follows naming convention: AppStack + app_name + stack_id
- Reads account and region from environment variables
- Integrates seamlessly with PipelineStack
- Supports all three platforms (TypeScript, Python, .NET)


### 4. Azure Pipeline Templates

#### Single Stack Pipeline
```yaml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: 'cdk-deployment-variables'

stages:
  - stage: Deploy
    displayName: 'Deploy CDK Application'
    jobs:
      - job: DeployStack
        displayName: 'Deploy Stack'
        steps:
          - checkout: self
          
          - template: templates/cdk-deploy-template.yml
            parameters:
              appName: $(APP_NAME)
              stackId: $(STACK_ID)
              appDir: './'
              permissionsBoundary: $(PERMISSIONS_BOUNDARY)
              awsServiceConnection: $(AWS_SERVICE_CONNECTION)
              platform: 'python'
              approvalNotification: $(APPROVAL_SNS_TOPIC)
```

#### Multi-Stack Pipeline
```yaml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: 'cdk-deployment-variables'

stages:
  - stage: DeployPipeline
    displayName: 'Deploy Pipeline Stack'
    jobs:
      - job: DeployPipelineStack
        displayName: 'Deploy Pipeline Stack'
        steps:
          - checkout: self
          
          - template: templates/cdk-deploy-template.yml
            parameters:
              appName: $(APP_NAME)
              stackId: 'pipeline'
              appDir: './'
              permissionsBoundary: $(PERMISSIONS_BOUNDARY)
              awsServiceConnection: $(AWS_SERVICE_CONNECTION)
              platform: 'python'

  - stage: DeployApplication
    displayName: 'Deploy Application Stack'
    dependsOn: DeployPipeline
    jobs:
      - job: DeployAppStack
        displayName: 'Deploy Application Stack'
        steps:
          - checkout: self
          
          - template: templates/cdk-deploy-template.yml
            parameters:
              appName: $(APP_NAME)
              stackId: 'app'
              appDir: './'
              permissionsBoundary: $(PERMISSIONS_BOUNDARY)
              awsServiceConnection: $(AWS_SERVICE_CONNECTION)
              platform: 'python'
```


### 5. Security Integration

#### Checkmarx SAST/SCA Scanning
```yaml
trigger:
  branches:
    include:
      - '*'
pr:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: 'checkmarx-variables'

stages:
  - stage: SecurityScan
    displayName: 'Security Scanning'
    jobs:
      - job: CheckmarxSAST
        displayName: 'Checkmarx SAST Scan'
        steps:
          - checkout: self
          
          - task: CheckmarxSAST@2
            inputs:
              checkmarxService: $(CHECKMARX_SERVICE_CONNECTION)
              projectName: $(Build.Repository.Name)
              teamName: $(CHECKMARX_TEAM)
              preset: 'Default'
              scanComment: 'Azure DevOps Pipeline Scan'
              failBuildOnNewSeverity: 'High'
              vulnerabilityThreshold: true
      
      - job: CheckmarxSCA
        displayName: 'Checkmarx SCA Scan'
        steps:
          - checkout: self
          
          - task: CheckmarxSCA@1
            inputs:
              checkmarxService: $(CHECKMARX_SERVICE_CONNECTION)
              projectName: $(Build.Repository.Name)
              teamName: $(CHECKMARX_TEAM)
              failBuildOnNewVulnerability: true
```

#### Security Features
- **SAST Scanning**: Static application security testing on all code changes
- **SCA Scanning**: Software composition analysis for dependency vulnerabilities
- **Break Build**: Blocks PR merging when vulnerabilities are detected
- **Baseline Support**: Allows baseline assessment for legacy code
- **Attestation**: Requires verification in CodePipeline before deployment
- **Compliance Reporting**: Maintains audit trails for all scanning activities


## Data Models

### Configuration Schema
```typescript
interface PipelineConfig {
  appName: string;           // Lowercase application name (used as qualifier)
  stackId: string;           // Stack identifier
  platform: 'python' | 'typescript' | 'dotnet';  // Python is preferred
  account: {
    testDev: string;        // Test/Dev account ID
  };
  permissions: {
    boundary: string;        // Permissions boundary ARN
  };
  notifications: {
    approvalTopic?: string;  // SNS topic for approvals
  };
  security: {
    checkmarxTeam: string;   // Checkmarx team name
    scanOnPR: boolean;       // Enable PR scanning
  };
  azureDevOps: {
    serviceConnection: string;  // AWS service connection name in Azure DevOps
  };
}
```

### Environment Variables
```typescript
interface EnvironmentVariables {
  // Required
  APP_NAME: string;              // Application name
  STACK_ID: string;              // Stack identifier
  CDK_DEFAULT_ACCOUNT: string;   // AWS account ID (test/dev)
  CDK_DEFAULT_REGION: string;    // AWS region
}
```

### Naming Conventions
```typescript
interface NamingConventions {
  pipelineStack: string;     // PipelineStack + app_name + stack_id
  applicationStack: string;  // AppStack + app_name + stack_id
  cdkToolkit: string;        // CDKToolkit + app_name
  iamRolePrefix: string;     // PipelineStack + app_name + stack_id
  qualifier: string;         // app_name.toLowerCase()
}
```


## Deployment Flow

### End-to-End Pipeline Execution

```
1. Developer commits code to Azure DevOps repository
   ↓
2. Azure Pipeline triggered
   ↓
3. AWS authentication via Azure DevOps service connection
   ↓
4. CDK Bootstrap test/dev account
   - Create/update CDKToolkit stack
   - Apply permissions boundaries
   - Upload assets to S3
   ↓
5. CDK Deploy PipelineStack
   - Create CodePipeline
   - Create CodeBuild projects
   ↓
6. CodePipeline triggered
   ↓
7. Source stage: Pull code from Azure DevOps
   ↓
8. Build stage: CodeBuild compiles and packages
   ↓
9. Security stage: Checkmarx attestation verification
   ↓
10. Deploy stage:
    - Deploy ApplicationStack via CloudFormation
    ↓
11. Manual approval (if configured)
```

### Deployment Pattern

```
Test/Dev Account
├── AWS Service Connection (from Azure DevOps)
├── Permissions-Boundary
├── CodePipeline
├── CodeBuild
├── S3 (CDK assets)
├── CDKToolkit stack
└── ApplicationStack (deployed via CloudFormation)
```


## Security Design

### Authentication & Authorization

#### Azure DevOps Service Connection
- **AWS Service Connection**: Secure authentication between Azure DevOps and AWS using service principal or IAM role
- **Credential Management**: Azure DevOps manages AWS credentials securely
- **Access Control**: Service connection configured with appropriate IAM permissions
- **Session Duration**: Temporary credentials with limited lifetime

#### Permissions Boundaries
- **Pipeline Account Boundary**: Enforces maximum permissions for all roles in pipeline account
- **Cross-Account Boundary**: Enforces maximum permissions for cross-account deployment roles
- **CloudFormation Execution Policy**: Limits what CloudFormation can create/modify
- **Least Privilege**: All roles granted minimum necessary permissions

#### Role Hierarchy
```
Azure DevOps Service Connection Role
├── Can assume: CodePipeline execution role
├── Boundary: Permissions-Boundary
└── Permissions: CDK bootstrap, deploy, S3 access

CodePipeline Execution Role
├── Can assume: CodeBuild role
├── Boundary: Permissions-Boundary
└── Permissions: Pipeline orchestration

CodeBuild Role
├── Boundary: Permissions-Boundary
└── Permissions: Build, test, deploy, CloudFormation
```

### Security Scanning

#### Checkmarx Integration
- **SAST (Static Application Security Testing)**: Analyzes source code for vulnerabilities
- **SCA (Software Composition Analysis)**: Scans dependencies for known vulnerabilities
- **Break Build**: Automatically blocks PR merging when issues detected
- **Baseline Assessment**: Supports legacy code with baseline vulnerability tracking
- **Incremental Scanning**: Only scans modified code for efficiency

#### Attestation Verification
- **CodePipeline Integration**: Requires Checkmarx attestation before deployment
- **Compliance Gate**: Ensures all code is scanned before reaching production
- **Audit Trail**: Maintains complete history of scan results
- **Reporting**: Generates compliance reports for security audits


## Error Handling

### Input Validation Errors
- **Missing Required Parameters**: Clear error messages indicating which parameters are missing
- **Invalid Platform**: Validation that platform is one of: typescript, python, dotnet
- **Invalid Action Type**: Validation that action-type is either deploy or destroy
- **Malformed ARNs**: Validation of ARN format for roles and boundaries

### Environment Variable Errors
- **Missing APP_NAME**: Throw error with message "APP_NAME environment variable is required"
- **Missing STACK_ID**: Throw error with message "STACK_ID environment variable is required"
- **Missing Account/Region**: Throw error with message "CDK_DEFAULT_ACCOUNT and CDK_DEFAULT_REGION are required"

### AWS Authentication Errors
- **Service Connection Failure**: Retry logic with exponential backoff
- **Role Assumption Failure**: Clear error indicating which role failed to assume
- **Permission Denied**: Detailed error showing which permission is missing
- **Credential Expiration**: Error indicating credentials need to be refreshed

### CDK Errors
- **Bootstrap Failure**: Detailed error with stack trace and remediation steps
- **Synthesis Failure**: Error showing which construct failed to synthesize
- **Deployment Failure**: CloudFormation error details with rollback information
- **Destroy Failure**: Error showing which resources failed to delete

### Security Scanning Errors
- **Checkmarx Connection Failure**: Retry logic with fallback to manual review
- **Scan Timeout**: Configurable timeout with clear error message
- **Attestation Missing**: Block deployment with clear remediation steps
- **Vulnerability Threshold Exceeded**: Detailed report of vulnerabilities found

### Recovery Strategies
- **Automatic Retry**: For transient failures (network, API throttling)
- **Manual Intervention**: For configuration errors requiring human review
- **Rollback**: Automatic CloudFormation rollback on deployment failure
- **Notification**: SNS notifications for critical failures


## Testing Strategy

### Unit Testing

#### Pipeline Template Tests
- **Parameter Validation**: Test all required and optional parameters
- **Default Values**: Verify correct defaults are applied
- **Error Messages**: Validate error messages for invalid inputs
- **Platform Detection**: Test platform-specific logic

#### CDK Stack Tests
- **Synthesis Tests**: Verify stacks synthesize without errors
- **Snapshot Tests**: Detect unintended changes to generated CloudFormation
- **Resource Count Tests**: Validate expected number of resources created
- **Property Tests**: Verify resource properties match specifications

#### Naming Convention Tests
- **Stack Names**: Verify PipelineStack and AppStack naming patterns
- **Role Names**: Verify IAM role naming with prefix
- **Qualifier**: Verify lowercase app-name is used as qualifier
- **CDKToolkit**: Verify toolkit stack naming

### Integration Testing

#### End-to-End Deployment Tests
- **Single Stack**: Deploy complete pipeline to test/dev account
- **Multi-Stack**: Deploy pipeline and application stacks sequentially
- **Destroy**: Verify infrastructure can be torn down cleanly

#### Security Integration Tests
- **Service Connection Authentication**: Verify Azure DevOps can authenticate to AWS
- **Permissions Boundaries**: Verify boundaries are enforced
- **Checkmarx Scanning**: Verify scans execute and block on vulnerabilities
- **Attestation**: Verify CodePipeline requires attestation

#### Pipeline Tests
- **Push Trigger**: Verify pipeline triggers on push to main
- **Manual Trigger**: Verify manual pipeline runs work correctly
- **Multi-Stage Dependencies**: Verify dependsOn creates correct order
- **Agent Pool**: Verify jobs execute on correct agent pools

### Performance Testing
- **Bootstrap Time**: Measure time to bootstrap accounts
- **Deployment Time**: Measure time for complete deployment
- **Synthesis Time**: Measure CDK synthesis performance
- **Parallel Deployments**: Test multiple concurrent deployments


## Documentation Structure

### README.md
- **Overview**: Framework purpose and benefits
- **Prerequisites**: Required tools, accounts, and permissions
- **Quick Start**: Step-by-step setup for first pipeline
- **Configuration**: Detailed parameter descriptions
- **Examples**: Complete examples for each platform
- **Troubleshooting**: Common issues and solutions
- **Contributing**: Guidelines for framework improvements

### Setup Guides
- **AWS Account Setup**: Provisioning test/dev account
- **Azure DevOps Configuration**: Repository settings and variable groups
- **Service Connection Setup**: Configuring AWS service connection in Azure DevOps
- **Permissions Boundaries**: Creating and applying boundaries
- **Checkmarx Setup**: Configuring security scanning

### Configuration Examples
- **Python Application**: Complete pipeline and CDK code (primary/recommended)
- **TypeScript Application**: Complete pipeline and CDK code
- **.NET Application**: Complete pipeline and CDK code
- **Multi-Stack Deployment**: Sequential stack deployment


### Troubleshooting Guide
- **Incorrect Account IDs**: How to verify and fix account configuration
- **Missing Permissions**: How to identify and add required permissions
- **CDK Synthesis Failures**: Common synthesis errors and fixes
- **Agent Connectivity**: Azure DevOps agent troubleshooting
- **Bootstrap Failures**: How to resolve bootstrap issues


### API Reference
- **Pipeline Template Parameters**: Complete parameter reference
- **Environment Variables**: Required and optional variables
- **Naming Conventions**: All naming patterns and rules
- **CDK Constructs**: Custom constructs and aspects


## Implementation Phases

### Phase 1: Core Framework (Weeks 1-2)
**Objective**: Establish foundational components

1. **Pipeline Template Development**
   - Create azure-pipelines.yml template with all required parameters
   - Implement parameter validation logic
   - Add environment setup tasks
   - Implement AWS service connection authentication
   - Add CDK bootstrap logic
   - Implement deploy/destroy tasks

2. **PipelineStack Templates**
   - Create Python template (primary)
   - Develop TypeScript template
   - Build .NET template
   - Implement RoleNamingConventionAspect
   - Add DefaultStackSynthesizer configuration

3. **Basic Documentation**
   - Write README with quick start
   - Document required parameters
   - Create basic troubleshooting guide

### Phase 2: Security & Multi-Account (Weeks 3-4)
**Objective**: Add security scanning and cross-account deployment

1. **Security Integration**
   - Implement Checkmarx SAST workflow
   - Implement Checkmarx SCA workflow
   - Add attestation verification in CodePipeline
   - Create security scanning documentation

2. **Permissions & Boundaries**
   - Add permissions boundary enforcement
   - Implement role creation with boundaries
   - Test permission constraints

3. **ApplicationStack Templates**
   - Create Python application template (primary)
   - Create TypeScript application template
   - Create .NET application template
   - Add integration examples

### Phase 3: Advanced Features (Weeks 5-6)
**Objective**: Add advanced workflows and optimization

1. **Multi-Stack Support**
   - Implement workflow_run triggers
   - Add dependency management
   - Create sequential deployment examples
   - Test complex multi-stack scenarios

2. **Enhanced Documentation**
   - Complete setup guides for all platforms
   - Add comprehensive configuration examples
   - Create detailed troubleshooting guide
   - Document all naming conventions

3. **Testing & Validation**
   - Write unit tests for all components
   - Create integration test suite
   - Perform end-to-end testing
   - Conduct security review

### Phase 4: Rollout & Support (Weeks 7-8)
**Objective**: Deploy to organization and provide support

1. **Pilot Deployment**
   - Select pilot teams
   - Deploy framework to pilot repositories
   - Gather feedback and iterate

2. **Organization Rollout**
   - Create migration guides
   - Provide training sessions
   - Establish support channels
   - Monitor adoption metrics

3. **Continuous Improvement**
   - Collect user feedback
   - Implement feature requests
   - Optimize performance
   - Update documentation


## Monitoring & Observability

### Pipeline Metrics
- **Deployment Success Rate**: Percentage of successful deployments
- **Deployment Duration**: Time from commit to production
- **Bootstrap Time**: Time to bootstrap new accounts
- **Synthesis Time**: CDK synthesis performance
- **Failure Rate by Stage**: Which stages fail most often

### Security Metrics
- **Scan Success Rate**: Percentage of successful security scans
- **Vulnerabilities Detected**: Count and severity of vulnerabilities
- **Scan Duration**: Time to complete security scans
- **Attestation Compliance**: Percentage of deployments with valid attestation
- **Blocked Deployments**: Count of deployments blocked by security

### Resource Metrics
- **Stack Count**: Number of active stacks per account
- **Resource Count**: Number of resources per stack
- **S3 Storage**: CDK asset storage usage
- **API Call Volume**: AWS API calls per deployment

### Alerting
- **Deployment Failures**: Immediate notification via SNS
- **Security Scan Failures**: Alert security team
- **Permission Errors**: Alert DevOps team
- **Resource Limit Warnings**: Proactive capacity alerts
- **Compliance Violations**: Alert compliance team

### Logging
- **CloudWatch Logs**: All CodeBuild and CodePipeline logs
- **GitHub Actions Logs**: Complete workflow execution logs
- **Audit Trail**: All role assumptions and API calls via CloudTrail
- **Security Scan Logs**: Complete Checkmarx scan results
- **Deployment History**: Complete history of all deployments

### Dashboards
- **Pipeline Health**: Overall pipeline success metrics
- **Security Posture**: Vulnerability trends and compliance
- **Performance**: Deployment times and bottlenecks
- **Resource Usage**: Account and resource utilization
- **Adoption**: Framework usage across organization


## Maintenance & Support

### Version Management
- **Semantic Versioning**: Follow semver for all releases (v1.0.0, v1.1.0, v2.0.0)
- **Git Tags**: Tag releases with annotated tags (git tag -a v1.0.0 -m "Release v1.0.0")
- **Changelog**: Maintain detailed changelog for all versions
- **Backward Compatibility**: Maintain compatibility within major versions
- **Deprecation Policy**: 6-month notice before removing features

### Update Strategy
- **Minor Updates**: Automatic updates for bug fixes and minor features
- **Major Updates**: Require explicit opt-in for breaking changes
- **Security Patches**: Immediate deployment for critical security fixes
- **Testing**: All updates tested in dev environment before rollout
- **Rollback Plan**: Ability to revert to previous version if issues arise

### Support Model
- **Documentation**: Comprehensive self-service documentation
- **Azure DevOps Work Items**: Track bugs and feature requests
- **Teams Channel**: Real-time support for urgent issues
- **Office Hours**: Weekly sessions for Q&A and troubleshooting
- **Training**: Quarterly training sessions for new users

### Feedback Collection
- **User Surveys**: Quarterly surveys to gather feedback
- **Usage Analytics**: Track adoption and usage patterns
- **Feature Requests**: Prioritize based on user demand
- **Bug Reports**: Triage and prioritize based on severity
- **Success Stories**: Document and share successful implementations

### Continuous Improvement
- **Performance Optimization**: Regular performance reviews and improvements
- **Security Updates**: Keep dependencies and tools up to date
- **Feature Enhancements**: Implement high-priority feature requests
- **Documentation Updates**: Keep documentation current with changes
- **Best Practices**: Update templates with emerging best practices


## Scalability Considerations

### Account Scalability
- **Multi-Account Support**: Framework supports unlimited target accounts
- **Account Isolation**: Each account independently bootstrapped
- **Resource Limits**: Monitor and alert on AWS service limits
- **Cost Optimization**: Shared resources in pipeline account to reduce costs

### Repository Scalability
- **Unlimited Repositories**: Framework supports any number of repositories
- **Shared Pipeline Template**: Single azure-pipelines.yml template reused across all repositories
- **Template Versioning**: Repositories can pin to specific framework versions
- **Independent Deployments**: Repositories deploy independently without conflicts

### Pipeline Scalability
- **Parallel Deployments**: Support multiple concurrent deployments
- **Queue Management**: CodePipeline handles deployment queuing
- **Resource Pooling**: Shared CodeBuild compute resources
- **Caching**: CDK asset caching to improve performance

### Performance Optimization
- **Asset Caching**: Reuse CDK assets across deployments
- **Incremental Builds**: Only rebuild changed components
- **Parallel Synthesis**: Synthesize multiple stacks in parallel
- **Lazy Loading**: Load resources only when needed

## Modular Framework Architecture

### Framework Distribution Model

#### Central Framework Repository
The Pipeline Design Framework is maintained in a central Azure DevOps repository that contains:
- **Reusable Azure Pipeline Templates**: Templates that can be referenced by any application repository
- **CDK Stack Templates**: Language-specific templates for all supported platforms (Python, TypeScript, .NET)
- **Documentation and Examples**: Comprehensive guides and working examples
- **Versioned Releases**: Semantic versioning with clear upgrade paths

#### Application Repository Integration
Each application repository (like Epic) integrates with the framework by:

1. **Referencing Framework Repository**: Using Azure DevOps repository resources to access templates
2. **Minimal Configuration**: Only defining application-specific parameters in variable groups
3. **Local Customization**: Ability to override or extend framework behavior when needed
4. **Independent Deployment**: Each application deploys independently without affecting others

### Epic Repository Pilot Implementation

#### Epic Repository Overview
- **Repository URL**: https://devops.globelifeinc.com/projects/Test%20Automation/_git/Epic
- **Purpose**: Test Automation platform infrastructure
- **Role**: Pilot implementation to validate framework before organization-wide rollout

#### Pilot Implementation Strategy

**Phase 1: Analysis**
1. Review current Epic repository structure and deployment process
2. Identify Epic-specific requirements and constraints
3. Map existing deployment workflow to framework patterns
4. Document any gaps or customizations needed

**Phase 2: Framework Integration**
1. Create Epic-specific azure-pipelines.yml that references framework templates
2. Set up Epic variable groups in Azure DevOps with application-specific configuration
3. Configure Epic repository to use framework CDK templates
4. Implement Epic-specific customizations while maintaining framework standards

**Phase 3: Validation**
1. Deploy Epic infrastructure using new framework in test environment
2. Validate all security scanning integration works with Epic codebase
3. Ensure Epic team can maintain and modify their pipeline configuration
4. Verify no breaking changes to existing Epic functionality

**Phase 4: Documentation**
1. Document Epic-specific lessons learned
2. Identify framework improvements needed
3. Create migration guide based on Epic experience
4. Develop onboarding template for other repositories

#### Epic Repository Configuration Example

**Epic-Specific Variable Group (Azure DevOps)**
```yaml
# Variable Group: epic-deployment-variables
APP_NAME: 'epic'
STACK_ID: 'testautomation'
PLATFORM: 'python'
APP_DIRECTORY: './infrastructure'
PERMISSIONS_BOUNDARY: 'arn:aws:iam::ACCOUNT_ID:policy/PermissionsBoundary'
AWS_SERVICE_CONNECTION: 'AWS-TestDev-Connection'
CDK_DEFAULT_REGION: 'us-west-2'
CHECKMARX_TEAM: 'Test Automation'
```

**Epic Repository Pipeline (azure-pipelines.yml)**
```yaml
# Epic Repository: azure-pipelines.yml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: 'epic-deployment-variables'

resources:
  repositories:
    - repository: pipeline-framework
      type: git
      name: 'Pipeline-Design-Framework'
      ref: 'refs/heads/main'

stages:
  - stage: SecurityScan
    displayName: 'Security Scanning'
    jobs:
      - template: azure-pipelines/security-scan-template.yml@pipeline-framework
        parameters:
          checkmarxTeam: $(CHECKMARX_TEAM)
          
  - stage: Deploy
    displayName: 'Deploy Epic Infrastructure'
    dependsOn: SecurityScan
    jobs:
      - template: azure-pipelines/cdk-deploy-template.yml@pipeline-framework
        parameters:
          appName: $(APP_NAME)
          stackId: $(STACK_ID)
          appDir: $(APP_DIRECTORY)
          permissionsBoundary: $(PERMISSIONS_BOUNDARY)
          awsServiceConnection: $(AWS_SERVICE_CONNECTION)
          platform: $(PLATFORM)
          approvalNotification: $(APPROVAL_SNS_TOPIC)
```

**Epic-Specific Configuration File (pipeline-config.yml)**
```yaml
# Epic Repository: pipeline-config.yml
appName: 'epic'
stackId: 'testautomation'
platform: 'python'
appDirectory: './infrastructure'

specialRequirements:
  - 'test-data-management'
  - 'ai-automation-platform'
  - 'selenium-grid-integration'

customTags:
  project: 'Test Automation'
  team: 'QA Engineering'
  environment: 'test-dev'
  costCenter: 'Engineering'

notifications:
  deploymentSuccess: 'epic-deployments@company.com'
  deploymentFailure: 'epic-alerts@company.com'
```

### Scaling to Multiple Repositories

#### Repository Onboarding Process

**Step 1: Framework Reference**
Add repository resource pointing to central framework repository in azure-pipelines.yml:
```yaml
resources:
  repositories:
    - repository: pipeline-framework
      type: git
      name: 'Pipeline-Design-Framework'
      ref: 'refs/heads/main'  # or specific version tag
```

**Step 2: Pipeline Configuration**
Create azure-pipelines.yml using framework templates:
```yaml
stages:
  - stage: Deploy
    jobs:
      - template: azure-pipelines/cdk-deploy-template.yml@pipeline-framework
        parameters:
          appName: $(APP_NAME)
          stackId: $(STACK_ID)
          # ... other parameters
```

**Step 3: Variable Group Setup**
Configure application-specific variables in Azure DevOps:
- Create variable group: `{app-name}-deployment-variables`
- Add required variables: APP_NAME, STACK_ID, PERMISSIONS_BOUNDARY, etc.
- Link variable group to pipeline

**Step 4: CDK Code Organization**
Structure CDK code following framework conventions:
```
repository/
├── azure-pipelines.yml
├── pipeline-config.yml
├── cdk/
│   ├── app.py (or app.ts, Program.cs)
│   ├── pipeline_stack.py
│   └── application_stack.py
└── README.md
```

**Step 5: Testing and Validation**
- Deploy to test environment
- Validate security scanning integration
- Verify deployment succeeds
- Test rollback procedures

#### Framework Versioning Strategy

**Semantic Versioning**
- **Major versions (v2.0.0)**: Breaking changes requiring migration
- **Minor versions (v1.1.0)**: New features, backward compatible
- **Patch versions (v1.0.1)**: Bug fixes, backward compatible

**Version Pinning**
Applications can pin to specific framework versions:
```yaml
resources:
  repositories:
    - repository: pipeline-framework
      type: git
      name: 'Pipeline-Design-Framework'
      ref: 'refs/tags/v1.2.0'  # Pin to specific version
```

**Upgrade Process**
1. Review framework changelog for breaking changes
2. Update version reference in azure-pipelines.yml
3. Test in development environment
4. Deploy to production after validation

**Migration Guides**
For major version upgrades:
- Detailed migration documentation
- Breaking changes clearly documented
- Code examples showing before/after
- Automated migration scripts where possible

#### Benefits of Modular Approach

**For the Organization**
- **Consistency**: All applications follow same deployment patterns
- **Maintainability**: Framework improvements benefit all applications automatically
- **Governance**: Centralized control over deployment standards
- **Security**: Consistent security scanning and compliance across all apps
- **Cost Efficiency**: Shared infrastructure and reduced duplication

**For Application Teams**
- **Simplicity**: Minimal configuration required to adopt framework
- **Flexibility**: Can customize while maintaining standards
- **Independence**: Deploy on their own schedule without conflicts
- **Support**: Centralized documentation and support
- **Best Practices**: Automatically inherit organizational best practices

**For DevOps Team**
- **Scalability**: Easy to onboard new applications
- **Maintenance**: Single source of truth for pipeline logic
- **Monitoring**: Centralized metrics and observability
- **Updates**: Roll out improvements to all applications efficiently
- **Compliance**: Ensure all applications meet organizational requirements

### Repository-Specific Customizations

#### Supported Customization Points

**1. Custom Build Steps**
Applications can add custom build steps before or after framework steps:
```yaml
jobs:
  - job: CustomBuild
    steps:
      - script: |
          # Custom pre-deployment steps
          npm run custom-build
      
      - template: azure-pipelines/cdk-deploy-template.yml@pipeline-framework
        parameters:
          # ... framework parameters
```

**2. Additional Security Scans**
Applications can add repository-specific security tools:
```yaml
- stage: SecurityScan
  jobs:
    - template: azure-pipelines/security-scan-template.yml@pipeline-framework
    
    - job: CustomSecurityScan
      steps:
        - task: SonarQubeScan@1
          # Custom security scanning
```

**3. Custom Deployment Stages**
Applications can add custom stages for specific requirements:
```yaml
stages:
  - stage: Deploy
    # Framework deployment
    
  - stage: IntegrationTests
    dependsOn: Deploy
    jobs:
      - job: RunTests
        # Custom integration tests
```

**4. Environment-Specific Configuration**
Applications can override defaults for specific environments:
```yaml
parameters:
  - name: environment
    default: 'dev'
    values: ['dev', 'test', 'prod']

stages:
  - stage: Deploy
    jobs:
      - template: azure-pipelines/cdk-deploy-template.yml@pipeline-framework
        parameters:
          appName: $(APP_NAME)
          stackId: ${{ parameters.environment }}
          # Environment-specific overrides
```

## Compliance & Governance

### Audit Requirements
- **CloudTrail**: All AWS API calls logged and retained
- **Azure DevOps Audit**: Complete history of all pipeline runs
- **Security Scan Results**: All scan results archived
- **Access Logs**: All role assumptions logged
- **Change Tracking**: All infrastructure changes tracked

### Compliance Controls
- **Permissions Boundaries**: Enforced on all roles
- **Security Scanning**: Required for all deployments
- **Attestation**: Required before production deployment
- **Manual Approval**: Optional for production deployments
- **Separation of Duties**: Different roles for different stages

### Governance Policies
- **Naming Standards**: Enforced via aspects and validation
- **Tagging Standards**: Required tags on all resources
- **Resource Limits**: Enforced via permissions boundaries
- **Approved Services**: Only approved AWS services allowed
- **Cost Controls**: Budget alerts and spending limits
