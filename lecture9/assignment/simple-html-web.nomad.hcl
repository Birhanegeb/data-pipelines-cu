# Lecture 9 — Static HTML via Python (no Docker)
# Uses raw_exec + python3 -m http.server. Requires raw_exec enabled and Python 3 on the client.
# If python3 is not at /usr/bin/python3 (e.g. Homebrew), change the path in config below.
# Keep cpu tiny: some dev clients (notably darwin) report low cpu.totalcompute (~48 MHz units);
# requesting more than that makes placement fail with "Dimension cpu exhausted".

job "simple-html-web" {
  type = "service"

  group "web" {
    count = 1

    network {
      port "http" {
        static = 8080
      }
    }

    task "http" {
      driver = "raw_exec"

      template {
        data = <<-EOH
          <!DOCTYPE html>
          <html>
          <head><title>Lecture 9 – Nomad</title></head>
          <body>
            <h1>Hello from Nomad</h1>
            <p>Simple static page served without Docker (Python <code>http.server</code>).</p>
          </body>
          </html>
        EOH
        destination = "local/index.html"
      }

      config {
        command = "/bin/bash"
        # Serve ./local (relative to task dir). Using $NOMAD_TASK_DIR in -c can be empty with
        # raw_exec, which made --directory wrong and Python return 404 for GET /.
        args = [
          "-c",
          "exec /usr/bin/python3 -m http.server 8090 --bind 0.0.0.0 --directory local",
        ]
      }

      resources {
        cpu    = 1
        memory = 64
      }
    }
  }
}
