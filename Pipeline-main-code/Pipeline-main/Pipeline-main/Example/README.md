# CI/CD Applications 

## Overview
This section outlines the GitHub Actions workflow for deploying infrastructure across multiple AWS accounts using CDK.

## Prerequisites
- Basic understanding of GitHub workflows actions and CDK. 
- GitHub repository access
- AWS accounts set up for development, testing, staging, and production
- Appropriate IAM roles and permissions boundaries configured
- Self-hosted GitHub runner

## Template Configuration

### Workflow Trigger
The workflow can be triggered by:
- Pull request into `main` branch
- Manual trigger using GitHub Actions interface (workflow_dispatch)

### Required Parameters
To use this template, configure the following parameters in your deploy.yml:

```yaml
dev-account: '<your-dev-account-id>'        # Development AWS account, optional, comment if not used
tst-account: '<your-test-account-id>'       # Test AWS account, optional, comment if not used
stg-account: '<your-staging-account-id>'    # Staging AWS account, optional, comment if not used
prd-account: '<your-prod-account-id>'       # Production AWS account, optional, comment if not used
app-name: '<your-app-name>'                 # Max 10 alphanumeric characters, groupiing of related stacks 
stack-id: '<your-stack-id>'                 # Max 10 alphanumeric characters
app-dir: '${{ github.workspace }}/ApplicationStackCode'  # CDK application directory containing cdk.json
permissions-boundary: '<your-boundary-name>' # IAM permissions boundary, for central account
role-to-assume: 'arn:aws:iam::<account-id>:role/GitHub_AccessRole' # OIDC IAM role ARN, account-id of central account
platform: 'typescript'                       # Supported: .net, python, typescript
cross-account-boundary: 'Boundary_<appspecific)' # boundary policy for bootstrapping in target accounts, supplied by AWS WebOps
approval-notification: '<email>'             # request for approval email/dist list
action-type: 'deploy/destroy'                # will deploy CDK or destroy CDK, CDK must be updated, a comment can be used
```

### Required Permissions
The workflow requires the following GitHub permissions:

```yaml
permissions:
  deployments: write
  statuses: write
  contents: write
  id-token: write
  actions: write
  checks: write
  packages: write
  pull-requests: write
```

### Branch Strategy
1. **Branch Setup**
   - Deployment should be execute using main branch.
   - Update the workflow trigger in deploy.yml to match your branch name:
   ```yaml
   on:
     push:
       branches:
         - main    # it must be main 
     workflow_dispatch:

## Stack Creation Standards

### Overview
This section outlines the standardized approach for creating new CDK stacks using DefaultStackSynthesizer with APP_NAME as a qualifier, applicable across supported CDK languages (.NET, Python, TypeScript).

### Required Environment Variables
The following environment variables must be setup:
- `APP_NAME`: Application identifier (max 10 alphanumeric characters).
- `CDK_DEFAULT_ACCOUNT`: AWS account ID
- `CDK_DEFAULT_REGION`: AWS region

## Stack Creation Templates

### Implementation Guidelines
1. Stack Naming Conventions
  - Stack names must follow the pattern: 'AppStack' + APP_NAME + STACK_ID
  - APP_NAME must be converted to lowercase when used as qualifier

2. DefaultStackSynthesizer Configuration
  - Required properties for all languages:
  - qualifier: lowercase APP_NAME value

3. Stack Properties
  - Required stack properties across all languages:
  - synthesizer/Synthesizer: DefaultStackSynthesizer instance
  - env/Environment: Account and Region configuration

### Language-Specific Stack Instantiation

### TypeScript/JavaScript
```typescript
import * as cdk from 'aws-cdk-lib';
import { ApplicationStack } from '../lib/cdk-code-stack';

const appTst = new cdk.App();

function getRequiredEnvVar(name: string): string {
  const value = process.env[name];
  if (!value) {
      throw new Error(`Required environment variable ${name} is not set`);
  }
  return value;
}
const app_name = getRequiredEnvVar('APP_NAME');
const stack_id = getRequiredEnvVar('STACK_ID');
const qualifier = app_name.toLowerCase();

const appDefaultSynthesizerApp = new cdk.DefaultStackSynthesizer({
  bucketPrefix: cdk.DefaultStackSynthesizer.DEFAULT_FILE_ASSET_PREFIX,
  qualifier: qualifier
});


new ApplicationStack(appTst, 'AppStack' + app_name + stack_id,{ // 'AppStack' + app_name + stack_id
  synthesizer: appDefaultSynthesizerApp,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
  
});

appTst.synth();
```
#### Python
```Python

import os
from aws_cdk import App, DefaultStackSynthesizer

app = App()
app_name = os.environ.get('APP_NAME', '').lower()
stack_id = os.environ.get('STACK_ID', '').lower()
if not app_name:
    raise ValueError('APP_NAME environment variable is required')

stack_synthesizer = DefaultStackSynthesizer(
    qualifier=app_name
)

YourStack(app, f"AppStack{app_name}{stack_id}",
    synthesizer=stack_synthesizer,
    env={
        'account': os.environ.get('CDK_DEFAULT_ACCOUNT'),
        'region': os.environ.get('CDK_DEFAULT_REGION')
    }
)
```

#### .NET
```C#

  using Amazon.CDK;
   
  var app = new App();
  var appName = Environment.GetEnvironmentVariable("APP_NAME")?.ToLowerInvariant();
  if (string.IsNullOrEmpty(appName))
      throw new Exception("APP_NAME environment variable is required");

  var stackId = Environment.GetEnvironmentVariable("STACK_ID")?.ToLowerInvariant();
  if (string.IsNullOrEmpty(stackId))
      throw new Exception("STACK_ID environment variable is required");

  var stackSynthesizer = new DefaultStackSynthesizer(new DefaultStackSynthesizerProps
  {
      Qualifier = appName
  });

  new YourStack(app, $"AppStack{appName}{stackId}", new StackProps
  {
      Synthesizer = stackSynthesizer,
      Env = new Environment
      {
          Account = System.Environment.GetEnvironmentVariable("CDK_DEFAULT_ACCOUNT"),
          Region = System.Environment.GetEnvironmentVariable("CDK_DEFAULT_REGION")
      }
  });

```
## Troubleshooting
Common issues to watch for:
- Incorrect AWS account IDs
- Missing or invalid permissions
- CDK synthesis failures
- Runner connectivity issues
- Invalid application directory structure

