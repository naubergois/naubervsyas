#!/usr/bin/env python3
"""Motion barato da thumb TINHA PILOTO → Short 9:16.

Ken Burns + punch + texto na tela. Áudio do corte-luta.
Sem vinheta. Sem Comfy. Um encode.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/naubergois/canalnauber/producao/ep2-voz")
THUMB = ROOT / "final" / "thumb.jpg"
AUDIO_SRC = ROOT / "final" / "corte-luta-9x16.mp4"
OUT = ROOT / "final" / "motion-thumb-piloto-9x16.mp4"
TMP = Path("/tmp/ep2-motion-thumb")
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

W, H = 1080, 1920
DUR = 30.0
FPS = 30
CREAM = (247, 241, 227, 255)
BAR = (10, 10, 12, 168)
YELLOW = (255, 225, 74, 255)

TMP.mkdir(parents=True, exist_ok=True)


def card(name: str, lines: list[str], y0: int, box_h: int, fs: int, fill=BAR) -> Path:
    dest = TMP / name
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(FONT, fs)
    d.rectangle((0, y0, W, y0 + box_h), fill=fill)
    sizes = []
    total = 0
    for line in lines:
        b = d.textbbox((0, 0), line, font=font)
        sizes.append((b[2] - b[0], b[3] - b[1]))
        total += b[3] - b[1] + 10
    y = y0 + (box_h - total) // 2
    for line, (tw, th) in zip(lines, sizes):
        d.text(((W - tw) // 2, y), line, font=font, fill=CREAM)
        y += th + 10
    im.save(dest)
    return dest


def prep_thumb_canvas() -> Path:
    """Thumb 16:9 no miolo 9:16. Cobre o TINHA PILOTO da capa (overlay fala)."""
    src = Image.open(THUMB).convert("RGB")
    # Corta o banner de texto do topo da thumb (~18% da altura)
    crop_top = int(src.height * 0.18)
    src = src.crop((0, crop_top, src.width, src.height))
    canvas = Image.new("RGB", (W, H), (10, 10, 12))
    yellow_h = 220
    ImageDraw.Draw(canvas).rectangle((0, 0, W, yellow_h), fill=(255, 225, 74))
    # escala pra largura 1080 mantendo proporção do crop
    tw = 1080
    th = int(src.height * (1080 / src.width))
    thumb = src.resize((tw, th), Image.Resampling.LANCZOS)
    y = yellow_h + max(0, ((H - yellow_h - 180) - th) // 2)
    canvas.paste(thumb, (0, y))
    dest = TMP / "canvas.jpg"
    canvas.save(dest, quality=95)
    return dest


def render(canvas: Path) -> None:
    frames = int(DUR * FPS)
    # Punch nos primeiros ~1s, depois zoom lento + drift horizontal leve
    z = (
        "if(lte(on,30),1+0.006*on,"
        "1.18+0.00035*(on-30))"
    )
    x = "iw/2-(iw/zoom/2)+40*sin(on/90)"
    y = "ih/2-(ih/zoom/2)"
    zoom = (
        f"[0:v]scale={W}:{H}:flags=lanczos,setsar=1,"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS},"
        f"format=yuv420p[v0]"
    )

    overlays = [
        ("hook.png", "between(t,0,3.4)"),
        ("mid.png", "between(t,4.2,14.5)"),
        ("end.png", "between(t,20,27.6)"),
        ("cta.png", "between(t,27.6,30)"),
    ]

    chain = zoom
    last = "v0"
    inputs = ["-loop", "1", "-t", str(DUR), "-i", str(canvas), "-i", str(AUDIO_SRC)]
    n = 2
    for i, (png, enable) in enumerate(overlays, start=1):
        inputs += ["-loop", "1", "-i", str(TMP / png)]
        nxt = f"v{i}"
        chain += f";[{last}][{n}:v]overlay=0:0:enable='{enable}'[{nxt}]"
        last = nxt
        n += 1

    cmd = [
        "ffmpeg", "-y", *inputs,
        "-filter_complex", chain,
        "-map", f"[{last}]", "-map", "1:a",
        "-t", str(DUR),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        "-r", str(FPS), "-movflags", "+faststart",
        str(OUT),
    ]
    print("==", OUT.name, flush=True)
    subprocess.run(cmd, check=True)


def main() -> None:
    card("hook.png", ["NÃO ERA", "TERMINATOR"], 240, 320, 78)
    card("mid.png", ["TINHA PILOTO"], 240, 180, 72, fill=(10, 10, 12, 200))
    card("end.png", ["ENTÃO O QUE", "ESTAVA LUTANDO?"], 240, 300, 62)
    card("cta.png", ["PAPO INTEIRO NO YOUTUBE", "@naubervsyas"], 1520, 300, 44)
    canvas = prep_thumb_canvas()
    render(canvas)
    print("OK", OUT)


if __name__ == "__main__":
    main()
