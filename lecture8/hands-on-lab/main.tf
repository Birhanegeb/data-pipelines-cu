# Lecture 8 Hands-on Lab: Baseline Infrastructure for Data Pipelines
# Deploys S3 buckets (raw, staged, curated) and optionally a database.
# Uses for_each and modules concepts from Chapters 4-5.

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

# -----------------------------------------------------------------------------
# S3 Buckets for data pipeline stages (raw, staged, curated)
# -----------------------------------------------------------------------------

resource "aws_s3_bucket" "pipeline" {
  for_each = toset(var.bucket_suffixes)

  bucket = "${var.project}-${var.env}-${each.key}"
}

resource "aws_s3_bucket_versioning" "pipeline" {
  for_each = aws_s3_bucket.pipeline

  bucket = each.value.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "pipeline" {
  for_each = aws_s3_bucket.pipeline

  bucket = each.value.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# -----------------------------------------------------------------------------
# RDS PostgreSQL (optional - set create_database = true to enable)
# -----------------------------------------------------------------------------

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

resource "aws_security_group" "rds" {
  count = var.create_database ? 1 : 0

  name        = "${var.project}-${var.env}-rds-sg"
  description = "Allow inbound PostgreSQL from VPC"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.default.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "main" {
  count = var.create_database ? 1 : 0

  name       = "${var.project}-${var.env}-db-subnet"
  subnet_ids = data.aws_subnets.default.ids
}

resource "aws_db_instance" "main" {
  count = var.create_database ? 1 : 0

  identifier     = "${var.project}-${var.env}-pipeline-db"
  engine         = "postgres"
  engine_version = "15"
  instance_class = var.db_instance_class

  allocated_storage     = 20
  max_allocated_storage = 100

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main[0].name
  vpc_security_group_ids = [aws_security_group.rds[0].id]
  publicly_accessible    = false
  skip_final_snapshot    = var.env != "prod"

  tags = {
    Project = var.project
    Env     = var.env
  }
}
