# Lecture 9 assignment files

| File | Description |
|------|-------------|
| **`hello-world.nomad.hcl`** | **Default:** `batch` + **Docker** `busybox` — works on **macOS** and **Linux**. |
| **`hello-world-exec.nomad.hcl`** | **Linux only:** `exec` + `/bin/echo` (no Docker). Fails on macOS (`missing drivers`). |
| **`nginx-web.nomad.hcl`** | Optional: nginx service on port **8080**. |

```bash
export NOMAD_ADDR=http://localhost:4646
nomad job run assignment/hello-world.nomad.hcl
nomad job status hello-world
nomad alloc logs <alloc-id> hello
```

See **../LECTURE9_ASSIGNMENT_README.md**.
