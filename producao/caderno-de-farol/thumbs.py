#!/usr/bin/env python3
"""Três capas 1280x720. Texto creme na barra preta, Arial Rounded Bold."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path("/Users/naubergois/.cursor/projects/Users-naubergois-canalnauber/assets")
ROOT = Path(__file__).resolve().parent
OUT = ROOT / "final"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1280, 720
BAR_H = 118
CREME = (247, 241, 227, 255)
PRETO = (0, 0, 0, 255)
FONT_PATH = Path("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf")


def load_fit(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    scale = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * scale), int(im.height * scale)), Image.Resampling.LANCZOS)
    left = (im.width - W) // 2
    top = (im.height - H) // 2 + 20
    return im.crop((left, top, left + W, top + H))


def bar_text(base: Image.Image, words: str) -> Image.Image:
    im = base.convert("RGBA")
    draw = ImageDraw.Draw(im)
    draw.rectangle((0, 0, W, BAR_H), fill=PRETO)
    font = ImageFont.truetype(str(FONT_PATH), 64)
    bbox = draw.textbbox((0, 0), words, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (W - tw) // 2
    y = (BAR_H - th) // 2 - 6
    draw.text((x, y), words, font=font, fill=CREME)
    return im.convert("RGB")


def save_jpg(im: Image.Image, name: str) -> Path:
    dest = OUT / name
    im.save(dest, "JPEG", quality=88, optimize=True, progressive=True)
    print(f"{dest}  {dest.stat().st_size / 1024:.0f} KB")
    return dest


CONCEPTS = [
    ("thumb-a-nao-carimba.jpg", ASSETS / "caderno-de-farol-selo.png", "NÃO CARIMBA"),
    ("thumb-b-sem-sombra.jpg", ASSETS / "cdf-sombra.png", "SEM SOMBRA"),
    ("thumb-c-tinta-viva.jpg", ASSETS / "cdf-thumb-tinta.png", "TINTA VIVA"),
]


def main() -> None:
    official = None
    for name, src, text in CONCEPTS:
        dest = save_jpg(bar_text(load_fit(src), text), name)
        if name.startswith("thumb-a-"):
            official = dest
    if official:
        lead = OUT / "thumb.jpg"
        Image.open(official).save(lead, "JPEG", quality=88, optimize=True)
        print("oficial ->", lead)


if __name__ == "__main__":
    main()
