# Lecture 9: HashiCorp Nomad

**Theme:** Workload orchestration — scheduling containers and batch jobs on a cluster, in the context of data pipelines and prior Terraform/Docker work.

## Official tutorials (source material)

- [Nomad introduction](https://developer.hashicorp.com/nomad/tutorials/get-started/introduction)
- [Install Nomad](https://developer.hashicorp.com/nomad/tutorials/get-started/install)
- [Create a cluster](https://developer.hashicorp.com/nomad/tutorials/get-started/cluster)
- [Deploy and update a job](https://developer.hashicorp.com/nomad/tutorials/get-started/jobs)
- [Stop the cluster](https://developer.hashicorp.com/nomad/tutorials/get-started/cleanup)

Optional deep dive: [learn-nomad-getting-started](https://github.com/hashicorp-education/learn-nomad-getting-started) (Terraform for cloud cluster, Pytechco jobs).

## Assignment

Minimal **`hello-world`** batch job (Docker **busybox**; Linux can use **`hello-world-exec`** without Docker): see **LECTURE9_ASSIGNMENT_README.md**. Optional **`nginx-web`** needs Docker.

## Prerequisites

- [Nomad](https://developer.hashicorp.com/nomad/install) ≥ 1.5
- **Docker** — required for **`hello-world.nomad.hcl`** and **`nginx-web.nomad.hcl`** (tutorial examples often use Docker too)

**macOS + Docker:** Use **`-data-dir` under `$HOME`** (default `-dev` uses `/private/tmp` → Docker mount errors). Run **`./nomad-dev-macos.sh`** from `lecture9/` or see **LECTURE9_ASSIGNMENT_README.md** (`sudo` alone is not enough).

## Troubleshooting (quick reference)

Each row is **(what you see → why → what to do)**.

| Symptom | Likely cause | Fix |
|--------|----------------|-----|
| **`Dimension "cpu" exhausted`** / failed to place | Other jobs already reserved CPU on the dev client | `nomad job stop -purge <job>` for each job, `nomad system gc`, restart agent; use small `resources` in jobspec |
| **`Constraint "missing drivers"`** (exec job) | **`exec`** driver is **Linux-only** | On macOS use **`hello-world.nomad.hcl`** (Docker), not **`hello-world-exec.nomad.hcl`** |
| **`permission denied`** / **`host_mnt/private/tmp/NomadClient`** | Default **`-dev`** uses **`/private/tmp`**; Docker Desktop cannot bind-mount there reliably | **`sudo` alone is not enough** — run **`./nomad-dev-macos.sh`** or **`sudo nomad agent -dev -data-dir="$HOME/nomad-dev-data" ...`** |
| Pytechco / tutorial jobs won’t place | Same as CPU, or jobspec has no **`resources`** and defaults are high | Purge other jobs; add **`resources { cpu = 250; memory = 256 }`** to the task (see **`examples/pytechco-redis-dev.nomad.hcl`**) |

Details: **LECTURE9_ASSIGNMENT_README.md**.

## Reference

- Lecture 6–7: Docker webserver, Terraform + Docker
- Lecture 8: Terraform baseline infrastructure
- [Nomad documentation](https://developer.hashicorp.com/nomad/docs)
