# Optional: extra variable types (Chapter 2 – Variables)
# These are not used in main.tf but show Terraform variable types.

variable "list_example" {
  description = "Example list type"
  type        = list(string)
  default     = ["a", "b", "c"]
}

variable "map_example" {
  description = "Example map type"
  type        = map(string)
  default = {
    key1 = "value1"
    key2 = "value2"
  }
}
