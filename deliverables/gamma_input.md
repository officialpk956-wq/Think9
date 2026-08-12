# LOOM — Gamma Input

Paste this into Gamma (Create → Paste in text → "Preserve" content mode) or let the Gamma
connector generate from it. Each `---` is a card break.

**Settings to use in Gamma:**
- Content mode: **Preserve** (not Generate) — keeps the exact numbers and wording
- Tone: professional, analytical
- Theme: dark, editorial (e.g. Oasis, Vortex, Chisel) — avoid pastel/startup themes
- Image style: minimal / abstract, or none. Do NOT let it auto-insert stock photos of
  warehouses and handshakes; they cheapen a technical pitch.

---

# LOOM
## A cross-portfolio sourcing intelligence layer

**30x the buying power. 1x the negotiating leverage.**

Think9 AI & Intelligence Challenge · Track 2: Cross-Portfolio Supply Chain & Sourcing

> "AI will redefine agility for business — making paths to growth speedy and seamless."
> — Think9, Principles

---

## Why now

# Packaging costs are spiking this quarter

**15–25%** increase in packaging input costs, 2026

- **Crude-linked inputs** — up 20–25% against pre-conflict levels
- **FMCG packaging specifically** — up 15–20%
- **D2C margins** — squeezed simultaneously on raw materials, packaging, logistics and manufacturing

This is margin defence against a dated, live shock — not a theoretical efficiency gain.

*Sources: Packaging South Asia; Inc42, "Boxed In: The War Shock For D2C"*

---

## The bottleneck

# Scale that exists on paper, not in the room

Each brand sources independently. That is the correct thing for each brand to do.

**30x** — the buying power of any single brand
**1x** — the negotiating leverage at the table

Because at the moment a brand negotiates, nobody in the building can see what the other brands pay for the same physical object.

Not a discipline problem. Not solved by a shared spreadsheet. And it gets monotonically worse as the portfolio grows.

**Built at 11 brands. Designed for 30+.**

---

## The hard problem

# One bottle. Five names.

The same 50ml amber glass bottle, as it actually appears across the portfolio:

- `50ml Amber Glass Bottle, 20mm neck` — Neude, PDF
- `Amber Boston Round 50 ML (20/400)` — Beauty by Bie, PDF
- `GB-AMB-50-20N` — Panchamrit, WhatsApp
- `Glass bottle - amber - 50cc - neck 20mm - w/o cap` — Neude, email
- `एम्बर ग्लास बॉटल 50ml 20mm` — Goodbug, WhatsApp

**You cannot combine orders for things you cannot prove are the same thing.**

So the bottleneck is not price comparison. It is SKU identity resolution — and that is what a script cannot do and a model against a spec graph can.

Nobody wrote these to be inconsistent. They arrived from four vendors across PDF, email and WhatsApp.

---

## Earning the AI

# Why not a script, and why not a hire

**Could a script do it? No.**
There is no fixed input schema. ~200 vendors, each with their own quote layout, new ones onboarding constantly. Any regex-based parser is obsolete within a quarter.

**Could a team do it? Too slow.**
3–4 FTE of tedious, error-prone work — and quotes expire in 15–30 days. Value exists only inside that window. A human queue introduces exactly the latency that destroys it.

**Why agentic? It is a loop.**
Low-confidence extraction must trigger a clarifying action. Resolution must decide match-or-create against growing state. Detection runs continuously as quotes arrive and lapse.

Perceive → reason → act → observe, against persistent state. That is an agent, not a transform.

---

## The money

# A surcharge we pay only because we order apart

> "Suppliers may accept 500 units if buyers agree to pay 20–30% more per unit."
> — Industry reporting on 2026 packaging procurement

**Ordering separately: 4×**
Four brands, each below MOQ, each paying the sub-MOQ premium — four separate times.

**Ordering together: 0×**
One consolidated order clears the MOQ. The premium does not apply at all.

**The saving is not "we negotiated harder." It is "we stopped paying a surcharge that existed only because we ordered separately."**

Arithmetic, not skill — which is why it is defensible. Negotiating leverage is upside on top.

---

## System architecture

# Six layers, three human gates

- **L0 · INGEST** — Email, WhatsApp, file drop, ERP export, stored immutably with provenance
- **L1 · EXTRACTION** — Line items with per-field confidence and source-span citation. Never infers a missing value *(confidence routing)*
- **L2 · RESOLUTION** — Line item to canonical SKU. Attribute normalization, tolerance rules, fuzzy fallback *(GATE 1)*
- **L3 · SPEC GRAPH** — Canonical SKUs, vendors keyed on GSTIN, brands, price history, procurement mode
- **L4 · OPPORTUNITY** — Five always-on detectors: bundling, price outlier, concentration, lead-time drift, expiry
- **L5 · BRIEF** — The negotiation packet a human takes into the call, with reasoning shown
- **L6 · DECISION** — Category manager approves. Outcome writes back, the graph learns *(GATES 2 & 3)*

The agent never commits spend and never contacts a vendor.

---

## Why it must be central

# Value that compounds instead of adding up

**Most AI proposals — Linear.**
Help one team do one thing faster. Deploy to 30 brands, get 30 units of value, pay 30 units of cost.

**LOOM — Superlinear.**
Every quote any brand receives makes the graph denser, which makes every future negotiation across all other brands better informed.

**The next brand starts at portfolio-best.**

- Brand 12 does not negotiate up from scratch — it inherits portfolio-best pricing, qualified vendors and known lead times on day one.
- Think9 grows partly by acquisition. An acquired brand arrives with its own vendor list and its own naming conventions — canonical resolution is exactly the tool that absorbs it.
- This only works if the system sits at the centre. Which is what "centralized intelligence layer" asks for.

---

## Human-in-the-loop

# Three gates, placed where errors cost most

**Gate 1 · Canonical creation (L2) — Sourcing analyst**
Graph pollution. A wrong merge silently corrupts every downstream recommendation and is hard to detect afterwards.

**Gate 2 · Spend recommendation (L6) — Category manager**
Committing money on a machine judgment. The agent proposes consolidation; a human authorises it.

**Gate 3 · Vendor communication (L6) — Category manager**
Reputational and negotiating-position damage. The agent drafts; a human sends.

**Confidence routing:** ≥ 0.90 auto-advance · 0.60–0.90 human review · < 0.60 reject to human

Human effort scales with ambiguity, not with volume. That is what makes it economical.

Full autonomy here would be a design error, not a feature.

---

## Proof of concept

# It runs. No API key, 1.8 seconds.

**12** vendor artifacts · **27** line items · **8** canonical SKUs · **5** Think9 brands

**Deliberately incompatible formats**
3 PDF letterheads · 3 CSVs with mutually contradictory column schemas · 2 email bodies with prices in prose · 3 WhatsApp transcripts including Hinglish and Devanagari · 1 Excel with merged cells

**Real, not scaffolded**
- Resolution cascade and the contradiction rule
- Five detectors computing from a live SQLite graph
- Every rupee figure derived, none asserted

The normalizer was written before the quote data existed and has not been tuned against it.

`python run_demo.py`

---

## Proof of concept — output

# Five names resolved. One bundle. A rupee figure.

**GLS-AMB-050-20** — 50ml amber glass bottle, 20mm neck

| Brand | Qty | Price |
|---|---|---|
| Neude | 800 | Rs 20.75 |
| Beauty by Bie | 600 | Rs 21.50 |
| Panchamrit | 450 | Rs 22.50 |
| Goodbug | 700 | Rs 22.80 |

2,550 units of requirement vs MOQ 2,500 → clears

**Rs 13,255** saved on this SKU by consolidating four brands into one order
**Rs 31,672.60** total identified across six audited findings, from 12 quotes
**23 / 27 resolved (85%)** · 4 held for human review

**The refusal matters as much as the match.**
A 48ml bottle scored 85% description similarity against the 50ml canonical — exactly the fuzzy-match threshold. A text-based matcher merges them. LOOM refuses: volume 48 ≠ 50, both stated. Had it merged, it would have added 1,000 phantom units to the bundle above.

Risk findings are excluded from the total — they quantify exposure against spend already counted, not new money.

---

## Implementation

# Thirty days to a banked saving

Scoped to packaging only — highest cross-brand overlap, substantial spend, and no regulatory sign-off to slow the loop.

**Days 1–7 · Ingest & extraction**
Live for packaging. Seed ~150 canonical SKUs from the top 3 brands by spend.
*Exit: extraction F1 ≥ 0.90*

**Days 8–15 · Resolution & graph**
Backfill 90 days of history via GST e-invoice records. GSTIN as vendor key.
*Exit: 80% of spend resolved*

**Days 16–23 · First real negotiation**
Opportunity agent live. Run one consolidated negotiation end to end.
*Exit: one banked rupee saving*

**Days 24–30 · Gates & measurement**
Human-gate console, alerting, instrumentation. Publish the baseline.
*Exit: cycle time, before / after*

A system that banks one real saving in month one earns the right to expand to ingredients, logistics and services. One that produces a dashboard does not.

---

## Stack

# Boring on purpose

- **Extraction** — Claude vision, OCR fallback. Removes the brittle OCR-to-parse chain for photographed quotes
- **Orchestration** — Temporal, not LangGraph. Negotiations span days and must survive restarts. Durability beats graph ergonomics
- **Storage** — Postgres + pgvector, not Neo4j. At this volume the graph is small; recursive CTEs handle the traversals
- **Serving** — FastAPI + Streamlit console. The human gates must exist by day 30. Streamlit builds in days

**Scale sanity check**
**24,000** quote line-items per year. About 100 a working day.
**~$500** a year in inference cost, against a savings target in crores.

A small-data problem wearing a big-data costume.

No Kafka. No Spark. No vector database. Refusing infrastructure the scale does not justify is itself a design decision.

---

## Failure modes

# What would make me wrong

**Wrong canonical merge**
Two different SKUs unified, and every recommendation built on a false equivalence.
→ Gate 1. All merges reversible with audit trail. Precision weighted above recall.

**Contract manufacturers buy the packaging**
If the co-packer procures, the brand isn't buying it and there is nothing to bundle.
→ Every brand-SKU edge carries procurement mode. Direct-buy bundles; CM-embedded gets rate-benchmarked.

**Vendors learn we bundle**
Base quotes inflate in anticipation of consolidated volume.
→ Do not disclose portfolio volume until commit. Maintain and use BATNA vendors.

**Over-consolidation**
Single-sourcing a bundled SKU creates a new portfolio-level supply risk.
→ Concentration is a first-class alert, surfaced alongside every saving.

An architecture that has not enumerated its failure modes has not been designed.
