---
name: footage-real-assunto
description: >-
  Obriga B-roll e imagens a serem footage real do assunto falado (evento, pessoa,
  produto, luta, demo), nao stock generico. Mapeia SRT/roteiro -> entidade ->
  video veridico -> janela TIMELINE -> verifica frame. Use when montar episodio,
  B-roll, overlay, TIMELINE, montar.py, editar video, footage, clipe do evento,
  REK, Unitree, luta, demo oficial, ou quando o usuario pedir video veridico /
  footage real do que esta sendo falado. Not for gerar imagem IA (use flux /
  nano-banana); not for so publicar no Studio (use editar-episodio-voz).
---

# Footage real do assunto

Se a fala nomeia um fato, evento, pessoa, produto ou clipe viral, a imagem tem que ser **desse** fato. Stock generico (boxe de academia, museu, robô de entrega "parecido") e erro — mesmo que o tema seja "luta" ou "robô".

Aplica em montagem long/short, TIMELINE, overlay, preview e republicação. Complementa `editar-episodio-voz` (passo B-roll).

## Regra dura

1. **Nome na fala → footage daquilo.** Frankie × T800 / REK → cage REK. Unitree G1 → demo Unitree. Foto do Moraes → aquela foto. Nao "algo no espirito".
2. **Dois assuntos no papo = duas fontes.** Nao reaproveitar o clipe A no trecho B.
3. **Sem footage veridico → nao inventa com stock enganoso.** Deixa mesa/webcam, still factual, ou para e busca o clipe. Nunca substitui por analogia visual (academia no lugar de cage; Starship no lugar de G1).
4. **Mute o original.** B-roll sem audio. Credito editorial / fair use / CC em `CREDITOS.txt`.
5. **Prova por frame.** Antes de publicar, extrai JPEG nos segundos da fala e confirma marca, arena, pessoa ou produto no quadro.

## Fluxo (obrigatorio)

```
- [ ] 1. Ler SRT/roteiro: listar entidades nomeadas + janelas de tempo (bruto)
- [ ] 2. Para cada entidade: achar fonte veridica (disco -> yt-dlp -> oficial)
- [ ] 3. Normalizar 1920x1080 25fps mute em broll/norm/
- [ ] 4. Atualizar TIMELINE / overlay com as janelas certas (offset vinheta/capa)
- [ ] 5. Remontar ou patch overlay
- [ ] 6. Verificar frames nos timestamps da fala
- [ ] 7. CREDITOS.txt + so entao republicar
```

### 1. Mapa fala → imagem

Do `audio/full.srt` (tempos do **bruto**):

| Tipo | Exemplo | Footage aceito | Footage proibido |
|------|---------|----------------|------------------|
| Evento + luta | REK SF, Frankie × EngineAI T800 | Clip do cage / reenvio noticioso do fight | Boxe USAF, spar de academia |
| Demo de marca | Unitree G1 UnifoLM | Video oficial / reenvio da demo | Delivery robot, humanoide generico |
| Pessoa / foto | Moraes, aviao | Still ou video daquele fato | "Imprensa generica" |
| Conceito abstrato | Transformer, consciencia | OK stock/didatico | — |

Silencio / Yas "olhando" pode ficar mesa ou humanoide neutro. No instante em que o nome sai, troca para o veridico.

### 2. Onde buscar

Ordem:

1. `broll/raw/` e `broll/norm/` do episodio
2. `yt-dlp` do evento / canal oficial (ex.: Unitree, reenvio noticioso do fight)
3. Wikimedia / governo / CC so para conceito ou still documental

Normalizar:

```bash
ffmpeg -y -i SRC -an \
  -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=25,setsar=1" \
  -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p \
  broll/norm/NOME.mp4
```

Inspecionar candidatos a cada ~10 s; cortar so o trecho continuo que mostra o sujeito certo (nao intro de outros robos no mesmo arquivo).

### 3. TIMELINE e offsets

`montar.py` usa segundos do **bruto**.

| Master | Offset tipico |
|--------|----------------|
| Com vinheta 5 s | youtube_t = bruto + 5 |
| Abertura capa (0–15 thumb, 15–20 bridge, 20+ = youtube@27) | abertura ≈ bruto − 2 |

Script de patch de overlay (ex.: `rebuild_rek_overlay.py`): janelas no tempo do arquivo de saida, nao do SRT cru.

Ao mudar TIMELINE, atualizar `broll/timeline.json` e a doc `final/YOUTUBE.txt` / `UPLOAD-*.md`.

### 4. Verificacao

```bash
for t in T1 T2 T3; do
  ffmpeg -y -ss $t -i MASTER -frames:v 1 /tmp/verify-$t.jpg
done
```

Ler os JPEGs. Se nao aparecer marca/arena/pessoa do assunto, **nao publica** — corrige TIMELINE ou a fonte.

## Anti-padroes (ja quebraram ep. 2)

- Colocar boxing-spar porque "e luta"
- Deixar humanoide de museu enquanto a fala diz Frankie / REK / T800
- Deixar delivery-robot enquanto a fala diz Unitree G1
- Uma unica janela curta de REK e o miolo da explicacao de volta no stock
- Publicar e so depois conferir frames

## Cruzamento

- Montagem completa / Studio: `editar-episodio-voz`
- Gerar capa ilustrada (nao footage do evento): skills de imagem do canal
- Este skill **vence** qualquer preferencia generica de "so Wikimedia" quando a fala nomeia um evento ou produto concreto
