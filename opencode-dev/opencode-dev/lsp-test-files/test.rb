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
