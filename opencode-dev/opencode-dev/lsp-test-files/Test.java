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
