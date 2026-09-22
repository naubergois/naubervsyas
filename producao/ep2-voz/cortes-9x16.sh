#!/bin/zsh
set -euo pipefail
# Recortes 9:16 do ep. 2. Sem vinheta. Um encode por vez.
SRC="/Users/naubergois/canalnauber/producao/ep2-voz/final/ep2-youtube.mp4"
OUT="/Users/naubergois/canalnauber/producao/ep2-voz/final"
FONT="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
TMP="/tmp/ep2-cuts"
mkdir -p "$TMP"

python3 - <<'PY'
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
tmp = Path("/tmp/ep2-cuts")
W, H = 1080, 1920
CREAM = (247, 241, 227, 255)
BAR = (10, 10, 12, 158)

def card(name, lines, y0, box_h, fs):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(font_path, fs)
    d.rectangle((0, y0, W, y0 + box_h), fill=BAR)
    sizes = []
    total = 0
    for line in lines:
        b = d.textbbox((0, 0), line, font=font)
        sizes.append((b[2] - b[0], b[3] - b[1]))
        total += b[3] - b[1] + 12
    y = y0 + (box_h - total) // 2
    for line, (w, h) in zip(lines, sizes):
        d.text(((W - w) // 2, y), line, font=font, fill=CREAM)
        y += h + 12
    im.save(tmp / name)

# luta
card("luta-hook.png", ["NÃO ERA", "TERMINATOR"], 220, 340, 78)
card("luta-mid.png", ["TINHA PILOTO"], 220, 200, 72)
card("luta-end.png", ["ENTÃO O QUE", "ESTAVA LUTANDO?"], 220, 300, 64)
card("end-yt.png", ["PAPO INTEIRO NO YOUTUBE", "@naubervsyas"], 1500, 340, 46)
# consciência
card("cons-hook.png", ["ELA DISSE", "QUE NÃO"], 220, 300, 78)
card("cons-mid.png", ["NÃO SENTE.", "NÃO TEM UM EU."], 220, 280, 64)
card("cons-end.png", ["SE PARECE", "CONSCIENTE. É?"], 220, 300, 64)
# coragem
card("cor-hook.png", ["UMA FRASE", "PRA FECHAR"], 220, 280, 68)
card("cor-end.png", ["CORAGEM NÃO É", "TER TODAS", "AS RESPOSTAS"], 220, 380, 64)
print("overlays ok")
PY

render() {
  local start="$1" dur="$2" dest="$3"
  shift 3
  # overlays: file enable file enable ...
  local inputs=(-ss "$start" -t "$dur" -i "$SRC")
  local n=1
  local chain="[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v0]"
  local last=v0
  local i=1
  while [[ $# -ge 2 ]]; do
    local png="$1" en="$2"
    shift 2
    inputs+=(-loop 1 -i "$TMP/$png")
    chain+= ";[${last}][${n}:v]overlay=0:0:enable='${en}'[v${i}]"
    last="v${i}"
    n=$((n + 1))
    i=$((i + 1))
  done
  ffmpeg -y "${inputs[@]}" \
    -filter_complex "$chain" \
    -map "[${last}]" -map 0:a -t "$dur" \
    -c:v libx264 -preset veryfast -crf 19 -pix_fmt yuv420p \
    -c:a aac -b:a 160k -ar 48000 \
    -r 30 -movflags +faststart \
    "$dest"
}

echo "== luta =="
# master 101.1–131.1 = contato → dois humanos (30 s)
render 101.1 30 "$OUT/corte-luta-9x16.mp4" \
  luta-hook.png "between(t,0,3.4)" \
  luta-mid.png "between(t,4.2,14.5)" \
  luta-end.png "between(t,20,27.6)" \
  end-yt.png "between(t,27.6,30)"

echo "== consciencia =="
# master 220.2–253.2 = Yas nega + desafio do Nauber (33 s)
render 220.2 33 "$OUT/corte-consciencia-9x16.mp4" \
  cons-hook.png "between(t,0,3.6)" \
  cons-mid.png "between(t,4.2,16)" \
  cons-end.png "between(t,22,30.2)" \
  end-yt.png "between(t,30.2,33)"

echo "== coragem =="
# master 1513.2–1541.2 = fio + frase (28 s)
render 1513.2 28 "$OUT/corte-coragem-9x16.mp4" \
  cor-hook.png "between(t,0,4)" \
  cor-end.png "between(t,10,24.5)" \
  end-yt.png "between(t,24.5,28)"

ls -lh "$OUT"/corte-*-9x16.mp4
echo done
