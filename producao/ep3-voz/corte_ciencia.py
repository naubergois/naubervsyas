#!/usr/bin/env python3
"""Corte do ep. 3: pesquisa acadêmica (paper vs descoberta).

Sem vinheta. Um encode por vez. Capas criativas (não o modelo dois lados).
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

YT = Path("/Users/naubergois/canalnauber/producao/ep3-voz/final/ep3-youtube.mp4")
OUT = Path("/Users/naubergois/canalnauber/producao/ep3-voz/final")
WORK = Path("/Volumes/NAUBER/HomeOffload/canalnauber-ep3-corte-ciencia")
TMP = WORK / "tmp"
THUMBS_IN = WORK / "thumbs"
FONT = Path("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf")
FONT_BOLD = Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")

# Janela no master (SRT 16:16 + vinheta 5s): "exemplo clássico" → fecho da Yas
START = 980.76
DUR = 150.0

CREAM = (247, 241, 227, 255)
BAR = (10, 10, 12, 168)
BLACK = (10, 10, 12, 255)

TMP.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)


def _font(size: int, rounded: bool = True) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONT if rounded else FONT_BOLD), size)


def card(name: str, size: tuple[int, int], lines: list[str], y0: int, box_h: int, fs: int) -> Path:
    w, h = size
    dest = TMP / name
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = _font(fs)
    d.rectangle((0, y0, w, y0 + box_h), fill=BAR)
    sizes = []
    total = 0
    for line in lines:
        b = d.textbbox((0, 0), line, font=font)
        sizes.append((b[2] - b[0], b[3] - b[1]))
        total += b[3] - b[1] + 10
    y = y0 + (box_h - total) // 2
    for line, (tw, th) in zip(lines, sizes):
        d.text(((w - tw) // 2, y), line, font=font, fill=CREAM)
        y += th + 10
    im.save(dest)
    return dest


def finish_thumbs() -> None:
    """Três capas distintas. Texto curto, barra sólida, sem repetir o título."""
    specs = [
        (
            "capa-a-versus.jpg",
            "thumb-a-artigo.jpg",
            "ARTIGO OU REMÉDIO",
            [(40, 430, 280, 490)],  # tapa THESISIS
        ),
        (
            "capa-b-perfume.jpg",
            "thumb-b-perfume.jpg",
            "NÃO É PERFUME",
            [],
        ),
        (
            "capa-c-artigo.jpg",
            "thumb-c-rastro.jpg",
            "SEM RASTRO",
            [(0, 0, 1280, 150), (780, 620, 1260, 720)],  # tapa inglês
        ),
    ]
    font = _font(72)
    for src_name, dest_name, text, patches in specs:
        src = Image.open(THUMBS_IN / src_name).convert("RGB")
        src = src.resize((1280, 720), Image.Resampling.LANCZOS)
        d = ImageDraw.Draw(src)
        for box in patches:
            d.rectangle(box, fill=(10, 10, 12))
        d.rectangle((0, 0, 1280, 136), fill=(10, 10, 12))
        b = d.textbbox((0, 0), text, font=font)
        tw, th = b[2] - b[0], b[3] - b[1]
        d.text(((1280 - tw) // 2, (136 - th) // 2 - 4), text, font=font, fill=(247, 241, 227))
        dest = OUT / dest_name
        src.save(dest, "JPEG", quality=88, optimize=True)
        src.save(WORK / "final" / dest_name, "JPEG", quality=88, optimize=True)
        print(dest, dest.stat().st_size // 1024, "KiB")


def render(dest: Path, size: tuple[int, int], vf_scale: str, overlays: list[tuple[str, str]]) -> None:
    inputs: list[str] = ["-ss", str(START), "-t", str(DUR), "-i", str(YT)]
    chain = f"[0:v]{vf_scale}[v0]"
    last = "v0"
    n = 1
    for i, (png, enable) in enumerate(overlays, start=1):
        inputs += ["-loop", "1", "-i", str(TMP / png)]
        nxt = f"v{i}"
        chain += f";[{last}][{n}:v]overlay=0:0:enable='{enable}'[{nxt}]"
        last = nxt
        n += 1
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        *inputs,
        "-filter_complex",
        chain,
        "-map",
        f"[{last}]",
        "-map",
        "0:a",
        "-t",
        str(DUR),
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "19",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "160k",
        "-ar",
        "48000",
        "-r",
        "30",
        "-movflags",
        "+faststart",
        str(dest),
    ]
    print("==", dest.name, flush=True)
    subprocess.run(cmd, check=True)
    print(dest.name, dest.stat().st_size // 1024, "KiB")


def main() -> None:
    (WORK / "final").mkdir(parents=True, exist_ok=True)
    finish_thumbs()

    # 16:9 — vídeo novo (capas valem)
    w, h = 1920, 1080
    card("w-hook.png", (w, h), ["IA ESCREVE O PAPER"], 36, 150, 64)
    card("w-mid.png", (w, h), ["ARTIGO É FORMA"], 36, 150, 64)
    card("w-ask.png", (w, h), ["POR QUE A FORMA?"], 36, 150, 64)
    card("w-yas.png", (w, h), ["NÃO É PERFUME"], 36, 150, 64)
    card("w-end.png", (w, h), ["E SE NÃO REPETE?"], 36, 150, 64)
    card("w-yt.png", (w, h), ["PAPO INTEIRO  @naubervsyas"], 900, 140, 42)

    wide = OUT / "corte-ciencia-16x9.mp4"
    render(
        wide,
        (w, h),
        "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1",
        [
            ("w-hook.png", "between(t,0,4.2)"),
            ("w-mid.png", "between(t,38,55)"),
            ("w-ask.png", "between(t,61,72)"),
            ("w-yas.png", "between(t,86,108)"),
            ("w-end.png", "between(t,131,145)"),
            ("w-yt.png", "between(t,145,150)"),
        ],
    )

    # 9:16 — mesmo corte, formato Short
    w, h = 1080, 1920
    card("v-hook.png", (w, h), ["IA ESCREVE", "O PAPER"], 220, 300, 72)
    card("v-mid.png", (w, h), ["ARTIGO É FORMA"], 220, 200, 64)
    card("v-ask.png", (w, h), ["POR QUE", "A FORMA?"], 220, 280, 68)
    card("v-yas.png", (w, h), ["NÃO É PERFUME"], 220, 200, 64)
    card("v-end.png", (w, h), ["E SE NÃO", "REPETE?"], 220, 280, 68)
    card("v-yt.png", (w, h), ["PAPO INTEIRO NO YOUTUBE", "@naubervsyas"], 1500, 340, 42)

    tall = OUT / "corte-ciencia-9x16.mp4"
    render(
        tall,
        (w, h),
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
        [
            ("v-hook.png", "between(t,0,4.2)"),
            ("v-mid.png", "between(t,38,55)"),
            ("v-ask.png", "between(t,61,72)"),
            ("v-yas.png", "between(t,86,108)"),
            ("v-end.png", "between(t,131,145)"),
            ("v-yt.png", "between(t,145,150)"),
        ],
    )


if __name__ == "__main__":
    main()
