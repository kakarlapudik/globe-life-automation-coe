---
inclusion: manual
---

# AI Test Automation Platform - CDK Pipeline Standards

This document defines the AWS CDK pipeline configuration for the AI Test Automation Platform, following the pipeline-design-framework standards.

## Overview

The AI Test Automation Platform uses AWS CDK to deploy serverless infrastructure across multiple AWS accounts (dev, staging, production). The pipeline follows the standards defined in the pipeline-design-framework.

## Architecture

### Stack Organization

```
ai-test-automation-platform/
├── infrastructure/
│   ├── bin/
│   │   └── app.ts                    # CDK app entry point
│   ├── lib/
│   │   ├── pipeline-stack.ts         # CI/CD pipeline
│   │   ├── backend-stack.ts          # Lambda functions, API Gateway
│   │   ├── data-stack.ts             # DynamoDB tables
│   │   ├── frontend-stack.ts         # S3, CloudFront for Vue.js app
│   │   └── constructs/
│   │       ├── secure-lambda.ts      # Lambda with security defaults
│   │       └── monitored-api.ts      # API Gateway with logging
│   ├── test/
│   │   └── stacks.test.ts
│   └── cdk.json
```

### Application Stacks

**1. Backend Stack**
- Lambda functions for NLP service, element detection, test execution
- Lambda functions for DDFE object repository (MySQL operations)
- API Gateway with JWT authentication
- CloudWatch Logs and X-Ray tracing
- Secrets Manager for API keys and MySQL credentials
- VPC configuration for Lambda-to-RDS connectivity

**2. Data Stack**
- DynamoDB tables for test definitions, results, users
- RDS MySQL for DDFE (Data-Driven Framework Engine) object repository
- KMS encryption keys for both DynamoDB and RDS
- Point-in-time recovery enabled
- Backup policies for both data stores

**3. Frontend Stack**
- S3 bucket for Vue.js static assets
- CloudFront distribution with HTTPS
- WAF rules for security
- Route53 DNS configuration

**4. Pipeline Stack**
- CodePipeline for CI/CD
- CodeBuild for testing and deployment
- Cross-account deployment roles
- Manual approval for production

## Environment Configuration

### Dev Environment
```typescript
{
  account: process.env.DEV_ACCOUNT_ID,
  region: 'us-east-1',
  lambdaMemory: 512,
  lambdaTimeout: 30,
  dynamodbBilling: 'PAY_PER_REQUEST',
  mysqlInstanceClass: 'db.t3.micro',
  mysqlAllocatedStorage: 20,
  enableMultiAz: false,
  enableXRay: true,
  logRetention: 7
}
```

### Staging Environment
```typescript
{
  account: process.env.STAGING_ACCOUNT_ID,
  region: 'us-east-1',
  lambdaMemory: 1024,
  lambdaTimeout: 60,
  dynamodbBilling: 'PAY_PER_REQUEST',
  mysqlInstanceClass: 'db.t3.small',
  mysqlAllocatedStorage: 50,
  enableMultiAz: true,
  enableXRay: true,
  logRetention: 30
}
```

### Production Environment
```typescript
{
  account: process.env.PROD_ACCOUNT_ID,
  region: 'us-east-1',
  lambdaMemory: 2048,
  lambdaTimeout: 300,
  dynamodbBilling: 'PROVISIONED',
  mysqlInstanceClass: 'db.r5.large',
  mysqlAllocatedStorage: 100,
  enableMultiAz: true,
  enableReadReplica: true,
  enableXRay: true,
  logRetention: 90,
  enableBackup: true
}
```

## Security Standards

### IAM Permissions
- All Lambda functions use least privilege IAM roles
- Permissions boundaries applied to all roles
- No wildcard permissions in production
- Cross-account roles for pipeline deployment

### Encryption
- All DynamoDB tables encrypted with KMS
- S3 buckets encrypted at rest
- API Gateway requires HTTPS
- Secrets stored in AWS Secrets Manager

### Network Security
- Lambda functions in VPC for MySQL RDS access
- Security groups restrict traffic:
  - Lambda: outbound 3306 to RDS only
  - RDS: inbound 3306 from Lambda only
- VPC endpoints for AWS services
- No public internet access for sensitive functions
- NAT gateways for Lambda internet access (if needed)

## Deployment Pipeline

### Pipeline Stages

1. **Source Stage**
   - Triggered by GitHub commits
   - CodeStar connection for authentication

2. **Build Stage**
   - Run unit tests (Jest for backend, Vitest for frontend)
   - Run security scans (cfn-nag, checkov)
   - Build Lambda deployment packages
   - Build Vue.js frontend
   - Synthesize CDK templates

3. **Dev Deployment**
   - Deploy to dev account
   - Run integration tests
   - Run smoke tests

4. **Staging Deployment**
   - Deploy to staging account
   - Run end-to-end tests
   - Performance testing

5. **Production Approval**
   - Manual approval gate
   - Review deployment plan

6. **Production Deployment**
   - Deploy to production account
   - Health checks
   - Automated rollback on failure

### Rollback Strategy

- CloudFormation automatic rollback on stack failure
- Lambda function versions and aliases
- DynamoDB point-in-time recovery
- S3 versioning for frontend assets

## Hybrid Data Architecture

### Data Storage Strategy

The AI Test Automation Platform uses a hybrid data storage approach:

**DynamoDB for:**
- Test execution results and logs
- User sessions and authentication data
- Real-time analytics and metrics
- High-throughput, low-latency operations

**MySQL RDS for DDFE:**
- Element repository (page objects, locators)
- Test case definitions and relationships
- Complex queries and reporting
- Relational data with ACID compliance

### Database Schema (MySQL DDFE)

```sql
-- Element Repository Tables
CREATE TABLE applications (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  url VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pages (
  id INT PRIMARY KEY AUTO_INCREMENT,
  application_id INT,
  name VARCHAR(255) NOT NULL,
  url_pattern VARCHAR(500),
  FOREIGN KEY (application_id) REFERENCES applications(id)
);

CREATE TABLE elements (
  id INT PRIMARY KEY AUTO_INCREMENT,
  page_id INT,
  name VARCHAR(255) NOT NULL,
  locator_type ENUM('id', 'xpath', 'css', 'name', 'class'),
  locator_value TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (page_id) REFERENCES pages(id)
);

CREATE TABLE element_usage (
  id INT PRIMARY KEY AUTO_INCREMENT,
  element_id INT,
  test_case_id VARCHAR(255),
  usage_count INT DEFAULT 1,
  last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (element_id) REFERENCES elements(id)
);
```

### Data Synchronization

- Lambda functions handle data operations for both stores
- Connection pooling for MySQL connections
- Caching layer (ElastiCache) for frequently accessed data
- Event-driven updates between DynamoDB and MySQL

## Monitoring and Observability

### CloudWatch Metrics
- Lambda invocation count, duration, errors
- API Gateway request count, latency, 4xx/5xx errors
- DynamoDB read/write capacity, throttles
- RDS MySQL CPU, memory, connections, IOPS

### CloudWatch Alarms
- Lambda error rate > 1%
- API Gateway 5xx errors > 5%
- DynamoDB throttling events
- High Lambda duration (> 80% of timeout)
- RDS MySQL CPU > 80%
- RDS MySQL storage < 20% free
- RDS MySQL connection count > 80% of max

### Logging
- Structured JSON logs from Lambda functions
- API Gateway access logs
- CloudTrail for audit trail
- MySQL slow query logs
- Centralized log aggregation

### Tracing
- AWS X-Ray enabled for all Lambda functions
- Service map visualization
- Trace analysis for performance bottlenecks

## Cost Optimization

### Development
- Use smallest Lambda memory sizes
- DynamoDB on-demand billing
- Single-AZ MySQL RDS
- Short log retention (7 days)
- Minimal NAT gateway usage

### Production
- Right-sized Lambda memory based on profiling
- DynamoDB provisioned capacity with auto-scaling
- Multi-AZ MySQL RDS with read replicas
- Longer log retention (90 days)
- Reserved capacity for predictable workloads

## Tagging Strategy

All resources tagged with:
```typescript
Tags.of(stack).add('Project', 'AITestAutomation')
Tags.of(stack).add('Environment', environment)
Tags.of(stack).add('ManagedBy', 'CDK')
Tags.of(stack).add('CostCenter', 'Engineering')
Tags.of(stack).add('Owner', 'QA-Team')
```

## Testing Strategy

### Unit Tests
- Test CDK constructs with assertions
- Verify resource properties
- Check IAM policies

### Integration Tests
- Deploy to dev environment
- Test API endpoints
- Verify database operations

### Security Tests
- Run cfn-nag on CloudFormation templates
- Run checkov for security compliance
- Verify encryption settings
- Check IAM permissions

## References

- Follow [pipeline-design-framework/cdk-standards.md](../pipeline-design-framework/cdk-standards.md)
- Follow [pipeline-design-framework/security.md](../pipeline-design-framework/security.md)
- Follow [pipeline-design-framework/deployment.md](../pipeline-design-framework/deployment.md)
