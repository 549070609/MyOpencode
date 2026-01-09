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
