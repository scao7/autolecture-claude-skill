#!/usr/bin/env python3
"""Extract figures from a PDF for autolecture-skill.

**Default: figures only.** We render each page to a tempdir (needed as
the source for cropping), crop every detected figure into the output
dir, and delete the temp pages. This keeps the output small and forces
the user to design real scenes per figure instead of pasting whole
pages as a lazy default.

**Opt-in: per-page rasters via `--with-pages`.** Use this ONLY when
the scene plan calls for text-highlight effects (quote a paragraph,
zoom into a formula on the page, annotate a paragraph). For everything
else, you want a clean figure crop.

Pipeline:
  1. `pdftoppm -r 144 file.pdf page` → temp dir
  2. pdfplumber detects figure rectangles + extracts caption text
  3. Pillow crops each figure from its page raster → `fig-1.png`, ...
  4. (Optional, `--with-pages`) Copy temp pages to output as
     `page-01.png` ...
  5. Always delete the temp dir
  6. Write `manifest.json` with what we extracted + captions

**No fallbacks.** All three deps (pdftoppm, pdfplumber, Pillow) are
required — skill rule is "质量优先". Missing → hard exit with the
install command.

Usage:
    python3 extract_pdf_figures.py --pdf paper.pdf --out figures/
    python3 extract_pdf_figures.py --pdf paper.pdf --out figures/ --with-pages
    python3 extract_pdf_figures.py --pdf paper.pdf --out figures/ --dpi 200

Requires:
    pdftoppm   (system; `apt install poppler-utils`)
    pdfplumber (Python; `pip install pdfplumber`)
    Pillow     (Python; `pip install Pillow`)
"""
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# Sibling _deps.py — guides install on missing deps. Sys.path insert
# so we work both as `python3 extract_pdf_figures.py …` and as
# `python3 -m scripts.extract_pdf_figures …`.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _deps import require_system, require_pip  # noqa: E402


def _run_pdftoppm(pdf: Path, dest: Path, dpi: int) -> list[Path]:
    """Render every page to a PNG under `dest`. Returns sorted list."""
    require_system("pdftoppm",
                   apt="poppler-utils", brew="poppler",
                   dnf="poppler-utils", pacman="poppler",
                   note="renders PDF pages to PNG (PDF figure extraction)")
    dest.mkdir(parents=True, exist_ok=True)
    prefix = dest / "page"
    cmd = ["pdftoppm", "-r", str(dpi), "-png", str(pdf), str(prefix)]
    print(f"running: {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"pdftoppm failed: {r.stderr[-400:]}")
    pages = sorted(dest.glob("page-*.png"))
    print(f"  → {len(pages)} pages at {dpi} DPI")
    return pages


def _extract_figures_pdfplumber(pdf: Path, out_dir: Path, page_pngs: list[Path]) -> list[dict]:
    """Figure extraction using pdfplumber's image/figure detection + Pillow
    crop. Returns a list of dicts:
        {"path": "fig-1.png", "page": 3, "caption": "Figure 1: …"}

    No-fallback policy — missing pdfplumber or Pillow exits the whole
    script. Skill rule: PDF mode either delivers figures or nothing.
    """
    require_pip("pdfplumber",
                note="detects figure bounding boxes in PDFs (PDF figure extraction)")
    require_pip("PIL", package="Pillow",
                note="crops figures from rendered page rasters (PDF figure extraction)")
    import pdfplumber
    from PIL import Image

    figures: list[dict] = []
    fig_idx = 0
    with pdfplumber.open(str(pdf)) as doc:
        for page_num, page in enumerate(doc.pages, start=1):
            page_png = page_pngs[page_num - 1] if page_num <= len(page_pngs) else None
            if not page_png or not page_png.is_file():
                continue
            page_img = Image.open(page_png)
            page_w_pt = page.width
            page_h_pt = page.height
            img_w_px = page_img.width
            img_h_px = page_img.height

            # pdfplumber yields detected figures (table-like blocks too).
            # We filter to images + figure-flagged regions.
            candidates = []
            for img in page.images:
                # img: dict with x0, y0, x1, y1 in PDF points (origin
                # bottom-left for pdfplumber's `images`, top-left for
                # most graphics — we double-check by clamping).
                candidates.append((img["x0"], img["top"], img["x1"], img["bottom"]))
            for fig in getattr(page, "figures", []) or []:
                candidates.append((fig["x0"], fig["top"], fig["x1"], fig["bottom"]))

            # Caption lookup: take the text immediately below the figure
            # bbox (~30pt window) and trim to start with "Figure"/"Fig.".
            page_text_words = page.extract_words() or []

            for x0, y0, x1, y1 in candidates:
                if x1 - x0 < 60 or y1 - y0 < 60:
                    continue   # skip tiny inline icons
                # PDF-point bbox → page-image-pixel bbox
                px0 = max(0, int(x0 / page_w_pt * img_w_px))
                py0 = max(0, int(y0 / page_h_pt * img_h_px))
                px1 = min(img_w_px, int(x1 / page_w_pt * img_w_px))
                py1 = min(img_h_px, int(y1 / page_h_pt * img_h_px))
                if px1 - px0 < 80 or py1 - py0 < 80:
                    continue
                fig_idx += 1
                crop = page_img.crop((px0, py0, px1, py1))
                out_path = out_dir / f"fig-{fig_idx}.png"
                crop.save(out_path, optimize=True)

                # Find caption: words within 40pt below the figure
                caption = ""
                for w in page_text_words:
                    if y1 < w["top"] < y1 + 40 and x0 - 20 < w["x0"] < x1 + 20:
                        caption += w["text"] + " "
                caption = caption.strip()
                # Trim to "Figure N: …" if visible
                low = caption.lower()
                for prefix in ("figure", "fig.", "fig "):
                    if prefix in low:
                        caption = caption[low.index(prefix):]
                        break

                figures.append({
                    "path": out_path.name,
                    "page": page_num,
                    "caption": caption[:200],
                })
            page_img.close()

    print(f"  → {len(figures)} figures extracted")
    return figures


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pdf", required=True, help="input PDF path")
    p.add_argument("--out", required=True, help="output directory")
    p.add_argument("--dpi", type=int, default=144, help="raster DPI (default 144)")
    p.add_argument(
        "--with-pages", action="store_true",
        help=("ALSO keep per-page rasters in output (page-01.png .. page-NN.png). "
              "Default is figures-only — pages live only in a tempdir long enough "
              "to be cropped. Turn this on when the scene plan involves text-"
              "highlight effects (quote a paragraph / zoom a formula on the page)."),
    )
    args = p.parse_args()

    pdf = Path(args.pdf).resolve()
    if not pdf.is_file():
        sys.exit(f"PDF not found: {pdf}")
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Render pages to a tempdir; cropping needs them. They only land in
    # `out_dir` if --with-pages is set.
    pages_dest = out_dir if args.with_pages else Path(tempfile.mkdtemp(prefix="pdf_pages_"))
    try:
        page_pngs = _run_pdftoppm(pdf, pages_dest, args.dpi)
        figures = _extract_figures_pdfplumber(pdf, out_dir, page_pngs)
    finally:
        # Clean up tempdir if we own it (i.e., --with-pages NOT set)
        if pages_dest != out_dir:
            shutil.rmtree(pages_dest, ignore_errors=True)

    manifest = {
        "pdf": str(pdf),
        "dpi": args.dpi,
        "figures": figures,
        "pages_kept": args.with_pages,
        "page_count": len(page_pngs),
    }
    if args.with_pages:
        manifest["pages"] = [{"page": i + 1, "path": p.name} for i, p in enumerate(page_pngs)]
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2),
                              encoding="utf-8")
    print(f"\nwrote {manifest_path}")
    print(f"  figures: {len(figures)}"
          + (f"  +  pages: {len(page_pngs)}" if args.with_pages else "  (pages discarded — pass --with-pages to keep)"))


if __name__ == "__main__":
    main()
