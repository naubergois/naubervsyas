#!/bin/zsh
# Recoloca o mascote AC/DC no fechamento da vinheta (5s, 9x16, 90s).
set -euo pipefail

P="/Users/naubergois/canalnauber/producao/abertura"
ARTE="/Users/naubergois/canalnauber/arte"
CORTES="$P/cortes"
FINAL="$P/final"
MUSIC="$P/audio/ready-aim-fire.mp3"

python3 - <<'PY'
from pathlib import Path
from PIL import Image

arte = Path("/Users/naubergois/canalnauber/arte")
cortes = Path("/Users/naubergois/canalnauber/producao/abertura/cortes")

icon = Image.open(arte / "icone-800.png").convert("RGBA")
wm = Image.open(arte / "wordmark.png").convert("RGBA")

# recorta o wordmark no que de fato tem tinta
bbox = wm.getbbox()
if bbox:
    wm = wm.crop(bbox)

def card_16x9() -> Image.Image:
    canvas = Image.new("RGB", (1920, 1080), (10, 10, 12))
    face = icon.resize((560, 560), Image.Resampling.LANCZOS)
    canvas.paste(face.convert("RGB"), (680, 150))
    # mesma faixa do cartão antigo: ~552 px, y 822
    w = 552
    h = max(1, round(wm.height * (w / wm.width)))
    mark = wm.resize((w, h), Image.Resampling.LANCZOS)
    x = (1920 - w) // 2
    y = 822
    canvas.paste(mark, (x, y), mark)
    return canvas

def card_9x16() -> Image.Image:
    canvas = Image.new("RGB", (1080, 1920), (10, 10, 12))
    face = icon.resize((720, 720), Image.Resampling.LANCZOS)
    canvas.paste(face.convert("RGB"), ((1080 - 720) // 2, 380))
    w = 860
    h = max(1, round(wm.height * (w / wm.width)))
    mark = wm.resize((w, h), Image.Resampling.LANCZOS)
    canvas.paste(mark, ((1080 - w) // 2, 380 + 720 + 56), mark)
    return canvas

card_16x9().save(cortes / "endcard_logo.png", optimize=True)
card_9x16().save(cortes / "endcard_logo_9x16.png", optimize=True)
print("endcards ok")
PY

zoom_logo() {
  local src="$1" dest="$2" dur="$3" w="$4" h="$5"
  local frames
  frames=$(python3 -c "print(int(round(float('$dur') * 30)))")
  ffmpeg -y -hide_banner -loglevel error \
    -loop 1 -i "$src" \
    -vf "zoompan=z='min(1.06,1+0.06*on/${frames})':d=${frames}:s=${w}x${h}:fps=30,format=yuv420p" \
    -t "$dur" -an \
    -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
    "$dest"
}

zoom_logo "$CORTES/endcard_logo.png" "$CORTES/vh_logo.mp4" 2.78 1920 1080
zoom_logo "$CORTES/endcard_logo.png" "$CORTES/endcard_logo.mp4" 4.10 1920 1080
zoom_logo "$CORTES/endcard_logo_9x16.png" "$CORTES/vh_logo_9x16.mp4" 2.78 1080 1920

# 16:9 — luta + flash + logo novo, trilha original
ffmpeg -y -hide_banner -loglevel error \
  -i "$CORTES/vh_luta.mp4" \
  -i "$CORTES/vh_flash.mp4" \
  -i "$CORTES/vh_logo.mp4" \
  -i "$MUSIC" \
  -filter_complex "
    [0:v]fps=30,format=yuv420p,setsar=1[v0];
    [1:v]fps=30,format=yuv420p,setsar=1[v1];
    [2:v]fps=30,format=yuv420p,setsar=1[v2];
    [v0][v1][v2]concat=n=3:v=1:a=0[v];
    [3:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:5.021333,asetpts=PTS-STARTPTS,volume=0.85[a]
  " \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -t 5.021333 -movflags +faststart \
  "$FINAL/vinheta-5s.mp4"

# 9x16 — recorte da luta/flash + cartão vertical
ffmpeg -y -hide_banner -loglevel error \
  -i "$CORTES/vh_luta.mp4" \
  -i "$CORTES/vh_flash.mp4" \
  -i "$CORTES/vh_logo_9x16.mp4" \
  -i "$MUSIC" \
  -filter_complex "
    [0:v]crop=1080:1080:420:0,scale=1080:1920,fps=30,format=yuv420p,setsar=1[v0];
    [1:v]crop=1080:1080:420:0,scale=1080:1920,fps=30,format=yuv420p,setsar=1[v1];
    [2:v]fps=30,format=yuv420p,setsar=1[v2];
    [v0][v1][v2]concat=n=3:v=1:a=0[v];
    [3:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:5.021333,asetpts=PTS-STARTPTS,volume=0.85[a]
  " \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -t 5.021333 -movflags +faststart \
  "$FINAL/vinheta-5s-9x16.mp4"

# Abertura 90s: troca só o cartão final
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$FINAL/abertura-canal-90s.mp4")
START=$(python3 -c "print(max(0, round(float('$DUR')-4.1, 3)))")
ffmpeg -y -hide_banner -loglevel error \
  -i "$FINAL/abertura-canal-90s.mp4" \
  -i "$CORTES/endcard_logo.mp4" \
  -filter_complex "
    [0:v]trim=0:${START},setpts=PTS-STARTPTS[v0];
    [0:a]atrim=0:${START},asetpts=PTS-STARTPTS[a0];
    [1:v]fps=30,format=yuv420p,setsar=1,trim=0:4.1,setpts=PTS-STARTPTS[v1];
    [0:a]atrim=start=${START},asetpts=PTS-STARTPTS[a1];
    [v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]
  " \
  -map "[v]" -map "[a]" \
  -c:v libx264 -preset veryfast -crf 19 -pix_fmt yuv420p \
  -c:a aac -b:a 256k -ar 48000 \
  -movflags +faststart \
  "$FINAL/abertura-canal-90s-new.mp4"
mv "$FINAL/abertura-canal-90s-new.mp4" "$FINAL/abertura-canal-90s.mp4"

# cópias 25 fps que o montar.py cola
for dest in \
  /Users/naubergois/canalnauber/producao/ep2-voz/preview/vinheta-5s-25fps.mp4 \
  /Users/naubergois/canalnauber/producao/ep3-voz/preview/vinheta-5s-25fps.mp4 \
  /Users/naubergois/canalnauber/producao/ep4-voz/preview/vinheta-5s-25fps.mp4 \
  /Users/naubergois/canalnauber/producao/chatgpt-voz/preview/vinheta-5s-25fps.mp4
do
  mkdir -p "$(dirname "$dest")" || true
  if ! ffmpeg -y -hide_banner -loglevel error \
    -i "$FINAL/vinheta-5s.mp4" \
    -vf "fps=25,format=yuv420p,setsar=1" \
    -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -ac 2 \
    -movflags +faststart "$dest"
  then
    echo "skip $dest"
  fi
done

echo READY
ls -lh "$FINAL/vinheta-5s.mp4" "$FINAL/vinheta-5s-9x16.mp4" "$FINAL/abertura-canal-90s.mp4"
