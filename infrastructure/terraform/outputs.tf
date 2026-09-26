output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "artifact_bucket_name" {
  value = aws_s3_bucket.artifacts.bucket
}

output "workflow_state_table_name" {
  value = aws_dynamodb_table.workflow_state.name
}
