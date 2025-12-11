"""
Application Stack Template for Python CDK
Reusable CDK stack for application infrastructure
Version: 1.0.0
"""
import os
from typing import Dict, Any, Optional
from aws_cdk import (
    Stack,
    Tags,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_logs as logs,
    aws_ssm as ssm,
    RemovalPolicy,
    DefaultStackSynthesizer,
    Aspects,
    CfnOutput
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
            if not node.role_name:
                purpose = node.node.id.replace('Role', '').lower()
                node.role_name = f"{self.app_name}-{self.stack_id}-{purpose}-role"
            
            if self.permissions_boundary:
                node.permissions_boundary = iam.ManagedPolicy.from_managed_policy_arn(
                    node, "PermissionsBoundary", self.permissions_boundary
                )


class ApplicationStack(Stack):
    """
    Reusable Application Stack for CDK applications
    Creates common application infrastructure components
    """
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        app_name: str,
        stack_id: str,
        environment_name: str = "dev",
        vpc_cidr: str = "10.0.0.0/16",
        permissions_boundary: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Initialize the Application Stack
        
        Args:
            scope: The scope in which to define this construct
            construct_id: The scoped construct ID
            app_name: Name of the application
            stack_id: Unique identifier for this stack
            environment_name: Environment name (dev, test, prod)
            vpc_cidr: CIDR block for VPC
            permissions_boundary: IAM permissions boundary ARN
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
        self.environment_name = environment_name
        self.permissions_boundary = permissions_boundary
        
        # Apply naming convention aspect
        Aspects.of(self).add(RoleNamingConventionAspect(app_name, stack_id, permissions_boundary))
        
        # Create core infrastructure
        self._create_vpc(vpc_cidr)
        self._create_security_groups()
        self._create_iam_roles()
        self._create_log_groups()
        self._create_parameter_store()
        self._create_outputs()
        self._add_tags()
    
    def _create_vpc(self, vpc_cidr: str) -> None:
        """Create VPC with public and private subnets"""
        self.vpc = ec2.Vpc(
            self,
            "VPC",
            vpc_name=f"{self.app_name}-{self.stack_id}-vpc",
            ip_addresses=ec2.IpAddresses.cidr(vpc_cidr),
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ],
            enable_dns_hostnames=True,
            enable_dns_support=True
        )
    
    def _create_security_groups(self) -> None:
        """Create security groups for different tiers"""
        self.app_security_group = ec2.SecurityGroup(
            self,
            "AppSecurityGroup",
            security_group_name=f"{self.app_name}-{self.stack_id}-app-sg",
            vpc=self.vpc,
            description="Security group for application tier",
            allow_all_outbound=True
        )
    
    def _create_iam_roles(self) -> None:
        """Create IAM roles for application components"""
        self.app_execution_role = iam.Role(
            self,
            "AppExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AmazonECSTaskExecutionRolePolicy")
            ]
        )
        
        self.app_task_role = iam.Role(
            self,
            "AppTaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        
        self.app_task_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["ssm:GetParameter", "ssm:GetParameters", "ssm:GetParametersByPath"],
                resources=[f"arn:aws:ssm:{self.region}:{self.account}:parameter/{self.app_name}/*"]
            )
        )
    
    def _create_log_groups(self) -> None:
        """Create CloudWatch log groups"""
        self.app_log_group = logs.LogGroup(
            self,
            "AppLogGroup",
            log_group_name=f"/aws/application/{self.app_name}/{self.stack_id}",
            retention=logs.RetentionDays.ONE_MONTH,
            removal_policy=RemovalPolicy.DESTROY
        )
    
    def _create_parameter_store(self) -> None:
        """Create SSM Parameter Store parameters"""
        ssm.StringParameter(
            self,
            "AppNameParameter",
            parameter_name=f"/{self.app_name}/{self.stack_id}/app-name",
            string_value=self.app_name,
            description="Application name"
        )
        
        ssm.StringParameter(
            self,
            "EnvironmentParameter",
            parameter_name=f"/{self.app_name}/{self.stack_id}/environment",
            string_value=self.environment_name,
            description="Environment name"
        )
        
        ssm.StringParameter(
            self,
            "VpcIdParameter",
            parameter_name=f"/{self.app_name}/{self.stack_id}/vpc-id",
            string_value=self.vpc.vpc_id,
            description="VPC ID"
        )
    
    def _create_outputs(self) -> None:
        """Create CloudFormation outputs"""
        CfnOutput(
            self,
            "VpcId",
            value=self.vpc.vpc_id,
            description="VPC ID",
            export_name=f"{self.app_name}-{self.stack_id}-vpc-id"
        )
        
        CfnOutput(
            self,
            "AppSecurityGroupId",
            value=self.app_security_group.security_group_id,
            description="Application Security Group ID",
            export_name=f"{self.app_name}-{self.stack_id}-app-sg-id"
        )
    
    def _add_tags(self) -> None:
        """Add tags to all resources"""
        tags = {
            "Application": self.app_name,
            "StackId": self.stack_id,
            "Environment": self.environment_name,
            "ManagedBy": "CDK",
            "Framework": "Pipeline-Design-Framework"
        }
        
        for key, value in tags.items():
            Tags.of(self).add(key, value)
