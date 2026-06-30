# BetterLyrics.DevTools

A plugin packaging and dependency trimming tool for BetterLyrics, built with Python and PyQt5 (`qfluentwidgets`).

This tool is primarily used to read the host application's dependency manifest, compare it with the plugin's own compiled output, automatically eliminate redundant public dependencies (such as `BetterLyrics.Core.dll`), and package the streamlined output into the `.blp` format.

## Directory Structure

```text
BetterLyricsDevTools/
├── main.py                     # Program entry point and window initialization
├── i18n.py                     # Internationalization (i18n) configuration and translation dictionary
└── views/
    ├── __init__.py
    ├── packer_interface.py     # Packaging logic, file comparison, and core dependency trimming
    └── settings_interface.py   # Theme (Dark/Light) and language settings

```

## Environment

Requires Python 3.8+.

Install the necessary GUI dependencies:

```bash
pip install PyQt5 PyQt5-Tools qfluentwidgets
```

Run the application:

```bash
python main.py
```

## Usage Instructions

1. **Host JSON**: Select the dependency manifest of the main BetterLyrics host application (e.g., `*.deps.json`). The tool will extract the DLLs it contains to use as a deduplication whitelist.
2. **Plugin Bin**: Select the plugin's compilation output directory (e.g., `bin/Release/...`).
3. **Dist Output**: Specify the destination path for the packaged `.blp` file.
4. Click **Trim & Package (.blp)**.

### Trimming Logic (Smart Trim)

* **Strict Mode (Dual JSON Comparison)**: If the plugin directory contains its own `deps.json`, the program automatically calculates the difference between the host and plugin dependencies, precisely retaining only the third-party dependencies unique to the plugin.
* **Standard Fallback Mode**: If the plugin lacks a `deps.json`, the program scans the directory and directly eliminates any DLL that appears in the host's whitelist.
* **File Filtering**: The packaging process automatically discards development artifacts like `.pdb` and `_trimmingconfig` files, and includes built-in protection to prevent the plugin's main entry DLL from being accidentally deleted.

## License

MIT License © BetterLyrics