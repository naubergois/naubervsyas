#!/usr/bin/env python3
"""Monta o episódio 3: voz do bruto + B-roll mudo + webcam + vinheta.

Fonte de imagem: captura Filmora 3440x1440 (não o export letterbox).
Assuntos da TIMELINE vêm do SRT (audio/full.srt).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path("/Users/naubergois/canalnauber/producao/ep3-voz")
NORM = ROOT / "broll" / "norm"
PREVIEW = ROOT / "preview"
FINAL = ROOT / "final"
SRC = Path(
    "/Users/naubergois/Movies/Wondershare Filmora Mac/Recorded/VID_20260923_215910.mp4"
)
VINHETA = Path("/Users/naubergois/canalnauber/producao/abertura/final/vinheta-5s.mp4")
WM = Path("/Users/naubergois/canalnauber/arte/marca-dagua-150.png")
DUR = 1270.65
TRIM = 0.0

# Tempos do bruto (SRT). B-roll sem som.
TIMELINE = [
    (0, 22, None),  # oi / mesa
    (22, 56, "doordash"),  # DoorDash libera IA na seleção
    (56, 120, "anthropic"),  # Anthropic quer raciocínio cru
    (120, 153, "nicolelis"),  # pesquisador brasileiro
    (153, 503, "alphago"),  # lance 37 / Lee Sedol 2016
    (503, 640, "atelier"),  # pincel / paleta / atelier
    (640, 686, "imprensa"),  # atores, emprego, sociedade
    (686, 860, "senado"),  # escala 6x1 / PEC / 2 set 2026
    (860, 1040, "imprensa"),  # ganhos, oriente/ocidente
    (1040, DUR, "ciencia"),  # ciência, reprodutibilidade
]


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd[:8]), "...")
    subprocess.check_call(cmd)


def probe_dur(path: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(path),
        ],
        text=True,
    )
    return float(out.strip())


def loop_clip(src: Path, need: float, dest: Path) -> None:
    d = probe_dur(src)
    if d <= 0:
        raise RuntimeError(f"sem duração: {src}")
    loops = max(1, int(need // d) + 1)
    lst = dest.with_suffix(".txt")
    lst.write_text("".join(f"file '{src}'\n" for _ in range(loops)))
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            "-t",
            f"{need:.3f}",
            "-c",
            "copy",
            str(dest),
        ]
    )


def build_broll(out: Path) -> None:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, (a, b, name) in enumerate(TIMELINE):
        need = max(0.2, b - a)
        if name is None:
            clip = PREVIEW / f"seg-{i:02d}-black.mp4"
            run(
                [
                    "ffmpeg",
                    "-y",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-f",
                    "lavfi",
                    "-i",
                    f"color=c=black:s=1920x1080:r=25:d={need:.3f}",
                    "-c:v",
                    "libx264",
                    "-preset",
                    "ultrafast",
                    "-pix_fmt",
                    "yuv420p",
                    "-an",
                    str(clip),
                ]
            )
        else:
            src = NORM / f"{name}.mp4"
            if not src.exists():
                raise FileNotFoundError(src)
            clip = PREVIEW / f"seg-{i:02d}-{name}.mp4"
            loop_clip(src, need, clip)
        parts.append(clip)
    lst = PREVIEW / "broll-concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(lst),
            "-c",
            "copy",
            str(out),
        ]
    )


def render(broll: Path, dest: Path, preview_t: float | None = None) -> None:
    FINAL.mkdir(parents=True, exist_ok=True)
    # 3440x1440 → 16:9 pela direita (guarda a webcam). Overlay cobre o branco.
    ss: list[str] = []
    if TRIM:
        ss += ["-ss", str(TRIM)]
    if preview_t:
        ss += ["-t", str(preview_t)]
    vf = (
        "[0:v]crop=2560:1440:880:0,scale=1920:1080,setsar=1[base];"
        "[1:v]scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,setsar=1[br];"
        "[base][br]overlay=0:0:eof_action=pass:enable='gte(t,22)'[mix];"
        "[0:v]crop=280:280:2513:569,scale=400:400,pad=406:406:3:3:color=0xFFE14A[cam];"
        "[mix][cam]overlay=W-w-22:H-h-22:enable='gte(t,22)'[v1];"
        "[2:v]scale=84:84[w];"
        "[v1][w]overlay=24:H-h-24,unsharp=5:5:0.28,format=yuv420p[vout]"
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
            str(SRC),
            "-i",
            str(broll),
            "-i",
            str(WM),
            "-filter_complex",
            vf,
            "-map",
            "[vout]",
            "-map",
            "0:a",
            "-af",
            "highpass=f=80,loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:v",
            "h264_videotoolbox",
            "-b:v",
            "10M",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )


def glue_vinheta(main: Path, dest: Path) -> None:
    bump = PREVIEW / "vinheta-5s-25fps.mp4"
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(VINHETA),
            "-r",
            "25",
            "-c:v",
            "h264_videotoolbox",
            "-b:v",
            "10M",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-video_track_timescale",
            "12800",
            str(bump),
        ]
    )
    # 25 fps + 60 fps não cola com -c copy ( infla o relógio do container ).
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(bump),
            "-i",
            str(main),
            "-filter_complex",
            "[0:v]fps=25,format=yuv420p,setsar=1[v0];"
            "[1:v]fps=25,format=yuv420p,setsar=1[v1];"
            "[0:a]aformat=sample_rates=48000:channel_layouts=stereo[a0];"
            "[1:a]aformat=sample_rates=48000:channel_layouts=stereo[a1];"
            "[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]",
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "h264_videotoolbox",
            "-b:v",
            "10M",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )


def main() -> None:
    global TIMELINE
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    PREVIEW.mkdir(exist_ok=True)
    FINAL.mkdir(exist_ok=True)
    if mode == "preview":
        TIMELINE = [row for row in TIMELINE if row[0] < 100]
        TIMELINE[-1] = (TIMELINE[-1][0], 100.0, TIMELINE[-1][2])
    (ROOT / "broll" / "timeline.json").write_text(
        json.dumps(TIMELINE, indent=2), encoding="utf-8"
    )
    if mode == "preview":
        broll = PREVIEW / "broll-track-90.mp4"
        build_broll(broll)
        out = PREVIEW / "amostra-90s.mp4"
        render(broll, out, preview_t=90)
        print("PREVIEW", out)
        return
    broll = PREVIEW / "broll-track.mp4"
    if mode == "broll":
        build_broll(broll)
        return
    if not broll.exists():
        build_broll(broll)
    if mode == "full":
        mid = FINAL / "ep3-sem-vinheta.mp4"
        out = FINAL / "ep3-youtube.mp4"
        render(broll, mid, preview_t=None)
        glue_vinheta(mid, out)
        print("FINAL", out)
        return
    raise SystemExit("uso: montar.py preview|full|broll")


if __name__ == "__main__":
    main()
