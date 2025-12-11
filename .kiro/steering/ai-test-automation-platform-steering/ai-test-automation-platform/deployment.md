---
inclusion: manual
---

# Deployment and Operations Guide

This document provides comprehensive guidance for deploying and operating the AI Test Automation Platform in AWS environments.

## Deployment Architecture

### AWS Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        CloudFront CDN                        │
│                    (Frontend Distribution)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
    ┌────▼────┐                 ┌───▼────┐
    │   S3    │                 │  API   │
    │ Bucket  │                 │Gateway │
    │(Static) │                 └───┬────┘
    └─────────┘                     │
                          ┌─────────┴──────────┐
                          │                    │
                     ┌────▼─────┐        ┌────▼─────┐
                     │  Lambda  │        │  Lambda  │
                     │ Function │        │ Function │
                     │  (Auth)  │        │  (Test)  │
                     └────┬─────┘        └────┬─────┘
                          │                   │
                          └─────────┬─────────┘
                                    │
                    ┌───────────────┴────────────────┐
                    │                                │
               ┌────▼────┐                     ┌────▼────┐
               │DynamoDB │                     │   S3    │
               │  Table  │                     │ Bucket  │
               │ (Data)  │                     │(Storage)│
               └─────────┘                     └─────────┘
```

## AWS CDK Deployment

### CDK Stack Structure

```python
# infrastructure/app.py
#!/usr/bin/env python3
import aws_cdk as cdk
from stacks.pipeline_stack import PipelineStack
from stacks.application_stack import ApplicationStack

app = cdk.App()

# Environment configuration
env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region")
)

# Pipeline stack for CI/CD
pipeline_stack = PipelineStack(
    app,
    "AITestAutomationPipeline",
    env=env
)

# Application stack
application_stack = ApplicationStack(
    app,
    "AITestAutomationApp",
    env=env
)

app.synth()
```

### Application Stack Definition

```python
# infrastructure/stacks/application_stack.py
from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_apigateway as apigw,
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cognito as cognito,
    Duration,
    RemovalPolicy
)
from constructs import Construct

class ApplicationStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB Tables
        self.test_cases_table = self._create_test_cases_table()
        self.test_executions_table = self._create_test_executions_table()
        
        # S3 Buckets
        self.test_data_bucket = self._create_test_data_bucket()
        self.frontend_bucket = self._create_frontend_bucket()
        
        # Cognito User Pool
        self.user_pool = self._create_user_pool()
        
        # Lambda Functions
        self.test_execution_function = self._create_test_execution_function()
        self.ai_analysis_function = self._create_ai_analysis_function()
        
        # API Gateway
        self.api = self._create_api_gateway()
        
        # CloudFront Distribution
        self.distribution = self._create_cloudfront_distribution()
    
    def _create_test_cases_table(self) -> dynamodb.Table:
        """Create DynamoDB table for test cases."""
        table = dynamodb.Table(
            self,
            "TestCasesTable",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN
        )
        
        # Add GSI for querying by status
        table.add_global_secondary_index(
            index_name="GSI1",
            partition_key=dynamodb.Attribute(
                name="GSI1PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="GSI1SK",
                type=dynamodb.AttributeType.STRING
            )
        )
        
        return table
    
    def _create_test_executions_table(self) -> dynamodb.Table:
        """Create DynamoDB table for test executions."""
        return dynamodb.Table(
            self,
            "TestExecutionsTable",
            partition_key=dynamodb.Attribute(
                name="PK",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="SK",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            point_in_time_recovery=True,
            removal_policy=RemovalPolicy.RETAIN
        )
    
    def _create_test_data_bucket(self) -> s3.Bucket:
        """Create S3 bucket for test data storage."""
        return s3.Bucket(
            self,
            "TestDataBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldVersions",
                    noncurrent_version_expiration=Duration.days(90)
                )
            ],
            removal_policy=RemovalPolicy.RETAIN
        )
    
    def _create_frontend_bucket(self) -> s3.Bucket:
        """Create S3 bucket for frontend static files."""
        return s3.Bucket(
            self,
            "FrontendBucket",
            website_index_document="index.html",
            website_error_document="index.html",
            public_read_access=False,
            removal_policy=RemovalPolicy.DESTROY
        )
    
    def _create_user_pool(self) -> cognito.UserPool:
        """Create Cognito User Pool for authentication."""
        user_pool = cognito.UserPool(
            self,
            "UserPool",
            user_pool_name="ai-test-automation-users",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(
                email=True,
                username=True
            ),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=True
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY
        )
        
        # Add app client
        user_pool.add_client(
            "WebClient",
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(
                    authorization_code_grant=True
                ),
                scopes=[cognito.OAuthScope.OPENID, cognito.OAuthScope.EMAIL]
            )
        )
        
        return user_pool
    
    def _create_test_execution_function(self) -> lambda_.Function:
        """Create Lambda function for test execution."""
        function = lambda_.Function(
            self,
            "TestExecutionFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handlers.test_execution.lambda_handler",
            code=lambda_.Code.from_asset("../src"),
            timeout=Duration.minutes(5),
            memory_size=1024,
            environment={
                "TEST_CASES_TABLE": self.test_cases_table.table_name,
                "TEST_EXECUTIONS_TABLE": self.test_executions_table.table_name,
                "TEST_DATA_BUCKET": self.test_data_bucket.bucket_name
            },
            tracing=lambda_.Tracing.ACTIVE
        )
        
        # Grant permissions
        self.test_cases_table.grant_read_data(function)
        self.test_executions_table.grant_read_write_data(function)
        self.test_data_bucket.grant_read_write(function)
        
        return function
    
    def _create_ai_analysis_function(self) -> lambda_.Function:
        """Create Lambda function for AI analysis."""
        function = lambda_.Function(
            self,
            "AIAnalysisFunction",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="handlers.ai_analysis.lambda_handler",
            code=lambda_.Code.from_asset("../src"),
            timeout=Duration.minutes(3),
            memory_size=2048,
            environment={
                "TEST_EXECUTIONS_TABLE": self.test_executions_table.table_name
            },
            tracing=lambda_.Tracing.ACTIVE
        )
        
        # Grant permissions
        self.test_executions_table.grant_read_write_data(function)
        
        return function
    
    def _create_api_gateway(self) -> apigw.RestApi:
        """Create API Gateway."""
        api = apigw.RestApi(
            self,
            "TestAutomationAPI",
            rest_api_name="AI Test Automation API",
            description="API for AI Test Automation Platform",
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                throttling_rate_limit=1000,
                throttling_burst_limit=2000,
                logging_level=apigw.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                metrics_enabled=True
            ),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS
            )
        )
        
        # Add resources and methods
        test_execution = api.root.add_resource("test-execution")
        test_execution.add_method(
            "POST",
            apigw.LambdaIntegration(self.test_execution_function)
        )
        
        return api
    
    def _create_cloudfront_distribution(self) -> cloudfront.Distribution:
        """Create CloudFront distribution for frontend."""
        origin_access_identity = cloudfront.OriginAccessIdentity(
            self,
            "OAI",
            comment="OAI for frontend bucket"
        )
        
        self.frontend_bucket.grant_read(origin_access_identity)
        
        distribution = cloudfront.Distribution(
            self,
            "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=cloudfront.S3Origin(
                    self.frontend_bucket,
                    origin_access_identity=origin_access_identity
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html"
                )
            ]
        )
        
        return distribution
```

## Deployment Process

### Prerequisites

```bash
# Install AWS CDK
npm install -g aws-cdk

# Install Python dependencies
pip install -r requirements.txt

# Configure AWS credentials
aws configure
```

### Deployment Commands

```bash
# Bootstrap CDK (first time only)
cdk bootstrap aws://ACCOUNT-ID/REGION

# Synthesize CloudFormation template
cdk synth

# Deploy application stack
cdk deploy AITestAutomationApp

# Deploy all stacks
cdk deploy --all

# Destroy stack (cleanup)
cdk destroy AITestAutomationApp
```

### Environment-Specific Deployments

```bash
# Deploy to development
cdk deploy --context environment=development

# Deploy to staging
cdk deploy --context environment=staging

# Deploy to production
cdk deploy --context environment=production
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy to AWS

on:
  push:
    branches:
      - main
      - develop

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          npm ci
      
      - name: Run tests
        run: |
          pytest tests/
          npm run test
      
      - name: Build frontend
        run: npm run build
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy with CDK
        run: |
          cd infrastructure
          cdk deploy --require-approval never
      
      - name: Upload frontend to S3
        run: |
          aws s3 sync dist/ s3://${{ secrets.FRONTEND_BUCKET }}/ --delete
      
      - name: Invalidate CloudFront cache
        run: |
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} \
            --paths "/*"
```

## Monitoring and Observability

### CloudWatch Dashboards

```python
# infrastructure/monitoring/dashboard.py
from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    aws_lambda as lambda_
)

class MonitoringDashboard:
    def __init__(self, stack, functions: dict):
        self.dashboard = cloudwatch.Dashboard(
            stack,
            "TestAutomationDashboard",
            dashboard_name="AI-Test-Automation-Platform"
        )
        
        self._add_lambda_metrics(functions)
        self._add_api_metrics()
        self._add_dynamodb_metrics()
    
    def _add_lambda_metrics(self, functions: dict):
        """Add Lambda function metrics to dashboard."""
        for name, function in functions.items():
            self.dashboard.add_widgets(
                cloudwatch.GraphWidget(
                    title=f"{name} - Invocations",
                    left=[function.metric_invocations()],
                    width=12
                ),
                cloudwatch.GraphWidget(
                    title=f"{name} - Duration",
                    left=[function.metric_duration()],
                    width=12
                ),
                cloudwatch.GraphWidget(
                    title=f"{name} - Errors",
                    left=[function.metric_errors()],
                    width=12
                )
            )
```

### Alarms Configuration

```python
# infrastructure/monitoring/alarms.py
from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_sns as sns
)

class AlarmConfiguration:
    def __init__(self, stack, functions: dict):
        # Create SNS topic for alarms
        self.alarm_topic = sns.Topic(
            stack,
            "AlarmTopic",
            display_name="Test Automation Alarms"
        )
        
        # Add email subscription
        self.alarm_topic.add_subscription(
            sns_subscriptions.EmailSubscription("ops@example.com")
        )
        
        self._create_lambda_alarms(stack, functions)
    
    def _create_lambda_alarms(self, stack, functions: dict):
        """Create alarms for Lambda functions."""
        for name, function in functions.items():
            # Error rate alarm
            error_alarm = cloudwatch.Alarm(
                stack,
                f"{name}ErrorAlarm",
                metric=function.metric_errors(),
                threshold=10,
                evaluation_periods=2,
                alarm_description=f"High error rate for {name}"
            )
            error_alarm.add_alarm_action(
                cw_actions.SnsAction(self.alarm_topic)
            )
            
            # Duration alarm
            duration_alarm = cloudwatch.Alarm(
                stack,
                f"{name}DurationAlarm",
                metric=function.metric_duration(),
                threshold=30000,  # 30 seconds
                evaluation_periods=3,
                alarm_description=f"High duration for {name}"
            )
            duration_alarm.add_alarm_action(
                cw_actions.SnsAction(self.alarm_topic)
            )
```

## Security Best Practices

### IAM Roles and Policies

```python
# infrastructure/security/iam_policies.py
from aws_cdk import (
    aws_iam as iam
)

class SecurityPolicies:
    @staticmethod
    def create_lambda_execution_role(stack, table_arns: list, bucket_arns: list):
        """Create IAM role for Lambda execution."""
        role = iam.Role(
            stack,
            "LambdaExecutionRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSXRayDaemonWriteAccess"
                )
            ]
        )
        
        # Add DynamoDB permissions
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:GetItem",
                    "dynamodb:PutItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:Query",
                    "dynamodb:Scan"
                ],
                resources=table_arns
            )
        )
        
        # Add S3 permissions
        role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                resources=[f"{arn}/*" for arn in bucket_arns]
            )
        )
        
        return role
```

### Secrets Management

```python
# src/utils/secrets.py
import boto3
import json
from functools import lru_cache

class SecretsManager:
    def __init__(self):
        self.client = boto3.client('secretsmanager')
    
    @lru_cache(maxsize=10)
    def get_secret(self, secret_name: str) -> dict:
        """Retrieve secret from AWS Secrets Manager."""
        try:
            response = self.client.get_secret_value(SecretId=secret_name)
            return json.loads(response['SecretString'])
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            raise

# Usage
secrets_manager = SecretsManager()
api_keys = secrets_manager.get_secret('ai-test-automation/api-keys')
```

## Operational Procedures

### Backup and Recovery

```python
# scripts/backup_dynamodb.py
import boto3
from datetime import datetime

def backup_dynamodb_table(table_name: str):
    """Create on-demand backup of DynamoDB table."""
    dynamodb = boto3.client('dynamodb')
    
    backup_name = f"{table_name}-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    response = dynamodb.create_backup(
        TableName=table_name,
        BackupName=backup_name
    )
    
    print(f"Backup created: {response['BackupDetails']['BackupArn']}")
    return response

# Run backup
backup_dynamodb_table('TestCasesTable')
backup_dynamodb_table('TestExecutionsTable')
```

### Scaling Configuration

```python
# infrastructure/scaling/autoscaling.py
from aws_cdk import (
    aws_applicationautoscaling as appscaling
)

class AutoScalingConfiguration:
    @staticmethod
    def configure_dynamodb_autoscaling(table):
        """Configure auto-scaling for DynamoDB table."""
        read_scaling = table.auto_scale_read_capacity(
            min_capacity=5,
            max_capacity=100
        )
        
        read_scaling.scale_on_utilization(
            target_utilization_percent=70
        )
        
        write_scaling = table.auto_scale_write_capacity(
            min_capacity=5,
            max_capacity=100
        )
        
        write_scaling.scale_on_utilization(
            target_utilization_percent=70
        )
```

This deployment guide provides a comprehensive foundation for deploying and operating the AI Test Automation Platform on AWS with best practices for security, monitoring, and scalability.
