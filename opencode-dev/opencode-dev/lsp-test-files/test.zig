const std = @import("std");

const Person = struct {
    name: []const u8,
    age: u32,
    
    fn greet(self: Person) []const u8 {
        return std.fmt.comptimePrint("Hello, {s}!", .{self.name});
    }
};

pub fn main() void {
    const alice = Person{ .name = "Alice", .age = 30 };
    std.debug.print("{s}\n", .{alice.greet()});
}
