output "bucket_ids" {
  value       = { for k, v in aws_s3_bucket.pipeline : k => v.id }
  description = "S3 bucket IDs by stage"
}

output "bucket_arns" {
  value       = { for k, v in aws_s3_bucket.pipeline : k => v.arn }
  description = "S3 bucket ARNs by stage"
}

output "db_endpoint" {
  value       = var.create_database ? aws_db_instance.main[0].endpoint : null
  description = "RDS PostgreSQL endpoint (if create_database = true)"
  sensitive   = true
}

output "db_address" {
  value       = var.create_database ? aws_db_instance.main[0].address : null
  description = "RDS host address (if create_database = true)"
}
