# LOOM Prototype — Build Spec

> Read `CLAUDE.md` first for project context. This document is the implementation detail.

**Target:** ~5.5 hours of build. Runs in under 10 seconds. No API key required.

---

## 0. Build order

Steps 1-4 are the critical path. If anything slips, it slips there.

| # | Module | Est. |
|---|---|---|
| 1 | Data generator + 12 quote files | 45m |
| 2 | `models.py` + `normalize.py` | 30m |
| 3 | `extract.py` | 60m |
| 4 | `resolve.py` <- the differentiator | 75m |
| 5 | `graph.py` | 30m |
| 6 | `opportunities.py` | 45m |
| 7 | `brief.py` + console report | 45m |
| 8 | README + fresh-clone test | 30m |

**Critical process note:** write `normalize.py` from packaging-domain first principles *before* generating the quote files, and do not tune it afterwards to make the demo pass. If it resolves 26 of 30 items, report 26 of 30. A resolver with visible misses is more credible than a perfect one, and tuning-to-fit is exactly what a reviewer will suspect.

**Checkpoint:** stop after step 4 and show the resolution output before building the graph and opportunity layers. The hero table and the near-miss must be verified before anything is built on top of them.

---

## 1. Canonical SKU registry

Eight canonical SKUs. Seed file: `data/seed/canonical_skus.json`.

| Canonical ID | Description | Key attributes |
|---|---|---|
| `GLS-AMB-050-20` | 50ml amber glass bottle, 20mm neck | glass, amber, bottle, 50ml, neck 20mm, no closure |
| `GLS-AMB-100-24` | 100ml amber glass bottle, 24mm neck | glass, amber, bottle, 100ml, neck 24mm |
| `GLS-AMB-048-20` | **48ml** amber glass bottle, 20mm neck | glass, amber, bottle, 48ml, neck 20mm <- **near-miss, must NOT merge with 050** |
| `CAP-PP-20-WHT` | 20mm white PP screw cap | PP, white, closure, 20mm |
| `PMP-LOT-24-WHT` | 24mm white lotion pump | PP, white, pump, 24mm |
| `JAR-PET-200-70` | 200ml PET jar, 70mm mouth | PET, clear, jar, 200ml, 70mm |
| `CTN-KRF-090090120` | Kraft carton 90x90x120mm | kraft, carton, 90x90x120 |
| `POU-STD-100-ZIP` | 100g stand-up zip pouch | laminate, pouch, 100g, zip |

`GLS-AMB-048-20` exists solely to prove the engine discriminates. It must remain unmerged in the final output, and the report must say so explicitly.

---

## 2. Brands and vendors

**Brands** (`data/seed/brands.json`): SuperYou, Goodbug, Panchamrit, Neude, Beauty by Bie.

**Vendors** (`data/seed/vendors.json`) — 6, each with a realistic-format GSTIN as primary key:

| Vendor | GSTIN | Supplies |
|---|---|---|
| Rajkot Glass Works | 24AAACR5055K1Z5 | glass bottles |
| Shree Packaging Industries | 27AABCS1429B1ZQ | caps, pumps, jars |
| Gujarat Glass & Containers | 24AACCG9862P1ZX | glass bottles |
| Mumbai Flexipack | 27AAECM4521N1ZK | pouches, labels |
| Everest Cartons | 27AADCE7734L1ZR | cartons |
| Deccan Closures | 29AAGCD2287M1ZP | caps, pumps |

---

## 3. Cross-brand overlap map

This determines which opportunities the demo surfaces. Design it deliberately.

| Canonical SKU | Brands buying | Vendors quoting | Opportunity |
|---|---|---|---|
| `GLS-AMB-050-20` | Neude, Beauty by Bie, Panchamrit | Rajkot, Gujarat Glass | **hero bundle** — 3 brands, 4 quotes, 5 names |
| `CAP-PP-20-WHT` | Neude, Beauty by Bie, Panchamrit, Goodbug | Shree, Deccan | 4-brand bundle |
| `CTN-KRF-090090120` | all 5 | Everest | 5-brand bundle + **concentration risk** (sole source) |
| `POU-STD-100-ZIP` | SuperYou, Goodbug | Mumbai Flexipack | 2-brand bundle, one CM-embedded |
| `JAR-PET-200-70` | Neude only | Shree | no bundle — **price outlier** vs history |
| `PMP-LOT-24-WHT` | Beauty by Bie, Neude | Shree, Deccan | bundle + **lead-time drift** on Shree |
| `GLS-AMB-100-24` | Panchamrit | Gujarat Glass | single brand, no action |
| `GLS-AMB-048-20` | SuperYou | Rajkot | **near-miss control** |

Plant **2-3 items that fail resolution** (genuinely ambiguous descriptions, e.g. `"bottle - 50 - amber"` with no neck spec) so the Gate 1 queue has real contents.

---

## 4. Quote files — 12 files, ~30 line items

`data/quotes/`. Each file carries: vendor, date issued, `valid_until`, line items with description / qty / unit price / MOQ / lead time.

| # | File | Format | Notes |
|---|---|---|---|
| 1 | `rajkot_glass_q3.pdf` | PDF letterhead | generate with reportlab |
| 2 | `gujarat_glass_quote.pdf` | PDF, different layout | |
| 3 | `shree_packaging_rate_list.pdf` | PDF, table-heavy | |
| 4 | `everest_cartons.csv` | CSV — cols: `item,qty,rate,moq` | |
| 5 | `mumbai_flexipack.csv` | CSV — cols: `Description,Order Qty,Price/Unit,Min Order` | **incompatible schema** |
| 6 | `deccan_closures.csv` | CSV — cols: `sku_code,product_desc,units,inr_per_unit` | **third schema** |
| 7 | `email_gujarat_glass.txt` | email body | prices in prose: *"we can offer at Rs 18.50 per piece for 5000 pcs"* |
| 8 | `email_shree_revised.txt` | email body | revised rates mid-thread |
| 9 | `whatsapp_rajkot.txt` | chat transcript | partial specs, *"same as last time"* |
| 10 | `whatsapp_deccan.txt` | chat transcript | Hinglish |
| 11 | `whatsapp_panchamrit_hindi.txt` | chat transcript | Devanagari descriptions |
| 12 | `neude_vendor_compare.xlsx` | Excel | merged cells, footnotes |

**Hero SKU appears as** (this is the demo):

| Brand | Source | As written | Price |
|---|---|---|---|
| Neude | Rajkot PDF | `50ml Amber Glass Bottle, 20mm neck` | Rs 22.00 @ 500 |
| Beauty by Bie | Gujarat PDF | `Amber Boston Round 50 ML (20/400)` | Rs 21.50 @ 600 |
| Panchamrit | WhatsApp Rajkot | `GB-AMB-50-20N` | Rs 23.00 @ 400 |
| Neude | Email Gujarat | `Glass bottle - amber - 50cc - neck 20mm - w/o cap` | Rs 20.75 @ 800 |
| Panchamrit | WhatsApp Hindi | `एम्बर ग्लास बॉटल 50ml 20mm` | Rs 22.50 @ 450 |

MOQ for this SKU: **2,500 units.** Every brand is below it. Combined: 2,750 — clears it. That is the demo.

---

## 5. `normalize.py` — attribute extraction

Write these rules from domain first principles. Keep them declarative and inspectable — a reviewer will read this file.

**Volume:** `ml | ML | mL | cc | CC | L | ltr | gm | g` -> normalize to ml. `50cc == 50ml`. `0.05L == 50ml`.

**Neck/closure size:** `20mm`, `20 mm`, `20/400`, `neck 20`, `20N`, `20-400` -> `20`. (The `/400` and `-400` suffixes are thread-finish designations, not part of the diameter.)

**Material:** `amber glass | glass | PET | PP | HDPE | kraft | BOPP | laminate` -> canonical token. Note `amber glass` must resolve material=`glass`, colour=`amber` — order matters.

**Colour:** `amber | white | clear | natural | transparent` (map `transparent`->`clear`).

**Form:** `bottle | jar | cap | closure | pump | carton | box | label | pouch`.

**Closure included:** detect `w/o cap`, `without cap`, `excl. closure`, `with cap` -> boolean or `None`.

**Hindi/Hinglish map** (minimum viable):

```
एम्बर -> amber
ग्लास -> glass
बॉटल -> bottle
बोतल -> bottle
ढक्कन -> cap
डिब्बा -> carton
पाउच -> pouch
सफेद -> white
जार  -> jar
```

Output: an `AttributeSignature` dataclass with `None` for anything absent. **Never infer a missing attribute.**

---

## 6. `resolve.py` — the differentiator

Four-stage cascade, returning `(canonical_id, confidence, method)`:

| Stage | Rule | Confidence |
|---|---|---|
| 1 | Vendor SKU-code lookup table hit | 0.95 |
| 2 | Exact attribute-signature match | 1.00 |
| 3 | Signature match within dimensional tolerance | 0.90 |
| 4 | Fuzzy description similarity (rapidfuzz `token_set_ratio` >= 85) **AND** no contradicting attribute | 0.70-0.85 |
| — | Otherwise | -> **propose new canonical, halt, queue for Gate 1** |

### Tolerance rules — the crux

- **Volume:** exact match required for values <=100ml. `50ml != 48ml`. Above 100ml, +/-2% tolerance.
- **Neck:** exact. Always.
- **Material:** exact. Never tolerate.
- **Colour:** exact, except `None` is compatible with anything (absent != different).
- **Contradiction rule:** if any two non-`None` attributes disagree, the match fails **regardless of description similarity.** This is what stops 48ml merging into 50ml when the text is 94% similar.

That last rule is the single most important line of logic in the prototype. Comment it clearly.

### Output

`ResolutionResult` with `line_item`, `canonical_id | None`, `confidence`, `method`, `gate_status` in `{auto, review, new_canonical_proposed}`.

---

## 7. `graph.py` — SQLite spec graph

Tables:

```sql
canonical_sku(id, description, attrs_json, moq, created_at, approved_by)
vendor(gstin, name, created_at)
brand(id, name)
quote(id, vendor_gstin, brand_id, issued_at, valid_until, source_file, source_format)
line_item(id, quote_id, raw_description, qty, unit_price, moq, lead_time_days,
          canonical_id, resolution_confidence, resolution_method, gate_status)
brand_sku_edge(brand_id, canonical_id, procurement_mode)   -- direct | cm_embedded | unknown
price_history(canonical_id, vendor_gstin, brand_id, unit_price, qty, observed_at)
```

Seed `price_history` with ~90 days of synthetic historical POs — this is the cold-start backfill, and it's what makes price-outlier and lead-time-drift detection possible.

---

## 8. `opportunities.py` — five detectors

### 1. MOQ bundling (the money)

For each canonical SKU with >=2 brands holding co-valid quotes:

```python
current_total = sum(qty_i * price_i for each brand)   # each below MOQ, each penalised
combined_qty  = sum(qty_i)
if combined_qty >= moq:
    base_price   = min(price_i)          # best price observed in portfolio
    consolidated = combined_qty * base_price
    savings      = current_total - consolidated
```

Model the penalty tiered by distance below MOQ: <25% of MOQ -> 30% premium; 25-50% -> 25%; 50-75% -> 20%; 75-100% -> 12%. Derive `base_price` by removing the penalty from the best observed price, and **show the working in the output** — inputs, tier applied, result. Nothing may be a black box.

### 2. Price outlier

Brand paying >15% above portfolio-best for the same canonical SKU within the validity window.

### 3. Vendor concentration

Vendor sole-sourcing >=3 brands on any canonical SKU -> portfolio single point of failure.

### 4. Lead-time drift

Current quoted lead time >20% above that vendor's trailing mean from `price_history`.

### 5. Expiry pressure

Bundleable quotes lapsing within 7 days. **Rank this to the top when triggered** — it's time-critical.

All opportunities ranked by rupee impact, not date.

---

## 9. `brief.py` — negotiation brief

For the top opportunity, print the packet a human takes into the call:

- Canonical SKU + spec
- Participating brands, quantities, current prices, **procurement mode each**
- Consolidated volume vs MOQ
- Portfolio-best price ever achieved
- This vendor's own historical floor
- **BATNA:** alternate qualified vendors with their prices
- Lead-time and concentration notes
- **Target price, with the reasoning shown**
- Explicit line: `AWAITING HUMAN APPROVAL — Gate 2. This system does not commit spend.`

---

## 10. `run_demo.py` — console report

Sections, in order:

1. **Ingest** — 12 files, formats, N line items, extraction confidence distribution
2. **Resolution** — the hero table: five names -> one canonical SKU, with method and confidence per row
3. **Discrimination check** — explicit callout that `GLS-AMB-048-20` did *not* merge, and why
4. **Gate 1 queue** — items held for human approval, with the reason each was held
5. **Coverage stat** — e.g. `Resolved 27/30 line items (90%). 3 held for human review.`
6. **Opportunities** — ranked, with rupee savings
7. **Negotiation brief** — the top one, in full
8. **Footer** — `Total portfolio savings identified from 12 quotes: Rs X,XX,XXX`

Plain text, box-drawing characters for tables, no colour dependency. Must be readable in a screen recording — that's what the video captures.

---

## 11. README.md

Must contain: one-command run, what the reviewer will see, a short architecture note mapping code to the L0-L6 layers, an explicit statement that the data is synthetic, and a note on what is real vs. scaffolded. **Be honest about the boundary** — claiming more than the code does is the fastest way to lose credibility.

```bash
pip install -r requirements.txt
python run_demo.py
```

---

## 12. Acceptance tests

- [ ] Fresh clone, no API key, one command -> clean run
- [ ] Hero table shows 5 names collapsing to `GLS-AMB-050-20`
- [ ] `GLS-AMB-048-20` does **not** merge, and the report says so
- [ ] Gate 1 queue is non-empty
- [ ] Bundling opportunity shows a rupee figure with the MOQ arithmetic visible
- [ ] Negotiation brief prints in full with the Gate 2 line
- [ ] Runtime < 10s
- [ ] Coverage is reported honestly, including misses
