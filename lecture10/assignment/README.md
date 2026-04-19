# Lecture 10 assignment jobspecs

| File | Purpose |
|------|---------|
| **`ollama.nomad.hcl`** | Ollama + `poststart` model pull (`tinyllama` by default) |
| **`open-webui.nomad.hcl`** | Optional UI; requires **`ollama`** job running first |

```bash
export NOMAD_ADDR=http://localhost:4646
nomad job run assignment/ollama.nomad.hcl
# wait for healthy; then optionally:
nomad job run assignment/open-webui.nomad.hcl
```

See **../LECTURE10_ASSIGNMENT_README.md**.
