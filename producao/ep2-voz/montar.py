#!/usr/bin/env python3
"""Monta o episódio 2: voz original + B-roll mudo + webcam + vinheta."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path("/Users/naubergois/canalnauber/producao/ep2-voz")
NORM = ROOT / "broll" / "norm"
PREVIEW = ROOT / "preview"
FINAL = ROOT / "final"
SRC = Path("/Users/naubergois/Compartilhado/Filmora/Meu Vídeo-3.mp4")
VINHETA = Path("/Users/naubergois/canalnauber/producao/abertura/final/vinheta-5s.mp4")
WM = Path("/Users/naubergois/canalnauber/arte/marca-dagua-150.png")
DUR = 1543.76
TRIM = 0.80  # corta o preto inicial, como no ep. 1

# Assuntos na fala (tempo no bruto). B-roll sem som.
TIMELINE = [
    (0, 22, None),  # oi + não fala de eleição — deixa a mesa
    (22, 55, "boxing-spar"),  # luta (sparring)
    (55, 95, "humanoide"),
    (95, 125, "boxing-spar"),
    (125, 155, "kb-vr"),  # teleoperação / VR
    (155, 175, "delivery-robot"),  # dois vídeos circulando
    (175, 215, "robot-arm"),  # Transformer = arquitetura
    (215, 250, "package-robot"),
    (250, 300, "brain-spect"),  # consciência
    (300, 360, "humanoide"),
    (360, 430, "brain-spect"),
    (430, 500, "robot-museum"),
    (500, 560, "kb-igreja"),  # religião / não sei
    (560, 640, "iris-robot"),
    (640, 710, "kb-igreja"),
    (710, 780, "kb-stf"),  # STF / escrutínio
    (780, 850, "kb-aviao"),  # foto do avião
    (850, 940, "kb-imprensa"),
    (940, 1040, "kb-stf"),
    (1040, 1140, "kb-imprensa"),
    (1140, 1240, "kb-aviao"),
    (1240, 1360, "kb-stf"),
    (1360, 1480, "kb-imprensa"),
    (1480, DUR, "kb-sf"),
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
    tmp = dest.with_name(dest.stem + "-full.mp4")
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
    if tmp.exists():
        tmp.unlink()


def build_broll(out: Path) -> None:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    parts = []
    for i, (a, b, name) in enumerate(TIMELINE):
        need = max(0.2, b - a)
        if name is None:
            # faixa preta = o overlay some (alpha) — geramos 1px verde-chave? 
            # usamos um mp4 preto; o filter trata None como “sem overlay”
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
    # Recorte 16:9 da direita (guarda a webcam). B-roll cobre o branco.
    # Webcam extraída por cima. Áudio do episódio, loudnorm leve.
    ss = ["-ss", str(TRIM)]
    if preview_t:
        ss += ["-t", str(preview_t)]
    # Só o primeiro bloco (0–22s) fica sem B-roll. O resto cobre o branco do ChatGPT.
    vf = (
        "[0:v]crop=1920:1080:640:0,setsar=1[base];"
        "[1:v]scale=1920:1080:force_original_aspect_ratio=increase,"
        "crop=1920:1080,setsar=1[br];"
        "[base][br]overlay=0:0:eof_action=pass:enable='gte(t,22)'[mix];"
        "[0:v]crop=372:248:2168:792,scale=400:266,pad=406:272:3:3:color=0xFFE14A[cam];"
        "[mix][cam]overlay=W-w-22:H-h-22:enable='gte(t,22)'[v1];"
        "[2:v]scale=84:84[w];"
        "[v1][w]overlay=24:H-h-24,unsharp=5:5:0.28,format=yuv420p[vout]"
    )
    # geq alpha on near-black: black B-roll segments become transparent
    cmd = [
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
        "loudnorm=I=-16:TP=-1.5:LRA=11",
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
    run(cmd)


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
    lst = PREVIEW / "concat-vinheta.txt"
    lst.write_text(f"file '{bump}'\nfile '{main}'\n")
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
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )


def main() -> None:
    import sys

    global TIMELINE
    mode = sys.argv[1] if len(sys.argv) > 1 else "preview"
    (ROOT / "preview").mkdir(exist_ok=True)
    (ROOT / "final").mkdir(exist_ok=True)
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
        mid = FINAL / "ep2-sem-vinheta.mp4"
        out = FINAL / "ep2-youtube.mp4"
        render(broll, mid, preview_t=None)
        glue_vinheta(mid, out)
        print("FINAL", out)
        return
    raise SystemExit("uso: montar.py preview|full|broll")


if __name__ == "__main__":
    main()
