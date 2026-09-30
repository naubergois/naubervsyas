#!/usr/bin/env python3
"""Piloto Caderno de Farol: locução Luciana + Ken Burns + trilha + 16:9 e Short."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS = Path("/Users/naubergois/.cursor/projects/Users-naubergois-canalnauber/assets")
ARTE = Path("/Users/naubergois/canalnauber/arte")
MUSIC = Path("/Users/naubergois/canalnauber/producao/abertura/audio/our-story-begins.mp3")
AUDIO = ROOT / "audio"
ELEVEN = AUDIO / "eleven"
PREV = ROOT / "preview"
I2V = PREV / "i2v"
FINAL = ROOT / "final"
STILLS = ROOT / "stills"
WATER = ARTE / "marca-dagua-150.png"
FONT = Path("/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf")

W, H = 1920, 1080
RW, RH = 1280, 720
FPS = 25

CHUNKS = [
    ("00", "A letra era dela. A data era amanhã.", ROOT / "stills" / "amanha-clean.png", "in"),
    (
        "01",
        "Cora trabalha no farol de Mucuripe. De noite o mar não traz peixe. Traz folha. Gráfico molhado. Pergunta que alguém largou no meio.",
        ASSETS / "caderno-de-farol-mare.png",
        "right",
    ),
    (
        "02",
        "O regulamento cabe numa linha. Carimba. Guarda. Não lê.",
        ASSETS / "caderno-de-farol-selo.png",
        "punch",
    ),
    (
        "03",
        "Ela carimba até a mão doer. Rascunho, um gato feito das páginas que ela recusou, acompanha o selo.",
        ASSETS / "caderno-de-farol-rascunho.png",
        "in",
    ),
    (
        "04",
        "Uma noite a lâmpada do farol já vinha fraca. Chega uma folha ainda quente. Sem data velha. A letra é a dela. No canto, o carimbo: amanhã.",
        ASSETS / "caderno-de-farol-cartaz-oficial.png",
        "up",
    ),
    ("05", "Cora lê um verbete só.", ASSETS / "caderno-de-farol-cora.png", "in"),
    (
        "06",
        "A cidade apaga em onda. Iracema. O porto. A faixa de prédio.",
        ASSETS / "cdf-cidade.png",
        "right",
    ),
    (
        "07",
        "A lâmpada morre. No escuro a página ainda brilha. A última linha não é pergunta. É ordem. Não carimba essa.",
        ROOT / "stills" / "amanha-clean.png",
        "punch",
    ),
    (
        "08",
        "De manhã Seu Lino abre a porta do farol. A lâmpada fria. O caderno aberto. Cora sem sombra no chão de aço.",
        ASSETS / "cdf-sombra.png",
        "up",
    ),
    (
        "09",
        "Uma folha nova encosta no vidro. Por fora.",
        ASSETS / "cdf-vidro.png",
        "in",
    ),
]


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(str(c) for c in cmd[:10]), "...", flush=True)
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None)


def probe(path: Path) -> float:
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


def say_chunk(text: str, dest: Path) -> None:
    eleven = ELEVEN / f"{dest.stem}.mp3"
    src = eleven if eleven.is_file() else None
    if src:
        run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(src),
                "-ac",
                "1",
                "-ar",
                "48000",
                str(dest),
            ]
        )
        return
    aiff = dest.with_suffix(".aiff")
    run(["say", "-v", "Luciana", "-r", "158", "-o", str(aiff), text])
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(aiff),
            "-ac",
            "1",
            "-ar",
            "48000",
            str(dest),
        ]
    )
    aiff.unlink(missing_ok=True)


def fit_i2v(src: Path, dest: Path, seconds: float) -> None:
    frames = max(int(seconds * FPS), 8)
    vf = (
        f"scale={RW}:{RH}:force_original_aspect_ratio=increase,"
        f"crop={RW}:{RH},fps={FPS},setsar=1,format=yuv420p"
    )
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-stream_loop",
            "-1",
            "-i",
            str(src),
            "-vf",
            vf,
            "-frames:v",
            str(frames),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-an",
            str(dest),
        ]
    )


def zoom_expr(kind: str) -> tuple[str, str, str]:
    if kind == "punch":
        z = "min(1.18,1.0+0.012*on)"
        x = "iw/2-(iw/zoom/2)"
        y = "ih/2-(ih/zoom/2)+8*sin(on/40)"
    elif kind == "right":
        z = "1.08"
        x = "iw/2-(iw/zoom/2)+0.35*on"
        y = "ih/2-(ih/zoom/2)"
    elif kind == "up":
        z = "min(1.14,1.02+0.00045*on)"
        x = "iw/2-(iw/zoom/2)"
        y = "ih/2-(ih/zoom/2)-0.22*on"
    else:
        z = "min(1.12,1.0+0.0004*on)"
        x = "iw/2-(iw/zoom/2)"
        y = "ih/2-(ih/zoom/2)"
    return z, x, y


def ken_burns(src: Path, dest: Path, seconds: float, kind: str) -> None:
    frames = max(int(seconds * FPS), 8)
    z, x, y = zoom_expr(kind)
    vf = (
        f"scale={RW}:{RH}:force_original_aspect_ratio=increase,"
        f"crop={RW}:{RH},"
        f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={RW}x{RH}:fps={FPS},"
        f"fps={FPS},format=yuv420p,setsar=1"
    )
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
            str(src),
            "-vf",
            vf,
            "-frames:v",
            str(frames),
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


def end_card(dest: Path, seconds: float = 4.0) -> None:
    from PIL import Image, ImageDraw, ImageFont

    STILLS.mkdir(parents=True, exist_ok=True)
    png = STILLS / "endcard.png"
    im = Image.new("RGB", (W, H), (8, 8, 10))
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(str(FONT), 72)
    small = ImageFont.truetype(str(FONT), 36)
    title = "CADERNO DE FAROL"
    sub = "ep. 1   @naubervsyas"
    tb = draw.textbbox((0, 0), title, font=font)
    sb = draw.textbbox((0, 0), sub, font=small)
    draw.text(((W - (tb[2] - tb[0])) // 2, H // 2 - 70), title, font=font, fill=(247, 241, 227))
    draw.text(((W - (sb[2] - sb[0])) // 2, H // 2 + 24), sub, font=small, fill=(255, 225, 74))
    im.save(png)
    n = int(seconds * FPS)
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
            str(png),
            "-vf",
            f"fps={FPS},format=yuv420p,setsar=1",
            "-frames:v",
            str(n),
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "18",
            "-an",
            str(dest),
        ]
    )


def write_srt(cues: list[tuple[float, float, str]], dest: Path) -> None:
    def ts(t: float) -> str:
        ms = int(round(t * 1000))
        h, rem = divmod(ms, 3_600_000)
        m, rem = divmod(rem, 60_000)
        s, ms = divmod(rem, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, (a, b, text) in enumerate(cues, 1):
        lines.append(str(i))
        lines.append(f"{ts(a)} --> {ts(b)}")
        lines.append(text)
        lines.append("")
    dest.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    AUDIO.mkdir(parents=True, exist_ok=True)
    PREV.mkdir(parents=True, exist_ok=True)
    FINAL.mkdir(parents=True, exist_ok=True)

    clips = []
    voices = []
    cues: list[tuple[float, float, str]] = []
    t = 0.0
    for key, text, still, kind in CHUNKS:
        wav = AUDIO / f"{key}.wav"
        eleven_mp3 = ELEVEN / f"{key}.mp3"
        if eleven_mp3.is_file() or not wav.is_file():
            say_chunk(text, wav)
        hold = max(probe(wav) + 0.55, 5.2)
        clip = PREV / f"{key}.mp4"
        i2v = I2V / f"{key}.mp4"
        if i2v.is_file() and i2v.stat().st_size > 8000:
            fit_i2v(i2v, clip, hold)
        elif not clip.is_file():
            ken_burns(still, clip, hold, kind)
        clips.append(clip)
        voices.append(wav)
        cues.append((t + 0.15, t + probe(wav) + 0.1, text))
        t += hold

    end = PREV / "end.mp4"
    end_card(end, 4.0)
    clips.append(end)

    lista = PREV / "lista.txt"
    lista.write_text("".join(f"file '{p.name}'\n" for p in clips), encoding="utf-8")
    picture = PREV / "picture.mp4"
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
            str(lista),
            "-c",
            "copy",
            str(picture),
        ]
    )

    # voz: silêncio até o tamanho de cada clipe, depois concat
    padded = []
    for wav, clip in zip(voices, clips[:-1]):
        dclip = probe(clip)
        dwav = probe(wav)
        pad = PREV / f"{wav.stem}-pad.wav"
        extra = max(dclip - dwav, 0.05)
        run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(wav),
                "-af",
                f"apad=pad_dur={extra:.3f}",
                "-t",
                f"{dclip:.3f}",
                "-ar",
                "48000",
                "-ac",
                "1",
                str(pad),
            ]
        )
        padded.append(pad)
    silence = PREV / "end-silence.wav"
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
            "anullsrc=r=48000:cl=mono",
            "-t",
            f"{probe(end):.3f}",
            str(silence),
        ]
    )
    padded.append(silence)
    concat_a = PREV / "voz-lista.txt"
    concat_a.write_text("".join(f"file '{p.name}'\n" for p in padded), encoding="utf-8")
    voice = PREV / "voz.wav"
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
            str(concat_a),
            "-c",
            "copy",
            str(voice),
        ]
    )

    srt = FINAL / "legendas.srt"
    write_srt(cues, srt)
    srt_prev = PREV / "legendas.srt"
    srt_prev.write_text(srt.read_text(encoding="utf-8"), encoding="utf-8")
    dur = probe(picture)
    master = FINAL / "caderno-de-farol-ep1.mp4"
    vf = (
        f"scale={W}:{H}:flags=lanczos,fps={FPS},setsar=1,"
        f"fade=t=out:st={max(dur-1.2,0.1):.2f}:d=1.2"
    )
    if WATER.is_file():
        run(
            [
                "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-i",
                str(picture.resolve()),
                "-i",
                str(voice.resolve()),
                "-i",
                str(MUSIC.resolve()),
                "-i",
                str(WATER.resolve()),
                "-filter_complex",
                f"[0:v]{vf}[v0];"
                f"[3:v]format=rgba,colorchannelmixer=aa=0.55[wm];"
                f"[v0][wm]overlay=36:H-h-28[v];"
                f"[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,aformat=channel_layouts=stereo,aresample=48000,asplit=2[voz1][voz2];"
                f"[2:a]atrim=0:{dur:.3f},asetpts=PTS-STARTPTS,volume=0.13,aformat=channel_layouts=stereo,aresample=48000[bed];"
                f"[bed][voz1]sidechaincompress=threshold=0.06:ratio=7:attack=20:release=260:makeup=1.05[duck];"
                f"[duck][voz2]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]",
                "-map",
                "[v]",
                "-map",
                "[a]",
                "-c:v",
                "h264_videotoolbox",
                "-b:v",
                "8M",
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
                "-t",
                f"{dur:.3f}",
                str(master.resolve()),
            ],
            cwd=PREV,
        )
    else:
        raise SystemExit("marca d'água ausente")

    # Short 9:16: primeiros 4 takes + clímax (00,05,06,07) ~35s
    short_list = PREV / "short-lista.txt"
    short_clips = [PREV / f"{k}.mp4" for k in ("00", "05", "06", "07")]
    short_list.write_text("".join(f"file '{p.name}'\n" for p in short_clips), encoding="utf-8")
    short_pic = PREV / "short-pic.mp4"
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
            str(short_list),
            "-c",
            "copy",
            str(short_pic),
        ]
    )
    short_voice_parts = [PREV / f"{k}-pad.wav" for k in ("00", "05", "06", "07")]
    short_al = PREV / "short-voz-lista.txt"
    short_al.write_text("".join(f"file '{p.name}'\n" for p in short_voice_parts), encoding="utf-8")
    short_voice = PREV / "short-voz.wav"
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
            str(short_al),
            "-c",
            "copy",
            str(short_voice),
        ]
    )
    short_out = FINAL / "caderno-de-farol-ep1-short.mp4"
    sd = probe(short_pic)
    run(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(short_pic),
            "-i",
            str(short_voice),
            "-i",
            str(MUSIC),
            "-filter_complex",
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps={FPS},setsar=1,format=yuv420p[v];"
            f"[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,aformat=channel_layouts=stereo,aresample=48000,asplit=2[voz1][voz2];"
            f"[2:a]atrim=0:{sd:.3f},asetpts=PTS-STARTPTS,volume=0.12,aformat=channel_layouts=stereo[bed];"
            f"[bed][voz1]sidechaincompress=threshold=0.06:ratio=7:attack=20:release=260:makeup=1.05[duck];"
            f"[duck][voz2]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]",
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "h264_videotoolbox",
            "-b:v",
            "6M",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            "-t",
            f"{sd:.3f}",
            str(short_out),
        ]
    )
    print("MASTER", master, f"{probe(master):.1f}s")
    print("SHORT", short_out, f"{probe(short_out):.1f}s")


if __name__ == "__main__":
    sys.exit(main())
