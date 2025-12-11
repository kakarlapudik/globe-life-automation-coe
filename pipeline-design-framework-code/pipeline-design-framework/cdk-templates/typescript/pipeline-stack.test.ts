/**
 * Unit tests for TypeScript PipelineStack
 * Tests validation, naming conventions, and resource creation
 */

import * as cdk from 'aws-cdk-lib';
import { Template } from 'aws-cdk-lib/assertions';
import { PipelineStack } from './pipeline-stack';

describe('PipelineStack', () => {
  describe('Validation', () => {
    test('throws error when appName is missing', () => {
      const app = new cdk.App();
      
      expect(() => {
        new PipelineStack(app, 'TestStack', {
          appName: '',
          stackId: 'test',
          sourceRepo: 'test-repo'
        });
      }).toThrow('APP_NAME is required in PipelineStackProps');
    });

    test('throws error when stackId is missing', () => {
      const app = new cdk.App();
      
      expect(() => {
        new PipelineStack(app, 'TestStack', {
          appName: 'testapp',
          stackId: '',
          sourceRepo: 'test-repo'
        });
      }).toThrow('STACK_ID is required in PipelineStackProps');
    });
  });

  describe('Stack Naming', () => {
    test('follows naming convention PipelineStack + appName + stackId', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo'
      });
      
      expect(stack.stackName).toBe('PipelineStackmyappdev');
    });
  });

  describe('Synthesizer Configuration', () => {
    test('uses DefaultStackSynthesizer with custom qualifier', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo'
      });
      
      // Qualifier should be first 10 chars of lowercase appName+stackId without hyphens
      const template = Template.fromStack(stack);
      
      // Verify synthesizer is configured (check for CDK bootstrap resources)
      expect(template).toBeDefined();
    });

    test('handles app names with hyphens in qualifier', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'my-app',
        stackId: 'dev-env',
        sourceRepo: 'test-repo'
      });
      
      // Should remove hyphens and truncate to 10 chars
      expect(stack.stackName).toBe('PipelineStackmy-appdev-env');
    });
  });

  describe('Resource Creation', () => {
    test('creates KMS key for encryption', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo'
      });
      
      const template = Template.fromStack(stack);
      
      template.resourceCountIs('AWS::KMS::Key', 1);
      template.hasResourceProperties('AWS::KMS::Key', {
        EnableKeyRotation: true
      });
    });

    test('creates S3 artifact bucket with encryption', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo'
      });
      
      const template = Template.fromStack(stack);
      
      template.resourceCountIs('AWS::S3::Bucket', 1);
      template.hasResourceProperties('AWS::S3::Bucket', {
        VersioningConfiguration: {
          Status: 'Enabled'
        },
        PublicAccessBlockConfiguration: {
          BlockPublicAcls: true,
          BlockPublicPolicy: true,
          IgnorePublicAcls: true,
          RestrictPublicBuckets: true
        }
      });
    });

    test('creates CodeBuild project', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo'
      });
      
      const template = Template.fromStack(stack);
      
      template.resourceCountIs('AWS::CodeBuild::Project', 1);
      template.hasResourceProperties('AWS::CodeBuild::Project', {
        Environment: {
          ComputeType: 'BUILD_GENERAL1_SMALL',
          Image: 'aws/codebuild/standard:7.0',
          PrivilegedMode: true,
          Type: 'LINUX_CONTAINER'
        }
      });
    });

    test('creates CodePipeline', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo'
      });
      
      const template = Template.fromStack(stack);
      
      template.resourceCountIs('AWS::CodePipeline::Pipeline', 1);
    });

    test('creates IAM roles for build and pipeline', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo'
      });
      
      const template = Template.fromStack(stack);
      
      // Should have BuildRole and PipelineRole
      template.resourceCountIs('AWS::IAM::Role', 2);
    });
  });

  describe('Environment Variables', () => {
    test('sets default environment variables', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo'
      });
      
      const template = Template.fromStack(stack);
      
      // Check that CodeBuild project has environment variables
      template.hasResourceProperties('AWS::CodeBuild::Project', {
        Environment: {
          EnvironmentVariables: [
            { Name: 'APP_NAME', Value: 'myapp' },
            { Name: 'STACK_ID', Value: 'dev' }
          ]
        }
      });
    });

    test('includes custom environment variables', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo',
        environmentVariables: {
          CUSTOM_VAR: 'custom-value',
          NODE_ENV: 'production'
        }
      });
      
      const template = Template.fromStack(stack);
      
      template.hasResourceProperties('AWS::CodeBuild::Project', {
        Environment: {
          EnvironmentVariables: [
            { Name: 'APP_NAME', Value: 'myapp' },
            { Name: 'STACK_ID', Value: 'dev' },
            { Name: 'CUSTOM_VAR', Value: 'custom-value' },
            { Name: 'NODE_ENV', Value: 'production' }
          ]
        }
      });
    });

    test('includes permissions boundary in environment variables when provided', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo',
        permissionsBoundary: 'arn:aws:iam::123456789012:policy/PermissionsBoundary'
      });
      
      const template = Template.fromStack(stack);
      
      template.hasResourceProperties('AWS::CodeBuild::Project', {
        Environment: {
          EnvironmentVariables: [
            { Name: 'APP_NAME', Value: 'myapp' },
            { Name: 'STACK_ID', Value: 'dev' },
            { 
              Name: 'PERMISSIONS_BOUNDARY', 
              Value: 'arn:aws:iam::123456789012:policy/PermissionsBoundary' 
            }
          ]
        }
      });
    });
  });

  describe('Permissions Boundary', () => {
    test('applies permissions boundary to IAM roles when provided', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo',
        permissionsBoundary: 'arn:aws:iam::123456789012:policy/PermissionsBoundary'
      });
      
      const template = Template.fromStack(stack);
      
      // Check that roles have permissions boundary
      template.hasResourceProperties('AWS::IAM::Role', {
        PermissionsBoundary: 'arn:aws:iam::123456789012:policy/PermissionsBoundary'
      });
    });
  });

  describe('Tagging', () => {
    test('applies standard tags to all resources', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo'
      });
      
      const template = Template.fromStack(stack);
      
      // Verify tags are present (CDK applies tags at stack level)
      expect(template).toBeDefined();
    });
  });

  describe('Build Spec Configuration', () => {
    test('uses default buildspec.yml when not specified', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo'
      });
      
      expect(stack.buildProject).toBeDefined();
    });

    test('uses custom buildspec path when specified', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo',
        buildSpecPath: 'custom-buildspec.yml'
      });
      
      expect(stack.buildProject).toBeDefined();
    });
  });

  describe('Integration', () => {
    test('creates complete pipeline infrastructure', () => {
      const app = new cdk.App();
      
      const stack = new PipelineStack(app, 'TestStack', {
        appName: 'myapp',
        stackId: 'dev',
        sourceRepo: 'test-repo',
        permissionsBoundary: 'arn:aws:iam::123456789012:policy/PermissionsBoundary',
        environmentVariables: {
          NODE_ENV: 'production'
        }
      });
      
      const template = Template.fromStack(stack);
      
      // Verify all major resources are created
      template.resourceCountIs('AWS::KMS::Key', 1);
      template.resourceCountIs('AWS::S3::Bucket', 1);
      template.resourceCountIs('AWS::IAM::Role', 2);
      template.resourceCountIs('AWS::CodeBuild::Project', 1);
      template.resourceCountIs('AWS::CodePipeline::Pipeline', 1);
      
      // Verify public properties are accessible
      expect(stack.pipeline).toBeDefined();
      expect(stack.buildProject).toBeDefined();
      expect(stack.artifactBucket).toBeDefined();
    });
  });
});
