#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ApplicationStack } from '../lib/cdk-code-stack';

// Initialize CDK application instance
const app = new cdk.App();

/**
 * Utility function to safely retrieve required environment variables
 * Throws an error if the environment variable is not set, ensuring fail-fast behavior
 * @param name - Name of the environment variable to retrieve
 * @returns The environment variable value
 * @throws Error if the environment variable is not set or empty
 */
function getRequiredEnvVar(name: string): string {
  const value = process.env[name];
  if (!value) {
      throw new Error(`Required environment variable ${name} is not set`);
  }
  return value;
}

// Retrieve required environment variables for stack configuration
const app_name = getRequiredEnvVar('APP_NAME');     // Application identifier (max 10 chars)
const stack_id = getRequiredEnvVar('STACK_ID');     // Stack identifier (max 10 chars)
const qualifier = app_name.toLowerCase();           // CDK qualifier must be lowercase

// Configure CDK synthesizer with custom qualifier for asset management
// This ensures assets are stored in buckets/roles specific to this application
const appDefaultSynthesizerApp = new cdk.DefaultStackSynthesizer({
  bucketPrefix: cdk.DefaultStackSynthesizer.DEFAULT_FILE_ASSET_PREFIX, // Standard CDK prefix
  qualifier: qualifier // Custom qualifier based on app name for isolation
});


// Create the main application stack with standardized naming convention
// Stack name format: AppStack + APP_NAME + STACK_ID (e.g., AppStack AppGL ApiGL)
new ApplicationStack(app, 'AppStack' + app_name + stack_id, {
  synthesizer: appDefaultSynthesizerApp,  // Custom synthesizer for asset isolation
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT, // Target AWS account ID
    region: process.env.CDK_DEFAULT_REGION,   // Target AWS region
  },
});

// Synthesize the CDK application to CloudFormation templates
app.synth();
