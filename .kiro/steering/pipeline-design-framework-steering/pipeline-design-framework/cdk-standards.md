---
inclusion: manual
---

# Pipeline Design Framework - CDK Standards

This document defines coding standards and best practices for AWS CDK development across TypeScript, Python, and .NET implementations.

## General CDK Principles

### 1. Stack Design

- Keep stacks focused and single-purpose
- Use stack dependencies for resource sharing
- Limit stack size (< 200 resources per stack)
- Use nested stacks for complex applications

### 2. Construct Hierarchy

```
App
└── Stage (optional, for pipelines)
    └── Stack
        └── Constructs
            └── Resources
```

### 3. Naming Conventions

- Stack names: PascalCase (e.g., `NetworkStack`, `ApplicationStack`)
- Construct IDs: PascalCase (e.g., `ApiGateway`, `UserTable`)
- Resource names: kebab-case with environment prefix (e.g., `dev-api-gateway`)

## TypeScript Standards

### Project Structure

```
cdk-app/
├── bin/
│   └── app.ts                 # CDK app entry point
├── lib/
│   ├── pipeline-stack.ts      # Pipeline infrastructure
│   ├── application-stack.ts   # Application resources
│   └── constructs/            # Reusable constructs
│       ├── secure-bucket.ts
│       └── monitored-lambda.ts
├── test/
│   ├── pipeline-stack.test.ts
│   └── application-stack.test.ts
├── cdk.json                   # CDK configuration
├── package.json
└── tsconfig.json
```

### Stack Implementation

```typescript
import * as cdk from 'aws-cdk-lib'
import { Construct } from 'constructs'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import * as apigateway from 'aws-cdk-lib/aws-apigateway'

export interface ApplicationStackProps extends cdk.StackProps {
  readonly environment: string
  readonly permissionsBoundaryArn?: string
}

export class ApplicationStack extends cdk.Stack {
  public readonly api: apigateway.RestApi
  public readonly handler: lambda.Function

  constructor(scope: Construct, id: string, props: ApplicationStackProps) {
    super(scope, id, props)

    // Apply permissions boundary if provided
    if (props.permissionsBoundaryArn) {
      cdk.Aspects.of(this).add(
        new PermissionsBoundaryAspect(props.permissionsBoundaryArn)
      )
    }

    // Create Lambda function
    this.handler = new lambda.Function(this, 'Handler', {
      runtime: lambda.Runtime.NODEJS_18_X,
      code: lambda.Code.fromAsset('lambda'),
      handler: 'index.handler',
      environment: {
        ENVIRONMENT: props.environment,
      },
      description: `API handler for ${props.environment}`,
    })

    // Create API Gateway
    this.api = new apigateway.RestApi(this, 'Api', {
      restApiName: `${props.environment}-api`,
      description: `API for ${props.environment} environment`,
      deployOptions: {
        stageName: props.environment,
        loggingLevel: apigateway.MethodLoggingLevel.INFO,
        dataTraceEnabled: true,
      },
    })

    // Add integration
    const integration = new apigateway.LambdaIntegration(this.handler)
    this.api.root.addMethod('GET', integration)

    // Add tags
    cdk.Tags.of(this).add('Environment', props.environment)
    cdk.Tags.of(this).add('ManagedBy', 'CDK')
  }
}
```

### Custom Constructs

```typescript
import { Construct } from 'constructs'
import * as s3 from 'aws-cdk-lib/aws-s3'
import * as kms from 'aws-cdk-lib/aws-kms'
import { RemovalPolicy } from 'aws-cdk-lib'

export interface SecureBucketProps {
  readonly bucketName: string
  readonly environment: string
  readonly retentionDays?: number
}

export class SecureBucket extends Construct {
  public readonly bucket: s3.Bucket
  public readonly encryptionKey: kms.Key

  constructor(scope: Construct, id: string, props: SecureBucketProps) {
    super(scope, id)

    // Create KMS key for encryption
    this.encryptionKey = new kms.Key(this, 'EncryptionKey', {
      description: `Encryption key for ${props.bucketName}`,
      enableKeyRotation: true,
      removalPolicy: RemovalPolicy.RETAIN,
    })

    // Create secure S3 bucket
    this.bucket = new s3.Bucket(this, 'Bucket', {
      bucketName: props.bucketName,
      encryption: s3.BucketEncryption.KMS,
      encryptionKey: this.encryptionKey,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      versioned: true,
      lifecycleRules: props.retentionDays ? [
        {
          expiration: cdk.Duration.days(props.retentionDays),
          noncurrentVersionExpiration: cdk.Duration.days(30),
        },
      ] : undefined,
      enforceSSL: true,
      removalPolicy: props.environment === 'prod' 
        ? RemovalPolicy.RETAIN 
        : RemovalPolicy.DESTROY,
    })
  }
}
```

### Pipeline Stack

```typescript
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline'
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions'
import * as codebuild from 'aws-cdk-lib/aws-codebuild'
import { pipelines } from 'aws-cdk-lib'

export class PipelineStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props)

    // Create CDK Pipeline
    const pipeline = new pipelines.CodePipeline(this, 'Pipeline', {
      pipelineName: 'ApplicationPipeline',
      synth: new pipelines.ShellStep('Synth', {
        input: pipelines.CodePipelineSource.connection(
          'org/repo',
          'main',
          {
            connectionArn: 'arn:aws:codestar-connections:...',
          }
        ),
        commands: [
          'npm ci',
          'npm run build',
          'npx cdk synth',
        ],
      }),
      crossAccountKeys: true,
      enableKeyRotation: true,
    })

    // Add dev stage
    const devStage = new ApplicationStage(this, 'Dev', {
      env: { account: '111111111111', region: 'us-east-1' },
      environment: 'dev',
    })
    pipeline.addStage(devStage)

    // Add prod stage with manual approval
    const prodStage = new ApplicationStage(this, 'Prod', {
      env: { account: '222222222222', region: 'us-east-1' },
      environment: 'prod',
    })
    pipeline.addStage(prodStage, {
      pre: [new pipelines.ManualApprovalStep('PromoteToProd')],
    })
  }
}
```

## Python Standards

### Project Structure

```
cdk-app/
├── app.py                     # CDK app entry point
├── stacks/
│   ├── __init__.py
│   ├── pipeline_stack.py
│   └── application_stack.py
├── constructs/
│   ├── __init__.py
│   └── secure_bucket.py
├── tests/
│   ├── __init__.py
│   └── test_stacks.py
├── cdk.json
└── requirements.txt
```

### Stack Implementation

```python
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    Tags,
    Duration,
)
from constructs import Construct
from typing import Optional

class ApplicationStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        environment: str,
        permissions_boundary_arn: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Lambda function
        self.handler = lambda_.Function(
            self,
            "Handler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("lambda"),
            handler="index.handler",
            environment={
                "ENVIRONMENT": environment,
            },
            description=f"API handler for {environment}",
            timeout=Duration.seconds(30),
        )

        # Create API Gateway
        self.api = apigateway.RestApi(
            self,
            "Api",
            rest_api_name=f"{environment}-api",
            description=f"API for {environment} environment",
            deploy_options=apigateway.StageOptions(
                stage_name=environment,
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
            ),
        )

        # Add integration
        integration = apigateway.LambdaIntegration(self.handler)
        self.api.root.add_method("GET", integration)

        # Add tags
        Tags.of(self).add("Environment", environment)
        Tags.of(self).add("ManagedBy", "CDK")
```

### Custom Constructs

```python
from constructs import Construct
from aws_cdk import (
    aws_s3 as s3,
    aws_kms as kms,
    RemovalPolicy,
    Duration,
)

class SecureBucket(Construct):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        bucket_name: str,
        environment: str,
        retention_days: int = None,
    ) -> None:
        super().__init__(scope, construct_id)

        # Create KMS key
        self.encryption_key = kms.Key(
            self,
            "EncryptionKey",
            description=f"Encryption key for {bucket_name}",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.RETAIN,
        )

        # Create secure bucket
        lifecycle_rules = []
        if retention_days:
            lifecycle_rules.append(
                s3.LifecycleRule(
                    expiration=Duration.days(retention_days),
                    noncurrent_version_expiration=Duration.days(30),
                )
            )

        self.bucket = s3.Bucket(
            self,
            "Bucket",
            bucket_name=bucket_name,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.encryption_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            versioned=True,
            lifecycle_rules=lifecycle_rules if lifecycle_rules else None,
            enforce_ssl=True,
            removal_policy=(
                RemovalPolicy.RETAIN
                if environment == "prod"
                else RemovalPolicy.DESTROY
            ),
        )
```

## .NET Standards

### Project Structure

```
CdkApp/
├── src/
│   ├── CdkApp/
│   │   ├── Program.cs
│   │   ├── PipelineStack.cs
│   │   ├── ApplicationStack.cs
│   │   └── Constructs/
│   │       └── SecureBucket.cs
├── test/
│   └── CdkApp.Tests/
│       └── StackTests.cs
├── cdk.json
└── CdkApp.sln
```

### Stack Implementation

```csharp
using Amazon.CDK;
using Amazon.CDK.AWS.Lambda;
using Amazon.CDK.AWS.APIGateway;
using Constructs;

namespace CdkApp
{
    public class ApplicationStackProps : StackProps
    {
        public string Environment { get; set; }
        public string PermissionsBoundaryArn { get; set; }
    }

    public class ApplicationStack : Stack
    {
        public RestApi Api { get; }
        public Function Handler { get; }

        public ApplicationStack(
            Construct scope,
            string id,
            ApplicationStackProps props
        ) : base(scope, id, props)
        {
            // Create Lambda function
            Handler = new Function(this, "Handler", new FunctionProps
            {
                Runtime = Runtime.DOTNET_6,
                Code = Code.FromAsset("lambda"),
                Handler = "Handler::Handler.Function::FunctionHandler",
                Environment = new Dictionary<string, string>
                {
                    ["ENVIRONMENT"] = props.Environment
                },
                Description = $"API handler for {props.Environment}",
                Timeout = Duration.Seconds(30)
            });

            // Create API Gateway
            Api = new RestApi(this, "Api", new RestApiProps
            {
                RestApiName = $"{props.Environment}-api",
                Description = $"API for {props.Environment} environment",
                DeployOptions = new StageOptions
                {
                    StageName = props.Environment,
                    LoggingLevel = MethodLoggingLevel.INFO,
                    DataTraceEnabled = true
                }
            });

            // Add integration
            var integration = new LambdaIntegration(Handler);
            Api.Root.AddMethod("GET", integration);

            // Add tags
            Tags.Of(this).Add("Environment", props.Environment);
            Tags.Of(this).Add("ManagedBy", "CDK");
        }
    }
}
```

## Best Practices

### 1. Environment Configuration

```typescript
// Use CDK context for environment-specific values
const config = this.node.tryGetContext(environment)

// Or use environment variables
const dbPassword = cdk.SecretValue.secretsManager('db-password')
```

### 2. Resource Naming

```typescript
// Include environment in resource names
const tableName = `${environment}-users-table`

// Use logical IDs that are stable
new dynamodb.Table(this, 'UsersTable', {
  tableName: tableName,
})
```

### 3. Removal Policies

```typescript
// Production resources should be retained
const removalPolicy = environment === 'prod' 
  ? RemovalPolicy.RETAIN 
  : RemovalPolicy.DESTROY
```

### 4. Permissions Boundaries

```typescript
// Apply to all IAM roles in the stack
cdk.Aspects.of(this).add(
  new PermissionsBoundaryAspect(permissionsBoundaryArn)
)
```

### 5. Testing

```typescript
// Use CDK assertions for testing
import { Template } from 'aws-cdk-lib/assertions'

test('Lambda function created', () => {
  const app = new cdk.App()
  const stack = new ApplicationStack(app, 'TestStack', {
    environment: 'test',
  })
  
  const template = Template.fromStack(stack)
  template.hasResourceProperties('AWS::Lambda::Function', {
    Runtime: 'nodejs18.x',
  })
})
```

### 6. Security

- Always enable encryption at rest
- Use KMS keys with rotation enabled
- Block public access on S3 buckets
- Enable SSL/TLS enforcement
- Apply least privilege IAM policies
- Use VPC endpoints where applicable

### 7. Cost Optimization

- Use appropriate instance sizes per environment
- Enable auto-scaling where applicable
- Set retention policies on logs
- Use lifecycle policies on S3
- Clean up unused resources

### 8. Monitoring

- Enable CloudWatch logging
- Create alarms for critical metrics
- Use X-Ray for distributed tracing
- Tag all resources for cost tracking
