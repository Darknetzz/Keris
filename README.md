# Keris Programming Language

<div align="center">

<img src="img/keris.png" alt="Keris Logo" width="200">

A general-purpose, dynamically-typed, interpreted programming language inspired by Python.

</div>

## Features

- **Python-inspired syntax**: Clean, readable code with familiar constructs
- **Dynamic typing**: Flexible type system with runtime type checking
- **Rich standard library**: I/O, math, string manipulation, collections
- **Error handling**: Try-catch blocks for robust error management
- **Functions**: First-class functions with closures
- **Collections**: Lists and dictionaries with convenient syntax
- **REPL**: Interactive shell for quick testing

## Installation

Keris is implemented in Python 3.7+. Install dependencies with:

```bash
pip install -r requirements.txt
```

```bash
# Clone or download the repository
cd Keris

# Run directly
python main.py

# Or make it executable (Unix/Linux)
chmod +x main.py
./main.py
```

### Building Standalone Executables

You can build standalone executables for Windows and Linux using PyInstaller. See [Building Instructions](docs/BUILD.md) for details.

```bash
# Build executable (works on both Windows and Linux)
python build.py
```

- **Windows**: Creates `dist/keris.exe`
- **Linux**: Creates `dist/keris`

## Quick Start

### Hello World

```keris
print("Hello, World!")
```

### Variables and Functions

```keris
def greet(name) {
    return "Hello, " + name
}

let message = greet("Keris")
print(message)
```

### Control Flow

```keris
let x = 10

if x > 5 {
    print("x is greater than 5")
} else {
    print("x is not greater than 5")
}

while x > 0 {
    print(x)
    x = x - 1
}
```

### Lists and Loops

```keris
let numbers = [1, 2, 3, 4, 5]
let sum = 0

for num in numbers {
    sum = sum + num
}

print("Sum:", sum)
```

### Dictionaries

```keris
let person = {
    "name": "Alice",
    "age": 30,
    "city": "New York"
}

print(person["name"] + " is " + person["age"] + " years old")
```

## Usage

### Running a Script

```bash
python main.py script.ks
```

### Interactive REPL

```bash
python main.py
```

Then type Keris code:

```
keris> let x = 42
keris> print(x)
42
keris> def add(a, b) { return a + b }
keris> print(add(5, 3))
8
keris> exit
```

## Language Documentation

- [Quick Start Guide](docs/QUICKSTART.md) - Get started in minutes
- [Language Specification](docs/SPECIFICATION.md) - Complete language reference
- [Tutorial](docs/tutorial.md) - Learn Keris step by step
- [Keris vs Python Comparison](docs/COMPARISON.md) - Detailed comparison with Python
- [Examples](examples/) - Example programs

## Standard Library

### I/O

#### `print`

```keris
print(*args)
```

Print values to stdout.

**Parameters:**

- `*args`: Variable number of arguments to print. All arguments are converted to strings and printed with spaces between them.



**Returns:** None: Always returns nil in Keris.


**Example:**

```keris
print("Hello", "World")   # Prints: Hello World
```

#### `read_line`

```keris
read_line()
```

Read a line from stdin.

Reads a single line of input from the user. Blocks until the user
presses Enter.

**Returns:** str: The line of text entered by the user, without the trailing newline.
Returns empty string on EOF.


**Example:**

```keris
let name = read_line()   # Waits for user input
```

#### `read_number`

```keris
read_number()
```

Read a number from stdin.

Reads a line from stdin and attempts to parse it as a number.
Automatically detects integers and floats based on decimal point.

**Returns:** int or float: The parsed number. Returns 0 if parsing fails or on EOF.


**Example:**

```keris
let age = read_number()   # Waits for numeric input
```


### Math

#### `math.abs`

```keris
math.abs(x)
```

Return the absolute value of a number.

**Parameters:**

- `x` (number): The number.



**Returns:** number: The absolute value of x.

#### `math.ceil`

```keris
math.ceil(x)
```

Return the ceiling of a number (smallest integer >= x).

**Parameters:**

- `x` (number): The number.



**Returns:** float: The ceiling of x.

#### `math.cos`

```keris
math.cos(x)
```

Return the cosine of x (in radians).

**Parameters:**

- `x` (number): Angle in radians.



**Returns:** float: The cosine of x.

#### `math.floor`

```keris
math.floor(x)
```

Return the floor of a number (largest integer <= x).

**Parameters:**

- `x` (number): The number.



**Returns:** float: The floor of x.

#### `math.max`

```keris
math.max(*args)
```

Return the maximum value from the given arguments.

**Parameters:**

- `*args`: Variable number of numeric arguments.



**Returns:** number or nil: The maximum value, or nil if no arguments provided.

#### `math.min`

```keris
math.min(*args)
```

Return the minimum value from the given arguments.

**Parameters:**

- `*args`: Variable number of numeric arguments.



**Returns:** number or nil: The minimum value, or nil if no arguments provided.

#### `math.pow`

```keris
math.pow(x, y)
```

Return x raised to the power of y.

**Parameters:**

- `x` (number): The base.

- `y` (number): The exponent.



**Returns:** number: x raised to the power of y.

#### `math.round`

```keris
math.round(x)
```

Round a number to the nearest integer.

**Parameters:**

- `x` (number): The number to round.



**Returns:** int: The rounded value.

#### `math.sin`

```keris
math.sin(x)
```

Return the sine of x (in radians).

**Parameters:**

- `x` (number): Angle in radians.



**Returns:** float: The sine of x.

#### `math.sqrt`

```keris
math.sqrt(x)
```

Return the square root of a number.

**Parameters:**

- `x` (number): The number (must be non-negative).



**Returns:** float: The square root of x.

#### `math.tan`

```keris
math.tan(x)
```

Return the tangent of x (in radians).

**Parameters:**

- `x` (number): Angle in radians.



**Returns:** float: The tangent of x.

**Constants:**

- `math.e`: 2.718281828459045
- `math.pi`: 3.141592653589793

### String

#### `str.join`

```keris
str.join(lst, delimiter="")
```

Join a list of values into a single string.

**Parameters:**

- `lst` (list): The list of values to join.

- `delimiter` (string, optional): The string to insert between each element. Defaults to empty string.



**Returns:** string: A new string formed by joining all elements with the delimiter.


**Example:**

```keris
str.join(["a", "b", "c"], ",")   # Returns: "a,b,c"
```

#### `str.len`

```keris
str.len(s)
```

Return the length of a string.

**Parameters:**

- `s` (string): The string to measure.



**Returns:** int: The number of characters in the string.


**Example:**

```keris
str.len("hello")   # Returns: 5
```

#### `str.lower`

```keris
str.lower(s)
```

Convert a string to lowercase.

**Parameters:**

- `s` (string): The string to convert.



**Returns:** string: A new string with all characters converted to lowercase.


**Example:**

```keris
str.lower("HELLO")   # Returns: "hello"
```

#### `str.split`

```keris
str.split(s, delimiter=None)
```

Split a string into a list of substrings.

**Parameters:**

- `s` (string): The string to split.

- `delimiter` (string, optional): The delimiter to split on. Defaults to space if not provided.



**Returns:** list: A list of substrings.


**Example:**

```keris
str.split("a,b,c", ",")   # Returns: ["a", "b", "c"]
```

#### `str.upper`

```keris
str.upper(s)
```

Convert a string to uppercase.

**Parameters:**

- `s` (string): The string to convert.



**Returns:** string: A new string with all characters converted to uppercase.


**Example:**

```keris
str.upper("hello")   # Returns: "HELLO"
```


### List

#### `list.append`

```keris
list.append(lst, item)
```

Append an item to the end of a list.

Modifies the list in-place.

**Parameters:**

- `lst` (list): The list to modify.

- `item` (any): The item to append.



**Returns:** None: Always returns nil.


**Example:**

```keris
let numbers = [1, 2, 3]
list.append(numbers, 4)   # numbers is now [1, 2, 3, 4]
```

#### `list.contains`

```keris
list.contains(lst, item)
```

Check if a list contains a specific item.

**Parameters:**

- `lst` (list): The list to search.

- `item` (any): The item to search for.



**Returns:** bool: true if the item is in the list, false otherwise.


**Example:**

```keris
list.contains([1, 2, 3], 2)   # Returns: true
```

#### `list.len`

```keris
list.len(lst)
```

Return the length (number of elements) of a list.

**Parameters:**

- `lst` (list): The list to measure.



**Returns:** int: The number of elements in the list.


**Example:**

```keris
list.len([1, 2, 3])   # Returns: 3
```

#### `list.pop`

```keris
list.pop(lst)
```

Remove and return the last item from a list.

Modifies the list in-place by removing the last element.

**Parameters:**

- `lst` (list): The list to pop from.



**Returns:** any or nil: The last item in the list, or nil if the list is empty.


**Example:**

```keris
let numbers = [1, 2, 3]
let last = list.pop(numbers)   # Returns 3, numbers is now [1, 2]
```

#### `list.shuffle`

```keris
list.shuffle(lst)
```

Shuffle the elements of a list.

Modifies the list in-place by shuffling the elements randomly.

**Parameters:**

- `lst` (list): The list to shuffle.



**Returns:** None: Always returns nil.


**Example:**

```keris
let numbers = [1, 2, 3, 4, 5]
list.shuffle(numbers)   # Randomly reorders the list
```

#### `list.sort`

```keris
list.sort(lst)
```

Sort the elements of a list.

Modifies the list in-place by sorting the elements in ascending order.

**Parameters:**

- `lst` (list): The list to sort.



**Returns:** None: Always returns nil.


**Example:**

```keris
let numbers = [3, 1, 4, 1, 5]
list.sort(numbers)   # numbers is now [1, 1, 3, 4, 5]
```


### Dict

#### `dict.contains`

```keris
dict.contains(d, key)
```

Check if a dictionary contains a specific key.

**Parameters:**

- `d` (dict): The dictionary to search.

- `key` (any): The key to search for.



**Returns:** bool: true if the key exists in the dictionary, false otherwise.


**Example:**

```keris
dict.contains({"a": 1}, "a")   # Returns: true
```

#### `dict.keys`

```keris
dict.keys(d)
```

Return a list of all keys in a dictionary.

**Parameters:**

- `d` (dict): The dictionary.



**Returns:** list: A list containing all keys in the dictionary.


**Example:**

```keris
dict.keys({"a": 1, "b": 2})   # Returns: ["a", "b"]
```

#### `dict.len`

```keris
dict.len(d)
```

Return the number of key-value pairs in a dictionary.

**Parameters:**

- `d` (dict): The dictionary.



**Returns:** int: The number of key-value pairs.


**Example:**

```keris
dict.len({"a": 1, "b": 2})   # Returns: 2
```

#### `dict.values`

```keris
dict.values(d)
```

Return a list of all values in a dictionary.

**Parameters:**

- `d` (dict): The dictionary.



**Returns:** list: A list containing all values in the dictionary.


**Example:**

```keris
dict.values({"a": 1, "b": 2})   # Returns: [1, 2]
```


### Type

#### `type.of`

```keris
type.of(value)
```

Get the type name of a value.

Returns a string representing the type of the given value.
Useful for runtime type checking in Keris code.

**Parameters:**

- `value` (any): The value to check the type of.



**Returns:** string: The type name. Possible values:
- "nil" for nil values
- "boolean" for true/false
- "number" for integers and floats
- "string" for strings
- "list" for lists
- "dict" for dictionaries
- "unknown" for unrecognized types


**Example:**

```keris
type.of(42)         # Returns: "number"
type.of("hello")    # Returns: "string"
type.of(true)       # Returns: "boolean"
```


### Range

#### `range`

```keris
range(start, end=None, step=1)
```

Create a range of numbers.

Generates a list of numbers in a specified range. Commonly used
in for loops to iterate over a sequence of numbers.

**Parameters:**

- `start` (int): If end is provided: the start value (inclusive). If end is nil: the end value (exclusive), starting from 0.

- `end` (int, optional): The end value (exclusive). If not provided, the range goes from 0 to start.

- `step` (int, optional): The step size between numbers. Defaults to 1.



**Returns:** list: A list of numbers in the specified range.


**Example:**

```keris
range(5)            # Returns: [0, 1, 2, 3, 4]
range(1, 5)          # Returns: [1, 2, 3, 4]
range(0, 10, 2)      # Returns: [0, 2, 4, 6, 8]
```


**Note:** The end value is exclusive, so range(0, 5) produces [0, 1, 2, 3, 4].



## Examples

See the [examples](examples/) directory for more complete programs.

## Project Structure

```
Keris/
├── README.md              # This file
├── main.py                # Entry point
├── src/                   # Source code
│   ├── token.py          # Token definitions
│   ├── lexer.py          # Lexical analyzer
│   ├── parser.py         # Parser
│   ├── ast.py            # AST nodes
│   ├── interpreter.py    # Interpreter
│   ├── runtime.py        # Runtime errors
│   ├── stdlib.py         # Standard library
│   └── keris.py          # Main interpreter
├── docs/                  # Documentation
│   ├── QUICKSTART.md     # Quick start guide
│   ├── SPECIFICATION.md  # Language specification
│   ├── DESIGN_OUTLINE.md # Design document
│   ├── BUILD.md          # Building instructions
│   ├── tutorial.md       # Tutorial
│   └── COMPARISON.md     # Keris vs Python comparison
├── examples/              # Example programs
└── tests/                 # Test suite
```

## Contributing

This is a learning project, but contributions and feedback are welcome!

## License

See LICENSE file for details.

## Version

Current version: 1.0.0

---

**Note**: Keris is an educational project. For production use, consider more mature languages like Python, JavaScript, or Rust.
