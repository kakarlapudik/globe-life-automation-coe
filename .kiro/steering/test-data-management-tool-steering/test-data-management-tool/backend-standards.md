---
inclusion: manual
---

# Test Data Management Tool - Backend Standards

This document defines coding standards and best practices for building the Node.js/TypeScript backend services for the Test Data Management Tool.

## Technology Stack

### Core Technologies
**Runtime**: Node.js 18+ LTS
**Language**: TypeScript 5.0+
**Web Framework**: Express.js 4.18+
**Database**: PostgreSQL 15+
**ORM**: Prisma or TypeORM
**Testing**: Jest + Supertest
**API Documentation**: Swagger/OpenAPI 3.0

### Supporting Libraries
**Validation**: Zod or Joi
**Authentication**: jsonwebtoken, passport
**Logging**: Winston or Pino
**Scheduling**: node-cron or Bull
**Data Generation**: Faker.js, Chance.js
**HTTP Client**: Axios

## Project Structure

```
src/
├── services/           # Business logic services
│   ├── data-generator/
│   │   ├── DataGeneratorService.ts
│   │   ├── SchemaParser.ts
│   │   └── JobManager.ts
│   ├── synthetic-data/
│   │   ├── SyntheticDataGenerator.ts
│   │   ├── PrivacyEngine.ts
│   │   └── PatternAnalyzer.ts
│   ├── data-manager/
│   │   ├── DataManagerService.ts
│   │   ├── TeamEnvironmentManager.ts
│   │   └── DataDistributor.ts
│   ├── quality/
│   │   ├── QualityValidator.ts
│   │   ├── RuleEngine.ts
│   │   └── MetricsCalculator.ts
│   └── scheduler/
│       ├── SchedulerService.ts
│       ├── RefreshExecutor.ts
│       └── NotificationManager.ts
├── models/             # Data models and types
│   ├── Dataset.ts
│   ├── Team.ts
│   ├── GenerationJob.ts
│   └── QualityReport.ts
├── repositories/       # Data access layer
│   ├── DatasetRepository.ts
│   ├── TeamRepository.ts
│   └── JobRepository.ts
├── api/                # API routes and controllers
│   ├── routes/
│   │   ├── generation.routes.ts
│   │   ├── team.routes.ts
│   │   └── quality.routes.ts
│   ├── controllers/
│   │   ├── GenerationController.ts
│   │   ├── TeamController.ts
│   │   └── QualityController.ts
│   └── middleware/
│       ├── auth.middleware.ts
│       ├── validation.middleware.ts
│       └── error.middleware.ts
├── utils/              # Utility functions
│   ├── logger.ts
│   ├── validators.ts
│   └── constants.ts
├── config/             # Configuration
│   ├── database.ts
│   ├── server.ts
│   └── environment.ts
└── types/              # TypeScript type definitions
    ├── api.types.ts
    ├── service.types.ts
    └── database.types.ts
```

## Coding Standards

### TypeScript Best Practices

```typescript
// Good: Use strict type definitions
interface DataSchema {
  entities: EntityDefinition[]
  relationships: RelationshipDefinition[]
  constraints: ConstraintDefinition[]
  volume: VolumeSpecification
}

interface GenerationOptions {
  format: 'JSON' | 'XML' | 'CSV' | 'SQL'
  teamId: string
  refreshCycle: boolean
  qualityLevel: 'basic' | 'standard' | 'premium'
}

// Good: Use async/await for asynchronous operations
async function generateData(
  schema: DataSchema,
  options: GenerationOptions
): Promise<Dataset> {
  try {
    const validatedSchema = await validateSchema(schema)
    const generatedData = await dataGenerator.generate(validatedSchema, options)
    const qualityReport = await qualityValidator.validate(generatedData)
    
    return {
      ...generatedData,
      qualityReport
    }
  } catch (error) {
    logger.error('Data generation failed', { error, schema, options })
    throw new DataGenerationError('Failed to generate data', error)
  }
}

// Good: Use dependency injection
class DataGeneratorService {
  constructor(
    private readonly schemaParser: SchemaParser,
    private readonly jobManager: JobManager,
    private readonly qualityValidator: QualityValidator,
    private readonly logger: Logger
  ) {}

  async generateData(
    schema: DataSchema,
    options: GenerationOptions
  ): Promise<Dataset> {
    // Implementation
  }
}

// Good: Use proper error handling with custom errors
class DataGenerationError extends Error {
  constructor(
    message: string,
    public readonly cause?: Error,
    public readonly context?: Record<string, any>
  ) {
    super(message)
    this.name = 'DataGenerationError'
  }
}

// Good: Use enums for constants
enum GenerationStatus {
  PENDING = 'pending',
  RUNNING = 'running',
  COMPLETED = 'completed',
  FAILED = 'failed'
}

// Good: Use type guards
function isDataSchema(obj: unknown): obj is DataSchema {
  return (
    typeof obj === 'object' &&
    obj !== null &&
    'entities' in obj &&
    'relationships' in obj &&
    Array.isArray((obj as any).entities)
  )
}
```

### Service Layer Pattern

```typescript
// DataGeneratorService.ts
import { injectable, inject } from 'inversify'
import { Logger } from 'winston'

@injectable()
export class DataGeneratorService {
  constructor(
    @inject('SchemaParser') private schemaParser: SchemaParser,
    @inject('JobManager') private jobManager: JobManager,
    @inject('Logger') private logger: Logger
  ) {}

  async generateData(
    schema: DataSchema,
    options: GenerationOptions
  ): Promise<GenerationJob> {
    this.logger.info('Starting data generation', { schema, options })

    // 