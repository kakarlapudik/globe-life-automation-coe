---
inclusion: manual
---

# Pipeline Design Framework - Security Standards

Security best practices and compliance requirements for AWS CDK pipelines.

## Security Principles

1. Defense in depth - multiple security layers
2. Least privilege - minimal required permissions
3. Zero trust - always verify
4. Encryption everywhere - at rest and in transit
5. Audit everything - comprehensive logging

## IAM Permissions Boundaries

All roles must operate within defined boundaries:

```typescript
const permissionsBoundary = new iam.ManagedPolicy(this, 'Boundary', {
  statements: [
    new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['*'],
      resources: ['*']
    }),
    new iam.PolicyStatement({
      effect: iam.Effect.DENY,
      actions: [
        'iam:CreateUser', 'iam:DeleteUser',
        'organizations:*',
        'aws-portal:*',
        'cloudtrail:DeleteTrail'
      ],
      resources: ['*']
    })
  ]
})
```

## Cross-Account Roles

```typescript
const deployRole = new iam.Role(this, 'DeployRole', {
  assumedBy: new iam.AccountPrincipal(toolsAccountId),
  externalIds: [externalId],
  maxSessionDuration: Duration.hours(1),
  permissionsBoundary: permissionsBoundary
})
```

## Encryption Standards

**S3 Buckets:**
```typescript
const bucket = new s3.Bucket(this, 'Bucket', {
  encryption: s3.BucketEncryption.KMS,
  encryptionKey: kmsKey,
  enforceSSL: true,
  blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
  versioned: true
})
```

**DynamoDB:**
```typescript
const table = new dynamodb.Table(this, 'Table', {
  encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
  encryptionKey: kmsKey,
  pointInTimeRecovery: true
})
```

**KMS Keys:**
```typescript
const key = new kms.Key(this, 'Key', {
  enableKeyRotation: true,
  description: 'Encryption key for sensitive data'
})
```

## Network Security

**VPC Configuration:**
```typescript
const vpc = new ec2.Vpc(this, 'VPC', {
  maxAzs: 3,
  natGateways: 2,
  subnetConfiguration: [
    { name: 'Public', subnetType: ec2.SubnetType.PUBLIC },
    { name: 'Private', subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS },
    { name: 'Isolated', subnetType: ec2.SubnetType.PRIVATE_ISOLATED }
  ]
})

// Enable VPC Flow Logs
new ec2.FlowLog(this, 'FlowLog', {
  resourceType: ec2.FlowLogResourceType.fromVpc(vpc)
})
```

**Security Groups:**
```typescript
const sg = new ec2.SecurityGroup(this, 'SG', {
  vpc,
  allowAllOutbound: false
})

sg.addIngressRule(ec2.Peer.anyIpv4(), ec2.Port.tcp(443), 'HTTPS only')
```

## API Security

```typescript
const api = new apigateway.RestApi(this, 'API', {
  policy: new iam.PolicyDocument({
    statements: [
      new iam.PolicyStatement({
        effect: iam.Effect.DENY,
        principals: [new iam.AnyPrincipal()],
        actions: ['execute-api:Invoke'],
        resources: ['*'],
        conditions: { Bool: { 'aws:SecureTransport': 'false' } }
      })
    ]
  })
})
```

## Secrets Management

```typescript
const secret = new secretsmanager.Secret(this, 'Secret', {
  generateSecretString: {
    secretStringTemplate: JSON.stringify({ username: 'admin' }),
    generateStringKey: 'password',
    passwordLength: 32
  },
  encryptionKey: kmsKey
})
```

## Security Scanning

Integrate security scanning in pipelines:

```yaml
- name: Run cfn-nag
  run: |
    gem install cfn-nag
    cfn-nag_scan --input-path cdk.out

- name: Run Checkov
  run: |
    pip install checkov
    checkov -d cdk.out --framework cloudformation
```

## Resource Tagging

```typescript
Tags.of(this).add('Environment', environment)
Tags.of(this).add('Project', 'PipelineFramework')
Tags.of(this).add('Owner', 'DevOps')
Tags.of(this).add('CostCenter', 'Engineering')
```

## Compliance

- Enable AWS Config for compliance monitoring
- Use AWS Security Hub for centralized security findings
- Implement CloudTrail for audit logging
- Regular security assessments and penetration testing
