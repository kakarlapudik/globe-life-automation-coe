# Epic Repository - Pipeline Framework Reference Implementation

This directory contains the reference implementation of the Pipeline Design Framework for the Epic Test Automation platform. It serves as the primary example for other teams adopting the framework.

## Overview

The Epic repository demonstrates:
- Complete Azure Pipeline configuration using framework templates
- Python CDK infrastructure setup
- Security scanning integration
- Multi-stage deployment with validation
- Resource cleanup for feature branches

## Configuration

### Variable Group: `epic-deployment-variables`

| Variable | Value | Description |
|----------|-------|-------------|
| `APP_NAME` | `epic` | Application name |
| `STACK_ID` | `testautomation` | Stack identifier |
| `PLATFORM` | `python` | CDK platform |
| `APP_DIRECTORY` | `./infrastructure` | Infrastructure code location |
| `PERMISSIONS_BOUNDARY` | `arn:aws:iam::...` | IAM permissions boundary |
| `AWS_SERVICE_CONNECTION` | `AWS-Epic-Production` | AWS service connection name |
| `CHECKMARX_TEAM` | `Test-Automation` | Checkmarx team |
| `CDK_DEFAULT_REGION` | `us-west-2` | AWS region |
| `APPROVAL_SNS_TOPIC` | `arn:aws:sns:...` | (Optional) Notification topic |
| `SONARQUBE_CONNECTION` | `SonarQube-Connection` | SonarQube service connection |
| `EPIC_TEAM_EMAIL` | `epic-team@example.com` | Team email for notifications |

## Pipeline Stages

### 1. Security Scanning
- **Trigger**: Pull requests only
- **Actions**:
  - Checkmarx SAST scan
  - SonarQube code quality analysis
  - OWASP dependency check
- **Policy**: Fails build on critical vulnerabilities

### 2. Deploy Infrastructure
- **Trigger**: Commits to `main` branch
- **Actions**:
  - Validates parameters
  - Sets up Node.js and Python environments
  - Installs AWS CDK CLI
  - Bootstraps CDK (if needed)
  - Deploys all CDK stacks
  - Sends notification (if configured)

### 3. Validate Deployment
- **Trigger**: After successful deployment
- **Actions**:
  - Validates CloudFormation stacks exist
  - Checks stack status
  - Runs integration tests
  - Publishes test results

### 4. Cleanup (Feature Branches)
- **Trigger**: Non-main branches
- **Actions**:
  - Requires manual approval
  - Destroys temporary test resources
  - Prevents resource accumulation

## Infrastructure Structure

```
infrastructure/
├── app.py                    # CDK app entry point
├── pipeline_stack.py         # Pipeline infrastructure
├── application_stack.py      # Application infrastructure
├── requirements.txt          # Python dependencies
└── cdk.json                  # CDK configuration
```

## Epic-Specific Features

### Test Data Management
- S3 buckets for test data storage
- DynamoDB tables for test metadata
- Lambda functions for data processing

### AI Automation Platform
- ECS Fargate services for AI workloads
- SageMaker endpoints for ML models
- Step Functions for workflow orchestration

### Selenium Grid Integration
- ECS cluster for Selenium Grid
- Application Load Balancer
- Auto-scaling configuration

### Test Reporting Dashboard
- CloudFront distribution
- S3 bucket for static assets
- API Gateway for backend APIs

## Deployment Process

### Initial Deployment

1. **Configure Variables**:
   ```bash
   # Set in Azure DevOps variable group
   APP_NAME=epic
   STACK_ID=testautomation
   PERMISSIONS_BOUNDARY=arn:aws:iam::123456789012:policy/BoundaryPolicy
   ```

2. **Commit and Push**:
   ```bash
   git add .
   git commit -m "Configure Epic pipeline"
   git push origin main
   ```

3. **Monitor Pipeline**:
   - Navigate to Azure DevOps Pipelines
   - Watch deployment progress
   - Check CloudFormation console for stack creation

### Updates

1. **Make Infrastructure Changes**:
   ```bash
   cd infrastructure
   # Edit stack files
   ```

2. **Test Locally**:
   ```bash
   export APP_NAME=epic
   export STACK_ID=testautomation
   export PERMISSIONS_BOUNDARY=arn:aws:iam::...
   
   cdk synth
   cdk diff
   ```

3. **Deploy via Pipeline**:
   ```bash
   git add .
   git commit -m "Update Epic infrastructure"
   git push origin main
   ```

## Testing

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run unit tests
pytest tests/unit/ -v

# Run integration tests (requires AWS credentials)
pytest tests/integration/ -v
```

### Pipeline Testing

- **Pull Request**: Triggers security scans only
- **Main Branch**: Full deployment and validation
- **Feature Branch**: Can trigger cleanup after approval

## Customizations

### Epic-Specific Configurations

1. **Extended Timeout**: Build timeout set to 60 minutes for large deployments
2. **Custom Exclusions**: Excludes test data and cache directories from security scans
3. **Integration Tests**: Validates Selenium Grid connectivity and AI platform APIs
4. **Cleanup Workflow**: Prevents accumulation of test environment resources

### Framework Extensions

Epic demonstrates how to extend the framework:

```yaml
# Custom validation stage
- stage: CustomValidation
  jobs:
    - job: ValidateSeleniumGrid
      steps:
        - script: |
            # Custom validation logic
            python scripts/validate_selenium_grid.py
```

## Lessons Learned

### What Worked Well
- ✅ Framework templates reduced pipeline setup time by 80%
- ✅ Standardized naming conventions improved resource management
- ✅ Automatic permissions boundary enforcement ensured compliance
- ✅ Security scanning caught vulnerabilities early in development

### Challenges Overcome
- **Challenge**: Large codebase caused long security scans
  - **Solution**: Optimized exclusion patterns, enabled incremental scans
  
- **Challenge**: Complex multi-stack dependencies
  - **Solution**: Used multi-stack template with explicit dependency ordering
  
- **Challenge**: Test environment cleanup
  - **Solution**: Added manual approval stage for resource destruction

### Recommendations for Other Teams
1. Start with single-stack deployment, add complexity gradually
2. Test locally with `cdk synth` before pushing to pipeline
3. Use feature branches for testing infrastructure changes
4. Monitor CloudFormation events for deployment issues
5. Set up SNS notifications for deployment status

## Support

For Epic-specific questions:
- **Team**: Test Automation Team
- **Email**: epic-team@example.com
- **Slack**: #epic-test-automation

For framework questions:
- **Team**: DevOps Team
- **Documentation**: [Framework Docs](../../docs/)
- **Examples**: [Other Examples](../)

## Related Documentation

- [Pipeline Design Framework README](../../README.md)
- [Setup Guide](../../docs/setup-guide.md)
- [Security Integration](../../docs/security-integration.md)
- [Troubleshooting](../../docs/troubleshooting.md)
