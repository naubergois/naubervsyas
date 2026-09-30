#!/usr/bin/env python3
"""Ep2 long-form: capa TINHA PILOTO + luta REK nos primeiros ~20s, sem vinheta no início.

Substitui o bloco visual 0–25s (vinheta + orb ChatGPT) por thumb Ken Burns + REK fight,
mantendo o áudio original a partir do fim da vinheta (5s).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LONG = ROOT / "final" / "ep2-youtube-rek.mp4"
if not LONG.is_file():
    LONG = ROOT / "final" / "ep2-youtube.mp4"
THUMB = ROOT / "final" / "thumb.jpg"
REK = ROOT / "broll" / "norm" / "rek-t800-fight.mp4"
VINHETA = Path("/Users/naubergois/canalnauber/producao/abertura/final/vinheta-5s.mp4")
OUT = ROOT / "final" / "ep2-long-abertura-capa.mp4"
TMP = Path("/tmp/ep2-a1/build")

W, H = 1920, 1080
FPS = 25
THUMB_SEC = 15.0
BOXING_SEC = 5.0  # nome legado: agora é bridge REK
OPEN_SEC = THUMB_SEC + BOXING_SEC  # 20s fight/capa visuals
VINHETA_DUR = 5.021333
BODY_A_SKIP = VINHETA_DUR  # áudio/vídeo do corpo após vinheta
BODY_V_JOIN = 27.0  # REK B-roll no long (pula vinheta + orb)


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(c) for c in cmd[:12]), "...", flush=True)
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


def build_thumb_open(dest: Path) -> None:
    """Ken Burns leve em 720p → upscale (zoompan em 1080p demora demais no Mac)."""
    frames = int(THUMB_SEC * FPS)
    z = f"if(lte(on,{int(0.8*FPS)}),1+0.004*on,1+0.004*{int(0.8*FPS)}+0.00022*(on-{int(0.8*FPS)}))"
    rw, rh = 1280, 720
    vf = (
        f"scale={rw}:{rh}:force_original_aspect_ratio=increase,"
        f"crop={rw}:{rh},"
        f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)+18*sin(on/120)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s={rw}x{rh}:fps={FPS},"
        f"scale={W}:{H}:flags=lanczos,format=yuv420p"
    )
    nframes = int(THUMB_SEC * FPS)
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-loop",
            "1",
            "-framerate",
            str(FPS),
            "-i",
            str(THUMB),
            "-vf",
            vf,
            "-frames:v",
            str(nframes),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-an",
            str(dest),
        ]
    )


def build_boxing_bridge(dest: Path) -> None:
    """Bridge REK (Frankie vs T800), sem áudio. Fallback: trecho do long."""
    if REK.is_file():
        run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-ss",
                "0",
                "-t",
                str(BOXING_SEC),
                "-i",
                str(REK),
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "18",
                "-pix_fmt",
                "yuv420p",
                str(dest),
            ]
        )
        return
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(BODY_V_JOIN),
            "-t",
            str(BOXING_SEC),
            "-i",
            str(LONG),
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(dest),
        ]
    )


def build_open_mux(vid: Path, aud_slice: Path, dest: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(vid),
            "-i",
            str(aud_slice),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            "-ar",
            "48000",
            "-shortest",
            str(dest),
        ]
    )


def extract_audio_slice(start: float, dur: float, dest: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(start),
            "-t",
            str(dur),
            "-i",
            str(LONG),
            "-vn",
            "-c:a",
            "aac",
            "-b:a",
            "256k",
            "-ar",
            "48000",
            str(dest),
        ]
    )


def build_tail(dest: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(BODY_V_JOIN),
            "-i",
            str(LONG),
            "-c",
            "copy",
            "-avoid_negative_ts",
            "make_zero",
            str(dest),
        ]
    )


def concat_parts(open_part: Path, tail: Path, dest: Path) -> None:
    lst = TMP / "concat.txt"
    lst.write_text(f"file '{open_part}'\nfile '{tail}'\n")
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
            "-movflags",
            "+faststart",
            str(dest),
        ]
    )


def main() -> None:
    if not LONG.is_file():
        sys.exit(f"sem long: {LONG}")
    if not THUMB.is_file():
        sys.exit(f"sem thumb: {THUMB}")

    TMP.mkdir(parents=True, exist_ok=True)
    thumb_v = TMP / "thumb-open.mp4"
    boxing_v = TMP / "boxing-bridge.mp4"
    open_v = TMP / "open-video.mp4"
    open_a = TMP / "open-audio.m4a"
    open_av = TMP / "open-av.mp4"
    tail = TMP / "tail.mp4"

    build_thumb_open(thumb_v)
    build_boxing_bridge(boxing_v)

    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(thumb_v),
            "-i",
            str(boxing_v),
            "-filter_complex",
            "[0:v][1:v]concat=n=2:v=1:a=0[v]",
            "-map",
            "[v]",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            str(open_v),
        ]
    )

    extract_audio_slice(BODY_A_SKIP, OPEN_SEC, open_a)
    build_open_mux(open_v, open_a, open_av)
    build_tail(tail)
    concat_parts(open_av, tail, OUT)

    dur = probe_dur(OUT)
    print(f"OK {OUT} ({dur:.2f}s)")


if __name__ == "__main__":
    main()
