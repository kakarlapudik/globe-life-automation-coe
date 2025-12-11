/**
 * Application Stack Template for TypeScript CDK
 * Reusable CDK stack template for application infrastructure
 * Version: 1.0.0
 */

import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';

export interface ApplicationStackProps extends cdk.StackProps {
  readonly appName: string;
  readonly stackId: string;
}

/**
 * Reusable Application Stack for CDK applications
 * Template for deploying application infrastructure
 */
export class ApplicationStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: ApplicationStackProps) {
    // Validate required properties
    if (!props.appName) {
      throw new Error('APP_NAME is required in ApplicationStackProps');
    }
    if (!props.stackId) {
      throw new Error('STACK_ID is required in ApplicationStackProps');
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

    // Override stack name to follow naming convention: AppStack + app_name + stack_id
    const stackName = `AppStack${props.appName}${props.stackId}`;

    super(scope, stackName, {
      ...props,
      synthesizer,
      stackName,
      env: {
        account: process.env.CDK_DEFAULT_ACCOUNT,
        region: process.env.CDK_DEFAULT_REGION
      }
    });

    // Add standard tags
    this.addTags(props.appName, props.stackId);

    // TODO: Add your application resources here
    // Example:
    // new lambda.Function(this, 'MyFunction', { ... });
    // new dynamodb.Table(this, 'MyTable', { ... });
    // new apigateway.RestApi(this, 'MyApi', { ... });
  }

  private addTags(appName: string, stackId: string): void {
    const tags = {
      Application: appName,
      StackId: stackId,
      Environment: stackId,
      ManagedBy: 'CDK',
      Framework: 'Pipeline-Design-Framework'
    };

    Object.entries(tags).forEach(([key, value]) => {
      cdk.Tags.of(this).add(key, value);
    });
  }
}
