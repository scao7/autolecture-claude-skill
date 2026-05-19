#!/usr/bin/env python3
"""Pull images + README from a GitHub repo for autolecture-skill.

Sparse-checkout strategy: shallow clone with `--filter=blob:none` then
selectively materialize only image files. Avoids pulling node_modules,
LFS files, big history. README files are kept too — they often have
context for which screenshots illustrate which feature.

Writes `<out>/.manifest.json` describing each image's path, size, and
any README captions referring to it (for the figure-matching step).

Usage:
    python3 clone_github_assets.py --repo https://github.com/user/proj --out figures/
    python3 clone_github_assets.py --repo /path/to/local/repo --out figures/
    python3 clone_github_assets.py --repo user/proj --out figures/ --max-mb 50

Limits (HARD BANS in SKILL.md):
- --max-mb caps total image bytes (default 50MB); over-limit images skipped + logged.
- Single image > 10MB skipped (likely a banner / huge screenshot we don't want).
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _deps import require_system  # noqa: E402

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp"}
MAX_SINGLE_BYTES = 10 * 1024 * 1024


def _normalize_repo(repo: str) -> str:
    """`user/proj` → full GitHub URL; URLs + local paths pass through."""
    if repo.startswith(("http://", "https://", "git@", "ssh://", "/")):
        return repo
    if "/" in repo and not repo.startswith("./"):
        return f"https://github.com/{repo}"
    return repo


def _clone_or_resolve(repo: str) -> Path:
    """Return a local path to the repo. Local input → return as-is.
    Remote → shallow blob-less clone to a tempdir."""
    if Path(repo).is_dir():
        return Path(repo).resolve()
    require_system("git", apt="git", brew="git", dnf="git", pacman="git",
                   note="clones the repo (image-only sparse checkout)")
    tmp = Path(tempfile.mkdtemp(prefix="autolecture_repo_"))
    cmd = ["git", "clone", "--depth", "1", "--filter=blob:none",
           "--no-checkout", repo, str(tmp)]
    print(f"running: {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        sys.exit(f"git clone failed: {r.stderr[-400:]}")
    # Check out only images + README — sparse-checkout pattern file
    sparse_dir = tmp / ".git" / "info"
    sparse_dir.mkdir(parents=True, exist_ok=True)
    patterns = [f"*{ext}" for ext in IMAGE_EXTS] + ["README*", "readme*"]
    (sparse_dir / "sparse-checkout").write_text("\n".join(patterns) + "\n")
    subprocess.run(["git", "-C", str(tmp), "config", "core.sparseCheckout", "true"],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(tmp), "checkout"],
                   capture_output=True, text=True)
    return tmp


def _collect_images(repo_root: Path, out_dir: Path, max_bytes: int) -> tuple[list[dict], list[str]]:
    """Copy images under repo_root into out_dir, flattening with a
    path-prefix to avoid collisions. Returns (manifest entries, skipped list)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    entries: list[dict] = []
    skipped: list[str] = []
    total_bytes = 0
    for src in sorted(repo_root.rglob("*")):
        if not src.is_file(): continue
        if src.suffix.lower() not in IMAGE_EXTS: continue
        # Skip junk dirs
        parts = src.relative_to(repo_root).parts
        if any(p in {"node_modules", ".git", "__pycache__", "vendor", "dist", "build"} for p in parts):
            continue
        size = src.stat().st_size
        if size > MAX_SINGLE_BYTES:
            skipped.append(f"{src.relative_to(repo_root)} ({size // 1024 // 1024} MB > 10 MB)")
            continue
        if total_bytes + size > max_bytes:
            skipped.append(f"{src.relative_to(repo_root)} (would exceed --max-mb)")
            continue
        # Flatten: docs/images/foo.png → docs_images_foo.png
        flat = "_".join(parts)
        dst = out_dir / flat
        shutil.copy2(src, dst)
        entries.append({
            "path": flat,
            "from": str(src.relative_to(repo_root)),
            "size_bytes": size,
        })
        total_bytes += size
    return entries, skipped


def _parse_readme_image_refs(repo_root: Path) -> dict[str, list[str]]:
    """Map image-basename → list of context paragraphs from any README*."""
    refs: dict[str, list[str]] = {}
    for readme in repo_root.rglob("README*"):
        if not readme.is_file(): continue
        if any(p in {"node_modules", ".git"} for p in readme.parts): continue
        try:
            md = readme.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # Find image refs: ![alt](path) and <img src="path">
        for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", md):
            alt, path = m.group(1), m.group(2)
            base = Path(path).name
            # Context = preceding heading + the alt text
            head = ""
            heading_match = list(re.finditer(r"^(#+ .+)$", md[:m.start()], re.MULTILINE))
            if heading_match:
                head = heading_match[-1].group(1).strip()
            refs.setdefault(base, []).append(f"{head} :: {alt}".strip(" :"))
    return refs


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True, help="repo URL, user/proj shorthand, or local path")
    p.add_argument("--out", required=True, help="output directory")
    p.add_argument("--max-mb", type=int, default=50,
                   help="total image-bytes cap (default 50 MB)")
    args = p.parse_args()

    repo_str = _normalize_repo(args.repo)
    repo_root = _clone_or_resolve(repo_str)
    print(f"repo at: {repo_root}")

    out_dir = Path(args.out).resolve()
    max_bytes = args.max_mb * 1024 * 1024

    images, skipped = _collect_images(repo_root, out_dir, max_bytes)
    readme_refs = _parse_readme_image_refs(repo_root)

    # Cross-link readme captions
    for img in images:
        base = Path(img["from"]).name
        img["readme_refs"] = readme_refs.get(base, [])

    manifest = {
        "repo": repo_str,
        "image_count": len(images),
        "total_bytes": sum(i["size_bytes"] for i in images),
        "max_mb": args.max_mb,
        "skipped": skipped,
        "images": images,
    }
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    mb = manifest["total_bytes"] / 1024 / 1024
    print(f"\ncollected {len(images)} images ({mb:.1f} MB) → {out_dir}")
    if skipped:
        print(f"skipped {len(skipped)} (size cap):")
        for s in skipped[:5]: print(f"  - {s}")
        if len(skipped) > 5: print(f"  …and {len(skipped) - 5} more")

    # Clean up tempdir if we cloned
    if "/tmp/" in str(repo_root) or "/autolecture_repo_" in str(repo_root):
        shutil.rmtree(repo_root, ignore_errors=True)


if __name__ == "__main__":
    main()
