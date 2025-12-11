/**
 * Application Stack Template for .NET CDK
 * Reusable CDK stack template for application infrastructure
 * Version: 1.0.0
 */

using System;
using System.Collections.Generic;
using Amazon.CDK;
using Constructs;

namespace PipelineFramework
{
    /// <summary>
    /// Properties for ApplicationStack
    /// </summary>
    public class ApplicationStackProps : StackProps
    {
        public string AppName { get; set; } = string.Empty;
        public string StackId { get; set; } = string.Empty;
    }

    /// <summary>
    /// Reusable Application Stack for CDK applications
    /// Template for deploying application infrastructure
    /// </summary>
    public class ApplicationStack : Stack
    {
        public ApplicationStack(Construct scope, string id, ApplicationStackProps props) : base(scope, id, ConfigureSynthesizer(props))
        {
            // Validate required properties
            if (string.IsNullOrEmpty(props.AppName))
            {
                throw new ArgumentException("APP_NAME is required in ApplicationStackProps");
            }
            if (string.IsNullOrEmpty(props.StackId))
            {
                throw new ArgumentException("STACK_ID is required in ApplicationStackProps");
            }

            // Add standard tags
            AddTags(props.AppName, props.StackId);

            // TODO: Add your application resources here
            // Example:
            // new Function(this, "MyFunction", new FunctionProps { ... });
            // new Table(this, "MyTable", new TableProps { ... });
            // new RestApi(this, "MyApi", new RestApiProps { ... });
        }

        private static StackProps ConfigureSynthesizer(ApplicationStackProps props)
        {
            // Validate required properties
            if (string.IsNullOrEmpty(props.AppName))
            {
                throw new ArgumentException("APP_NAME is required in ApplicationStackProps");
            }
            if (string.IsNullOrEmpty(props.StackId))
            {
                throw new ArgumentException("STACK_ID is required in ApplicationStackProps");
            }

            // Configure synthesizer with custom qualifier
            var qualifier = $"{props.AppName.ToLower().Replace("-", "")}{props.StackId.ToLower().Replace("-", "")}";
            if (qualifier.Length > 10)
            {
                qualifier = qualifier.Substring(0, 10);
            }

            var synthesizer = new DefaultStackSynthesizer(new DefaultStackSynthesizerProps
            {
                Qualifier = qualifier,
                FileAssetsBucketName = $"cdk-{qualifier}-assets-${{AWS::AccountId}}-${{AWS::Region}}",
                BucketPrefix = "",
                ImageAssetsRepositoryName = $"cdk-{qualifier}-container-assets-${{AWS::AccountId}}-${{AWS::Region}}",
                CloudFormationExecutionRole = $"arn:aws:iam::${{AWS::AccountId}}:role/cdk-{qualifier}-cfn-exec-role-${{AWS::AccountId}}-${{AWS::Region}}",
                DeployRoleArn = $"arn:aws:iam::${{AWS::AccountId}}:role/cdk-{qualifier}-deploy-role-${{AWS::AccountId}}-${{AWS::Region}}",
                FileAssetPublishingRoleArn = $"arn:aws:iam::${{AWS::AccountId}}:role/cdk-{qualifier}-file-publishing-role-${{AWS::AccountId}}-${{AWS::Region}}",
                ImageAssetPublishingRoleArn = $"arn:aws:iam::${{AWS::AccountId}}:role/cdk-{qualifier}-image-publishing-role-${{AWS::AccountId}}-${{AWS::Region}}",
                LookupRoleArn = $"arn:aws:iam::${{AWS::AccountId}}:role/cdk-{qualifier}-lookup-role-${{AWS::AccountId}}-${{AWS::Region}}"
            });

            // Override stack name to follow naming convention: AppStack + app_name + stack_id
            var stackName = $"AppStack{props.AppName}{props.StackId}";

            return new StackProps
            {
                Synthesizer = synthesizer,
                StackName = stackName,
                Env = new Environment
                {
                    Account = System.Environment.GetEnvironmentVariable("CDK_DEFAULT_ACCOUNT"),
                    Region = System.Environment.GetEnvironmentVariable("CDK_DEFAULT_REGION")
                },
                Description = props.Description,
                Tags = props.Tags,
                TerminationProtection = props.TerminationProtection
            };
        }

        private void AddTags(string appName, string stackId)
        {
            var tags = new Dictionary<string, string>
            {
                ["Application"] = appName,
                ["StackId"] = stackId,
                ["Environment"] = stackId,
                ["ManagedBy"] = "CDK",
                ["Framework"] = "Pipeline-Design-Framework"
            };

            foreach (var tag in tags)
            {
                Tags.Of(this).Add(tag.Key, tag.Value);
            }
        }
    }
}
