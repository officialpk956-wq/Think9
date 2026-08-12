"""Attribute extraction from free-text packaging descriptions.

Each attribute has its own small, inspectable function rather than one
regex blob, so every rule can be audited independently. Nothing here is
tuned against the demo data — it implements docs/PROTOTYPE_SPEC.md section
5 directly, written before a single quote file existed.

Never infer: a field the text doesn't state stays None. Downstream,
resolve.py treats None as "compatible with anything" — that is a
resolution-stage decision, not a normalization one.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

# Hindi/Hinglish -> English. Applied before every other rule so downstream
# regexes only ever see English tokens. Minimum viable map per spec.
HINDI_TOKENS = {
    "एम्बर": "amber",
    "ग्लास": "glass",
    "बॉटल": "bottle",
    "बोतल": "bottle",
    "ढक्कन": "cap",
    "डिब्बा": "carton",
    "पाउच": "pouch",
    "सफेद": "white",
    "जार": "jar",
}

# material vs colour are separate lookups even though "amber glass" contains
# both words in one phrase - order-independent extraction, not sequential
# parsing, is what makes material=glass/colour=amber both land correctly.
MATERIAL_TOKENS = {
    "glass": "glass",
    "pet": "PET",
    "hdpe": "HDPE",
    "pp": "PP",
    "kraft": "kraft",
    "bopp": "BOPP",
    "laminate": "laminate",
}

COLOUR_TOKENS = {
    "amber": "amber",
    "white": "white",
    "clear": "clear",
    "natural": "natural",
    "transparent": "clear",
}

FORM_TOKENS = {
    "bottle": "bottle",
    "jar": "jar",
    "closure": "cap",
    "cap": "cap",
    "pump": "pump",
    "carton": "carton",
    "box": "carton",
    "label": "label",
    "pouch": "pouch",
}

_CLOSURE_EXCLUDED_RE = re.compile(r"\bw/o\s*cap\b|\bwithout\s*cap\b|\bexcl\.?\s*closure\b", re.I)
_CLOSURE_INCLUDED_RE = re.compile(r"\bwith\s*cap\b", re.I)

# ml/cc are 1:1; L/ltr scale by 1000. gm/g is deliberately NOT folded into
# volume here (unlike the spec's literal wording) - a 100g pouch is a fill
# weight, not a liquid volume, and treating grams as ml via a 1:1 density
# assumption would silently corrupt the pouch/carton attribute signature.
# Weight gets its own field instead; see AttributeSignature.weight_g.
_VOLUME_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(ml|cc|ltr|l)\b", re.I)
_WEIGHT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:gm|g)\b", re.I)

# Neck/closure diameter. Checked in priority order: an explicit "neck 20mm"
# beats a bare "20mm" elsewhere in the string. /400 and -400 are
# thread-finish designations (e.g. continuous-thread family 400), not part
# of the diameter, so the neck regexes stop at the number before the slash.
_NECK_EXPLICIT_RE = re.compile(r"neck\s*(\d+(?:\.\d+)?)\s*mm?\b", re.I)
_NECK_MM_NECK_RE = re.compile(r"(\d+(?:\.\d+)?)\s*mm\s*neck\b", re.I)
_NECK_THREAD_RE = re.compile(r"(\d+(?:\.\d+)?)\s*[/-]\s*\d{3}\b")
_NECK_N_SUFFIX_RE = re.compile(r"(\d+(?:\.\d+)?)N\b")
_NECK_MM_GENERIC_RE = re.compile(r"(\d+(?:\.\d+)?)\s*mm\b", re.I)

_DIMENSIONS_RE = re.compile(r"(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)", re.I)


@dataclass(frozen=True)
class AttributeSignature:
    material: Optional[str] = None
    colour: Optional[str] = None
    form: Optional[str] = None
    volume_ml: Optional[float] = None
    neck_mm: Optional[float] = None
    weight_g: Optional[float] = None
    dimensions_mm: Optional[str] = None
    closure_included: Optional[bool] = None


def _translate_hindi(text: str) -> str:
    for hindi, english in HINDI_TOKENS.items():
        text = text.replace(hindi, english)
    return text


def _token_lookup(text: str, table: dict[str, str]) -> Optional[str]:
    for token, canonical in table.items():
        if re.search(rf"\b{re.escape(token)}\b", text):
            return canonical
    return None


def _extract_volume(text: str) -> Optional[float]:
    m = _VOLUME_RE.search(text)
    if not m:
        return None
    value, unit = float(m.group(1)), m.group(2).lower()
    return value * 1000 if unit in ("l", "ltr") else value


def _extract_weight(text: str) -> Optional[float]:
    m = _WEIGHT_RE.search(text)
    return float(m.group(1)) if m else None


def _extract_neck(text: str, dimensions: Optional[str]) -> Optional[float]:
    for pattern in (_NECK_EXPLICIT_RE, _NECK_MM_NECK_RE, _NECK_THREAD_RE, _NECK_N_SUFFIX_RE):
        m = pattern.search(text)
        if m:
            return float(m.group(1))
    if dimensions:
        # A WxHxD carton spec has no neck. Without this guard the generic
        # "Nmm" fallback below misreads "90x90x120mm"'s last number as one.
        return None
    m = _NECK_MM_GENERIC_RE.search(text)
    return float(m.group(1)) if m else None


def _extract_dimensions(text: str) -> Optional[str]:
    m = _DIMENSIONS_RE.search(text)
    return f"{m.group(1)}x{m.group(2)}x{m.group(3)}" if m else None


def _extract_closure(text: str) -> Optional[bool]:
    if _CLOSURE_EXCLUDED_RE.search(text):
        return False
    if _CLOSURE_INCLUDED_RE.search(text):
        return True
    return None


def extract_attributes(raw_description: str) -> AttributeSignature:
    """Pull a packaging AttributeSignature out of one free-text description."""
    text = _translate_hindi(raw_description).lower()
    dimensions = _extract_dimensions(text)
    return AttributeSignature(
        material=_token_lookup(text, MATERIAL_TOKENS),
        colour=_token_lookup(text, COLOUR_TOKENS),
        form=_token_lookup(text, FORM_TOKENS),
        volume_ml=_extract_volume(text),
        neck_mm=_extract_neck(text, dimensions),
        weight_g=_extract_weight(text),
        dimensions_mm=dimensions,
        closure_included=_extract_closure(text),
    )
