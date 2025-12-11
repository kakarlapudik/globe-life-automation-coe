# Remediation Agent - Quick Reference

## Overview
The Remediation Agent provides automated fix generation, self-healing test scripts, and comprehensive validation for test failures and configuration issues.

## Quick Start

### 1. Generate Automated Fix
```typescript
import { AutoRemediationEngine } from './services/auto-remediation-engine';
import { BedrockService } from './services/bedrock-service';

const bedrockService = new BedrockService();
const engine = new AutoRemediationEngine(bedrockService);

const request = {
  issueType: 'selector-broken',
  context: {
    testId: 'test-123',
    testName: 'Login Test',
    failureMessage: 'Element not found: #login-btn',
    testCode: 'await page.click("#login-btn");',
    timestamp: new Date()
  },
  priority: 'high'
};

const result = await engine.generateFix(request);
console.log(`Fix type: ${result.fixType}`);
console.log(`Confidence: ${result.confidence}`);
console.log(`Changes: ${result.fix.changes.length}`);
```

### 2. Self-Heal Test Script
```typescript
import { SelfHealingFramework } from './services/self-healing-framework';

const framework = new SelfHealingFramework(bedrockService);

const testScript = {
  id: 'test-1',
  name: 'Login Test',
  code: 'await page.click("#login-btn");',
  selectors: [{
    id: 'sel-1',
    name: 'login-button',
    value: '#login-btn',
    type: 'css',
    lineNumber: 1,
    usageCount: 10,
    failureCount: 3
  }],
  waitTimes: [],
  retryLogic: []
};

const failureContext = {
  testId: 'test-1',
  failureType: 'selector-not-found',
  failedSelector: '#login-btn',
  errorMessage: 'Element not found',
  timestamp: new Date()
};

const healingResult = await framework.healTestScript(testScript, failureContext);
console.log(`Healed: ${healingResult.success}`);
console.log(`Changes: ${healingResult.changes.length}`);
console.log(`New code: ${healingResult.testAfter}`);
```

### 3. Validate and Apply Fix
```typescript
import { RemediationValidationService } from './services/remediation-validation-service';

const validationService = new RemediationValidationService();

const validationRequest = {
  remediationId: 'rem-1',
  fix: result.fix,
  testId: 'test-1',
  originalCode: 'await page.click("#old");',
  fixedCode: 'await page.click("[data-testid=\\"new\\"]");',
  environment: 'test'
};

const validation = await validationService.validateFix(validationRequest);

if (validation.recommendation === 'apply') {
  await engine.applyFix(result.fix, request);
  validationService.trackRemediation('rem-1', 'applied');
} else if (validation.recommendation === 'review') {
  console.log('Manual review required:', validation.reasoning);
} else {
  console.log('Fix rejected:', validation.issues);
}
```

## Fix Types

### Code Patch
Fixes logic errors and code issues:
```typescript
{
  issueType: 'test-failure',
  context: {
    failureMessage: 'Assertion failed',
    testCode: '...',
    stackTrace: '...'
  }
}
```

### Configuration Update
Fixes environment and configuration issues:
```typescript
{
  issueType: 'configuration-error',
  context: {
    failureMessage: 'Invalid timeout',
    configuration: { timeout: 1000 }
  }
}
```

### Selector Update
Fixes broken element locators:
```typescript
{
  issueType: 'selector-broken',
  context: {
    failedSelector: '#old-selector',
    failureMessage: 'Element not found'
  }
}
```

### Retry Logic
Fixes timing and synchronization issues:
```typescript
{
  issueType: 'timeout',
  context: {
    failureMessage: 'Timeout waiting for element'
  }
}
```

## Healing Strategies

### 1. Selector Healing
Generates alternative selectors:
- Data attributes: `[data-testid="button"]`
- Multiple strategies: CSS, XPath, text content
- Fallback options: 3 alternatives per failure

### 2. Wait Time Adjustment
Optimizes timeouts based on history:
- Calculates average failure time
- Adds 50% buffer
- Bounds: 5-60 seconds

### 3. Retry Logic Optimization
Improves retry strategies:
- Minimum 3 attempts
- Exponential backoff
- Proper error handling

### 4. Code Structure Fixes
Bedrock-powered improvements:
- Error handling
- Synchronization
- Best practices

## Validation Levels

### 1. Syntax Validation
- Balanced braces
- Basic syntax correctness
- Score: 0.0 or 1.0

### 2. Logic Validation
- Test intent preservation
- No new issues introduced
- Score: 0.5 or 1.0

### 3. Performance Validation
- No sleep() calls
- No infinite loops
- Limited iterations
- Score: 0.7 or 1.0

### 4. Security Validation
- No eval() usage
- No innerHTML assignments
- No XSS vulnerabilities
- Score: 0.0 or 1.0

## Recommendations

### Apply (Score ≥ 0.8, No High Issues)
```typescript
if (validation.recommendation === 'apply') {
  // Safe to apply automatically
  await engine.applyFix(fix, request);
}
```

### Review (Score 0.5-0.8 or High Issues)
```typescript
if (validation.recommendation === 'review') {
  // Manual review recommended
  console.log('Issues:', validation.issues);
  // Wait for human approval
}
```

### Reject (Score < 0.5 or Critical Issues)
```typescript
if (validation.recommendation === 'reject') {
  // Do not apply
  console.log('Fix rejected:', validation.reasoning);
}
```

## Rollback

### Create Rollback Plan
```typescript
const plan = validationService.createRollbackPlan('rem-1', fix);
console.log(`Steps: ${plan.steps.length}`);
console.log(`Risk: ${plan.riskLevel}`);
console.log(`Time: ${plan.estimatedTime}s`);
```

### Execute Rollback
```typescript
const success = await validationService.executeRollback(plan);
if (success) {
  console.log('Rollback completed');
}
```

## Impact Analysis

```typescript
const impact = await validationService.analyzeImpact('rem-1', fix, 'test-1');

console.log('Affected tests:', impact.affectedTests.length);
console.log('Affected components:', impact.affectedComponents);
console.log('Overall risk:', impact.riskAssessment.overallRisk);
console.log('Estimated downtime:', impact.estimatedDowntime, 'seconds');
console.log('Rollback complexity:', impact.rollbackComplexity);
```

## Success Tracking

### Track Status
```typescript
validationService.trackRemediation('rem-1', 'pending');
validationService.trackRemediation('rem-1', 'validating');
validationService.trackRemediation('rem-1', 'applied');
```

### Update Metrics
```typescript
validationService.updateSuccessMetrics('rem-1', {
  testPassRate: 0.95,
  executionTime: 1200,
  failureReduction: 0.8,
  stabilityScore: 0.9
});
```

### Get History
```typescript
const tracking = validationService.getRemediationTracking('rem-1');
console.log('Status:', tracking.status);
console.log('Applied at:', tracking.appliedAt);
console.log('Pass rate:', tracking.successMetrics.testPassRate);

const allHistory = validationService.getAllRemediationHistory();
console.log('Total remediations:', allHistory.length);
```

## Confidence Scoring

### Factors that Increase Confidence
- Single change (+0.1)
- High diagnostic confidence (+0.15)
- Selector/retry fixes (+0.05)
- Simple fix type (+0.1)

### Factors that Decrease Confidence
- Multiple changes
- No diagnostic data
- Complex fix type
- High risk level

### Confidence Ranges
- **0.9-0.95**: Very high confidence, safe to auto-apply
- **0.8-0.9**: High confidence, recommend apply
- **0.7-0.8**: Medium confidence, recommend review
- **<0.7**: Low confidence, manual review required

## Best Practices

### 1. Always Validate Before Applying
```typescript
const validation = await validationService.validateFix(request);
if (validation.recommendation !== 'apply') {
  // Don't auto-apply
}
```

### 2. Create Rollback Plans
```typescript
const plan = validationService.createRollbackPlan(remediationId, fix);
// Store plan before applying fix
```

### 3. Track All Remediations
```typescript
validationService.trackRemediation(remediationId, 'applied');
// Monitor success metrics
```

### 4. Analyze Impact First
```typescript
const impact = await validationService.analyzeImpact(remediationId, fix, testId);
if (impact.riskAssessment.overallRisk === 'high') {
  // Require manual approval
}
```

### 5. Monitor Success Metrics
```typescript
// After test execution
validationService.updateSuccessMetrics(remediationId, {
  testPassRate: newPassRate,
  failureReduction: reductionPercentage
});
```

## Common Patterns

### Pattern 1: Automatic Remediation
```typescript
// Generate fix
const fix = await engine.generateFix(request);

// Validate
const validation = await validationService.validateFix({
  remediationId: 'rem-1',
  fix: fix.fix,
  testId: request.context.testId,
  originalCode: originalCode,
  fixedCode: fixedCode,
  environment: 'test'
});

// Apply if safe
if (validation.recommendation === 'apply' && fix.confidence > 0.8) {
  await engine.applyFix(fix.fix, request);
  validationService.trackRemediation('rem-1', 'applied');
}
```

### Pattern 2: Self-Healing with Validation
```typescript
// Heal test
const healing = await framework.healTestScript(testScript, failureContext);

// Validate healing
const validation = await validationService.validateFix({
  remediationId: 'heal-1',
  fix: healing,
  testId: testScript.id,
  originalCode: healing.testBefore,
  fixedCode: healing.testAfter,
  environment: 'test'
});

// Apply if valid
if (validation.isValid && healing.confidence > 0.8) {
  // Update test script
  testScript.code = healing.testAfter;
}
```

### Pattern 3: Rollback on Failure
```typescript
// Apply fix
const applied = await engine.applyFix(fix, request);
validationService.trackRemediation('rem-1', 'applied');

// Run tests
const testResult = await runTests();

// Rollback if tests fail
if (!testResult.passed) {
  const plan = validationService.createRollbackPlan('rem-1', fix);
  await validationService.executeRollback(plan);
  validationService.trackRemediation('rem-1', 'rolled-back');
}
```

## Troubleshooting

### Issue: Low Confidence Scores
**Solution**: Provide diagnostic results with root cause analysis
```typescript
const request = {
  ...baseRequest,
  diagnosticResult: {
    rootCause: 'Selector changed in UI',
    confidence: 0.9,
    affectedComponents: ['login-form'],
    suggestedFixes: ['Update selector']
  }
};
```

### Issue: Validation Failures
**Solution**: Check validation issues and fix code
```typescript
if (!validation.isValid) {
  validation.issues.forEach(issue => {
    console.log(`${issue.severity}: ${issue.message}`);
  });
}
```

### Issue: Rollback Failures
**Solution**: Ensure rollback plan is created before applying
```typescript
const plan = validationService.createRollbackPlan(remediationId, fix);
// Store plan in database
await applyFix();
// If needed, retrieve plan and rollback
```

## AWS Bedrock Models Used

- **Claude 3 Sonnet**: Primary model for fix generation and analysis
- **Claude 3 Haiku**: Fast responses for simple fixes
- **Temperature**: 0.1 for deterministic fixes
- **Max Tokens**: 1000-2000 depending on complexity

## Performance

- **Fix Generation**: <5 seconds
- **Validation**: <2 seconds
- **Healing**: <3 seconds
- **Impact Analysis**: <1 second
- **Rollback**: 30 seconds per step

## Limits

- **Max Changes per Fix**: Recommended ≤3 for low risk
- **Confidence Cap**: 95% (never 100%)
- **Timeout Bounds**: 5-60 seconds
- **Retry Attempts**: Minimum 3, recommended 3-5

---

For detailed documentation, see `TASK_54_REMEDIATION_AGENT_SUMMARY.md`
