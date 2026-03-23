# Terraform Assignment: First Webserver (Local)
# Deploys a Docker container serving a simple HTML page on localhost:8080

terraform {
  required_version = ">= 1.0.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}

provider "docker" {}

resource "docker_image" "nginx" {
  name = "nginx:alpine"
}

resource "local_file" "index_html" {
  content = <<-HTML
    <!DOCTYPE html>
    <html>
    <head><title>My First Terraform Webserver</title></head>
    <body>
      <h1>Hello from Terraform! 3</h1>
      <p>This page was deployed using Terraform (local Docker).</p>
    </body>
    </html>
  HTML
  filename = "${path.module}/index.html"
}

resource "docker_container" "webserver" {
  image    = docker_image.nginx.image_id
  name     = "terraform-assignment-webserver"
  must_run = true

  depends_on = [local_file.index_html]

  ports {
    internal = 80
    external = 8080
  }

  volumes {
    host_path      = abspath(path.module)
    container_path = "/usr/share/nginx/html"
    read_only      = true
  }
}

output "local_url" {
  value       = "http://localhost:8080"
  description = "URL to access your deployed HTML page (local)"
}

output "container_name" {
  value       = docker_container.webserver.name
  description = "Docker container name"
}
