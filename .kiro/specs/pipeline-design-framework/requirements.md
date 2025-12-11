# Requirements Document

## Introduction

This document defines the requirements for a Pipeline Design Framework that establishes organizational standards and templates for creating consistent, reliable, and maintainable CI/CD pipelines across all repositories using AWS CDK, GitHub Actions, and AWS CodePipeline. The framework provides reusable composite actions, CDK stack templates, and standardized deployment workflows to ensure all pipelines follow organizational guidelines for multi-account AWS deployments.

## Glossary

- **Pipeline**: An automated CI/CD workflow using GitHub Actions and AWS CodePipeline that builds, tests, and deploys code changes across multiple AWS accounts
- **Composite Action**: A reusable GitHub Action that packages multiple steps into a single action (defined in action.yml)
- **PipelineStack**: The CDK infrastructure code that defines the AWS CodePipeline and associated resources
- **ApplicationStack**: The CDK code that defines the application infrastructure to be deployed
- **Stage**: A deployment environment (dev, test, staging, production) in the pipeline
- **Cross-Account Deployment**: Deployment from a central pipeline account to target application accounts
- **Permissions Boundary**: IAM policy that defines the maximum permissions for roles
- **OIDC Role**: OpenID Connect role used for secure authentication between GitHub and AWS
- **Bootstrap**: Process of provisioning required CDK resources in an AWS account
- **Qualifier**: A unique identifier (lowercase app name) used to namespace CDK resources
- **Synthesizer**: CDK component that controls how assets are published and stacks are deployed
- **Self-Hosted Runner**: GitHub Actions runner hosted on organization infrastructure

## Requirements

### Requirement 1

**User Story:** As a developer, I want a reusable Azure Pipeline template for CDK deployments, so that I can deploy infrastructure consistently across all repositories without duplicating pipeline code.

#### Acceptance Criteria

1. WHEN a developer references the pipeline template THEN the system SHALL provide a reusable template file defining all required parameters and execution steps
2. WHEN the pipeline template executes THEN the system SHALL support TypeScript, Python, and .NET CDK applications
3. WHEN parameters are provided THEN the system SHALL validate required parameters (app-name, stack-id, app-dir, permissions-boundary, aws-service-connection, platform, approval-notification)
4. WHEN the template runs THEN the system SHALL set up Node.js environment, configure AWS credentials via service connection, bootstrap CDK, and deploy the PipelineStack
5. WHERE optional parameters are omitted THEN the system SHALL use sensible defaults (node-version: 20, cdk-default-region: us-west-2, action-type: deploy)
6. WHEN the framework is distributed THEN the system SHALL be modular and reusable across multiple application repositories
7. WHEN the Epic repository is used as pilot THEN the system SHALL validate the framework works correctly before organization-wide rollout

### Requirement 2

**User Story:** As a DevOps engineer, I want standardized CDK PipelineStack templates, so that all applications follow consistent infrastructure patterns for multi-account deployments.

#### Acceptance Criteria

1. WHEN a PipelineStack is created THEN the system SHALL use DefaultStackSynthesizer with app-name as qualifier
2. WHEN environment variables are missing THEN the system SHALL throw clear error messages indicating which required variables are not set
3. WHEN the PipelineStack instantiates THEN the system SHALL apply RoleNamingConventionAspect to enforce consistent IAM role naming (PipelineStack + app_name + stack_id)
4. WHEN cross-account deployments are configured THEN the system SHALL support optional dev, test, staging, and production account IDs
5. WHEN the stack synthesizes THEN the system SHALL use the lowercase app-name as the CDK qualifier for resource namespacing

### Requirement 3

**User Story:** As a developer, I want standardized ApplicationStack templates for each supported language, so that I can create CDK applications that integrate seamlessly with the pipeline framework.

#### Acceptance Criteria

1. WHEN creating a TypeScript ApplicationStack THEN the system SHALL provide a template using DefaultStackSynthesizer with qualifier set to lowercase APP_NAME
2. WHEN creating a Python ApplicationStack THEN the system SHALL provide a template using DefaultStackSynthesizer with qualifier set to lowercase APP_NAME
3. WHEN creating a .NET ApplicationStack THEN the system SHALL provide a template using DefaultStackSynthesizer with qualifier set to lowercase APP_NAME
4. WHEN stack naming is applied THEN the system SHALL follow the pattern 'AppStack' + APP_NAME + STACK_ID
5. WHEN environment configuration is set THEN the system SHALL use CDK_DEFAULT_ACCOUNT and CDK_DEFAULT_REGION environment variables

### Requirement 4

**User Story:** As a developer, I want a standardized GitHub workflow template, so that I can quickly configure CI/CD for my repository with minimal setup.

#### Acceptance Criteria

1. WHEN a workflow template is provided THEN the system SHALL include triggers for push to main branch and manual workflow_dispatch
2. WHEN the workflow executes THEN the system SHALL require specific GitHub permissions (deployments, statuses, contents, id-token, actions, checks, packages, pull-requests)
3. WHEN the workflow runs THEN the system SHALL execute on self-hosted runners
4. WHEN the deploy step executes THEN the system SHALL checkout code and invoke the composite action with all required parameters
5. WHERE multi-stack deployments are needed THEN the system SHALL support workflow_run triggers to create sequential deployment dependencies

### Requirement 5

**User Story:** As a security engineer, I want Checkmarx security scanning integrated into all pipelines, so that vulnerabilities are caught before deployment and compliance requirements are met.

#### Acceptance Criteria

1. WHEN a pull request is created to main branch THEN the system SHALL automatically trigger Checkmarx SAST and SCA scanning
2. WHEN security scanning completes THEN the system SHALL require attestation verification in AWS CodePipeline before deployment proceeds
3. WHEN security vulnerabilities are detected THEN the system SHALL block pull request merging until issues are resolved
4. WHEN legacy code is scanned THEN the system SHALL support baseline vulnerability assessment and incremental scanning of only modified code
5. WHEN audit trails are required THEN the system SHALL maintain complete compliance reporting and logs for all scanning activities

### Requirement 6

**User Story:** As a cloud operations engineer, I want standardized AWS account provisioning and access management, so that developers can deploy securely across multiple accounts.

#### Acceptance Criteria

1. WHEN setting up a pipeline account THEN the system SHALL require GitHub_AccessRole (OIDC) and Permissions-Boundary to be provisioned
2. WHEN setting up application accounts THEN the system SHALL require Boundary_CICDPipeline and Permissions-Boundary to be provisioned in each target environment (dev, test, staging, production)
3. WHEN developers need access THEN the system SHALL require tickets to Cloud Ops for AWS roles, GitHub Admin for repository access, and IT Security for Checkmarx scanning
4. WHEN bootstrapping accounts THEN the system SHALL use custom permissions boundaries and CloudFormation execution policies
5. WHEN cross-account deployments occur THEN the system SHALL assume roles with appropriate boundaries in target accounts

### Requirement 7

**User Story:** As a developer, I want clear naming conventions and resource organization, so that I can easily identify and manage pipeline resources across multiple accounts.

#### Acceptance Criteria

1. WHEN IAM roles are created THEN the system SHALL prefix them with 'PipelineStack' + app_name + stack_id
2. WHEN CDK resources are created THEN the system SHALL use lowercase app_name as the qualifier for namespacing
3. WHEN stacks are named THEN the system SHALL follow the pattern 'PipelineStack' + app_name + stack_id for pipeline stacks and 'AppStack' + app_name + stack_id for application stacks
4. WHEN CDK Toolkit is bootstrapped THEN the system SHALL use CDKToolkit + app_name as the stack name
5. WHEN S3 buckets are created THEN the system SHALL use the qualifier to ensure unique bucket names across accounts

### Requirement 8

**User Story:** As a developer, I want comprehensive documentation and examples, so that I can understand how to configure and customize pipelines for my specific needs.

#### Acceptance Criteria

1. WHEN developers access the framework THEN the system SHALL provide a README with complete setup instructions, prerequisites, and configuration examples
2. WHEN configuring workflows THEN the system SHALL provide template examples for TypeScript, Python, and .NET applications
3. WHEN troubleshooting issues THEN the system SHALL document common problems (incorrect account IDs, missing permissions, CDK synthesis failures, runner connectivity)
4. WHEN setting up multi-stack deployments THEN the system SHALL provide examples using workflow_run triggers for sequential dependencies
5. WHEN creating git tags for releases THEN the system SHALL document the versioning command format (git tag -a v1.0.0 -m "Release v1.0.0")

### Requirement 9

**User Story:** As a developer, I want support for both deployment and destruction actions, so that I can manage the full lifecycle of my infrastructure.

#### Acceptance Criteria

1. WHEN action-type is set to 'deploy' THEN the system SHALL execute CDK deploy to create or update infrastructure
2. WHEN action-type is set to 'destroy' THEN the system SHALL execute CDK destroy to tear down infrastructure
3. WHEN action-type is omitted THEN the system SHALL default to 'deploy' action
4. WHEN destroying infrastructure THEN the system SHALL require explicit confirmation to prevent accidental deletions
5. WHEN the action completes THEN the system SHALL provide clear success or failure messages with relevant details

### Requirement 10

**User Story:** As a platform engineer, I want the framework to support the complete CI/CD execution flow, so that deployments follow a secure, auditable process from code commit to production.

#### Acceptance Criteria

1. WHEN code is committed THEN the system SHALL trigger GitHub Actions which authenticate via OIDC to assume GitHub_AccessRole
2. WHEN GitHub Actions execute THEN the system SHALL bootstrap the pipeline account with required roles and upload build artifacts and CDK code to S3
3. WHEN CodePipeline is triggered THEN the system SHALL invoke CodeBuild to build and package the application
4. WHEN cross-account deployment occurs THEN the system SHALL have CodeBuild assume cross-account roles to bootstrap and deploy to target environments
5. WHEN CloudFormation executes THEN the system SHALL deploy the CDK stack and provision infrastructure, completing the end-to-end pipeline delivery


### Requirement 11

**User Story:** As an organization, I want the pipeline framework to be modular and easily adoptable across all application-specific repositories, so that each application team can independently deploy their infrastructure while following organizational standards.

#### Acceptance Criteria

1. WHEN the framework is distributed THEN the system SHALL be maintained in a central repository that can be referenced by any application repository
2. WHEN an application repository adopts the framework THEN the system SHALL require minimal setup and configuration
3. WHEN application-specific configuration is provided THEN the system SHALL isolate it from other repositories to prevent conflicts
4. WHEN the framework is updated THEN the system SHALL maintain backward compatibility and provide easy upgrade paths
5. WHEN repository-specific customizations are needed THEN the system SHALL support them while maintaining core organizational standards

### Requirement 12

**User Story:** As a pilot project, I want to implement the pipeline framework in the Epic repository first, so that I can validate the framework works correctly before rolling out to other repositories.

#### Acceptance Criteria

1. WHEN the Epic repository infrastructure is deployed THEN the system SHALL successfully deploy using the new pipeline framework
2. WHEN security scanning is integrated THEN the system SHALL work correctly with the Epic repository codebase
3. WHEN the Epic team uses the framework THEN the system SHALL not break any existing Epic repository functionality
4. WHEN lessons are learned from Epic implementation THEN the system SHALL document improvements needed for the framework
5. WHEN the Epic pilot is complete THEN the system SHALL provide a migration guide based on the Epic repository experience
6. WHEN framework modularity is validated THEN the system SHALL demonstrate the easy adoption process using Epic as the reference implementation
