#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ApplicationStack } from '../lib/cdk-code-stack';

const appTst = new cdk.App();

function getRequiredEnvVar(name: string): string {
  const value = process.env[name];
  if (!value) {
      throw new Error(`Required environment variable ${name} is not set`);
  }
  return value;
}
const app_name = getRequiredEnvVar('APP_NAME');
const stack_id = getRequiredEnvVar('STACK_ID');
const qualifier = app_name.toLowerCase();

const appDefaultSynthesizerApp = new cdk.DefaultStackSynthesizer({
  bucketPrefix: cdk.DefaultStackSynthesizer.DEFAULT_FILE_ASSET_PREFIX,
  qualifier: qualifier
});


new ApplicationStack(appTst, 'AppStack' + app_name + stack_id,{ // 'ApplicationStack' + app_name + stack_id
  synthesizer: appDefaultSynthesizerApp,
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  },
  
});

appTst.synth();
