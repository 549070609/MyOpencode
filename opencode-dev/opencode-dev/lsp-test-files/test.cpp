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
