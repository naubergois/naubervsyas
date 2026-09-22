---
name: editar-episodio-voz
description: Monta, capa e publica episódio do Nauber vs Yas a partir do bruto ChatGPT Voz + webcam. Recorte 16:9, áudio original, vinheta, B-roll mudo, webcam, roda Jarvis só na fala da IA, thumbnail amarelo/aço e upload no Studio. Use when the user asks to editar o vídeo, montar episódio, colocar vinheta, B-roll, roda Jarvis, capa, thumbnail ou subir para o YouTube.
---

# Editar episódio — Nauber vs Yas

Papo gravado em ultrawide (ChatGPT Voz + webcam). Sai 16:9 com a voz que já está no arquivo. Não sobe sem o usuário pedir.

Cópia desta skill no repo: `canalnauber/.cursor/skills/editar-episodio-voz/`. Scripts que já rodaram: `producao/ep2-voz/montar.py` e `jarvis_ring.py` — copia e troca `ROOT` / `SRC` / `TIMELINE`. Detalhe de filtro e Studio: [receita.md](receita.md).

## Casa

| Item | Path |
|---|---|
| Repo | `/Users/naubergois/canalnauber` |
| Bruto | `/Users/naubergois/Compartilhado/Filmora/Meu Vídeo-N.mp4` |
| Vinheta | `producao/abertura/final/vinheta-5s.mp4` |
| Marca d’água | `arte/marca-dagua-150.png` |
| Capa-modelo | `arte/thumb-modelo-dois-lados.png` |
| Canal | `UCAuts0wWOYpi8ZaRrkfeqhQ` · `@naubervsyas` |
| Studio | Chrome CDP `127.0.0.1:9230` + `browser-harness` |

Pasta nova: `producao/epN-voz/{audio,broll/norm,preview,final}`.

Este Mac tem 16 GB. **Um encode por vez.** `h264_videotoolbox` no master. `libx264` só em clipe curto de B-roll. Antes do overlay Jarvis, apaga `*-tmp.mp4`, `*-sem-vinheta.mp4` e preview de segmento — o disco enche.

## Checklist

```
- [ ] 1. Probe do bruto + pasta
- [ ] 2. Transcrever (whisper-cli, CPU)
- [ ] 3. B-roll mudo por assunto (domínio público)
- [ ] 4. Preview 90s (crop + overlay + webcam + áudio)
- [ ] 5. Master + vinheta
- [ ] 6. Roda Jarvis só na fala da Yas (preview, depois full)
- [ ] 7. Capa 1280×720
- [ ] 8. Studio: título, descrição, capa, público — só se pediu subir
```

Não mistura Canal da Ciência. Não usa vinheta no lugar do papo. Não aplica o `AF` pesado do ep. 1 se o Filmora já misturou bem.

## 1. Probe

```bash
ffprobe -hide_banner -show_streams -show_format "BRUTO"
```

Esperado: 2560×1080, AAC. Anota duração. Corta preto inicial (~0,8 s) no encode, não no bruto.

## 2. Transcrição

```bash
ffmpeg -y -i BRUTO -ac 1 -ar 16000 audio/whisper.wav
whisper-cli -m ~/.cache/whisper/ggml-base.bin -l pt -ng -osrt -of audio/full audio/whisper.wav
```

`-ng` — Metal estoura RAM. Tempos do SRT são do **bruto**. Master = `t - TRIM + 5` (vinheta).

## 3. B-roll

Silencioso. Assunto da fala, não enfeite. Wikimedia / governo / CC. Sem Unitree oficial, sem anime, sem clipe com cara na entrevista quando o papo é luta.

Normaliza cada fonte:

```bash
ffmpeg -y -i SRC -an \
  -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25,setsar=1" \
  -c:v libx264 -preset veryfast -pix_fmt yuv420p broll/norm/NOME.mp4
```

Primeiros ~20 s: mesa crua (oi, recusa de pauta). Depois overlay `enable='gte(t,22)'`. Timeline em segundos do bruto. Créditos em `CREDITOS.txt`.

## 4–5. Montagem

Copia `montar.py`. Ajusta `SRC`, `DUR`, `TRIM`, `TIMELINE`.

- Crop 16:9 **pela direita** (guarda webcam): `crop=1920:1080:640:0`
- Webcam: `crop=372:248:2168:792,scale=400:266,pad=406:272:3:3:color=0xFFE14A` — confere o recorte; a barra do Windows já entrou uma vez
- Áudio do episódio. Loudnorm leve: `I=-16:TP=-1.5:LRA=11`, AAC 256k/48k. Sem de-esser se a mix já está boa
- Marca d’água canto inferior esquerdo
- Preview 90 s **antes** do master
- Vinheta: 25 fps, concat copy. Crédito Kevin MacLeod na descrição (Ready Aim Fire)

```bash
python3 montar.py preview
python3 montar.py full
```

## 6. Roda Jarvis

Acende só quando a **Yas** fala. Ciano `#3DFFF0`. Some na vinheta e no turno do Nauber.

Copia `jarvis_ring.py`. Trava a abertura no `who()` (oi / “tudo bem” / recusa de pauta) **antes** das listas de palavra. Janela Yas: funde gap < 1,8 s, descarta < 0,45 s, desloca `−TRIM+5`.

1. `python3 jarvis_ring.py preview`
2. Still: Yas on, Nauber off
3. Libera ~2 GB e `python3 jarvis_ring.py full` (`-c:a copy`)

Alpha: extrai o alpha do loop e **multiplica** pelo gate. Sem isso a roda vira um quadrado opaco.

## 7. Capa

1280×720 JPG < 2 MB. Charge, não foto. Amarelo `#FFE14A` na esquerda (Nauber, jaleco, óculos grosso). Aço `#0A0A0C` na direita (Yas, crânio cromado, olho `#E10600`). Raio ciano no meio. Texto ≤ 5 palavras, creme `#F7F1E3`, **não** repete o título. Barra preta **sólida** em cima — o gerador grava letra escondida. Referência: `arte/thumb-modelo-dois-lados.png`.

Título: briga + detalhe. ≤ 60 caracteres. Primeiras 150 da descrição = o problema, não “neste vídeo”. Tags 7–10. Não é conteúdo para crianças. Vinheta = crédito da trilha.

## 8. YouTube

Só se o usuário pediu subir. Receita do Studio em [receita.md](receita.md). Canal `UCAuts0wWOYpi8ZaRrkfeqhQ`. Grava `final/YOUTUBE.txt` com título, URL, capa. Atualiza `README.md` e `CRESCIMENTO.md`. Não commita o MP4.

## Não faz

- Trilha por cima da fala
- B-roll com som
- Encode paralelo no videotoolbox
- Telefone no `youtube.com/verify` sem o usuário
- Vinheta de 5 s no TikTok/Short no lugar do papo
- Handle `@nauberbg` / `@naubergois`
