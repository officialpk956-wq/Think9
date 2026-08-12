"""L2 resolution: map each LineItem to a CanonicalSKU, or hold it for Gate 1.

Four-stage cascade per docs/PROTOTYPE_SPEC.md section 6:
  1. vendor SKU-code lookup                                  (0.95)
  2/3. attribute-signature match, exact or within tolerance   (0.90-1.00)
  4. fuzzy description similarity, no contradiction            (0.70-0.85)
  otherwise -> propose new canonical, halt, queue for Gate 1

Stages 2 and 3 share one function (`_signature_candidates`) because they
share the same contradiction check and differ only in whether the volume
tolerance band was needed to reach a match - that's a confidence input,
not a different rule.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rapidfuzz import fuzz

from loom.models import CanonicalSKU, LineItem
from loom.normalize import AttributeSignature

SEED_DIR = Path(__file__).parent.parent / "data" / "seed"

FUZZY_THRESHOLD = 85
AMBIGUITY_MARGIN = 5  # candidates within this many fuzzy points of the top score tie, rather than win


@dataclass
class ResolutionResult:
    line_item: LineItem
    canonical_id: Optional[str]
    confidence: float
    method: str
    gate_status: str  # "auto" | "review" | "new_canonical_proposed"
    reason: str = ""  # shown in the Gate 1 queue


def load_registry(seed_dir: Path = SEED_DIR) -> list[CanonicalSKU]:
    raw = json.loads((seed_dir / "canonical_skus.json").read_text(encoding="utf-8"))
    return [CanonicalSKU(id=r["id"], description=r["description"], moq=r["moq"], attrs=AttributeSignature(**r["attrs"])) for r in raw]


def load_sku_code_lookup(seed_dir: Path = SEED_DIR) -> dict[tuple[str, str], str]:
    raw = json.loads((seed_dir / "sku_code_lookup.json").read_text(encoding="utf-8"))
    return {(r["vendor_gstin"], r["sku_code"]): r["canonical_id"] for r in raw}


def _volumes_compatible(v1: float, v2: float) -> bool:
    """Exact match required at/under 100ml; +/-2% tolerance above it.

    This is what keeps a 50ml and a 48ml bottle from ever being treated as
    the same volume no matter how similar their descriptions read - and
    it's the reason GLS-AMB-048-20 never merges into GLS-AMB-050-20 below.
    """
    if v1 == v2:
        return True
    if v1 <= 100 or v2 <= 100:
        return False
    return abs(v1 - v2) / max(v1, v2) <= 0.02


# ---------------------------------------------------------------------------
# THE CONTRADICTION RULE
#
# If any two non-None attributes disagree, the match fails - full stop,
# regardless of how similar the free-text descriptions read. A shared
# description is evidence FOR a match; a disagreeing attribute is proof
# AGAINST one, and proof beats evidence. Every stage below (signature match
# and the fuzzy fallback) is filtered through this gate before anything
# else runs.
#
# This is the single rule that stops "48ml Amber Glass Bottle, 20mm neck"
# (94% textually similar to the 50ml canonical - same words, same neck)
# from ever merging into it: volume=48 vs volume=50 are both explicitly
# stated, they disagree, and no amount of shared vocabulary overrides that.
#
# The inverse matters just as much: a None attribute contradicts nothing.
# normalize.py never infers a missing field, so treating "unstated" as
# "different" would punish an under-specified description instead of
# correctly flagging it as ambiguous (see the "bottle - 50 - amber" case,
# which ties three canonicals precisely because it states too little to
# rule any of them out).
# ---------------------------------------------------------------------------
def contradicts(item: AttributeSignature, candidate: AttributeSignature) -> bool:
    if item.material and candidate.material and item.material != candidate.material:
        return True
    if item.colour and candidate.colour and item.colour != candidate.colour:
        return True
    if item.form and candidate.form and item.form != candidate.form:
        return True
    if item.dimensions_mm and candidate.dimensions_mm and item.dimensions_mm != candidate.dimensions_mm:
        return True
    if item.weight_g is not None and candidate.weight_g is not None and item.weight_g != candidate.weight_g:
        return True
    if item.closure_included is not None and candidate.closure_included is not None and item.closure_included != candidate.closure_included:
        return True
    if item.neck_mm is not None and candidate.neck_mm is not None and item.neck_mm != candidate.neck_mm:
        return True  # neck is exact, always - no tolerance band
    if item.volume_ml is not None and candidate.volume_ml is not None and not _volumes_compatible(item.volume_ml, candidate.volume_ml):
        return True
    return False


def _match_score(item: AttributeSignature, candidate: AttributeSignature) -> tuple[int, bool]:
    """How many attributes both sides state and agree on, and whether the
    volume tolerance band (vs. an exact hit) was needed for any of them."""
    pairs = [
        (item.material, candidate.material),
        (item.colour, candidate.colour),
        (item.form, candidate.form),
        (item.dimensions_mm, candidate.dimensions_mm),
        (item.weight_g, candidate.weight_g),
        (item.closure_included, candidate.closure_included),
        (item.neck_mm, candidate.neck_mm),
    ]
    score = sum(1 for a, b in pairs if a is not None and b is not None and a == b)
    tolerance_used = False
    if item.volume_ml is not None and candidate.volume_ml is not None:
        score += 1
        tolerance_used = item.volume_ml != candidate.volume_ml
    return score, tolerance_used


def _signature_candidates(item: LineItem, registry: list[CanonicalSKU]) -> list[tuple[CanonicalSKU, int, bool]]:
    """Every canonical the item's attributes don't contradict, with a match score."""
    candidates = []
    for sku in registry:
        if contradicts(item.attrs, sku.attrs):
            continue
        score, tolerance_used = _match_score(item.attrs, sku.attrs)
        candidates.append((sku, score, tolerance_used))
    return candidates


def _fuzzy_candidates(item: LineItem, registry: list[CanonicalSKU], allowed_ids: set[str]) -> list[tuple[CanonicalSKU, float]]:
    scored = [
        (sku, fuzz.token_set_ratio(item.raw_description, sku.description))
        for sku in registry if sku.id in allowed_ids
    ]
    scored = [pair for pair in scored if pair[1] >= FUZZY_THRESHOLD]
    return sorted(scored, key=lambda pair: -pair[1])


def resolve_line_item(item: LineItem, registry: list[CanonicalSKU], sku_lookup: dict) -> ResolutionResult:
    # Stage 1: vendor SKU-code lookup - a direct key hit, no ambiguity possible.
    if item.sku_code:
        canonical_id = sku_lookup.get((item.vendor_gstin, item.sku_code))
        if canonical_id:
            return ResolutionResult(item, canonical_id, 0.95, "sku_code_lookup", "auto")

    # Stages 2/3: attribute-signature match, contradiction-filtered.
    candidates = _signature_candidates(item, registry)
    if candidates:
        top_score = max(score for _, score, _ in candidates)
        tied = [c for c in candidates if c[1] == top_score]
        if top_score >= 2:
            if len(tied) > 1:
                names = ", ".join(sku.id for sku, _, _ in tied)
                return ResolutionResult(item, None, 0.0, "signature_ambiguous", "review",
                                         f"Matches {len(tied)} canonicals equally well ({names}) - too few stated attributes to distinguish them")
            sku, _, tolerance_used = tied[0]
            confidence = 0.90 if tolerance_used else 1.00
            method = "tolerance_signature" if tolerance_used else "exact_signature"
            return ResolutionResult(item, sku.id, confidence, method, "auto")
        # Exactly one shared attribute is too weak to trust alone - confirm
        # (or reject) with fuzzy text similarity before deciding anything.
    non_contradicted_ids = {sku.id for sku in registry if not contradicts(item.attrs, sku.attrs)}

    # Stage 4: fuzzy description similarity, restricted to canonicals the
    # attribute signature hasn't already ruled out - text similarity never
    # overrides a contradiction, it only breaks ties among what's left.
    fuzzy = _fuzzy_candidates(item, registry, non_contradicted_ids)
    if fuzzy:
        top_sku, top_score = fuzzy[0]
        tied_fuzzy = [c for c in fuzzy if top_score - c[1] <= AMBIGUITY_MARGIN]
        if len(tied_fuzzy) > 1:
            names = ", ".join(sku.id for sku, _ in tied_fuzzy)
            return ResolutionResult(item, None, 0.0, "fuzzy_ambiguous", "review",
                                     f"Fuzzy match ties between {names} - too close to call automatically")
        confidence = 0.70 + min(top_score - FUZZY_THRESHOLD, 15) / 15 * 0.15
        return ResolutionResult(item, top_sku.id, round(confidence, 2), "fuzzy_description", "auto")

    return ResolutionResult(item, None, 0.0, "no_match", "new_canonical_proposed",
                             "No existing canonical SKU matches this description without contradiction")


def resolve_all(items: list[LineItem], registry: Optional[list[CanonicalSKU]] = None,
                 sku_lookup: Optional[dict] = None) -> list[ResolutionResult]:
    registry = registry if registry is not None else load_registry()
    sku_lookup = sku_lookup if sku_lookup is not None else load_sku_code_lookup()
    return [resolve_line_item(item, registry, sku_lookup) for item in items]
