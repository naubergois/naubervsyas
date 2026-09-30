#!/usr/bin/env python3
"""Página limpa + letra em português, sem inglês do gerador."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path(
    "/Users/naubergois/.cursor/projects/Users-naubergois-canalnauber/assets/cdf-pagina-limpa.png"
)
OUT = Path(__file__).resolve().parent / "stills" / "pagina-pt.png"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(SRC).convert("RGBA")
    w, h = im.size
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    # tapa VAZIO / EMPTY
    draw.rectangle((int(w * 0.10), int(h * 0.08), int(w * 0.38), int(h * 0.22)), fill=(244, 236, 214, 255))
    draw.rectangle((int(w * 0.18), int(h * 0.72), int(w * 0.48), int(h * 0.88)), fill=(244, 236, 214, 255))
    script = ImageFont.truetype("/System/Library/Fonts/Supplemental/SnellRoundhand.ttc", 58)
    stamp = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf", 26)
    draw.text((int(w * 0.16), int(h * 0.30)), "Não carimba essa.", font=script, fill=(40, 32, 24, 255))
    sx, sy = int(w * 0.58), int(h * 0.22)
    draw.rectangle((sx, sy, sx + 118, sy + 38), outline=(200, 160, 30, 255), width=3)
    draw.text((sx + 10, sy + 6), "25 SET", font=stamp, fill=(160, 120, 20, 255))
    Image.alpha_composite(im, overlay).convert("RGB").save(OUT)
    print(OUT)


if __name__ == "__main__":
    main()
