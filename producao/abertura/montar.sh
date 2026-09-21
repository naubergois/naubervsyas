#!/bin/zsh
# Remaster: falas CONACI (feliz + Picasso), carreira MP,
# vídeos CivitAI do Exterminador + zoom das stills, rock Our Story Begins.
set -euo pipefail

P="/Users/naubergois/canalnauber/producao/abertura"
CORTES="$P/cortes"
FINAL="$P/final"
AI="$P/ai"
MUSIC="$P/audio/our-story-begins.mp3"
DADO="/Users/naubergois/palestraconaci/cortes-najara/02-dado-nao-basta.mp4"
APRES="/Users/naubergois/palestraconaci/cortes-najara/01-apresentacao.mp4"

mkdir -p "$CORTES" "$FINAL"
fit="scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:black,fps=30,setsar=1"

fitvid() {
  ffmpeg -y -hide_banner -loglevel error \
    -f lavfi -i anullsrc=r=48000:cl=stereo \
    -i "$1" -t 5 \
    -filter_complex "[1:v]${fit}[v]" \
    -map "[v]" -map 0:a -shortest \
    -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -ac 2 \
    -movflags +faststart "$2"
}

# I2V CivitAI (esqueleto / olho / crânio) + T2V (walk / lightning)
fitvid "$AI/civitai-i2v-esqueleto.mp4" "$CORTES/term_esqueleto.mp4"
fitvid "$AI/civitai-i2v-olho.mp4" "$CORTES/term_olho.mp4"
fitvid "$AI/civitai-i2v-cranio.mp4" "$CORTES/term_cranio_civitai.mp4"
fitvid "$AI/civitai-term-walk.mp4" "$CORTES/term_walk_civitai.mp4"
fitvid "$AI/civitai-term-lightning.mp4" "$CORTES/term_lightning_civitai.mp4"

cat > "$CORTES/lista.txt" <<'EOF'
file 'hook_conaci.mp4'
file 'term_esqueleto.mp4'
file 'carreira_1.mp4'
file 'carreira_3.mp4'
file 'term_walk_civitai.mp4'
file 'carreira_5.mp4'
file 'carreira_6.mp4'
file 'fala_feliz.mp4'
file 'term_olho.mp4'
file 'carreira_7.mp4'
file 'carreira_8.mp4'
file 'fala_picasso.mp4'
file 'term_lightning_civitai.mp4'
file 'term_guerra.mp4'
file 'carreira_9.mp4'
file 'term_cranio_civitai.mp4'
file 'term_aperto.mp4'
file 'term_cadeira.mp4'
EOF

ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i "$CORTES/lista.txt" \
  -vf "fps=30,format=yuv420p,setsar=1" \
  -af "aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS" \
  -c:v libx264 -preset veryfast -crf 19 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 \
  -movflags +faststart "$CORTES/picture.mp4"

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$CORTES/picture.mp4")
FADE=$(python3 -c "print(max(0.1, round(float('$DUR')-1.4, 3)))")

ffmpeg -y -hide_banner -loglevel error \
  -i "$CORTES/picture.mp4" \
  -loop 1 -i "$CORTES/ov_hook.png" \
  -loop 1 -i "$CORTES/ov_stamps.png" \
  -i "$MUSIC" \
  -filter_complex "
    [1:v]format=rgba[h];
    [2:v]format=rgba[s];
    [0:v][h]overlay=0:0:enable='between(t,0,4)'[v1];
    [v1][s]overlay=0:0:enable='between(t,4,16)'[v2];
    [v2]fade=t=out:st=${FADE}:d=1.4,format=yuv420p[v];
    [0:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,volume=1.95[voice];
    [3:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS,atrim=0:${DUR},volume=0.17[bed];
    [bed][voice]sidechaincompress=threshold=0.05:ratio=8:attack=18:release=280:makeup=1.1[ducked];
    [ducked][voice]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[mix]
  " \
  -map "[v]" -map "[mix]" \
  -c:v libx264 -preset veryfast -crf 19 -pix_fmt yuv420p \
  -c:a aac -b:a 256k -ar 48000 \
  -t "$DUR" -movflags +faststart \
  "$FINAL/abertura-canal-90s.mp4"

echo READY
ls -lh "$FINAL/abertura-canal-90s.mp4"
