# Lecture 9 — Simple Nomad service job (Docker nginx)
# Parallels Lecture 6: nginx serving a minimal HTML page on host port 8080.

job "nginx-web" {
  type = "service"

  group "web" {
    count = 1

    network {
      port "http" {
        static = 8080
        to     = 80
      }
    }

    task "nginx" {
      driver = "docker"

      # Small explicit reservation helps placement on dev agents and avoids competing with other jobs.
      resources {
        cpu    = 200
        memory = 256
      }

      template {
        data = <<-EOH
          <!DOCTYPE html>
          <html>
          <head><title>Lecture 9 – Nomad</title></head>
          <body>
            <h1>Hello from Nomad</h1>
            <p>This nginx task is scheduled by Nomad (Docker driver).</p>
            <p>Compare with Lecture 6: Terraform docker_container + nginx.</p>
          </body>
          </html>
        EOH
        destination = "local/index.html"
      }

      config {
        image = "nginx:alpine"
        ports = ["http"]
        volumes = [
          "local/index.html:/usr/share/nginx/html/index.html:ro",
        ]
      }
    }
  }
}
