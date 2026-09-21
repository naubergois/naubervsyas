#!/bin/zsh
# Equilibra voz humana x robô (ChatGPT) e empacota 16:9 para o YouTube.
set -euo pipefail

SRC="${SRC:-/Users/naubergois/Compartilhado/Filmora/Meu Vídeo-2.mp4}"
ROOT="/Users/naubergois/canalnauber/producao/chatgpt-voz"
FINAL="$ROOT/final"
WM="/Users/naubergois/canalnauber/arte/marca-dagua-150.png"
mkdir -p "$FINAL" "$ROOT/preview"

# Robô estoura (~0 dBTP). Você fica ~12–18 dB abaixo.
# highpass + denoise + de-esser no TTS + speechnorm (sobe a sua, segura o robô)
# + loudnorm YouTube (−14 LUFS / −1.5 dBTP).
AF="highpass=f=80,afftdn=nf=-20,deesser=i=0.32:m=0.5:f=0.55:s=o,speechnorm=e=10:c=6:p=0.92:r=0.001:f=0.001:l=1,loudnorm=I=-14:TP=-1.5:LRA=8,alimiter=limit=0.89:level=false"

# Ultrawide 2560×1080 → recorte 16:9 que preenche a tela (sem faixa preta).
# x=160 guarda o título ChatGPT Voz e a webcam.
VF="crop=1920:1080:160:0,unsharp=5:5:0.35,format=yuv420p"

preview() {
  local out="$ROOT/preview/amostra-70s.mp4"
  ffmpeg -y -hide_banner -ss 80 -t 70 -i "$SRC" -i "$WM" \
    -filter_complex "[0:v]${VF}[v];[1:v]scale=96:96[w];[v][w]overlay=W-w-28:H-h-28[vout]" \
    -map "[vout]" -map 0:a \
    -af "$AF" \
    -c:v h264_videotoolbox -b:v 8M -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -ac 2 \
    -movflags +faststart \
    "$out"
  echo "PREVIEW $out"
}

VINHETA="${VINHETA:-/Users/naubergois/canalnauber/producao/abertura/final/vinheta-5s.mp4}"

full() {
  local out="$FINAL/chatgpt-voz-youtube-fill.mp4"
  ffmpeg -y -hide_banner -i "$SRC" -i "$WM" \
    -filter_complex "[0:v]${VF}[v];[1:v]scale=84:84[w];[v][w]overlay=24:H-h-24[vout]" \
    -map "[vout]" -map 0:a \
    -af "$AF" \
    -c:v h264_videotoolbox -b:v 10M -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -ac 2 \
    -movflags +faststart \
    "$out"
  echo "FINAL $out"
}

# Vinheta 5s (30 fps) → 25 fps / AAC 48 k, cola no começo, corta o preto inicial do episódio.
vinheta() {
  local main="${1:-$FINAL/chatgpt-voz-sem-vinheta.mp4}"
  if [[ ! -f "$main" && -f "$FINAL/chatgpt-voz-youtube-fill.mp4" ]]; then
    main="$FINAL/chatgpt-voz-youtube-fill.mp4"
  fi
  local bump="$ROOT/preview/vinheta-5s-25fps.mp4"
  local trim="$ROOT/preview/episodio-sem-preto.mp4"
  local list="$ROOT/preview/concat-vinheta.txt"
  local out="$FINAL/chatgpt-voz-youtube.mp4"

  ffmpeg -y -hide_banner -i "$VINHETA" \
    -r 25 -c:v h264_videotoolbox -b:v 10M -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -ac 2 \
    -video_track_timescale 12800 \
    -movflags +faststart \
    "$bump"

  ffmpeg -y -hide_banner -ss 1.00 -i "$main" -c copy -avoid_negative_ts make_zero "$trim"
  printf "file '%s'\nfile '%s'\n" "$bump" "$trim" > "$list"
  ffmpeg -y -hide_banner -f concat -safe 0 -i "$list" -c copy -movflags +faststart "$out"
  echo "COM VINHETA $out"
}

case "${1:-full}" in
  preview) preview ;;
  full) full ;;
  vinheta) vinheta "${2:-}" ;;
  *) echo "uso: $0 preview|full|vinheta" >&2; exit 2 ;;
esac
