data class Person(val name: String, val age: Int)

fun Person.greet(): String = "Hello, $name!"

fun main() {
    val alice = Person("Alice", 30)
    println(alice.greet())
}
