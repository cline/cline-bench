"""
Test suite for Film Archiver v1.2.1 fixes:
1. Phantom tk window fix (lazy import pattern)
2. DMG installer UX improvements (background image + visual guide)
"""
import os
import subprocess
from pathlib import Path


def test_main_py_no_top_level_messagebox_import():
    """
    Test that main.py does NOT have top-level 'from tkinter import messagebox' import.
    This was the bug - importing messagebox at module level creates phantom Tk window.
    """
    main_py = Path("/app/film_archiver_app/main.py")
    assert main_py.exists(), "main.py should exist"
    
    content = main_py.read_text()
    lines = content.split('\n')
    
    # Check that NO line in the top-level imports has 'from tkinter import messagebox'
    # Top-level means before the main() function definition
    in_main_function = False
    top_level_imports = []
    
    for line in lines:
        if 'def main(' in line:
            in_main_function = True
            break
        if 'import' in line and 'messagebox' in line:
            top_level_imports.append(line.strip())
    
    # Should have NO top-level imports of messagebox
    assert len(top_level_imports) == 0, \
        f"Found top-level messagebox import (causes phantom tk window): {top_level_imports}"


def test_main_py_has_lazy_import_in_exception_handler():
    """
    Test that main.py DOES have lazy import of messagebox inside exception handler.
    This is the fix - defer import until actually needed.
    """
    main_py = Path("/app/film_archiver_app/main.py")
    content = main_py.read_text()
    
    # Should have 'from tkinter import messagebox' somewhere in the file
    assert 'from tkinter import messagebox' in content, \
        "Should have messagebox import somewhere"
    
    # Should have comment about lazy import / phantom windows
    assert 'lazy import' in content.lower() or 'phantom' in content.lower(), \
        "Should have comment explaining the lazy import pattern to prevent phantom windows"
    
    # The import should be inside the exception handler (after 'except Exception')
    lines = content.split('\n')
    found_except = False
    found_lazy_import = False
    
    for i, line in enumerate(lines):
        if 'except Exception' in line:
            found_except = True
        if found_except and 'from tkinter import messagebox' in line:
            found_lazy_import = True
            break
    
    assert found_lazy_import, \
        "Should have lazy messagebox import inside exception handler"


def test_create_dmg_background_py_exists():
    """
    Test that create_dmg_background.py script exists.
    This is the new file that generates the DMG background image with visual guide.
    """
    script = Path("/app/film_archiver_app/create_dmg_background.py")
    assert script.exists(), "create_dmg_background.py should exist"
    
    content = script.read_text()
    
    # Should be substantial (not just a stub)
    assert len(content) > 1000, \
        "create_dmg_background.py should have substantial content (>1000 chars)"
    
    # Should use PIL/Pillow for image generation
    assert 'from PIL import Image' in content or 'import PIL' in content, \
        "Should use PIL for image generation"
    
    # Should have function to create DMG background
    assert 'def create_dmg_background' in content, \
        "Should have create_dmg_background function"
    
    # Should generate arrow visual guide
    assert 'arrow' in content.lower(), \
        "Should create arrow graphic for visual guide"
    
    # Should have instruction text
    assert 'Applications' in content, \
        "Should reference Applications folder in visual"


def test_create_dmg_background_py_can_run():
    """
    Test that create_dmg_background.py can actually run and generate an image.
    This verifies the DMG background generation infrastructure works.
    """
    script = Path("/app/film_archiver_app/create_dmg_background.py")
    output_path = Path("/tmp/test_dmg_background.png")
    
    # Remove output if it exists from previous test
    if output_path.exists():
        output_path.unlink()
    
    # Run the script with output path
    result = subprocess.run(
        ["python3", str(script)],
        cwd="/app/film_archiver_app",
        capture_output=True,
        text=True
    )
    
    # Script should run successfully
    assert result.returncode == 0, \
        f"create_dmg_background.py should run without errors. stderr: {result.stderr}"
    
    # Should create dmg_background.png in the script's directory
    expected_output = Path("/app/film_archiver_app/dmg_background.png")
    assert expected_output.exists(), \
        "Should create dmg_background.png file"
    
    # Image should be substantial (not empty)
    assert expected_output.stat().st_size > 1000, \
        "Generated image should be substantial (>1KB)"


def test_create_dmg_sh_has_background_customization():
    """
    Test that create_dmg.sh has been enhanced with background image customization.
    """
    script = Path("/app/film_archiver_app/create_dmg.sh")
    assert script.exists(), "create_dmg.sh should exist"
    
    content = script.read_text()
    
    # Should call create_dmg_background.py to generate image
    assert 'create_dmg_background.py' in content, \
        "Should call create_dmg_background.py to generate background"
    
    # Should create .background directory for the image
    assert '.background' in content, \
        "Should create .background directory for DMG background image"
    
    # Should use AppleScript for Finder customization
    assert 'osascript' in content or 'AppleScript' in content, \
        "Should use AppleScript for Finder window customization"
    
    # Should set background picture
    assert 'background picture' in content.lower() or 'set background' in content.lower(), \
        "Should set DMG background picture"
    
    # Should position icons (app and Applications alias)
    assert 'position of item' in content or 'set position' in content, \
        "Should set icon positions in DMG window"
    
    # Should mention Applications (for the symlink/alias)
    assert 'Applications' in content, \
        "Should create Applications folder symlink"


def test_python_syntax_valid():
    """
    Test that all modified Python files have valid syntax.
    """
    python_files = [
        Path("/app/film_archiver_app/main.py"),
        Path("/app/film_archiver_app/create_dmg_background.py"),
    ]
    
    for py_file in python_files:
        if py_file.exists():
            result = subprocess.run(
                ["python3", "-m", "py_compile", str(py_file)],
                capture_output=True,
                text=True
            )
            assert result.returncode == 0, \
                f"{py_file.name} should have valid Python syntax. Error: {result.stderr}"