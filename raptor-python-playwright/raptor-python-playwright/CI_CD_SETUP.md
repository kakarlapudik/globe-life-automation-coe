# CI/CD Setup Guide

This document provides step-by-step instructions for setting up CI/CD pipelines for the RAPTOR Python Playwright Framework.

## Quick Start

The RAPTOR framework includes pre-configured CI/CD pipelines for:
- ✅ **GitHub Actions** - `.github/workflows/ci.yml`
- ✅ **Jenkins** - `Jenkinsfile`
- ✅ **Azure DevOps** - `azure-pipelines.yml`

Choose the platform that best fits your organization's needs.

---

## GitHub Actions Setup

### Prerequisites
- GitHub repository
- GitHub account with admin access

### Step 1: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click **Settings** → **Actions** → **General**
3. Under "Actions permissions", select **Allow all actions and reusable workflows**
4. Click **Save**

### Step 2: Configure Secrets

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add the following secrets:

   **TEST_PYPI_API_TOKEN**:
   - Name: `TEST_PYPI_API_TOKEN`
   - Value: Your TestPyPI API token
   - Get token from: https://test.pypi.org/manage/account/token/

   **PYPI_API_TOKEN**:
   - Name: `PYPI_API_TOKEN`
   - Value: Your PyPI API token
   - Get token from: https://pypi.org/manage/account/token/

   **CODECOV_TOKEN** (optional, for private repos):
   - Name: `CODECOV_TOKEN`
   - Value: Your Codecov token
   - Get token from: https://codecov.io/

### Step 3: Enable Branch Protection

1. Go to **Settings** → **Branches**
2. Click **Add rule**
3. Branch name pattern: `main`
4. Enable:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Require linear history
5. Select status checks:
   - ✅ test
   - ✅ integration-test
   - ✅ build
6. Click **Create**

### Step 4: Test the Pipeline

```bash
# Make a change and push
git add .
git commit -m "Test CI/CD"
git push origin main

# View results
# Go to GitHub → Actions tab
```

### ✅ GitHub Actions Setup Complete!

---

## Jenkins Setup

### Prerequisites
- Jenkins server (2.300+)
- Python 3.10+ installed on Jenkins agent
- Git plugin installed

### Step 1: Install Required Plugins

1. Go to **Manage Jenkins** → **Manage Plugins**
2. Install the following plugins:
   - Pipeline
   - Git
   - HTML Publisher
   - JUnit
   - Email Extension Plugin
3. Restart Jenkins

### Step 2: Configure Credentials

1. Go to **Manage Jenkins** → **Manage Credentials**
2. Click **(global)** → **Add Credentials**

   **PyPI Credentials**:
   - Kind: Secret text
   - Scope: Global
   - Secret: Your PyPI API token
   - ID: `pypi-credentials`
   - Description: PyPI API Token

   **TestPyPI Credentials**:
   - Kind: Secret text
   - Scope: Global
   - Secret: Your TestPyPI API token
   - ID: `test-pypi-credentials`
   - Description: TestPyPI API Token

### Step 3: Create Pipeline Job

1. Click **New Item**
2. Enter name: `RAPTOR-CI-CD`
3. Select **Pipeline**
4. Click **OK**

### Step 4: Configure Pipeline

1. Under **Pipeline**, select:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: Your repository URL
   - Credentials: Select your Git credentials
   - Branch Specifier: `*/main`
   - Script Path: `Jenkinsfile`
2. Click **Save**

### Step 5: Configure Email Notifications (Optional)

1. Go to **Manage Jenkins** → **Configure System**
2. Scroll to **Extended E-mail Notification**
3. Configure SMTP server settings
4. Test configuration
5. Click **Save**

### Step 6: Test the Pipeline

1. Click **Build Now**
2. View console output
3. Check HTML reports

### ✅ Jenkins Setup Complete!

---

## Azure DevOps Setup

### Prerequisites
- Azure DevOps organization
- Azure DevOps project
- Project admin access

### Step 1: Import Repository

1. Go to **Repos** → **Files**
2. Click **Import repository**
3. Enter repository URL
4. Click **Import**

### Step 2: Create Service Connections

1. Go to **Project Settings** → **Service connections**
2. Click **New service connection**

   **TestPyPI Connection**:
   - Type: **Python package upload (Twine)**
   - Repository URL: `https://test.pypi.org/legacy/`
   - Username: `__token__`
   - Password: Your TestPyPI API token
   - Service connection name: `TestPyPI`
   - Click **Save**

   **PyPI Connection**:
   - Type: **Python package upload (Twine)**
   - Repository URL: `https://upload.pypi.org/legacy/`
   - Username: `__token__`
   - Password: Your PyPI API token
   - Service connection name: `PyPI`
   - Click **Save**

### Step 3: Create Environments

1. Go to **Pipelines** → **Environments**
2. Click **New environment**

   **TestPyPI Environment**:
   - Name: `test-pypi`
   - Description: TestPyPI deployment environment
   - Click **Create**

   **Production PyPI Environment**:
   - Name: `production-pypi`
   - Description: Production PyPI deployment environment
   - Click **Create**
   - Add approvals:
     - Click **Approvals and checks**
     - Click **Approvals**
     - Add approvers
     - Click **Create**

### Step 4: Create Pipeline

1. Go to **Pipelines** → **Pipelines**
2. Click **New pipeline**
3. Select **Azure Repos Git**
4. Select your repository
5. Select **Existing Azure Pipelines YAML file**
6. Path: `/azure-pipelines.yml`
7. Click **Continue**
8. Click **Run**

### Step 5: Configure Branch Policies

1. Go to **Repos** → **Branches**
2. Click **...** next to `main` → **Branch policies**
3. Enable:
   - ✅ Require a minimum number of reviewers: 1
   - ✅ Check for linked work items
   - ✅ Build validation
     - Build pipeline: Select your pipeline
     - Path filter: Leave empty
     - Trigger: Automatic
4. Click **Save**

### Step 6: Test the Pipeline

```bash
# Make a change and push
git add .
git commit -m "Test CI/CD"
git push origin main

# View results
# Go to Pipelines → Your Pipeline
```

### ✅ Azure DevOps Setup Complete!

---

## Verification

### Test All Pipelines

1. **Make a test change**:
   ```bash
   echo "# Test CI/CD" >> README.md
   git add README.md
   git commit -m "Test CI/CD pipelines"
   git push origin main
   ```

2. **Verify GitHub Actions**:
   - Go to GitHub → Actions tab
   - Check that workflow runs successfully
   - Verify all jobs pass

3. **Verify Jenkins**:
   - Go to Jenkins Dashboard
   - Check that build runs successfully
   - Verify all stages pass

4. **Verify Azure DevOps**:
   - Go to Pipelines → Your Pipeline
   - Check that pipeline runs successfully
   - Verify all stages pass

### Expected Results

All pipelines should:
- ✅ Run linting checks
- ✅ Run type checking
- ✅ Execute unit tests
- ✅ Execute property-based tests
- ✅ Execute integration tests
- ✅ Execute E2E tests
- ✅ Execute performance tests
- ✅ Run security scans
- ✅ Build distributions
- ✅ Build documentation

---

## Troubleshooting

### GitHub Actions

**Issue**: Workflow doesn't trigger
- **Solution**: Check branch protection rules and workflow triggers

**Issue**: Secrets not found
- **Solution**: Verify secrets are added in repository settings

**Issue**: Tests fail
- **Solution**: Check Actions logs for detailed error messages

### Jenkins

**Issue**: Pipeline not found
- **Solution**: Verify Jenkinsfile is in repository root

**Issue**: Credentials not found
- **Solution**: Check credential IDs match Jenkinsfile

**Issue**: Email notifications not working
- **Solution**: Configure SMTP settings in Jenkins

### Azure DevOps

**Issue**: Service connection fails
- **Solution**: Verify API tokens are valid and not expired

**Issue**: Environment not found
- **Solution**: Create environments in Pipelines → Environments

**Issue**: Build validation fails
- **Solution**: Check branch policies and pipeline configuration

---

## Next Steps

After setup is complete:

1. **Monitor Builds**: Check build status regularly
2. **Review Reports**: Check test results and coverage reports
3. **Optimize**: Identify slow stages and optimize
4. **Train Team**: Ensure team knows how to use CI/CD
5. **Iterate**: Continuously improve based on feedback

---

## Support

For help with CI/CD setup:

1. Check [CI/CD Integration Guide](docs/CI_CD_INTEGRATION_GUIDE.md)
2. Check [CI/CD Quick Reference](docs/CI_CD_QUICK_REFERENCE.md)
3. Check platform documentation:
   - [GitHub Actions](https://docs.github.com/en/actions)
   - [Jenkins](https://www.jenkins.io/doc/)
   - [Azure DevOps](https://docs.microsoft.com/en-us/azure/devops/)
4. Open an issue in the repository

---

## Summary

✅ **GitHub Actions**: Cloud-based, easy setup, great for open source
✅ **Jenkins**: Self-hosted, highly customizable, great for enterprises
✅ **Azure DevOps**: Integrated platform, great for Microsoft shops

Choose the platform that best fits your needs. All three are fully configured and ready to use!
