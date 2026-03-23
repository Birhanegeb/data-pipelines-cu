# Chapter 3: How to Manage Terraform State – Remote Backend
# Creates S3 bucket + DynamoDB table for Terraform state and locking.
# Use this once; then point other configs' backend to this bucket/table.

terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 bucket for state files
resource "aws_s3_bucket" "terraform_state" {
  bucket = var.bucket_name

  # Allow destroy for learning; set to false in production
  force_destroy = true
}

# Versioning so you can recover previous state
resource "aws_s3_bucket_versioning" "enabled" {
  bucket = aws_s3_bucket.terraform_state.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Encrypt state at rest
resource "aws_s3_bucket_server_side_encryption_configuration" "default" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "public_access" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# DynamoDB table for state locking (prevents concurrent apply)
resource "aws_dynamodb_table" "terraform_locks" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "bucket_name" {
  description = "S3 bucket name; must be globally unique"
  type        = string
}

variable "table_name" {
  description = "DynamoDB table name for locks"
  type        = string
}

output "s3_bucket_arn" {
  value = aws_s3_bucket.terraform_state.arn
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.terraform_locks.name
}

output "backend_config" {
  description = "Add this to your other Terraform configs to use remote state"
  value = <<-EOT
    backend "s3" {
      bucket         = "${aws_s3_bucket.terraform_state.id}"
      key            = "some/path/terraform.tfstate"
      region         = "${var.aws_region}"
      dynamodb_table = "${aws_dynamodb_table.terraform_locks.name}"
      encrypt        = true
    }
  EOT
}
