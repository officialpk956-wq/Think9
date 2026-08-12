# LOOM — prototype

A cross-portfolio sourcing intelligence layer. Weaves separate brand procurement
threads into one fabric so that volume that is invisible today becomes bundleable.

**Think9 AI & Intelligence Challenge — Track 2: Cross-Portfolio Supply Chain & Sourcing Agent.**

---

## Run it

```bash
pip install -r requirements.txt
python run_demo.py
```

**No API key. No network. No services to start.** Runs in about 1.5 seconds.

The demo data ships in `data/`. To regenerate it: `python generate_data.py`.
To run the self-checks: `python tests/test_resolve.py && python tests/test_opportunities.py`.

A verbatim capture of the full console output is committed at
[`output/demo_run.txt`](output/demo_run.txt), so the figures below can be quoted
without re-running anything.

---

## What you will see

| # | Section | What it proves |
|---|---|---|
| 1 | **Ingest & extraction** | 12 vendor artifacts in 5 formats → 27 line items, with confidence routing |
| 2 | **Resolution** | Five different names across 4 brands and 4 channels collapse to one canonical SKU |
| 3 | **Discrimination check** | A 48ml bottle is evaluated against the 50ml canonical and **refused**, on screen |
| 4 | **Gate 1 queue** | 4 items held for a human, each with the reason it was held |
| 5 | **Coverage** | 23/27 (85%), reported as measured |
| 6 | **Spec graph** | SQLite, 7 tables, 90 days of backfilled price history |
| 7 | **Opportunities** | 5 detectors, ranked, every rupee figure showing its own arithmetic |
| 8 | **Negotiation brief** | The full packet for the top opportunity, ending at Gate 2 |

The headline: **five names, one bottle, 2,550 units, MOQ 2,500 — Rs 13,255** that
exists only because nobody could previously see that four brands were buying the
same object.

---

## The actual hard problem

Not price comparison. **SKU identity resolution.**

The same 50ml amber glass bottle arrives as:

```
50ml Amber Glass Bottle, 20mm neck          (Rajkot PDF,       Neude)
Amber Boston Round 50 ML (20/400)           (Gujarat PDF,      Beauty by Bie)
GB-AMB-50-20N                               (WhatsApp,         Panchamrit)
Glass bottle - amber - 50cc - neck 20mm     (email prose,      Neude)
एम्बर ग्लास बॉटल 50ml 20mm                    (WhatsApp Hindi,   Goodbug)
```

Until a system *proves* those are one object, bundling is arithmetically impossible.

### The contradiction rule

The single most important piece of logic in this repo, in `loom/resolve.py`:

> **If any two non-`None` attributes disagree, the match fails — regardless of
> description similarity.**

`48ml Amber Glass Bottle, 20mm neck` scores **85** on `token_set_ratio` against
the 50ml canonical, which *clears* the stage-4 fuzzy threshold of 85. Material,
colour, form and neck all agree. A text-similarity matcher merges them.

LOOM refuses, because `volume_ml` 48 ≠ 50, both are explicitly stated, and below
100ml volume must match exactly with no tolerance band. A shared description is
evidence *for* a match; a disagreeing attribute is proof *against* one, and proof
beats evidence. The demo shows this rejection happening rather than asserting it.

The inverse matters equally: a `None` attribute contradicts nothing. Normalization
never infers a missing field, so an under-specified line (`"bottle - 50 - amber"`)
ties three canonicals and routes to a human instead of being silently guessed.

---

## Architecture

Code maps to the L0–L6 layers in `docs/LOOM_architecture_and_strategy.md`:

| Layer | Module | Does |
|---|---|---|
| **L0** Ingest | `data/quotes/` + `manifest.json` | Raw artifacts with provenance (vendor, brand, dates) |
| **L1** Extraction | `loom/extract.py` | Format-specific parsers → `LineItem` + per-item confidence |
| — | `loom/normalize.py` | Free text → `AttributeSignature`. Never infers absent fields |
| **L2** Resolution | `loom/resolve.py` | 4-stage cascade → canonical SKU. **Gate 1** |
| **L3** Spec graph | `loom/graph.py` | SQLite, 7 tables, the compounding asset |
| **L4** Opportunity | `loom/opportunities.py` | 5 always-on detectors, ranked by rupee impact |
| **L5** Brief | `loom/brief.py` | The packet a human takes into the call |
| **L6** Decision | *(human)* | **Gates 2 & 3.** The agent never commits spend |

### Resolution cascade

| Stage | Rule | Confidence |
|---|---|---|
| 1 | Vendor SKU-code lookup | 0.95 |
| 2 | Exact attribute-signature match | 1.00 |
| 3 | Signature match within dimensional tolerance | 0.90 |
| 4 | Fuzzy description ≥85 **and** no contradicting attribute | 0.70–0.85 |
| — | Otherwise → propose new canonical, halt, **queue for Gate 1** | — |

Stages 2–4 are all filtered through the contradiction rule first.

### The three human gates

1. **Canonical creation** (L2) — prevents graph pollution, the highest-cost error.
2. **Spend recommendation** (L6) — the agent proposes; a human authorizes.
3. **Vendor communication** (L6) — the agent drafts; a human sends.

Confidence routing at L1 is a soft fourth gate: human effort scales with
*ambiguity*, not with volume.

---

## Real vs. scaffolded

Being precise about this, because overclaiming is the fastest way to lose credibility.

**There is no API key, and no degraded mode.** The deterministic path *is* the
demo — every number in the output above is computed locally by the code in
`loom/`, with no model call anywhere in the pipeline. Nothing is stubbed out
waiting for a key, and nothing runs better if you supply one. A reviewer clones
this and sees the whole system.

**Genuinely real — this is the load-bearing work:**

- **`normalize.py`** — every attribute rule written from packaging-domain first
  principles *before* the quote data existed, and deliberately not tuned afterwards.
  Two bugs it exposed during testing (a carton's `90x90x120mm` leaking into
  `neck_mm`; a vendor's own name tag leaking a material token out of WhatsApp
  transcripts) were fixed as logic errors, not papered over.
- **`resolve.py`** — the full cascade, the contradiction rule, tolerance bands,
  and ambiguity detection. Nothing here is faked or hardcoded to the demo.
- **`opportunities.py`** — all five detectors compute from the graph. Every rupee
  figure prints its inputs, the penalty tier applied, and the result, so the
  arithmetic can be checked by hand rather than taken on trust. The headline
  Rs 31,672.60 is a sum of six audited findings, not an estimate.
- **`graph.py`** — real SQLite with real joins; the detectors query it, so it is
  load-bearing rather than decorative.

**Scaffolded, and honestly so:**

- **The data is synthetic.** Twelve quote files generated by `generate_data.py`,
  using real Think9 brand names and realistic-format GSTINs. No real vendor
  pricing appears anywhere.
- **The extraction parsers are format-specific, not a general vision model.**
  This is the most important boundary in the repo. `extract.py` is `pdfplumber`,
  `csv`, `openpyxl` and regex — five hand-written parsers that know what a PDF
  table, a CSV and a WhatsApp transcript look like. The formats vary deliberately
  (5 formats, 6 mutually incompatible column schemas, prose pricing, Hinglish,
  Devanagari) and column matching is keyword-based rather than positional, so the
  parsers face genuine heterogeneity rather than a fixed schema. But they are not
  general: **a photographed quote, a scanned fax or a novel layout would defeat
  them.** Production L1 is Claude-with-vision precisely because that space is
  unbounded. What the prototype proves is L2 onward — that once line items exist,
  identity resolution and opportunity detection work. It does not prove that
  extraction generalizes, and does not claim to.
- **Brand and vendor identity come from `manifest.json`**, i.e. L0 provenance,
  rather than being parsed out of document bodies. A real ingest pipeline
  attaches this at the inbox/channel level, which is what the manifest stands in for.
- **The sub-MOQ penalty tiers are a model**, not observed vendor data — grounded
  in 2026 industry reporting that suppliers accept ~500 units for 20–30% more per
  unit. The tiers are declared as one constant in `opportunities.py` and shown in
  the output so the assumption is inspectable and arguable.
- **`TODAY` is pinned** to 2026-08-11 so quote validity windows stay meaningful
  whenever this is cloned. A demo whose quotes have all silently expired proves nothing.

**Competing quotes are not additive demand.** Several vendors quoting the same
brand for the same object are competing offers on *one* requirement. The bundling
and price-outlier detectors therefore consolidate by `(brand, canonical_sku)`:
each brand contributes its requirement once, at the best live price available to
it, and the losing quotes are retained as that brand's BATNA rather than as extra
units. Where a brand's competing quotes disagree on quantity, the smaller is
taken — a consolidated volume must never overstate real demand.

This matters because it is the easiest way to fake a large number. On the hero
SKU, Neude is quoted by both Rajkot and Gujarat for the same 800 units; summing
the raw quote lines would report 3,350 units instead of the real 2,550, and would
inflate the saving by roughly a third. `tests/test_opportunities.py` locks this
behaviour down. The bundle clears MOQ on deduplicated demand (2,550 vs 2,500),
not because the double-count was left in.

---

## Scale

~30 brands × ~50 sourced SKUs × ~4 vendors × quarterly re-quoting ≈ **24,000 quote
line-items per year**, about 100 per working day.

This is a small-data problem wearing a big-data costume. SQLite here, Postgres in
production. No Kafka, no Spark, no vector database, no distributed anything.
Dependencies: `rapidfuzz`, `pdfplumber`, `reportlab`, `openpyxl`. Refusing
infrastructure theatre is a design decision, not an omission.

---

## Layout

```
prototype/
  data/quotes/         12 synthetic vendor quotes, 5 formats + manifest
  data/seed/           canonical SKUs, vendors, brands, sku-code lookup,
                       procurement modes, 90 days of price history
  loom/
    models.py          LineItem, CanonicalSKU, Vendor, Quote, Opportunity
    normalize.py       attribute extraction from free text
    extract.py         format-specific parsers
    resolve.py         <- the differentiator
    graph.py           SQLite spec graph
    opportunities.py   5 detectors
    brief.py           negotiation brief
  tests/test_resolve.py        resolution cascade + contradiction rule
  tests/test_opportunities.py  the money path: no double-counted volume
  output/demo_run.txt          verbatim console output, committed
  generate_data.py
  run_demo.py
```
