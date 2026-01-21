"""Generate documentation from docstrings in stdlib.py.

This script dynamically extracts docstrings from the standard library
and generates markdown documentation, ensuring it stays in sync with the code.
"""

import inspect
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple

import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from stdlib import create_stdlib


def parse_docstring(docstring: str) -> Dict[str, Any]:
    """Parse a docstring into structured components.
    
    Args:
        docstring: The docstring to parse.
        
    Returns:
        Dictionary with keys: description, args, returns, example, note
    """
    if not docstring:
        return {}
    
    result = {
        "description": "",
        "args": [],
        "returns": "",
        "example": "",
        "note": ""
    }
    
    lines = docstring.strip().split('\n')
    current_section = "description"
    current_content = []
    
    for line in lines:
        line = line.strip()
        
        # Detect section headers
        if line.lower().startswith("args:"):
            # Save previous section
            if current_section == "description":
                result["description"] = "\n".join(current_content).strip()
            current_section = "args"
            current_content = []
            continue
        elif line.lower().startswith("returns:"):
            if current_section == "args":
                result["args"] = _parse_args(current_content)
            elif current_section == "description":
                result["description"] = "\n".join(current_content).strip()
            current_section = "returns"
            current_content = []
            continue
        elif line.lower().startswith("example:"):
            if current_section == "returns":
                result["returns"] = "\n".join(current_content).strip()
            elif current_section == "description":
                result["description"] = "\n".join(current_content).strip()
            current_section = "example"
            current_content = []
            continue
        elif line.lower().startswith("note:"):
            if current_section == "example":
                result["example"] = "\n".join(current_content).strip()
            elif current_section == "returns":
                result["returns"] = "\n".join(current_content).strip()
            elif current_section == "description":
                result["description"] = "\n".join(current_content).strip()
            current_section = "note"
            current_content = []
            continue
        else:
            current_content.append(line)
    
    # Save final section
    if current_section == "description":
        result["description"] = "\n".join(current_content).strip()
    elif current_section == "returns":
        result["returns"] = "\n".join(current_content).strip()
    elif current_section == "example":
        result["example"] = "\n".join(current_content).strip()
    elif current_section == "note":
        result["note"] = "\n".join(current_content).strip()
    elif current_section == "args":
        result["args"] = _parse_args(current_content)
    
    return result


def _parse_args(args_content: List[str]) -> List[Dict[str, str]]:
    """Parse Args section into list of parameter dictionaries.
    
    Args:
        args_content: Lines from the Args section.
        
    Returns:
        List of dicts with 'name', 'type', 'description' keys.
    """
    args = []
    current_arg = None
    
    for line in args_content:
        if not line:
            continue
        
        # Check for parameter definition with type (e.g., "x (number): The number.")
        match_with_type = re.match(r'^(\w+(?:\*|\.\.\.)?)\s*\(([^)]+)\):\s*(.+)$', line)
        # Check for parameter definition without type (e.g., "*args: Variable number...")
        match_without_type = re.match(r'^(\w+(?:\*|\.\.\.)?):\s*(.+)$', line)
        
        if match_with_type:
            if current_arg:
                args.append(current_arg)
            current_arg = {
                "name": match_with_type.group(1),
                "type": match_with_type.group(2),
                "description": match_with_type.group(3).strip()
            }
        elif match_without_type:
            if current_arg:
                args.append(current_arg)
            current_arg = {
                "name": match_without_type.group(1),
                "type": None,
                "description": match_without_type.group(2).strip()
            }
        elif current_arg:
            # Continuation of description (handle indented lines)
            if line.startswith(" ") or line.startswith("\t"):
                # Continuation line - add to description
                current_arg["description"] += " " + line.strip()
            else:
                # New parameter without explicit marker - might be malformed docstring
                # But we'll try to parse it as a continuation
                current_arg["description"] += " " + line
    
    if current_arg:
        args.append(current_arg)
    
    return args


def get_function_signature(func: Any, func_name: str) -> str:
    """Get function signature as a string.
    
    Args:
        func: The function object.
        func_name: The name of the function.
        
    Returns:
        String representation of the function signature.
    """
    try:
        sig = inspect.signature(func)
        params = []
        for param_name, param in sig.parameters.items():
            if param.default != inspect.Parameter.empty:
                default = param.default
                if isinstance(default, str):
                    default = f'"{default}"'
                params.append(f"{param_name}={default}")
            elif param.kind == inspect.Parameter.VAR_POSITIONAL:
                params.append(f"*{param_name}")
            elif param.kind == inspect.Parameter.VAR_KEYWORD:
                params.append(f"**{param_name}")
            else:
                params.append(param_name)
        
        param_str = ", ".join(params)
        return f"{func_name}({param_str})"
    except (ValueError, TypeError):
        # For built-in functions or functions without signatures
        return func_name


def format_function_doc(name: str, func: Any, module_name: str = None) -> str:
    """Format a single function's documentation as markdown.
    
    Args:
        name: The function name in Keris.
        func: The function object.
        module_name: Optional module name prefix (e.g., "math", "str").
        
    Returns:
        Markdown formatted documentation string.
    """
    docstring = inspect.getdoc(func)
    if not docstring:
        return ""
    
    parsed = parse_docstring(docstring)
    
    # Build markdown
    parts = []
    
    # Function name and signature
    full_name = f"{module_name}.{name}" if module_name else name
    sig = get_function_signature(func, full_name)
    parts.append(f"#### `{full_name}`\n")
    parts.append(f"```keris\n{sig}\n```\n")
    
    # Description
    if parsed["description"]:
        parts.append(f"{parsed['description']}\n")
    
    # Arguments
    if parsed["args"]:
        parts.append("**Parameters:**\n")
        for arg in parsed["args"]:
            type_info = f" ({arg['type']})" if arg.get('type') else ""
            parts.append(f"- `{arg['name']}`{type_info}: {arg['description']}\n")
        parts.append("\n")
    
    # Returns
    if parsed["returns"]:
        parts.append(f"**Returns:** {parsed['returns']}\n\n")
    
    # Example
    if parsed["example"]:
        # Convert Keris comments to markdown code blocks
        example_code = parsed["example"]
        # Replace // comments with # for Keris (they're the same but # is more standard)
        example_code = example_code.replace(" // ", "  # ")
        parts.append("**Example:**\n")
        parts.append(f"```keris\n{example_code}\n```\n\n")
    
    # Note
    if parsed["note"]:
        parts.append(f"**Note:** {parsed['note']}\n\n")
    
    return "\n".join(parts)


def generate_stdlib_docs() -> str:
    """Generate complete standard library documentation.
    
    Returns:
        Markdown formatted documentation string.
    """
    stdlib = create_stdlib()
    
    sections = []
    
    # I/O Functions
    io_funcs = ["print", "read_line", "read_number"]
    if any(name in stdlib for name in io_funcs):
        sections.append("### I/O\n\n")
        for name in io_funcs:
            if name in stdlib:
                func = stdlib[name]
                sections.append(format_function_doc(name, func))
        sections.append("\n")
    
    # Math Module
    if "math" in stdlib and isinstance(stdlib["math"], dict):
        sections.append("### Math\n\n")
        math_module = stdlib["math"]
        
        # Sort functions before constants
        funcs = {}
        constants = {}
        for name, value in math_module.items():
            if callable(value):
                funcs[name] = value
            else:
                constants[name] = value
        
        # Functions
        for name in sorted(funcs.keys()):
            sections.append(format_function_doc(name, funcs[name], "math"))
        
        # Constants
        if constants:
            sections.append("**Constants:**\n\n")
            for name in sorted(constants.keys()):
                value = constants[name]
                sections.append(f"- `math.{name}`: {value}\n")
            sections.append("\n")
    
    # String Module
    if "str" in stdlib and isinstance(stdlib["str"], dict):
        sections.append("### String\n\n")
        str_module = stdlib["str"]
        for name in sorted(str_module.keys()):
            if callable(str_module[name]):
                sections.append(format_function_doc(name, str_module[name], "str"))
        sections.append("\n")
    
    # List Module
    if "list" in stdlib and isinstance(stdlib["list"], dict):
        sections.append("### List\n\n")
        list_module = stdlib["list"]
        for name in sorted(list_module.keys()):
            if callable(list_module[name]):
                sections.append(format_function_doc(name, list_module[name], "list"))
        sections.append("\n")
    
    # Dict Module
    if "dict" in stdlib and isinstance(stdlib["dict"], dict):
        sections.append("### Dict\n\n")
        dict_module = stdlib["dict"]
        for name in sorted(dict_module.keys()):
            if callable(dict_module[name]):
                sections.append(format_function_doc(name, dict_module[name], "dict"))
        sections.append("\n")
    
    # Type Module
    if "type" in stdlib and isinstance(stdlib["type"], dict):
        sections.append("### Type\n\n")
        type_module = stdlib["type"]
        for name in sorted(type_module.keys()):
            if callable(type_module[name]):
                sections.append(format_function_doc(name, type_module[name], "type"))
        sections.append("\n")
    
    # Range function
    if "range" in stdlib:
        sections.append("### Range\n\n")
        sections.append(format_function_doc("range", stdlib["range"]))
        sections.append("\n")
    
    return "".join(sections)


def update_readme_section(readme_path: Path, new_content: str):
    """Update the Standard Library section in README.md.
    
    Args:
        readme_path: Path to README.md.
        new_content: New content for the Standard Library section.
    """
    readme = readme_path.read_text(encoding="utf-8")
    
    # Find the Standard Library section
    start_marker = "## Standard Library"
    end_marker = "## Examples"
    
    start_idx = readme.find(start_marker)
    end_idx = readme.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print("Warning: Could not find Standard Library section markers in README.md")
        return
    
    # Replace the section
    before = readme[:start_idx + len(start_marker)]
    after = readme[end_idx:]
    
    new_readme = f"{before}\n\n{new_content}\n{after}"
    readme_path.write_text(new_readme, encoding="utf-8")
    print(f"[OK] Updated {readme_path}")


def main():
    """Main entry point."""
    print("Generating documentation from docstrings...")
    
    # Generate documentation
    docs = generate_stdlib_docs()
    
    # Update README.md
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        update_readme_section(readme_path, docs)
    else:
        print(f"Warning: {readme_path} not found")
    
    # Optionally write to a separate file
    docs_path = Path(__file__).parent / "docs" / "stdlib.md"
    docs_path.parent.mkdir(exist_ok=True)
    docs_path.write_text(f"# Standard Library Reference\n\n{docs}", encoding="utf-8")
    print(f"[OK] Generated {docs_path}")
    
    print("\nDocumentation generation complete!")


if __name__ == "__main__":
    main()
