"""Checks on the money path: competing quotes must never inflate volume.

Run: `python tests/test_opportunities.py`
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loom.opportunities import consolidate_by_brand, sub_moq_penalty


def _rows(*specs) -> list[sqlite3.Row]:
    """Build sqlite3.Rows the way live_lines() returns them."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("CREATE TABLE r (id INTEGER, brand_id TEXT, qty INTEGER, unit_price REAL,"
                 " vendor_name TEXT, procurement_mode TEXT, days_to_expiry REAL)")
    for i, (brand, qty, price, vendor) in enumerate(specs):
        conn.execute("INSERT INTO r VALUES (?,?,?,?,?,'direct',5)", (i, brand, qty, price, vendor))
    return conn.execute("SELECT * FROM r").fetchall()


def test_competing_quotes_count_once():
    """Two vendors quoting one brand for one requirement is NOT 1,600 units."""
    reqs = consolidate_by_brand(_rows(
        ("Neude", 800, 22.00, "Rajkot"),
        ("Neude", 800, 20.75, "Gujarat"),
    ))
    assert len(reqs) == 1, "one brand, one requirement"
    assert reqs[0]["qty"] == 800, f"expected 800 units, got {reqs[0]['qty']} - volume double-counted"
    assert reqs[0]["unit_price"] == 20.75, "must take the best price available to that brand"
    assert len(reqs[0]["alternates"]) == 1, "the losing quote is retained as BATNA"


def test_conflicting_quantities_take_the_smaller():
    """A consolidated figure must never overstate demand."""
    reqs = consolidate_by_brand(_rows(
        ("Goodbug", 700, 1.92, "Deccan"),
        ("Goodbug", 500, 2.00, "Deccan"),
    ))
    assert reqs[0]["qty"] == 500, "conservative: smallest stated requirement"
    assert reqs[0]["unit_price"] == 1.92


def test_distinct_brands_do_aggregate():
    """Consolidation must not over-correct - different brands are real added volume."""
    reqs = consolidate_by_brand(_rows(
        ("Neude", 800, 20.75, "Gujarat"),
        ("Goodbug", 700, 22.80, "Rajkot"),
    ))
    assert len(reqs) == 2
    assert sum(r["qty"] for r in reqs) == 1500


def test_hero_bundle_clears_moq_on_real_demand():
    """The headline number must survive the dedup, not depend on it being absent."""
    reqs = consolidate_by_brand(_rows(
        ("Neude", 800, 22.00, "Rajkot"), ("Neude", 800, 20.75, "Gujarat"),
        ("Beauty by Bie", 600, 21.50, "Gujarat"),
        ("Panchamrit", 450, 22.50, "Rajkot"),
        ("Goodbug", 700, 22.80, "Rajkot"),
    ))
    combined = sum(r["qty"] for r in reqs)
    assert combined == 2550, f"expected 2,550 units of real requirement, got {combined}"
    assert combined >= 2500, "hero bundle must clear MOQ on deduplicated demand"


def test_penalty_tiers():
    assert sub_moq_penalty(400, 2500) == 0.30   # 16% of MOQ
    assert sub_moq_penalty(800, 2500) == 0.25   # 32%
    assert sub_moq_penalty(300, 600) == 0.20    # 50% exactly -> the 50-75% band
    assert sub_moq_penalty(2600, 2500) == 0.0   # at or above MOQ, no premium


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS  {test.__name__}")
    print(f"\n{len(tests)} checks passed")
