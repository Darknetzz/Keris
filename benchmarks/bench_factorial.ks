// Benchmark: recursive factorial (fact(100))
def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)

let result = fact(100)
print("fact(100) =", result)
