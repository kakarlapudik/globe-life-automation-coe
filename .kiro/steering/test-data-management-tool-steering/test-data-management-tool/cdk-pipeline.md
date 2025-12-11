---
inclusion: manual
---

# Test Data Management Tool - CDK Pipeline Standards

This document defines the AWS CDK pipeline configuration for the Test Data Management Tool, following the pipeline-design-framework standards.

## Overview

The Test Data Management Tool uses AWS CDK to deploy a FastAPI backend and Vue.js frontend across multiple AWS accounts (dev, staging, production). The pipeline follows the standards defined in the pipeline-design-framework.

## Architecture

### Stack Organization

```
test-data-management-tool/
├── infrastructure/
│   ├── bin/
│   │   └── app.ts                    # CDK app entry point
│   ├── lib/
│   │   ├── pipeline-stack.ts         # CI/CD pipeline
│   │   ├── backend-stack.ts          # ECS Fargate for FastAPI
│   │   ├── database-stack.ts         # RDS PostgreSQL
│   │   ├── frontend-stack.ts         # S3, CloudFront for Vue.js
│   │   ├── network-stack.ts          # VPC, subnets, security groups
│   │   └── constructs/
│   │       ├── secure-database.ts    # RDS with encryption
│   │       └── fargate-service.ts    # ECS service with auto-scaling
│   ├── test/
│   │   └── stacks.test.ts
│   └── cdk.json
```

### Application Stacks

**1. Network Stack**
- VPC with public and private subnets
- NAT gateways for private subnet internet access
- VPC endpoints for AWS services
- Security groups for application tiers

**2. Database Stack**
- RDS MySQL with Multi-AZ
- KMS encryption for data at rest
- Automated backups
- Read replicas for production
- Secrets Manager for credentials

**3. Backend Stack**
- ECS Fargate for FastAPI application
- Application Load Balancer
- Auto-scaling based on CPU/memory
- CloudWatch Logs
- Task execution role with least privilege

**4. Frontend Stack**
- S3 bucket for Vue.js static assets
- CloudFront distribution with HTTPS
- WAF rules for DDoS protection
- Route53 DNS configuration
- OAI for S3 access

**5. Pipeline Stack**
- CodePipeline for CI/CD
- CodeBuild for Docker image builds
- ECR for container registry
- Cross-account deployment roles
- Manual approval for production

## Environment Configuration

### Dev Environment
```typescript
{
  account: process.env.DEV_ACCOUNT_ID,
  region: 'us-east-1',
  vpcCidr: '10.0.0.0/16',
  dbInstanceClass: 'db.t3.micro',
  dbAllocatedStorage: 20,
  ecsTaskCpu: 256,
  ecsTaskMemory: 512,
  ecsDesiredCount: 1,
  enableMultiAz: false,
  logRetention: 7
}
```

### Staging Environment
```typescript
{
  account: process.env.STAGING_ACCOUNT_ID,
  region: 'us-east-1',
  vpcCidr: '10.1.0.0/16',
  dbInstanceClass: 'db.t3.small',
  dbAllocatedStorage: 50,
  ecsTaskCpu: 512,
  ecsTaskMemory: 1024,
  ecsDesiredCount: 2,
  enableMultiAz: true,
  logRetention: 30
}
```

### Production Environment
```typescript
{
  account: process.env.PROD_ACCOUNT_ID,
  region: 'us-east-1',
  vpcCidr: '10.2.0.0/16',
  dbInstanceClass: 'db.r5.large',
  dbAllocatedStorage: 100,
  ecsTaskCpu: 1024,
  ecsTaskMemory: 2048,
  ecsDesiredCount: 3,
  ecsMaxCount: 10,
  enableMultiAz: true,
  enableReadReplica: true,
  logRetention: 90,
  enableBackup: true
}
```

## Security Standards

### IAM Permissions
- ECS task execution role with minimal permissions
- Task role for application-specific permissions
- Permissions boundaries applied to all roles
- Cross-account roles for pipeline deployment

### Encryption
- RDS encrypted with KMS customer-managed keys
- S3 buckets encrypted at rest
- ALB requires HTTPS with TLS 1.2+
- Database credentials in Secrets Manager
- Secrets rotation enabled

### Network Security
- ECS tasks in private subnets
- ALB in public subnets
- Security groups restrict traffic:
  - ALB: 443 from internet
  - ECS: 8000 from ALB only
  - RDS: 3306 from ECS only
- VPC Flow Logs enabled
- Network ACLs for additional protection

### Application Security
- FastAPI with JWT authentication
- CORS configured for frontend domain only
- Rate limiting on API endpoints
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy ORM (MySQL connector)

## Deployment Pipeline

### Pipeline Stages

1. **Source Stage**
   - Triggered by GitHub commits
   - CodeStar connection for authentication

2. **Build Stage**
   - Run backend tests (pytest)
   - Run frontend tests (Vitest)
   - Run security scans (cfn-nag, checkov, Snyk)
   - Build Docker image for FastAPI
   - Push to ECR
   - Build Vue.js frontend
   - Synthesize CDK templates

3. **Dev Deployment**
   - Deploy infrastructure to dev account
   - Deploy Docker image to ECS
   - Deploy frontend to S3/CloudFront
   - Run integration tests
   - Run API smoke tests

4. **Staging Deployment**
   - Deploy to staging account
   - Run end-to-end tests
   - Performance testing with load tests
   - Security scanning

5. **Production Approval**
   - Manual approval gate
   - Review deployment plan
   - Check test results

6. **Production Deployment**
   - Blue/green deployment for ECS
   - Deploy to production account
   - Health checks
   - Automated rollback on failure
   - Gradual traffic shift

### Rollback Strategy

- ECS blue/green deployment for zero-downtime rollback
- CloudFormation automatic rollback on stack failure
- RDS automated backups for data recovery
- S3 versioning for frontend assets
- Database migration rollback scripts

## Monitoring and Observability

### CloudWatch Metrics
- ECS CPU and memory utilization
- ALB request count, latency, target response time
- RDS MySQL CPU, memory, connections, IOPS
- CloudFront cache hit rate, error rate

### CloudWatch Alarms
- ECS task failure rate > 5%
- ALB 5xx errors > 1%
- RDS CPU > 80%
- RDS storage < 20% free
- High ALB latency (> 2 seconds)

### Logging
- ECS container logs to CloudWatch Logs
- ALB access logs to S3
- MySQL slow query logs
- CloudTrail for audit trail
- Structured JSON logs from FastAPI

### Dashboards
- Application health dashboard
- Infrastructure metrics dashboard
- Cost tracking dashboard

## Database Management

### Migrations
- Alembic for MySQL database migrations
- Migrations run in CodeBuild before deployment
- Rollback scripts for each migration
- Test migrations in dev/staging first
- MySQL-specific migration considerations

### Backups
- Automated daily backups
- 7-day retention in dev
- 30-day retention in production
- Point-in-time recovery enabled
- Cross-region backup replication for production

### Performance
- Connection pooling in FastAPI
- Read replicas for read-heavy workloads
- Query performance monitoring
- Index optimization

## Cost Optimization

### Development
- Single-AZ RDS
- Smallest instance sizes
- No NAT gateways (use VPC endpoints)
- Short log retention
- Minimal ECS task count

### Production
- Multi-AZ for high availability
- Right-sized instances based on metrics
- Reserved instances for predictable workloads
- Auto-scaling for ECS tasks
- S3 lifecycle policies
- CloudFront caching optimization

## Tagging Strategy

All resources tagged with:
```typescript
Tags.of(stack).add('Project', 'TestDataManagement')
Tags.of(stack).add('Environment', environment)
Tags.of(stack).add('ManagedBy', 'CDK')
Tags.of(stack).add('CostCenter', 'QA')
Tags.of(stack).add('Owner', 'QA-Team')
Tags.of(stack).add('Application', 'TestDataTool')
```

## Testing Strategy

### Unit Tests
- Test CDK constructs with assertions
- Verify resource properties
- Check security group rules
- Validate IAM policies

### Integration Tests
- Deploy to dev environment
- Test API endpoints
- Verify database connectivity
- Test authentication flow

### Load Tests
- Use Locust or k6 for load testing
- Test in staging environment
- Verify auto-scaling behavior
- Identify performance bottlenecks

### Security Tests
- Run cfn-nag on CloudFormation templates
- Run checkov for security compliance
- Snyk for container vulnerability scanning
- OWASP ZAP for API security testing
- Verify encryption settings

## Disaster Recovery

### RTO and RPO
- Dev: RTO 4 hours, RPO 24 hours
- Staging: RTO 2 hours, RPO 4 hours
- Production: RTO 1 hour, RPO 1 hour

### Recovery Procedures
- Database restore from automated backups
- Infrastructure recreation from CDK
- Application deployment from ECR
- DNS failover to backup region (production only)

## References

- Follow [pipeline-design-framework/cdk-standards.md](../pipeline-design-framework/cdk-standards.md)
- Follow [pipeline-design-framework/security.md](../pipeline-design-framework/security.md)
- Follow [pipeline-design-framework/deployment.md](../pipeline-design-framework/deployment.md)
- Follow [backend-standards.md](./backend-standards.md) for FastAPI implementation
- Follow [frontend-standards.md](./frontend-standards.md) for Vue.js implementation
