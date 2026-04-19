# Lecture 10: Nomad + Ollama (AI Workloads)

**Theme:** Run **private LLM** workloads on **HashiCorp Nomad** using **Ollama** (and optionally **Open WebUI**), following the official **AI workloads** tutorial track.

## Slides (Marp)

```bash
cd lecture10
npx @marp-team/marp-cli slides.md -o slides.html --no-stdin
```

Or `npm install` and `npm run slides`.

## Official tutorials (source)

- [AI workloads on Nomad – Overview](https://developer.hashicorp.com/nomad/tutorials/ai-workloads/ai-workloads-overview)
- [Configure a Granite AI workload](https://developer.hashicorp.com/nomad/tutorials/ai-workloads/configure-granite-workload)
- [Run a Granite AI workload](https://developer.hashicorp.com/nomad/tutorials/ai-workloads/run-granite-workload)
- [Scale node pools](https://developer.hashicorp.com/nomad/tutorials/ai-workloads/scale-node-pools)

Companion jobspecs (full Granite + S3 + node pools): HashiCorp **learn-nomad-ai** style repos linked from those pages.

## Assignment (simplified)

Course versions in **`assignment/`** — smaller defaults for local dev. See **`LECTURE10_ASSIGNMENT_README.md`**.

## Prerequisites

- **Nomad** ≥ 1.5, **Docker**
- **RAM:** 4GB+ minimum for tiny models; **8GB+** recommended; Granite-class models need more (see Ollama docs)
- **`curl`** on the Nomad client (for the `exec` poststart pull task)

## Related lectures

- **Lecture 8:** Terraform (S3, RDS — same ideas as tutorial `nomadVar` + S3 for Open WebUI)
- **Lecture 9:** Nomad basics, `hello-world` batch job; optional nginx service
