"""Smallest possible check on the resolution cascade - not a full suite,
just enough that a broken contradiction rule or a broken stage-1 lookup
fails loudly. Run: `python tests/test_resolve.py`.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loom.models import LineItem
from loom.normalize import extract_attributes
from loom.resolve import load_registry, load_sku_code_lookup, resolve_line_item

REGISTRY = load_registry()
SKU_LOOKUP = load_sku_code_lookup()


def _item(description, vendor_gstin="24AAACR5055K1Z5", sku_code=None):
    return LineItem(
        raw_description=description, qty=100, unit_price=10.0, moq=None, lead_time_days=None,
        brand="TestBrand", vendor_gstin=vendor_gstin, source_file="test", source_format="test",
        sku_code=sku_code, attrs=extract_attributes(description),
    )


def test_hero_merge():
    for desc in ["50ml Amber Glass Bottle, 20mm neck", "Amber Boston Round 50 ML (20/400)",
                 "Glass bottle - amber - 50cc - neck 20mm - w/o cap"]:
        result = resolve_line_item(_item(desc), REGISTRY, SKU_LOOKUP)
        assert result.canonical_id == "GLS-AMB-050-20", f"{desc!r} -> {result.canonical_id}"
        assert result.gate_status == "auto"


def test_near_miss_does_not_merge():
    result = resolve_line_item(_item("48ml Amber Glass Bottle, 20mm neck"), REGISTRY, SKU_LOOKUP)
    assert result.canonical_id == "GLS-AMB-048-20", "48ml must resolve to its own canonical, not the 50ml one"
    assert result.gate_status == "auto"


def test_sparse_description_is_held_ambiguous_not_guessed():
    result = resolve_line_item(_item("bottle - 50 - amber"), REGISTRY, SKU_LOOKUP)
    assert result.canonical_id is None, "must not guess between 48/50/100ml when volume is unstated"
    assert result.gate_status == "review"


def test_sku_code_stage1_lookup():
    result = resolve_line_item(_item("GB-AMB-50-20N", sku_code="GB-AMB-50-20N"), REGISTRY, SKU_LOOKUP)
    assert result.canonical_id == "GLS-AMB-050-20"
    assert result.method == "sku_code_lookup"
    assert result.confidence == 0.95


def test_unrecognized_product_proposes_new_canonical():
    result = resolve_line_item(_item("Printed BOPP Label Roll 50x30mm"), REGISTRY, SKU_LOOKUP)
    assert result.canonical_id is None
    assert result.gate_status == "new_canonical_proposed"


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"\n{len(tests)} checks passed")
