#!/usr/bin/env python3
"""
Scale images in a folder to multiple square sizes and save as PNG into a single output folder.

Usage:
  python scale_images.py input output

- fit  (default): Bild proportional verkleinern und transparent auf Quadrat „einpassen“.
- cover: Bild mittig auf Quadrat zuschneiden (ohne Ränder) und dann skalieren.
"""

from pathlib import Path
from PIL import Image, ImageOps
import sys

SIZES = [1024, 512, 256, 128, 64, 32]
SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".heic"}  # HEIC evtl. Plugin nötig

def make_square_fit(img: Image.Image, size: int) -> Image.Image:
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGBA", "LA"):
        img = img.convert("RGBA")
    img_thumb = img.copy()
    img_thumb.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - img_thumb.width) // 2
    y = (size - img_thumb.height) // 2
    canvas.paste(img_thumb, (x, y), img_thumb)
    return canvas

def make_square_cover(img: Image.Image, size: int) -> Image.Image:
    img = ImageOps.exif_transpose(img)
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img_cropped = img.crop((left, top, left + side, top + side))
    img_cropped = img_cropped.resize((size, size), Image.Resampling.LANCZOS)
    if img_cropped.mode not in ("RGBA", "LA"):
        img_cropped = img_cropped.convert("RGBA")
    return img_cropped

def process_image(in_path: Path, out_dir: Path, mode: str = "fit") -> None:
    try:
        with Image.open(in_path) as img:
            for s in SIZES:
                if mode == "cover":
                    out_img = make_square_cover(img, s)
                else:
                    out_img = make_square_fit(img, s)

                out_name = f"{in_path.stem}_{s}x{s}.png"
                out_path = out_dir / out_name
                out_img.save(out_path, format="PNG", optimize=True)
        print(f"OK  : {in_path.name}")
    except Exception as e:
        print(f"FEHLER bei {in_path}: {e}")

def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    in_dir = Path(sys.argv[1]).expanduser().resolve()
    out_dir = Path(sys.argv[2]).expanduser().resolve()
    mode = "fit"

    if len(sys.argv) >= 4:
        m = sys.argv[3].lower()
        if m in ("fit", "--mode=fit"):
            mode = "fit"
        elif m in ("cover", "--mode=cover"):
            mode = "cover"
        elif m.startswith("--mode="):
            mode = m.split("=", 1)[1]
        else:
            mode = m
        if mode not in ("fit", "cover"):
            print("Ungültiger --mode. Erlaubt: fit | cover")
            sys.exit(2)

    if not in_dir.exists() or not in_dir.is_dir():
        print(f"Eingabeordner nicht gefunden: {in_dir}")
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(
        p for p in in_dir.iterdir()
        if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES
    )

    if not images:
        print("Keine unterstützten Bilddateien im Eingabeordner gefunden.")
        sys.exit(0)

    print(f"Verarbeite {len(images)} Dateien aus {in_dir} → {out_dir} (mode={mode})")
    for p in images:
        process_image(p, out_dir, mode)

if __name__ == "__main__":
    main()
