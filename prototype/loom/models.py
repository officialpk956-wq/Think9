"""Core data model for the LOOM prototype.

L0-L2 flow: a Quote (one vendor artifact) contains LineItems (extracted
candidates). resolve.py links each LineItem to a CanonicalSKU or holds it
for Gate 1. See docs/PROTOTYPE_SPEC.md for the full field-level spec.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Optional

from loom.normalize import AttributeSignature

# The demo's "now". Pinned rather than date.today() so quote validity
# windows, expiry pressure and the 90-day history stay meaningful whenever
# a reviewer happens to clone this - a demo whose quotes have all silently
# expired proves nothing.
TODAY = date(2026, 8, 11)


@dataclass
class Vendor:
    gstin: str
    name: str
    supplies: list[str]


@dataclass
class LineItem:
    """One extracted candidate row from a vendor artifact (L1 output)."""

    raw_description: str
    qty: Optional[int]
    unit_price: Optional[float]
    moq: Optional[int]          # vendor-quoted MOQ for this line, as stated
    lead_time_days: Optional[int]
    brand: str
    vendor_gstin: str
    source_file: str
    source_format: str
    sku_code: Optional[str] = None          # vendor's own product code, if present
    extraction_confidence: float = 1.0       # L1 confidence, drives confidence routing
    attrs: AttributeSignature = field(default_factory=AttributeSignature)


@dataclass
class Quote:
    id: str
    vendor_gstin: str
    issued_at: date
    valid_until: date
    source_file: str
    source_format: str
    line_items: list[LineItem]


@dataclass
class CanonicalSKU:
    id: str
    description: str
    attrs: AttributeSignature
    moq: int


@dataclass
class Opportunity:
    """One detector finding (L4 output).

    `additive` separates real savings from risk exposure: bundling and
    price-outlier rupees are money recoverable now and sum into the
    portfolio total. Concentration, lead-time drift and expiry pressure
    quantify exposure or urgency against spend already counted elsewhere -
    summing them would inflate the headline figure by double counting.
    """

    kind: str
    canonical_id: str
    headline: str
    rupee_impact: float
    additive: bool
    expiry_pressure: bool = False
    working: list[str] = field(default_factory=list)  # the arithmetic, shown not hidden
    payload: dict[str, Any] = field(default_factory=dict)
