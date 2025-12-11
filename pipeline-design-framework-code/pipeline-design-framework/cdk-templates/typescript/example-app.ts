#!/usr/bin/env node
/**
 * Example CDK Application using TypeScript PipelineStack
 * This demonstrates how to use the PipelineStack template
 */

import * as cdk from 'aws-cdk-lib';
import { PipelineStack } from './pipeline-stack';

const app = new cdk.App();

// Get configuration from environment variables or context
const appName = process.env.APP_NAME || app.node.tryGetContext('appName');
const stackId = process.env.STACK_ID || app.node.tryGetContext('stackId');
const permissionsBoundary = process.env.PERMISSIONS_BOUNDARY || app.node.tryGetContext('permissionsBoundary');

if (!appName) {
  throw new Error('APP_NAME environment variable or context is required');
}

if (!stackId) {
  throw new Error('STACK_ID environment variable or context is required');
}

// Create the pipeline stack
new PipelineStack(app, 'PipelineStack', {
  appName: appName,
  stackId: stackId,
  sourceRepo: 'my-application-repo',
  sourceBranch: 'main',
  buildSpecPath: 'buildspec.yml',
  permissionsBoundary: permissionsBoundary,
  environmentVariables: {
    // Add any additional environment variables needed for your build
    NODE_ENV: 'production',
    BUILD_VERSION: '1.0.0'
  },
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'us-west-2'
  },
  description: `Pipeline infrastructure for ${appName}-${stackId}`
});

app.synth();
