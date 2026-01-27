#!/usr/bin/env python3
"""
Benchmark Keris against Python and generate a comparison chart.
Run: python run_benchmarks.py
Output: prints table to stdout, writes benchmarks/report.html
"""

import io
import sys
import time
from pathlib import Path
from contextlib import redirect_stdout

# Project root
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.lexer import Lexer
from src.parser import Parser
from src.compiler import compile_chunk, CompilerError
from src.vm import VM
from src.runtime import RuntimeError as KerisRuntimeError


# ---------------------------------------------------------------------------
# Keris benchmark sources (indent-based; 4 spaces per level)
# ---------------------------------------------------------------------------

KERIS_FIB = """
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
let result = fib(30)
"""

KERIS_FACTORIAL = """
def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)
let result = fact(100)
"""

KERIS_LOOP = """
let sum = 0
let i = 0
while i < 200000:
    sum = sum + i
    i = i + 1
"""


def run_keris(source: str, runs: int = 3) -> float:
    """Run Keris source (bytecode VM) and return median time in seconds (stdout suppressed)."""
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()
    try:
        chunk = compile_chunk(statements)
    except CompilerError:
        raise
    out = io.StringIO()
    times = []
    for _ in range(runs):
        vm = VM()
        start = time.perf_counter()
        with redirect_stdout(out):
            try:
                vm.run(chunk)
            except KerisRuntimeError:
                pass
        times.append(time.perf_counter() - start)
    times.sort()
    return times[len(times) // 2]


def run_python_fib(runs: int = 3) -> float:
    def fib(n):
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        fib(30)
        times.append(time.perf_counter() - start)
    times.sort()
    return times[len(times) // 2]


def run_python_factorial(runs: int = 3) -> float:
    def fact(n):
        if n <= 1:
            return 1
        return n * fact(n - 1)
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        fact(100)
        times.append(time.perf_counter() - start)
    times.sort()
    return times[len(times) // 2]


def run_python_loop(runs: int = 3) -> float:
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        s = 0
        i = 0
        while i < 200000:
            s += i
            i += 1
        times.append(time.perf_counter() - start)
    times.sort()
    return times[len(times) // 2]


def ms(t: float) -> str:
    return f"{t * 1000:.2f}"


def main() -> None:
    runs = 5
    results = []

    print("Running benchmarks (Keris vs Python)...")
    print()

    # Fibonacci
    try:
        k_fib = run_keris(KERIS_FIB, runs)
        p_fib = run_python_fib(runs)
        results.append(("Fibonacci (recursive, fib(30))", k_fib, p_fib))
        print(f"  Fibonacci:    Keris {ms(k_fib)} ms  |  Python {ms(p_fib)} ms")
    except Exception as e:
        results.append(("Fibonacci (recursive, fib(30))", None, run_python_fib(runs)))
        print(f"  Fibonacci:    Keris ERROR ({e})  |  Python {ms(results[-1][2])} ms")

    # Factorial
    try:
        k_fac = run_keris(KERIS_FACTORIAL, runs)
        p_fac = run_python_factorial(runs)
        results.append(("Factorial (recursive, fact(100))", k_fac, p_fac))
        print(f"  Factorial:    Keris {ms(k_fac)} ms  |  Python {ms(p_fac)} ms")
    except Exception as e:
        results.append(("Factorial (recursive, fact(100))", None, run_python_factorial(runs)))
        print(f"  Factorial:    Keris ERROR ({e})  |  Python {ms(results[-1][2])} ms")

    # Loop
    try:
        k_loop = run_keris(KERIS_LOOP, runs)
        p_loop = run_python_loop(runs)
        results.append(("Loop (sum 0..199999)", k_loop, p_loop))
        print(f"  Loop sum:     Keris {ms(k_loop)} ms  |  Python {ms(p_loop)} ms")
    except Exception as e:
        results.append(("Loop (sum 0..199999)", None, run_python_loop(runs)))
        print(f"  Loop sum:     Keris ERROR ({e})  |  Python {ms(results[-1][2])} ms")

    print()
    # Build HTML report
    html = build_html(results)
    out_path = ROOT / "benchmarks" / "report.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"Report written to {out_path}")
    print()
    print("Summary: Keris is interpreted by Python, so it is expected to be slower than")
    print("native Python. The chart normalizes Python = 1x for comparison.")


def build_html(results: list) -> str:
    """Build HTML with table and bar chart. Python = 1x baseline."""
    rows = []
    for name, k_time, p_time in results:
        if k_time is not None and p_time and p_time > 0:
            ratio = k_time / p_time
            rows.append((name, k_time, p_time, ratio))
        else:
            rows.append((name, k_time, p_time, None))

    html_rows = []
    for name, k_time, p_time, ratio in rows:
        k_ms = f"{k_time * 1000:.2f}" if k_time is not None else "—"
        p_ms = f"{p_time * 1000:.2f}" if p_time else "—"
        ratio_str = f"{ratio:.1f}×" if ratio is not None else "—"
        html_rows.append(
            f"        <tr><td>{name}</td><td>{k_ms} ms</td><td>{p_ms} ms</td>"
            f"<td>{ratio_str}</td></tr>"
        )

    chart_bars = []
    for name, k_time, p_time, ratio in rows:
        if ratio is not None and ratio > 0:
            total = 1.0 + ratio
            pct_py = 100 * (1.0 / total)
            pct_keris = 100 * (ratio / total)
            chart_bars.append(
                f'        <div class="row"><span class="label">{name}</span>'
                f'<div class="bar-wrap"><div class="bar py" style="width:{pct_py}%"></div>'
                f'<div class="bar keris" style="width:{pct_keris}%"></div></div>'
                f'<span class="legend">Py 1× / Keris {ratio:.1f}×</span></div>'
            )
        else:
            chart_bars.append(
                f'        <div class="row"><span class="label">{name}</span>'
                f'<span class="legend">—</span></div>'
            )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Keris vs Python benchmark</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }}
    h1 {{ color: #1a1a2e; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem 0.75rem; text-align: right; }}
    th {{ background: #1a1a2e; color: #eee; }}
    td:first-child {{ text-align: left; }}
    .chart {{ margin: 2rem 0; }}
    .row {{ display: flex; align-items: center; gap: 1rem; margin: 0.5rem 0; }}
    .label {{ flex: 0 0 280px; font-size: 0.9rem; }}
    .bar-wrap {{ flex: 1; display: flex; height: 24px; background: #f0f0f0; border-radius: 4px; overflow: hidden; }}
    .bar {{ height: 100%; min-width: 2px; }}
    .bar.py {{ background: #2e7d32; }}
    .bar.keris {{ background: #1565c0; }}
    .legend {{ flex: 0 0 120px; font-size: 0.85rem; color: #555; }}
    .note {{ color: #666; font-size: 0.9rem; margin-top: 2rem; }}
  </style>
</head>
<body>
  <h1>Keris vs Python benchmark</h1>
  <p>Lower bar = faster. Python is baseline (1×). Keris runs on the Python interpreter.</p>
  <div class="chart">
{"\n".join(chart_bars)}
  </div>
  <h2>Times (median of {5} runs)</h2>
  <table>
    <tr><th>Benchmark</th><th>Keris</th><th>Python</th><th>Keris / Python</th></tr>
{"\n".join(html_rows)}
  </table>
  <p class="note">Run <code>python run_benchmarks.py</code> to regenerate. All benchmarks use the same algorithms in both languages.</p>
</body>
</html>
"""


if __name__ == "__main__":
    main()
