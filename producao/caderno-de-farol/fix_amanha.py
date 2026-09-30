#!/usr/bin/env python3
from pathlib import Path

from PIL import Image, ImageDraw

SRC = Path(
    "/Users/naubergois/.cursor/projects/Users-naubergois-canalnauber/assets/caderno-de-farol-amanha.png"
)
OUT = Path(__file__).resolve().parent / "stills" / "amanha-clean.png"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC).convert("RGB")
    w, h = im.size
    draw = ImageDraw.Draw(im)
    # tapa AMANHA no canto
    draw.rectangle((int(w * 0.78), 0, w, int(h * 0.08)), fill=(6, 10, 22))
    im.save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
