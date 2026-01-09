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
