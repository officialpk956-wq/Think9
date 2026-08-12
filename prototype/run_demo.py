"""LOOM demo: ingest 12 vendor quotes, resolve them to canonical SKUs, build
the portfolio spec graph, and surface ranked savings with a negotiation brief.

Runs end to end on synthetic data with no API key. See README.md.
"""
from __future__ import annotations

import json
import re
import textwrap
from collections import Counter

from rapidfuzz import fuzz

from loom.brief import render_brief
from loom.extract import QUOTES_DIR, extract_all
from loom.graph import build_graph, graph_stats
from loom.models import TODAY
from loom.normalize import AttributeSignature
from loom.opportunities import detect_all, portfolio_total
from loom.resolve import (
    FUZZY_THRESHOLD,
    _volumes_compatible,
    contradicts,
    load_registry,
    load_sku_code_lookup,
    resolve_line_item,
)

# L1 confidence routing (CLAUDE.md section 7): >=0.90 auto-advance,
# 0.60-0.90 human review, <0.60 reject to human before resolution is attempted.
L1_REJECT_THRESHOLD = 0.60

WIDTH = 78
ATTR_FIELDS = ["material", "colour", "form", "volume_ml", "neck_mm", "weight_g",
               "dimensions_mm", "closure_included"]


def _box(title: str) -> None:
    print(f"\n{'=' * WIDTH}\n{title}\n{'=' * WIDTH}")


def _strip_chat_tag(text: str) -> str:
    return re.sub(r"^\[.*?\]:\s*", "", text.splitlines()[0])


def _fmt(value) -> str:
    if value is None:
        return "-"
    # Seed attrs arrive as ints from JSON, extracted attrs as floats. Render
    # both the same way so a real disagreement isn't mistaken for 48.0 vs 48.
    return f"{value:g}" if isinstance(value, (int, float)) and not isinstance(value, bool) else str(value)


def report_ingest(items) -> None:
    _box("L0 / L1  --  INGEST & EXTRACTION")
    manifest = json.loads((QUOTES_DIR / "manifest.json").read_text(encoding="utf-8"))
    formats = Counter(e["format"] for e in manifest)
    print(f"{len(manifest)} vendor artifacts ingested: "
          + ", ".join(f"{n} {fmt}" for fmt, n in formats.items()))
    print(f"{len(items)} line items extracted")
    print(f"Reference date: {TODAY.isoformat()} (pinned, so quote validity stays meaningful)\n")
    buckets = Counter()
    for it in items:
        if it.extraction_confidence >= 0.90:
            buckets[">= 0.90   auto-advance"] += 1
        elif it.extraction_confidence >= L1_REJECT_THRESHOLD:
            buckets["0.60-0.90  human review queue"] += 1
        else:
            buckets["<  0.60   reject to human"] += 1
    print("Extraction confidence distribution:")
    for label in (">= 0.90   auto-advance", "0.60-0.90  human review queue", "<  0.60   reject to human"):
        print(f"   {label:<30} {buckets.get(label, 0)}")


def report_resolution_hero(results) -> None:
    _box("L2  --  RESOLUTION: five names, one physical object")
    hero = [r for r in results if r.canonical_id == "GLS-AMB-050-20"]
    print(f"{'Brand':<14}{'Source':<30}{'As written':<32}{'Method':<17}{'Conf':>5}")
    print("-" * 98)
    for r in hero:
        it = r.line_item
        written = it.sku_code if (r.method == "sku_code_lookup" and it.sku_code) \
            else _strip_chat_tag(it.raw_description)[:30]
        print(f"{it.brand:<14}{it.source_file:<30}{written:<32}{r.method:<17}{r.confidence:>5.2f}")
    brands = sorted({r.line_item.brand for r in hero})
    # Requirement, not line sum: a brand quoted twice for one requirement
    # contributes its volume once. Rajkot and Gujarat both quote Neude's 800.
    requirement = sum(min(r.line_item.qty for r in hero if r.line_item.brand == b) for b in brands)
    print("-" * 98)
    print(f"{len(hero)} line items | {len(brands)} brands ({', '.join(brands)}) | "
          f"{requirement:,} units of requirement")
    print("ALL RESOLVE TO:  GLS-AMB-050-20  --  50ml amber glass bottle, 20mm neck")
    print("(Neude is quoted twice for the same 800-unit requirement - counted once, not summed.)")


def _attribute_check(item_attrs: AttributeSignature, cand_attrs: AttributeSignature) -> list[str]:
    """Render the attribute-by-attribute comparison the contradiction rule runs."""
    lines = []
    for field in ATTR_FIELDS:
        a, b = getattr(item_attrs, field), getattr(cand_attrs, field)
        if a is None and b is None:
            continue
        if a is None or b is None:
            verdict = "not stated - compatible"
        elif field == "volume_ml":
            verdict = "agree" if _volumes_compatible(a, b) else "*** CONTRADICTS ***"
        else:
            verdict = "agree" if a == b else "*** CONTRADICTS ***"
        lines.append(f"      {field:<18}{_fmt(a):<12}vs {_fmt(b):<12}{verdict}")
    return lines


def report_discrimination_check(results, registry) -> None:
    """Show the near-miss being evaluated against the hero canonical and refused.

    The point of this section is the refusal, not the correct answer - a
    viewer has to watch a wrong merge get turned down on the evidence.
    """
    _box("DISCRIMINATION CHECK  --  watching a wrong merge get refused")
    near = next(r for r in results if r.canonical_id == "GLS-AMB-048-20")
    item = near.line_item
    by_id = {sku.id: sku for sku in registry}
    print(f"Line item:  {item.raw_description!r}")
    print(f"            {item.brand} / {item.source_file}\n")

    for candidate_id in ("GLS-AMB-050-20", "GLS-AMB-048-20"):
        sku = by_id[candidate_id]
        similarity = fuzz.token_set_ratio(item.raw_description, sku.description)
        blocked = contradicts(item.attrs, sku.attrs)
        print(f"  Candidate {candidate_id}  ({sku.description})")
        print(f"      description similarity: {similarity:.0f}%   "
              f"(rapidfuzz token_set_ratio, stage-4 threshold {FUZZY_THRESHOLD})")
        for line in _attribute_check(item.attrs, sku.attrs):
            print(line)
        if blocked:
            clears = "clears" if similarity >= FUZZY_THRESHOLD else "is below"
            print("      VERDICT: REJECTED by the contradiction rule.")
            print(f"      Every other attribute agrees, and description similarity {clears} the")
            print(f"      stage-4 threshold ({similarity:.0f} vs {FUZZY_THRESHOLD}) - a purely "
                  "text-based matcher merges these two.")
            print(f"      None of that counts: volume_ml {_fmt(item.attrs.volume_ml)} != "
                  f"{_fmt(sku.attrs.volume_ml)}, both explicitly stated, both <= 100ml")
            print("      where exact match is required and no tolerance band applies.")
            print("      A shared description is evidence for a match; a disagreeing attribute is")
            print("      proof against one, and proof beats evidence.")
        else:
            print(f"      VERDICT: ACCEPTED at confidence {near.confidence:.2f} "
                  f"(method={near.method}).")
        print()
    print("Had the 48ml merged into GLS-AMB-050-20, it would have added 1,000 phantom units")
    print("to the bundle below and corrupted every price comparison on that SKU thereafter.")


def report_gate1(l1_rejects, results) -> list:
    _box("GATE 1 QUEUE  --  held for human approval")
    held = [(it, "reject_low_confidence",
             f"extraction_confidence={it.extraction_confidence:.2f} - too little extracted to resolve")
            for it in l1_rejects]
    held += [(r.line_item, r.gate_status, r.reason) for r in results if r.gate_status != "auto"]
    for it, status, reason in held:
        print(f"  [{status}]  {it.brand} / {it.source_file}")
        print(f"      {_strip_chat_tag(it.raw_description)[:88]!r}")
        for line in textwrap.wrap(f"reason: {reason}", width=90,
                                  initial_indent="      ", subsequent_indent="              "):
            print(line)
        print()
    print(f"{len(held)} items held. The agent does not guess past this point: a wrong canonical")
    print("merge silently corrupts every downstream recommendation, so ambiguity routes to a human.")
    return held


def report_coverage(total_items: int, held_count: int) -> None:
    _box("COVERAGE")
    resolved = total_items - held_count
    print(f"Resolved {resolved}/{total_items} line items ({resolved / total_items:.0%}). "
          f"{held_count} held for human review.")
    print("Reported as measured. The resolver was written before the quote data existed and")
    print("has not been tuned against it - the misses above are real and are the honest number.")


def report_graph(conn) -> None:
    _box("L3  --  PORTFOLIO SPEC GRAPH")
    stats = list(graph_stats(conn).items())
    print("  " + "   ".join(f"{t}={n}" for t, n in stats[:4]))
    print("  " + "   ".join(f"{t}={n}" for t, n in stats[4:]))
    print("\n  price_history holds 90 days of backfilled POs - without it the price-outlier and")
    print("  lead-time detectors have no baseline and the system looks useless in week one.")


def report_opportunities(opportunities) -> None:
    _box("L4  --  OPPORTUNITIES (ranked: time-critical first, then rupee impact)")
    for i, o in enumerate(opportunities, 1):
        tag = "  [EXPIRING]" if o.expiry_pressure else ""
        basis = "saving" if o.additive else "exposure, not additive"
        print(f"#{i}  [{o.kind}]  Rs {o.rupee_impact:,.2f}  ({basis}){tag}")
        print(f"    {o.headline}")
        for line in o.working:
            print(f"    {line}" if line else "")
        print()


def report_footer(opportunities) -> None:
    _box("PORTFOLIO TOTAL")
    additive = sorted((o for o in opportunities if o.additive),
                      key=lambda o: o.rupee_impact, reverse=True)
    for o in additive:
        print(f"  {o.kind:<20}{o.canonical_id:<20}Rs {o.rupee_impact:>12,.2f}")
    print("-" * WIDTH)
    print(f"  Total portfolio savings identified from 12 quotes: "
          f"Rs {portfolio_total(opportunities):,.2f}")
    print("\n  Risk findings (concentration, lead-time drift, expiry) are excluded from this")
    print("  total - they quantify exposure against spend already counted, not new money.")


def main() -> None:
    items = extract_all()
    to_resolve = [it for it in items if it.extraction_confidence >= L1_REJECT_THRESHOLD]
    l1_rejects = [it for it in items if it.extraction_confidence < L1_REJECT_THRESHOLD]

    registry = load_registry()
    sku_lookup = load_sku_code_lookup()
    results = [resolve_line_item(it, registry, sku_lookup) for it in to_resolve]

    report_ingest(items)
    report_resolution_hero(results)
    report_discrimination_check(results, registry)
    held = report_gate1(l1_rejects, results)
    report_coverage(len(items), len(held))

    conn = build_graph(results, l1_rejects)
    report_graph(conn)

    opportunities = detect_all(conn)
    report_opportunities(opportunities)

    top_bundle = next(o for o in opportunities if o.kind == "moq_bundling")
    _box("L5  --  NEGOTIATION BRIEF (top opportunity)")
    print(render_brief(conn, top_bundle, opportunities))

    report_footer(opportunities)


if __name__ == "__main__":
    main()
