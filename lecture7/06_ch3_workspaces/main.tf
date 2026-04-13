# Chapter 3: How to Manage Terraform State – Workspaces
# Instance type depends on terraform.workspace (default = t2.medium, others = t2.micro).

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

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "example" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = terraform.workspace == "default" ? "t2.medium" : "t2.micro"

  tags = {
    Name = "lecture7-ch3-workspace-${terraform.workspace}"
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

output "workspace" {
  value = terraform.workspace
}

output "instance_id" {
  value = aws_instance.example.id
}

output "instance_type" {
  value = aws_instance.example.instance_type
}
