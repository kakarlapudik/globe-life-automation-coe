# Test Generation Agent - Quick Reference

## Overview

The Test Generation Agent is an AI-powered system that automatically creates test cases from natural language descriptions, failures, coverage gaps, and edge cases using AWS Bedrock exclusively.

## Components

### 1. Test Generation Engine (`test-generation-engine.ts`)

Core service for AI-powered test case generation.

**Key Features:**
- Natural language to test conversion
- Template-based test generation
- Page object model generation
- Test data generation
- Edge case identification

**Usage:**
```typescript
import { TestGenerationEngine } from './services/test-generation-engine';
import { BedrockService } from './services/bedrock-service';

const bedrockService = new BedrockService(config);
const engine = new TestGenerationEngine(bedrockService);

// Generate test from description
const result = await engine.generateTest({
  description: 'Test user login with valid credentials',
  context: {
    pageUrl: 'https://example.com/login',
    userRole: 'standard-user',
  },
  options: {
    includeEdgeCases: true,
    generatePageObjects: true,
    generateTestData: true,
  },
});

console.log(result.testDefinition);
console.log(result.pageObjects);
console.log(result.testData);
```

**Built-in Templates:**
- `login` - Standard login flow
- `form-submission` - Form submission flow
- `search` - Search functionality

**Custom Templates:**
```typescript
engine.registerTemplate({
  id: 'custom-flow',
  name: 'Custom Flow',
  description: 'Custom test flow',
  category: 'custom',
  variables: ['url', 'username'],
  tags: ['custom'],
  steps: [/* test steps */],
});
```

### 2. Dynamic Test Creator (`dynamic-test-creator.ts`)

Creates tests dynamically from failures, coverage gaps, and edge cases.

**Key Features:**
- Failure-driven test generation
- Coverage gap analysis
- Regression test generation
- Edge case test generation
- Test suite generation from multiple failures

**Usage:**

**Generate from Failure:**
```typescript
import { DynamicTestCreator } from './services/dynamic-test-creator';

const creator = new DynamicTestCreator(bedrockService, testGenerationEngine);

const failure: FailureAnalysis = {
  testId: 'test-123',
  testName: 'Login Test',
  failureReason: 'Element not found',
  failedStep: /* step details */,
  errorMessage: 'Element #login-btn not found',
  timestamp: new Date(),
};

const regressionTest = await creator.generateTestFromFailure(failure);
```

**Analyze Coverage Gaps:**
```typescript
const gaps = await creator.analyzeCoverageGaps(
  existingTests,
  ['User Authentication', 'Password Reset', 'Profile Management']
);

// Generate tests for gaps
const newTests = await creator.generateTestsForGaps(gaps);
```

**Generate Regression Test:**
```typescript
const regressionTest = await creator.generateRegressionTest({
  bugId: 'BUG-456',
  bugDescription: 'Login fails with special characters',
  stepsToReproduce: [
    'Navigate to login page',
    'Enter username',
    'Enter password with special characters',
    'Click login button',
  ],
  expectedBehavior: 'User should be logged in',
  actualBehavior: 'Login fails with error',
  affectedFeatures: ['authentication', 'password-validation'],
});
```

**Generate Edge Case Tests:**
```typescript
const edgeCaseScenarios = await creator.identifyEdgeCaseScenarios(baseTest);
const edgeCaseTests = await creator.generateEdgeCaseTests(baseTest, edgeCaseScenarios);
```

### 3. Test Validator (`test-validator.ts`)

Validates generated tests for syntax, quality, and executability.

**Key Features:**
- Syntax validation
- Structural validation
- Semantic validation using Bedrock
- Quality scoring
- Optimization suggestions
- Execution simulation

**Usage:**

**Validate Test:**
```typescript
import { TestValidator } from './services/test-validator';

const validator = new TestValidator(bedrockService);

const result = await validator.validateTest(testDefinition);

console.log('Valid:', result.isValid);
console.log('Score:', result.score);
console.log('Issues:', result.issues);
console.log('Warnings:', result.warnings);
console.log('Suggestions:', result.suggestions);
```

**Calculate Quality Metrics:**
```typescript
const metrics = await validator.calculateQualityMetrics(testDefinition);

console.log('Completeness:', metrics.completeness);
console.log('Maintainability:', metrics.maintainability);
console.log('Reliability:', metrics.reliability);
console.log('Clarity:', metrics.clarity);
console.log('Overall:', metrics.overall);
```

**Generate Optimization Suggestions:**
```typescript
const suggestions = await validator.generateOptimizationSuggestions(testDefinition);

suggestions.forEach(s => {
  console.log(`${s.type} (${s.priority}): ${s.description}`);
  console.log(`Impact: ${s.impact}`);
});
```

**Simulate Execution:**
```typescript
const simulation = await validator.simulateExecution(testDefinition);

console.log('Can Execute:', simulation.canExecute);
console.log('Estimated Duration:', simulation.estimatedDuration);
console.log('Potential Issues:', simulation.potentialIssues);
```

## Validation Rules

### Syntax Validation
- Test name is required
- Test description is required
- At least one test step is required
- Interactive steps must have target selectors
- Type steps must have input values
- Assert steps must have expected results

### Structural Validation
- Tests should have assertions
- Tests should have navigation steps
- Wait steps should precede assertions
- Tests should not be excessively long (>20 steps)
- Avoid duplicate selectors

### Semantic Validation (AI-powered)
- Logical flow issues
- Unrealistic scenarios
- Missing error handling
- Incomplete test coverage
- Ambiguous assertions
- Timing issues

## Quality Scoring

Quality score is calculated based on:
- **Critical issues**: -25 points each
- **Errors**: -10 points each
- **Warnings**: -5 points each
- **Good practices**: +5 points each
  - Has assertions
  - Has wait steps
  - Has alternative selectors

Score range: 0-100

## Best Practices

### Test Generation
1. Provide clear, detailed descriptions
2. Include context (page URL, user role, application context)
3. Specify requirements explicitly
4. Use templates for common patterns
5. Enable edge case generation for comprehensive coverage

### Dynamic Test Creation
1. Generate tests from failures immediately
2. Regularly analyze coverage gaps
3. Create regression tests for all bugs
4. Test edge cases systematically
5. Group similar failures for efficient test generation

### Test Validation
1. Validate all generated tests before execution
2. Address critical issues immediately
3. Review and fix errors
4. Consider warnings for test quality
5. Apply optimization suggestions
6. Simulate execution to catch runtime issues

## AWS Bedrock Models Used

- **Claude 3 Opus**: Complex test generation, comprehensive analysis
- **Claude 3 Sonnet**: Balanced tasks, validation, optimization
- **Claude 3 Haiku**: Fast edge case generation, quick validations

## Integration Example

Complete workflow:

```typescript
// 1. Generate test
const engine = new TestGenerationEngine(bedrockService);
const result = await engine.generateTest({
  description: 'Test user registration with email verification',
  options: {
    includeEdgeCases: true,
    generatePageObjects: true,
    generateTestData: true,
  },
});

// 2. Validate test
const validator = new TestValidator(bedrockService);
const validation = await validator.validateTest(result.testDefinition);

if (!validation.isValid) {
  console.error('Validation failed:', validation.issues);
  // Fix issues or regenerate
}

// 3. Calculate quality metrics
const metrics = await validator.calculateQualityMetrics(result.testDefinition);
console.log('Quality Score:', metrics.overall);

// 4. Get optimization suggestions
const suggestions = await validator.generateOptimizationSuggestions(result.testDefinition);
console.log('Optimizations:', suggestions);

// 5. Simulate execution
const simulation = await validator.simulateExecution(result.testDefinition);
if (!simulation.canExecute) {
  console.error('Cannot execute:', simulation.potentialIssues);
}

// 6. Execute test (if valid)
if (validation.isValid && simulation.canExecute) {
  // Execute test using test execution engine
}
```

## Error Handling

All services handle errors gracefully:
- Invalid Bedrock responses are caught and logged
- Fallback values are provided when AI generation fails
- Detailed error messages help with debugging
- Services continue operation even if optional features fail

## Performance Considerations

- Use templates for common patterns (faster than full generation)
- Cache generated page objects for reuse
- Batch multiple test generations when possible
- Use Haiku model for simple, fast operations
- Use Opus model only for complex scenarios

## Testing

All services have comprehensive unit tests:
- `test-generation-engine.test.ts`
- `dynamic-test-creator.test.ts`
- `test-validator.test.ts`

Run tests:
```bash
npm test -- src/services/__tests__/test-generation-engine.test.ts
npm test -- src/services/__tests__/dynamic-test-creator.test.ts
npm test -- src/services/__tests__/test-validator.test.ts
```

## Next Steps

1. Integrate with Test Generator Agent (`src/agents/test-generator-agent.ts`)
2. Add UI components for test generation
3. Implement test execution integration
4. Add analytics and reporting
5. Create documentation and training materials
