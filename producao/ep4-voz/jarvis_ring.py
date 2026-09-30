#!/usr/bin/env python3
"""Roda Jarvis do ep. 4 — HUD ciano + orbe, só na fala da Yas."""
from __future__ import annotations

import json
import math
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path("/Users/naubergois/canalnauber/producao/ep4-voz")
PREVIEW = ROOT / "preview"
FINAL = ROOT / "final"
SRT = ROOT / "audio" / "full.srt"
MASTER = FINAL / "ep4-youtube.mp4"
ORB_SRC = Path(
    "/Users/naubergois/canalnauber/producao/ep2-voz/preview/jarvis-bot-loop.mov"
)
TRIM = 0.0
VINHETA = 5.0
FPS = 25
SIZE = 600
HI = 1200
CYAN = (61, 255, 240)
MAGENTA = (255, 61, 138)
VIOLET = (130, 72, 255)
ICE = (200, 255, 255)
MASTER_DUR = 1491.72

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
    "ótimo ponto",
    "a jogada famosa",
    "ótima pergunta",
    "o paralelo faz",
    "estou bem na medida",
    "pronta para",
    "eu sou uma inteligência",
    "eu consigo ajudar",
    "um modelo não sabe",
    "eu estimo",
    "eu posso dizer que não sei",
    "deixa eu organizar",
    "olha, o ponto",
    "não é intenção",
    "não é imaginação",
    "uso responsável",
    "validação humana",
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
    "vamos ao episódio",
    "pra começar",
    "pesquisador brasileiro",
    "eu acho que depende",
    "vamos iniciar",
    "hoje a gente tem uma missão",
    "a missão é apresentar",
    "eu vou provocar",
    "vamos começar com",
    "vamos dar um exemplo",
    "nós sabemos que",
    "eu entendo e você falou",
    "concordo, mas",
    "miguel",
    "turma",
    "valeu",
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


def _has(text: str, key: str) -> bool:
    return re.search(rf"(^|[^a-zà-ú]){re.escape(key)}([^a-zà-ú]|$)", text) is not None


def who(text: str, start: float) -> str:
    # abertura travada: oi do Nauber, resposta curta da Yas, missão do Nauber
    if start < 11.0:
        return "nauber"
    if 11.0 <= start < 19.0:
        return "yas"
    if 19.0 <= start < 61.0:
        return "nauber"
    if 61.0 <= start < 63.0:
        return "yas"
    # monólogo do host no AlphaGo, antes da pergunta
    if 251.0 <= start < 314.0:
        return "nauber"
    t = text.lower()
    if any(_has(t, k) for k in YAS):
        return "yas"
    if any(_has(t, k) for k in NAUBER):
        return "nauber"
    if len(text) > 160:
        return "yas"
    q = t.lstrip("- ").startswith(
        ("como", "qual", "o que", "você", "tu ", "será", "e aí", "tá.")
    )
    if "?" in text and len(text) < 90 and q:
        return "nauber"
    informal = sum(
        1
        for w in ("tá", "né", "pra", "contigo", "vamo")
        if _has(t, w)
    )
    if informal and len(text) < 80:
        return "nauber"
    return "yas"


def yas_windows(cues: list[tuple[float, float, str]]) -> list[tuple[float, float]]:
    spans: list[tuple[float, float]] = []
    cur_a = cur_b = None
    for a, b, t in cues:
        if who(t, a) != "yas":
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
    shifted = []
    for a, b in spans:
        sa, sb = a - TRIM + VINHETA, b - TRIM + VINHETA
        if sb <= VINHETA + 0.2:
            continue
        shifted.append((max(VINHETA, sa), sb))
    return [(round(a, 3), round(b, 3)) for a, b in shifted if b - a >= 0.45]


def _arc(d: ImageDraw.ImageDraw, cx: float, cy: float, r: float, w: int, start: float, sweep: float, color, a: int) -> None:
    box = (cx - r, cy - r, cx + r, cy + r)
    d.arc(box, start, start + sweep, fill=color + (a,), width=w)


def draw_ring(angle: float, pulse: float, orb: Image.Image | None = None) -> Image.Image:
    s = HI
    cx = cy = s / 2
    k = s / 512
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))

    halo = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    r_h = 208 * k * pulse
    hd.ellipse((cx - r_h, cy - r_h, cx + r_h, cy + r_h), outline=CYAN + (70,), width=int(32 * k))
    hd.ellipse(
        (cx - r_h * 0.84, cy - r_h * 0.84, cx + r_h * 0.84, cy + r_h * 0.84),
        outline=VIOLET + (36,),
        width=int(16 * k),
    )
    halo = halo.filter(ImageFilter.GaussianBlur(20 * k))
    im = Image.alpha_composite(im, halo)

    sweep = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sweep)
    rs = 200 * k
    sd.pieslice((cx - rs, cy - rs, cx + rs, cy + rs), angle, angle + 42, fill=CYAN + (26,))
    sd.pieslice(
        (cx - rs, cy - rs, cx + rs, cy + rs),
        angle + 200,
        angle + 228,
        fill=MAGENTA + (16,),
    )
    sweep = sweep.filter(ImageFilter.GaussianBlur(10 * k))
    im = Image.alpha_composite(im, sweep)

    d = ImageDraw.Draw(im)
    r_out = 194 * k
    for i in range(12):
        start = angle + i * 30 + 4
        _arc(d, cx, cy, r_out, max(3, int(5 * k)), start, 18, CYAN, 235)
    for i in range(4):
        start = -angle * 1.35 + i * 90
        _arc(d, cx, cy, 162 * k, max(2, int(4 * k)), start, 58, ICE, 190)
    _arc(d, cx, cy, 138 * k, max(2, int(3 * k)), angle * 1.8, 250, CYAN, 170)
    _arc(d, cx, cy, 122 * k, max(1, int(2 * k)), -angle * 2.2, 200, MAGENTA, 150)

    for i in range(48):
        ang = math.radians(angle * 0.55 + i * 7.5)
        long_tick = i % 6 == 0
        inner = (176 if long_tick else 180) * k
        outer = (198 if long_tick else 190) * k
        x1 = cx + inner * math.cos(ang)
        y1 = cy + inner * math.sin(ang)
        x2 = cx + outer * math.cos(ang)
        y2 = cy + outer * math.sin(ang)
        if long_tick:
            col = MAGENTA + (240,)
            w = max(2, int(3 * k))
        else:
            col = CYAN + (200,)
            w = max(1, int(2 * k))
        d.line((x1, y1, x2, y2), fill=col, width=w)

    if orb is not None:
        core = int(292 * k)
        orb_r = orb.resize((core, core), Image.Resampling.LANCZOS)
        ox = int(cx - core / 2)
        oy = int(cy - core / 2)
        im.alpha_composite(orb_r, (ox, oy))

    d = ImageDraw.Draw(im)
    cr = 58 * k * (0.90 + 0.10 * pulse)
    d.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), outline=CYAN + (210,), width=max(2, int(3 * k)))
    d.ellipse(
        (cx - cr * 0.42, cy - cr * 0.42, cx + cr * 0.42, cy + cr * 0.42),
        outline=ICE + (int(90 + 70 * pulse),),
        width=max(1, int(2 * k)),
    )
    gap = 26 * k
    arm = 78 * k
    hair = CYAN + (130,)
    d.line((cx - arm, cy, cx - gap, cy), fill=hair, width=max(1, int(2 * k)))
    d.line((cx + gap, cy, cx + arm, cy), fill=hair, width=max(1, int(2 * k)))
    d.line((cx, cy - arm, cx, cy - gap), fill=hair, width=max(1, int(2 * k)))
    d.line((cx, cy + gap, cx, cy + arm), fill=hair, width=max(1, int(2 * k)))

    im = im.filter(ImageFilter.GaussianBlur(0.55))
    return im.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def extract_orb_frames(dest: Path, n: int) -> list[Path]:
    dest.mkdir(parents=True, exist_ok=True)
    first = dest / "0000.png"
    if first.exists() and len(list(dest.glob("*.png"))) >= n:
        return [dest / f"{i:04d}.png" for i in range(n)]
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(ORB_SRC),
            "-frames:v",
            str(n),
            str(dest / "%04d.png"),
        ]
    )
    # ffmpeg 1-index
    paths = sorted(dest.glob("*.png"))
    if len(paths) < n:
        raise RuntimeError(f"orbe: {len(paths)} frames, queria {n}")
    return paths[:n]


def write_loop(dest: Path, seconds: float = 4.0) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    n = int(seconds * FPS)
    frames = dest.parent / "_jarvis_frames"
    frames.mkdir(exist_ok=True)
    orb_paths = extract_orb_frames(dest.parent / "_orb_frames", n)
    still = dest.parent / "jarvis-anel.png"
    for i in range(n):
        t = i / FPS
        pulse = 0.96 + 0.04 * math.sin(t * math.tau * 1.55)
        ang = t * 78
        orb = Image.open(orb_paths[i]).convert("RGBA")
        frame = draw_ring(ang, pulse, orb)
        frame.save(frames / f"{i:04d}.png")
        if i == 18:
            frame.save(still)
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
    print("LOOP", dest, dest.stat().st_size // 1024, "KiB")


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
        raw.extend(bytes([g]) * 16)
    dest.write_bytes(raw)
    dest.with_suffix(".n").write_text(str(n), encoding="utf-8")


def overlay(src: Path, loop: Path, gate: Path, dest: Path, t_limit: float | None) -> None:
    ss = ["-t", str(t_limit)] if t_limit else []
    fc = (
        f"[1:v]format=rgba,scale={SIZE}:{SIZE},split[jrgb][ja];"
        "[ja]alphaextract[aa];"
        f"[2:v]scale={SIZE}:{SIZE},format=gray[g];"
        "[aa][g]blend=all_mode=multiply:shortest=1[am];"
        "[jrgb][am]alphamerge[jm];"
        f"[0:v][jm]overlay=(W-w)/2-100:(H-h)/2-56[vout]"
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
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    PREVIEW.mkdir(exist_ok=True)
    cues = parse_srt(SRT)
    wins = yas_windows(cues)
    (PREVIEW / "yas-windows.json").write_text(json.dumps(wins, indent=2), encoding="utf-8")
    print(f"{len(wins)} janelas do Yas, {sum(b - a for a, b in wins):.0f}s no ar")
    loop = PREVIEW / "jarvis-bot-loop.mov"
    if mode == "loop" or not loop.exists():
        write_loop(loop)
    gate = PREVIEW / "yas-gate.gray"
    write_gate(wins, MASTER_DUR, gate)
    if mode == "loop":
        print("STILL", PREVIEW / "jarvis-anel.png")
        return
    if mode == "preview":
        out = PREVIEW / "amostra-jarvis-90s.mp4"
        overlay(MASTER, loop, gate, out, t_limit=90)
        print("PREVIEW", out)
        return
    out = FINAL / "ep4-youtube.mp4"
    tmp = FINAL / "ep4-jarvis-tmp.mp4"
    overlay(MASTER, loop, gate, tmp, t_limit=None)
    tmp.replace(out)
    print("FINAL", out)


if __name__ == "__main__":
    main()
