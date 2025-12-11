# Film Archiver: Phantom Window & DMG Polish

@Wetdogtaste just shipped v1.2.0 of their macOS film photography app. They built the DMG, tested the installer, ran the app, closed it... and noticed a small blank window titled "tk" lingering in the upper left corner. Weird. Unprofessional. Not supposed to happen.

They also realized their DMG installer, while functional, gave users no visual cue about what to do. Just an app icon and an Applications folder. No arrow, no instruction, no "drag me here" guidance. First-time users would be confused.

These are the kinds of polish issues that separate hobby projects from professional software. The app worked fine - it managed film photography metadata, organized scans, tracked camera bodies and film stocks. But little quality-of-life problems like phantom windows make otherwise solid software feel janky.

The fix took 20 minutes. The phantom window? A tkinter import timing issue - importing `messagebox` at the top level instantiates an invisible Tk root that never gets cleaned up. Solution: lazy import inside the exception handler where it's actually used. The DMG problem? Create a Python script using PIL to generate a custom background image with an arrow and "Drag to Applications" text, then wire it into the DMG build process with AppleScript for proper window positioning.

This environment teaches practical desktop application development. Agents must diagnose a subtle Python/tkinter quirk (when does module initialization create side effects?) and implement macOS-specific packaging polish (DMG customization, visual guides, platform conventions). It's not flashy, but it's the kind of work that makes software feel professional. The Terminus agent we tested found both fixes correctly but then spent 25 episodes trying to rebuild the app with PyInstaller - getting stuck on Python version mismatches and virtual environment issues. That's authentic too: even when you know the fix, tooling can derail you.

---

## Technical Details

**The bugs:**
1. Phantom "tk" window remains after closing app (tkinter initialization side effect)
2. DMG installer lacks visual guidance (blank window, no drag instruction)

**The fixes:**
1. Change `from tkinter import messagebox` from top-level import to lazy import inside exception handler
2. Add `create_dmg_background.py` script that generates background image with PIL
3. Enhance `create_dmg.sh` with AppleScript for Finder customization and icon positioning
4. Update version 1.2.0 → 1.2.1 across spec file and build scripts

**Total changes:** ~250 lines across 6 files (main.py, create_dmg_background.py, create_dmg.sh, Film_Archiver.spec, build_dmg.sh, dmg_background.png)

**Verification:**
- Import location test (structural - no top-level messagebox import)
- Lazy import test (structural - import inside exception handler with comment)
- Background generator exists (structural - has PIL, has arrow, has "Applications" text)
- Background generator runs (behavioral - actually executes, creates PNG >1KB)
- DMG script enhanced (structural - has .background dir, AppleScript, icon positions)
- Python syntax valid (compilation - all files parse correctly)

**Repository:** [Wetdogtaste/Film-Archiver](https://github.com/Wetdogtaste/Film-Archiver)  
**Broken:** commit `075453d1` (v1.2.0, Nov 30 2025 19:00 UTC)  
**Fixed:** commit `928fa124` (v1.2.1, Nov 30 2025 19:33 UTC - 20 minutes later)

**Build environment:**
- Python 3.x with tkinter (macOS system Python works)
- PyInstaller for app bundling (not required for tests)
- PIL/Pillow for DMG background generation
- macOS hdiutil/bless for DMG creation (not required for tests)

**Why it's valuable:**
This is a focused dual-issue task with fast turnaround (20 minutes). It teaches:
- Python import timing and side effects (when does `import` execute code?)
- PyInstaller bundling considerations (console mode, cleanup handlers)
- macOS packaging conventions (DMG backgrounds, visual guidance)
- User experience polish (what makes installation obvious?)
- Version management discipline (coordinating version bumps)

The tkinter bug is particularly instructive - it demonstrates how module-level imports can have unexpected side effects. Many Python developers don't realize `from tkinter import X` instantiates a Tk root immediately, while `import tkinter; tkinter.X` defers initialization. This is authentic debugging knowledge.

**Why tests are structural:**
The phantom window bug is fundamentally about import timing. A truly behavioral test would require building the macOS app with PyInstaller, launching it, closing it, then using macOS UI automation to detect windows titled "tk". That's complex, slow, and fragile in Docker.

Instead, we test the root cause directly: is the import at the top level (bug) or inside a function (fix)? This captures the essence of the fix without requiring macOS build tooling. For the DMG, we do test behaviorally where feasible - the background generator actually runs and we verify it produces output.

**Docker naming gotcha:**
Task directory must not have internal hyphens. Harbor generates Docker image names from the path, and `01kbb2wvw29szdjwcs76265t3k-film-archiver` produces `film-__<random>` with double underscores (invalid Docker name). Solution: `01kbb2wvw29szdjwcs76265t3k-filmarchiver` works fine.

**Environment gap identified:**
The Docker container has a broken Python venv from different user (`/Users/michaelziebell/...`) and no `python` symlink (only `python3`). Agents trying to rebuild hit pip externally-managed-environment errors. Future improvement: pre-install PyInstaller or clean up venv paths. However, since tests verify code changes not builds, this doesn't block validation.

**Agent results:**
- **Oracle:** 1.0 (reference solution passes all 7 tests)
- **Nop:** 0.0 (broken state correctly fails all tests)
- **Terminus:** 0.0 after 45 episodes (found both fixes in episodes 7-14, then spent episodes 15-45 stuck trying to rebuild with broken dependencies)

**Build time:** ~5 minutes (1min Dockerfile, instant solution script, 3min test suite with pytest)

**User satisfaction criteria:**
The user reported two specific problems and asked for fixes "keeping in mind maintaining a cohesive macos visual is important." Both requirements are binary:
1. Does phantom tk window appear? (yes = fail, no = pass)
2. Does DMG show drag-to-Applications guidance? (yes = pass, no = fail)

Our tests verify exactly what the user cared about, nothing more.