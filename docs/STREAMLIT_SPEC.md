# LOOM Console — Streamlit Build Spec

> Read `CLAUDE.md` and `docs/PROTOTYPE_SPEC.md` first. The prototype is **frozen** — this app
> does not change it.

**Purpose:** the human-gate console the architecture promises by day 30. It is the L6 decision
layer made visible, plus a readable window onto L1–L4.

**Target:** ~2 hours. `streamlit run app.py`, no API key.

---

## 0. Non-negotiable constraints

| # | Rule | Why |
|---|---|---|
| 1 | **Import the existing `loom/` modules. Write no new business logic.** | The app is a view. Any calculation living in `app.py` is a bug. |
| 2 | **Every number must match `output/demo_run.txt` exactly.** | Rs 31,672.60 total, Rs 13,255 hero, 23/27 resolved, 4 held. If they diverge, the app is wrong. |
| 3 | **No new dependencies beyond `streamlit`.** | Same discipline as the prototype. No plotly, no pandas styling libraries. |
| 4 | **The Gate buttons must not commit anything real.** | They record a decision in session state and show what *would* happen. The agent never commits spend — that claim must stay true in the UI. |
| 5 | **Runs from a fresh clone with no API key.** | Same as the prototype. |

Add `streamlit>=1.32` to `requirements.txt`. Nothing else.

---

## 1. Structure

Single file `app.py` at the prototype root. Four tabs, in pipeline order — the tab bar itself
should read as the architecture:

```
[ 1 · Ingest ]  [ 2 · Resolution ]  [ 3 · Gate 1 Queue ]  [ 4 · Opportunities ]
```

Sidebar (persistent):
- LOOM wordmark and one-line descriptor
- Run stats: 12 artifacts · 27 line items · 23 resolved (85%) · 4 held
- **Rs 31,672.60 identified** as a large metric
- Small caption: *"Synthetic data. No API key. Pipeline runs in 1.8s."*

Cache the pipeline with `@st.cache_resource` so it runs once, not on every interaction.

---

## 2. Tab 1 — Ingest

Shows the mess the system eats. This is what makes the resolution tab land.

- A row of format chips: `3 PDF` `3 CSV` `2 email` `3 WhatsApp` `1 Excel`
- A selectbox listing all 12 source files
- On selection: show the **raw file contents** in a monospace block (for PDFs, show the
  extracted text), and beside it the **line items extracted from that file** with their
  per-field confidence
- Where a field was not stated, render `—` and not a guess. Make the null-safety visible.
- Flag the one L1 rejection inline where it occurs (`whatsapp_deccan.txt`) with its confidence
  of 0.40 and the reason

---

## 3. Tab 2 — Resolution

The hero tab. Two sections.

### 3a. Five names, one object

A table of the five hero line items — raw description, brand, source file, method, confidence —
with a prominent banner beneath:

> **ALL RESOLVE TO → GLS-AMB-050-20** · 50ml amber glass bottle, 20mm neck
> 4 brands · 2,550 units of requirement

Render the raw descriptions in monospace. The visual point is that five different strings
collapse to one identifier.

### 3b. The discrimination check — make it interactive

This is the most valuable screen in the app. Let the user pick **any** line item from a
selectbox and see it evaluated against **every** canonical SKU:

For each candidate, a card showing:
- Candidate ID and description
- `description similarity: NN%` with the stage-4 threshold (85) alongside
- An attribute-by-attribute comparison table: attribute · item value · candidate value ·
  `agree` / `*** CONTRADICTS ***` / `not stated — compatible`
- A verdict line: **ACCEPTED** (green) or **REJECTED by the contradiction rule** (red)

Default the selectbox to the 48ml bottle, since that is the case that proves the engine
discriminates. Beneath its result, show the explanation verbatim from the engine:

> A shared description is evidence for a match; a disagreeing attribute is proof against one,
> and proof beats evidence.

Do not hardcode any of this — call the real resolver and render what it returns.

---

## 4. Tab 3 — Gate 1 Queue

The human gate, made real.

Four cards, one per held item. Each shows:
- Gate status badge: `reject_low_confidence` / `new_canonical_proposed` / `review`
- Raw description, brand, source file
- The reason it was held, in full
- For `review` items, the competing canonical candidates it could not choose between

**Buttons per card:** `Approve` · `Reject` · `Defer`

On click, record the decision in `st.session_state` and show the consequence in plain language,
e.g. *"Would create canonical SKU CAN-009 and link 1 line item. Not committed — this is a
prototype."*

At the top of the tab, a standing note:

> The agent stops here. A wrong canonical merge silently corrupts every downstream
> recommendation, so ambiguity routes to a human rather than a guess.

---

## 5. Tab 4 — Opportunities

Ranked list, highest rupee impact first. Each expandable row shows the headline, the kind badge,
the rupee figure, and an `EXPIRING` flag where applicable.

Expanded, show the **working** — the same lines the console prints. The MOQ arithmetic must be
visible and hand-checkable: each brand's qty and price, the penalty tier applied, combined volume
versus MOQ, derived base price, resulting saving. No black boxes.

Below the list, render the full **negotiation brief** for the top opportunity: participating
brands with competing quotes shown as alternates, volume position, price intelligence, BATNA,
risk notes, and the target with its reasoning.

End with the Gate 2 block:

- `Approve consolidation` · `Reject` · `Request changes`
- Beneath, permanently visible:

> **AWAITING HUMAN APPROVAL — GATE 2.** This system does not commit spend. It has not contacted
> this vendor and will not. Gate 3 covers vendor communication: a category manager sends anything
> that leaves the building.

Footer: the portfolio total, plus the non-additive note about risk findings.

---

## 6. Styling

Restrained. This is an internal operations console, not a marketing site.

- `st.set_page_config(layout="wide", page_title="LOOM Console")`
- Default Streamlit theme. Do not fight it.
- Monospace for anything that came from a vendor: raw descriptions, SKU codes, file contents
- Colour used only semantically — green accepted, red contradicts/rejected, amber held
- `st.metric` for the headline numbers
- No logos, no stock imagery, no gradients

---

## 7. Acceptance tests

- [ ] `streamlit run app.py` starts clean on a fresh clone, no API key
- [ ] Sidebar total reads **Rs 31,672.60**, matching `output/demo_run.txt`
- [ ] Tab 2 shows five raw strings resolving to `GLS-AMB-050-20`
- [ ] The 48ml item is **REJECTED** against `GLS-AMB-050-20` on volume, with the similarity
      shown as 85% against a threshold of 85
- [ ] Tab 3 holds exactly 4 items, each with its real reason
- [ ] Tab 4's top opportunity is Rs 13,255 with the MOQ arithmetic fully visible
- [ ] Gate 2 text is present and the buttons commit nothing
- [ ] No business logic lives in `app.py` — verify by inspection
