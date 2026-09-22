#!/usr/bin/env python3
"""Orbe Astra 3D — variações de cor e emoção, fundo transparente.

Uso:
  python3 jarvis_bot.py              # todas as emoções
  python3 jarvis_bot.py calma        # uma só
  python3 jarvis_bot.py --loop calma # loop com alpha (pesado)
"""
from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/Users/naubergois/canalnauber/producao/ep2-voz")
OUT = ROOT / "preview"
SIZE = 1080
FPS = 25
SECONDS = 4.0
CREAM = (247, 241, 227)
DARK = np.array([5, 6, 12], dtype=np.float32)


@dataclass(frozen=True)
class Mood:
    slug: str
    label: str
    core: tuple[int, int, int]
    accent: tuple[int, int, int]
    fill: tuple[int, int, int]
    warm: tuple[int, int, int]
    deep: tuple[int, int, int]
    pulse: float
    swirl: float
    tempo: float
    glow: float


MOODS: tuple[Mood, ...] = (
    Mood(
        "calma", "calma",
        (61, 255, 240), (130, 72, 255), (90, 160, 255),
        (200, 230, 255), (28, 70, 210),
        pulse=0.055, swirl=1.15, tempo=0.82, glow=0.18,
    ),
    Mood(
        "alegria", "alegria",
        (255, 225, 74), (255, 160, 40), (255, 210, 120),
        (255, 240, 180), (210, 90, 20),
        pulse=0.12, swirl=2.15, tempo=1.18, glow=0.28,
    ),
    Mood(
        "carinho", "carinho",
        (255, 110, 170), (255, 61, 138), (255, 170, 200),
        (255, 210, 180), (160, 30, 90),
        pulse=0.075, swirl=1.35, tempo=0.88, glow=0.26,
    ),
    Mood(
        "curiosidade", "curiosidade",
        (180, 110, 255), (90, 70, 255), (210, 160, 255),
        (255, 200, 255), (70, 30, 160),
        pulse=0.09, swirl=2.40, tempo=1.08, glow=0.22,
    ),
    Mood(
        "tensao", "tensão",
        (255, 90, 50), (255, 40, 70), (255, 140, 60),
        (255, 200, 80), (140, 20, 30),
        pulse=0.14, swirl=2.80, tempo=1.35, glow=0.16,
    ),
    Mood(
        "foco", "foco",
        (40, 120, 255), (20, 220, 255), (70, 90, 210),
        (180, 220, 255), (10, 30, 90),
        pulse=0.04, swirl=0.85, tempo=0.70, glow=0.12,
    ),
    Mood(
        "empatia", "empatia",
        (80, 230, 200), (247, 241, 227), (120, 200, 190),
        (255, 220, 190), (20, 90, 90),
        pulse=0.065, swirl=1.05, tempo=0.78, glow=0.30,
    ),
    Mood(
        "energia", "energia",
        (61, 255, 240), (255, 61, 138), (130, 72, 255),
        (255, 225, 74), (40, 20, 120),
        pulse=0.13, swirl=2.55, tempo=1.25, glow=0.24,
    ),
)


def ease_out(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def ease_in(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x**3


def talk(t: float, tempo: float) -> float:
    t = (t * tempo) % SECONDS
    peaks = (0.18, 0.52, 0.88, 1.28, 1.70, 2.12, 2.58, 3.05, 3.48)
    widths = (0.28, 0.24, 0.30, 0.26, 0.32, 0.24, 0.28, 0.26, 0.30)
    amps = (0.86, 0.58, 0.95, 0.64, 0.90, 0.50, 0.92, 0.60, 0.74)
    v = 0.0
    for p, w, a in zip(peaks, widths, amps):
        u = (t - (p - w * 0.22)) / w
        if u < 0 or u > 1:
            continue
        if u < 0.14:
            v = max(v, -0.08 * ease_out(u / 0.14) * a)
        elif u < 0.42:
            v = max(v, a * ease_out((u - 0.14) / 0.28))
        elif u < 0.62:
            v = max(v, a)
        else:
            v = max(v, a * (1 - ease_in((u - 0.62) / 0.38)))
    return max(0.0, v)


def _norm(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n else v


def _rgb(c: tuple[int, int, int]) -> np.ndarray:
    return np.array(c, dtype=np.float32)


def draw_frame(t: float, mood: Mood) -> Image.Image:
    voice = talk(t, mood.tempo)
    radius = SIZE * 0.36 * (1.0 + mood.pulse * voice)
    cx = cy = SIZE / 2.0
    yy, xx = np.ogrid[:SIZE, :SIZE]
    x = (xx - cx) / radius
    y = (yy - cy) / radius
    r2 = x * x + y * y
    inside = r2 <= 1.05
    z = np.sqrt(np.maximum(1.0 - np.minimum(r2, 1.0), 0.0))
    nx, ny, nz = x, y, z

    L1 = _norm(np.array([-0.45, -0.55, 0.85]))
    L2 = _norm(np.array([0.65, 0.15, 0.55]))
    L3 = _norm(np.array([0.05, 0.75, 0.45]))
    V = np.array([0.0, 0.0, 1.0])

    d1 = np.clip(nx * L1[0] + ny * L1[1] + nz * L1[2], 0, 1)
    d2 = np.clip(nx * L2[0] + ny * L2[1] + nz * L2[2], 0, 1)
    d3 = np.clip(nx * L3[0] + ny * L3[1] + nz * L3[2], 0, 1)

    def spec(L, power):
        H = _norm(L + V)
        return np.clip(nx * H[0] + ny * H[1] + nz * H[2], 0, 1) ** power

    s1 = spec(L1, 48)
    s2 = spec(L2, 32)
    fresnel = (1.0 - nz) ** 2.4

    lon = np.arctan2(ny, nx)
    lat = np.arcsin(np.clip(nz, 0, 1))
    pole = np.clip(r2 * 8.0, 0.0, 1.0)
    swirl = lon * 3.2 * pole + lat * 5.0 + t * mood.swirl + voice * 0.8
    bands = 0.5 + 0.5 * np.sin(swirl)
    bands2 = 0.5 + 0.5 * np.sin(lon * 5 * pole - lat * 4 + t * mood.swirl * 1.35)

    c_cy = _rgb(mood.core)
    c_vi = _rgb(mood.accent)
    c_mg = _rgb(mood.fill)
    c_au = _rgb(mood.warm)
    c_bl = _rgb(mood.deep)

    albedo = (
        c_bl * (0.22 + 0.18 * nz[..., None])
        + c_cy * (0.28 * d1 + 0.22 * bands)[..., None]
        + c_vi * (0.32 * d2 + 0.18 * (1 - bands))[..., None]
        + c_mg * (0.22 * d3 + 0.20 * bands2 * voice)[..., None]
        + c_au * (0.10 * d3 * (1 - voice) + 0.16 * s1)[..., None]
    )
    albedo *= 0.55 + 0.45 * (0.35 + 0.65 * d1 + 0.25 * d2)[..., None]
    albedo *= 0.78 + 0.32 * voice

    irid = c_cy * (1 - bands2)[..., None] + c_mg * bands2[..., None]
    albedo += fresnel[..., None] * irid * (0.55 + 0.35 * voice)
    albedo += (s1 * 210 + s2 * 90)[..., None] * np.array([0.85, 1.0, 1.0])
    rim = np.exp(-((np.sqrt(np.maximum(r2, 1e-6)) - 1.0) ** 2) / 0.0016)
    albedo += rim[..., None] * (c_cy * 0.65 + c_mg * 0.35) * (0.75 + 0.4 * voice)

    halo = np.exp(-np.maximum(np.sqrt(r2) - 1.0, 0) ** 2 / 0.085)
    halo = halo * (mood.glow + 0.20 * voice)

    alpha = np.zeros((SIZE, SIZE), dtype=np.float32)
    edge = np.clip((1.02 - np.sqrt(r2)) / 0.06, 0, 1)
    alpha[inside] = (0.18 + 0.82 * nz[inside] ** 0.35) * edge[inside] * 255
    alpha = np.clip(alpha + halo * 110 + rim * 160, 0, 255)

    rgb = np.clip(albedo, 0, 255)
    out = np.zeros((SIZE, SIZE, 4), dtype=np.uint8)
    out[..., 0] = rgb[..., 0]
    out[..., 1] = rgb[..., 1]
    out[..., 2] = rgb[..., 2]
    out[..., 3] = alpha.astype(np.uint8)
    out[..., 0] = np.clip(out[..., 0] + halo * mood.core[0] * 0.35, 0, 255)
    out[..., 1] = np.clip(out[..., 1] + halo * mood.core[1] * 0.35, 0, 255)
    out[..., 2] = np.clip(out[..., 2] + halo * mood.core[2] * 0.35, 0, 255)
    return Image.fromarray(out, "RGBA")


def flatten_dark(frame: Image.Image) -> np.ndarray:
    arr = np.asarray(frame)
    a = arr[..., 3:4].astype(np.float32) / 255.0
    rgb = arr[..., :3].astype(np.float32) * a + DARK * (1.0 - a)
    return np.clip(rgb, 0, 255).astype(np.uint8)


def write_preview(mood: Mood, dest: Path, still: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    n = int(SECONDS * FPS)
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{SIZE}x{SIZE}",
        "-r", str(FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    mid = int(n * 0.42)
    for i in range(n):
        frame = draw_frame(i / FPS, mood)
        if i == mid:
            frame.save(still)
        proc.stdin.write(flatten_dark(frame).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg preview failed: {mood.slug}")
    print("PREVIEW", dest.name, dest.stat().st_size // 1024, "KiB")


def write_loop(mood: Mood, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    n = int(SECONDS * FPS)
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{SIZE}x{SIZE}",
        "-r", str(FPS), "-i", "-",
        "-c:v", "png", str(dest),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    assert proc.stdin is not None
    for i in range(n):
        proc.stdin.write(draw_frame(i / FPS, mood).tobytes())
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError("ffmpeg loop failed")
    print("LOOP", dest, dest.stat().st_size // 1024, "KiB")


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in (
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def write_sheet(stills: list[tuple[Mood, Path]], dest: Path) -> None:
    cols, rows = 4, 2
    cell = 420
    pad = 28
    w = cols * cell + pad * (cols + 1)
    h = rows * (cell + 48) + pad * (rows + 1)
    sheet = Image.new("RGB", (w, h), (5, 6, 12))
    draw = ImageDraw.Draw(sheet)
    font = _font(28)
    for i, (mood, path) in enumerate(stills):
        col, row = i % cols, i // cols
        x = pad + col * (cell + pad)
        y = pad + row * (cell + 48 + pad)
        orb = Image.open(path).convert("RGBA").resize((cell, cell), Image.Resampling.LANCZOS)
        bg = Image.new("RGBA", (cell, cell), (5, 6, 12, 255))
        sheet.paste(Image.alpha_composite(bg, orb).convert("RGB"), (x, y))
        tw = draw.textlength(mood.label, font=font)
        draw.text((x + (cell - tw) / 2, y + cell + 8), mood.label, fill=CREAM, font=font)
    sheet.save(dest, quality=92)
    print("SHEET", dest)


def concat_previews(paths: list[Path], dest: Path) -> None:
    lst = dest.with_suffix(".txt")
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in paths))
    subprocess.check_call(
        [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(lst),
            "-c", "copy", str(dest),
        ]
    )
    lst.unlink(missing_ok=True)
    print("REEL", dest, dest.stat().st_size // 1024, "KiB")


def mood_by_slug(slug: str) -> Mood:
    for m in MOODS:
        if m.slug == slug:
            return m
    raise SystemExit(f"emoção desconhecida: {slug}")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    args = [a for a in sys.argv[1:] if a != "--loop"]
    want_loop = "--loop" in sys.argv[1:]
    selected = [mood_by_slug(args[0])] if args else list(MOODS)

    stills: list[tuple[Mood, Path]] = []
    previews: list[Path] = []
    for mood in selected:
        still = OUT / f"orbe-{mood.slug}.png"
        preview = OUT / f"orbe-{mood.slug}.mp4"
        write_preview(mood, preview, still)
        stills.append((mood, still))
        previews.append(preview)
        if want_loop:
            write_loop(mood, OUT / f"orbe-{mood.slug}-loop.mov")

    if len(selected) > 1:
        write_sheet(stills, OUT / "orbe-emocoes.jpg")
        concat_previews(previews, OUT / "orbe-emocoes.mp4")
        # atalho do preview que o Cursor já tem aberto
        calma = OUT / "orbe-calma.mp4"
        if calma.exists():
            (OUT / "jarvis-bot-fala.mp4").write_bytes(calma.read_bytes())


if __name__ == "__main__":
    main()
