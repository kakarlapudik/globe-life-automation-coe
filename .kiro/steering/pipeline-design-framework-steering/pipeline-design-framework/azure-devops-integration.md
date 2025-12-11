---
inclusion: manual
---

# Pipeline Design Framework - Azure DevOps Integration

This document defines standards for integrating AWS CDK deployments with Azure DevOps pipelines.

## Overview

The framework provides reusable Azure Pipeline templates that handle CDK synthesis, testing, security scanning, and deployment to multiple AWS accounts.

## Azure Pipeline Structure

### Basic Pipeline Template

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  - group: aws-credentials
  - name: CDK_DEFAULT_REGION
    value: 'us-east-1'

stages:
  - stage: Build
    displayName: 'Build and Test'
    jobs:
      - job: BuildCDK
        displayName: 'Build CDK Application'
        steps:
          - template: azure-pipelines/cdk-build-template.yml

  - stage: DeployDev
    displayName: 'Deploy to Dev'
    dependsOn: Build
    condition: succeeded()
    jobs:
      - deployment: DeployDev
        environment: 'dev'
        strategy:
          runOnce:
            deploy:
              steps:
                - template: azure-pipelines/cdk-deploy-template.yml
                  parameters:
                    environment: 'dev'
                    awsAccountId: '$(DEV_AWS_ACCOUNT_ID)'
                    awsRegion: 'us-east-1'

  - stage: DeployProd
    displayName: 'Deploy to Production'
    dependsOn: DeployDev
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - deployment: DeployProd
        environment: 'production'
        strategy:
          runOnce:
            deploy:
              steps:
                - template: azure-pipelines/cdk-deploy-template.yml
                  parameters:
                    environment: 'prod'
                    awsAccountId: '$(PROD_AWS_ACCOUNT_ID)'
                    awsRegion: 'us-east-1'
```

## Reusable Templates

### CDK Build Template

```yaml
# azure-pipelines/cdk-build-template.yml
parameters:
  - name: nodeVersion
    type: string
    default: '18.x'
  - name: cdkVersion
    type: string
    default: 'latest'

steps:
  - task: NodeTool@0
    displayName: 'Install Node.js'
    inputs:
      versionSpec: '${{ parameters.nodeVersion }}'

  - script: |
      npm ci
    displayName: 'Install dependencies'

  - script: |
      npm run build
    displayName: 'Build application'

  - script: |
      npm test
    displayName: 'Run unit tests'

  - script: |
      npm install -g aws-cdk@${{ parameters.cdkVersion }}
    displayName: 'Install AWS CDK'

  - script: |
      cdk synth
    displayName: 'Synthesize CDK application'

  - task: PublishBuildArtifacts@1
    displayName: 'Publish CDK artifacts'
    inputs:
      pathToPublish: 'cdk.out'
      artifactName: 'cdk-output'
```

### CDK Deploy Template

```yaml
# azure-pipelines/cdk-deploy-template.yml
parameters:
  - name: environment
    type: string
  - name: awsAccountId
    type: string
  - name: awsRegion
    type: string
    default: 'us-east-1'
  - name: stackName
    type: string
    default: ''
  - name: requireApproval
    type: string
    default: 'never'

steps:
  - task: DownloadBuildArtifacts@0
    displayName: 'Download CDK artifacts'
    inputs:
      artifactName: 'cdk-output'
      downloadPath: '$(System.DefaultWorkingDirectory)'

  - task: AWSShellScript@1
    displayName: 'Configure AWS credentials'
    inputs:
      awsCredentials: 'aws-service-connection'
      regionName: '${{ parameters.awsRegion }}'
      scriptType: 'inline'
      inlineScript: |
        echo "Configured AWS credentials for account ${{ parameters.awsAccountId }}"

  - script: |
      npm install -g aws-cdk
    displayName: 'Install AWS CDK'

  - script: |
      cdk deploy \
        --app "cdk.out" \
        --require-approval ${{ parameters.requireApproval }} \
        --context environment=${{ parameters.environment }} \
        ${{ parameters.stackName }}
    displayName: 'Deploy CDK stack to ${{ parameters.environment }}'
    env:
      AWS_ACCOUNT_ID: ${{ parameters.awsAccountId }}
      AWS_REGION: ${{ parameters.awsRegion }}
      ENVIRONMENT: ${{ parameters.environment }}

  - script: |
      cdk diff \
        --app "cdk.out" \
        --context environment=${{ parameters.environment }}
    displayName: 'Show deployment diff'
    condition: always()
```

### Security Scan Template

```yaml
# azure-pipelines/security-scan-template.yml
parameters:
  - name: cdkOutPath
    type: string
    default: 'cdk.out'

steps:
  - task: DownloadBuildArtifacts@0
    displayName: 'Download CDK artifacts'
    inputs:
      artifactName: 'cdk-output'
      downloadPath: '$(System.DefaultWorkingDirectory)'

  - script: |
      pip install cfn-lint
    displayName: 'Install cfn-lint'

  - script: |
      cfn-lint ${{ parameters.cdkOutPath }}/*.template.json
    displayName: 'Run CloudFormation linter'
    continueOnError: true

  - script: |
      docker run --rm -v $(pwd):/data bridgecrew/checkov \
        -d /data/${{ parameters.cdkOutPath }} \
        --framework cloudformation \
        --output junitxml > checkov-report.xml
    displayName: 'Run Checkov security scan'
    continueOnError: true

  - task: PublishTestResults@2
    displayName: 'Publish security scan results'
    inputs:
      testResultsFormat: 'JUnit'
      testResultsFiles: 'checkov-report.xml'
      failTaskOnFailedTests: false
```

### Multi-Stack Deploy Template

```yaml
# azure-pipelines/multi-stack-template.yml
parameters:
  - name: environment
    type: string
  - name: awsAccountId
    type: string
  - name: awsRegion
    type: string
  - name: stacks
    type: object
    default: []

steps:
  - ${{ each stack in parameters.stacks }}:
    - template: cdk-deploy-template.yml
      parameters:
        environment: ${{ parameters.environment }}
        awsAccountId: ${{ parameters.awsAccountId }}
        awsRegion: ${{ parameters.awsRegion }}
        stackName: ${{ stack.name }}
        requireApproval: ${{ stack.requireApproval }}
```

## AWS Credentials Configuration

### Service Connection Setup

1. In Azure DevOps, navigate to Project Settings > Service connections
2. Create a new AWS service connection
3. Configure with IAM user credentials or assume role

### Using AWS Credentials in Pipeline

```yaml
variables:
  - group: aws-credentials  # Variable group containing AWS credentials

steps:
  - task: AWSShellScript@1
    inputs:
      awsCredentials: 'aws-service-connection'
      regionName: '$(AWS_REGION)'
      scriptType: 'inline'
      inlineScript: |
        aws sts get-caller-identity
```

### Cross-Account Deployment

```yaml
# Assume role in target account
steps:
  - script: |
      CREDENTIALS=$(aws sts assume-role \
        --role-arn "arn:aws:iam::$(TARGET_ACCOUNT_ID):role/DeploymentRole" \
        --role-session-name "azure-devops-deployment" \
        --query 'Credentials.[AccessKeyId,SecretAccessKey,SessionToken]' \
        --output text)
      
      export AWS_ACCESS_KEY_ID=$(echo $CREDENTIALS | cut -d' ' -f1)
      export AWS_SECRET_ACCESS_KEY=$(echo $CREDENTIALS | cut -d' ' -f2)
      export AWS_SESSION_TOKEN=$(echo $CREDENTIALS | cut -d' ' -f3)
      
      cdk deploy --all
    displayName: 'Deploy to target account'
    env:
      AWS_DEFAULT_REGION: $(AWS_REGION)
```

## Environment-Specific Deployments

### Using Environments for Approvals

```yaml
stages:
  - stage: DeployProd
    jobs:
      - deployment: DeployProd
        environment: 'production'  # Requires manual approval in Azure DevOps
        strategy:
          runOnce:
            deploy:
              steps:
                - template: cdk-deploy-template.yml
```

### Variable Groups per Environment

```yaml
variables:
  - ${{ if eq(variables['Build.SourceBranch'], 'refs/heads/main') }}:
    - group: prod-variables
  - ${{ if eq(variables['Build.SourceBranch'], 'refs/heads/develop') }}:
    - group: dev-variables
```

## Testing Integration

### Unit Tests

```yaml
- script: |
    npm test -- --coverage
  displayName: 'Run unit tests with coverage'

- task: PublishTestResults@2
  inputs:
    testResultsFormat: 'JUnit'
    testResultsFiles: '**/test-results.xml'

- task: PublishCodeCoverageResults@1
  inputs:
    codeCoverageTool: 'Cobertura'
    summaryFileLocation: '**/coverage/cobertura-coverage.xml'
```

### Integration Tests

```yaml
- script: |
    npm run test:integration
  displayName: 'Run integration tests'
  env:
    AWS_REGION: $(AWS_REGION)
    ENVIRONMENT: ${{ parameters.environment }}
```

## Notifications

### Slack Notifications

```yaml
- task: SlackNotification@1
  condition: always()
  inputs:
    SlackApiToken: '$(SLACK_TOKEN)'
    MessageAuthor: 'Azure DevOps'
    Channel: '#deployments'
    Message: |
      Deployment to ${{ parameters.environment }} completed
      Status: $(Agent.JobStatus)
      Build: $(Build.BuildNumber)
```

### Email Notifications

```yaml
- task: SendEmail@1
  condition: failed()
  inputs:
    To: 'team@example.com'
    Subject: 'Deployment Failed: $(Build.DefinitionName)'
    Body: 'Deployment to ${{ parameters.environment }} failed. Check logs for details.'
```

## Best Practices

### 1. Use Variable Groups

Store sensitive data and environment-specific configuration in Azure DevOps variable groups:

- AWS credentials
- Account IDs
- Region configurations
- Feature flags

### 2. Implement Approval Gates

Use Azure DevOps environments with approval gates for production deployments.

### 3. Cache Dependencies

```yaml
- task: Cache@2
  inputs:
    key: 'npm | "$(Agent.OS)" | package-lock.json'
    path: '$(npm_config_cache)'
    restoreKeys: |
      npm | "$(Agent.OS)"
  displayName: 'Cache npm packages'
```

### 4. Parallel Deployments

```yaml
jobs:
  - job: DeployStack1
    steps:
      - template: cdk-deploy-template.yml
        parameters:
          stackName: 'Stack1'
  
  - job: DeployStack2
    steps:
      - template: cdk-deploy-template.yml
        parameters:
          stackName: 'Stack2'
```

### 5. Rollback Strategy

```yaml
- script: |
    cdk deploy --rollback
  displayName: 'Rollback on failure'
  condition: failed()
```

### 6. Artifact Management

```yaml
- task: PublishBuildArtifacts@1
  inputs:
    pathToPublish: 'cdk.out'
    artifactName: 'cdk-$(Build.BuildNumber)'
    publishLocation: 'Container'
```

### 7. Logging and Monitoring

```yaml
- script: |
    cdk deploy --verbose --debug
  displayName: 'Deploy with verbose logging'
```

## Troubleshooting

### Common Issues

1. **Credentials not found**: Ensure AWS service connection is configured
2. **CDK version mismatch**: Pin CDK version in package.json
3. **Timeout errors**: Increase pipeline timeout settings
4. **Permission denied**: Check IAM role permissions and boundaries

### Debug Mode

```yaml
- script: |
    export CDK_DEBUG=true
    cdk deploy --verbose
  displayName: 'Deploy with debug mode'
```
