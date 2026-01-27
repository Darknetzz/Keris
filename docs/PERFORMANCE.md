# Performance

Keris can run in three ways. By default, scripts use **compile-to-Python** for near–native speed.

## Execution modes

| Mode | How to enable | Speed (vs Python) |
|------|----------------|-------------------|
| **Compile to Python** | Default | **~0.9×–2.2×** (often close or faster) |
| Bytecode VM | `--no-compile` | ~50–150× slower |
| Tree-walk interpreter | `--tree-walk` | ~100–170× slower |

- **Compile to Python**: Keris is transpiled to Python AST and executed with `exec()`, so the hot path is real Python bytecode on CPython. This is why benchmarks show Keris in the same ballpark as Python (and sometimes slightly faster on recursion).
- **VM / tree-walk**: No transpilation; Keris runs on the in-Python VM or by walking the AST. Much slower, but useful for debugging or when the transpiler doesn’t support a construct yet.

## Benchmarks

From the project root:

```bash
python run_benchmarks.py
```

This compares Keris (compile-to-Python) with Python on Fibonacci, Factorial, and a simple loop. The report is written to [benchmarks/report.html](../benchmarks/report.html). See [benchmarks/README.md](../benchmarks/README.md) for typical results and how benchmarks are run.
