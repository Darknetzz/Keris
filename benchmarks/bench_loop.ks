// Benchmark: loop sum 0..199999 (no list allocation)
let sum = 0
let i = 0
while i < 200000:
    sum = sum + i
    i = i + 1
print("sum 0..199999 =", sum)
