# CDK Infrastructure Implementation - Design

## Overview

This document outlines the technical design for implementing AWS CDK infrastructure for both the AI Test Automation Platform and Test Data Management Tool. The design follows enterprise-grade patterns with proper separation of concerns, security best practices, and multi-environment support.

## Architecture

### High-Level Structure

```
cdk-infrastructure/
├── bin/
│   └── app.ts                    # CDK app entry point
├── lib/
│   ├── shared/
│   │   ├── constructs/           # Reusable constructs
│   │   ├── config/              # Configuration management
│   │   └── utils/               # Utility functions
│   ├── ai-platform/
│   │   ├── network-stack.ts
│   │   ├── data-stack.ts
│   │   ├── backend-stack.ts
│   │   └── frontend-stack.ts
│   ├── data-tool/
│   │   ├── network-stack.ts
│   │   ├── database-stack.ts
│   │   ├── backend-stack.ts
│   │   └── frontend-stack.ts
│   └── pipeline/
│       ├── security-stack.ts
│       ├── monitoring-stack.ts
│       └── pipeline-stack.ts
├── config/
│   ├── dev.json
│   ├── staging.json
│   ├── production.json
│   └── common.json
├── test/
│   ├── unit/
│   └── integration/
├── cdk.json
├── package.json
└── tsconfig.json
```

## Stack Design

### AI Platform Stacks

#### 1. AiPlatformNetworkStack
- VPC with private subnets for RDS
- Security groups for Lambda and RDS
- VPC endpoints for AWS services

#### 2. AiPlatformDataStack
- DynamoDB tables for test results
- MySQL RDS for DDFE element repository
- KMS keys and Secrets Manager

#### 3. AiPlatformBackendStack
- Lambda functions for NLP and element detection
- API Gateway with JWT auth
- Lambda layers for dependencies

#### 4. AiPlatformFrontendStack
- S3 bucket for Vue.js app
- CloudFront distribution
- SSL certificate

### Data Tool Stacks

#### 1. DataToolNetworkStack
- VPC with public/private subnets
- NAT gateways and Internet Gateway
- Security groups for ALB, ECS, RDS

#### 2. DataToolDatabaseStack
- MySQL RDS with Multi-AZ
- KMS encryption
- Automated backups

#### 3. DataToolBackendStack
- ECS Fargate cluster
- Application Load Balancer
- Auto-scaling policies

#### 4. DataToolFrontendStack
- S3 bucket for Vue.js app
- CloudFront distribution
- SSL certificate

## Configuration Management

### Environment Configuration Interface

```typescript
interface EnvironmentConfig {
  account: string;
  region: string;
  environment: 'dev' | 'staging' | 'production';
  
  aiPlatform: {
    lambda: { memory: number; timeout: number };
    dynamodb: { billingMode: string };
    mysql: { instanceClass: string; allocatedStorage: number; multiAz: boolean };
  };
  
  dataTool: {
    ecs: { cpu: number; memory: number; desiredCount: number };
    mysql: { instanceClass: string; allocatedStorage: number; multiAz: boolean };
  };
  
  monitoring: {
    logRetentionDays: number;
    enableXRay: boolean;
  };
  
  security: {
    enableEncryption: boolean;
    permissionsBoundaryArn?: string;
  };
}
```

## Security Design

### IAM Roles
- Lambda execution roles with VPC access
- ECS task roles with Secrets Manager access
- Permissions boundaries applied to all roles

### Encryption
- KMS customer-managed keys for all data
- S3 bucket encryption at rest
- RDS encryption with KMS
- Secrets Manager for database credentials

### Network Security
- Security groups with least privilege
- Private subnets for databases
- VPC endpoints to avoid internet traffic

## Database Schema

### MySQL for DDFE (AI Platform)

```sql
CREATE DATABASE ddfe_repository;

CREATE TABLE applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    url VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pages (
    id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    url_pattern VARCHAR(500),
    FOREIGN KEY (application_id) REFERENCES applications(id)
);

CREATE TABLE elements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    page_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    locator_type ENUM('id', 'xpath', 'css', 'name'),
    locator_value TEXT NOT NULL,
    FOREIGN KEY (page_id) REFERENCES pages(id)
);
```

### MySQL for Test Data Tool

```sql
CREATE DATABASE test_data_management;

CREATE TABLE environments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    base_url VARCHAR(500)
);

CREATE TABLE test_datasets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    environment_id INT,
    data_type ENUM('user', 'product', 'order', 'custom'),
    FOREIGN KEY (environment_id) REFERENCES environments(id)
);

CREATE TABLE test_data_records (
    id INT PRIMARY KEY AUTO_INCREMENT,
    dataset_id INT NOT NULL,
    record_data JSON NOT NULL,
    is_reserved BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (dataset_id) REFERENCES test_datasets(id)
);
```

## Monitoring

### CloudWatch Dashboards
- Lambda invocations and errors
- DynamoDB read/write capacity
- RDS CPU and connections
- ECS task count and CPU

### CloudWatch Alarms
- Lambda error rate > 5 in 5 minutes
- RDS CPU > 80% for 15 minutes
- ECS task count < desired count
- API Gateway 5xx errors > 10 in 5 minutes

## Testing Strategy

### Unit Tests
- Validate stack resource properties
- Verify security group rules
- Check IAM policy permissions
- Confirm encryption settings

### Integration Tests
- Test cross-stack references
- Validate VPC connectivity
- Verify database accessibility

## Deployment Strategy

### Stack Dependencies
1. Network stacks (VPC, subnets, security groups)
2. Data stacks (databases, DynamoDB)
3. Backend stacks (Lambda, ECS)
4. Frontend stacks (S3, CloudFront)
5. Pipeline stack (CI/CD)

### Environment Promotion
- Dev: Minimal resources, single-AZ
- Staging: Moderate resources, Multi-AZ
- Production: Full resources, Multi-AZ, read replicas

## Cost Optimization

### Resource Sizing
- Dev: t3.micro RDS, 512MB Lambda
- Staging: t3.small RDS, 1024MB Lambda
- Production: r5.large RDS, 2048MB Lambda

### Auto-scaling
- ECS scales based on CPU (70% target)
- DynamoDB on-demand for dev, provisioned for prod
- Lambda concurrent execution limits

This design provides a comprehensive, scalable, and maintainable CDK infrastructure following AWS best practices.
