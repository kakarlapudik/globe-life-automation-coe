# Lambda Data Processor - Quick Reference

## Overview
The Lambda Data Processor is a core component of the Agent-Based Architecture that handles real-time event processing, failure pattern extraction, and data storage management.

## Components

### 1. Event Processing Pipeline
**File**: `src/services/event-processing-pipeline.ts`

Processes events from Kinesis streams and batch data sources.

```typescript
import { EventProcessingPipeline } from './services/event-processing-pipeline';

const pipeline = new EventProcessingPipeline(
  'stream-name',
  'table-name',
  'bucket-name',
  'us-east-1'
);

// Process Kinesis records
const result = await pipeline.processStreamEvents(records);

// Process batch data
const batchResult = await pipeline.processBatchData(events, {
  batchSize: 25,
  maxRetries: 3,
  retryDelayMs: 1000,
  timeoutMs: 5000
});
```

**Key Features**:
- Real-time stream processing
- Configurable batch processing
- Automatic retry with exponential backoff
- Dual storage (DynamoDB + S3)
- Processing statistics

### 2. Failure Pattern Extractor
**File**: `src/services/failure-pattern-extractor.ts`

Extracts patterns from failure events using ML algorithms.

```typescript
import { FailurePatternExtractor } from './services/failure-pattern-extractor';

const extractor = new FailurePatternExtractor();

// Extract patterns
const patterns = await extractor.extractPatterns(events);

// Detect anomalies
const anomaly = await extractor.detectAnomalies(event, historicalData);

// Cluster failures
const clusters = await extractor.clusterFailures(events);
```

**Key Features**:
- Signature generation with normalization
- K-means clustering
- Anomaly detection
- Pattern management

### 3. Data Storage Layer
**File**: `src/services/data-storage-layer.ts`

Manages data persistence in DynamoDB and S3.

```typescript
import { DataStorageLayer } from './services/data-storage-layer';

const storage = new DataStorageLayer({
  dynamoTableName: 'failures',
  s3BucketName: 'historical-data',
  region: 'us-east-1',
  retentionDays: 30
});

// Store recent failure
await storage.storeRecentFailure(event);

// Query failures
const failures = await storage.queryRecentFailures('test-failure');

// Archive data
await storage.archiveHistoricalData(events, new Date());
```

**Key Features**:
- DynamoDB with GSIs
- S3 with lifecycle policies
- Batch operations
- Storage metrics

## Data Flow

```
Events → Kinesis → Processing Pipeline → Pattern Extractor
                                              ↓
                                    Storage Layer
                                    ↓         ↓
                              DynamoDB      S3
```

## Configuration

### Environment Variables
```bash
KINESIS_STREAM_NAME=test-events-stream
DYNAMODB_TABLE_NAME=test-failures
S3_BUCKET_NAME=test-historical-data
AWS_REGION=us-east-1
RETENTION_DAYS=30
```

### AWS Resources
- Kinesis Stream
- DynamoDB Tables (events + patterns)
- S3 Bucket
- IAM Roles

## Common Operations

### Process Events
```typescript
// Single event
await pipeline.processEvent(event);

// Batch
await pipeline.processBatchData(events, config);

// Stream
await pipeline.processStreamEvents(kinesisRecords);
```

### Extract Patterns
```typescript
// Generate signature
const signature = await extractor.generateSignature(event);

// Extract patterns
const patterns = await extractor.extractPatterns(events);

// Get all patterns
const allPatterns = extractor.getAllPatterns();
```

### Store Data
```typescript
// Store event
await storage.storeRecentFailure(event);

// Store pattern
await storage.storeFailurePattern(pattern);

// Archive
await storage.archiveHistoricalData(events, date);
```

### Query Data
```typescript
// Query by event type
const failures = await storage.queryRecentFailures('test-failure');

// Query with time range
const failures = await storage.queryRecentFailures(
  'test-failure',
  startDate,
  endDate
);

// Query patterns
const patterns = await storage.queryFailurePatterns('critical');
```

## Error Handling

### Retryable Errors
- ThrottlingException
- ProvisionedThroughputExceededException
- ServiceUnavailable
- InternalServerError
- RequestTimeout

### Retry Strategy
```typescript
// Exponential backoff
delay = 2^retryCount * 1000ms
maxRetries = 3
```

## Performance

### Metrics
- Event processing: < 100ms
- Pattern extraction: O(n log n)
- Storage operations: < 50ms
- Query operations: < 200ms

### Scalability
- DynamoDB: Pay-per-request auto-scaling
- S3: Unlimited storage
- Kinesis: Configurable shards
- Lambda: Concurrent execution

## Testing

### Run Tests
```bash
# All tests
npm test

# Specific component
npm test event-processing-pipeline
npm test failure-pattern-extractor
npm test data-storage-layer

# With coverage
npm test -- --coverage
```

### Test Structure
- Unit tests with mocked AWS SDK
- Success and error scenarios
- Data validation tests
- Integration test scenarios

## Monitoring

### CloudWatch Metrics
- Event processing rate
- Error rate
- Pattern detection count
- Storage operations
- Query latency

### Alarms
- High error rate
- Processing latency
- Storage capacity
- Pattern anomalies

## Troubleshooting

### Common Issues

**Memory Issues**
- Increase Lambda memory
- Optimize batch sizes
- Use streaming for large datasets

**Throttling**
- Increase DynamoDB capacity
- Implement exponential backoff
- Use batch operations

**Pattern Quality**
- Adjust clustering parameters
- Increase historical data
- Tune normalization rules

## Best Practices

1. **Batch Operations**: Use batch writes for efficiency
2. **Error Handling**: Always implement retry logic
3. **Monitoring**: Set up CloudWatch alarms
4. **Testing**: Maintain high test coverage
5. **Documentation**: Keep patterns documented
6. **Lifecycle**: Configure S3 lifecycle policies
7. **Security**: Use encryption and IAM roles
8. **Performance**: Monitor and optimize queries

## Integration Points

### Upstream
- EventBridge (Task 48)
- Event Source Connectors

### Downstream
- Pattern Detection Agent (Task 52)
- Diagnostic Agent (Task 53)
- Remediation Agent (Task 54)
- Agent Orchestrator (Task 50)

## Resources

- [AWS Kinesis Documentation](https://docs.aws.amazon.com/kinesis/)
- [AWS DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [Task 49 Summary](../TASK_49_LAMBDA_DATA_PROCESSOR_SUMMARY.md)

## Support

For issues or questions:
1. Check CloudWatch logs
2. Review error messages
3. Verify AWS permissions
4. Check resource limits
5. Consult team documentation
