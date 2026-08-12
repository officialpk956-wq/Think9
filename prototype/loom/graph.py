"""L3 portfolio spec graph: SQLite.

Everything downstream (opportunity detection, the negotiation brief) reads
from here rather than from the in-flight Python objects, so the graph is
load-bearing rather than decorative - which is the point of L3 being "the
compounding asset".

In-memory by default: the demo is idempotent and leaves no artifact behind.
Pass a path to persist. At ~24k line items/year, SQLite here and Postgres
in production is the whole storage story - see CLAUDE.md section 4.
"""
from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import date
from pathlib import Path

from loom.models import TODAY
from loom.resolve import ResolutionResult, load_registry

SEED_DIR = Path(__file__).parent.parent / "data" / "seed"
QUOTES_DIR = Path(__file__).parent.parent / "data" / "quotes"

# Deviation from the spec's table list: brand sits on line_item, not quote.
# One vendor rate-list is routinely shared across several brands' procurement
# (everest_cartons.csv serves all five), so brand is a property of who is
# buying the line, not of the artifact it arrived in.
SCHEMA = """
CREATE TABLE canonical_sku (
    id TEXT PRIMARY KEY, description TEXT NOT NULL, attrs_json TEXT NOT NULL,
    moq INTEGER NOT NULL, created_at TEXT NOT NULL, approved_by TEXT);
CREATE TABLE vendor (
    gstin TEXT PRIMARY KEY, name TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE brand (id TEXT PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE quote (
    id TEXT PRIMARY KEY, vendor_gstin TEXT NOT NULL REFERENCES vendor(gstin),
    issued_at TEXT NOT NULL, valid_until TEXT NOT NULL,
    source_file TEXT NOT NULL, source_format TEXT NOT NULL);
CREATE TABLE line_item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_id TEXT NOT NULL REFERENCES quote(id),
    brand_id TEXT NOT NULL REFERENCES brand(id),
    raw_description TEXT NOT NULL, qty INTEGER, unit_price REAL, moq INTEGER,
    lead_time_days INTEGER, canonical_id TEXT REFERENCES canonical_sku(id),
    resolution_confidence REAL, resolution_method TEXT, gate_status TEXT NOT NULL);
CREATE TABLE brand_sku_edge (
    brand_id TEXT NOT NULL, canonical_id TEXT NOT NULL,
    procurement_mode TEXT NOT NULL, PRIMARY KEY (brand_id, canonical_id));
CREATE TABLE price_history (
    canonical_id TEXT NOT NULL, vendor_gstin TEXT NOT NULL, brand_id TEXT NOT NULL,
    unit_price REAL NOT NULL, qty INTEGER NOT NULL, lead_time_days INTEGER,
    observed_at TEXT NOT NULL);
"""


def _seed(name: str):
    return json.loads((SEED_DIR / f"{name}.json").read_text(encoding="utf-8"))


def build_graph(results: list[ResolutionResult], l1_rejects=(), db_path: str = ":memory:") -> sqlite3.Connection:
    """Write registries, quotes, line items and history into the graph.

    L1-rejected items are recorded too, with a null canonical_id and their
    gate status. They are real observed data that a human still has to deal
    with - dropping them would make the graph's line_item count quietly
    disagree with the number of items actually extracted.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    stamp = TODAY.isoformat()

    # Canonical SKUs carry approved_by because every row in this table either
    # came from the seeded registry or passed Gate 1. Nothing writes itself in.
    for sku in load_registry():
        conn.execute(
            "INSERT INTO canonical_sku VALUES (?,?,?,?,?,?)",
            (sku.id, sku.description, json.dumps(asdict(sku.attrs)), sku.moq, stamp, "seed_registry"),
        )
    for v in _seed("vendors"):
        conn.execute("INSERT INTO vendor VALUES (?,?,?)", (v["gstin"], v["name"], stamp))
    for b in _seed("brands"):
        conn.execute("INSERT INTO brand VALUES (?,?)", (b, b))
    for entry in json.loads((QUOTES_DIR / "manifest.json").read_text(encoding="utf-8")):
        conn.execute("INSERT INTO quote VALUES (?,?,?,?,?,?)", (
            entry["source_file"], entry["vendor_gstin"], entry["issued_at"],
            entry["valid_until"], entry["source_file"], entry["format"]))

    modes = {(m["brand"], m["canonical_id"]): m["procurement_mode"] for m in _seed("procurement_modes")}
    for r in results:
        it = r.line_item
        conn.execute(
            "INSERT INTO line_item (quote_id, brand_id, raw_description, qty, unit_price, moq,"
            " lead_time_days, canonical_id, resolution_confidence, resolution_method, gate_status)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (it.source_file, it.brand, it.raw_description, it.qty, it.unit_price, it.moq,
             it.lead_time_days, r.canonical_id, r.confidence, r.method, r.gate_status))
        # A brand-SKU edge only exists once a line actually resolves - an
        # unresolved item has no canonical to attach to, by design.
        if r.canonical_id:
            conn.execute(
                "INSERT OR IGNORE INTO brand_sku_edge VALUES (?,?,?)",
                (it.brand, r.canonical_id, modes.get((it.brand, r.canonical_id), "direct")))

    for it in l1_rejects:
        conn.execute(
            "INSERT INTO line_item (quote_id, brand_id, raw_description, qty, unit_price, moq,"
            " lead_time_days, canonical_id, resolution_confidence, resolution_method, gate_status)"
            " VALUES (?,?,?,?,?,?,?,NULL,NULL,NULL,?)",
            (it.source_file, it.brand, it.raw_description, it.qty, it.unit_price, it.moq,
             it.lead_time_days, "reject_low_confidence"))

    for h in _seed("price_history"):
        conn.execute("INSERT INTO price_history VALUES (?,?,?,?,?,?,?)", (
            h["canonical_id"], h["vendor_gstin"], h["brand"], h["unit_price"],
            h["qty"], h["lead_time_days"], h["observed_at"]))

    conn.commit()
    return conn


def live_lines(conn: sqlite3.Connection, today: date = TODAY) -> list[sqlite3.Row]:
    """Resolved line items whose quote is still inside its validity window.

    Value only exists inside that window (CLAUDE.md section 5), so every
    detector starts from this view rather than from all line items ever seen.
    """
    return conn.execute("""
        SELECT li.*, q.valid_until, q.vendor_gstin, q.source_file, v.name AS vendor_name,
               cs.moq AS canonical_moq, cs.description AS canonical_description,
               COALESCE(bse.procurement_mode, 'unknown') AS procurement_mode,
               julianday(q.valid_until) - julianday(?) AS days_to_expiry
        FROM line_item li
        JOIN quote q ON q.id = li.quote_id
        JOIN vendor v ON v.gstin = q.vendor_gstin
        JOIN canonical_sku cs ON cs.id = li.canonical_id
        LEFT JOIN brand_sku_edge bse
               ON bse.brand_id = li.brand_id AND bse.canonical_id = li.canonical_id
        WHERE li.canonical_id IS NOT NULL
          AND li.qty IS NOT NULL AND li.unit_price IS NOT NULL
          AND date(q.valid_until) >= date(?)
        ORDER BY li.canonical_id, li.unit_price
    """, (today.isoformat(), today.isoformat())).fetchall()


def historical_floor(conn: sqlite3.Connection, canonical_id: str, vendor_gstin: str | None = None) -> float | None:
    """Best unit price ever observed for a SKU - portfolio-wide, or for one vendor."""
    if vendor_gstin:
        row = conn.execute(
            "SELECT MIN(unit_price) AS floor FROM price_history WHERE canonical_id=? AND vendor_gstin=?",
            (canonical_id, vendor_gstin)).fetchone()
    else:
        row = conn.execute(
            "SELECT MIN(unit_price) AS floor FROM price_history WHERE canonical_id=?",
            (canonical_id,)).fetchone()
    return row["floor"]


def mean_lead_time(conn: sqlite3.Connection, canonical_id: str, vendor_gstin: str) -> float | None:
    """Vendor's trailing mean lead time for one SKU.

    Scoped per (vendor, SKU) rather than per vendor overall: a vendor's
    25-day bottle and 15-day cap have genuinely different lead times, and
    averaging across them would manufacture drift that isn't there.
    """
    row = conn.execute(
        "SELECT AVG(lead_time_days) AS mean FROM price_history"
        " WHERE canonical_id=? AND vendor_gstin=? AND lead_time_days IS NOT NULL",
        (canonical_id, vendor_gstin)).fetchone()
    return row["mean"]


def graph_stats(conn: sqlite3.Connection) -> dict[str, int]:
    tables = ["canonical_sku", "vendor", "brand", "quote", "line_item", "brand_sku_edge", "price_history"]
    return {t: conn.execute(f"SELECT COUNT(*) AS n FROM {t}").fetchone()["n"] for t in tables}
