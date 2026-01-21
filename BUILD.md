# Building keris.exe

## Quick Build

Build the executable using pybin:

```bash
python build_exe.py
```

Or directly:
```bash
D:/Bin/!custombins/pybin.exe --name=keris --onefile --console --clean main.py
```

The executable will be created at `dist/keris.exe`

## Usage

After building, you can use `keris.exe` just like the Python script:

```bash
# Run REPL
dist\keris.exe

# Run a script
dist\keris.exe examples\hello.ks
```

## Build Options

The build script uses the following options:

- `--name=keris`: Sets the output executable name to `keris.exe`
- `--onefile`: Creates a single executable file (easier to distribute)
- `--console`: Keeps the console window (needed for REPL)
- `--clean`: Cleans cache before building

## Distribution

The `dist/keris.exe` file is a standalone executable that includes Python and all dependencies. You can distribute it without requiring Python to be installed on the target machine.
