/**
 * Pipeline Stack Template for .NET CDK
 * Reusable CDK stack for creating AWS CodePipeline infrastructure
 * Version: 1.0.0
 */

using System;
using System.Collections.Generic;
using System.Linq;
using Amazon.CDK;
using Amazon.CDK.AWS.CodePipeline;
using Amazon.CDK.AWS.CodePipeline.Actions;
using Amazon.CDK.AWS.CodeBuild;
using Amazon.CDK.AWS.IAM;
using Amazon.CDK.AWS.S3;
using Amazon.CDK.AWS.KMS;
using Constructs;

namespace PipelineFramework
{
    /// <summary>
    /// Aspect to enforce naming conventions and permissions boundaries on IAM roles
    /// </summary>
    public class RoleNamingConventionAspect : IAspect
    {
        private readonly string _appName;
        private readonly string _stackId;
        private readonly string? _permissionsBoundary;

        public RoleNamingConventionAspect(string appName, string stackId, string? permissionsBoundary = null)
        {
            _appName = appName;
            _stackId = stackId;
            _permissionsBoundary = permissionsBoundary;
        }

        public void Visit(IConstruct node)
        {
            if (node is Role role)
            {
                // Enforce naming convention
                if (string.IsNullOrEmpty(role.RoleName))
                {
                    var purpose = node.Node.Id.Replace("Role", "").ToLower();
                    // Note: RoleName is read-only after construction, so this is set during construction
                }

                // Attach permissions boundary
                if (!string.IsNullOrEmpty(_permissionsBoundary))
                {
                    role.PermissionsBoundary = ManagedPolicy.FromManagedPolicyArn(
                        node,
                        "PermissionsBoundary",
                        _permissionsBoundary
                    );
                }
            }
        }
    }

    /// <summary>
    /// Properties for PipelineStack
    /// </summary>
    public class PipelineStackProps : StackProps
    {
        public string AppName { get; set; } = string.Empty;
        public string StackId { get; set; } = string.Empty;
        public string SourceRepo { get; set; } = string.Empty;
        public string SourceBranch { get; set; } = "main";
        public string BuildSpecPath { get; set; } = "buildspec.yml";
        public string? PermissionsBoundary { get; set; }
        public Dictionary<string, string>? EnvironmentVariables { get; set; }
    }

    /// <summary>
    /// Reusable Pipeline Stack for CDK applications
    /// Creates CodePipeline with CodeBuild for automated deployments
    /// </summary>
    public class PipelineStack : Stack
    {
        public Pipeline Pipeline { get; private set; }
        public Project BuildProject { get; private set; }
        public Bucket ArtifactBucket { get; private set; }

        private readonly string _appName;
        private readonly string _stackId;
        private readonly string _sourceRepo;
        private readonly string _sourceBranch;
        private readonly string? _permissionsBoundary;
        private readonly Dictionary<string, string> _environmentVariables;
        private Key _pipelineKey;
        private Role _buildRole;
        private Role _pipelineRole;

        public PipelineStack(Construct scope, string id, PipelineStackProps props) : base(scope, id, ConfigureSynthesizer(props))
        {
            // Validate required environment variables
            if (string.IsNullOrEmpty(props.AppName))
            {
                throw new ArgumentException("APP_NAME is required in PipelineStackProps");
            }
            if (string.IsNullOrEmpty(props.StackId))
            {
                throw new ArgumentException("STACK_ID is required in PipelineStackProps");
            }

            _appName = props.AppName;
            _stackId = props.StackId;
            _sourceRepo = props.SourceRepo;
            _sourceBranch = props.SourceBranch;
            _permissionsBoundary = props.PermissionsBoundary;

            // Set default environment variables
            _environmentVariables = new Dictionary<string, string>
            {
                ["APP_NAME"] = _appName,
                ["STACK_ID"] = _stackId,
                ["CDK_DEFAULT_REGION"] = Region
            };

            if (props.EnvironmentVariables != null)
            {
                foreach (var kvp in props.EnvironmentVariables)
                {
                    _environmentVariables[kvp.Key] = kvp.Value;
                }
            }

            if (!string.IsNullOrEmpty(_permissionsBoundary))
            {
                _environmentVariables["PERMISSIONS_BOUNDARY"] = _permissionsBoundary;
            }

            // Apply naming convention aspect
            Aspects.Of(this).Add(new RoleNamingConventionAspect(_appName, _stackId, _permissionsBoundary));

            // Create pipeline resources
            CreateEncryptionKey();
            ArtifactBucket = CreateArtifactBucket();
            _buildRole = CreateBuildRole();
            _pipelineRole = CreatePipelineRole();
            BuildProject = CreateBuildProject(props.BuildSpecPath);
            Pipeline = CreatePipeline();
            AddTags();
        }

        private static StackProps ConfigureSynthesizer(PipelineStackProps props)
        {
            // Validate required properties
            if (string.IsNullOrEmpty(props.AppName))
            {
                throw new ArgumentException("APP_NAME is required in PipelineStackProps");
            }
            if (string.IsNullOrEmpty(props.StackId))
            {
                throw new ArgumentException("STACK_ID is required in PipelineStackProps");
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

            // Override stack name to follow naming convention: PipelineStack + app_name + stack_id
            var stackName = $"PipelineStack{props.AppName}{props.StackId}";

            return new StackProps
            {
                Synthesizer = synthesizer,
                StackName = stackName,
                Env = props.Env,
                Description = props.Description,
                Tags = props.Tags,
                TerminationProtection = props.TerminationProtection
            };
        }

        private void CreateEncryptionKey()
        {
            _pipelineKey = new Key(this, "PipelineKey", new KeyProps
            {
                Description = $"KMS Key for {_appName}-{_stackId} pipeline",
                EnableKeyRotation = true,
                RemovalPolicy = RemovalPolicy.DESTROY
            });
        }

        private Bucket CreateArtifactBucket()
        {
            return new Bucket(this, "ArtifactBucket", new BucketProps
            {
                BucketName = $"{_appName}-{_stackId}-pipeline-artifacts-{Account}",
                Encryption = BucketEncryption.KMS,
                EncryptionKey = _pipelineKey,
                Versioned = true,
                BlockPublicAccess = BlockPublicAccess.BLOCK_ALL,
                RemovalPolicy = RemovalPolicy.DESTROY,
                AutoDeleteObjects = true
            });
        }

        private Role CreateBuildRole()
        {
            var role = new Role(this, "BuildRole", new RoleProps
            {
                RoleName = $"{_appName}-{_stackId}-build-role",
                AssumedBy = new ServicePrincipal("codebuild.amazonaws.com"),
                ManagedPolicies = new[]
                {
                    ManagedPolicy.FromAwsManagedPolicyName("PowerUserAccess")
                }
            });

            // Add CDK-specific permissions
            role.AddToPolicy(new PolicyStatement(new PolicyStatementProps
            {
                Effect = Effect.ALLOW,
                Actions = new[]
                {
                    "iam:CreateRole",
                    "iam:DeleteRole",
                    "iam:AttachRolePolicy",
                    "iam:DetachRolePolicy",
                    "iam:PutRolePolicy",
                    "iam:DeleteRolePolicy",
                    "iam:PassRole"
                },
                Resources = new[] { $"arn:aws:iam::{Account}:role/{_appName}-*" }
            }));

            _pipelineKey.GrantEncryptDecrypt(role);

            return role;
        }

        private Role CreatePipelineRole()
        {
            var role = new Role(this, "PipelineRole", new RoleProps
            {
                RoleName = $"{_appName}-{_stackId}-pipeline-role",
                AssumedBy = new ServicePrincipal("codepipeline.amazonaws.com")
            });

            ArtifactBucket.GrantReadWrite(role);
            _pipelineKey.GrantEncryptDecrypt(role);

            role.AddToPolicy(new PolicyStatement(new PolicyStatementProps
            {
                Effect = Effect.ALLOW,
                Actions = new[] { "codebuild:BatchGetBuilds", "codebuild:StartBuild" },
                Resources = new[] { $"arn:aws:codebuild:{Region}:{Account}:project/{_appName}-*" }
            }));

            return role;
        }

        private Project CreateBuildProject(string buildSpecPath)
        {
            var envVars = _environmentVariables.ToDictionary(
                kvp => kvp.Key,
                kvp => new BuildEnvironmentVariable { Value = kvp.Value }
            );

            return new Project(this, "BuildProject", new ProjectProps
            {
                ProjectName = $"{_appName}-{_stackId}-build",
                Role = _buildRole,
                Environment = new BuildEnvironment
                {
                    BuildImage = LinuxBuildImage.STANDARD_7_0,
                    ComputeType = ComputeType.SMALL,
                    Privileged = true
                },
                EnvironmentVariables = envVars,
                BuildSpec = !string.IsNullOrEmpty(buildSpecPath)
                    ? BuildSpec.FromSourceFilename(buildSpecPath)
                    : BuildSpec.FromSourceFilename("buildspec.yml"),
                Timeout = Duration.Hours(2),
                EncryptionKey = _pipelineKey
            });
        }

        private Pipeline CreatePipeline()
        {
            var sourceOutput = new Artifact_("SourceOutput");
            var buildOutput = new Artifact_("BuildOutput");

            var buildAction = new CodeBuildAction(new CodeBuildActionProps
            {
                ActionName = "Build",
                Project = BuildProject,
                Input = sourceOutput,
                Outputs = new[] { buildOutput }
            });

            return new Pipeline(this, "Pipeline", new PipelineProps
            {
                PipelineName = $"{_appName}-{_stackId}-pipeline",
                Role = _pipelineRole,
                ArtifactBucket = ArtifactBucket,
                EncryptionKey = _pipelineKey
            });
        }

        private void AddTags()
        {
            var tags = new Dictionary<string, string>
            {
                ["Application"] = _appName,
                ["StackId"] = _stackId,
                ["Environment"] = "pipeline",
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
