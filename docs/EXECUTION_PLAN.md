# Execution Plan — T9 Challenge
**Now:** Monday 10 Aug 2026 · **Deadline:** Wednesday 12 Aug · **Working time:** Mon + Tue full days

---

## The governing principle

You are rewriting everything in your own words. That is the right call, and it dictates the shape of this plan.

**The submission is not the deliverable. The interview is.** A polished deck you can't defend line-by-line is worth less than a rougher one you wrote yourself. So this plan front-loads my drafting into Monday, and protects large blocks on Tuesday for you to absorb, rewrite, and stress-test.

Every block below has an explicit owner. Where it says **YOU**, I can't do it for you and shouldn't try.

---

## Deliverables

| # | Artifact | Format | Owner | Priority |
|---|---|---|---|---|
| 1 | Slide deck | PDF, 12–14 slides | Me → **YOU** rewrite | **P0** |
| 2 | Working prototype | Python repo + README | Me | **P0** |
| 3 | Architecture doc | Markdown/PDF (already drafted) | Me → **YOU** trim | P1 |
| 4 | Video walkthrough | ~5 min screen recording | **YOU** (my script) | P1 |
| 5 | Submission email | Short, 6–8 lines | Me → **YOU** rewrite | **P0** |
| 6 | Defence notes | Q&A prep, not submitted | Me → **YOU** rehearse | P1 |

**If everything slips, P0 alone is a strong submission.** Deck + working code + a good email beats a half-finished everything.

---

## MONDAY — Build day (my load is heaviest)

### Block 1 · Prototype core *(me, ~3h)*
Build in this order, because each depends on the last:

1. **Synthetic dataset** — 12 vendor quotes across deliberately messy formats:
   - 3 PDFs on fake vendor letterhead
   - 3 CSV/Excel with mutually incompatible column schemas
   - 2 email bodies with prices in prose
   - 2 WhatsApp chat transcripts (India-realistic: partial specs, "same as last time")
   - 2 with Hindi/Hinglish product descriptions
   
   Covering ~8 canonical SKUs across 5 brands — **SuperYou, Goodbug, Panchamrit, Neude, Beauty by Bie** — with each canonical SKU appearing under 3–5 different names.

2. **`extract.py`** — format-specific parsers, per-field confidence, source-span citation, null-if-absent. Optional Claude vision path if `ANTHROPIC_API_KEY` is set; deterministic fallback otherwise so **it runs on any machine with no key**.

3. **`resolve.py`** — the star. Attribute normalization (50cc = 50ml = 50 ML), material/colour/finish canonicalization, dimensional tolerance, fuzzy match on residual description. Fully deterministic, no API needed.

### Block 2 · Prototype intelligence *(me, ~2h)*
4. **`graph.py`** — SQLite spec graph. Canonical SKUs, vendors (keyed on GSTIN), brands, price history, lead times, **`procurement_mode`** (`direct` / `cm_embedded` / `unknown`).
5. **`opportunities.py`** — five detectors: MOQ-bundling, price outlier, vendor concentration, lead-time drift, quote-expiry pressure.
6. **`brief.py`** — negotiation brief: consolidated volume, portfolio-best price, vendor's own floor, BATNA alternatives, target price with reasoning shown.
7. **`run_demo.py`** + HTML report + README.

**Exit criterion:** `python run_demo.py` runs clean on a fresh clone and prints a bundling recommendation with a rupee figure.

### Block 3 · Deck v1 *(me, ~2h)*
Full draft, 12–14 slides, structure below. Written to be *rewritten* — I'll keep sentences short and claims separable so you can restate them in your voice without unpicking the logic.

### Block 4 · **YOU — absorption** *(~1.5h, Monday evening)*
Read in this order: research brief → market context brief → architecture doc → deck.

Do not edit yet. Just read, and keep a running list of anything you don't believe or can't explain. That list is Tuesday's agenda.

---

## TUESDAY — Your day

### Block 5 · **YOU — rewrite the deck** *(~3h, morning)*
Rewrite every slide in your own words. Rules:
- If you can't explain a claim without reading it, **cut it**
- Replace any number you can't source with one you can
- Your voice > my phrasing, every time

I'm on hand to fix anything that breaks under rewriting.

### Block 6 · Prototype polish + your review *(me + YOU, ~2h)*
You run it yourself on your own machine. Anything confusing gets fixed. Then I finalise the README so a reviewer can run it in one command.

### Block 7 · Video *(YOU, ~2h including retakes)*
My script + shot list. 5 minutes, structured below. Expect 3–4 takes; that's normal and fine.

### Block 8 · Defence prep *(YOU, ~1h)*
I produce ~15 likely challenge questions with answers. You rehearse aloud. The ones that matter most:
- *"Your brands use contract manufacturers — who actually buys the packaging?"*
- *"You've only got 11 brands, not 30. Does this even pay for itself?"*
- *"Why won't a shared spreadsheet solve this?"*
- *"What happens when the model merges two SKUs that aren't the same?"*

### Block 9 · Assemble + send *(YOU, ~45min)*
Export deck to PDF, push repo, upload video, draft email, **send Tuesday night.**

---

## WEDNESDAY — Buffer only

Deadline day is not a work day. It exists so that a laptop failure, a bad night's sleep, or a broken export doesn't cost you the submission. **Target sending Tuesday evening.**

---

## Deck structure (12–14 slides)

Their stated values include *"Clarity over complexity"* and *"Less is more."* A dense deck argues against their own principles — restraint is itself part of the pitch.

| # | Slide | Job |
|---|---|---|
| 1 | **Title + one-line thesis** | "30x buying power, 1x leverage." Open on their own principle: *"AI will redefine agility."* |
| 2 | **Why now** | Packaging costs +15–25%. Live margin shock, dated. |
| 3 | **The bottleneck** | Each brand negotiates alone; nobody sees across the portfolio. |
| 4 | **One bottle, five names** | ⭐ The money slide. Show the same SKU under 5 names. Visual, instant, unarguable. |
| 5 | **Why AI — not a script, not a hire** | Earn the AI explicitly. Three tests. |
| 6 | **The MOQ penalty** | 20–30% surcharge, paid 5× instead of 0×. The arithmetic. |
| 7 | **Architecture** | Six layers, one diagram. |
| 8 | **The compounding asset** | Spec graph. Why this must be central, not per-brand. |
| 9 | **Human-in-the-loop** | Three named gates. Confidence routing. |
| 10 | **Prototype — what it does** | Screenshot of messy inputs. |
| 11 | **Prototype — the output** | Bundling recommendation + rupee saving. |
| 12 | **30-day roadmap** | Four milestones. Day 16–23 = one real banked saving. |
| 13 | **Stack + scale sanity** | 24k quotes/yr, ~$500/yr inference. Postgres, not Kafka. |
| 14 | **What would make me wrong** | Failure modes, stated openly. Ends on confidence, not bravado. |

**Optional 15th if it earns its place:** the pattern generalises — swap the entity and the same five layers become the Feedback Hub or the Think9 Brain.

**Two framing decisions carried throughout:**
- Position LOOM inside the **Office of Optimisation**, delivering that unit's first supply-chain case study
- Frame as **"built at 11 brands, designed for 30+"** — never correct their 30+ figure directly

---

## Video script — 5 minutes

| Time | Content |
|---|---|
| 0:00–0:30 | Hook. "Five Think9 brands buy the same bottle from three vendors at three prices. Nobody knows, because it has five different names." |
| 0:30–1:15 | Show the five names on screen. State the resolution problem. |
| 1:15–2:00 | Architecture — six layers, 40 seconds. Do not linger. |
| 2:00–3:45 | **Live prototype run.** Messy quotes in → canonical resolution → bundling recommendation with the rupee figure. This is the segment that wins it. |
| 3:45–4:30 | The MOQ arithmetic + 30-day roadmap. |
| 4:30–5:00 | Close: where it goes next, and what would make you wrong. |

**Record the terminal live.** Do not use a pre-baked screenshot — the whole point is proving it runs.

---

## Cut lines — if you fall behind

Cut in this order, without hesitation:

1. HTML report *(console output is enough)*
2. Claude vision extraction path *(deterministic fallback demos identically)*
3. Video *(P1, not P0)*
4. Architecture doc as a separate artifact *(fold key content into deck appendix)*
5. Slides 13 and 14 *(painful, but 12 slides still tells the story)*

**Never cut:** the working prototype, slide 4 (five names), slide 6 (MOQ arithmetic), or the 30-day roadmap. Those four are the submission.

---

## Definition of done

- [ ] `python run_demo.py` runs clean on a **fresh clone, no API key**
- [ ] Every number in the deck traces to a source or to prototype output
- [ ] You can explain **every slide** without reading it
- [ ] Deck is ≤14 slides
- [ ] README lets a reviewer run it in **one command**
- [ ] Video ≤5:30
- [ ] Email is under 10 lines
- [ ] Real brand names used (SuperYou, Goodbug, Panchamrit, Neude, Beauty by Bie)
- [ ] Office of Optimisation named as the system's home
- [ ] Nothing anywhere corrects their "30+ brands" figure
- [ ] Zero mention of Future Group

---

## Risk register

| Risk | Mitigation |
|---|---|
| Prototype doesn't run on your machine | Test on your machine **Monday night**, not Tuesday |
| Rewriting takes longer than 3h | Deck is drafted in short, separable sentences specifically to speed this up |
| You freeze on video | Script + shot list; 3–4 takes is normal; audio matters more than video |
| A number gets challenged | Every figure sourced in the briefs; say "self-reported" or "industry estimate" where true |
| Scope creep into a second track | **Do not.** One track, done deeply, beats two done shallowly. |

---

## What I do next, in order

1. Synthetic dataset + extraction layer
2. Resolution engine *(the differentiator)*
3. Spec graph + opportunity detectors + negotiation brief
4. End-to-end demo + README
5. Deck v1
6. Video script + shot list
7. Defence Q&A
8. Submission email draft

Starting at (1) now unless you want to reorder.
