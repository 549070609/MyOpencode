local Person = {}
Person.__index = Person

function Person.new(name, age)
    local self = setmetatable({}, Person)
    self.name = name
    self.age = age
    return self
end

function Person:greet()
    return "Hello, " .. self.name .. "!"
end

local alice = Person.new("Alice", 30)
print(alice:greet())
