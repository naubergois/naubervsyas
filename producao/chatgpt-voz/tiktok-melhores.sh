#!/bin/zsh
set -euo pipefail
SRC="/Users/naubergois/canalnauber/producao/chatgpt-voz/final/chatgpt-voz-youtube.mp4"
ART="/Users/naubergois/canalnauber/producao/chatgpt-voz/final/post-tt-9x16.png"
PERFIL="/Users/naubergois/canalnauber/arte/perfil-1080.png"
FONT="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
OUTDIR="/Users/naubergois/canalnauber/producao/chatgpt-voz/final"
TMP="/tmp/tt-hl/clips"
mkdir -p "$TMP"

python3 - <<'PY'
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
tmp = Path("/tmp/tt-hl/clips")

def card(name, lines, size, y0, box_h, fs):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(font_path, fs)
    d.rectangle((0, y0, size[0], y0 + box_h), fill=(10, 10, 12, 150))
    total_h = 0
    sizes = []
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=font)
        sizes.append((bbox[2] - bbox[0], bbox[3] - bbox[1]))
        total_h += bbox[3] - bbox[1] + 10
    y = y0 + (box_h - total_h) // 2
    for line, (w, h) in zip(lines, sizes):
        d.text(((size[0] - w) // 2, y), line, font=font, fill=(247, 241, 227, 255))
        y += h + 10
    im.save(tmp / name)

card("txt-hook.png", ["O RÓTULO VIRA", "CAMISA DE TIME"], (1080, 1920), 720, 300, 72)
card("txt-camisa.png", ["CAMISA DE TIME.", "A DISCUSSÃO ACABA."], (1080, 1920), 0, 220, 58)
card("txt-pergunta.png", ["DIREITA OU ESQUERDA?", "OU OLHAR O PROBLEMA?"], (1080, 1920), 0, 220, 52)
card("txt-pacote.png", ["ESCOLHEM O RÓTULO.", "LEVAM O PACOTE."], (1080, 1920), 0, 220, 56)
card("txt-pronto.png", ["SEM OLHAR O", "PROBLEMA ESPECÍFICO."], (1080, 1920), 0, 220, 56)
card("txt-payoff.png", ["ESQUERDA E DIREITA", "NÃO AJUDAM EM NADA."], (1080, 1920), 0, 220, 52)
card("txt-end.png", ["PAPO INTEIRO NO YOUTUBE", "@naubervsyas"], (1080, 1920), 1480, 360, 52)
print("overlays ok")
PY

render_talk() {
  local start="$1" dur="$2" overlay="$3" dest="$4"
  ffmpeg -y -ss "$start" -t "$dur" -i "$SRC" -loop 1 -i "$ART" -i "$overlay" \
    -filter_complex "[0:v]crop=380:310:1480:170,scale=1080:880:flags=lanczos,setsar=1[cam];\
[1:v]scale=1080:1040:force_original_aspect_ratio=increase,crop=1080:1040,setsar=1[art];\
[cam][art]vstack=inputs=2[stack];\
[stack][2:v]overlay=0:0[v]" \
    -map "[v]" -map 0:a -t "$dur" \
    -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 160k -ar 48000 \
    -r 30 -shortest "$dest"
}

ffmpeg -y -loop 1 -i "$ART" -i "$TMP/txt-hook.png" -f lavfi -i anullsrc=r=48000:cl=stereo \
  -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg];\
[bg][1:v]overlay=0:0[v]" \
  -map "[v]" -map 2:a -t 1.6 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 160k -ar 48000 -r 30 -shortest "$TMP/00-hook.mp4"

render_talk 152.3 4.9 "$TMP/txt-camisa.png" "$TMP/01-camisa.mp4"
render_talk 107.15 10.2 "$TMP/txt-pergunta.png" "$TMP/02-pergunta.mp4"
render_talk 189.2 7.2 "$TMP/txt-pacote.png" "$TMP/03-pacote.mp4"
render_talk 632.35 8.4 "$TMP/txt-pronto.png" "$TMP/04-pronto.mp4"
render_talk 828.43 3.7 "$TMP/txt-payoff.png" "$TMP/05-payoff.mp4"

ffmpeg -y -loop 1 -i "$PERFIL" -i "$TMP/txt-end.png" -f lavfi -i anullsrc=r=48000:cl=stereo \
  -filter_complex "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[bg];\
[bg][1:v]overlay=0:0[v]" \
  -map "[v]" -map 2:a -t 2.8 -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 160k -ar 48000 -r 30 -shortest "$TMP/06-end.mp4"

printf '%s\n' \
  "file '$TMP/00-hook.mp4'" \
  "file '$TMP/01-camisa.mp4'" \
  "file '$TMP/02-pergunta.mp4'" \
  "file '$TMP/03-pacote.mp4'" \
  "file '$TMP/04-pronto.mp4'" \
  "file '$TMP/05-payoff.mp4'" \
  "file '$TMP/06-end.mp4" \
  > "$TMP/list.txt"

# fix last line if quote broke
cat > "$TMP/list.txt" <<EOF
file '$TMP/00-hook.mp4'
file '$TMP/01-camisa.mp4'
file '$TMP/02-pergunta.mp4'
file '$TMP/03-pacote.mp4'
file '$TMP/04-pronto.mp4'
file '$TMP/05-payoff.mp4'
file '$TMP/06-end.mp4'
EOF

ffmpeg -y -f concat -safe 0 -i "$TMP/list.txt" -c:v libx264 -preset veryfast -crf 18 \
  -pix_fmt yuv420p -c:a aac -b:a 160k -ar 48000 -movflags +faststart \
  "$OUTDIR/tiktok-melhores-32s.mp4"

ffprobe -v error -show_entries format=duration -show_entries stream=width,height -of default=nw=1 \
  "$OUTDIR/tiktok-melhores-32s.mp4"
ls -lh "$OUTDIR/tiktok-melhores-32s.mp4"
