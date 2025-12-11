# Pattern Detection Agent - Quick Reference

## Overview
The Pattern Detection Agent provides ML-based failure pattern recognition, intelligent alerting, and comprehensive analytics for the AI Test Automation Platform.

## Quick Start

### 1. Pattern Recognition

```typescript
import { PatternRecognitionEngine } from './services/pattern-recognition-engine';
import { BedrockService } from './services/bedrock-service';

// Initialize
const bedrockService = new BedrockService();
const engine = new PatternRecognitionEngine(bedrockService);

// Detect patterns
const failures = [
  {
    errorType: 'TimeoutError',
    component: 'LoginPage',
    duration: 5000,
    timestamp: new Date(),
    environment: 'production'
  }
  // ... more failures
];

const result = await engine.detectPatterns(failures, {
  useML: true,
  minConfidence: 0.7
});

console.log(`Found ${result.patterns.length} patterns`);
console.log(`Detected ${result.anomalies.length} anomalies`);
```

### 2. Alert Generation

```typescript
import { PatternAlertSystem, AlertChannel } from './services/pattern-alert-system';

// Initialize
const alertSystem = new PatternAlertSystem();

// Generate alerts
const alerts = await alertSystem.generateAlerts(result.patterns);

// Prioritize alerts
const prioritized = alertSystem.prioritizeAlerts(alerts);

// Route to channels
for (const alert of prioritized) {
  await alertSystem.routeAlert(alert);
}
```

### 3. Analytics

```typescript
import { PatternAnalyticsService } from './services/pattern-analytics-service';

// Initialize
const analytics = new PatternAnalyticsService();

// Build trend visualization
const trendData = analytics.buildTrendVisualization(pattern, historicalData);

// Analyze impact
const impact = analytics.analyzePatternImpact(pattern, testData);

// Generate forecast
const forecast = analytics.generateForecast(pattern, historicalData, 7);

// Get dashboard data
const dashboard = analytics.getDashboardData(patterns);
```

## Common Use Cases

### Detect and Alert on Critical Patterns

```typescript
// Detect patterns
const result = await engine.detectPatterns(failures);

// Filter critical patterns
const critical = result.patterns.filter(p => 
  p.severity === PatternSeverity.CRITICAL
);

// Generate and send alerts
const alerts = await alertSystem.generateAlerts(critical);
for (const alert of alerts) {
  await alertSystem.routeAlert(alert);
}
```

### Analyze Pattern Trends

```typescript
// Build visualization
const trendData = analytics.buildTrendVisualization(pattern, historicalData);

// Check trend direction
if (trendData.trend.direction === 'up') {
  console.log('Pattern is increasing!');
  console.log(`Velocity: ${trendData.trend.velocity}`);
}

// Get forecast
const forecast = analytics.generateForecast(pattern, historicalData, 7);
console.log(`Predicted occurrences in 7 days: ${forecast.predictions.length}`);
```

### Configure Alert Rules

```typescript
// Add custom alert rule
alertSystem.addRule({
  id: 'critical-payment-rule',
  name: 'Critical Payment Failures',
  enabled: true,
  conditions: [
    {
      type: 'severity',
      operator: 'eq',
      value: AlertSeverity.CRITICAL
    },
    {
      type: 'pattern_count',
      operator: 'gte',
      value: 5
    }
  ],
  actions: [
    {
      type: 'notify',
      channels: [AlertChannel.SLACK, AlertChannel.EMAIL],
      recipients: ['team@example.com']
    },
    {
      type: 'escalate',
      channels: [],
      recipients: []
    }
  ],
  cooldownPeriod: 30
});
```

### Find Pattern Correlations

```typescript
// Find correlations
const correlations = analytics.findPatternCorrelations(patterns);

// Filter strong correlations
const strong = correlations.filter(c => 
  c.correlationCoefficient > 0.7
);

console.log(`Found ${strong.length} strong correlations`);
strong.forEach(c => {
  console.log(`${c.pattern1Id} <-> ${c.pattern2Id}: ${c.relationship}`);
});
```

## API Reference

### PatternRecognitionEngine

#### Methods
- `detectPatterns(failures, options)` - Detect patterns from failure data
- `analyzeTimeSeries(patternId, dataPoints)` - Analyze time-series data
- `classifyPattern(pattern)` - Classify pattern type
- `getPattern(patternId)` - Get pattern by ID
- `getAllPatterns()` - Get all patterns
- `clearPatterns()` - Clear all patterns

#### Options
```typescript
{
  useML?: boolean,              // Enable ML enhancement (default: true)
  minConfidence?: number        // Min confidence (default: 0.7)
}
```

### PatternAlertSystem

#### Methods
- `generateAlerts(patterns)` - Generate alerts from patterns
- `prioritizeAlerts(alerts)` - Prioritize alerts
- `deduplicateAlerts(alerts)` - Remove duplicates
- `routeAlert(alert)` - Send alert to channels
- `addRule(rule)` - Add alert rule
- `removeRule(ruleId)` - Remove alert rule
- `acknowledgeAlert(alertId)` - Acknowledge alert
- `resolveAlert(alertId)` - Resolve alert

#### Configuration
```typescript
alertSystem.configureDeduplication({
  enabled: true,
  timeWindow: 60,              // minutes
  similarityThreshold: 0.8,    // 0-1
  groupByFields: ['patternId', 'severity']
});
```

### PatternAnalyticsService

#### Methods
- `buildTrendVisualization(pattern, data)` - Build trend chart
- `analyzePatternImpact(pattern, testData)` - Analyze impact
- `findPatternCorrelations(patterns)` - Find correlations
- `generateForecast(pattern, data, days)` - Generate forecast
- `getDashboardData(patterns)` - Get dashboard data
- `getTrendData(patternId)` - Get trend data
- `getImpactAnalysis(patternId)` - Get impact analysis
- `getForecast(patternId)` - Get forecast

## Pattern Types

```typescript
enum PatternType {
  FAILURE = 'failure',
  PERFORMANCE = 'performance',
  FLAKY = 'flaky',
  TIMEOUT = 'timeout',
  ASSERTION = 'assertion',
  NETWORK = 'network',
  CONFIGURATION = 'configuration',
  UNKNOWN = 'unknown'
}
```

## Alert Severities

```typescript
enum AlertSeverity {
  CRITICAL = 'critical',  // Immediate action required
  HIGH = 'high',          // Urgent attention needed
  MEDIUM = 'medium',      // Should be addressed soon
  LOW = 'low',            // Monitor and track
  INFO = 'info'           // Informational only
}
```

## Alert Channels

```typescript
enum AlertChannel {
  SLACK = 'slack',        // Slack notifications
  TEAMS = 'teams',        // Microsoft Teams
  EMAIL = 'email',        // Email notifications
  WEBHOOK = 'webhook'     // Custom webhooks
}
```

## Best Practices

### 1. Pattern Detection
- Use ML enhancement for better accuracy
- Set appropriate confidence thresholds
- Process failures in batches for efficiency
- Clear patterns periodically to manage memory

### 2. Alert Management
- Configure deduplication to reduce noise
- Set cooldown periods on rules
- Use priority scoring for triage
- Route critical alerts to multiple channels

### 3. Analytics
- Build visualizations for trending patterns
- Analyze impact before taking action
- Use forecasts for capacity planning
- Monitor correlations for root cause analysis

### 4. Performance
- Batch process large failure datasets
- Cache analytics results
- Use appropriate time windows
- Clean up old data regularly

## Troubleshooting

### Pattern Detection Issues
```typescript
// Check if patterns are being detected
const result = await engine.detectPatterns(failures, { useML: false });
console.log(`Patterns: ${result.patterns.length}`);
console.log(`Clusters: ${result.clusters.length}`);

// Verify failure data format
failures.forEach(f => {
  console.log(`Error: ${f.errorType}, Component: ${f.component}`);
});
```

### Alert Not Sending
```typescript
// Check alert status
const alert = alertSystem.getAlert(alertId);
console.log(`Status: ${alert?.status}`);
console.log(`Channels: ${alert?.channels}`);

// Verify alert rules
const rules = alertSystem.getRules();
console.log(`Active rules: ${rules.length}`);
```

### Analytics Data Missing
```typescript
// Verify data was generated
const trendData = analytics.getTrendData(patternId);
if (!trendData) {
  console.log('Trend data not found - rebuild visualization');
  analytics.buildTrendVisualization(pattern, historicalData);
}
```

## Integration Examples

### With Lambda Data Processor
```typescript
// Receive processed failures from Lambda
const processedFailures = await lambdaProcessor.getFailures();

// Detect patterns
const patterns = await engine.detectPatterns(processedFailures);

// Generate alerts
const alerts = await alertSystem.generateAlerts(patterns);
```

### With Agent Orchestrator
```typescript
// Register pattern detection task
orchestrator.registerTask({
  agentId: 'pattern-detection',
  task: async (data) => {
    const patterns = await engine.detectPatterns(data.failures);
    return { patterns, alerts: await alertSystem.generateAlerts(patterns) };
  }
});
```

### With Diagnostic Agent
```typescript
// Provide pattern data for diagnostics
const patterns = engine.getAllPatterns();
const diagnostics = await diagnosticAgent.analyze({
  patterns,
  correlations: analytics.findPatternCorrelations(patterns)
});
```

## Resources

- [Full Implementation Summary](../TASK_52_PATTERN_DETECTION_AGENT_SUMMARY.md)
- [Agent Architecture Guide](../AGENT_ARCHITECTURE_IMPLEMENTATION_GUIDE.md)
- [AWS Bedrock Integration](../TASK_3.1_BEDROCK_INFRASTRUCTURE_SUMMARY.md)
- [Lambda Data Processor](../TASK_49_LAMBDA_DATA_PROCESSOR_SUMMARY.md)

## Support

For issues or questions:
1. Check the implementation summary
2. Review test files for usage examples
3. Consult the agent architecture guide
4. Contact the platform team
