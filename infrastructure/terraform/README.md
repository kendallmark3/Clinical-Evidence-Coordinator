# AWS Prototype Terraform

This is a **starter**, not an enterprise reference architecture.

Target shape:

- ECR repository
- App Runner service
- S3 artifact bucket
- DynamoDB workflow-state table
- IAM role/policies

The application still runs locally without AWS.

## Suggested progression

1. Build and test locally.
2. Push image to ECR.
3. Deploy App Runner.
4. Add Bedrock invocation permission only when real-model testing begins.
5. Add S3/DynamoDB wiring when persistence is required.
6. Add SQS only when async workloads justify it.
