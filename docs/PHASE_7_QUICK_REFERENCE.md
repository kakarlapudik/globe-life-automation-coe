# Phase 7 Quick Reference Guide

## Overview

Quick reference for Phase 7 features, commands, and common tasks.

---

## Advanced Agents

### Code Review Agent

**Run Code Review**
```typescript
POST /api/v1/agents/code-review/execute
{
  "testFiles": ["tests/**/*.test.ts"],
  "includeMetrics": true
}
```

**Key Metrics**
- Cyclomatic Complexity: < 10 (good), 10-20 (moderate), > 20 (high)
- Cognitive Complexity: < 15 (good), 15-30 (moderate), > 30 (high)
- Maintainability Index: > 80 (good), 60-80 (moderate), < 60 (poor)

### Security Testing Agent

**Run Security Scan**
```typescript
POST /api/v1/agents/security/execute
{
  "sast": true,
  "dast": true,
  "dependencies": true,
  "targetUrl": "https://app.example.com"
}
```

**Severity Levels**
- Critical: Immediate action required
- High: Fix within 7 days
- Medium: Fix within 30 days
- Low: Fix when convenient

### Accessibility Testing Agent

**Run Accessibility Scan**
```typescript
POST /api/v1/agents/accessibility/execute
{
  "url": "https://app.example.com",
  "level": "AA",
  "includeColorContrast": true
}
```

**WCAG Levels**
- Level A: Minimum accessibility
- Level AA: Standard compliance (recommended)
- Level AAA: Enhanced accessibility

### Load Testing Agent

**Create Load Test**
```typescript
POST /api/v1/agents/load-testing/execute
{
  "virtualUsers": 1000,
  "duration": "10m",
  "pattern": "ramp-up",
  "targetUrl": "https://app.example.com"
}
```

**Load Patterns**
- `ramp-up`: Gradual increase
- `spike`: Sudden surge
- `sustained`: Constant load
- `geographic`: Distributed

---

## Integrations

### Slack Bot Commands

```
/test run <test-name>           # Run specific test
/test status <execution-id>     # Check test status
/test create <description>      # Create test from description
/test report <project>          # Get test report
/test list                      # List all tests
/test help                      # Show all commands
```

### GitHub Integration

**Webhook Events**
- `pull_request`: PR opened/updated
- `push`: Code pushed to branch
- `release`: Release created

**Configuration**
```json
{
  "events": ["pull_request", "push"],
  "testSelection": "ai-powered",
  "mergeBlocking": true
}
```

### ServiceNow Integration

**Incident Creation Rules**
```typescript
{
  "severity": "high",
  "failureCount": 3,
  "timeWindow": "1h",
  "assignmentGroup": "QA Team"
}
```

### APM Integration

**Supported Providers**
- Datadog
- New Relic
- AppDynamics (coming soon)

**Metrics to Correlate**
- Response time
- Error rate
- Throughput
- Resource utilization

---

## AI/ML Features

### Test Recommendation Engine

**Get Recommendations**
```typescript
POST /api/v1/ml/recommendations
{
  "commitHash": "abc123",
  "repository": "my-app",
  "confidenceThreshold": 0.7
}
```

**Risk Levels**
- High: > 0.8 probability
- Medium: 0.5 - 0.8 probability
- Low: < 0.5 probability

### Test Suite Optimization

**Run Optimization**
```typescript
POST /api/v1/ml/optimize-suite
{
  "projectId": "my-project",
  "includeRedundancy": true,
  "includeFlakiness": true
}
```

**Expected Improvements**
- Test reduction: 20-30%
- Execution time: 40-50% faster
- Flakiness: 80-90% reduction

### Predictive Test Selection

**Get Predictions**
```typescript
POST /api/v1/ml/predict
{
  "tests": ["test1", "test2"],
  "context": {
    "codeChanges": [...],
    "historicalData": [...]
  }
}
```

**Model Performance**
- Accuracy: > 85%
- Precision: > 80%
- Recall: > 90%

### Auto-Generated Documentation

**Generate Documentation**
```typescript
POST /api/v1/ml/generate-docs
{
  "testFiles": ["tests/**/*.test.ts"],
  "format": "markdown",
  "includeExamples": true
}
```

**Supported Formats**
- Markdown (.md)
- HTML (.html)
- PDF (.pdf)

---

## Developer Tools

### VS Code Extension

**Keyboard Shortcuts**
- `Ctrl+Shift+T`: Generate test
- `Ctrl+Shift+R`: Run test
- `Ctrl+Shift+C`: Show coverage
- `Ctrl+Shift+D`: Debug test

**Commands**
- `AI Test: Generate Test`
- `AI Test: Run Test`
- `AI Test: Show Coverage`
- `AI Test: Configure`

### CLI Tool

**Installation**
```bash
npm install -g @ai-test-platform/cli
```

**Common Commands**
```bash
ai-test init                    # Initialize project
ai-test run [pattern]           # Run tests
ai-test watch [pattern]         # Watch mode
ai-test run --parallel 4        # Parallel execution
ai-test config set <key> <val>  # Set configuration
ai-test config get <key>        # Get configuration
```

**Configuration File**
```yaml
# .ai-test.yml
endpoint: https://api.platform.com
token: your-api-token
parallel: 4
reporter: junit
timeout: 30000
```

### Browser Extension

**Recording Steps**
1. Click extension icon
2. Click "Start Recording"
3. Interact with application
4. Click "Stop Recording"
5. Click "Generate Code"
6. Select framework
7. Copy code to project

**Supported Frameworks**
- Playwright
- Selenium
- Cypress
- Puppeteer

### Real-Time Collaboration

**Start Session**
```typescript
POST /api/v1/collaboration/sessions
{
  "testFile": "tests/login.test.ts",
  "participants": ["user1@example.com"]
}
```

**Features**
- Live cursor tracking
- Real-time edits
- Inline comments
- Conflict resolution

---

## Enterprise Features

### Cost Allocation

**View Costs**
```typescript
GET /api/v1/cost/summary?period=month
```

**Set Budget**
```typescript
POST /api/v1/cost/budgets
{
  "projectId": "my-project",
  "monthly": 5000,
  "alertThreshold": 0.8
}
```

**Cost Breakdown**
- Test execution: 40%
- Agent usage: 30%
- Storage: 20%
- Compute: 10%

### Compliance Reporting

**Supported Standards**
- SOX (Sarbanes-Oxley)
- HIPAA (Health Insurance Portability)
- GDPR (General Data Protection Regulation)
- ISO 27001 (Information Security)

**Generate Report**
```typescript
POST /api/v1/compliance/reports
{
  "standard": "SOX",
  "startDate": "2024-01-01",
  "endDate": "2024-12-31",
  "includeEvidence": true
}
```

### Custom Agent Marketplace

**Install Agent**
```typescript
POST /api/v1/marketplace/install
{
  "agentId": "custom-agent-123",
  "version": "1.0.0"
}
```

**Publish Agent**
```bash
agent-sdk publish my-agent --version 1.0.0
```

### White-Label Configuration

**Set Branding**
```typescript
PUT /api/v1/white-label/branding
{
  "logo": "https://example.com/logo.png",
  "primaryColor": "#007bff",
  "companyName": "Your Company"
}
```

**Custom Domain**
```typescript
POST /api/v1/white-label/domains
{
  "domain": "testing.yourcompany.com",
  "sslCertificate": "arn:aws:acm:..."
}
```

---

## Common Tasks

### Run Complete Test Suite
```bash
ai-test run --parallel 8 --reporter html
```

### Generate Test from Code
1. Select code in VS Code
2. Right-click → "Generate Test"
3. Review generated test
4. Save to project

### Set Up PR Testing
1. Navigate to Integrations → GitHub
2. Click "Connect Repository"
3. Authorize access
4. Configure test selection
5. Enable merge blocking

### Create Load Test
1. Navigate to Load Testing → New Test
2. Set virtual users and duration
3. Select load pattern
4. Configure target URL
5. Start test

### Generate Compliance Report
1. Navigate to Compliance
2. Select standard (SOX, HIPAA, etc.)
3. Choose date range
4. Click "Generate Report"
5. Export to PDF

---

## Troubleshooting

### Agent Not Responding
```bash
# Check agent status
curl -X GET https://api.platform.com/v1/agents/{id}/status

# Restart agent
curl -X POST https://api.platform.com/v1/agents/{id}/restart
```

### Integration Failures
```bash
# Test integration
curl -X POST https://api.platform.com/v1/integrations/{id}/test

# View integration logs
curl -X GET https://api.platform.com/v1/integrations/{id}/logs
```

### ML Model Issues
```bash
# Check model status
curl -X GET https://api.platform.com/v1/ml/models/{id}/status

# View model metrics
curl -X GET https://api.platform.com/v1/ml/models/{id}/metrics
```

---

## Support

### Documentation
- User Guide: `/docs/PHASE_7_USER_GUIDE.md`
- Developer Guide: `/docs/PHASE_7_DEVELOPER_GUIDE.md`
- API Reference: `/docs/api-reference`

### Contact
- Email: support@ai-test-platform.com
- Chat: In-app support
- Forum: community.ai-test-platform.com
- Status: status.ai-test-platform.com

### Emergency Support
- Phone: 1-800-TEST-AI
- Emergency Email: emergency@ai-test-platform.com
- Response Time: < 1 hour for critical issues

---

*Last Updated: December 2024*
*Version: Phase 7.0*
