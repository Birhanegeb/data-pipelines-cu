variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project name (used in resource naming)"
  type        = string
  default     = "data-pipeline"
}

variable "env" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "bucket_suffixes" {
  description = "S3 bucket suffixes for pipeline stages"
  type        = list(string)
  default     = ["raw", "staged", "curated"]
}

# Database (optional)
variable "create_database" {
  description = "Whether to create RDS PostgreSQL instance"
  type        = bool
  default     = false
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "pipelinedb"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "pipelineadmin"
}

variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
  default     = "" # Set via TF_VAR_db_password or -var="db_password=..."
}
