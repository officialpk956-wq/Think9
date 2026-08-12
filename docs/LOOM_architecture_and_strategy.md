# LOOM
### A Cross-Portfolio Sourcing Intelligence Layer for Think9

*Think9 AI & Intelligence Challenge — Track 2: Cross-Portfolio Supply Chain & Sourcing Agent*

---

## 1. The Problem & The Opportunity

### 1.1 The bottleneck, stated precisely

Think9 operates 30+ brands. Each brand's team sources independently: they email vendors, receive quotes, negotiate, and issue POs. This is the natural and correct thing for each brand to do in isolation.

It is also the single largest destroyer of portfolio-level margin.

The reason is a specific, mechanical one:

> **Think9 has 30x the buying power of any single brand, but 1x the negotiating leverage — because at the moment a brand negotiates, nobody in the building can see what the other 29 brands are paying for the same physical object.**

This is not a discipline problem. It is not solved by "better process" or a shared spreadsheet, and it will get monotonically worse as the portfolio grows. It is an information problem with three compounding properties:

**(a) The data arrives in formats no database can hold.** Vendor quotes come as PDFs on letterhead, photos of printed quotes sent over WhatsApp, email bodies with prices in prose, and Excel files with merged cells and footnotes. Roughly none of it is structured.

**(b) The data expires.** A vendor quote is typically valid 15–30 days. By the time a quarterly procurement review could surface a bundling opportunity, the quotes it would have bundled have lapsed. Insight that arrives after expiry has zero value.

**(c) The same object has 30 different names.** This is the crux, and section 1.2 is devoted to it.

### 1.2 The actual hard problem: SKU identity resolution

Consider one physical object — a 50ml amber glass bottle with a 20mm neck finish.

| Brand | How it appears in their quote |
|---|---|
| Brand A | "50ml Amber Glass Bottle, 20mm neck" |
| Brand B | "Amber Boston Round 50 ML (20/400)" |
| Brand C | "GB-AMB-50-20N" *(vendor's internal SKU code)* |
| Brand D | "Glass bottle – amber – 50cc – neck 20mm – w/o cap" |
| Brand E | "एम्बर ग्लास बॉटल 50ml" *(vendor quote in Hindi)* |

These are the same object. Until a system can *prove* they are the same object, bundling is impossible — you cannot consolidate volume across line items you cannot match.

**This is the wedge.** Every other capability in this system — extraction, price comparison, risk flagging, negotiation prep — is downstream of, and worthless without, canonical SKU resolution. It is also precisely the task that is intractable for deterministic software (the naming space is unbounded and adversarially inconsistent) and tractable for a modern language model working against a structured spec graph.

### 1.3 Why an agent, not a script or a hire

The brief asks us to earn the AI. Three tests:

**Could a script do this?** No. A script requires a fixed input schema. There is no fixed schema — there are ~200 vendors each with their own quote layout, and new vendors onboard continuously. Any regex-based extractor is obsolete within a quarter.

**Could a data-entry team do this?** Technically yes, and this is what most companies actually do. But the economics fail at Think9's velocity: normalizing ~24,000 quote line-items per year and continuously re-checking them against a live spec graph is roughly 3–4 FTE of tedious, high-error work. More decisively, humans cannot do it *fast enough* — the value is only realized inside the 15-day quote validity window, and a human queue introduces exactly the latency that kills it.

**Why agentic specifically, rather than a single model call?** Because the work requires a loop, not a transform:
- Extraction confidence varies per field, and low-confidence fields must trigger a *clarification action* (query the vendor, query the brand team) rather than a silent guess.
- Resolution requires reasoning over specs with tolerances and then *deciding whether to create a new canonical entity or match an existing one* — a stateful judgment against a growing graph.
- Opportunity detection runs continuously against changing state (new quotes, expiring quotes, shifting lead times), not on request.

That is an agent: perceive → reason → act → observe, against persistent state.

### 1.4 The opportunity, sized

The business case does not rest on negotiating harder. It rests on a structural surcharge that exists purely because brands order separately.

**The MOQ penalty.** Packaging suppliers price against minimum order quantities. Industry reporting on 2026 procurement states it plainly: *suppliers may accept 500 units if buyers agree to pay 20–30% more per unit.* Ordering below MOQ is not a negotiation failure — it is a published surcharge.

Think9's brands are individually small by design. SuperYou targets ₹40–50 Cr over 18–24 months; early-stage brands order components in hundreds, not tens of thousands. **Most Think9 brands are therefore paying the sub-MOQ premium on most shared components, most of the time.**

Five brands each ordering 500 units of the same bottle pay that penalty five times. One consolidated order of 2,500 units clears the MOQ and pays it zero times.

> **Eliminating the sub-MOQ premium on shared components is a 20–30% unit-cost reduction on those components — before a single rupee of negotiating leverage is applied.**

Leverage from consolidated volume is then upside on top, not the core claim. This matters because it makes the case *arithmetic* rather than dependent on assumptions about anyone's negotiating skill.

**The timing is not incidental.** Crude-linked input costs are up 20–25% against pre-conflict levels and FMCG packaging costs specifically are up 15–20%. Margin defence is a live problem this quarter, not a theoretical efficiency gain.

**The behaviour is already validated.** Indian SMEs are actively renegotiating supplier terms through pooled procurement to achieve flexible MOQs. The practice works; it is simply being done manually, deal by deal, catching only the opportunities someone happens to notice. LOOM does not invent pooled procurement — it makes it continuous and exhaustive.

Two second-order benefits, both larger than they first appear:
- **Vendor risk becomes visible.** When multiple brands unknowingly depend on one vendor for one component, that is a portfolio-level single point of failure nobody has ever seen on a screen.
- **The next brand starts at portfolio-best pricing on day one** instead of negotiating up from scratch. This is the compounding asset, and it is the reason this system belongs at the centre rather than inside any brand.

### 1.5 Why the problem compounds

Two forces are expanding the naming space simultaneously.

**Portfolio growth.** Think9 is building toward 30+ brands. Every brand added multiplies the number of independent naming conventions in play.

**Quick-commerce SKU proliferation.** Dark stores stock only 2,000–3,000 SKUs against 1 lakh+ on Amazon, and favour compact formats under 500g. Brands launching q-commerce-exclusive SKUs see 20–30% higher repeat purchase, so every brand now maintains a q-commerce pack range *in addition to* its D2C and retail ranges. More pack sizes means more components, more vendor quotes, more names for the same objects.

The resolution problem therefore gets structurally harder every quarter it is deferred. Building the canonical graph at 11 brands is cheap. Building it at 30 brands across three channel-specific pack ranges is a migration project.

**This is the "why now."** Not that the opportunity is large — that it is currently at its smallest it will ever be, and the cost of capturing it only rises.

---

## 2. System Architecture & Workflow

### 2.1 Design principles

Four constraints shaped every decision below.

1. **The agent never spends money.** It recommends; a human commits. Non-negotiable.
2. **Extraction never invents.** The model may only extract values present in the source, and every extracted field carries a pointer back to its source span. If a field is absent, it is `null` — never inferred.
3. **Graph pollution is the highest-cost failure.** One bad canonical merge silently corrupts every downstream recommendation. Merges are gated and reversible.
4. **Build for 24k quotes/year, not 24M.** This is a small-data problem wearing a big-data costume. Postgres is sufficient. Resisting infrastructure theater is itself a design decision.

### 2.2 The layers

```
┌──────────────────────────────────────────────────────────────────┐
│  L0  INGEST                                                      │
│  sourcing@think9 inbox · WhatsApp Business API · file drop ·     │
│  ERP/PO export · vendor portal                                   │
│  → every artifact stored immutably with provenance + timestamp   │
└────────────────────────────┬─────────────────────────────────────┘
                             │  raw artifact
┌────────────────────────────▼─────────────────────────────────────┐
│  L1  EXTRACTION AGENT                          [vision + text]   │
│  PDF / image / email / spreadsheet → LineItem candidates         │
│  Per-field confidence · source-span citation · null-if-absent    │
│                                                                  │
│  Confidence routing:                                             │
│    ≥0.90  auto-advance                                           │
│    0.60–0.90  → human review queue                               │
│    <0.60  → reject to human, or agent queries vendor             │
└────────────────────────────┬─────────────────────────────────────┘
                             │  structured LineItem
┌────────────────────────────▼─────────────────────────────────────┐
│  L2  RESOLUTION AGENT                    ◆ HITL GATE 1           │
│  Map LineItem → Canonical SKU                                    │
│  · attribute normalization (50cc = 50ml = 50 ML)                 │
│  · material / colour / finish canonicalization                   │
│  · dimensional tolerance rules                                   │
│  · fuzzy + embedding match on residual description               │
│  Match ≥ threshold → link.  Below → propose NEW canonical SKU,   │
│  which a human must approve before it enters the graph.          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│  L3  PORTFOLIO SPEC GRAPH            ← THE COMPOUNDING ASSET     │
│                                                                  │
│   CanonicalSKU ──quoted_by──▶ Vendor                             │
│        │                        │                                │
│        ├──used_by──▶ Brand      ├──lead_time_history             │
│        ├──price_history         ├──quality_incidents             │
│        └──spec_attributes       └──concentration_exposure        │
│                                                                  │
│  Every resolved quote makes this graph denser and every future   │
│  negotiation better. This is why the system is central.          │
└────────────────────────────┬─────────────────────────────────────┘
                             │  continuous scan
┌────────────────────────────▼─────────────────────────────────────┐
│  L4  OPPORTUNITY AGENT                             [always-on]   │
│  ① Bundling — same canonical SKU, ≥2 brands, quotes co-valid     │
│  ② Price outlier — brand paying >X% above portfolio best         │
│  ③ Vendor concentration — N brands single-sourced on one vendor  │
│  ④ Lead-time drift — vendor's quoted LT trending up vs history   │
│  ⑤ Expiry pressure — bundleable quotes lapsing within 7 days     │
└────────────────────────────┬─────────────────────────────────────┘
                             │  ranked opportunities
┌────────────────────────────▼─────────────────────────────────────┐
│  L5  NEGOTIATION BRIEF GENERATOR                                 │
│  For a selected opportunity, assemble the packet a human takes   │
│  into the call:                                                  │
│   · consolidated volume across participating brands              │
│   · best price ever achieved anywhere in the portfolio           │
│   · this vendor's own pricing history (their floor)              │
│   · BATNA: alternate qualified vendors + their prices            │
│   · lead-time and quality record                                 │
│   · a target price with the reasoning shown                      │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│  L6  HUMAN DECISION LAYER          ◆ GATE 2  ◆ GATE 3           │
│  Category manager approves / rejects / edits.                    │
│  Outcome writes back to L3 → graph learns → next brief improves. │
└──────────────────────────────────────────────────────────────────┘
```

### 2.3 Human-in-the-loop checkpoints

The brief asks for these explicitly, and full autonomy here would be a design error, not a feature. Three gates, each placed where the cost of an unreviewed error is highest:

| Gate | Location | What it prevents | Who |
|---|---|---|---|
| **1 — Canonical creation** | L2 | Graph pollution. A wrong merge silently corrupts every downstream recommendation and is hard to detect after the fact. | Sourcing analyst |
| **2 — Spend recommendation** | L6 | Committing money on a machine judgment. Agent proposes consolidation; human authorizes. | Category manager |
| **3 — Vendor communication** | L6 | Reputational and negotiating-position damage. Agent drafts vendor-facing messages; a human sends them. | Category manager |

Additionally, **confidence routing at L1** is a soft gate: it lets high-confidence extraction flow without human cost while guaranteeing ambiguous data reaches a person. This is what makes the system economical — the human effort scales with *ambiguity*, not with *volume*.

As the graph matures and precision is measured, Gate 1 can be relaxed to spot-audit for high-confidence matches. Gates 2 and 3 should not be relaxed.

### 2.4 The workflow, end to end

1. A vendor emails a PDF quote to `sourcing@think9`. It lands in L0 with provenance.
2. L1 extracts 14 line items. Twelve fields clear 0.90 and advance; two ("neck finish" and one unit ambiguity) route to the review queue.
3. L2 resolves 11 line items to existing canonical SKUs. Three are unrecognized and are proposed as new canonicals — a human approves two and rejects one as a duplicate spelling of an existing entry.
4. L3 absorbs the resolved items: new price points, a lead-time observation, a vendor-brand edge.
5. L4, scanning continuously, notices that canonical SKU `GLS-AMB-050-20` now has co-valid quotes from four brands at four different prices, with the earliest expiring in nine days. It raises a ranked bundling opportunity.
6. L5 assembles the brief: combined volume, portfolio-best price, this vendor's historical floor, two alternate vendors as BATNA, target price with reasoning.
7. A category manager reviews, adjusts the target, and runs the negotiation. The outcome — agreed or not — writes back to L3.
8. The next brief for this SKU is better, because step 7 happened.

Step 8 is the whole thesis.

---

## 3. Proof of Concept

A working Python prototype accompanies this document. It runs end to end on synthetic-but-realistic data with no API keys required.

**What it demonstrates:**
- Ingestion of vendor quotes across deliberately inconsistent formats
- Attribute normalization and canonical SKU resolution across divergent naming
- Detection of cross-brand bundling opportunities with quantified savings
- Vendor concentration and price-outlier flagging
- Generation of a negotiation brief

**What it deliberately does not do:** commit spend, contact vendors, or auto-approve canonical merges. Those are the gated paths, and the prototype stops at each gate by design.

See `README.md` in the prototype directory for run instructions and a walkthrough of the output.

---

## 4. Implementation Plan

### 4.1 Stack

| Layer | Choice | Why this and not the obvious alternative |
|---|---|---|
| Ingest | Gmail API, WhatsApp Business Cloud API, S3 for raw artifacts | Meets vendors where they already are. Forcing vendors onto a portal is a 6-month change-management project that fails. |
| Extraction | Claude (vision) primary; Textract/Tesseract OCR fallback for degraded scans | Vision-native handling of PDFs and photographed quotes removes the brittle OCR→parse chain entirely. |
| Orchestration | Temporal | Not LangGraph. Quotes and negotiations are long-running, span days, and must survive process restarts with exact-once semantics. Durability matters more than graph ergonomics here. |
| Storage | Postgres + pgvector | Not Neo4j. At 24k quotes/year the graph is small; recursive CTEs handle the traversals. Adding a graph DB buys nothing and costs an operational surface. |
| Serving | FastAPI + Streamlit console | Streamlit for the human-gate console specifically because it is buildable in days, and the gates are what must exist by day 30. |
| Eval | Golden set of 200 hand-labelled quote line-items | Extraction field-level F1, resolution precision/recall. Precision is weighted far above recall — a missed match costs an opportunity, a false match corrupts the graph. |

**Scale sanity check:** 30 brands × ~50 sourced SKUs × ~4 vendors × quarterly re-quoting ≈ **24,000 quote line-items per year**. Roughly 100 per working day. At ~$0.02 per extraction that is **~$500/year in inference cost** against a savings target measured in crores. The cost argument is not close, and no distributed-systems infrastructure is warranted.

### 4.2 Thirty-day roadmap to a minimum viable version

Scoped to **packaging components only**, and here is why that is the right wedge: packaging is highly standardized, has the highest cross-brand overlap of any category, represents substantial spend, and — unlike actives, ingredients, or formulations — carries no regulatory or compliance sign-off that would slow the loop. It is the category where the system can prove itself fastest.

| Days | Milestone | Exit criterion |
|---|---|---|
| **1–7** | Ingest + extraction live for packaging. Manual seed of ~150 canonical SKUs from the top 3 brands by spend. | Extraction field-level F1 ≥ 0.90 on the golden set. |
| **8–15** | Resolution agent + spec graph. Backfill 90 days of historical quotes and POs to defeat cold start. | ≥ 80% of packaging spend resolved to canonical SKUs; resolution precision ≥ 0.95. |
| **16–23** | Opportunity agent + first negotiation brief. **Run one real consolidated negotiation.** | One executed bundle with a measured, signed-off rupee saving. |
| **24–30** | Human-gate console, alerting, instrumentation. Measure and publish the baseline. | Quote-to-decision cycle time reported, before vs. after. |

The day-16–23 milestone is the one that matters. A system that produces one real, banked saving in month one earns the right to expand to ingredients, logistics, and services. One that produces a dashboard does not.

### 4.3 Metrics

**North star: quote-to-decision cycle time** — the elapsed time from a quote arriving to a sourcing decision being made. Target: days → hours. This is chosen deliberately because Think9's stated goal is *execution speed*, not cost alone, and because it is the metric that generalizes when this architecture is later applied to other functions.

Supporting metrics:

| Metric | Why it matters |
|---|---|
| **Intra-portfolio price variance for identical canonical SKU** | The purest measure of the problem. Should trend to zero. |
| Canonical coverage (% of spend resolved) | System reach. Gates how much of the portfolio the other metrics even apply to. |
| Realized bundling savings (₹, cumulative) | The banked business case. |
| Vendor concentration index | Portfolio risk that is currently invisible. |
| Extraction F1 / resolution precision | System health. Precision degradation is the early warning for graph pollution. |

### 4.4 Failure modes and mitigations

Stating these is not hedging; an architecture that has not enumerated its failure modes has not been designed.

| Risk | Consequence | Mitigation |
|---|---|---|
| **Hallucinated specifications** | Fabricated attributes enter the graph and propagate silently | Extraction-only prompting with mandatory source-span citation; absent fields are `null`, never inferred |
| **Wrong canonical merge** | Two genuinely different SKUs unified → recommendations built on a false equivalence | HITL Gate 1; all merges reversible with full audit trail; precision weighted above recall in eval |
| **Vendor gaming** | Vendors learn Think9 bundles and inflate base quotes in anticipation | Do not disclose consolidated portfolio volume until commit; maintain and actively use BATNA vendors |
| **Cold start** | Empty graph produces no opportunities, system looks useless in week one | Backfill 90 days of historical POs before go-live (days 8–15) |
| **Over-consolidation** | Single-sourcing a bundled SKU creates a new portfolio-level supply risk | Concentration index is a first-class alert, not an afterthought; briefs surface it alongside savings |
| **Human gate becomes the bottleneck** | Review queue backs up, latency advantage is lost | Confidence routing keeps human effort proportional to ambiguity; queue depth is itself a monitored metric |

---

## 5. Why This Belongs at the Centre

A closing argument, because it is the thing the brief is actually testing.

Most AI proposals help one team do one thing faster. Their value is linear: deploy to 30 brands, get 30 units of value, pay 30 units of cost.

LOOM is different in kind. Every quote any brand receives makes the graph denser, which makes every subsequent negotiation across all other brands better-informed. The 31st brand does not start from zero — it starts with portfolio-best pricing, qualified vendors, and known lead times on day one.

That is superlinear, it only works if the system is central, and it is the specific reason this is an intelligence *layer* rather than a tool.

The architecture also generalizes. Extract from unstructured sources → resolve to canonical entities → build a portfolio graph → detect cross-brand opportunities → route to a human gate. Swap the entity from *component* to *consumer complaint*, *creative asset*, or *decision*, and the same five layers become the Feedback Hub, the Creative Engine, or the Think9 Brain. LOOM is a proof of the pattern as much as a solution to sourcing.
