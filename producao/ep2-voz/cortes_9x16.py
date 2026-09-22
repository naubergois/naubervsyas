#!/usr/bin/env python3
"""Recortes 9:16 do ep. 2. Sem vinheta. Um encode por vez."""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SRC = Path("/Users/naubergois/canalnauber/producao/ep2-voz/final/ep2-youtube.mp4")
OUT = Path("/Users/naubergois/canalnauber/producao/ep2-voz/final")
TMP = Path("/tmp/ep2-cuts")
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
W, H = 1080, 1920
CREAM = (247, 241, 227, 255)
BAR = (10, 10, 12, 158)

TMP.mkdir(parents=True, exist_ok=True)


def card(name: str, lines: list[str], y0: int, box_h: int, fs: int) -> Path:
    dest = TMP / name
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, fs)
    d.rectangle((0, y0, W, y0 + box_h), fill=BAR)
    sizes = []
    total = 0
    for line in lines:
        b = d.textbbox((0, 0), line, font=font)
        sizes.append((b[2] - b[0], b[3] - b[1]))
        total += b[3] - b[1] + 12
    y = y0 + (box_h - total) // 2
    for line, (w, h) in zip(lines, sizes):
        d.text(((W - w) // 2, y), line, font=font, fill=CREAM)
        y += h + 12
    im.save(dest)
    return dest


def render(start: float, dur: float, dest: Path, overlays: list[tuple[str, str]]) -> None:
    inputs = ["-ss", str(start), "-t", str(dur), "-i", str(SRC)]
    chain = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,setsar=1[v0]"
    )
    last = "v0"
    n = 1
    for i, (png, enable) in enumerate(overlays, start=1):
        inputs += ["-loop", "1", "-i", str(TMP / png)]
        nxt = f"v{i}"
        chain += f";[{last}][{n}:v]overlay=0:0:enable='{enable}'[{nxt}]"
        last = nxt
        n += 1
    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", chain,
        "-map", f"[{last}]", "-map", "0:a", "-t", str(dur),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        "-r", "30", "-movflags", "+faststart",
        str(dest),
    ]
    print("==", dest.name, flush=True)
    subprocess.run(cmd, check=True)


def main() -> None:
    card("luta-hook.png", ["NÃO ERA", "TERMINATOR"], 220, 340, 78)
    card("luta-mid.png", ["TINHA PILOTO"], 220, 200, 72)
    card("luta-end.png", ["ENTÃO O QUE", "ESTAVA LUTANDO?"], 220, 300, 64)
    card("end-yt.png", ["PAPO INTEIRO NO YOUTUBE", "@naubervsyas"], 1500, 340, 46)
    card("cons-hook.png", ["ELA DISSE", "QUE NÃO"], 220, 300, 78)
    card("cons-mid.png", ["NÃO SENTE.", "NÃO TEM UM EU."], 220, 280, 64)
    card("cons-end.png", ["SE PARECE", "CONSCIENTE. É?"], 220, 300, 64)
    card("cor-hook.png", ["UMA FRASE", "PRA FECHAR"], 220, 280, 68)
    card("cor-end.png", ["CORAGEM NÃO É", "TER TODAS", "AS RESPOSTAS"], 220, 380, 64)

    render(
        101.1,
        30,
        OUT / "corte-luta-9x16.mp4",
        [
            ("luta-hook.png", "between(t,0,3.4)"),
            ("luta-mid.png", "between(t,4.2,14.5)"),
            ("luta-end.png", "between(t,20,27.6)"),
            ("end-yt.png", "between(t,27.6,30)"),
        ],
    )
    render(
        220.2,
        33,
        OUT / "corte-consciencia-9x16.mp4",
        [
            ("cons-hook.png", "between(t,0,3.6)"),
            ("cons-mid.png", "between(t,4.2,16)"),
            ("cons-end.png", "between(t,22,30.2)"),
            ("end-yt.png", "between(t,30.2,33)"),
        ],
    )
    render(
        1513.2,
        28,
        OUT / "corte-coragem-9x16.mp4",
        [
            ("cor-hook.png", "between(t,0,4)"),
            ("cor-end.png", "between(t,10,24.5)"),
            ("end-yt.png", "between(t,24.5,28)"),
        ],
    )
    for p in OUT.glob("corte-*-9x16.mp4"):
        print(p.name, p.stat().st_size // 1024, "KiB")


if __name__ == "__main__":
    main()
