# Lecture 10: Nomad + Ollama Assignment

Run **Ollama** on Nomad and **pull a small LLM** using the same patterns as the HashiCorp **AI workloads** tutorial (`poststart` task + `nomadService` + `/api/pull`).

## Objectives

1. Start a **Nomad dev cluster** (same as Lecture 9) with Docker available.
2. Submit **`assignment/ollama.nomad.hcl`**.
3. Verify the model pull (see logs / Ollama API) and optionally call **`http://<host>:11434/api/tags`** to list models.
4. **Optional (bonus):** Submit **`assignment/open-webui.nomad.hcl`** *after* Ollama is healthy, open the UI, and send a chat prompt.
5. Clean up: `nomad job stop -purge` for each job; stop the dev agent.

## Prerequisites

- Nomad CLI, Docker, enough **RAM** (see below).
- **`curl`** installed on the machine running the Nomad **client** (used by the `exec` poststart task).

## CPU exhaustion (`Dimension "cpu" exhausted`)

The **ollama** job has **two tasks** in one group (Ollama + `pull-model`); Nomad counts **both** toward the node until the poststart task finishes. **Open WebUI** adds more CPU. On a laptop dev agent, run **only ollama** first, or lower `resources.cpu` in the jobspecs. Stop other jobs: `nomad job stop -purge open-webui` then `ollama` if you need a clean node.

## RAM notes

- Default model in `ollama.nomad.hcl` is **`tinyllama`** — smallest practical demo.
- To match the HashiCorp tutorial, change the pull to **`granite3.3:2b`** (requires substantially more memory).
- If `pull-model` fails, check the allocation logs: `nomad alloc logs <alloc-id> pull-model`.

## Steps

### 1. Dev agent + CLI

Terminal A:

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

### 2. Run Ollama job

From the repo:

```bash
cd lecture10
nomad job run assignment/ollama.nomad.hcl
```

Wait for the **`pull-model`** task to finish (poststart). Then test (adjust host if not localhost):

```bash
curl -s http://localhost:11434/api/tags | head
```

### 3. Optional: Open WebUI

After **`ollama`** is running:

```bash
nomad job run assignment/open-webui.nomad.hcl
```

Open **`http://localhost:3000`** (or the mapped static port in the jobspec). Create a local account if prompted (signup enabled for lab).

### 4. Clean up

```bash
nomad job stop -purge open-webui
nomad job stop -purge ollama
```

## How to submit

1. Screenshot of **Nomad UI** showing job **`ollama`** (and optionally **`open-webui`**) running.
2. Screenshot of **`api/tags`** output in terminal **or** Open WebUI chat (if you did the bonus).
3. Short note: link to **Lecture 8** (Terraform + cloud capacity) or **Lecture 9** (Nomad services).
4. Pull request with screenshots; note any jobspec changes (e.g. model name, resources).

### PR title example

```
Lecture 10: Nomad + Ollama - [Your Name]
```

## Reference

- [AI workloads on Nomad – Overview](https://developer.hashicorp.com/nomad/tutorials/ai-workloads/ai-workloads-overview)
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- Lecture 9: Nomad introduction + `hello-world` job (optional nginx)
