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
