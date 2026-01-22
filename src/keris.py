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


def run(source: str) -> None:
    """Run Keris source code."""
    lexer = Lexer(source)
    tokens = lexer.scan_tokens()
    
    parser = Parser(tokens)
    try:
        statements = parser.parse()
    except ParseError as e:
        console.print(f"[red]Parse error:[/red] {e}", style="bold red")
        sys.exit(1)
    
    interpreter = Interpreter()
    try:
        interpreter.interpret(statements)
    except RuntimeError as e:
        console.print(f"[red]Runtime error:[/red] {e}", style="bold red")
        sys.exit(1)


def run_file(filename: str) -> None:
    """Run a Keris source file."""
    file_path = Path(filename)
    if not file_path.exists():
        console.print(f"[red]Error:[/red] File '[bold]{filename}[/bold]' not found", style="bold red")
        sys.exit(1)
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        run(source)
    except IOError as e:
        console.print(f"[red]Error reading file:[/red] {e}", style="bold red")
        sys.exit(1)


def run_prompt() -> None:
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
    
    if script:
        run_file(script)
    else:
        run_prompt()


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
