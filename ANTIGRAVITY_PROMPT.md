# Antigravity Prompt — LOOM Console

Open `D:\Think9` as the workspace, then paste everything below the line.

---

## Context

This repo is a submission for the **Think9 AI & Intelligence Challenge** — a hiring assignment,
deadline Wednesday 12 August 2026. Think9 is an Indian venture studio in Mumbai building a
portfolio of consumer brands. The brief asks for an agentic AI system deployable centrally across
their brand portfolio to remove a business bottleneck.

Read these before writing any code:
- `CLAUDE.md` — full project context, the argument, the constraints
- `docs/PROTOTYPE_SPEC.md` — how the existing engine works
- `docs/STREAMLIT_SPEC.md` — the console spec you are implementing
- `prototype/output/demo_run.txt` — the committed reference output, 327 lines

### The pitch in three sentences

Think9 has 30x the buying power of any single brand but 1x the negotiating leverage, because at
the moment a brand negotiates nobody can see what the other brands pay for the same physical
object. The hard problem is not price comparison — it is **SKU identity resolution**: the same
50ml amber glass bottle appears across brands as `50ml Amber Glass Bottle, 20mm neck`,
`Amber Boston Round 50 ML (20/400)`, `GB-AMB-50-20N`, `Glass bottle - amber - 50cc - neck 20mm -
w/o cap`, and `एम्बर ग्लास बॉटल 50ml 20mm`. Until a system proves those are one object, bundling
is arithmetically impossible.

### What already exists — and must not change

`prototype/` contains a **frozen, working, verified** pipeline. It runs in 1.8s with no API key,
passes 10/10 tests, and produces `Rs 31,672.60` of identified savings across six audited findings.

**Do not modify anything under `prototype/loom/`, `prototype/data/`, or `prototype/run_demo.py`.**
If you believe there is a bug, report it — do not fix it.

---

## What to build

A single-file Streamlit app, `prototype/app.py`, that is a **view over the frozen engine**.

This app is the demo. It will be screen-recorded end to end for a video walkthrough, so the five
tabs must run left to right in narrative order. The presenter walks across the tab bar and the
story tells itself.

```
[ 1 · The Problem ]  [ 2 · Ingest ]  [ 3 · Resolution ]  [ 4 · Gate 1 Queue ]  [ 5 · Opportunities ]
```

### Hard constraints

1. **Import from `loom/`. Write no business logic in `app.py`.** Every number must come from the
   engine. Any calculation living in the app is a bug.
2. **Every figure must match `output/demo_run.txt` exactly** — Rs 31,672.60 total, Rs 13,255 hero
   bundle, 2,550 units vs MOQ 2,500, 23/27 resolved (85%), 4 held. If they diverge, the app is
   wrong, not the prototype.
3. **Only new dependency is `streamlit`.** No pandas styling, no plotly, no altair. Add
   `streamlit>=1.32` to `requirements.txt` and nothing else.
4. **The Gate buttons must not commit anything.** They record a decision in `st.session_state` and
   display what *would* happen. The claim "this agent never commits spend" has to remain literally
   true inside the UI.
5. **Runs on a fresh clone with no API key**, via `streamlit run app.py`.
6. Cache the pipeline with `@st.cache_resource` so it executes once, not on every rerun.

---

## Sidebar (persistent)

- `LOOM` wordmark, and beneath it: *Cross-portfolio sourcing intelligence*
- A **`▶ Run pipeline`** button. On click, execute the real pipeline and display the elapsed time
  (`Completed in 1.8s`) plus a progress line per layer (L0 → L6). This matters: the video needs a
  visible moment of the thing actually executing, not just rendering precomputed results.
- Run stats as `st.metric`: `12 artifacts` · `27 line items` · `23 resolved (85%)` · `4 held`
- **`Rs 31,672.60 identified`** as the headline metric
- Caption: *Synthetic data · No API key · Pipeline runs in 1.8s*

---

## Tab 1 — The Problem

The hook. Mostly static, but it must be the most visually striking screen in the app.

- Headline: **One bottle. Five names.**
- The five raw strings in monospace cards, each tagged with brand and source format (PDF /
  WhatsApp / email). Include the Devanagari string exactly as written.
- Beneath, in large type: **You cannot combine orders for things you cannot prove are the same
  thing.**
- A short block: the bottleneck is not price comparison, it is SKU identity resolution.
- A second block — the money: *suppliers may accept 500 units if buyers agree to pay 20–30% more
  per unit.* Four brands ordering separately pay that surcharge four times; one consolidated order
  pays it zero times. **The saving is not "we negotiated harder" — it is "we stopped paying a
  surcharge that existed only because we ordered separately."**

---

## Tab 2 — Ingest

Shows the mess the system eats. This is what makes Tab 3 land.

- Format chips: `3 PDF` `3 CSV` `2 email` `3 WhatsApp` `1 Excel`
- Selectbox of all 12 source files
- Two columns: **raw file contents** in monospace on the left (extracted text for PDFs), and the
  **line items extracted from that file** on the right, with per-field confidence
- Fields that were not stated render as `—`, never a guess. Make the null-safety visible.
- Flag the L1 rejection inline where it occurs (`whatsapp_deccan.txt`, confidence 0.40) with its
  reason

---

## Tab 3 — Resolution

The most important tab. Two sections.

**3a — Five names, one object.** A table of the five hero line items (raw description, brand,
source, method, confidence), with a prominent banner beneath:

> **ALL RESOLVE TO → GLS-AMB-050-20** · 50ml amber glass bottle, 20mm neck
> 4 brands · 2,550 units of requirement

**3b — The discrimination check, interactive.** A selectbox of every line item; on selection,
evaluate it against **every** canonical SKU and render one card per candidate showing:

- Candidate ID and description
- `description similarity: NN%` alongside the stage-4 threshold of 85
- Per-attribute comparison: attribute · item value · candidate value ·
  `agree` / `*** CONTRADICTS ***` / `not stated — compatible`
- Verdict: **ACCEPTED** (green) or **REJECTED by the contradiction rule** (red)

**Default the selectbox to the 48ml bottle.** It scores exactly 85% against the 50ml canonical —
precisely the fuzzy-match threshold — so a pure text matcher merges them and LOOM refuses anyway.
Render the engine's own explanation beneath:

> A shared description is evidence for a match; a disagreeing attribute is proof against one, and
> proof beats evidence.

Call the real resolver. Hardcode nothing.

---

## Tab 4 — Gate 1 Queue

The human gate made real. Four cards, one per held item:

- Status badge: `reject_low_confidence` / `new_canonical_proposed` / `review`
- Raw description, brand, source file
- The full reason it was held
- For `review` items, the competing canonicals it could not choose between

Buttons per card: `Approve` · `Reject` · `Defer`. On click, store the decision in session state
and state the consequence plainly — e.g. *"Would create canonical SKU CAN-009 and link 1 line
item. Not committed — this is a prototype."*

Standing note at the top of the tab:

> The agent stops here. A wrong canonical merge silently corrupts every downstream recommendation,
> so ambiguity routes to a human rather than a guess.

---

## Tab 5 — Opportunities

Ranked by rupee impact. Each row expandable, showing the headline, kind badge, rupee figure, and
an `EXPIRING` flag where applicable.

Expanded, show the **full working** — the same lines the console prints. The MOQ arithmetic must
be hand-checkable: each brand's qty and price, penalty tier applied, combined volume vs MOQ,
derived base price, resulting saving.

Below, the complete **negotiation brief** for the top opportunity: participating brands with
competing quotes shown as alternates (not summed), volume position, price intelligence, BATNA,
risk notes, target price with reasoning.

Close with the Gate 2 block — `Approve consolidation` · `Reject` · `Request changes` — and
permanently visible:

> **AWAITING HUMAN APPROVAL — GATE 2.** This system does not commit spend. It has not contacted
> this vendor and will not. Gate 3 covers vendor communication: a category manager sends anything
> that leaves the building.

Footer: portfolio total plus the note that risk findings are excluded because they quantify
exposure against spend already counted, not new money.

---

## Styling

Restrained. This is an internal operations console for a category manager, not a marketing site.

- `st.set_page_config(layout="wide", page_title="LOOM Console")`
- Default Streamlit theme — do not fight it
- Monospace for anything a vendor wrote: raw descriptions, SKU codes, file contents
- Colour only semantically: green accepted, red contradicts/rejected, amber held
- `st.metric` for headline numbers
- No logos, no stock imagery, no gradients, no emoji

---

## Verification — required before you report done

Run the app, open it in the browser, and **screenshot every tab**. Check against this list:

- [ ] `streamlit run app.py` starts clean on a fresh clone with no API key
- [ ] Sidebar total reads **Rs 31,672.60**
- [ ] `▶ Run pipeline` visibly executes and reports elapsed time
- [ ] Tab 3 shows five raw strings resolving to `GLS-AMB-050-20`
- [ ] The 48ml item is **REJECTED** against `GLS-AMB-050-20` on volume, similarity shown as 85%
      against threshold 85
- [ ] Tab 4 holds exactly 4 items, each with its real reason
- [ ] Tab 5's top opportunity is **Rs 13,255** with the MOQ arithmetic fully visible
- [ ] Gate 2 text present; no button commits anything
- [ ] No business logic in `app.py` — confirm by inspection
- [ ] Nothing under `prototype/loom/`, `prototype/data/`, or `run_demo.py` was modified
      (`git diff --stat` to prove it)

Report any figure that does not match `demo_run.txt` rather than adjusting the app to hide it.

---

## One more thing

This app will be screen-recorded at 1920×1080 and compressed. Keep type large, avoid dense tables
that need horizontal scrolling, and make sure the key numbers — Rs 13,255, Rs 31,672.60, 2,550 vs
2,500, 85% vs 85 — are the largest things on their respective screens.
