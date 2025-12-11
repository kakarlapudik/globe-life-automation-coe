# eServiceCenter V2 Migration Plan

## Executive Summary

This document outlines the migration plan for integrating the eServiceCenter V2 test automation repository with the Pipeline Design Framework. The migration will modernize the CI/CD pipeline while maintaining all existing functionality.

## Current State Analysis

### Existing Pipeline Configuration

**Current Pipelines:**
1. `azure-pipelines.yml` - Main build pipeline
2. `azure-pipelines1.yml` - Duplicate of main pipeline
3. `Selenium_CI.yml` - Smoke test pipeline (misconfigured)

**Current Configuration:**
```yaml
trigger: main
pool: default (self-hosted agent)
jdkVersion: 1.8
goals: package
```

**Issues Identified:**
1. ❌ `Selenium_CI.yml` references `smoke.xml` as mavenPomFile (should be `pom.xml`)
2. ❌ JDK 1.8 specified but pom.xml requires Java 11/22
3. ❌ No test profile execution (Smoke or Regression)
4. ❌ Duplicate pipeline configurations
5. ❌ No security scanning integration
6. ❌ No artifact publishing
7. ❌ No test report publishing beyond JUnit
8. ❌ No environment-specific configuration

### Test Execution Requirements

**Test Suites:**
- Smoke Tests (`Smoke.xml`) - Quick validation
- Regression Tests (`Regression.xml`) - Full test suite
- API Regression (`RegressionAPI.xml`) - API-only tests
- UI Regression (`RegressionUI.xml`) - UI-only tests

**External Dependencies:**
- MySQL database for test data
- AWS Secrets Manager for credentials
- LambdaTest for cross-browser testing
- Email service for notifications

## Migration Strategy

### Phase 1: Pipeline Modernization (Week 1)

#### Objectives
- Create modern Azure Pipeline using framework best practices
- Fix existing configuration issues
- Maintain backward compatibility

#### Tasks

1. **Create New Pipeline Configuration**
   - File: `azure-pipelines-framework.yml`
   - Use framework templates (if applicable for Java/Maven)
   - Configure proper JDK version (11 or 22)
   - Set up Maven profiles for different test suites

2. **Configure Variable Groups**
   - Create `eservicecenter-v2-variables` variable group
   - Store database connection strings
   - Store AWS credentials
   - Store LambdaTest credentials
   - Store email configuration

3. **Set Up Service Connections**
   - AWS service connection for Secrets Manager
   - Database service connection (if needed)
   - Email service connection

4. **Fix Test Execution**
   - Configure Maven to execute TestNG suites
   - Use Maven profiles: `-P Smoke` or `-P Regression`
   - Ensure proper test result publishing

### Phase 2: Enhanced Reporting & Artifacts (Week 2)

#### Objectives
- Publish ExtentReports as pipeline artifacts
- Enhance test result visibility
- Set up email notifications

#### Tasks

1. **Artifact Publishing**
   - Publish ExtentReports HTML
   - Publish test screenshots
   - Publish test logs
   - Publish Surefire reports

2. **Enhanced Reporting**
   - Integrate TestNG results with Azure DevOps
   - Create custom test result dashboard
   - Set up test trend analysis

3. **Notification Setup**
   - Configure email notifications for test failures
   - Set up Slack/Teams notifications (optional)
   - Create test summary reports

### Phase 3: Security & Quality Gates (Week 3)

#### Objectives
- Integrate Checkmarx security scanning
- Add code quality checks
- Implement deployment gates

#### Tasks

1. **Security Scanning**
   - Add Checkmarx SAST scanning
   - Add Checkmarx SCA scanning
   - Configure vulnerability thresholds

2. **Quality Gates**
   - Set minimum test pass rate
   - Configure code coverage thresholds
   - Add dependency vulnerability checks

3. **Compliance**
   - Add audit logging
   - Implement approval gates for production
   - Document security controls

### Phase 4: Multi-Environment Support (Week 4)

#### Objectives
- Support multiple test environments
- Enable environment-specific configurations
- Implement deployment strategies

#### Tasks

1. **Environment Configuration**
   - Create DEV environment configuration
   - Create QA environment configuration
   - Create STAGING environment configuration
   - Create PROD environment configuration

2. **Environment Variables**
   - Configure environment-specific URLs
   - Set up environment-specific credentials
   - Manage environment-specific test data

3. **Deployment Strategy**
   - Implement blue-green deployment for test environments
   - Set up canary releases
   - Configure rollback procedures

## Detailed Implementation Plan

### New Pipeline Structure

```yaml
# azure-pipelines-framework.yml

trigger:
  branches:
    include:
      - main
      - develop
  paths:
    exclude:
      - README.md
      - docs/*

pr:
  branches:
    include:
      - main
      - develop

variables:
  - group: eservicecenter-v2-variables
  - name: mavenVersion
    value: '3.8.x'
  - name: jdkVersion
    value: '11'

stages:
  - stage: Build
    displayName: 'Build and Unit Tests'
    jobs:
      - job: Build
        pool:
          name: default
        steps:
          - task: Maven@3
            displayName: 'Maven Build'
            inputs:
              mavenPomFile: 'pom.xml'
              goals: 'clean compile'
              javaHomeOption: 'JDKVersion'
              jdkVersionOption: '$(jdkVersion)'
              mavenOptions: '-Xmx3072m'

  - stage: SmokeTests
    displayName: 'Smoke Tests'
    dependsOn: Build
    jobs:
      - job: SmokeTest
        pool:
          name: default
        steps:
          - task: Maven@3
            displayName: 'Run Smoke Tests'
            inputs:
              mavenPomFile: 'pom.xml'
              goals: 'test'
              options: '-P Smoke'
              javaHomeOption: 'JDKVersion'
              jdkVersionOption: '$(jdkVersion)'
              mavenOptions: '-Xmx3072m'
              publishJUnitResults: true
              testResultsFiles: '**/surefire-reports/TEST-*.xml'
          
          - task: PublishPipelineArtifact@1
            displayName: 'Publish Test Reports'
            condition: always()
            inputs:
              targetPath: '$(System.DefaultWorkingDirectory)/test-output'
              artifact: 'smoke-test-reports'
              publishLocation: 'pipeline'

  - stage: RegressionTests
    displayName: 'Regression Tests'
    dependsOn: SmokeTests
    condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
    jobs:
      - job: RegressionTest
        pool:
          name: default
        steps:
          - task: Maven@3
            displayName: 'Run Regression Tests'
            inputs:
              mavenPomFile: 'pom.xml'
              goals: 'test'
              options: '-P Regression'
              javaHomeOption: 'JDKVersion'
              jdkVersionOption: '$(jdkVersion)'
              mavenOptions: '-Xmx3072m'
              publishJUnitResults: true
              testResultsFiles: '**/surefire-reports/TEST-*.xml'
          
          - task: PublishPipelineArtifact@1
            displayName: 'Publish Test Reports'
            condition: always()
            inputs:
              targetPath: '$(System.DefaultWorkingDirectory)/test-output'
              artifact: 'regression-test-reports'
              publishLocation: 'pipeline'

  - stage: SecurityScan
    displayName: 'Security Scanning'
    dependsOn: Build
    jobs:
      - job: Checkmarx
        pool:
          name: default
        steps:
          - task: CheckmarxSAST@2023
            displayName: 'Checkmarx SAST Scan'
            inputs:
              projectName: 'eServiceCenter_V2'
              preset: 'High and Medium'
              vulnerabilityThreshold: true
              high: 0
              medium: 10
```

### Variable Group Configuration

**Variable Group Name:** `eservicecenter-v2-variables`

**Variables:**
```
# Database Configuration
DB_HOST: <mysql-host>
DB_PORT: 3306
DB_NAME: test_automation
DB_USERNAME: <username>
DB_PASSWORD: <password> (secret)

# AWS Configuration
AWS_REGION: us-east-1
AWS_SECRET_NAME: eservicecenter-v2-secrets

# LambdaTest Configuration
LT_USERNAME: <lambdatest-username>
LT_ACCESS_KEY: <lambdatest-key> (secret)
LT_GRID_URL: https://hub.lambdatest.com/wd/hub

# Email Configuration
SMTP_HOST: <smtp-host>
SMTP_PORT: 587
SMTP_USERNAME: <email-username>
SMTP_PASSWORD: <email-password> (secret)
EMAIL_RECIPIENTS: <recipient-list>

# Application Configuration
APP_URL_DEV: https://dev.eservicecenter.com
APP_URL_QA: https://qa.eservicecenter.com
APP_URL_STAGING: https://staging.eservicecenter.com
APP_URL_PROD: https://eservicecenter.com

# Test Configuration
TEST_ENVIRONMENT: QA
TESTER_NAME: $(Build.RequestedFor)
PARALLEL_THREADS: 1
```

### Service Connection Setup

1. **AWS Service Connection**
   - Name: `aws-eservicecenter-v2`
   - Type: AWS
   - Access Key ID: From AWS IAM
   - Secret Access Key: From AWS IAM
   - Region: us-east-1

2. **Database Service Connection** (if supported)
   - Name: `mysql-eservicecenter-v2`
   - Type: Generic
   - Server URL: MySQL connection string
   - Credentials: Stored in variable group

## Migration Checklist

### Pre-Migration
- [ ] Backup existing pipeline configurations
- [ ] Document current pipeline behavior
- [ ] Identify all external dependencies
- [ ] Create test environment for validation
- [ ] Notify team of upcoming changes

### Migration Execution
- [ ] Create variable group in Azure DevOps
- [ ] Set up service connections
- [ ] Create new pipeline file (`azure-pipelines-framework.yml`)
- [ ] Test pipeline in feature branch
- [ ] Validate smoke tests execute correctly
- [ ] Validate regression tests execute correctly
- [ ] Verify test reports are published
- [ ] Confirm email notifications work

### Post-Migration
- [ ] Monitor first production run
- [ ] Validate all test results
- [ ] Check artifact publishing
- [ ] Verify email notifications
- [ ] Update team documentation
- [ ] Archive old pipeline configurations
- [ ] Conduct team training session

### Rollback Plan
- [ ] Keep old pipeline files for 30 days
- [ ] Document rollback procedure
- [ ] Test rollback in non-production environment
- [ ] Define rollback triggers and decision criteria

## Risk Assessment

### High Risk
1. **Database Connectivity**
   - Risk: Pipeline may not connect to MySQL database
   - Mitigation: Test connection in pre-production, use service connections
   - Rollback: Revert to old pipeline

2. **AWS Secrets Manager Access**
   - Risk: Pipeline may not access secrets
   - Mitigation: Configure AWS service connection properly, test in dev
   - Rollback: Use variable group secrets temporarily

### Medium Risk
1. **LambdaTest Integration**
   - Risk: Cross-browser tests may fail
   - Mitigation: Validate LambdaTest credentials, test with single browser first
   - Rollback: Run tests on local agents only

2. **Test Report Publishing**
   - Risk: ExtentReports may not publish correctly
   - Mitigation: Test artifact publishing in dev environment
   - Rollback: Use JUnit reports only

### Low Risk
1. **Email Notifications**
   - Risk: Email notifications may not send
   - Mitigation: Test email configuration separately
   - Rollback: Use Azure DevOps notifications

## Success Criteria

### Must Have
- ✅ All smoke tests execute successfully
- ✅ All regression tests execute successfully
- ✅ Test results published to Azure DevOps
- ✅ Pipeline completes within acceptable time
- ✅ No regression in test coverage

### Should Have
- ✅ ExtentReports published as artifacts
- ✅ Email notifications working
- ✅ Security scanning integrated
- ✅ Multi-environment support

### Nice to Have
- ✅ Test trend dashboards
- ✅ Automated rollback on failure
- ✅ Parallel test execution
- ✅ Performance metrics tracking

## Timeline

**Week 1:** Pipeline modernization and basic functionality
**Week 2:** Enhanced reporting and artifacts
**Week 3:** Security scanning and quality gates
**Week 4:** Multi-environment support and optimization

**Total Duration:** 4 weeks
**Go-Live Date:** TBD based on team availability

## Support and Training

### Documentation
- Pipeline configuration guide
- Variable group setup guide
- Troubleshooting guide
- FAQ document

### Training Sessions
- Session 1: New pipeline overview (1 hour)
- Session 2: Running tests and viewing results (1 hour)
- Session 3: Troubleshooting and maintenance (1 hour)

### Support Channels
- Azure DevOps wiki for documentation
- Teams channel for questions
- Weekly office hours for first month

## Conclusion

This migration plan provides a structured approach to modernizing the eServiceCenter V2 test automation pipeline while minimizing risk and maintaining functionality. The phased approach allows for validation at each step and provides clear rollback procedures if needed.
