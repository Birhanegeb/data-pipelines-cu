# Lecture 10 — Ollama on Nomad (simplified from HashiCorp AI workloads tutorial)
# - ollama-task: Docker ollama/ollama + Nomad service ollama-backend
# - pull-model: poststart exec curls /api/pull (tinyllama by default; switch to granite3.3:2b if you have RAM)

job "ollama" {
  type = "service"

  group "ollama" {
    count = 1

    network {
      port "ollama" {
        to     = 11434
        static = 11434
      }
    }

    task "ollama-task" {
      driver = "docker"

      service {
        name     = "ollama-backend"
        port     = "ollama"
        provider = "nomad"
      }

      config {
        image = "ollama/ollama:latest"
        ports = ["ollama"]
      }

      # Lower CPU helps single-node dev agents; raise for production / larger models.
      resources {
        cpu    = 1500
        memory = 4096
      }
    }

    task "pull-model" {
      driver = "exec"

      lifecycle {
        hook    = "poststart"
        sidecar = false
      }

      resources {
        cpu    = 50
        memory = 256
      }

      template {
        data = <<EOH
{{ range nomadService "ollama-backend" }}
OLLAMA_BASE_URL=http://{{ .Address }}:{{ .Port }}
{{ end }}
EOH
        destination = "secrets/env.env"
        env         = true
      }

      config {
        command = "/bin/bash"
        args = [
          "-c",
          <<-SCRIPT
            set -e
            echo "Waiting for Ollama at $OLLAMA_BASE_URL ..."
            for i in {1..60}; do
              if curl -sf "$OLLAMA_BASE_URL/api/tags" >/dev/null 2>&1; then
                break
              fi
              sleep 2
            done
            echo "Pulling model (switch to granite3.3:2b in jobspec if you have enough RAM) ..."
            curl -sS -X POST "$OLLAMA_BASE_URL/api/pull" -d '{"name":"tinyllama"}'
            echo "Done."
          SCRIPT
        ]
      }
    }
  }
}
