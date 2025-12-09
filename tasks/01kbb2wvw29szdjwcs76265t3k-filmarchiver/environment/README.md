# Film Archiver Environment

This environment sets up the broken state of the Film Archiver application at v1.2.0.

## Broken State

**Commit**: 075453d1afe3f0b6b5f08dc82364d01469208c72 (v1.2.0)

### Issue 1: Phantom Tk Window

The `main.py` file has a top-level import:
```python
from tkinter import messagebox
```

This creates a hidden Tk() root window when the module loads, which remains as a blank window titled "tk" after the main application closes.

### Issue 2: Basic DMG Installer

The `create_dmg.sh` script is basic with no visual guidance for users on how to install the application.

## Dependencies

- Python 3
- Pillow (for testing DMG background generation)
- uv (for test environment management)

## Structure

The application code is in the `film_archiver_app/` subdirectory.