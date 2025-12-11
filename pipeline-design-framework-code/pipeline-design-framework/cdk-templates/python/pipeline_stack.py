"""
Pipeline Stack Template for Python CDK
Reusable CDK stack for creating AWS CodePipeline infrastructure
Version: 1.0.0
"""
import os
from typing import Dict, Any, Optional
from aws_cdk import (
    Stack,
    Tags,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_codebuild as codebuild,
    aws_iam as iam,
    aws_s3 as s3,
    aws_kms as kms,
    RemovalPolicy,
    Duration,
    DefaultStackSynthesizer,
    Aspects
)
from constructs import Construct, IConstruct
import jsii


@jsii.implements(iam.IAspect)
class RoleNamingConventionAspect:
    """Aspect to enforce naming conventions and permissions boundaries on IAM roles"""
    
    def __init__(self, app_name: str, stack_id: str, permissions_boundary: Optional[str] = None):
        self.app_name = app_name
        self.stack_id = stack_id
        self.permissions_boundary = permissions_boundary
    
    def visit(self, node: IConstruct) -> None:
        if isinstance(node, iam.Role):
            # Enforce naming convention
            if not node.role_name:
                purpose = node.node.id.replace('Role', '').lower()
                node.role_name = f"{self.app_name}-{self.stack_id}-{purpose}-role"
            
            # Attach permissions boundary
            if self.permissions_boundary:
                node.permissions_boundary = iam.ManagedPolicy.from_managed_policy_arn(
                    node, "PermissionsBoundary", self.permissions_boundary
                )


class PipelineStack(Stack):
    """
    Reusable Pipeline Stack for CDK applications
    Creates CodePipeline with CodeBuild for automated deployments
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        app_name: str,
        stack_id: str,
        source_repo: str,
        source_branch: str = "main",
        build_spec_path: str = "buildspec.yml",
        permissions_boundary: Optional[str] = None,
        environment_variables: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> None:
        """
        Initialize the Pipeline Stack
        
        Args:
            scope: The scope in which to define this construct
            construct_id: The scoped construct ID
            app_name: Name of the application
            stack_id: Unique identifier for this stack
            source_repo: Source repository name
            source_branch: Source branch name (default: main)
            build_spec_path: Path to buildspec.yml file
            permissions_boundary: IAM permissions boundary ARN
            environment_variables: Additional environment variables for build
            **kwargs: Additional stack properties
        """
        # Configure synthesizer with custom qualifier
        qualifier = f"{app_name.lower().replace('-', '')}{stack_id.lower().replace('-', '')}"[:10]
        
        synthesizer = DefaultStackSynthesizer(
            qualifier=qualifier,
            file_assets_bucket_name=f"cdk-{qualifier}-assets-${{AWS::AccountId}}-${{AWS::Region}}",
            bucket_prefix="",
            image_assets_repository_name=f"cdk-{qualifier}-container-assets-${{AWS::AccountId}}-${{AWS::Region}}",
            cloud_formation_execution_role=f"arn:aws:iam::${{AWS::AccountId}}:role/cdk-{qualifier}-cfn-exec-role-${{AWS::AccountId}}-${{AWS::Region}}",
            deploy_role_arn=f"arn:aws:iam::${{AWS::AccountId}}:role/cdk-{qualifier}-deploy-role-${{AWS::AccountId}}-${{AWS::Region}}",
            file_asset_publishing_role_arn=f"arn:aws:iam::${{AWS::AccountId}}:role/cdk-{qualifier}-file-publishing-role-${{AWS::AccountId}}-${{AWS::Region}}",
            image_asset_publishing_role_arn=f"arn:aws:iam::${{AWS::AccountId}}:role/cdk-{qualifier}-image-publishing-role-${{AWS::AccountId}}-${{AWS::Region}}",
            lookup_role_arn=f"arn:aws:iam::${{AWS::AccountId}}:role/cdk-{qualifier}-lookup-role-${{AWS::AccountId}}-${{AWS::Region}}"
        )
        
        super().__init__(scope, construct_id, synthesizer=synthesizer, **kwargs)
        
        self.app_name = app_name
        self.stack_id = stack_id
        self.source_repo = source_repo
        self.source_branch = source_branch
        self.permissions_boundary = permissions_boundary
        
        # Set default environment variables
        self.environment_variables = {
            "APP_NAME": app_name,
            "STACK_ID": stack_id,
            "CDK_DEFAULT_REGION": self.region,
            **(environment_variables or {})
        }
        
        if permissions_boundary:
            self.environment_variables["PERMISSIONS_BOUNDARY"] = permissions_boundary
        
        # Apply naming convention aspect
        Aspects.of(self).add(RoleNamingConventionAspect(app_name, stack_id, permissions_boundary))
        
        # Create pipeline resources
        self._create_encryption_key()
        self._create_artifact_bucket()
        self._create_build_role()
        self._create_pipeline_role()
        self._create_build_project()
        self._create_pipeline()
        self._add_tags()
    
    def _create_encryption_key(self) -> None:
        """Create KMS key for pipeline encryption"""
        self.pipeline_key = kms.Key(
            self,
            "PipelineKey",
            description=f"KMS Key for {self.app_name}-{self.stack_id} pipeline",
            enable_key_rotation=True,
            removal_policy=RemovalPolicy.DESTROY
        )
    
    def _create_artifact_bucket(self) -> None:
        """Create S3 bucket for pipeline artifacts"""
        self.artifact_bucket = s3.Bucket(
            self,
            "ArtifactBucket",
            bucket_name=f"{self.app_name}-{self.stack_id}-pipeline-artifacts-{self.account}",
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.pipeline_key,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )
    
    def _create_build_role(self) -> None:
        """Create IAM role for CodeBuild"""
        self.build_role = iam.Role(
            self,
            "BuildRole",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("PowerUserAccess")
            ]
        )
        
        # Add CDK-specific permissions
        self.build_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "iam:CreateRole",
                    "iam:DeleteRole",
                    "iam:AttachRolePolicy",
                    "iam:DetachRolePolicy",
                    "iam:PutRolePolicy",
                    "iam:DeleteRolePolicy",
                    "iam:PassRole"
                ],
                resources=[f"arn:aws:iam::{self.account}:role/{self.app_name}-*"]
            )
        )
        
        self.pipeline_key.grant_encrypt_decrypt(self.build_role)
    
    def _create_pipeline_role(self) -> None:
        """Create IAM role for CodePipeline"""
        self.pipeline_role = iam.Role(
            self,
            "PipelineRole",
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com")
        )
        
        self.artifact_bucket.grant_read_write(self.pipeline_role)
        self.pipeline_key.grant_encrypt_decrypt(self.pipeline_role)
        
        self.pipeline_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["codebuild:BatchGetBuilds", "codebuild:StartBuild"],
                resources=[f"arn:aws:codebuild:{self.region}:{self.account}:project/{self.app_name}-*"]
            )
        )
    
    def _create_build_project(self) -> None:
        """Create CodeBuild project"""
        self.build_project = codebuild.Project(
            self,
            "BuildProject",
            project_name=f"{self.app_name}-{self.stack_id}-build",
            role=self.build_role,
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
                privileged=True
            ),
            environment_variables={
                name: codebuild.BuildEnvironmentVariable(value=value)
                for name, value in self.environment_variables.items()
            },
            timeout=Duration.hours(2),
            encryption_key=self.pipeline_key
        )
    
    def _create_pipeline(self) -> None:
        """Create CodePipeline"""
        source_output = codepipeline.Artifact("SourceOutput")
        build_output = codepipeline.Artifact("BuildOutput")
        
        # Note: Source action needs to be configured based on actual source control
        # This is a placeholder that should be customized per application
        
        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Build",
            project=self.build_project,
            input=source_output,
            outputs=[build_output]
        )
        
        self.pipeline = codepipeline.Pipeline(
            self,
            "Pipeline",
            pipeline_name=f"{self.app_name}-{self.stack_id}-pipeline",
            role=self.pipeline_role,
            artifact_bucket=self.artifact_bucket,
            encryption_key=self.pipeline_key
        )
    
    def _add_tags(self) -> None:
        """Add tags to all resources"""
        tags = {
            "Application": self.app_name,
            "StackId": self.stack_id,
            "Environment": "pipeline",
            "ManagedBy": "CDK",
            "Framework": "Pipeline-Design-Framework"
        }
        
        for key, value in tags.items():
            Tags.of(self).add(key, value)
