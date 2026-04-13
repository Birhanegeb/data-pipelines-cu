# Lecture 9: Nomad Assignment — Hello World

Run a **Nomad development cluster** and submit a **minimal batch job** that prints **`Hello, world from Nomad!`**.

## Objectives

1. Install the **Nomad CLI** (≥ 1.5) and verify with `nomad -v`.
2. Start a **local dev agent** (or use a cluster with `NOMAD_ADDR` set).
3. Submit **`assignment/hello-world.nomad.hcl`** with `nomad job run`.
4. Confirm the job **completed** and read the task output from **allocation logs**.
5. Clean up with `nomad job stop -purge` (optional for batch; job may already be terminal).

## Prerequisites

- **Nomad** ≥ 1.5
- **Docker** running (for **`hello-world.nomad.hcl`**)
- **Linux-only, no Docker:** use **`hello-world-exec.nomad.hcl`** instead (`exec` + `/bin/echo`)

## Steps

### 1. Start the dev agent

**macOS + Docker Desktop:** `nomad agent -dev` stores allocations under **`/private/tmp/NomadClient…`**. Docker often **cannot** create bind mounts there → **`permission denied`** / `host_mnt/private/tmp/NomadClient`. **`sudo` alone does not fix this**; you must set **`-data-dir`** to a folder under **`/Users/you/...`** (Docker shares `/Users` by default).

**Easiest (from `lecture9/`):**

```bash
chmod +x nomad-dev-macos.sh
./nomad-dev-macos.sh
```

**Same thing manually** (`$HOME` expands *before* `sudo`, so the path stays under your home):

```bash
mkdir -p "$HOME/nomad-dev-data"
sudo nomad agent -dev \
  -data-dir="$HOME/nomad-dev-data" \
  -bind 0.0.0.0 \
  -network-interface='{{ GetDefaultInterfaces | attr "name" }}'
```

**Linux:** plain dev agent is usually fine:

```bash
sudo nomad agent -dev \
  -bind 0.0.0.0 \
  -network-interface='{{ GetDefaultInterfaces | attr "name" }}'
```

Terminal B:

```bash
export NOMAD_ADDR=http://localhost:4646
nomad node status
```

### 2. Run the job

```bash
cd lecture9
nomad job run assignment/hello-world.nomad.hcl
```

### 3. See “Hello, world”

```bash
nomad job status hello-world
# Note the Allocation ID from the job status, then:
nomad alloc logs <allocation-id> hello
```

You should see: **`Hello, world from Nomad!`**

You can also open **http://localhost:4646/ui** → job **hello-world** → allocation → **Logs**.

### 4. Clean up

```bash
nomad job stop -purge hello-world
```

Stop the dev agent with **Ctrl+C** in the first terminal.

## Troubleshooting: `Resources exhausted` / `Dimension "cpu" exhausted`

The dev client only has so much **allocatable** CPU. Other jobs (Ollama, Open WebUI, nginx, Pytechco, etc.) can use it all — even **100 MHz** may not fit.

1. **List and purge everything** (repeat until `nomad job status` is empty or only shows stopped jobs):

   ```bash
   nomad job status
   nomad job stop -purge <each-running-job-id>
   ```

2. **Garbage-collect** old allocations:

   ```bash
   nomad system gc
   ```

3. **Restart the dev agent** (Ctrl+C, then start `nomad agent -dev ...` again).

4. Run **`hello-world`** again. The jobspec uses **`cpu = 1`** (Nomad minimum MHz) and **`memory = 64`**.

If it **still** fails, check how much CPU the node exposes:

```bash
nomad node status -verbose
```

Look for **CPU** / resources on your client — if another process outside Nomad is pinning the machine, close it or reboot.

### `Constraint "missing drivers"` / `exec` on macOS

Use **`hello-world.nomad.hcl`** (Docker + busybox). Do **not** use **`hello-world-exec.nomad.hcl`** on macOS — the **`exec`** driver is **Linux-only**.

### Docker: `permission denied` / `host_mnt/private/tmp/NomadClient` (macOS)

Default **`-dev`** uses **`/private/tmp`**. Docker Desktop cannot reliably **`mkdir`** there for mounts. **Use `-data-dir` under your home** (see step 1): run **`./nomad-dev-macos.sh`** or **`sudo nomad agent -dev -data-dir="$HOME/nomad-dev-data" ...`**.

Then **`nomad job stop -purge hello-world`**, restart the agent with the new flags, and run the job again.

In Docker Desktop → **Settings → Resources → File sharing**, ensure **`/Users`** is allowed (default on recent versions).

You can still run **`nomad job run`** as your normal user.

## How to Submit

1. **Screenshot** of **Nomad UI** showing job **hello-world** completed (or terminal showing `nomad alloc logs` with the hello line).
2. **Pull Request** with the screenshot (and your jobspec if you changed it).

### PR title example

```
Lecture 9: Nomad hello-world - [Your Name]
```

## Extension (optional)

- **`assignment/nginx-web.nomad.hcl`** — Docker **nginx** service on port **8080** (like Lecture 6); requires **Docker**.
- Official **Pytechco** tutorial: [learn-nomad-getting-started](https://github.com/hashicorp-education/learn-nomad-getting-started) (`v1.1` tag).

## Reference

- [Nomad Quick Start](https://developer.hashicorp.com/nomad/tutorials/get-started)
- Lecture 6–7: Terraform + Docker
