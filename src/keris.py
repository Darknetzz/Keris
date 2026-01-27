"""Main entry point for the Keris interpreter."""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .lexer import Lexer
from .parser import Parser, ParseError
from .interpreter import Interpreter
from .compiler import compile_chunk, CompilerError
from .vm import VM
from .python_compiler import compile_to_python, TranspileError
from .runtime import RuntimeError

app = typer.Typer(
    name="keris",
    help="Keris Programming Language - A general-purpose, dynamically-typed, interpreted programming language inspired by Python.\n\n"
         "📚 Documentation: https://github.com/Darknetzz/Keris\n"
         "🐙 GitHub: https://github.com/Darknetzz/Keris",
    add_completion=False,
)
console = Console()
VERSION = "1.0.0"


def run(source: str, use_vm: bool = True, use_compile: bool = True) -> None:
    """Run Keris source. Tries Python compile (fast) first, then VM, then tree-walk."""
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    parser = Parser(tokens)
    try:
        statements = parser.parse()
    except ParseError as e:
        console.print(f"[red]Parse error:[/red] {e}", style="bold red")
        sys.exit(1)
    
    # 1) Compile to Python and exec for near-native speed
    if use_compile:
        try:
            code, globals_dict = compile_to_python(statements)
            exec(code, globals_dict)
            return
        except TranspileError:
            pass
        except Exception as e:
            console.print(f"[red]Runtime error:[/red] {e}", style="bold red")
            sys.exit(1)
    
    # 2) Bytecode VM
    if use_vm:
        try:
            chunk = compile_chunk(statements)
            vm = VM()
            vm.run(chunk)
            return
        except CompilerError:
            pass
    # 3) Tree-walk interpreter
    interpreter = Interpreter()
    try:
        interpreter.interpret(statements)
    except RuntimeError as e:
        console.print(f"[red]Runtime error:[/red] {e}", style="bold red")
        sys.exit(1)


def run_file(filename: str, use_vm: bool = True, use_compile: bool = True) -> None:
    """Run a Keris source file."""
    file_path = Path(filename)
    if not file_path.exists():
        console.print(f"[red]Error:[/red] File '[bold]{filename}[/bold]' not found", style="bold red")
        sys.exit(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        run(source, use_vm=use_vm, use_compile=use_compile)
    except IOError as e:
        console.print(f"[red]Error reading file:[/red] {e}", style="bold red")
        sys.exit(1)


def run_prompt(use_vm: bool = True) -> None:
    """Run the Keris REPL."""
    interpreter = Interpreter()
    
    # Welcome banner
    banner = Panel.fit(
        f"[bold cyan]Keris v{VERSION}[/bold cyan]\n"
        "[dim]Type 'exit' or 'quit' to exit[/dim]",
        border_style="cyan",
        title="[bold]Keris REPL[/bold]",
    )
    console.print(banner)
    console.print()
    
    while True:
        try:
            line = console.input("[bold cyan]keris>[/bold cyan] ")
            if line.strip() in ("exit", "quit"):
                break
            if not line.strip():
                continue
            
            # Try to parse and execute
            lexer = Lexer(line)
            tokens = lexer.scan_tokens()
            
            parser = Parser(tokens)
            try:
                statements = parser.parse()
                interpreter.interpret(statements)
            except ParseError as e:
                console.print(f"[red]Parse error:[/red] {e}", style="bold red")
            except RuntimeError as e:
                console.print(f"[red]Runtime error:[/red] {e}", style="bold red")
        except EOFError:
            console.print()
            break
        except KeyboardInterrupt:
            console.print()
            break


@app.command()
def main(
    script: Optional[str] = typer.Argument(None, help="Keris script file to run"),
    version: bool = typer.Option(False, "--version", "-v", help="Show version information"),
    tree_walk: bool = typer.Option(False, "--tree-walk", help="Use tree-walk interpreter only (no compile, no VM)"),
    no_compile: bool = typer.Option(False, "--no-compile", help="Skip compile-to-Python; use VM or tree-walk only"),
) -> None:
    """
    Keris Programming Language Interpreter
    
    Run a Keris script file or start an interactive REPL.
    
    📚 Documentation: https://github.com/Darknetzz/Keris
    🐙 GitHub: https://github.com/Darknetzz/Keris
    """
    if version:
        console.print(f"[bold cyan]Keris v{VERSION}[/bold cyan]")
        sys.exit(0)
    
    use_compile = not no_compile and not tree_walk
    use_vm = not tree_walk
    if script:
        run_file(script, use_vm=use_vm, use_compile=use_compile)
    else:
        run_prompt(use_vm=use_vm)


def cli() -> None:
    """CLI entry point that handles typer exceptions gracefully."""
    try:
        app()
    except typer.Exit:
        # Typer.Exit is raised for normal exits (like --help, --version)
        # This is expected behavior, so we exit cleanly
        sys.exit(0)


if __name__ == "__main__":
    cli()
