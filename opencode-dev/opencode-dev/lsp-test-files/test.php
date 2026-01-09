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
