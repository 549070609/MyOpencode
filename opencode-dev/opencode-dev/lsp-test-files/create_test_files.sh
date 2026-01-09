#!/bin/bash

echo "🚀 开始下载所有 LSP 服务器..."

# 创建各种语言的测试文件来触发 LSP 下载
echo "📝 创建测试文件..."

# TypeScript/JavaScript
cat > test.js << 'EOF'
function hello(name) {
  return `Hello, ${name}!`;
}
console.log(hello("World"));
EOF

cat > test.ts << 'EOF'
interface Person {
  name: string;
  age: number;
}

function greet(person: Person): string {
  return `Hello, ${person.name}!`;
}

const user: Person = { name: "Alice", age: 30 };
console.log(greet(user));
EOF

cat > package.json << 'EOF'
{
  "name": "test-project",
  "version": "1.0.0",
  "dependencies": {
    "typescript": "^5.0.0"
  },
  "devDependencies": {
    "eslint": "^8.0.0"
  }
}
EOF

# Python
cat > test.py << 'EOF'
def hello(name: str) -> str:
    return f"Hello, {name}!"

class Person:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    def greet(self) -> str:
        return hello(self.name)

if __name__ == "__main__":
    person = Person("Alice", 30)
    print(person.greet())
EOF

# C/C++
cat > test.c << 'EOF'
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    char* name;
    int age;
} Person;

void greet(Person* person) {
    printf("Hello, %s!\n", person->name);
}

int main() {
    Person alice = {"Alice", 30};
    greet(&alice);
    return 0;
}
EOF

cat > test.cpp << 'EOF'
#include <iostream>
#include <string>

class Person {
private:
    std::string name;
    int age;

public:
    Person(const std::string& name, int age) : name(name), age(age) {}
    
    std::string greet() const {
        return "Hello, " + name + "!";
    }
};

int main() {
    Person alice("Alice", 30);
    std::cout << alice.greet() << std::endl;
    return 0;
}
EOF

# Go
cat > test.go << 'EOF'
package main

import "fmt"

type Person struct {
    Name string
    Age  int
}

func (p Person) Greet() string {
    return fmt.Sprintf("Hello, %s!", p.Name)
}

func main() {
    alice := Person{Name: "Alice", Age: 30}
    fmt.Println(alice.Greet())
}
EOF

# Rust
cat > Cargo.toml << 'EOF'
[package]
name = "test-rust"
version = "0.1.0"
edition = "2021"

[dependencies]
EOF

cat > test.rs << 'EOF'
struct Person {
    name: String,
    age: u32,
}

impl Person {
    fn new(name: String, age: u32) -> Self {
        Person { name, age }
    }
    
    fn greet(&self) -> String {
        format!("Hello, {}!", self.name)
    }
}

fn main() {
    let alice = Person::new("Alice".to_string(), 30);
    println!("{}", alice.greet());
}
EOF

# Java
cat > Test.java << 'EOF'
public class Test {
    public static class Person {
        private String name;
        private int age;
        
        public Person(String name, int age) {
            this.name = name;
            this.age = age;
        }
        
        public String greet() {
            return "Hello, " + name + "!";
        }
    }
    
    public static void main(String[] args) {
        Person alice = new Person("Alice", 30);
        System.out.println(alice.greet());
    }
}
EOF

# Kotlin
cat > test.kt << 'EOF'
data class Person(val name: String, val age: Int)

fun Person.greet(): String = "Hello, $name!"

fun main() {
    val alice = Person("Alice", 30)
    println(alice.greet())
}
EOF

# PHP
cat > test.php << 'EOF'
<?php

class Person {
    private $name;
    private $age;
    
    public function __construct($name, $age) {
        $this->name = $name;
        $this->age = $age;
    }
    
    public function greet() {
        return "Hello, " . $this->name . "!";
    }
}

$alice = new Person("Alice", 30);
echo $alice->greet();
?>
EOF

# Ruby
cat > test.rb << 'EOF'
class Person
  attr_reader :name, :age
  
  def initialize(name, age)
    @name = name
    @age = age
  end
  
  def greet
    "Hello, #{@name}!"
  end
end

alice = Person.new("Alice", 30)
puts alice.greet
EOF

# Lua
cat > test.lua << 'EOF'
local Person = {}
Person.__index = Person

function Person.new(name, age)
    local self = setmetatable({}, Person)
    self.name = name
    self.age = age
    return self
end

function Person:greet()
    return "Hello, " .. self.name .. "!"
end

local alice = Person.new("Alice", 30)
print(alice:greet())
EOF

# Zig
cat > test.zig << 'EOF'
const std = @import("std");

const Person = struct {
    name: []const u8,
    age: u32,
    
    fn greet(self: Person) []const u8 {
        return std.fmt.comptimePrint("Hello, {s}!", .{self.name});
    }
};

pub fn main() void {
    const alice = Person{ .name = "Alice", .age = 30 };
    std.debug.print("{s}\n", .{alice.greet()});
}
EOF

# Terraform
cat > main.tf << 'EOF'
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
EOF

# YAML
cat > test.yaml << 'EOF'
person:
  name: Alice
  age: 30
  greeting: Hello, Alice!

settings:
  enabled: true
  version: 1.0
  features:
    - greeting
    - validation
EOF

# Shell/Bash
cat > test.sh << 'EOF'
#!/bin/bash

name="Alice"
age=30

greet() {
    echo "Hello, $name!"
}

echo "Name: $name"
echo "Age: $age"
greet
EOF

chmod +x test.sh

# Svelte
cat > test.svelte << 'EOF'
<script>
  let name = "Alice";
  let age = 30;
  
  function greet() {
    return `Hello, ${name}!`;
  }
</script>

<main>
  <h1>{greet()}</h1>
  <p>Name: {name}</p>
  <p>Age: {age}</p>
</main>

<style>
  main {
    font-family: Arial, sans-serif;
    padding: 20px;
  }
</style>
EOF

# Vue
cat > test.vue << 'EOF'
<template>
  <div>
    <h1>{{ greeting }}</h1>
    <p>Name: {{ name }}</p>
    <p>Age: {{ age }}</p>
  </div>
</template>

<script>
export default {
  data() {
    return {
      name: "Alice",
      age: 30
    };
  },
  computed: {
    greeting() {
      return `Hello, ${this.name}!`;
    }
  }
};
</script>

<style scoped>
div {
  font-family: Arial, sans-serif;
  padding: 20px;
}
</style>
EOF

# Astro
cat > test.astro << 'EOF'
---
const name = "Alice";
const age = 30;

function greet(name: string): string {
  return `Hello, ${name}!`;
}
---

<html lang="en">
<head>
  <title>Test Astro</title>
</head>
<body>
  <h1>{greet(name)}</h1>
  <p>Name: {name}</p>
  <p>Age: {age}</p>
</body>
</html>
EOF

# Typst
cat > test.typ << 'EOF'
#set page(paper: "a4")
#set text(font: "DejaVu Sans")

= Test Document

#let greet(name) = "Hello, " + name + "!"

== Greeting

#greet("Alice")

== Person Information

- Name: Alice
- Age: 30
EOF

# Dart
cat > test.dart << 'EOF'
class Person {
  String name;
  int age;
  
  Person(this.name, this.age);
  
  String greet() {
    return 'Hello, $name!';
  }
}

void main() {
  final alice = Person('Alice', 30);
  print(alice.greet());
}
EOF

# Prisma
cat > schema.prisma << 'EOF'
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "sqlite"
  url      = "file:./dev.db"
}

model User {
  id    Int    @id @default(autoincrement())
  name  String
  age   Int
  posts Post[]
}

model Post {
  id       Int  @id @default(autoincrement())
  title    String
  content  String?
  authorId Int
  author   User @relation(fields: [authorId], references: [id])
}
EOF

echo "✅ 测试文件创建完成！"
echo "📁 位置：$(pwd)"
ls -la