# LOOM — Video Script v2
### Streamlit-led · 5:15 target · covers all four required sections

---

## Where to start, and why

**Open in the Streamlit app, not the PDF.**

Most candidates will open on a title slide. Opening on a running system is differentiated
immediately, and it puts your proof at second zero instead of minute three. Tab 1 was built to
carry the hook.

You switch media exactly twice:

| Segment | Screen | Required section it satisfies |
|---|---|---|
| 0:00 – 0:50 | **Streamlit** Tab 1 | The Problem & Opportunity |
| 0:50 – 1:35 | **Deck** slide 5 | System Architecture & Workflow |
| 1:35 – 4:05 | **Streamlit** Tabs 2 → 5 | Proof of Concept / Prototype |
| 4:05 – 4:50 | **Deck** slide 8 | Implementation Plan |
| 4:50 – 5:15 | **Deck** slide 9 | Close |

**Say the section names out loud** as you hit them — "so that's the architecture and the
human-in-the-loop checkpoints" — so the reviewer can tick the brief's four boxes without
hunting. It costs two seconds and makes you easy to score.

### Setup before recording
- 1920×1080, single monitor, Do Not Disturb on
- Browser at **100% zoom**, no bookmarks bar, no extra tabs
- Streamlit already running and loaded on Tab 1 — never record the startup
- Deck open behind in presentation mode at slide 5
- Click through all five tabs once as a dry run so nothing loads slowly on camera

---

# THE SCRIPT

---

## 0:00 – 0:50 · The Problem & Opportunity
**Screen: Streamlit, Tab 1 — The Problem**

> "Think9 is building toward thirty-plus consumer brands. Right now, four of those brands buy the
> same fifty-millilitre amber glass bottle — from different vendors, at different prices. Nobody
> knows, because in the quotes it has five different names.
>
> *[scroll slowly down the five cards]*
>
> A PDF calls it '50ml Amber Glass Bottle, 20mm neck.' Another vendor calls it 'Amber Boston
> Round, 50 ML, 20/400.' Panchamrit gets a WhatsApp message with just a SKU code. There's an email
> saying '50cc, neck 20mm, without cap.' And one quote arrives in Hindi.
>
> Nobody wrote these to be inconsistent — they came from four vendors across three channels.
>
> And here's the thing: **you cannot combine orders for things you cannot prove are the same
> thing.** So the bottleneck isn't price comparison. It's identity. Think9 has thirty times the
> buying power of any single brand and one times the negotiating leverage, entirely because of
> this.
>
> *[scroll to the MOQ block]*
>
> The cost is specific. Packaging suppliers price against minimum order quantities — industry
> reporting for 2026 says suppliers will take five hundred units if you pay twenty to thirty
> percent more per unit. Four brands ordering separately pay that surcharge four times. One
> consolidated order pays it zero times.
>
> So the saving isn't 'we negotiated harder.' It's 'we stopped paying a surcharge that existed
> only because we ordered separately.' That's arithmetic, not skill — which is why it's
> defensible."

**Delivery:** Slowest segment in the video. Pause after "five different names."

---

## 0:50 – 1:35 · System Architecture & Workflow
**Screen: Deck, slide 5 — Architecture**

> "That's the architecture. Six layers.
>
> Quotes arrive wherever vendors actually send them — email, WhatsApp, file drops, ERP exports.
> Extraction pulls structured line items with a confidence score per field, and never invents a
> value that isn't in the source. Resolution maps each line item to a canonical SKU. That feeds a
> spec graph, which is the compounding asset — every quote any brand receives makes every future
> negotiation across every other brand better informed. Five detectors run continuously over that
> graph, and when one fires, a human gets a negotiation brief.
>
> Three human-in-the-loop checkpoints. Gate one, creating a new canonical SKU — because a wrong
> merge silently corrupts everything downstream, and that's the highest-cost error in the system.
> Gate two, any spend recommendation. Gate three, anything that goes to a vendor.
>
> The agent never commits spend and never contacts a supplier. Below those gates, confidence
> routing: above nine-tenths it advances, in the middle a human reviews, below point-six it's
> rejected outright. Human effort scales with ambiguity, not with volume."

**Delivery:** Brisk — forty-five seconds. Lingering here is what kills demo videos.

---

## 1:35 – 4:05 · Proof of Concept
**Screen: back to Streamlit**

### 1:35 – 1:50 · Run it live
**Sidebar — click ▶ Run pipeline**

> "This is a working prototype. Twelve vendor quotes, no API key. Let's run it."

*[click. let the timer land.]*

> "Under two seconds. Twenty-seven line items, twenty-three resolved, four held for a human,
> thirty-one thousand six hundred rupees identified."

---

### 1:50 – 2:15 · Tab 2 — Ingest

> "This is what it eats. Three PDFs, three CSVs with mutually contradictory column schemas, two
> emails with prices written in prose, three WhatsApp transcripts including Hinglish and
> Devanagari, one Excel with merged cells.
>
> *[select a WhatsApp file]*
>
> Raw source on the left, what was extracted on the right, with confidence per field. Where a
> field wasn't stated it shows a dash — it does not guess. That matters more than it sounds:
> a fabricated attribute would poison the graph permanently."

---

### 2:15 – 3:05 · Tab 3 — Resolution ← **the centrepiece**

> "Here's the resolution. Those same five strings, four different source formats — all resolving
> to one canonical SKU. Four brands, two thousand five hundred and fifty units of requirement.
>
> *[scroll to the discrimination check]*
>
> But this is the part I actually want to show you.
>
> There's a forty-eight millilitre bottle in this data. Watch what happens when it's evaluated
> against the fifty-millilitre canonical.
>
> Description similarity: eighty-five percent — which is *exactly* the fuzzy-match threshold.
> Material agrees. Colour agrees. Form agrees. Neck agrees. A purely text-based matcher merges
> these two.
>
> LOOM refuses. Volume forty-eight does not equal fifty, both explicitly stated, and below a
> hundred millilitres there's no tolerance band.
>
> A shared description is evidence for a match. A disagreeing attribute is proof against one.
> Proof beats evidence.
>
> Had it merged, it would have put a thousand phantom units into the bundle I'm about to show you."

**Delivery:** Slow right down. Two seconds of silence after "proof beats evidence."

---

### 3:05 – 3:30 · Tab 4 — Gate 1 Queue

> "Four items where the agent stopped and asked.
>
> One WhatsApp message with no specifications at all — rejected at extraction, confidence
> point-four. Two products it has genuinely never seen, proposed as new canonical SKUs. And one
> that's honestly ambiguous — 'bottle, fifty, amber' matches three different canonicals equally
> well, so it refuses to choose.
>
> Approve, reject, defer — a human decides. Twenty-three of twenty-seven resolved, eighty-five
> percent. That's the measured number. The normalizer was written before this data existed and
> hasn't been tuned against it, so the misses are real."

**Delivery:** This is your credibility segment. Say the 85% without apology.

---

### 3:30 – 4:05 · Tab 5 — Opportunities

> "Ranked by rupee impact.
>
> *[expand the top one]*
>
> Four brands, each ordering below MOQ, each paying the sub-MOQ premium. Neude eight hundred,
> Beauty by Bie six hundred, Panchamrit four-fifty, Goodbug seven hundred. Consolidated: two
> thousand five hundred and fifty against a minimum of two thousand five hundred. It clears.
>
> The arithmetic is all here — penalty tier, derived base price, resulting saving. Thirteen
> thousand two hundred and fifty-five rupees on one bottle. Thirty-one thousand six hundred across
> the portfolio, from twelve quotes.
>
> *[scroll to the brief]*
>
> And this is the output that matters — the packet a category manager takes into the call.
> Consolidated volume, portfolio-best price, the vendor's own historical floor, alternate vendors
> as BATNA, a target price with the reasoning shown.
>
> Then it stops. Awaiting human approval, gate two. It does not commit spend, and it has not
> contacted this vendor."

---

## 4:05 – 4:50 · Implementation Plan
**Screen: Deck, slide 8**

> "Thirty days to a minimum viable version.
>
> Week one, ingest and extraction live for packaging — highest cross-brand overlap, no regulatory
> sign-off slowing the loop. Week two, resolution and the graph, backfilled from GST e-invoice
> records, using GSTIN as the vendor key — that data is legally mandated and already structured,
> which solves cold start.
>
> Week three is the milestone that matters: one real consolidated negotiation, with a banked rupee
> saving. Not a dashboard. Week four, the human-gate console and instrumentation.
>
> The stack is deliberately boring. Temporal rather than LangGraph, because negotiations span days
> and have to survive restarts. Postgres rather than a graph database, because at twenty-four
> thousand line items a year the graph is small. Around five hundred dollars a year in inference
> against a savings target in crores. No Kafka, no Spark, no vector database — refusing
> infrastructure the scale doesn't justify is itself a design decision."

---

## 4:50 – 5:15 · Close
**Screen: Deck, slide 9 — What would make me wrong**

> "Where I could be wrong.
>
> If contract manufacturers buy the packaging, there's less to bundle directly — so every
> brand-SKU edge carries a procurement mode, and CM-embedded spend gets rate-benchmarked instead
> of consolidated. If vendors learn we bundle, they'll inflate base quotes — so portfolio volume
> isn't disclosed until commit. And a wrong canonical merge is the highest-cost failure in the
> system, which is exactly why that's the one gate I won't automate.
>
> Everything you've seen runs on a fresh clone with no API key in under two seconds. Repo and deck
> are in the submission. Thank you."

---

# Delivery notes

**Audio beats video.** A clear voice over a plain screen beats a polished screen with echo.

**Don't read this.** Learn the shape and talk. Reading is audible and costs more credibility than
a stumble does.

**Pause instead of "um."** Silence sounds like thinking.

**Three or four takes is normal.** Record the Tab 3 segment separately if it helps — it's the one
worth getting right.

**Camera bubble small, bottom-right.** Turn it off during Tab 3 and Tab 5 if it covers numbers.

---

# Pre-upload checklist

- [ ] Under 5:30
- [ ] Streamlit text readable at 50% zoom
- [ ] The pipeline runs live on camera — not a pre-loaded screen
- [ ] The 48ml refusal is explained, not skipped
- [ ] All four brief sections named out loud
- [ ] "It does not commit spend" said out loud
- [ ] 85% stated without apology
- [ ] No notifications, no stray browser tabs
- [ ] Loom sharing set to **anyone with the link** — verify in an incognito window
