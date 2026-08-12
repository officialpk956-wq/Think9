# LOOM — Video Walkthrough Script & Shot List

**Target: 5:00. Hard ceiling 5:30.** Loom's free tier caps at 5 minutes, so plan for 4:45.

The single most important thing in this video is **the terminal running live**. Everything else is setup for it. Most candidates will submit slides; you are submitting proof. Do not let the slides eat the runtime.

---

## Part 1 — Setup before you hit record

### Screen
- **One monitor.** If you have two, disconnect the second — Loom records the wrong one about a third of the time.
- **Resolution 1920×1080.** Higher and your terminal text becomes unreadable when compressed.
- Close Slack, email, and anything that can pop a notification. Do Not Disturb on.
- Clean desktop background. No personal files visible in the folder path.

### Terminal
- **Font size 16–18pt minimum.** This is the most common mistake — what looks fine on your screen is illegible in a compressed recording.
- Window maximised, roughly 100 columns wide. The output is formatted to 99 chars, so it will not wrap.
- Dark background, light text. Higher contrast survives compression better.
- `cd` into the prototype directory **before** recording, and clear the screen. The first thing on camera should be an empty prompt.

### Windows to have open, in this order
1. Terminal (foreground, ready)
2. Deck open at slide 1, in presentation mode
3. Nothing else

### Do a dry run first
Run `python run_demo.py` once before recording so it's warm and you know exactly where each section lands when you scroll. **Do not skip this.** Hunting for the right output section on camera is what makes a demo look unrehearsed.

---

## Part 2 — The script

Timings are targets, not rules. If you run over, cut from Part 5 (architecture), never from Part 4 (the live run).

---

### 0:00 – 0:30 · Hook
**On screen:** Deck, slide 1.

> "Think9 is building toward thirty-plus consumer brands. Right now, five of those brands buy the same fifty-millilitre amber glass bottle. They buy it from three different vendors, at three different prices, and nobody in the building knows — because in the quotes, it has five different names.
>
> This is LOOM. It's a sourcing intelligence layer that sits across the whole portfolio. I'll show you the problem, then I'll show you it running."

**Delivery:** Slower than feels natural. This is the only part they'll judge before deciding whether to keep watching.

---

### 0:30 – 1:15 · The five names
**On screen:** Deck, slide 3 — "One bottle. Five names."

> "Here's the same physical object as it actually arrives. A PDF from Neude's vendor calls it '50ml Amber Glass Bottle, 20mm neck.' Beauty by Bie's supplier calls it 'Amber Boston Round 50 ML, 20/400.' Panchamrit gets a WhatsApp message with just a vendor SKU code. There's an email describing it as '50cc, neck 20mm, without cap.' And one quote comes in Hindi.
>
> Nobody wrote these to be inconsistent. They came from four vendors across PDF, email and WhatsApp.
>
> And this is the part that matters: **you cannot combine orders for things you cannot prove are the same thing.** So the bottleneck isn't price comparison. It's identity. Until a system resolves that, bundling is arithmetically impossible."

**Delivery:** Pause after "five different names." Let it sit for a beat.

---

### 1:15 – 1:45 · Architecture — fast
**On screen:** Deck, slide 5.

> "Six layers. Quotes come in from wherever vendors actually send them. Extraction pulls structured line items with a confidence score per field — and never invents a value that isn't there. Resolution maps each line item to a canonical SKU. That feeds a spec graph, which is the compounding asset — every quote any brand receives makes every future negotiation better informed. Detectors run continuously over that graph, and when they find something, a human gets a negotiation brief.
>
> Three human gates. The agent never commits spend and never contacts a vendor."

**Delivery:** Deliberately brisk. Forty-five seconds, then move. Lingering here is what kills demo videos.

---

### 1:45 – 3:30 · THE LIVE RUN ← this is the video
**On screen:** Terminal, full screen, empty prompt.

> "This is a working prototype. Twelve vendor quotes in deliberately incompatible formats — PDFs, CSVs with contradictory column schemas, emails with prices written in prose, WhatsApp transcripts including Hinglish and Devanagari. No API key. Let's run it."

**→ Type `python run_demo.py` and hit enter. Let it complete. It takes under two seconds.**

> "That's the whole pipeline."

**→ Scroll back to the top. Walk down through it.**

**At the resolution table:**
> "Five different strings, four source formats — all resolved to one canonical SKU. That's the thing the whole system depends on."

**At the discrimination check — slow down here:**
> "But this is what I actually want you to see. There's a forty-eight millilitre bottle in this data. Against the fifty-millilitre canonical it scores eighty-five percent description similarity — which is exactly the fuzzy-match threshold. A text-based matcher merges these two.
>
> LOOM refuses. Volume forty-eight doesn't equal fifty, both are explicitly stated, and below a hundred millilitres there's no tolerance band. A shared description is evidence for a match. A disagreeing attribute is proof against one. Proof beats evidence.
>
> Had it merged, it would have added a thousand phantom units to the bundle underneath."

**At the Gate 1 queue:**
> "Four items held for a human. One WhatsApp message with no specs at all. Two products it's never seen. And one that's genuinely ambiguous — 'bottle, fifty, amber' matches three different canonical SKUs equally well, so it refuses to guess.
>
> Twenty-three of twenty-seven resolved. Eighty-five percent. That's the real number — the normalizer was written before this data existed and hasn't been tuned against it."

**At the opportunities and the brief:**
> "Four brands, each ordering below minimum order quantity, each paying a sub-MOQ premium. Consolidated, that's 2,550 units against an MOQ of 2,500 — it clears. Thirteen thousand two hundred and fifty-five rupees on this one bottle. Thirty-one thousand six hundred across the portfolio, from twelve quotes.
>
> And it stops here. Awaiting human approval. It does not commit spend."

**Delivery:** This is where you slow down, not speed up. Let the terminal do the talking — leave two or three seconds of silence while they read.

---

### 3:30 – 4:15 · The money
**On screen:** Deck, slide 4.

> "One thing about that number, because it's the argument the whole pitch rests on.
>
> Packaging suppliers price against minimum order quantities. Industry reporting for 2026 says it plainly — suppliers will accept five hundred units if you agree to pay twenty to thirty percent more per unit. Think9's brands are individually small, so they're almost certainly paying that surcharge on most shared components, most of the time.
>
> Four brands ordering separately pay that penalty four times. One consolidated order pays it zero times.
>
> So the saving isn't 'we negotiated harder.' It's 'we stopped paying a surcharge that existed only because we ordered separately.' That's arithmetic, not skill — which is exactly why it's defensible."

---

### 4:15 – 4:45 · Close
**On screen:** Deck, final slide.

> "Thirty days: packaging first, backfilled from GST e-invoice records. The milestone that matters is days sixteen to twenty-three — one real consolidated negotiation, with a banked rupee saving. Not a dashboard.
>
> Where I could be wrong: if contract manufacturers buy the packaging, there's less to bundle directly — so every brand-SKU edge carries a procurement mode, and CM-embedded spend gets rate-benchmarked instead. And a wrong canonical merge is the highest-cost failure in the system, which is why that's the one gate I won't automate.
>
> Everything you just saw runs on a fresh clone with no API key in under two seconds. Repo's in the submission. Thank you."

---

## Part 3 — Delivery notes

**Audio matters more than video.** A clear voice over a plain screen beats a polished screen with echo. Record in a small room with soft furnishings, phone earbuds with a mic are fine, and stay 15–20cm from the mic.

**Three or four takes is normal.** Do not try to nail it first time. Record Part 4 (the live run) separately if it helps — it's the section worth getting right.

**Do not read the script.** Learn the shape, then talk. Reading is audible, and it costs you more credibility than a stumble does.

**Pause instead of saying "um."** Silence sounds like thinking. Filler sounds like uncertainty.

**Camera bubble: on, small, bottom-right.** A face makes it a person presenting rather than a screen recording. Turn it off during the terminal section if it covers output.

**If you fluff a line, stop, breathe, and say it again.** Loom lets you trim. Don't restart the whole take.

---

## Part 4 — Common mistakes to avoid

| Mistake | Why it costs you |
|---|---|
| Terminal font too small | The single most common failure. If they can't read the output, the proof doesn't land |
| Spending 2 minutes on architecture | The slides already cover it. The video exists to show the thing *running* |
| Using a pre-recorded screenshot | Defeats the entire purpose. Run it live |
| Apologising for the synthetic data | State it once, plainly, and move on. Apologising invites doubt |
| Racing through the terminal output | Give them time to read. Silence is fine |
| Going over 5 minutes | They may simply stop watching |

---

## Part 5 — Checklist before you upload

- [ ] Video is under 5:00
- [ ] Terminal text readable at 50% zoom
- [ ] The live run is visible, unedited, start to finish
- [ ] The 48ml refusal is explained, not skipped
- [ ] The rupee figures are said out loud
- [ ] "It does not commit spend" is said out loud
- [ ] No notifications appeared on screen
- [ ] Audio is clear throughout
- [ ] Loom link sharing is set to **anyone with the link** — test in an incognito window
