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
