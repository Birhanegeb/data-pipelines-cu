# Lecture 8: Terraform for Data Pipelines — Finalizing

**Theme:** Automating the provisioning of cloud infrastructure for data pipelines.

Based on **Terraform: Up and Running, 3rd Edition** by Yevgeniy Brikman (O'Reilly), Chapters 4, 5, 6, 7.

## Topics

| Chapter | Content |
|---------|---------|
| **Ch 4** | Reusable infrastructure with Terraform modules (inputs, outputs, local values, versioned modules, gotchas) |
| **Ch 5** | Loops (`count`, `for_each`, `for`), conditionals, zero-downtime deployment, common gotchas |
| **Ch 6** | Managing secrets (provider auth, resource secrets, state/plan security, Vault/Secrets Manager) |
| **Ch 7** | Multiple providers (same provider in multiple regions/accounts, different providers together) |

## Slides (Marp)

Slides are in **`slides.md`** (Marp Markdown format).

### Build with Marp CLI

```bash
# Install marp-cli (one of):
npm install -g @marp-team/marp-cli
brew install marp-cli

# Generate HTML
npx @marp-team/marp-cli slides.md -o slides.html

# Generate PDF (requires Chrome/Edge/Firefox)
npx @marp-team/marp-cli slides.md --pdf -o slides.pdf

# Watch mode (live reload)
npx @marp-team/marp-cli -w slides.md
```

Or run from project root:
```bash
cd lecture8
npx @marp-team/marp-cli slides.md -o slides.html
```

## Hands-on Lab

Deploy a **baseline infrastructure** (S3 buckets + optional RDS) in `hands-on-lab/`:

```bash
cd lecture8/hands-on-lab
terraform init
terraform plan
terraform apply
```

See `hands-on-lab/README.md` for details.

## Assignment: Baseline Infrastructure

Deploy **storage buckets** and a **database** using modules and for_each.

- **assignment/docker/** — MinIO + PostgreSQL with `modules/docker-service` and `for_each`
- **assignment/aws/** — S3 buckets + optional RDS with `modules/s3-bucket` and `for_each`

See **LECTURE8_ASSIGNMENT_README.md** for objectives, how to run, and submission.

## Reference

- Book: *Terraform: Up and Running*, 3rd Ed. — Chapters 4, 5, 6, 7
- Lecture 6: First webserver (Docker)
- Lecture 7: Terraform Ch 1–3, webserver + n8n
