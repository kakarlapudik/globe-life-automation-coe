/**
 * Pipeline Stack Template for TypeScript CDK
 * Reusable CDK stack for creating AWS CodePipeline infrastructure
 * Version: 1.0.0
 */

import * as cdk from 'aws-cdk-lib';
import * as codepipeline from 'aws-cdk-lib/aws-codepipeline';
import * as codepipeline_actions from 'aws-cdk-lib/aws-codepipeline-actions';
import * as codebuild from 'aws-cdk-lib/aws-codebuild';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as kms from 'aws-cdk-lib/aws-kms';
import { Construct } from 'constructs';

/**
 * Aspect to enforce naming conventions and permissions boundaries on IAM roles
 */
class RoleNamingConventionAspect implements cdk.IAspect {
  constructor(
    private readonly appName: string,
    private readonly stackId: string,
    private readonly permissionsBoundary?: string
  ) {}

  visit(node: Construct): void {
    if (node instanceof iam.Role) {
      const role = node as iam.Role;
      
      // Enforce naming convention
      if (!role.roleName) {
        const purpose = node.node.id.replace('Role', '').toLowerCase();
        (role as any).roleName = `${this.appName}-${this.stackId}-${purpose}-role`;
      }
      
      // Attach permissions boundary
      if (this.permissionsBoundary) {
        role.permissionsBoundary = iam.ManagedPolicy.fromManagedPolicyArn(
          node,
          'PermissionsBoundary',
          this.permissionsBoundary
        );
      }
    }
  }
}

export interface PipelineStackProps extends cdk.StackProps {
  readonly appName: string;
  readonly stackId: string;
  readonly sourceRepo: string;
  readonly sourceBranch?: string;
  readonly buildSpecPath?: string;
  readonly permissionsBoundary?: string;
  readonly environmentVariables?: { [key: string]: string };
}

/**
 * Reusable Pipeline Stack for CDK applications
 * Creates CodePipeline with CodeBuild for automated deployments
 */
export class PipelineStack extends cdk.Stack {
  public readonly pipeline: codepipeline.Pipeline;
  public readonly buildProject: codebuild.Project;
  public readonly artifactBucket: s3.Bucket;
  
  private readonly appName: string;
  private readonly stackId: string;
  private readonly sourceRepo: string;
  private readonly sourceBranch: string;
  private readonly permissionsBoundary?: string;
  private readonly environmentVariables: { [key: string]: string };
  private pipelineKey!: kms.Key;
  private buildRole!: iam.Role;
  private pipelineRole!: iam.Role;

  constructor(scope: Construct, id: string, props: PipelineStackProps) {
    // Validate required environment variables
    if (!props.appName) {
      throw new Error('APP_NAME is required in PipelineStackProps');
    }
    if (!props.stackId) {
      throw new Error('STACK_ID is required in PipelineStackProps');
    }
    
    // Configure synthesizer with custom qualifier
    const qualifier = `${props.appName.toLowerCase().replace(/-/g, '')}${props.stackId.toLowerCase().replace(/-/g, '')}`.substring(0, 10);
    
    const synthesizer = new cdk.DefaultStackSynthesizer({
      qualifier: qualifier,
      fileAssetsBucketName: `cdk-${qualifier}-assets-\${AWS::AccountId}-\${AWS::Region}`,
      bucketPrefix: '',
      imageAssetsRepositoryName: `cdk-${qualifier}-container-assets-\${AWS::AccountId}-\${AWS::Region}`,
      cloudFormationExecutionRole: `arn:aws:iam::\${AWS::AccountId}:role/cdk-${qualifier}-cfn-exec-role-\${AWS::AccountId}-\${AWS::Region}`,
      deployRoleArn: `arn:aws:iam::\${AWS::AccountId}:role/cdk-${qualifier}-deploy-role-\${AWS::AccountId}-\${AWS::Region}`,
      fileAssetPublishingRoleArn: `arn:aws:iam::\${AWS::AccountId}:role/cdk-${qualifier}-file-publishing-role-\${AWS::AccountId}-\${AWS::Region}`,
      imageAssetPublishingRoleArn: `arn:aws:iam::\${AWS::AccountId}:role/cdk-${qualifier}-image-publishing-role-\${AWS::AccountId}-\${AWS::Region}`,
      lookupRoleArn: `arn:aws:iam::\${AWS::AccountId}:role/cdk-${qualifier}-lookup-role-\${AWS::AccountId}-\${AWS::Region}`
    });
    
    // Override stack name to follow naming convention: PipelineStack + app_name + stack_id
    const stackName = `PipelineStack${props.appName}${props.stackId}`;
    
    super(scope, stackName, { ...props, synthesizer, stackName });
    
    this.appName = props.appName;
    this.stackId = props.stackId;
    this.sourceRepo = props.sourceRepo;
    this.sourceBranch = props.sourceBranch || 'main';
    this.permissionsBoundary = props.permissionsBoundary;
    
    // Set default environment variables
    this.environmentVariables = {
      APP_NAME: this.appName,
      STACK_ID: this.stackId,
      CDK_DEFAULT_REGION: this.region,
      ...(props.environmentVariables || {})
    };
    
    if (this.permissionsBoundary) {
      this.environmentVariables.PERMISSIONS_BOUNDARY = this.permissionsBoundary;
    }
    
    // Apply naming convention aspect
    cdk.Aspects.of(this).add(
      new RoleNamingConventionAspect(this.appName, this.stackId, this.permissionsBoundary)
    );
    
    // Create pipeline resources
    this.createEncryptionKey();
    this.artifactBucket = this.createArtifactBucket();
    this.buildRole = this.createBuildRole();
    this.pipelineRole = this.createPipelineRole();
    this.buildProject = this.createBuildProject(props.buildSpecPath);
    this.pipeline = this.createPipeline();
    this.addTags();
  }

  private createEncryptionKey(): void {
    this.pipelineKey = new kms.Key(this, 'PipelineKey', {
      description: `KMS Key for ${this.appName}-${this.stackId} pipeline`,
      enableKeyRotation: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });
  }

  private createArtifactBucket(): s3.Bucket {
    return new s3.Bucket(this, 'ArtifactBucket', {
      bucketName: `${this.appName}-${this.stackId}-pipeline-artifacts-${this.account}`,
      encryption: s3.BucketEncryption.KMS,
      encryptionKey: this.pipelineKey,
      versioned: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true
    });
  }

  private createBuildRole(): iam.Role {
    const role = new iam.Role(this, 'BuildRole', {
      assumedBy: new iam.ServicePrincipal('codebuild.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('PowerUserAccess')
      ]
    });
    
    // Add CDK-specific permissions
    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: [
        'iam:CreateRole',
        'iam:DeleteRole',
        'iam:AttachRolePolicy',
        'iam:DetachRolePolicy',
        'iam:PutRolePolicy',
        'iam:DeleteRolePolicy',
        'iam:PassRole'
      ],
      resources: [`arn:aws:iam::${this.account}:role/${this.appName}-*`]
    }));
    
    this.pipelineKey.grantEncryptDecrypt(role);
    
    return role;
  }

  private createPipelineRole(): iam.Role {
    const role = new iam.Role(this, 'PipelineRole', {
      assumedBy: new iam.ServicePrincipal('codepipeline.amazonaws.com')
    });
    
    this.artifactBucket.grantReadWrite(role);
    this.pipelineKey.grantEncryptDecrypt(role);
    
    role.addToPolicy(new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['codebuild:BatchGetBuilds', 'codebuild:StartBuild'],
      resources: [`arn:aws:codebuild:${this.region}:${this.account}:project/${this.appName}-*`]
    }));
    
    return role;
  }

  private createBuildProject(buildSpecPath?: string): codebuild.Project {
    return new codebuild.Project(this, 'BuildProject', {
      projectName: `${this.appName}-${this.stackId}-build`,
      role: this.buildRole,
      environment: {
        buildImage: codebuild.LinuxBuildImage.STANDARD_7_0,
        computeType: codebuild.ComputeType.SMALL,
        privileged: true
      },
      environmentVariables: Object.entries(this.environmentVariables).reduce(
        (acc, [key, value]) => ({
          ...acc,
          [key]: { value }
        }),
        {}
      ),
      buildSpec: buildSpecPath 
        ? codebuild.BuildSpec.fromSourceFilename(buildSpecPath)
        : codebuild.BuildSpec.fromSourceFilename('buildspec.yml'),
      timeout: cdk.Duration.hours(2),
      encryptionKey: this.pipelineKey
    });
  }

  private createPipeline(): codepipeline.Pipeline {
    const sourceOutput = new codepipeline.Artifact('SourceOutput');
    const buildOutput = new codepipeline.Artifact('BuildOutput');
    
    const buildAction = new codepipeline_actions.CodeBuildAction({
      actionName: 'Build',
      project: this.buildProject,
      input: sourceOutput,
      outputs: [buildOutput]
    });
    
    return new codepipeline.Pipeline(this, 'Pipeline', {
      pipelineName: `${this.appName}-${this.stackId}-pipeline`,
      role: this.pipelineRole,
      artifactBucket: this.artifactBucket,
      encryptionKey: this.pipelineKey
    });
  }

  private addTags(): void {
    const tags = {
      Application: this.appName,
      StackId: this.stackId,
      Environment: 'pipeline',
      ManagedBy: 'CDK',
      Framework: 'Pipeline-Design-Framework'
    };
    
    Object.entries(tags).forEach(([key, value]) => {
      cdk.Tags.of(this).add(key, value);
    });
  }
}
