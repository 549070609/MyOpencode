interface Person {
  name: string;
  age: number;
}

function greet(person: Person): string {
  return `Hello, ${person.name}!`;
}

const user: Person = { name: "Alice", age: 30 };
console.log(greet(user));
