variable "name" {
  description = "The name to greet"
  type        = string
  default     = "Alice"
}

variable "age" {
  description = "The age"
  type        = number
  default     = 30
}

output "greeting" {
  value = "Hello, ${var.name}!"
}

resource "local_file" "greeting" {
  content  = "Hello, ${var.name}, you are ${var.age} years old!"
  filename = "${path.module}/greeting.txt"
}
