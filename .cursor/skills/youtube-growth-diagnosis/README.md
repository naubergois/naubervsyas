# youtube-growth-skills

> Agent skill that diagnoses YouTube channel growth from your real Studio analytics — it finds the funnel leak, not generic advice.

An [agent skill](https://skills.sh) for working out why a YouTube channel or video under- or over-performs. Instead of guessing, it guides you through pulling your real numbers from YouTube Studio's **Ask Studio**, then analyzes them: it separates format from topic from distribution, flags single-data-point flukes, and returns a prioritized list of fixes that act on the traffic you already have.

Built on one premise: most channels don't have a *reach* problem, they have a *funnel* problem.

## Install (coding agents)

```bash
npx skills add shashu10/youtube-growth-skills
```

Installs to your coding agent (Claude Code, Cursor, Codex, and others). The agent loads it automatically when you ask about growing a channel.

## Use it in a chat model (no install needed)

Ask Studio can't install skills — and neither can the Gemini app, ChatGPT, or Google AI Studio. For those, paste the contents of [`SKILL.md`](SKILL.md) in as instructions:

- **Google AI Studio / ChatGPT custom instructions:** paste it into the *System instructions* field (cleaner — it persists for the whole session).
- **Plain chat:** paste it as your first message.

Then say something like *"help me grow my channel."*

## How it works

1. **Trigger it** — ask about growing your channel, or paste Studio numbers from https://studio.youtube.com/?d=as.
2. **Pull the data** — the skill hands you copy-paste prompts for Ask Studio (inside YouTube Studio) that extract the right cuts (traffic sources, retention curves, CTR, new-vs-returning) and compile them into one block.
3. **Get the diagnosis** — paste that block back, and it names the single biggest funnel leak and gives you a prioritized fix list, every claim tied to a number.

## License

MIT — see [LICENSE](LICENSE).
