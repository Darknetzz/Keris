// Benchmark: recursive Fibonacci (fib(30))
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

let result = fib(30)
print("fib(30) =", result)
