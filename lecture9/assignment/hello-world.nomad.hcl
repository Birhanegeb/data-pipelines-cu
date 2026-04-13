# Lecture 9 — Hello world (works on macOS + Linux)
# The "exec" driver is Linux-only; Docker+busybox runs on macOS dev agents too.

job "hello-world" {
  type = "batch"

  group "app" {
    count = 1

    task "hello" {
      driver = "docker"

      config {
        image   = "busybox:stable"
        command = "sh"
        args    = ["-c", "echo 'Hello, world from Nomad!'"]
      }

      # cpu=1 is Nomad’s minimum (MHz); keeps CPU reservation tiny on crowded dev agents.
      # memory 64 MB — enough for busybox; minimum allowed is 10.
      resources {
        cpu    = 1
        memory = 64
      }
    }
  }
}
