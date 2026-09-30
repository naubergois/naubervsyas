#!/usr/bin/env python3
"""Substitui B-roll genérico pelos vídeos verídicos do papo.

Janelas alinhadas ao SRT (áudio bruto) + offset da abertura capa:
  abertura ≈ bruto − 2  (0–15 thumb, 15–20 bridge, 20+ = youtube@27)

Fala → B-roll:
  ~32–55s  luta no Instagram          → REK Frankie × EngineAI T800
  ~78–147s Frankie / T800 / teleop    → REK (não humanoide de museu)
  ~147–175s Unitree G1 autônomo       → demo oficial UnifoLM-X2
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REK = ROOT / "broll" / "norm" / "rek-t800-fight.mp4"
UNITREE = ROOT / "broll" / "norm" / "unitree-g1-fight.mp4"
WM = Path("/Users/naubergois/canalnauber/arte/marca-dagua-150.png")

YOUTUBE_IN = ROOT / "final" / "ep2-youtube.mp4"
YOUTUBE_OUT = ROOT / "final" / "ep2-youtube-rek.mp4"

ABERTURA_IN = ROOT / "final" / "ep2-long-abertura-capa.mp4"
ABERTURA_OUT = ROOT / "final" / "ep2-long-rek.mp4"

# ep2-youtube: vinheta 0–5; TIMELINE +5
YT_REK = [
    (27.0, 60.0),    # bruto 22–55
    (83.0, 152.0),   # bruto 78–147 (Frankie → marketing Terminator)
]
YT_UNITREE = [
    (152.0, 180.0),  # bruto 147–175
]

# ep2-long-abertura-capa: abertura = youtube − 7 (= bruto − 2)
AB_REK = [
    (15.0, 53.0),    # bridge + intro luta
    (76.0, 145.0),   # Frankie / T800 / teleop / specs
]
AB_UNITREE = [
    (145.0, 173.0),  # Unitree G1
]


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd[:14]), "...", flush=True)
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


def enable_expr(windows: list[tuple[float, float]]) -> str:
    parts = [f"between(t\\,{a}\\,{b})" for a, b in windows]
    return "+".join(parts)


def overlay_broll(
    src: Path,
    dest: Path,
    broll: Path,
    windows: list[tuple[float, float]],
    *,
    use_wm: bool = True,
) -> None:
    if not broll.is_file():
        sys.exit(f"sem broll: {broll}")
    if not src.is_file():
        sys.exit(f"sem fonte: {src}")

    en = enable_expr(windows)
    # Webcam ~406x272 canto inferior direito; WM ~84x84 esquerdo.
    vf = (
        f"[1:v]scale=1920:1080:force_original_aspect_ratio=increase,"
        f"crop=1920:1080,setsar=1,format=yuv420p[br];"
        f"[0:v][br]overlay=0:0:eof_action=repeat:enable='{en}'[mix];"
        f"[0:v]crop=406:272:1492:786[cam];"
        f"[mix][cam]overlay=1492:786:enable='{en}'[v1]"
    )
    inputs = ["-i", str(src), "-stream_loop", "-1", "-i", str(broll)]
    if use_wm and WM.is_file():
        vf += (
            f";[2:v]scale=84:84[w];"
            f"[v1][w]overlay=24:972:enable='{en}',format=yuv420p[vout]"
        )
        inputs += ["-i", str(WM)]
        map_v = "[vout]"
    else:
        vf += ";[v1]format=yuv420p[vout]"
        map_v = "[vout]"

    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-stats",
        *inputs,
        "-filter_complex",
        vf,
        "-map",
        map_v,
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
        "-movflags",
        "+faststart",
        "-shortest",
        str(dest),
    ]
    run(cmd)
    print(f"OK {dest} ({probe_dur(dest):.2f}s)")


def patch(
    src: Path,
    dest: Path,
    rek_windows: list[tuple[float, float]],
    unitree_windows: list[tuple[float, float]],
) -> None:
    mid = dest.with_name(dest.stem + "-rek-only.mp4")
    print(f"== REK {rek_windows}", flush=True)
    overlay_broll(src, mid, REK, rek_windows)
    print(f"== Unitree {unitree_windows}", flush=True)
    overlay_broll(mid, dest, UNITREE, unitree_windows)
    mid.unlink(missing_ok=True)


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "abertura"
    if mode in ("youtube", "both"):
        patch(YOUTUBE_IN, YOUTUBE_OUT, YT_REK, YT_UNITREE)
    if mode in ("abertura", "both", "long"):
        src = ABERTURA_IN if ABERTURA_IN.is_file() else YOUTUBE_OUT
        if src == ABERTURA_IN:
            patch(src, ABERTURA_OUT, AB_REK, AB_UNITREE)
        else:
            patch(src, ABERTURA_OUT, YT_REK, YT_UNITREE)
        canon = ROOT / "final" / "ep2-long-abertura-capa.mp4"
        if ABERTURA_OUT.is_file():
            bak = ROOT / "final" / "ep2-long-abertura-capa-boxing-bak.mp4"
            if canon.is_file() and not bak.is_file():
                canon.rename(bak)
                print(f"backup {bak}")
            run(["cp", "-f", str(ABERTURA_OUT), str(canon)])
            print(f"canon {canon}")


if __name__ == "__main__":
    main()
