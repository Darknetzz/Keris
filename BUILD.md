# Building keris.exe

## Quick Build

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   python build_exe.py
   ```
   
   Or directly:
   ```bash
   pyinstaller --name=keris --onefile --console --clean main.py
   ```

3. The executable will be created at `dist/keris.exe`

## Usage

After building, you can use `keris.exe` just like the Python script:

```bash
# Run REPL
dist\keris.exe

# Run a script
dist\keris.exe examples\hello.ks
```

## Alternative: Manual PyInstaller Command

If you prefer to run PyInstaller directly:

```bash
pyinstaller --name=keris --onefile --console --clean main.py
```

### Options Explained

- `--name=keris`: Sets the output executable name to `keris.exe`
- `--onefile`: Creates a single executable file (easier to distribute)
- `--console`: Keeps the console window (needed for REPL)
- `--clean`: Cleans PyInstaller cache before building

## Distribution

The `dist/keris.exe` file is a standalone executable that includes Python and all dependencies. You can distribute it without requiring Python to be installed on the target machine.
