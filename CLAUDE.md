# LOOM — Project Context

> **This file is the primary context for Claude Code working in this repo. Read it fully before writing any code.**

---

## 1. What this is

This is a submission for the **Think9 AI & Intelligence Challenge**, a hiring assignment. Deadline **Wednesday 12 August 2026**.

Think9 is an Indian venture studio (Mumbai) building a portfolio of consumer brands. The challenge asks candidates to pitch an agentic AI system deployable centrally across their brand portfolio to remove a business bottleneck.

**Our chosen track: Cross-Portfolio Supply Chain & Sourcing Agent.**

**The system is called LOOM** — it weaves 30 separate brand procurement threads into one fabric.

We are building a **working prototype** to accompany a slide deck. The prototype is the primary differentiator: most candidates will submit slides only.

---

## 2. The core argument (do not lose this)

Think9 has **30x the buying power of any single brand but 1x the negotiating leverage**, because at the moment a brand negotiates, nobody can see what the other brands pay for the same physical object.

The hard problem is **not** price comparison. It is **SKU identity resolution**.

The same 50ml amber glass bottle appears across brands as:
- `50ml Amber Glass Bottle, 20mm neck`
- `Amber Boston Round 50 ML (20/400)`
- `GB-AMB-50-20N`
- `Glass bottle - amber - 50cc - neck 20mm - w/o cap`
- `एम्बर ग्लास बॉटल 50ml 20mm`

Until a system **proves** these are the same object, bundling is arithmetically impossible. That is the wedge, and it is what the prototype must demonstrate above all else.

### The money argument

Packaging suppliers price against **Minimum Order Quantity**. Industry reporting for 2026: *suppliers may accept 500 units if buyers agree to pay 20-30% more per unit.*

Think9's brands are individually small, so each is likely paying that sub-MOQ surcharge. Five brands each ordering 500 units pay the penalty **five times**. One consolidated order of 2,500 units clears MOQ and pays it **zero times**.

**The saving is not "we negotiated harder." It is "we stopped paying a surcharge that existed only because we ordered separately."** This is arithmetic, not skill — which is why it is defensible.

---

## 3. Non-negotiable constraints

| # | Constraint | Why |
|---|---|---|
| 1 | **Must run with NO API key** | A reviewer clones and runs. If it needs a key, most never see it work. An optional Claude path may exist, but the deterministic path must fully demo the system. |
| 2 | **The resolution engine must be genuinely real** | It is the claim being made. Extraction may be partly scaffolded; resolution may not be faked. |
| 3 | **Output must be a rupee figure** | Not a dashboard, not a chart. A number a category manager could act on. |
| 4 | **Show the misses** | A resolver catching 26/30 with visible failures is more credible than one catching 30/30. Do not hide failures. |
| 5 | **Human gates must be visibly real** | Items held awaiting approval must appear in output. A system that refuses to merge and asks a human reads as engineering; one that resolves everything reads as theatre. |
| 6 | **Minimal dependencies** | `rapidfuzz`, `pdfplumber`, `reportlab` only. Deliberately boring. No Kafka, no Spark, no vector DB. |

---

## 4. Scale reality — do not over-engineer

~30 brands x ~50 sourced SKUs x ~4 vendors x quarterly re-quoting = **~24,000 quote line-items per year**. About 100 per working day.

This is a **small-data problem wearing a big-data costume**. SQLite for the prototype, Postgres in production. Refusing infrastructure theater is itself part of the pitch — do not add distributed anything.

---

## 5. Domain facts that shape the design

- **GSTIN is the vendor primary key.** India mandates GST e-invoicing above Rs 5 Cr turnover; every B2B invoice gets an Invoice Reference Number. Vendor identity resolves on a legal identifier, so we skip fuzzy company-name matching entirely.
- **`procurement_mode` matters.** Most Indian D2C brands use contract manufacturers who often buy packaging. Every brand-SKU edge carries `direct` | `cm_embedded` | `unknown`. Direct-buy gets bundling; CM-embedded gets rate-benchmarking.
- **Quotes expire** (typically 15-30 days). Value only exists inside the validity window. Expiry pressure is a first-class signal.
- **Packaging costs are up 15-25%** in 2026 on crude-linked inputs. Live margin pressure.
- **Quick commerce multiplies SKUs** — dark stores stock 2,000-3,000 items and favour sub-500g packs, so brands run q-commerce ranges *plus* D2C *plus* retail. The naming problem compounds.

---

## 6. Real brands to use in the data

Use the actual Think9 CPG cluster — this is a credibility signal:

**SuperYou** (protein snacks), **Goodbug** (gut health), **Panchamrit** (wellness gummies), **Neude** (milk-based beauty), **Beauty by Bie** (personal care)

Do **not** use Amar Chitra Katha, Tinkle, Broadway, or Food Stories — those are publishing IP and retail formats, and they don't source packaging.

---

## 7. Architecture the prototype implements

```
L0  INGEST        -> raw artifacts with provenance
L1  EXTRACTION    -> LineItem candidates, per-field confidence, source-span citation
L2  RESOLUTION    -> LineItem -> CanonicalSKU        [HITL GATE 1]
L3  SPEC GRAPH    -> the compounding asset
L4  OPPORTUNITY   -> 5 detectors, always-on
L5  BRIEF         -> negotiation packet for a human
L6  DECISION      -> human approves                  [GATES 2 & 3]
```

**Confidence routing at L1:** >=0.90 auto-advance, 0.60-0.90 human review queue, <0.60 reject to human.

**Three human gates:** (1) new canonical SKU creation — prevents graph pollution, the highest-cost error; (2) spend recommendation; (3) vendor-facing communication. The agent **never commits spend**.

---

## 8. Repo layout

```
prototype/
  data/quotes/          12 synthetic vendor quotes, mixed formats
  data/seed/            canonical SKU registry, vendor master, historical POs
  loom/
    models.py           LineItem, CanonicalSKU, Vendor, Quote, Opportunity
    normalize.py        attribute normalization
    extract.py          format-specific parsers
    resolve.py          <- the differentiator
    graph.py            SQLite spec graph
    opportunities.py    5 detectors
    brief.py            negotiation brief generator
  run_demo.py
  requirements.txt
  README.md
```

Full build spec in `docs/PROTOTYPE_SPEC.md`. **Read it before starting.**

---

## 9. Style

- Clear over clever. A reviewer reads this for five minutes.
- Type hints and dataclasses throughout.
- Normalization and tolerance rules must be **explicit and inspectable**, not buried in regex soup — that's exactly what a reviewer will poke at.
- Comments explain *why*, not *what*.
- No `print` scattered through logic; reporting belongs in the reporting layer.

---

## 10. Definition of done

- [ ] `python run_demo.py` runs clean on a **fresh clone with no API key**
- [ ] Output shows five names collapsing into one canonical SKU
- [ ] The 48ml near-miss does **not** merge
- [ ] Gate 1 queue visibly holds items for human approval
- [ ] Ranked opportunities with rupee savings
- [ ] One full negotiation brief printed
- [ ] README runs it in one command
- [ ] Runtime under ~10 seconds

---

## 11. Context files in `docs/`

| File | Contains |
|---|---|
| `LOOM_architecture_and_strategy.md` | Full architecture, HITL gates, failure modes, 30-day roadmap, metrics |
| `Think9_research_brief.md` | Company research — portfolio, leadership, Office of Optimisation, strategic guidance |
| `Think9_market_context_brief.md` | MOQ economics, GST e-invoicing, contract manufacturing, quick commerce |
| `EXECUTION_PLAN.md` | Timeline, deliverables, cut lines |
| `PROTOTYPE_SPEC.md` | **The detailed build spec — start here** |
| `260808_T9 Challenge_v1.pdf` | The original assignment |

---

## 12. Things NOT to do

- Do not correct Think9's "30+ brands" figure. Public evidence says ~11-14, but that's their framing. Frame as *"built at 11 brands, designed for 30+."*
- Do not mention Future Group or the Biyani family retail history anywhere.
- Do not add infrastructure the scale doesn't justify.
- Do not make the demo resolve everything perfectly — plant and show failures.
- Do not let the agent commit spend or contact vendors, even in simulation.
- Do not build a web UI. Console output plus optional HTML report only.
