# eServiceCenter V2 Pipeline Example

This directory contains documentation and configuration examples for integrating the eServiceCenter V2 test automation repository with modern CI/CD practices.

## Contents

1. **REPOSITORY_ANALYSIS.md** - Comprehensive analysis of the eServiceCenter V2 repository structure, dependencies, and current state
2. **MIGRATION_PLAN.md** - Detailed migration plan with phases, timelines, and risk assessment
3. **azure-pipelines-eservicecenter.yml** - Modern Azure Pipeline configuration example

## Quick Start

### Prerequisites

- Azure DevOps project with pipeline access
- Self-hosted agent pool named "default"
- JDK 11 or 22 installed on build agents
- Maven 3.8.x installed on build agents
- Access to MySQL database for test data
- AWS credentials for Secrets Manager (optional)
- LambdaTest account for cross-browser testing (optional)

### Setup Steps

1. **Create Variable Group**
   ```
   Navigate to: Azure DevOps > Pipelines > Library > Variable groups
   Create new group: eservicecenter-v2-variables
   ```

   Add the following variables:
   - `DB_HOST` - MySQL database host
   - `DB_PORT` - MySQL database port (default: 3306)
   - `DB_NAME` - Database name
   - `DB_USERNAME` - Database username
   - `DB_PASSWORD` - Database password (mark as secret)
   - `AWS_REGION` - AWS region (if using Secrets Manager)
   - `AWS_SECRET_NAME` - Secret name in AWS Secrets Manager
   - `LT_USERNAME` - LambdaTest username (if using)
   - `LT_ACCESS_KEY` - LambdaTest access key (mark as secret)
   - `APP_URL_QA` - QA environment URL
   - `TEST_ENVIRONMENT` - Current test environment (DEV/QA/STAGING/PROD)

2. **Configure Service Connections** (if needed)
   ```
   Navigate to: Azure DevOps > Project Settings > Service connections
   ```
   
   Create connections for:
   - AWS (if using Secrets Manager)
   - Email service (if using email notifications)

3. **Create Pipeline**
   ```
   Navigate to: Azure DevOps > Pipelines > New Pipeline
   Select: Azure Repos Git
   Choose: eServiceCenter_V2 repository
   Select: Existing Azure Pipelines YAML file
   Path: /azure-pipelines-eservicecenter.yml
   ```

4. **Run Pipeline**
   - Click "Run" to execute the pipeline
   - Monitor execution in Azure DevOps
   - View test results in the Tests tab
   - Download test reports from Artifacts

## Pipeline Stages

The pipeline includes the following stages:

### 1. Build & Compile
- Compiles Java code using Maven
- Publishes build artifacts for downstream stages
- Validates code compiles successfully

### 2. Smoke Tests
- Executes quick validation tests
- Runs on every commit
- Publishes test results and reports
- Fails fast if critical issues found

### 3. Regression Tests
- Executes full test suite
- Runs only on main branch
- Comprehensive validation
- Longer execution time

### 4. API Regression Tests
- Executes API-specific tests
- Runs in parallel with UI tests
- Validates backend functionality

### 5. UI Regression Tests
- Executes UI-specific tests
- Runs in parallel with API tests
- Validates frontend functionality

### 6. Security Scanning
- Checkmarx SAST scanning (when configured)
- Vulnerability detection
- Compliance validation

### 7. Reporting & Notifications
- Generates test summary
- Sends email notifications (when configured)
- Publishes comprehensive reports

## Test Suites

The repository contains multiple TestNG suite configurations:

- **Smoke.xml** - Quick smoke tests for rapid feedback
- **Regression.xml** - Full regression test suite
- **RegressionAPI.xml** - API-only regression tests
- **RegressionUI.xml** - UI-only regression tests

## Artifacts Published

Each pipeline run publishes the following artifacts:

1. **build-output** - Compiled classes and dependencies
2. **smoke-test-reports-{BuildId}** - Smoke test ExtentReports
3. **smoke-surefire-reports-{BuildId}** - Smoke test Surefire reports
4. **regression-test-reports-{BuildId}** - Regression test ExtentReports
5. **regression-surefire-reports-{BuildId}** - Regression test Surefire reports
6. **api-test-reports-{BuildId}** - API test reports
7. **ui-test-reports-{BuildId}** - UI test reports

## Configuration Options

### Environment Variables

Configure test environment by setting variables in the variable group:

```yaml
variables:
  - name: testEnvironment
    value: 'QA'  # Options: DEV, QA, STAGING, PROD
  - name: parallelThreads
    value: '1'   # Number of parallel test threads
```

### Test Execution

Run specific test suites by modifying the Maven goals:

```yaml
# Smoke tests
goals: 'test'
options: '-P Smoke'

# Regression tests
goals: 'test'
options: '-P Regression'

# Specific suite file
goals: 'test'
options: '-Dsurefire.suiteXmlFiles=RegressionAPI.xml'
```

### JDK Version

The pipeline uses JDK 11 by default. To change:

```yaml
variables:
  - name: jdkVersion
    value: '11'  # Options: 11, 17, 22
```

## Troubleshooting

### Common Issues

**Issue: Tests fail to connect to database**
- Solution: Verify DB_HOST, DB_PORT, DB_USERNAME, and DB_PASSWORD in variable group
- Check network connectivity from build agent to database

**Issue: AWS Secrets Manager access denied**
- Solution: Verify AWS service connection is configured
- Check IAM permissions for the service principal

**Issue: LambdaTest tests fail**
- Solution: Verify LT_USERNAME and LT_ACCESS_KEY are correct
- Check LambdaTest account status and concurrent session limits

**Issue: JDK version mismatch**
- Solution: Ensure build agent has correct JDK version installed
- Update jdkVersion variable to match installed version

**Issue: Maven build fails**
- Solution: Check Maven is installed on build agent
- Verify pom.xml is valid
- Check for dependency resolution issues

### Viewing Test Results

1. **Azure DevOps Tests Tab**
   - Navigate to pipeline run
   - Click "Tests" tab
   - View pass/fail statistics
   - Drill down into individual test results

2. **ExtentReports**
   - Navigate to pipeline run
   - Click "Artifacts" tab
   - Download test report artifact
   - Open HTML report in browser

3. **Surefire Reports**
   - Navigate to pipeline run
   - Click "Artifacts" tab
   - Download surefire report artifact
   - View XML test results

## Migration from Old Pipeline

If migrating from the existing pipeline configuration:

1. Review [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for detailed steps
2. Create variable group with required configuration
3. Test new pipeline in feature branch first
4. Validate all tests execute correctly
5. Switch main branch to use new pipeline
6. Archive old pipeline configurations

## Best Practices

1. **Use Variable Groups** - Store all configuration in variable groups, not in YAML
2. **Mark Secrets** - Always mark sensitive values as secrets
3. **Test in Feature Branches** - Validate pipeline changes before merging to main
4. **Monitor First Runs** - Watch initial executions closely for issues
5. **Publish Artifacts** - Always publish test reports for debugging
6. **Use Stages** - Separate concerns into distinct stages
7. **Fail Fast** - Run smoke tests before expensive regression tests
8. **Parallel Execution** - Run independent test suites in parallel

## Support

For questions or issues:

1. Review [REPOSITORY_ANALYSIS.md](REPOSITORY_ANALYSIS.md) for technical details
2. Check [MIGRATION_PLAN.md](MIGRATION_PLAN.md) for migration guidance
3. Consult Azure DevOps pipeline documentation
4. Contact DevOps team for infrastructure issues

## Next Steps

1. Review repository analysis document
2. Read migration plan
3. Set up variable group
4. Create test pipeline
5. Validate smoke tests
6. Enable regression tests
7. Configure security scanning
8. Set up notifications

## Additional Resources

- [Azure Pipelines Documentation](https://docs.microsoft.com/en-us/azure/devops/pipelines/)
- [Maven Documentation](https://maven.apache.org/guides/)
- [TestNG Documentation](https://testng.org/doc/documentation-main.html)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [ExtentReports Documentation](https://www.extentreports.com/)
