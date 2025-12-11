# Multi-Tenancy Guide

## Overview

The AI Test Automation Platform provides comprehensive multi-tenancy support, enabling multiple organizations to use the platform with complete data isolation, tenant-specific configurations, and white-labeling capabilities.

## Key Features

### 1. Complete Tenant Isolation
- **Data Layer**: Separate DynamoDB partition keys and S3 prefixes per tenant
- **Execution**: Isolated test execution environments
- **Security**: IAM policies enforce tenant-specific access

### 2. Tenant-Specific Configurations
- Execution settings (parallelism, timeouts, browsers)
- Data retention policies
- Security settings (SSO, MFA, IP whitelisting)
- Feature flags and beta features
- Integration settings (webhooks, Slack, JIRA)

### 3. White-Labeling (Enterprise)
- Custom branding (logo, colors, favicon)
- Custom domains
- Custom CSS
- Branded emails and support contacts

### 4. Usage Tracking & Limits
- Real-time usage monitoring
- Automatic limit enforcement
- Plan-based feature access
- Usage alerts and notifications

## Getting Started

### 1. Deploy Infrastructure

```bash
cd cdk-infrastructure
cdk deploy MultiTenancyStack --context environment=production
```

This creates:
- DynamoDB tables for tenants and usage tracking
- S3 buckets for tenant data and artifacts
- IAM policies for tenant isolation
- CloudWatch alarms for monitoring

### 2. Initialize Multi-Tenancy Service

```typescript
import { MultiTenancyService } from './services/multi-tenancy-service';

const multiTenancyService = new MultiTenancyService({
  region: 'us-east-1',
  tenantsTable: process.env.TENANTS_TABLE_NAME!,
  usageTable: process.env.USAGE_TABLE_NAME!,
});
```

### 3. Apply Tenant Isolation Middleware

```typescript
import express from 'express';
import { TenantIsolationMiddleware } from './middleware/tenant-isolation';

const app = express();
const tenantIsolation = new TenantIsolationMiddleware(multiTenancyService);

// Apply to all routes
app.use(tenantIsolation.isolate());
app.use(tenantIsolation.trackUsage('apiCalls', 1));
```

## Tenant Management

### Creating a Tenant

```typescript
const tenant = await multiTenancyService.createTenant({
  name: 'Acme Corporation',
  domain: 'acme.com',
  plan: TenantPlan.PROFESSIONAL,
  adminEmail: 'admin@acme.com',
  configuration: {
    maxParallelExecutions: 30,
    enforceSSO: true,
    allowedDomains: ['acme.com'],
  },
  whiteLabel: {
    enabled: true,
    companyName: 'Acme Testing',
    logoUrl: 'https://acme.com/logo.png',
    primaryColor: '#FF6B35',
  },
});
```

### Updating Configuration

```typescript
await multiTenancyService.updateTenantConfiguration(tenantId, {
  maxParallelExecutions: 50,
  enabledFeatures: ['api-testing', 'visual-testing', 'advanced-analytics'],
});
```

### Updating White-Label Settings

```typescript
await multiTenancyService.updateWhiteLabel(tenantId, {
  customDomain: 'testing.acme.com',
  supportEmail: 'support@acme.com',
  customCss: '.primary-button { background-color: #FF6B35; }',
});
```

### Upgrading Plan

```typescript
await multiTenancyService.upgradeTenantPlan(tenantId, TenantPlan.ENTERPRISE);
```

## Usage Tracking

### Track Usage

```typescript
// Track test executions
await multiTenancyService.trackUsage({
  tenantId,
  metric: 'executions',
  increment: 1,
});

// Track API calls
await multiTenancyService.trackUsage({
  tenantId,
  metric: 'apiCalls',
  increment: 1,
});

// Track storage
await multiTenancyService.trackUsage({
  tenantId,
  metric: 'storageGB',
  increment: 0.5,
});
```

### Get Usage

```typescript
const usage = await multiTenancyService.getTenantUsage(tenantId);
console.log({
  executions: usage.executions,
  apiCalls: usage.apiCalls,
  storageGB: usage.storageGB,
  bedrockTokens: usage.bedrockTokens,
  bedrockCost: usage.bedrockCost,
});
```

### Check Limits

```typescript
const limitsCheck = await multiTenancyService.checkLimits(tenantId);
if (!limitsCheck.withinLimits) {
  console.error('Exceeded limits:', limitsCheck.exceededLimits);
}
```

## Middleware Usage

### Basic Isolation

```typescript
// Apply tenant isolation
app.use(tenantIsolation.isolate());

// Access tenant context in routes
app.get('/api/tests', (req, res) => {
  const { tenantId, userId } = req.tenantContext;
  // Query tests for this tenant only
});
```

### Limit Checking

```typescript
// Check limits before expensive operations
app.post('/api/tests/execute',
  tenantIsolation.checkLimits('executions'),
  async (req, res) => {
    // Execute test
  }
);
```

### Usage Tracking

```typescript
// Track API calls
app.use('/api', tenantIsolation.trackUsage('apiCalls', 1));

// Track executions
app.post('/api/tests/execute',
  tenantIsolation.trackUsage('executions', 1),
  async (req, res) => {
    // Execute test
  }
);
```

### Feature Gating

```typescript
// Require specific features
app.get('/api/analytics/advanced',
  tenantIsolation.requireFeature('advanced-analytics'),
  async (req, res) => {
    // Return advanced analytics
  }
);
```

### Resource Validation

```typescript
// Validate resource belongs to tenant
app.get('/api/tests/:id',
  tenantIsolation.validateResourceAccess('test'),
  async (req, res) => {
    // Return test details
  }
);
```

## Data Isolation

### DynamoDB Partition Keys

All DynamoDB items use tenant-specific partition keys:

```typescript
const partitionKey = multiTenancyService.getTenantPartitionKey(
  tenantId,
  'test',
  testId
);
// Result: 'tenant-123#test#test-456'

// Use in DynamoDB operations
await dynamodb.putItem({
  TableName: 'tests',
  Item: {
    pk: partitionKey,
    // ... other attributes
  },
});
```

### S3 Prefixes

All S3 objects use tenant-specific prefixes:

```typescript
const prefix = multiTenancyService.getTenantS3Prefix(
  tenantId,
  'artifacts'
);
// Result: 'tenants/tenant-123/artifacts/'

// Use in S3 operations
await s3.putObject({
  Bucket: 'tenant-artifacts',
  Key: `${prefix}screenshot-${Date.now()}.png`,
  Body: screenshotBuffer,
});
```

## Plans and Limits

### Plan Comparison

| Feature | Free | Starter | Professional | Enterprise |
|---------|------|---------|--------------|------------|
| Users | 3 | 10 | 50 | Unlimited |
| Projects | 2 | 10 | 50 | Unlimited |
| Tests/Project | 50 | 200 | 1,000 | Unlimited |
| Executions/Month | 500 | 5,000 | 50,000 | Unlimited |
| Storage | 5 GB | 50 GB | 500 GB | Unlimited |
| API Calls/Day | 1,000 | 10,000 | 100,000 | Unlimited |
| Concurrent Executions | 2 | 5 | 20 | 50 |

### Feature Matrix

| Feature | Free | Starter | Professional | Enterprise |
|---------|------|---------|--------------|------------|
| Test Creation | ✅ | ✅ | ✅ | ✅ |
| Test Execution | ✅ | ✅ | ✅ | ✅ |
| Basic Reporting | ✅ | ✅ | ✅ | ✅ |
| Browser Testing | ✅ | ✅ | ✅ | ✅ |
| API Testing | ❌ | ✅ | ✅ | ✅ |
| Visual Testing | ❌ | ✅ | ✅ | ✅ |
| CI/CD Integration | ❌ | ✅ | ✅ | ✅ |
| Advanced Analytics | ❌ | ❌ | ✅ | ✅ |
| Custom Reporting | ❌ | ❌ | ✅ | ✅ |
| Parallel Execution | ❌ | ❌ | ✅ | ✅ |
| Test Healing | ❌ | ❌ | ✅ | ✅ |
| White-Labeling | ❌ | ❌ | ❌ | ✅ |
| SSO | ❌ | ❌ | ❌ | ✅ |
| Advanced Security | ❌ | ❌ | ❌ | ✅ |
| Dedicated Support | ❌ | ❌ | ❌ | ✅ |
| Custom Integrations | ❌ | ❌ | ❌ | ✅ |
| Audit Logging | ❌ | ❌ | ❌ | ✅ |

## Tenant Identification

The platform supports multiple methods for identifying tenants:

### 1. X-Tenant-ID Header

```bash
curl -H "X-Tenant-ID: tenant-123" https://api.platform.com/tests
```

### 2. Custom Domain

```bash
curl https://acme.platform.com/tests
# Automatically identifies tenant by domain
```

### 3. Subdomain

```bash
curl https://tenant-123.platform.com/tests
# Automatically identifies tenant by subdomain
```

### 4. JWT Token

```typescript
// JWT payload includes tenantId
{
  "sub": "user-456",
  "tenantId": "tenant-123",
  "email": "user@acme.com"
}
```

## Security Best Practices

### 1. Always Validate Tenant Context

```typescript
app.use((req, res, next) => {
  if (!req.tenantContext) {
    return res.status(401).json({ error: 'Tenant context required' });
  }
  next();
});
```

### 2. Use Tenant-Specific Keys

```typescript
// Always include tenant ID in database keys
const key = `${tenantId}#${resourceType}#${resourceId}`;
```

### 3. Validate Resource Ownership

```typescript
// Before returning resources, verify they belong to the tenant
if (resource.tenantId !== req.tenantContext.tenantId) {
  return res.status(403).json({ error: 'Access denied' });
}
```

### 4. Enforce Limits

```typescript
// Check limits before expensive operations
const limitsCheck = await multiTenancyService.checkLimits(tenantId);
if (!limitsCheck.withinLimits) {
  return res.status(429).json({ 
    error: 'Limit exceeded',
    exceededLimits: limitsCheck.exceededLimits 
  });
}
```

## Monitoring and Alerts

### CloudWatch Metrics

- DynamoDB read/write capacity
- S3 bucket size
- API call rates per tenant
- Execution counts per tenant

### Usage Alerts

Configure alerts for:
- Approaching plan limits
- Unusual usage patterns
- High costs
- Failed operations

### Audit Logging

All tenant operations are logged:
- Tenant creation/updates
- Configuration changes
- Plan upgrades
- Usage tracking
- Limit violations

## Troubleshooting

### Tenant Not Found

```typescript
// Check if tenant exists
const tenant = await multiTenancyService.getTenant(tenantId);
if (!tenant) {
  console.error('Tenant not found:', tenantId);
}
```

### Limits Exceeded

```typescript
// Check which limits are exceeded
const limitsCheck = await multiTenancyService.checkLimits(tenantId);
console.log('Exceeded limits:', limitsCheck.exceededLimits);

// Upgrade plan or increase limits
await multiTenancyService.upgradeTenantPlan(tenantId, TenantPlan.ENTERPRISE);
```

### Cross-Tenant Access

```typescript
// Verify partition keys include tenant ID
const key = multiTenancyService.getTenantPartitionKey(tenantId, type, id);
console.log('Partition key:', key);

// Verify IAM policies enforce tenant isolation
// Check CloudTrail logs for unauthorized access attempts
```

## Migration Guide

### Migrating Existing Data

1. **Add Tenant ID to Existing Records:**
   ```typescript
   // Update all records to include tenant ID
   for (const record of existingRecords) {
     const newKey = `${tenantId}#${record.type}#${record.id}`;
     await dynamodb.updateItem({
       TableName: 'tests',
       Key: { pk: record.pk },
       UpdateExpression: 'SET pk = :newKey, tenantId = :tenantId',
       ExpressionAttributeValues: {
         ':newKey': newKey,
         ':tenantId': tenantId,
       },
     });
   }
   ```

2. **Migrate S3 Objects:**
   ```typescript
   // Move objects to tenant-specific prefixes
   const prefix = multiTenancyService.getTenantS3Prefix(tenantId, 'artifacts');
   await s3.copyObject({
     Bucket: 'artifacts',
     CopySource: `artifacts/${oldKey}`,
     Key: `${prefix}${newKey}`,
   });
   ```

3. **Update Application Code:**
   - Add tenant isolation middleware
   - Update database queries to use tenant partition keys
   - Update S3 operations to use tenant prefixes

## API Reference

See [Multi-Tenancy Service API](../src/services/multi-tenancy-service.ts) for complete API documentation.

## Examples

See [Multi-Tenancy Examples](../examples/multi-tenancy-example.ts) for complete working examples.

## Support

For questions or issues:
- Check the [Troubleshooting](#troubleshooting) section
- Review [Security Best Practices](#security-best-practices)
- Contact support at support@platform.com
