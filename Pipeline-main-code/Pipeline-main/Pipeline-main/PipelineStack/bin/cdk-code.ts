#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { PipelineStack } from '../lib/cdk-code-stack-infra';
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

const dev_cross_account = getOptionalEnvVar('DEV_ACCOUNT');
const tst_cross_account = getOptionalEnvVar('TST_ACCOUNT');
const stg_cross_account = getOptionalEnvVar('STG_ACCOUNT');
const prd_cross_account = getOptionalEnvVar('PRD_ACCOUNT');

const app_name = getRequiredEnvVar('APP_NAME');
const stack_id = getRequiredEnvVar('STACK_ID');
const app_dir = getRequiredEnvVar('APP_DIR');
const platform = getRequiredEnvVar('PLATFORM');
const permissions_boundary = getRequiredEnvVar('PERMISSIONS_BOUNDARY');
const cross_account_boundary = getRequiredEnvVar('CROSS_ACCOUNT_BOUNDARY');
const approval_notification = getRequiredEnvVar('APPROVAL_NOTIFICATION');
const action_type = getOptionalEnvVar('ACTION_TYPE');


const qualifier = app_name.toLowerCase();

const ROLE_NAME_PREFIX = 'PipelineStack' + app_name + stack_id;
const roleNamingConventionAspect = new RoleNamingConventionAspect(ROLE_NAME_PREFIX);
cdk.Aspects.of(app).add(roleNamingConventionAspect);

const appDefaultSynthesizer = new cdk.DefaultStackSynthesizer({
  bucketPrefix: cdk.DefaultStackSynthesizer.DEFAULT_FILE_ASSET_PREFIX,
  qualifier: qualifier,
});

new PipelineStack(app, 'PipelineStack'+ app_name + stack_id, { 
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: 'us-west-2',
  },
   devcrossAccountId: dev_cross_account,
   tstcrossAccountId: tst_cross_account,
   stgcrossAccountId: stg_cross_account,
   prdcrossAccountId: prd_cross_account,
   appname: app_name,
   stackid: stack_id,
   appdirectory: app_dir,
   platform: platform,
   permissionsboundary: permissions_boundary,
   synthesizer: appDefaultSynthesizer,
   crossaccountboundary: cross_account_boundary,
   approvalnotification: approval_notification,
   actiontype: action_type,
  });

app.synth();
