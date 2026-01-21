"""Standard library functions for Keris.

This module provides built-in functions and modules that are available
to all Keris programs. Functions are implemented as Python callables
and are automatically registered in the global environment.
"""

import math as py_math
from typing import Any, List, Dict


def create_stdlib() -> Dict[str, Any]:
    """Create and return the standard library.
    
    Returns:
        Dict[str, Any]: Dictionary mapping function/module names to their implementations.
                       Functions can be called directly from Keris code.
    """
    stdlib = {}
    
    # ============================================================================
    # I/O Functions
    # ============================================================================
    
    def print_func(*args):
        """Print values to stdout.
        
        Args:
            *args: Variable number of arguments to print. All arguments are converted
                   to strings and printed with spaces between them.
        
        Returns:
            None: Always returns nil in Keris.
        
        Example:
            print("Hello", "World")  // Prints: Hello World
        """
        print(*args)
        return None
    
    def read_line_func():
        """Read a line from stdin.
        
        Reads a single line of input from the user. Blocks until the user
        presses Enter.
        
        Returns:
            str: The line of text entered by the user, without the trailing newline.
                 Returns empty string on EOF.
        
        Example:
            let name = read_line()  // Waits for user input
        """
        try:
            return input()
        except EOFError:
            return ""
    
    def read_number_func():
        """Read a number from stdin.
        
        Reads a line from stdin and attempts to parse it as a number.
        Automatically detects integers and floats based on decimal point.
        
        Returns:
            int or float: The parsed number. Returns 0 if parsing fails or on EOF.
        
        Example:
            let age = read_number()  // Waits for numeric input
        """
        try:
            line = input()
            if '.' in line:
                return float(line)
            return int(line)
        except (EOFError, ValueError):
            return 0
    
    stdlib["print"] = print_func
    stdlib["read_line"] = read_line_func
    stdlib["read_number"] = read_number_func
    
    # ============================================================================
    # Math Module
    # ============================================================================
    
    def math_abs(x):
        """Return the absolute value of a number.
        
        Args:
            x (number): The number.
        
        Returns:
            number: The absolute value of x.
        """
        return abs(x)
    
    def math_sqrt(x):
        """Return the square root of a number.
        
        Args:
            x (number): The number (must be non-negative).
        
        Returns:
            float: The square root of x.
        """
        return py_math.sqrt(x)
    
    def math_pow(x, y):
        """Return x raised to the power of y.
        
        Args:
            x (number): The base.
            y (number): The exponent.
        
        Returns:
            number: x raised to the power of y.
        """
        return x ** y
    
    def math_max(*args):
        """Return the maximum value from the given arguments.
        
        Args:
            *args: Variable number of numeric arguments.
        
        Returns:
            number or nil: The maximum value, or nil if no arguments provided.
        """
        return max(args) if args else None
    
    def math_min(*args):
        """Return the minimum value from the given arguments.
        
        Args:
            *args: Variable number of numeric arguments.
        
        Returns:
            number or nil: The minimum value, or nil if no arguments provided.
        """
        return min(args) if args else None
    
    def math_floor(x):
        """Return the floor of a number (largest integer <= x).
        
        Args:
            x (number): The number.
        
        Returns:
            float: The floor of x.
        """
        return py_math.floor(x)
    
    def math_ceil(x):
        """Return the ceiling of a number (smallest integer >= x).
        
        Args:
            x (number): The number.
        
        Returns:
            float: The ceiling of x.
        """
        return py_math.ceil(x)
    
    def math_round(x):
        """Round a number to the nearest integer.
        
        Args:
            x (number): The number to round.
        
        Returns:
            int: The rounded value.
        """
        return round(x)
    
    def math_sin(x):
        """Return the sine of x (in radians).
        
        Args:
            x (number): Angle in radians.
        
        Returns:
            float: The sine of x.
        """
        return py_math.sin(x)
    
    def math_cos(x):
        """Return the cosine of x (in radians).
        
        Args:
            x (number): Angle in radians.
        
        Returns:
            float: The cosine of x.
        """
        return py_math.cos(x)
    
    def math_tan(x):
        """Return the tangent of x (in radians).
        
        Args:
            x (number): Angle in radians.
        
        Returns:
            float: The tangent of x.
        """
        return py_math.tan(x)
    
    # Math constants (not functions, but included in math module)
    math_module = {
        "abs": math_abs,
        "sqrt": math_sqrt,
        "pow": math_pow,
        "max": math_max,
        "min": math_min,
        "floor": math_floor,
        "ceil": math_ceil,
        "round": math_round,
        "sin": math_sin,
        "cos": math_cos,
        "tan": math_tan,
        "pi": py_math.pi,  # Mathematical constant π (approximately 3.14159...)
        "e": py_math.e,     # Mathematical constant e (approximately 2.71828...)
    }
    stdlib["math"] = math_module
    
    # ============================================================================
    # String Module
    # ============================================================================
    
    def str_len(s: str) -> int:
        """Return the length of a string.
        
        Args:
            s (string): The string to measure.
        
        Returns:
            int: The number of characters in the string.
        
        Example:
            str.len("hello")  // Returns: 5
        """
        return len(s)
    
    def str_upper(s: str) -> str:
        """Convert a string to uppercase.
        
        Args:
            s (string): The string to convert.
        
        Returns:
            string: A new string with all characters converted to uppercase.
        
        Example:
            str.upper("hello")  // Returns: "HELLO"
        """
        return s.upper()
    
    def str_lower(s: str) -> str:
        """Convert a string to lowercase.
        
        Args:
            s (string): The string to convert.
        
        Returns:
            string: A new string with all characters converted to lowercase.
        
        Example:
            str.lower("HELLO")  // Returns: "hello"
        """
        return s.lower()
    
    def str_split(s: str, delimiter: str = None) -> List:
        """Split a string into a list of substrings.
        
        Args:
            s (string): The string to split.
            delimiter (string, optional): The delimiter to split on. 
                                        Defaults to space if not provided.
        
        Returns:
            list: A list of substrings.
        
        Example:
            str.split("a,b,c", ",")  // Returns: ["a", "b", "c"]
        """
        if delimiter is None:
            delimiter = " "
        return s.split(delimiter)
    
    def str_join(lst: List, delimiter: str = "") -> str:
        """Join a list of values into a single string.
        
        Args:
            lst (list): The list of values to join.
            delimiter (string, optional): The string to insert between each element.
                                        Defaults to empty string.
        
        Returns:
            string: A new string formed by joining all elements with the delimiter.
        
        Example:
            str.join(["a", "b", "c"], ",")  // Returns: "a,b,c"
        """
        return delimiter.join(str(x) for x in lst)
    
    str_module = {
        "len": str_len,
        "upper": str_upper,
        "lower": str_lower,
        "split": str_split,
        "join": str_join,
    }
    stdlib["str"] = str_module
    
    # ============================================================================
    # List Module
    # ============================================================================
    
    def list_append(lst: List, item: Any) -> None:
        """Append an item to the end of a list.
        
        Modifies the list in-place.
        
        Args:
            lst (list): The list to modify.
            item (any): The item to append.
        
        Returns:
            None: Always returns nil.
        
        Example:
            let numbers = [1, 2, 3]
            list.append(numbers, 4)  // numbers is now [1, 2, 3, 4]
        """
        lst.append(item)
        return None
    
    def list_pop(lst: List) -> Any:
        """Remove and return the last item from a list.
        
        Modifies the list in-place by removing the last element.
        
        Args:
            lst (list): The list to pop from.
        
        Returns:
            any or nil: The last item in the list, or nil if the list is empty.
        
        Example:
            let numbers = [1, 2, 3]
            let last = list.pop(numbers)  // Returns 3, numbers is now [1, 2]
        """
        if len(lst) == 0:
            return None
        return lst.pop()
    
    def list_len(lst: List) -> int:
        """Return the length (number of elements) of a list.
        
        Args:
            lst (list): The list to measure.
        
        Returns:
            int: The number of elements in the list.
        
        Example:
            list.len([1, 2, 3])  // Returns: 3
        """
        return len(lst)
    
    def list_contains(lst: List, item: Any) -> bool:
        """Check if a list contains a specific item.
        
        Args:
            lst (list): The list to search.
            item (any): The item to search for.
        
        Returns:
            bool: true if the item is in the list, false otherwise.
        
        Example:
            list.contains([1, 2, 3], 2)  // Returns: true
        """
        return item in lst
    
    list_module = {
        "append": list_append,
        "pop": list_pop,
        "len": list_len,
        "contains": list_contains,
    }
    stdlib["list"] = list_module
    
    # ============================================================================
    # Dictionary Module
    # ============================================================================
    
    def dict_keys(d: Dict) -> List:
        """Return a list of all keys in a dictionary.
        
        Args:
            d (dict): The dictionary.
        
        Returns:
            list: A list containing all keys in the dictionary.
        
        Example:
            dict.keys({"a": 1, "b": 2})  // Returns: ["a", "b"]
        """
        return list(d.keys())
    
    def dict_values(d: Dict) -> List:
        """Return a list of all values in a dictionary.
        
        Args:
            d (dict): The dictionary.
        
        Returns:
            list: A list containing all values in the dictionary.
        
        Example:
            dict.values({"a": 1, "b": 2})  // Returns: [1, 2]
        """
        return list(d.values())
    
    def dict_len(d: Dict) -> int:
        """Return the number of key-value pairs in a dictionary.
        
        Args:
            d (dict): The dictionary.
        
        Returns:
            int: The number of key-value pairs.
        
        Example:
            dict.len({"a": 1, "b": 2})  // Returns: 2
        """
        return len(d)
    
    def dict_contains(d: Dict, key: Any) -> bool:
        """Check if a dictionary contains a specific key.
        
        Args:
            d (dict): The dictionary to search.
            key (any): The key to search for.
        
        Returns:
            bool: true if the key exists in the dictionary, false otherwise.
        
        Example:
            dict.contains({"a": 1}, "a")  // Returns: true
        """
        return key in d
    
    dict_module = {
        "keys": dict_keys,
        "values": dict_values,
        "len": dict_len,
        "contains": dict_contains,
    }
    stdlib["dict"] = dict_module
    
    # ============================================================================
    # Type Module
    # ============================================================================
    
    def typeof(value: Any) -> str:
        """Get the type name of a value.
        
        Returns a string representing the type of the given value.
        Useful for runtime type checking in Keris code.
        
        Args:
            value (any): The value to check the type of.
        
        Returns:
            string: The type name. Possible values:
                   - "nil" for nil values
                   - "boolean" for true/false
                   - "number" for integers and floats
                   - "string" for strings
                   - "list" for lists
                   - "dict" for dictionaries
                   - "unknown" for unrecognized types
        
        Example:
            type.of(42)        // Returns: "number"
            type.of("hello")   // Returns: "string"
            type.of(true)      // Returns: "boolean"
        """
        if value is None:
            return "nil"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, (int, float)):
            return "number"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "list"
        elif isinstance(value, dict):
            return "dict"
        else:
            return "unknown"
    
    type_module = {
        "of": typeof,
    }
    stdlib["type"] = type_module
    
    # ============================================================================
    # Range Function
    # ============================================================================
    
    def range_func(start: int, end: int = None, step: int = 1) -> List:
        """Create a range of numbers.
        
        Generates a list of numbers in a specified range. Commonly used
        in for loops to iterate over a sequence of numbers.
        
        Args:
            start (int): If end is provided: the start value (inclusive).
                        If end is nil: the end value (exclusive), starting from 0.
            end (int, optional): The end value (exclusive). If not provided,
                               the range goes from 0 to start.
            step (int, optional): The step size between numbers. Defaults to 1.
        
        Returns:
            list: A list of numbers in the specified range.
        
        Example:
            range(5)           // Returns: [0, 1, 2, 3, 4]
            range(1, 5)         // Returns: [1, 2, 3, 4]
            range(0, 10, 2)     // Returns: [0, 2, 4, 6, 8]
        
        Note:
            The end value is exclusive, so range(0, 5) produces [0, 1, 2, 3, 4].
        """
        if end is None:
            return list(range(0, start))
        return list(range(start, end, step))
    
    stdlib["range"] = range_func
    
    return stdlib
