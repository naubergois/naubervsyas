# Receita — filtros e Studio

Lê isto quando for montar ou publicar. O fluxo está no [SKILL.md](SKILL.md).

## Crop e overlay (master)

Bruto 2560×1080. `TRIM` = preto inicial (ep. 2: `0.80`).

```
[0:v]crop=1920:1080:640:0,setsar=1[base];
[1:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1[br];
[base][br]overlay=0:0:eof_action=pass:enable='gte(t,22)'[mix];
[0:v]crop=372:248:2168:792,scale=400:266,pad=406:272:3:3:color=0xFFE14A[cam];
[mix][cam]overlay=W-w-22:H-h-22:enable='gte(t,22)'[v1];
[2:v]scale=84:84[w];
[v1][w]overlay=24:H-h-24,unsharp=5:5:0.28,format=yuv420p[vout]
```

Entradas: `[0]` bruto (depois do `-ss TRIM`), `[1]` B-roll 1920×1080 25 fps, `[2]` `marca-dagua-150.png`.

Webcam: se a barra do Windows entrar, sobe o `y` do crop (792) e baixa a altura (248). Confere num still.

Áudio do `[0]`. `-af loudnorm=I=-16:TP=-1.5:LRA=11`. `-c:v h264_videotoolbox -b:v 10M`. `-c:a aac -b:a 256k -ar 48000`.

Ep. 1 (robô estourado) usou `highpass + afftdn + deesser + speechnorm + loudnorm I=-14`. Só se o TTS clipear. Mix boa do Filmora: não esmaga.

## Vinheta

```bash
ffmpeg -y -i VINHETA-5s -r 25 -c:v h264_videotoolbox -b:v 10M \
  -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -video_track_timescale 12800 bump.mp4
# concat.txt: bump + master
ffmpeg -y -f concat -safe 0 -i concat.txt -c copy -movflags +faststart out.mp4
```

Trilha da vinheta: Ready Aim Fire, Kevin MacLeod. Cola o bloco CC na descrição.

## Jarvis

Loop PNG 4 s, 25 fps, 440×440, RGBA. Overlay:

```
[1:v]format=rgba,scale=440:440,split[jrgb][ja];
[ja]alphaextract[aa];
[2:v]scale=440:440,format=gray[g];
[aa][g]blend=all_mode=multiply:shortest=1[am];
[jrgb][am]alphamerge[jm];
[0:v][jm]overlay=(W-w)/2-120:(H-h)/2-70[vout]
```

`[2]` = rawvideo gray 4×4 25 fps (`yas-gate.gray`). Fade 0,18 s nas pontas. `-c:a copy`. Tempo do gate = tempo do **master** (já com vinheta).

`who()`: listas `YAS` / `NAUBER` em `jarvis_ring.py`. Abertura **antes** das listas, sem overlap (`< 5.8` Yas, `>= 5.8` Nauber). Frase longa (> 160) = Yas. Pergunta curta informal = Nauber.

Loop novo da Yas: `python3 jarvis_bot.py` → `preview/jarvis-bot-loop.mov` (RGBA, 4 s, ela “fala”). `jarvis_ring.py` usa esse arquivo se existir. Preview de movimento: `preview/jarvis-bot-fala.mp4`.

Preview do overlay no episódio: still em ~8 s (Yas on), ~14 s (Nauber off), ~32 s (Yas no B-roll).

Disco: overlay precisa ~2 GB livres além do master. Apaga `epN-jarvis-tmp.mp4` incompleto, `epN-sem-vinheta.mp4`, `preview/seg-*.mp4`, wavs do whisper, cópia velha em `Compartilhado/Filmora`.

## Capa (PIL)

Gerador de imagem + `arte/thumb-modelo-dois-lados.png` de referência. Depois:

```python
d.rectangle((0, 0, 1280, 136), fill=(10, 10, 12, 255))  # tapa letra do gerador
d.text((640, 68), "TEXTO", font=fnt(78), fill=(247, 241, 227), anchor="mm")
```

Fonte: `/System/Library/Fonts/Supplemental/Arial Rounded Bold.ttf`. JPG quality 90–92.

## Studio (browser-harness)

```bash
export BU_CDP_URL=http://127.0.0.1:9230
# Chrome já no 9230 (perfil não-Default). Não usa a janela Default do usuário.
```

1. `goto_url("https://studio.youtube.com/channel/UCAuts0wWOYpi8ZaRrkfeqhQ/videos/upload?d=ud")`
2. `upload_file('input[name=Filedata]', '…/epN-youtube.mp4')`
3. Título `#title-textarea`, descrição `#description-textarea`
4. `VIDEO_MADE_FOR_KIDS_NOT_MFK`
5. Capa: `ytcp-thumbnail-uploader #select-button` + `upload_file('… input#file-loader', thumb.jpg)`
6. `#next-button` × 3
7. `tp-yt-paper-radio-button[name=PUBLIC]`
8. `#done-button` (Publicar)
9. Se aparecer “Ainda estamos verificando”: clicar **Publicar mesmo assim** (shadow DOM)
10. Confere oembed `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=ID`

Canal novo já passou da trava de 15 min. Se voltar `youtube.com/verify`, para e avisa — não preenche telefone.

Link público: `https://youtu.be/ID`. Arquivo `final/YOUTUBE.txt` no padrão do ep. 1.

## Whisper se Metal morrer

`whisper-cli: GGML_ASSERT` / OOM → `-ng` e, se o sandbox matar, `required_permissions: ["all"]`.
