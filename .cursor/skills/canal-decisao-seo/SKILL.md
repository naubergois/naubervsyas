---
name: canal-decisao-seo
description: >-
  Runs the Nauber vs Yas channel loop for agents: pick channels, rank angles, pack
  search/SEO/GEO, fan out posts, then decide the next move from native numbers. Use
  when the user asks for SEO, divulgacao, tomada de decisao de canal, crescimento,
  calendario, republicacao, perfil, hashtag, GEO, or "implementar o loop". Not for
  editing video (use editar-episodio-voz) or inventing a new episode to fill a calendar.
---

# Canal: decisão, SEO, divulgação

O YouTube é a casa. TikTok, Reels e Shorts são porta. O agente não espalha handle: escolhe, empacota, sai e mede.

Artefatos canônicos: `producao/canal-loop/`. Skill de marca e crescimento já existem; esta skill **orquestra** e **grava** o resultado ali. Não republica o plano em `CRESCIMENTO.md` a cada turno — atualiza o loop e aponta.

## Antes de qualquer ferramenta

1. Ler `producao/canal-loop/README.md` e o estágio pedido.
2. Se o arquivo do estágio existir e estiver fresco (menos de um trimestre, sem pivô), carregar e seguir. Só reescreve se o usuário pediu revisão ou o número mudou.
3. Não inventar volume de keyword, share of voice nem métrica de dashboard. Número só se veio do Studio, do app nativo ou de um arquivo deste repo.
4. Não publicar sozinho. Fila pronta em `fila.md`; sobe só com "publica" / "sobe" explícito. WoopSocial e Publora: confirmar conta ligada; se não estiver, entregar copy-paste.
5. Canal da Ciência não mistura. Handle `@naubervsyas`. Sem vinheta no lugar do papo.

## Loop (nessa ordem)

| Estágio | Job | Arquivo | Skill-fonte |
|---|---|---|---|
| 0 | Quem somos | `brand-profile.md` `audience.md` | brand-profile, audience-research |
| 1 | Onde e o que não fazer | `social-strategy.md` `content-pillars.md` `goals-and-kpis.md` | social-strategy, content-pillars, goals-and-kpis |
| 2 | Qual recorte | `angulos.md` | content-angle-ranker, youtube-growth-diagnosis |
| 3 | Busca | `social-seo.md` `youtube-seo.md` `instagram-seo.md` `tiktok-seo.md` `geo.md` `hashtags.md` | social-seo, youtube-seo-system, instagram-seo, ai-search-optimization, hashtag-strategy |
| 4 | Sai | `calendario.md` `republicacao.md` `perfis.md` `fila.md` | cross-platform-repurposing, batch-content-plan, profile-optimization, scheduling-and-queue, yt-repurposer |
| 5 | Decide de novo | `analytics.md` `experimentos.md` | analytics-and-reporting, experimentation-and-ab-testing, youtube-growth-diagnosis |

Pedido parcial: entra no estágio certo. Pedido "implementar tudo" / "roda o loop": percorre 0→5 e atualiza o que estiver velho.

## Regras do canal (não negociar)

- Um papo quando o tema pedir. Não grava episódio para encher calendário.
- De cada episódio saem no máximo quatro portas: um corte 9:16, um frame de frase, um post com link (Facebook quando existir), um comentário fixo.
- Três ângulos por episódio, não doze.
- Short abre no meio da briga. Primeira linha da legenda é a frase indexada. Cartão ou primeiro comentário aponta o long.
- Pedir inscrição no final do long, no cartão e na descrição. Nunca no gancho do TikTok.
- Uma pergunta por peça. Ação que o algoritmo lê: enviar ou salvar.
- Capa 1280×720 charge, texto ≤ 5 palavras, não repete o título. Regra: `.cursor/rules/capas-criativas.mdc`.
- Anúncio pago só quando um corte já segura sozinho.

## Qualidade

- Prosa humana: `.cursor/skills/texto-humano` (se não estiver no repo, `~/.cursor/skills/texto-humano`).
- Cada artefato: entra, explica, pousa. Sem "neste documento" / "vamos explorar".
- Self-check do estágio: [references/qualidade.md](references/qualidade.md).
- Rotas para skills irmãs: [references/rotas.md](references/rotas.md).

## Depois de escrever

Rodar `python3 producao/canal-loop/validar.py` na raiz do repo. Se falhar, completar o arquivo que faltou. Não inventar arquivo vazio.

## Exemplo

Usuário: "qual canal entra essa semana e como sobe o corte da ciência"

1. Carrega `social-strategy.md` (YouTube casa; IG ainda no celular).
2. Lê `angulos.md` — ciência já tem porta YT/TikTok; Instagram é a lacuna.
3. Usa `instagram-seo.md` + `fila.md` bloco ciência.
4. Não agenda sozinho. Entrega a legenda e pede o celular.
