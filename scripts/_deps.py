"""Shared dep-check helpers — print install guidance, exit cleanly.

Skill policy: **fail loud, don't degrade**. When a dependency is missing
we exit non-zero with actionable next steps so the user can paste a
command and re-run. Never silently skip a step or downgrade output
quality.

Use:
    from _deps import require_pip, require_system

    require_system("pdftoppm", apt="poppler-utils", brew="poppler",
                   note="renders PDF pages to PNG")
    require_pip("pdfplumber", note="detects figure rectangles in PDFs")
"""
from __future__ import annotations

import platform
import shutil
import sys


def _box(lines: list[str]) -> str:
    """Format a multi-line install guide as a boxed warning."""
    width = max(len(l) for l in lines) + 4
    bar = "─" * width
    out = ["", "┌" + bar + "┐"]
    for ln in lines:
        out.append("│  " + ln.ljust(width - 2) + "│")
    out.append("└" + bar + "┘")
    return "\n".join(out)


def require_system(binary: str, *, apt: str | None = None,
                   brew: str | None = None, dnf: str | None = None,
                   pacman: str | None = None,
                   note: str = "") -> None:
    """Ensure a system binary is on PATH. Exit with platform-specific
    install command on failure."""
    if shutil.which(binary):
        return
    sysname = platform.system()
    lines = [f"Missing system dependency: `{binary}`"]
    if note:
        lines.append(f"  Used to: {note}")
    lines.append("")
    lines.append("Install with:")
    if sysname == "Linux":
        if apt:
            lines.append(f"  Debian/Ubuntu:  sudo apt install -y {apt}")
        if dnf:
            lines.append(f"  Fedora/RHEL:    sudo dnf install -y {dnf}")
        if pacman:
            lines.append(f"  Arch:           sudo pacman -S {pacman}")
    elif sysname == "Darwin":
        if brew:
            lines.append(f"  macOS (Homebrew):  brew install {brew}")
    else:
        lines.append(f"  See your package manager for `{binary}`")
    lines.append("")
    lines.append("Then re-run this script.")
    print(_box(lines), file=sys.stderr)
    sys.exit(2)


def require_pip(module: str, *, package: str | None = None,
                note: str = "") -> None:
    """Ensure a Python module is importable. Exit with `pip install`
    command on failure. `package` defaults to `module` — set it when
    the import name differs (e.g., module=PIL, package=Pillow).
    """
    pkg = package or module
    try:
        __import__(module)
        return
    except ImportError:
        pass
    lines = [f"Missing Python dependency: `{pkg}` (import name: `{module}`)"]
    if note:
        lines.append(f"  Used to: {note}")
    lines.append("")
    lines.append("Install with:")
    # Detect current env from sys.executable so the user installs into
    # the right interpreter (especially conda envs).
    py = sys.executable
    if "/envs/" in py:
        env_name = py.split("/envs/")[1].split("/")[0]
        lines.append(f"  conda activate {env_name}")
        lines.append(f"  pip install {pkg}")
    else:
        lines.append(f"  {py} -m pip install {pkg}")
    lines.append("")
    lines.append("Then re-run this script.")
    print(_box(lines), file=sys.stderr)
    sys.exit(2)
