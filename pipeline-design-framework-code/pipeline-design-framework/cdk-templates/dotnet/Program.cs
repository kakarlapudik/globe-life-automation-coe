#!/usr/bin/env dotnet run
/**
 * Example CDK Application using .NET PipelineStack
 * This demonstrates how to use the PipelineStack template
 */

using System;
using System.Collections.Generic;
using Amazon.CDK;
using PipelineFramework;

namespace ExampleApp
{
    sealed class Program
    {
        public static void Main(string[] args)
        {
            var app = new App();

            // Get configuration from environment variables or context
            var appName = Environment.GetEnvironmentVariable("APP_NAME") 
                ?? app.Node.TryGetContext("appName")?.ToString();
            var stackId = Environment.GetEnvironmentVariable("STACK_ID") 
                ?? app.Node.TryGetContext("stackId")?.ToString();
            var permissionsBoundary = Environment.GetEnvironmentVariable("PERMISSIONS_BOUNDARY") 
                ?? app.Node.TryGetContext("permissionsBoundary")?.ToString();

            if (string.IsNullOrEmpty(appName))
            {
                throw new ArgumentException("APP_NAME environment variable or context is required");
            }

            if (string.IsNullOrEmpty(stackId))
            {
                throw new ArgumentException("STACK_ID environment variable or context is required");
            }

            // Create the pipeline stack
            new PipelineStack(app, "PipelineStack", new PipelineStackProps
            {
                AppName = appName,
                StackId = stackId,
                SourceRepo = "my-application-repo",
                SourceBranch = "main",
                BuildSpecPath = "buildspec.yml",
                PermissionsBoundary = permissionsBoundary,
                EnvironmentVariables = new Dictionary<string, string>
                {
                    // Add any additional environment variables needed for your build
                    ["DOTNET_VERSION"] = "6.0",
                    ["BUILD_CONFIGURATION"] = "Release"
                },
                Env = new Environment
                {
                    Account = Environment.GetEnvironmentVariable("CDK_DEFAULT_ACCOUNT"),
                    Region = Environment.GetEnvironmentVariable("CDK_DEFAULT_REGION") ?? "us-west-2"
                },
                Description = $"Pipeline infrastructure for {appName}-{stackId}"
            });

            app.Synth();
        }
    }
}
