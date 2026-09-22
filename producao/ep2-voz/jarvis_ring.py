#!/usr/bin/env python3
"""Roda estilo Jarvis — acende só quando o Yas (IA) fala."""
from __future__ import annotations

import math
import re
import struct
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path("/Users/naubergois/canalnauber/producao/ep2-voz")
PREVIEW = ROOT / "preview"
FINAL = ROOT / "final"
SRT = ROOT / "audio" / "full.srt"
MASTER = FINAL / "ep2-youtube.mp4"
TRIM = 0.80
VINHETA = 5.0
FPS = 25
SIZE = 512
CYAN = (61, 255, 240)
MAGENTA = (255, 61, 138)

YAS = (
    "claro",
    "justo",
    "exatamente",
    "hmm",
    "hum",
    "pois é",
    "olha",
    "entendi",
    "minutinho",
    "no meu caso",
    "funcionalista",
    "experiência subjetiva",
    "arquitetura",
    "ou seja",
    "sendo bem",
    "eu diria",
    "uma leitura",
    "vou pegar",
    "antes de responder",
    "eu consigo",
    "eu agruparia",
    "eu sugiro",
    "não há evidência",
    "ferramenta que processa",
    "vamos para partes",
    "eu partirei",
    "eu não tenho experiência",
    "eu não consigo entrar",
    "fui genérica",
    "agora é de forma concreta",
    "fio condutor",
    "coragem não é",
    "nos vemos no próximo",
)
NAUBER = (
    "eu particularmente",
    "eu vi no instagram",
    "eu vou lançar",
    "eu estou conversando",
    "eu acho que",
    "eu levei",
    "eu gosto muito",
    "você está me enrolando",
    "muito obrigado",
    "tá bom",
    "desafio polêmico",
    "não dá espolha",
    "você tem criadores",
    "como é que você",
    "como é que tu",
    "qual a lição",
    "vamos falar sobre",
    "eu queria que",
    "eu queria perguntar",
)


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd[:7]), "...")
    subprocess.check_call(cmd)


def parse_srt(path: Path) -> list[tuple[float, float, str]]:
    raw = path.read_text(encoding="utf-8")
    blocks = re.split(r"\n\s*\n", raw.strip())
    out = []
    for b in blocks:
        lines = [ln for ln in b.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        m = re.search(
            r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)",
            lines[1],
        )
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        b_ = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        text = " ".join(lines[2:]).strip()
        if text.lower() in {"[silêncio]", "[musica]", ""}:
            continue
        out.append((a, b_, text))
    return out


def who(text: str, start: float) -> str:
    # abertura travada: oi do Nauber, “tudo bem” do Yas, eleição do Nauber
    if start < 3.4:
        return "nauber"
    if 3.4 <= start < 5.8:
        return "yas"
    if 5.8 <= start < 23.0:
        return "nauber"
    t = text.lower()
    if any(k in t for k in YAS):
        return "yas"
    if any(k in t for k in NAUBER):
        return "nauber"
    if len(text) > 160:
        return "yas"
    q = t.lstrip("- ").startswith(
        ("como", "qual", "o que", "você", "tu ", "será", "e aí", "tá.")
    )
    if "?" in text and len(text) < 90 and q:
        return "nauber"
    informal = sum(1 for w in ("tá", "né", "pra", "contigo", "vamo") if w in t)
    if informal and len(text) < 80:
        return "nauber"
    return "yas"


def yas_windows(cues: list[tuple[float, float, str]]) -> list[tuple[float, float]]:
    labeled = [(a, b, who(t, a), t) for a, b, t in cues]
    spans: list[tuple[float, float]] = []
    cur_a = cur_b = None
    for a, b, sp, _ in labeled:
        if sp != "yas":
            if cur_a is not None:
                spans.append((cur_a, cur_b))
                cur_a = cur_b = None
            continue
        if cur_a is None:
            cur_a, cur_b = a, b
        elif a - cur_b < 1.8:
            cur_b = b
        else:
            spans.append((cur_a, cur_b))
            cur_a, cur_b = a, b
    if cur_a is not None:
        spans.append((cur_a, cur_b))
    # source → master (vinheta 5s, corte 0.8s do preto)
    shifted = []
    for a, b in spans:
        sa, sb = a - TRIM + VINHETA, b - TRIM + VINHETA
        if sb <= VINHETA + 0.2:
            continue
        shifted.append((max(VINHETA, sa), sb))
    return [(round(a, 3), round(b, 3)) for a, b in shifted if b - a >= 0.45]


def draw_ring(angle: float, pulse: float) -> Image.Image:
    im = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = cy = SIZE / 2
    glow = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    r0 = 198 * pulse
    # halo
    gd.ellipse((cx - r0, cy - r0, cx + r0, cy + r0), outline=CYAN + (40,), width=18)
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    im = Image.alpha_composite(im, glow)
    d = ImageDraw.Draw(im)
    veil = 160 * pulse
    d.ellipse(
        (cx - veil, cy - veil, cx + veil, cy + veil),
        fill=(4, 14, 18, 38),
    )

    def arc(r, w, start, sweep, color, a=220):
        box = (cx - r, cy - r, cx + r, cy + r)
        d.arc(box, start, start + sweep, fill=color + (a,), width=w)

    # outer broken ring
    for i in range(8):
        start = angle + i * 45 + 6
        arc(186, 4, start, 32, CYAN, 230)
    # mid ring
    for i in range(3):
        start = -angle * 1.4 + i * 120
        arc(154, 3, start, 78, CYAN, 200)
    # inner ring
    arc(118, 2, angle * 2, 260, CYAN, 180)
    # ticks
    for i in range(24):
        ang = math.radians(angle * 0.7 + i * 15)
        inner, outer = (168, 178) if i % 3 else (164, 184)
        x1 = cx + inner * math.cos(ang)
        y1 = cy + inner * math.sin(ang)
        x2 = cx + outer * math.cos(ang)
        y2 = cy + outer * math.sin(ang)
        col = MAGENTA + (230,) if i % 6 == 0 else CYAN + (210,)
        d.line((x1, y1, x2, y2), fill=col, width=2)
    # core
    cr = 52 * (0.88 + 0.12 * pulse)
    d.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), outline=CYAN + (200,), width=3)
    d.ellipse(
        (cx - cr * 0.55, cy - cr * 0.55, cx + cr * 0.55, cy + cr * 0.55),
        fill=CYAN + (int(50 + 40 * pulse),),
    )
    # crosshair
    gap = 22
    d.line((cx - 70, cy, cx - gap, cy), fill=CYAN + (140,), width=1)
    d.line((cx + gap, cy, cx + 70, cy), fill=CYAN + (140,), width=1)
    d.line((cx, cy - 70, cx, cy - gap), fill=CYAN + (140,), width=1)
    d.line((cx, cy + gap, cx, cy + 70), fill=CYAN + (140,), width=1)
    return im.filter(ImageFilter.GaussianBlur(0.4))


def write_loop(dest: Path, seconds: float = 4.0) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    n = int(seconds * FPS)
    frames = dest.parent / "_jarvis_frames"
    frames.mkdir(exist_ok=True)
    for i in range(n):
        t = i / FPS
        pulse = 0.94 + 0.06 * math.sin(t * math.tau * 1.7)
        ang = t * 70
        draw_ring(ang, pulse).save(frames / f"{i:04d}.png")
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-framerate",
            str(FPS),
            "-i",
            str(frames / "%04d.png"),
            "-c:v",
            "png",
            "-pix_fmt",
            "rgba",
            str(dest),
        ]
    )


def write_gate(windows: list[tuple[float, float]], duration: float, dest: Path) -> None:
    n = int(math.ceil(duration * FPS))
    fade = int(0.18 * FPS)
    val = [0.0] * n
    for a, b in windows:
        ia, ib = int(a * FPS), min(n, int(b * FPS))
        for i in range(max(0, ia), ib):
            k = 1.0
            if i - ia < fade:
                k = (i - ia) / fade
            if ib - i < fade:
                k = min(k, (ib - i) / fade)
            val[i] = max(val[i], k)
    raw = bytearray()
    for v in val:
        g = int(max(0, min(255, v * 255)))
        raw.extend(bytes([g]) * 16)  # 4x4 gray
    dest.write_bytes(raw)
    # header sidecar
    dest.with_suffix(".n").write_text(str(n), encoding="utf-8")


def overlay(src: Path, loop: Path, gate: Path, dest: Path, t_limit: float | None) -> None:
    n = int(gate.with_suffix(".n").read_text())
    ss = []
    if t_limit:
        ss = ["-t", str(t_limit)]
    # porta 4x4 → tamanho da roda; multiplica o alpha do loop
    fc = (
        f"[1:v]format=rgba,scale={SIZE}:{SIZE},split[jrgb][ja];"
        "[ja]alphaextract[aa];"
        f"[2:v]scale={SIZE}:{SIZE},format=gray[g];"
        "[aa][g]blend=all_mode=multiply:shortest=1[am];"
        "[jrgb][am]alphamerge[jm];"
        f"[0:v][jm]overlay=(W-w)/2-120:(H-h)/2-70[vout]"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-stats",
            *ss,
            "-i",
            str(src),
            "-stream_loop",
            "-1",
            "-i",
            str(loop),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "gray",
            "-s",
            "4x4",
            "-r",
            str(FPS),
            "-i",
            str(gate),
            "-filter_complex",
            fc,
            "-map",
            "[vout]",
            "-map",
            "0:a",
            "-c:v",
            "h264_videotoolbox",
            "-b:v",
            "10M",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "copy",
            "-shortest",
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )


def main() -> None:
    import json
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    PREVIEW.mkdir(exist_ok=True)
    cues = parse_srt(SRT)
    wins = yas_windows(cues)
    (PREVIEW / "yas-windows.json").write_text(json.dumps(wins, indent=2), encoding="utf-8")
    print(f"{len(wins)} janelas do Yas, {sum(b-a for a,b in wins):.0f}s no ar")
    bot = PREVIEW / "jarvis-bot-loop.mov"
    loop = bot if bot.exists() else PREVIEW / "jarvis-loop.mov"
    if not loop.exists():
        write_loop(loop)
    dur = 1548.2
    gate = PREVIEW / "yas-gate.gray"
    write_gate(wins, dur, gate)
    if mode == "preview":
        out = PREVIEW / "amostra-jarvis-90s.mp4"
        overlay(MASTER, loop, gate, out, t_limit=90)
        print("PREVIEW", out)
        return
    out = FINAL / "ep2-youtube.mp4"
    tmp = FINAL / "ep2-jarvis-tmp.mp4"
    overlay(MASTER, loop, gate, tmp, t_limit=None)
    tmp.replace(out)
    print("FINAL", out)


if __name__ == "__main__":
    main()
