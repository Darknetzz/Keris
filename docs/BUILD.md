# Building keris Executable

PyInstaller can create standalone executables for both Windows and Linux. The build process is the same on both platforms.

## Quick Build

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Build the executable:
   ```bash
   python build.py
   ```
   
   Or directly:
   ```bash
   pyinstaller --name=keris --onefile --console --clean main.py
   ```

3. The executable will be created:
   - **Windows**: `dist/keris.exe`
   - **Linux**: `dist/keris`

## Usage

After building, you can use the executable just like the Python script:

### Windows

```bash
# Run REPL
dist\keris.exe

# Run a script
dist\keris.exe examples\hello.ks
```

### Linux

```bash
# Run REPL
./dist/keris

# Run a script
./dist/keris examples/hello.ks
```

## Alternative: Manual PyInstaller Command

If you prefer to run PyInstaller directly:

```bash
pyinstaller --name=keris --onefile --console --clean main.py
```

### Options Explained

- `--name=keris`: Sets the output executable name (`keris.exe` on Windows, `keris` on Linux)
- `--onefile`: Creates a single executable file (easier to distribute)
- `--console`: Keeps the console window (needed for REPL)
- `--clean`: Cleans PyInstaller cache before building

## Cross-Platform Building

PyInstaller automatically detects the platform you're building on:
- Build on **Windows** → Creates `keris.exe`
- Build on **Linux** → Creates `keris` (executable binary)

To build for a different platform, you can use PyInstaller's cross-compilation features or build on the target platform.

## Binary Size Differences

Windows binaries are typically **larger** than Linux binaries (often 1.5-2x the size) due to several factors:

### Why Windows Binaries Are Larger

1. **Visual C++ Runtime Libraries**: Windows executables include Microsoft Visual C++ runtime libraries (MSVCRT, VCRUNTIME, etc.) which add 1-3 MB
2. **PE Format Overhead**: Windows PE (Portable Executable) format has more overhead than Linux ELF format
3. **System DLLs**: Windows may bundle additional system DLLs and dependencies
4. **Compression Differences**: UPX compression may be less effective on Windows binaries

### Reducing Windows Binary Size

If you need to reduce the Windows binary size, you can:

1. **Exclude unnecessary modules** by editing `keris.spec`:
   ```python
   a = Analysis(
       ['main.py'],
       excludes=['tkinter', 'matplotlib', 'numpy', 'pandas'],  # Add modules to exclude
       # ... other options
   )
   ```

2. **Use `--exclude-module` flag**:
   ```bash
   pyinstaller --onefile --exclude-module tkinter --exclude-module matplotlib main.py
   ```

3. **Strip debug symbols** (already enabled in spec with `strip=False` - set to `True` to enable):
   ```python
   exe = EXE(
       # ...
       strip=True,  # Remove debug symbols
   )
   ```

4. **Disable UPX** if it's causing issues (though it usually helps):
   ```python
   exe = EXE(
       # ...
       upx=False,  # Disable UPX compression
   )
   ```

**Note**: The size difference is normal and expected. Windows binaries need to be self-contained with all runtime dependencies, while Linux can rely more on system libraries.

## Distribution

The executable file in `dist/` is a standalone binary that includes Python and all dependencies. You can distribute it without requiring Python to be installed on the target machine.

**Note**: The executable is platform-specific. A Windows build will only run on Windows, and a Linux build will only run on Linux. Build on the target platform or use cross-compilation tools for multi-platform distribution.
