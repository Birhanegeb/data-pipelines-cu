# Lecture 10 — Open WebUI → Ollama (simplified; no S3 / nomadVar)
# Run AFTER job "ollama" is healthy. HashiCorp full tutorial adds S3 + Nomad Variables from Terraform.

job "open-webui" {
  type = "service"

  group "web" {
    count = 1

    network {
      port "ui" {
        to     = 8080
        static = 3000
      }
    }

    task "open-webui-task" {
      driver = "docker"

      service {
        name     = "open-webui-svc"
        port     = "ui"
        provider = "nomad"

        check {
          type     = "http"
          path     = "/"
          interval = "20s"
          timeout  = "5s"
        }
      }

      config {
        image = "ghcr.io/open-webui/open-webui:main"
        ports = ["ui"]
      }

      template {
        data = <<EOH
OLLAMA_BASE_URL={{ range nomadService "ollama-backend" }}http://{{ .Address }}:{{ .Port }}{{ end }}
WEBUI_SECRET_KEY=lecture10-dev-change-me
ENABLE_SIGNUP=True
EOH
        destination = "secrets/env.env"
        env         = true
      }

      # Reduced for laptops; increase if the UI is sluggish.
      resources {
        cpu    = 400
        memory = 1536
      }
    }
  }
}
