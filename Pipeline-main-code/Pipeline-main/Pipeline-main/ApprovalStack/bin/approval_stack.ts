#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ApprovalStack } from '../lib/approval_stack-stack';
import { RoleNamingConventionAspect } from '../lib/aspects';

const app = new cdk.App();

function getRequiredEnvVar(name: string): string {
  const value = process.env[name];
  if (!value) {
      throw new Error(`Required environment variable ${name} is not set`);
  }
  return value;
}

 function getOptionalEnvVar(name: string): string {
  const value = process.env[name];
  return value ? value : '';
}

const app_name = getRequiredEnvVar('APP_NAME');
const stack_id = getRequiredEnvVar('STACK_ID');
const permissions_boundary = getRequiredEnvVar('PERMISSIONS_BOUNDARY');
const approval_notification = getRequiredEnvVar('APPROVAL_NOTIFICATION');
const qualifier = app_name.toLowerCase();

const ROLE_NAME_PREFIX = 'ApprovalStack' + app_name + stack_id;
const roleNamingConventionAspect = new RoleNamingConventionAspect(ROLE_NAME_PREFIX);
cdk.Aspects.of(app).add(roleNamingConventionAspect);

const appDefaultSynthesizer = new cdk.DefaultStackSynthesizer({
  bucketPrefix: cdk.DefaultStackSynthesizer.DEFAULT_FILE_ASSET_PREFIX,
  qualifier: qualifier,
});

new ApprovalStack(app, 'ApprovalStack'+ app_name + stack_id, {
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION 
  },
  pipelineName: 'PipelineStack'+ app_name + stack_id || 'MyPipeline',
  approvalNotification: (approval_notification || '').split(',').filter(Boolean),
  permissionsboundary: permissions_boundary,
  appname: app_name,
  stackid: stack_id,
  synthesizer: appDefaultSynthesizer,
});
