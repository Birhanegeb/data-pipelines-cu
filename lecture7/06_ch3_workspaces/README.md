# 06 – Chapter 3: Terraform Workspaces

**Source:** *Terraform: Up and Running*, 3rd Ed., Chapter 3 – How to Manage Terraform State.

## What this script does

- Creates **one EC2 instance** whose **instance type** depends on the current **workspace**:
  - **default** workspace → `t2.medium`
  - Any other workspace (e.g. `stage`, `prod`) → `t2.micro`
- Uses `terraform.workspace` in a conditional expression and in the Name tag.

Workspaces let you keep multiple state environments (e.g. dev, stage, prod) in one config and one backend, with different state per workspace.

## Concepts

| Concept    | Where in the script |
|-----------|----------------------|
| Workspace | `terraform.workspace` – built-in value, name of current workspace |
| Conditional | `terraform.workspace == "default" ? "t2.medium" : "t2.micro"` |
| Multiple states | `terraform workspace new stage` creates a separate state for `stage` |

## How to run

```bash
terraform init
terraform apply
# Creates instance in "default" workspace (t2.medium)

terraform workspace new stage
terraform apply
# Creates instance in "stage" workspace (t2.micro)

terraform workspace list
terraform workspace select default
terraform destroy
terraform workspace select stage
terraform destroy
```

## Prerequisites

- Terraform >= 1.0, AWS credentials.
- State is stored **locally** unless you add a backend (e.g. 07_ch3_remote_state).
