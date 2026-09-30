# Diagnóstico parcial — Nauber vs Yas (@naubervsyas)

Dados do Studio já conhecidos (painel 22/set/2026, últimos 28 dias), alinhados a [CRESCIMENTO.md](../../CRESCIMENTO.md). Ask Studio ainda não rodou — use os prompts abaixo para fechar o funil com números privados.

## O funil (o que os números públicos já mostram)

Tráfego quase inexistente: **35 views** no canal, **1 inscrito**, **0,6 h** de exibição. Não dá para falar em “alcance” ainda; dá para falar em **embalagem vs. abertura**.

O episódio 2 prova que a **capa vende**: **16% CTR** num canal minúsculo é sinal de que título/thumbnail batem com a curiosidade. Quem clicou, porém, ficou **1 min 42 s** num vídeo de **~25 min** — o vazamento está no **começo do long**, não no tema.

O Short da luta (**12 views** no rótulo/camisa; o corte novo **~162 views** no scan) existe, mas ainda não puxa massa para o long. Ep. 1 (**19 views**) quase não teve porta depois do Short (**12 views**). Padrão: **porta fraca + cold open errado**, não falta de assunto.

## O maior vazamento

**Ponte Shorts → long-form + cold open (vinheta).** Quem veio por “homem vs robô / luta” encontrou vinheta, mesa branca e “não vou falar de eleição” antes do payoff. Isso explica CTR alto com retenção baixa. Shorts que não terminam em loop aberto + cartão claro para o episódio deixam view morta no feed.

Correção já em curso no plano: cortes **sem vinheta**, gancho **“tinha piloto”** (erro de previsão), cartão/descrição apontando o long.

## Prioridade (antes de gravar ep. 3)

1. **Subir os 3 cortes do ep. 2** (luta, consciência, fecho) — mesmo 9:16, legenda nativa, TikTok pendente.
2. **Reabrir o long nos primeiros 15 s** com a imagem da capa; vinheta depois ou fora.
3. **Medir retenção do short** — se cair antes de 3 s, recorta o mesmo papo, não muda de tema.
4. **Comentário fixo + resposta** nos dois longs — canal novo precisa de conversa, não de “curte segue”.
5. **Rodar Ask Studio** (prompts abaixo) para quantificar tráfego Shorts vs long e clique Short → canal.

## Ignore por enquanto

- Contagem de inscrito como scorecard de Short (feed é swipe).
- Comparar ep. 1 vs ep. 2 com n=1 como “formato vencedor”.
- Ep. 3, anúncio pago, ou multiplicar redes antes de uma porta segurar retenção.

## Sinais externos (Attract Signal)

Scan em `producao/crescimento-attract/`: Cortes do Flow, Inteligência Ltda (Shorts do canal principal; 1 winner ≥5k likes, vários políticos abaixo do corte), e @naubervsyas (3 Shorts, amostra pequena). Relatório completo: `attract-signal-report.md` + `content-sprint.csv`.

---

## Ask Studio — cole no Studio (web), um por vez

Antes: ajuste o período **dentro** de cada prompt (ex.: “últimos 24 meses”). Anexe vídeos com **+ / Add** onde pedir `[add a video]`. Histórico some ao fechar — copie o bloco do prompt 8 antes de sair.

**1. Discovery engine**

```
For my long-form videos only (exclude Shorts), over the last 24 months, what percentage of views came from each traffic source: Browse features, Suggested videos, YouTube search, External, Channel pages, Playlists, and Notifications? Then give the exact same breakdown for my Shorts only. List each as "source: percentage" and keep the two lists clearly separate.
```

**2. Retention cliff**

```
For [add one typical recent long-form video], what percentage of viewers are still watching at 0:30, at 1:00, and at 5:00? Is there a sharp drop in the first 30–40 seconds? Describe the overall shape of the audience retention curve.
```

**7. Shorts → long-form bridge**

```
How many viewers arrived at my long-form videos or my channel page from my Shorts? What is the click-through rate from my Shorts to other content on the channel?
```

**8. Compile**

```
Compile everything you've reported in this conversation into one structured summary I can copy elsewhere. Organize it under these headers: (1) Traffic sources — long-form vs. Shorts; (2) Retention curves; (3) Breakout video breakdown; (4) Shorts — edited vs. auto-clipped; (5) New vs. returning viewers; (6) Impressions & CTR trend; (7) Shorts → long-form bridge. Use plain numbers and short bullet points. Do not add advice or interpretation — data only.
```

Cole o resultado do prompt 8 de volta no chat de diagnóstico para fechar prioridades com tráfego real.
