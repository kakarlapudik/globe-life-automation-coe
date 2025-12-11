---
inclusion: manual
---

# Pipeline Design Framework - Deployment Guide

Deployment strategies and operational procedures for AWS CDK pipelines.

## Multi-Account Strategy

Deploy across Tools, Dev, Staging, and Production accounts with proper isolation and cross-account roles.

## Account Bootstrap

```bash
# Tools account (pipeline host)
cdk bootstrap aws://TOOLS-ACCOUNT/us-east-1 \
  --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess

# Target accounts with trust
cdk bootstrap aws://TARGET-ACCOUNT/us-east-1 \
  --trust TOOLS-ACCOUNT \
  --cloudformation-execution-policies arn:aws:iam::aws:policy/AdministratorAccess
```

## Environment Configuration

```typescript
export const environments = {
  dev: {
    account: '111111111111',
    region: 'us-east-1',
    instanceTypes: { lambda: 128, ec2: 't3.micro' },
    scaling: { minCapacity: 1, maxCapacity: 5 }
  },
  staging: {
    account: '222222222222',
    region: 'us-east-1',
    instanceTypes: { lambda: 256, ec2: 't3.small' },
    scaling: { minCapacity: 2, maxCapacity: 10 }
  },
  prod: {
    account: '333333333333',
    region: 'us-east-1',
    instanceTypes: { lambda: 512, ec2: 't3.medium' },
    scaling: { minCapacity: 3, maxCapacity: 20 }
  }
}
```

## Pipeline Structure

```typescript
const pipeline = new pipelines.CodePipeline(this, 'Pipeline', {
  synth: new pipelines.ShellStep('Synth', {
    input: pipelines.CodePipelineSource.connection(
      'org/repo', 'main',
      { connectionArn: process.env.CODESTAR_CONNECTION_ARN }
    ),
    commands: ['npm ci', 'npm run build', 'npm test', 'npx cdk synth']
  }),
  crossAccountKeys: true
})

// Add stages with testing
pipeline.addStage(devStage, {
  post: [new pipelines.ShellStep('IntegrationTests', {
    commands: ['npm run test:integration']
  })]
})

pipeline.addStage(prodStage, {
  pre: [new pipelines.ManualApprovalStep('PromoteToProd')]
})
```

## Monitoring

```typescript
const errorAlarm = new cloudwatch.Alarm(this, 'Errors', {
  metric: lambdaFunction.metricErrors(),
  threshold: 1,
  evaluationPeriods: 1
})

errorAlarm.addAlarmAction(new cloudwatchActions.SnsAction(alertTopic))
```

## Rollback

Enable automatic rollback on failures:

```typescript
const stack = new Stack(this, 'App', {
  terminationProtection: env === 'prod',
  rollbackConfiguration: {
    rollbackTriggers: [{ arn: errorAlarm.alarmArn, type: 'AWS::CloudWatch::Alarm' }]
  }
})
```

## Deployment Checklist

**Pre-Deployment:**
- Code review completed
- All tests passing
- Security scan passed

**Deployment:**
- Deploy to staging
- Run smoke tests
- Get approval
- Deploy to production

**Post-Deployment:**
- Verify health checks
- Monitor metrics
- Update documentation
