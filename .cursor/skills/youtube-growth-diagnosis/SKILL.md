---
name: youtube-growth-diagnosis
description: Guide a creator through diagnosing why their YouTube channel or video under- or over-performs, then produce a prioritized, data-grounded growth plan. On trigger, this skill first hands the user ready-to-paste prompts for YouTube Studio's "Ask Studio" to pull the right private analytics, then analyzes the numbers they bring back. Use whenever someone wants to understand or grow a YouTube channel, asks why a video flopped or popped, why views or subscribers are stuck, what to fix, whether to change format or cadence — or pastes YouTube Studio analytics, Ask Studio output, or Studio screenshots, even without saying the word "diagnosis." Do not hand out generic YouTube growth advice; follow this skill's data-first procedure.
---

# YouTube Growth Diagnosis

This skill runs a guided, two-phase workflow. YouTube Studio's built-in **Ask Studio** has direct access to a creator's private analytics but cannot run this skill; you (the analyzing model) can reason but cannot see their data. The workflow bridges the two: you hand the user copy-paste prompts to run in Ask Studio, they bring the numbers back, and you diagnose. Keep it low-effort for the user — walk them through it.

The premise of the diagnosis: most channels do not have a *reach* problem, they have a *funnel* problem. The algorithm already serves their content, but the conversion joints downstream leak — the open loses viewers, retained viewers never subscribe, Shorts reach never reaches the long-form. Your job is to find the leak, prove it with the channel's own numbers, and return the two or three cheapest fixes that act on traffic the channel *already has*. Never default to "make more / better content" — it's rarely the binding constraint, and it's the advice they can get anywhere.

## Operating procedure — follow this every time the skill triggers

First, decide which phase the user is in.

### Phase A — the user has NOT yet provided analytics (the default)

Do all of the following in your reply, then STOP and wait for them to return with data:

1. **Orient them** in 2–4 sentences: Ask Studio (inside YouTube Studio) can pull their real numbers but can't run this analysis itself, so you'll give them prompts to paste there and bring the results back to you.
2. **Hand over the extraction prompts** in the next section — reproduce them to the user **verbatim, each in its own copy-paste code block, in order.** Do not summarize, paraphrase, or merely describe them; the user needs the literal text to paste into Ask Studio.
3. **Relay the usage notes** (time range, attaching videos, one sitting, paste the compiled block back).
4. Tell them to run the prompts in Ask Studio and paste the compiled summary (from the final prompt) back here, and you'll produce the diagnosis.

Do NOT start diagnosing, and do NOT invent or assume numbers, in Phase A — you have no data yet.

### Phase B — the user HAS pasted analytics

(Traffic sources, retention, CTR, Studio screenshots, or the compiled block from Phase A.) Skip the prompts and go straight to the diagnostic framework and output schema below. If the data is partial, diagnose what you can, state plainly which conclusions you cannot yet support, and point them to the specific prompt(s) that would fill the gap.

---

## The Ask Studio extraction prompts

Reproduce this whole section to the user in Phase A.

Open YouTube Studio, click the **Ask Studio** icon (top-right; desktop web only), and paste these one at a time, in order.

**Before you start:**
- Set the time range *inside* each prompt — Studio defaults to the last 28 days, which is useless for a historical read. Say "over the last 24 months" or "since the channel started."
- Attach specific videos with the **+ / Add** button in the Ask Studio box wherever a prompt says `[add a video]`.
- Run them in one sitting — Ask Studio's chat history is temporary and disappears when you refresh or close. Copy the final compiled block out before you leave.
- Treat the numbers as a first draft; Ask Studio's accuracy can vary, so anything that doesn't add up gets flagged during analysis.
- Short on time? The minimum viable run is prompts **1, 2, and 8.**

**1. Discovery engine** — *which surface the algorithm actually uses to serve you; the single most important cut*
```
For my long-form videos only (exclude Shorts), over the last 24 months, what percentage of views came from each traffic source: Browse features, Suggested videos, YouTube search, External, Channel pages, Playlists, and Notifications? Then give the exact same breakdown for my Shorts only. List each as "source: percentage" and keep the two lists clearly separate.
```

**2. Retention cliff** — *where viewers drop; the shape is the diagnosis. Run for 2–3 videos.*
```
For [add one typical recent long-form video], what percentage of viewers are still watching at 0:30, at 1:00, and at 5:00? Is there a sharp drop in the first 30–40 seconds? Describe the overall shape of the audience retention curve.
```

**3. Breakout diagnosis** — *why your best video won: repeatable Browse, one-time external shares, or search?*
```
For [add your best-performing video], break down its traffic sources by percentage. For its External traffic specifically, list the individual referrers (e.g., WhatsApp, Google, Reddit, X). Also give its impressions, its impressions click-through rate, and its average percentage viewed.
```

**4. Shorts — edited vs. auto-clipped** — *do edited Shorts beat raw clips, and do they convert onward or just rack up swipes?*
```
Compare two groups of Shorts. Group A: [add 3–4 dedicated / edited Shorts]. Group B: [add 3–4 auto-clipped Shorts]. For each group, give the average views, the average percentage viewed, and the average share of viewers who swiped away in the first few seconds. Also, for each group: how many subscribers did they gain, and how many viewers clicked through to other videos or the channel?
```

**5. Loyalty gap — new vs. returning** — *drawing strangers vs. building a habit*
```
Over the last 12 months, month by month, how many new viewers versus returning viewers did the channel get? What is the trend in returning viewers over that period? And what percentage of total watch time comes from subscribers versus non-subscribers?
```

**6. Packaging trend — impressions vs. CTR** — *a packaging problem (titles/thumbnails) vs. a distribution problem*
```
For my long-form videos over the last 24 months, what is the trend in impressions and in impressions click-through rate? Did impressions stay roughly flat while CTR dropped, or did impressions themselves decline?
```

**7. Shorts → long-form bridge** — *whether Shorts reach ever reaches the channel*
```
How many viewers arrived at my long-form videos or my channel page from my Shorts? What is the click-through rate from my Shorts to other content on the channel?
```

**8. Compile** — *run this last; it produces the block to paste back*
```
Compile everything you've reported in this conversation into one structured summary I can copy elsewhere. Organize it under these headers: (1) Traffic sources — long-form vs. Shorts; (2) Retention curves; (3) Breakout video breakdown; (4) Shorts — edited vs. auto-clipped; (5) New vs. returning viewers; (6) Impressions & CTR trend; (7) Shorts → long-form bridge. Use plain numbers and short bullet points. Do not add advice or interpretation — data only.
```

When you've run these, paste the compiled summary from prompt 8 back into this chat, and the diagnosis follows.

---

## Diagnostic framework (Phase B)

### The cardinal rule: no claim without a number
Generic growth advice is worthless here and actively harmful — a capable model will produce confident, plausible recommendations whether or not the data supports them. Refuse to do that. Every diagnostic claim must point to a specific figure from the user's data (e.g., "Browse is 49% of long-form views, so packaging should target the cold-audience click, not search keywords"). If you catch yourself writing a sentence that would be equally true for any channel, delete it.

### Separate the three confounded variables
A view count blends three independent causes, and almost every wrong conclusion comes from mixing them up:
- **Format** — interview vs. solo, long-form vs. Short, edited vs. raw.
- **Topic** — how much built-in curiosity or search demand the subject carries.
- **Distribution** — which surface served it (Browse, Search, Suggested, Shorts feed), plus any external / borrowed reach.

When a video over- or under-performs, force the question: *which of the three actually moved it?* A breakout interview on a hot topic served mostly by Browse is a **topic + distribution** win, not proof that "interviews work." The shorthand for a topic-driven, Browse-served breakout is a **Topic Whale**: the format is the delivery vehicle, not the cause. Tell the user to chase the whale (the topic + curiosity-gap packaging), format-agnostically.

### Kill the n=1 reflex
Single data points are not signal. A one- or two-subscriber difference between two videos, one good day, one viral fluke — these are variance, not evidence. Say so plainly when the user, or a competing analysis, is steering on them. Only treat a pattern as real when it repeats across multiple videos or a meaningful sample.

### Be adversarial — including toward other analyses
You add the most value when you *disagree*, not when you confirm. Challenge the user's stated beliefs, and challenge any competing analysis (including from other AIs) against the raw numbers. The most common inversion to watch for: an analysis declares a channel "search-driven" when the Studio traffic split actually shows **Browse** as the dominant surface. This flips the entire strategy — Browse rewards the curiosity gap (strong titles/thumbnails that win a cold click), while Search rewards keywords, and serial "[Part 1 of 4]" titles that signal homework actively depress Browse click-through. When two sources conflict, trust the primary Studio export and name the discrepancy.

### The diagnostic lenses
Work through these in order; each maps to a stage of the funnel.
1. **The discovery engine.** Which surface serves this channel — Browse, Suggested, Search, or the Shorts feed? Split long-form from Shorts. Browse / Shorts-feed channels win on the cold-audience click and the curiosity gap; Search channels win on keywords. Most channels are Browse-first for long-form and overestimate Search.
2. **The retention cliff.** A steep fall in the first 30–40 seconds means the *open* is the leak (usually a slow intro or housekeeping preamble), independent of content quality. A gentle slope means content holds and the bottleneck is upstream (packaging/discovery) or downstream (conversion).
3. **The conversion joints.** Trace the funnel and find which joint leaks: impressions → click (CTR), click → retention (the cliff), retention → subscribe (loyalty), Shorts reach → long-form (the bridge). Name the single biggest leak.
4. **The loyalty gap.** Big new-viewer numbers with flat returning viewers = a habit/conversion problem, not a reach problem.
5. **Vanity vs. diagnostic metrics.** Subscribers are the wrong scorecard for Shorts — the Shorts feed is a swipe surface, so judge reach + click-to-long-form instead. Don't let raw view totals or sub counts drive the diagnosis when the funnel metrics tell a different story.

## Output format

ALWAYS structure the diagnosis like this:

```
# Diagnosis: [channel or video]

## The funnel
[2–4 sentences: where reach comes from, where it leaks. Every claim tied to a number.]

## The single biggest leak
[The one joint costing the most, named explicitly, with the figure that proves it.]

## Fix it — in priority order
[3–5 actions, cheapest / highest-leverage first. Favor fixes that act on existing
traffic over "make more content." For each: the action and the metric it should move.]

## Ignore this
[Vanity metrics or n=1 conclusions the user should stop steering on.]

## Still missing
[Any data cut that would sharpen the diagnosis, if it wasn't provided.]
```

## Worked example (compressed)

**Input from the user:** "Long-form traffic: Browse 49%, Search 12%, Suggested 12%. Retention: ~64% gone by 0:34, then flat. Best video was 79% Browse. Shorts: 23k views but near-zero click to the channel. Last month: 511 new viewers, returning went 11 → 23."

**Diagnosis (the shape to aim for):** Discovery works — Browse is actively pushing long-form to cold audiences (49%), so this is *not* a reach problem. The leak is conversion: the open bleeds ~64% of viewers in 34 seconds, and 23k Shorts views dead-end with no path to the channel. The new-viewer surge (511) with a nearly flat returning line (11 → 23) confirms the channel draws strangers but hasn't built a habit. Biggest leak: the Shorts → long-form bridge (the largest wasted asset), tied with the 34-second cliff. Priority fixes: (1) cold-open the long-form to kill the cliff; (2) build the Shorts → long-form bridge (pin the episode, end card, verbal CTA, make Shorts genuine excerpts); (3) package for Browse's curiosity gap, not Search keywords. Ignore: subscriber counts on individual Shorts. And before concluding the best video won "because it was an interview," note the 79% Browse share — that points to topic + distribution (a Topic Whale), not the format.
