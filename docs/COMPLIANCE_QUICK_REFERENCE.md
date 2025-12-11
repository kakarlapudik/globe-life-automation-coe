# Compliance & Audit Logging - Quick Reference

## Overview

The AI Test Automation Platform includes comprehensive audit logging and compliance reporting capabilities supporting SOC 2, GDPR, and HIPAA frameworks.

## Quick Start

### Generate a Compliance Report

```typescript
import { ComprehensiveComplianceReporting, ComplianceFramework } from './services/compliance-reporting-service';

const service = new ComprehensiveComplianceReporting(
  auditService,
  securityMonitoring,
  dataRetention,
  reportRepository,
  controlRepository,
  findingRepository
);

// Generate SOC 2 report for the year
const report = await service.generateReport(
  ComplianceFramework.SOC2,
  new Date('2024-01-01'),
  new Date('2024-12-31'),
  'admin@example.com'
);

console.log(`Compliance Score: ${report.overallScore}%`);
console.log(`Status: ${report.status}`);
```

### Export Report

```typescript
// Export as HTML
const htmlBuffer = await service.exportReport(report.id, 'html');
fs.writeFileSync('compliance-report.html', htmlBuffer);

// Export as JSON
const jsonBuffer = await service.exportReport(report.id, 'json');
fs.writeFileSync('compliance-report.json', jsonBuffer);
```

### Create a Finding

```typescript
import { FindingSeverity, FindingStatus } from './services/compliance-reporting-service';

const findingId = await service.createFinding({
  severity: FindingSeverity.HIGH,
  controlId: 'SOC2-CC6.1',
  title: 'Weak Password Policy',
  description: 'Password policy does not meet minimum requirements',
  impact: 'Increased risk of unauthorized access',
  remediation: 'Update password policy to require 12+ characters',
  status: FindingStatus.OPEN
});
```

### Resolve a Finding

```typescript
await service.resolveFinding(findingId, 'Password policy updated');
```

## Supported Frameworks

### SOC 2 (10 Controls)
- Logical and Physical Access Controls
- Authentication and Authorization
- User Access Removal
- Network Security
- Data Transmission Security
- System Monitoring
- Security Event Response
- Incident Response Process
- Audit Logging
- Audit Log Retention

### GDPR (9 Controls)
- Principles of Data Processing
- Lawfulness of Processing
- Right of Access
- Right to Erasure
- Data Protection by Design
- Records of Processing Activities
- Security of Processing
- Notification of Personal Data Breach
- Data Protection Impact Assessment

### HIPAA (11 Controls)
- Security Management Process
- Workforce Security
- Information Access Management
- Security Awareness and Training
- Security Incident Procedures
- Access Control
- Audit Controls
- Integrity Controls
- Person or Entity Authentication
- Transmission Security
- Data Retention

## Compliance Status

| Status | Criteria |
|--------|----------|
| **Compliant** | Score ≥ 95%, No high/critical findings |
| **Partially Compliant** | Score ≥ 70%, May have medium/low findings |
| **Non-Compliant** | Any critical findings OR Score < 70% |

## Data Retention Policies

| Data Type | Retention Period | Archive |
|-----------|-----------------|---------|
| Audit Logs | 365 days | Yes (Glacier) |
| Test Results | 90 days | No |
| Test Artifacts | 30 days | No |
| User Sessions | 7 days | No |
| Security Alerts | 730 days | Yes (Glacier) |
| Temporary Files | 1 day | No |
| Cached Data | 3 days | No |

## AWS Resources

### DynamoDB Tables
- `{env}-audit-logs` - Audit event storage
- `{env}-security-alerts` - Security alert storage
- `{env}-compliance-reports` - Compliance report storage
- `{env}-compliance-controls` - Control definitions
- `{env}-compliance-findings` - Finding tracking
- `{env}-data-retention-policies` - Retention policy configuration

### S3 Buckets
- `{env}-audit-logs-archive` - Archived audit logs
- `{env}-compliance-reports` - Generated compliance reports

### Lambda Functions
- `{env}-compliance-report-generator` - Monthly report generation
- `{env}-data-retention-cleanup` - Daily data cleanup

### Scheduled Jobs
- **Monthly Reports**: 1st of month at 2 AM UTC
- **Daily Cleanup**: Every day at 2 AM UTC

## CloudWatch Alarms

| Alarm | Threshold | Action |
|-------|-----------|--------|
| High Failed Logins | >10 in 5 minutes | SNS Alert |
| Critical Security Alerts | ≥1 per minute | SNS Alert |

## API Endpoints (Future)

```typescript
// Generate report
POST /api/compliance/reports
{
  "framework": "SOC2",
  "startDate": "2024-01-01",
  "endDate": "2024-12-31"
}

// Get report
GET /api/compliance/reports/{reportId}

// List reports
GET /api/compliance/reports?framework=SOC2

// Export report
GET /api/compliance/reports/{reportId}/export?format=html

// Create finding
POST /api/compliance/findings
{
  "severity": "HIGH",
  "controlId": "SOC2-CC6.1",
  "title": "Weak Password Policy",
  ...
}

// Resolve finding
PUT /api/compliance/findings/{findingId}/resolve
{
  "resolution": "Password policy updated"
}
```

## Environment Variables

```bash
# DynamoDB Tables
AUDIT_LOGS_TABLE=production-audit-logs
SECURITY_ALERTS_TABLE=production-security-alerts
COMPLIANCE_REPORTS_TABLE=production-compliance-reports
COMPLIANCE_CONTROLS_TABLE=production-compliance-controls
COMPLIANCE_FINDINGS_TABLE=production-compliance-findings
DATA_RETENTION_POLICIES_TABLE=production-data-retention-policies

# S3 Buckets
AUDIT_LOGS_BUCKET=production-audit-logs-archive
COMPLIANCE_REPORTS_BUCKET=production-compliance-reports

# SNS Topics
SECURITY_ALERT_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:production-security-alerts
```

## Deployment

```bash
# Deploy audit compliance stack
cd cdk-infrastructure
cdk deploy AuditComplianceStack \
  --context environment=production \
  --context auditLogRetentionDays=2555 \
  --context alertEmail=security@example.com
```

## Monitoring

### View Audit Logs
```bash
aws dynamodb scan \
  --table-name production-audit-logs \
  --limit 10
```

### View Security Alerts
```bash
aws dynamodb scan \
  --table-name production-security-alerts \
  --filter-expression "severity = :severity" \
  --expression-attribute-values '{":severity":{"S":"CRITICAL"}}'
```

### Trigger Manual Report Generation
```bash
aws lambda invoke \
  --function-name production-compliance-report-generator \
  --payload '{"reportType":"adhoc","frameworks":["SOC2"]}' \
  response.json
```

### Trigger Manual Cleanup
```bash
aws lambda invoke \
  --function-name production-data-retention-cleanup \
  response.json
```

## Troubleshooting

### Report Generation Fails
1. Check Lambda logs: `aws logs tail /aws/lambda/production-compliance-report-generator`
2. Verify DynamoDB table access
3. Check IAM permissions

### Data Retention Not Working
1. Check Lambda logs: `aws logs tail /aws/lambda/production-data-retention-cleanup`
2. Verify EventBridge rule is enabled
3. Check retention policy configuration

### Missing Audit Logs
1. Verify audit service is logging events
2. Check DynamoDB table for recent entries
3. Verify TTL is not expiring logs too early

## Best Practices

1. **Regular Reviews**: Review compliance reports monthly
2. **Finding Resolution**: Resolve findings within 30 days
3. **Control Testing**: Test controls quarterly
4. **Evidence Collection**: Ensure automated evidence collection is working
5. **Retention Policies**: Review and update retention policies annually
6. **Security Alerts**: Monitor and respond to security alerts within 24 hours
7. **Backup**: Regularly backup compliance reports and audit logs
8. **Access Control**: Limit access to compliance data to authorized personnel only

## Support

For issues or questions:
- Check logs in CloudWatch
- Review the comprehensive summary: `TASK_6.4_AUDIT_COMPLIANCE_SUMMARY.md`
- Contact the security team for compliance-related questions
