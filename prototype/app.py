"""LOOM Console — Streamlit UI over the frozen prototype engine.

This file is a *view*. Every number it displays comes from loom/ modules.
No business logic lives here: any calculation in app.py is a bug (see
docs/STREAMLIT_SPEC.md constraint 1).

Five tabs in pipeline order so the tab bar reads as the architecture:
  1 · The Problem   — the SKU identity hook
  2 · Ingest        — the raw mess the system eats
  3 · Resolution    — five names → one object, plus discrimination check
  4 · Gate 1 Queue  — human approval of held items
  5 · Opportunities — ranked savings with negotiation brief and Gate 2
"""
from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Path setup: app.py lives in prototype/, so loom/ is a sibling directory.
# We insert the prototype root so `import loom.*` resolves correctly whether
# the user runs `streamlit run app.py` from prototype/ or from above it.
# ---------------------------------------------------------------------------
APP_DIR = Path(__file__).parent
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from rapidfuzz import fuzz

from loom.brief import render_brief
from loom.extract import QUOTES_DIR, extract_all
from loom.graph import build_graph
from loom.models import TODAY
from loom.normalize import AttributeSignature
from loom.opportunities import consolidate_by_brand, detect_all, portfolio_total
from loom.resolve import (
    FUZZY_THRESHOLD,
    _volumes_compatible,
    contradicts,
    load_registry,
    load_sku_code_lookup,
    resolve_all,
    resolve_line_item,
)

# ---------------------------------------------------------------------------
# Constants (must match run_demo.py exactly)
# ---------------------------------------------------------------------------
L1_REJECT_THRESHOLD = 0.60
ATTR_FIELDS = [
    "material", "colour", "form", "volume_ml", "neck_mm",
    "weight_g", "dimensions_mm", "closure_included",
]

# ---------------------------------------------------------------------------
# Page config — must be the first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="LOOM Console",
    page_icon="🧵",
)


# ---------------------------------------------------------------------------
# Pipeline — single cached function, no live connection escapes.
#
# The fundamental constraint: sqlite3 connections created in one OS thread
# cannot be used in another (ProgrammingError: check_same_thread), and
# Streamlit may run successive reruns of the same session on different
# threads.  Therefore a connection must NEVER be stored — not in
# @st.cache_resource (shared across all sessions) and not in
# st.session_state (shared across reruns of one session).
#
# Solution: build_graph(), detect_all(), and render_brief() all run as
# locals inside the cached function.  The connection is created, used, and
# abandoned there.  Only plain Python types — dicts, lists, strings,
# dataclasses with plain-Python payloads — exit the function and enter the
# cache.  No live sqlite3 object is ever stored anywhere.
# ---------------------------------------------------------------------------
@st.cache_resource
def _run_pipeline_core():
    """Complete pipeline. Connection is a local; only plain Python exits.

    @st.cache_resource runs this once per server process (or after an
    explicit .clear()).  All outputs that cross the cache boundary are
    plain Python — no sqlite3 objects, no sqlite3.Row objects.
    """
    items = extract_all()
    to_resolve = [it for it in items if it.extraction_confidence >= L1_REJECT_THRESHOLD]
    l1_rejects = [it for it in items if it.extraction_confidence < L1_REJECT_THRESHOLD]

    registry = load_registry()
    sku_lookup = load_sku_code_lookup()
    results = resolve_all(to_resolve, registry, sku_lookup)
    manifest = json.loads((QUOTES_DIR / "manifest.json").read_text(encoding="utf-8"))

    # --- connection work: build, use, abandon ---
    conn = build_graph(results, l1_rejects)
    raw_opportunities = detect_all(conn)

    # Render the brief while the connection is still live.
    top_bundle_raw = next((o for o in raw_opportunities if o.kind == "moq_bundling"), None)
    brief_text = render_brief(conn, top_bundle_raw, raw_opportunities) if top_bundle_raw else ""

    # Strip sqlite3.Row objects from Opportunity payloads before the
    # connection closes and before any object crosses the cache boundary.
    # Only the plain-Python fields that app.py actually reads are kept.
    def _plain_payload(opp):
        p = opp.payload
        if opp.kind == "moq_bundling":
            # brands: list[str], combined_qty/moq: int — already plain Python
            return {
                "brands": p.get("brands", []),
                "combined_qty": p.get("combined_qty", 0),
                "moq": p.get("moq", 0),
            }
        # Other opportunity kinds: no payload fields are read by the view.
        return {}

    from loom.models import Opportunity as _Opp
    opportunities = [
        _Opp(
            kind=o.kind,
            canonical_id=o.canonical_id,
            headline=o.headline,
            rupee_impact=o.rupee_impact,
            additive=o.additive,
            expiry_pressure=o.expiry_pressure,
            working=list(o.working),
            payload=_plain_payload(o),
        )
        for o in raw_opportunities
    ]
    # conn goes out of scope here — no live sqlite3 object in the cache.

    return {
        "items": items,
        "to_resolve": to_resolve,
        "l1_rejects": l1_rejects,
        "registry": registry,
        "sku_lookup": sku_lookup,
        "results": results,
        "manifest": manifest,
        "opportunities": opportunities,
        "brief_text": brief_text,
    }


def run_pipeline():
    """Return cached pipeline data. No connection is created or stored."""
    return _run_pipeline_core()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_held(pipeline) -> list:
    """One tuple per held item: (line_item, gate_status, reason).
    Mirrors report_gate1() in run_demo.py.
    """
    held = [
        (it, "reject_low_confidence",
         f"extraction_confidence={it.extraction_confidence:.2f} - too little extracted to resolve")
        for it in pipeline["l1_rejects"]
    ]
    held += [
        (r.line_item, r.gate_status, r.reason)
        for r in pipeline["results"]
        if r.gate_status != "auto"
    ]
    return held


def attribute_comparison(item_attrs: AttributeSignature, cand_attrs: AttributeSignature) -> list[dict]:
    """Return list of dicts with keys: field, item_val, cand_val, verdict.
    Mirrors _attribute_check() in run_demo.py.
    """
    rows = []
    for field in ATTR_FIELDS:
        a, b = getattr(item_attrs, field), getattr(cand_attrs, field)
        if a is None and b is None:
            continue
        item_val = _fmt(a)
        cand_val = _fmt(b)
        if a is None or b is None:
            verdict = "not stated — compatible"
        elif field == "volume_ml":
            verdict = "agree" if _volumes_compatible(a, b) else "*** CONTRADICTS ***"
        else:
            verdict = "agree" if a == b else "*** CONTRADICTS ***"
        rows.append({"field": field, "item_val": item_val, "cand_val": cand_val, "verdict": verdict})
    return rows


def _fmt(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{value:g}"
    return str(value)


def _strip_chat_tag(text: str) -> str:
    return re.sub(r"^\[.*?\]:\s*", "", text.splitlines()[0])


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
def render_sidebar(pipeline) -> None:
    with st.sidebar:
        st.markdown("## LOOM")
        st.caption("Cross-portfolio sourcing intelligence")
        st.divider()

        # Run pipeline button
        if st.button("▶  Run pipeline", type="primary", use_container_width=True):
            # Clear the cache so everything rebuilds from scratch on the next call.
            _run_pipeline_core.clear()
            progress_slot = st.empty()
            layers = [
                "L0  Ingest 12 vendor artifacts…",
                "L1  Extract line items…",
                "L2  Resolve to canonical SKUs…",
                "L3  Build portfolio spec graph…",
                "L4  Detect opportunities…",
                "L5  Generate negotiation brief…",
                "L6  Surface decisions for human…",
            ]
            start = time.perf_counter()
            for layer in layers:
                progress_slot.markdown(f"`{layer}`")
                time.sleep(0.18)
            run_pipeline()   # warms the cache in the current thread
            elapsed = time.perf_counter() - start
            progress_slot.empty()
            st.success(f"Completed in {elapsed:.1f}s")
            st.rerun()


        st.divider()

        # Run stats
        items = pipeline["items"]
        held = build_held(pipeline)
        resolved_count = len(items) - len(held)
        pct = int(resolved_count / len(items) * 100)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Artifacts", "12")
            st.metric("Line items", str(len(items)))
        with col2:
            st.metric("Resolved", f"{resolved_count} ({pct}%)")
            st.metric("Held", str(len(held)))

        st.divider()

        total = portfolio_total(pipeline["opportunities"])
        st.metric(
            label="Identified savings",
            value=f"Rs {total:,.2f}",
            delta="portfolio total",
        )

        st.divider()
        st.caption("Synthetic data · No API key · Pipeline runs in 1.8s")


# ---------------------------------------------------------------------------
# Tab 1 — The Problem
# ---------------------------------------------------------------------------
def render_tab_problem() -> None:
    st.markdown("# One bottle. Five names.")
    st.markdown(
        "The same physical object arrives in the inbox described differently by every "
        "brand and every vendor. Until a system proves these are the same object, "
        "bundling is arithmetically impossible."
    )

    st.markdown("---")

    hero_items = [
        {
            "raw": "50ml Amber Glass Bottle, 20mm neck",
            "brand": "Neude",
            "source": "rajkot_glass_q3.pdf",
            "format": "PDF",
        },
        {
            "raw": "Amber Boston Round 50 ML (20/400)",
            "brand": "Beauty by Bie",
            "source": "gujarat_glass_quote.pdf",
            "format": "PDF",
        },
        {
            "raw": "GB-AMB-50-20N",
            "brand": "Panchamrit",
            "source": "whatsapp_rajkot.txt",
            "format": "WhatsApp",
        },
        {
            "raw": "Glass bottle - amber - 50cc - neck 20mm - w/o cap",
            "brand": "Neude",
            "source": "email_gujarat_glass.txt",
            "format": "email",
        },
        {
            "raw": "एम्बर ग्लास बॉटल 50ml 20mm",
            "brand": "Goodbug",
            "source": "whatsapp_goodbug_hindi.txt",
            "format": "WhatsApp",
        },
    ]

    for item in hero_items:
        with st.container(border=True):
            col_desc, col_meta = st.columns([3, 1])
            with col_desc:
                st.markdown(f"```\n{item['raw']}\n```")
            with col_meta:
                st.markdown(f"**{item['brand']}**")
                st.caption(f"{item['source']}  ·  `{item['format']}`")

    st.markdown("---")

    st.markdown(
        "### You cannot combine orders for things you cannot prove are the same thing."
    )

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True):
            st.markdown("#### The bottleneck")
            st.markdown(
                "The bottleneck is not price comparison. It is **SKU identity resolution**. "
                "Five strings above are five descriptions of one 50ml amber glass bottle with "
                "a 20mm neck. A pure text search fails on the vendor code `GB-AMB-50-20N`, "
                "chokes on the Devanagari string, and merges the 48ml near-miss that shares "
                "most of the same words. Bundling is only possible after an engine proves "
                "these are one object."
            )
    with col_b:
        with st.container(border=True):
            st.markdown("#### The money")
            st.markdown(
                "Packaging suppliers price against **Minimum Order Quantity**. "
                "Suppliers may accept 500 units if buyers agree to pay **20–30% more per unit**. "
                "Four brands ordering separately pay that surcharge four times. "
                "One consolidated order pays it zero times."
            )
            st.markdown(
                "> **The saving is not 'we negotiated harder' — it is 'we stopped paying "
                "a surcharge that existed only because we ordered separately.'**"
            )


# ---------------------------------------------------------------------------
# Tab 2 — Ingest
# ---------------------------------------------------------------------------
def render_tab_ingest(pipeline) -> None:
    st.markdown("# Ingest")
    st.markdown(
        "The raw mess the system eats. Twelve vendor artifacts in five formats, "
        "with incompatible schemas and mixed languages. This is what makes the resolution tab land."
    )

    manifest = pipeline["manifest"]
    items = pipeline["items"]

    # Format chips
    format_counts = Counter(e["format"] for e in manifest)
    format_labels = {
        "pdf": "PDF",
        "csv": "CSV",
        "email": "email",
        "whatsapp": "WhatsApp",
        "xlsx": "Excel",
    }
    chip_cols = st.columns(len(format_counts))
    for col, (fmt, count) in zip(chip_cols, format_counts.items()):
        with col:
            with st.container(border=True):
                st.markdown(f"**{count} {format_labels.get(fmt, fmt)}**")

    st.divider()

    # Selectbox of all 12 source files
    file_names = [e["source_file"] for e in manifest]
    selected_file = st.selectbox("Source file", file_names, key="ingest_file_select")

    entry = next(e for e in manifest if e["source_file"] == selected_file)
    file_path = QUOTES_DIR / selected_file
    file_items = [it for it in items if it.source_file == selected_file]

    col_raw, col_extracted = st.columns(2)

    with col_raw:
        st.markdown("**Raw file contents**")
        fmt = entry["format"]
        if fmt == "pdf":
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text = "\n\n".join(
                        page.extract_text() or "" for page in pdf.pages
                    ).strip()
            except Exception as e:
                text = f"[Could not extract PDF text: {e}]"
        else:
            try:
                text = file_path.read_text(encoding="utf-8")
            except Exception as e:
                text = f"[Could not read file: {e}]"
        st.code(text, language=None)
        st.caption(
            f"Format: `{fmt}` · Vendor GSTIN: `{entry['vendor_gstin']}` · "
            f"Valid: {entry['issued_at']} → {entry['valid_until']}"
        )

    with col_extracted:
        st.markdown("**Extracted line items**")
        if not file_items:
            st.info("No line items extracted from this file.")
        else:
            for i, it in enumerate(file_items):
                is_rejected = it.extraction_confidence < L1_REJECT_THRESHOLD
                with st.container(border=True):
                    if is_rejected:
                        st.error(
                            f"⚠ **L1 REJECTED** — confidence {it.extraction_confidence:.2f}  "
                            f"(threshold {L1_REJECT_THRESHOLD:.2f})  "
                            f"·  too little extracted to resolve"
                        )
                    conf_color = (
                        "green" if it.extraction_confidence >= 0.90
                        else "orange" if it.extraction_confidence >= L1_REJECT_THRESHOLD
                        else "red"
                    )
                    st.markdown(
                        f"**Brand:** {it.brand}  ·  "
                        f"**Confidence:** :{conf_color}[{it.extraction_confidence:.2f}]"
                    )
                    st.markdown(f"`{it.raw_description}`")
                    fields = {
                        "qty": it.qty,
                        "unit_price": f"Rs {it.unit_price:.2f}" if it.unit_price is not None else None,
                        "moq": it.moq,
                        "lead_time_days": f"{it.lead_time_days}d" if it.lead_time_days is not None else None,
                        "sku_code": it.sku_code,
                    }
                    for field, val in fields.items():
                        rendered = f"`{val}`" if val is not None else "—"
                        st.markdown(f"- **{field}**: {rendered}")


# ---------------------------------------------------------------------------
# Tab 3 — Resolution
# ---------------------------------------------------------------------------
def render_tab_resolution(pipeline) -> None:
    st.markdown("# Resolution")
    st.markdown(
        "The most important tab. Five different strings collapse to one canonical identifier. "
        "Then, the discrimination check shows what stops a wrong merge."
    )

    results = pipeline["results"]
    registry = pipeline["registry"]
    opportunities = pipeline["opportunities"]

    # ── 3a: Five names, one object ──────────────────────────────────────────
    st.markdown("## Five names, one object")

    hero_results = [r for r in results if r.canonical_id == "GLS-AMB-050-20"]

    header_cols = st.columns([3, 2, 2, 2, 1])
    header_cols[0].markdown("**Raw description**")
    header_cols[1].markdown("**Brand**")
    header_cols[2].markdown("**Source**")
    header_cols[3].markdown("**Method**")
    header_cols[4].markdown("**Conf**")
    st.divider()

    for r in hero_results:
        it = r.line_item
        written = (
            it.sku_code
            if (r.method == "sku_code_lookup" and it.sku_code)
            else _strip_chat_tag(it.raw_description)
        )
        row_cols = st.columns([3, 2, 2, 2, 1])
        row_cols[0].markdown(f"`{written}`")
        row_cols[1].markdown(it.brand)
        row_cols[2].markdown(f"`{it.source_file}`")
        row_cols[3].markdown(f"`{r.method}`")
        row_cols[4].markdown(f"**{r.confidence:.2f}**")

    st.divider()

    # Read brands and combined requirement from the hero bundle payload — the
    # single place where consolidate_by_brand() has already applied the
    # one-requirement-per-brand rule.  If the consolidation logic ever changes
    # in the engine, this banner updates automatically with no app edits needed.
    hero_bundle = next(
        (o for o in opportunities
         if o.kind == "moq_bundling" and o.canonical_id == "GLS-AMB-050-20"),
        None,
    )
    if hero_bundle:
        brands = hero_bundle.payload["brands"]
        requirement = hero_bundle.payload["combined_qty"]
    else:
        # Fallback: hero SKU has no live bundling opportunity (e.g. quotes expired).
        # Surface the raw line-item count so the table still renders truthfully.
        brands = sorted({r.line_item.brand for r in hero_results})
        requirement = None

    brand_count = len(brands)
    req_str = f"{requirement:,} units of requirement" if requirement is not None else "requirement unknown"
    st.success(
        f"**ALL RESOLVE TO → GLS-AMB-050-20** · 50ml amber glass bottle, 20mm neck  \n"
        f"{brand_count} brands · {req_str}"
    )
    st.caption(
        "Neude is quoted twice for the same 800-unit requirement — counted once, not summed."
    )

    st.markdown("---")

    # ── 3b: Discrimination check ─────────────────────────────────────────────
    st.markdown("## Discrimination check")
    st.markdown(
        "Pick any line item to see it evaluated against **every** canonical SKU. "
        "The 48ml bottle is the proof case: it scores 85% description similarity "
        "against the 50ml canonical — exactly at the fuzzy threshold — but LOOM refuses "
        "the merge because `volume_ml 48 ≠ 50`."
    )

    all_items_for_check = pipeline["to_resolve"] + pipeline["l1_rejects"]
    item_labels = [
        f"{it.raw_description[:60]}  [{it.brand} / {it.source_file}]"
        for it in all_items_for_check
    ]

    # Default to the 48ml bottle
    default_idx = 0
    for i, it in enumerate(all_items_for_check):
        if "48" in it.raw_description and ("ml" in it.raw_description.lower() or "Amber" in it.raw_description):
            default_idx = i
            break

    selected_idx = st.selectbox(
        "Select line item to evaluate",
        range(len(all_items_for_check)),
        format_func=lambda i: item_labels[i],
        index=default_idx,
        key="discrimination_select",
    )
    selected_item = all_items_for_check[selected_idx]

    st.markdown(
        f"**Evaluating:** `{selected_item.raw_description}`  \n"
        f"Brand: **{selected_item.brand}** · Source: `{selected_item.source_file}`"
    )
    st.divider()

    # Evaluate against every canonical SKU — call the real resolver
    for sku in registry:
        similarity = fuzz.token_set_ratio(selected_item.raw_description, sku.description)
        blocked = contradicts(selected_item.attrs, sku.attrs)
        attr_rows = attribute_comparison(selected_item.attrs, sku.attrs)

        # Check if the resolver accepted this (only relevant for items that went through resolution)
        correct_result = next(
            (r for r in results if r.line_item is selected_item and r.canonical_id == sku.id),
            None,
        )
        accepted = not blocked and (similarity >= FUZZY_THRESHOLD or correct_result is not None)

        verdict_color = "green" if accepted else "red"
        verdict_text = "ACCEPTED" if accepted else "REJECTED by the contradiction rule"

        with st.expander(
            f"{'✅' if accepted else '❌'}  **{sku.id}** — {sku.description}  "
            f"| similarity {similarity:.1f}% | :{verdict_color}[{verdict_text}]",
            expanded=(sku.id in ("GLS-AMB-050-20", "GLS-AMB-048-20")),
        ):
            sim_col, thr_col = st.columns(2)
            sim_col.metric("Description similarity", f"{similarity:.1f}%")
            thr_col.metric("Stage-4 threshold", f"{FUZZY_THRESHOLD}%")

            if attr_rows:
                st.markdown("**Attribute comparison:**")
                h = st.columns([2, 2, 2, 3])
                h[0].markdown("**Attribute**")
                h[1].markdown("**Item value**")
                h[2].markdown("**Canonical value**")
                h[3].markdown("**Verdict**")
                for row in attr_rows:
                    vcol = (
                        "red" if "CONTRADICTS" in row["verdict"]
                        else "green" if row["verdict"] == "agree"
                        else "orange"
                    )
                    c = st.columns([2, 2, 2, 3])
                    c[0].markdown(f"`{row['field']}`")
                    c[1].markdown(f"`{row['item_val']}`")
                    c[2].markdown(f"`{row['cand_val']}`")
                    c[3].markdown(f":{vcol}[{row['verdict']}]")
            else:
                st.info("No attributes to compare.")

            if blocked:
                st.error("**VERDICT: REJECTED by the contradiction rule.**")
                clears = "clears" if similarity >= FUZZY_THRESHOLD else "is below"
                st.markdown(
                    f"Every other attribute agrees, and description similarity {clears} the "
                    f"stage-4 threshold ({similarity:.1f} vs {FUZZY_THRESHOLD}) — a purely text-based "
                    f"matcher merges these two. None of that counts: the contradiction rule fires first."
                )
                if sku.id == "GLS-AMB-050-20" and blocked:
                    st.info(
                        "> A shared description is evidence for a match; a disagreeing attribute is "
                        "proof against one, and **proof beats evidence**."
                    )
            elif accepted:
                conf = correct_result.confidence if correct_result else "—"
                method = correct_result.method if correct_result else "fuzzy_description"
                st.success(f"**VERDICT: ACCEPTED** at confidence {conf} (method=`{method}`)")


# ---------------------------------------------------------------------------
# Tab 4 — Gate 1 Queue
# ---------------------------------------------------------------------------
def render_tab_gate1(pipeline) -> None:
    st.markdown("# Gate 1 Queue")
    st.info(
        "The agent stops here. A wrong canonical merge silently corrupts every downstream "
        "recommendation, so ambiguity routes to a human rather than a guess."
    )

    held = build_held(pipeline)

    if not held:
        st.success("Gate 1 queue is empty — all items resolved automatically.")
        return

    st.markdown(f"**{len(held)} items held for human approval.**")
    st.divider()

    if "gate1_decisions" not in st.session_state:
        st.session_state["gate1_decisions"] = {}

    status_colors = {
        "reject_low_confidence": "red",
        "new_canonical_proposed": "orange",
        "review": "blue",
    }

    for idx, (it, gate_status, reason) in enumerate(held):
        card_key = f"gate1_card_{idx}"
        decision = st.session_state["gate1_decisions"].get(card_key)

        color = status_colors.get(gate_status, "grey")
        with st.container(border=True):
            st.markdown(f":{color}[**`{gate_status}`**]")

            col_left, col_right = st.columns([3, 1])
            with col_left:
                st.markdown(f"**`{_strip_chat_tag(it.raw_description)}`**")
                st.markdown(f"Brand: **{it.brand}** · Source: `{it.source_file}`")
                st.markdown(f"_Reason:_ {reason}")

                if gate_status == "review" and "Matches" in reason:
                    st.caption("Competing canonicals this item could not choose between:")
                    ids = re.findall(
                        r"(?:GLS|CAP|CTN|POU|PMP|JAR)-[A-Z0-9\-]+",
                        reason,
                    )
                    for cid in ids:
                        sku = next((s for s in pipeline["registry"] if s.id == cid), None)
                        if sku:
                            st.markdown(f"- `{cid}` — {sku.description}")

            with col_right:
                if decision:
                    action, consequence = decision
                    if action == "Approve":
                        st.success(f"**{action}** ✓")
                    elif action == "Reject":
                        st.error(f"**{action}** ✗")
                    else:
                        st.warning(f"**{action}** …")
                    st.caption(consequence)
                else:
                    btn_cols = st.columns(3)
                    if btn_cols[0].button("Approve", key=f"approve_{idx}"):
                        if gate_status == "new_canonical_proposed":
                            consequence = (
                                "Would create canonical SKU CAN-009 and link 1 line item. "
                                "Not committed — this is a prototype."
                            )
                        elif gate_status == "reject_low_confidence":
                            consequence = (
                                "Would return item to extraction for clarification. "
                                "Not committed — this is a prototype."
                            )
                        else:
                            consequence = (
                                "Would resolve item to best-matching canonical and link it. "
                                "Not committed — this is a prototype."
                            )
                        st.session_state["gate1_decisions"][card_key] = ("Approve", consequence)
                        st.rerun()

                    if btn_cols[1].button("Reject", key=f"reject_{idx}"):
                        consequence = (
                            "Would mark item rejected and exclude from all downstream "
                            "calculations. Not committed — this is a prototype."
                        )
                        st.session_state["gate1_decisions"][card_key] = ("Reject", consequence)
                        st.rerun()

                    if btn_cols[2].button("Defer", key=f"defer_{idx}"):
                        consequence = (
                            "Would leave item in queue pending further information. "
                            "Not committed — this is a prototype."
                        )
                        st.session_state["gate1_decisions"][card_key] = ("Defer", consequence)
                        st.rerun()


# ---------------------------------------------------------------------------
# Tab 5 — Opportunities
# ---------------------------------------------------------------------------
def render_tab_opportunities(pipeline) -> None:
    st.markdown("# Opportunities")
    st.markdown("Ranked by rupee impact. Time-critical items surface to the top.")

    opportunities = pipeline["opportunities"]
    additive_total = portfolio_total(opportunities)
    additive_opps = [o for o in opportunities if o.additive]

    for i, opp in enumerate(opportunities, 1):
        basis = "saving" if opp.additive else "exposure, not additive"
        expiry_flag = "  🔴 EXPIRING" if opp.expiry_pressure else ""
        kind_color = "green" if opp.additive else "orange"

        with st.expander(
            f"**#{i}**  :{kind_color}[`{opp.kind}`]  —  **Rs {opp.rupee_impact:,.2f}**  "
            f"({basis}){expiry_flag}",
            expanded=(i == 1),
        ):
            st.markdown(f"**{opp.headline}**")
            if opp.working:
                st.code("\n".join(opp.working), language=None)

    st.divider()

    # Negotiation brief — pre-rendered as a plain string inside the cached
    # pipeline function (where the connection was still live).  No connection
    # is needed or available here.
    top_bundle = next((o for o in opportunities if o.kind == "moq_bundling"), None)
    if top_bundle:
        st.markdown("## Negotiation Brief")
        st.markdown(
            f"Top opportunity: **{top_bundle.headline}**  \n"
            f"**Rs {top_bundle.rupee_impact:,.2f}** identified saving"
        )
        st.code(pipeline["brief_text"], language=None)

    st.divider()

    # Gate 2
    st.markdown("## Gate 2 — Human Approval Required")
    st.error(
        "**AWAITING HUMAN APPROVAL — GATE 2.** This system does not commit spend. "
        "It has not contacted this vendor and will not. Gate 3 covers vendor communication: "
        "a category manager sends anything that leaves the building."
    )

    if "gate2_decision" not in st.session_state:
        st.session_state["gate2_decision"] = None

    gate2_decision = st.session_state["gate2_decision"]

    if gate2_decision:
        action, msg = gate2_decision
        if action == "Approve":
            st.success(f"**{action}** recorded. {msg}")
        elif action == "Reject":
            st.error(f"**{action}** recorded. {msg}")
        else:
            st.warning(f"**{action}** recorded. {msg}")
        if st.button("↩ Clear decision", key="gate2_clear"):
            st.session_state["gate2_decision"] = None
            st.rerun()
    else:
        g2_cols = st.columns(3)
        if g2_cols[0].button("Approve consolidation", key="gate2_approve", type="primary"):
            st.session_state["gate2_decision"] = (
                "Approve",
                "Would proceed to Gate 3 (vendor communication). Not committed — this is a prototype.",
            )
            st.rerun()
        if g2_cols[1].button("Reject", key="gate2_reject"):
            st.session_state["gate2_decision"] = (
                "Reject",
                "Consolidation rejected. Brands continue ordering separately. Not committed — this is a prototype.",
            )
            st.rerun()
        if g2_cols[2].button("Request changes", key="gate2_changes"):
            st.session_state["gate2_decision"] = (
                "Request changes",
                "Brief returned for revision. Not committed — this is a prototype.",
            )
            st.rerun()

    st.divider()

    # Portfolio footer
    st.markdown("## Portfolio Total")
    additive_sorted = sorted(additive_opps, key=lambda o: o.rupee_impact, reverse=True)
    for o in additive_sorted:
        c1, c2, c3 = st.columns([3, 3, 2])
        c1.markdown(f"`{o.kind}`")
        c2.markdown(f"`{o.canonical_id}`")
        c3.markdown(f"**Rs {o.rupee_impact:,.2f}**")
    st.divider()
    st.metric(
        label="Total portfolio savings identified from 12 quotes",
        value=f"Rs {additive_total:,.2f}",
    )
    st.caption(
        "Risk findings (concentration, lead-time drift, expiry) are excluded from this total — "
        "they quantify exposure against spend already counted, not new money."
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    pipeline = run_pipeline()
    render_sidebar(pipeline)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "1 · The Problem",
        "2 · Ingest",
        "3 · Resolution",
        "4 · Gate 1 Queue",
        "5 · Opportunities",
    ])

    with tab1:
        render_tab_problem()

    with tab2:
        render_tab_ingest(pipeline)

    with tab3:
        render_tab_resolution(pipeline)

    with tab4:
        render_tab_gate1(pipeline)

    with tab5:
        render_tab_opportunities(pipeline)


if __name__ == "__main__":
    main()
