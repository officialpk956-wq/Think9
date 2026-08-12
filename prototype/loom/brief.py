"""L5 negotiation brief: the packet a human takes into the call.

Assembles what a category manager needs to negotiate from a position of
knowledge - consolidated volume, the portfolio's best-ever price, this
vendor's own floor, and a BATNA - and then stops. The brief recommends a
target; a human commits the spend. That boundary is Gate 2 and it is not
negotiable (CLAUDE.md section 7).
"""
from __future__ import annotations

import sqlite3
from datetime import date

from loom.graph import historical_floor, mean_lead_time
from loom.models import TODAY, Opportunity

WIDTH = 78


def _rule(char: str = "-") -> str:
    return char * WIDTH


def _days(n: int) -> str:
    return f"{n} day" if n == 1 else f"{n} days"


def _alternate_vendors(conn: sqlite3.Connection, canonical_id: str, exclude_gstin: str,
                       today: date) -> list[sqlite3.Row]:
    """Qualified alternates: anyone else quoting this SKU live, or who has supplied it before."""
    return conn.execute("""
        SELECT v.name AS vendor_name, v.gstin,
               MIN(li.unit_price) AS best_live,
               (SELECT MIN(ph.unit_price) FROM price_history ph
                 WHERE ph.canonical_id = ? AND ph.vendor_gstin = v.gstin) AS best_history
        FROM line_item li
        JOIN quote q ON q.id = li.quote_id
        JOIN vendor v ON v.gstin = q.vendor_gstin
        WHERE li.canonical_id = ? AND v.gstin != ?
          AND li.unit_price IS NOT NULL AND date(q.valid_until) >= date(?)
        GROUP BY v.gstin
        ORDER BY best_live
    """, (canonical_id, canonical_id, exclude_gstin, today.isoformat())).fetchall()


def render_brief(conn: sqlite3.Connection, opportunity: Opportunity,
                 all_opportunities: list[Opportunity], today: date = TODAY) -> str:
    p = opportunity.payload
    requirements, best = p["requirements"], p["best"]
    canonical_id = opportunity.canonical_id
    target_vendor_gstin = best["chosen"]["vendor_gstin"]

    portfolio_floor = historical_floor(conn, canonical_id)
    vendor_floor = historical_floor(conn, canonical_id, target_vendor_gstin)
    alternates = _alternate_vendors(conn, canonical_id, target_vendor_gstin, today)
    target_price = p["base_price"]

    out: list[str] = [
        _rule("="),
        f"NEGOTIATION BRIEF  |  {canonical_id}",
        _rule("="),
        f"Spec          {best['chosen']['canonical_description']}",
        f"Counterparty  {best['chosen']['vendor_name']}  (GSTIN {target_vendor_gstin})",
        f"Prepared      {today.isoformat()}   Earliest quote lapse: "
        f"{p['soonest_expiry']['valid_until']} "
        f"({_days(int(p['soonest_expiry']['days_to_expiry']))})",
        "",
        "PARTICIPATING BRANDS  (one requirement each; competing quotes shown as alternates)",
        _rule(),
        f"  {'Brand':<15}{'Qty':>7}  {'Price':>8}  {'Line value':>12}  {'Mode':<12} Vendor",
    ]
    for req in requirements:
        r = req["chosen"]
        out.append(
            f"  {req['brand']:<15}{req['qty']:>7,}  {'Rs ' + format(req['unit_price'], '.2f'):>8}"
            f"  {'Rs ' + format(req['qty'] * req['unit_price'], ',.2f'):>12}"
            f"  {r['procurement_mode']:<12} {r['vendor_name']}")
        # Competing offers on this same requirement - the brand's own BATNA,
        # and the reason this volume is not counted twice.
        for alt in req["alternates"]:
            out.append(f"  {'  alternate':<15}{'':>7}  {'Rs ' + format(alt['unit_price'], '.2f'):>8}"
                       f"  {'not counted':>12}  {'':<12} {alt['vendor_name']}")
    out += [
        _rule(),
        f"  {'TOTAL':<15}{p['combined_qty']:>7,}  {'':>8}  "
        f"{'Rs ' + format(p['current_total'], ',.2f'):>12}",
        "",
        "VOLUME POSITION",
        _rule(),
        f"  Consolidated volume   {p['combined_qty']:,} units",
        f"  MOQ for this SKU      {p['moq']:,} units",
        f"  Status                clears MOQ by {p['combined_qty'] - p['moq']:,} units"
        f"  ({p['combined_qty'] / p['moq']:.0%} of MOQ)",
        f"  Individually          every brand is below MOQ and paying the sub-MOQ premium",
        "",
        "PRICE INTELLIGENCE",
        _rule(),
        f"  Best live quote                 Rs {best['unit_price']:.2f}  "
        f"({best['chosen']['vendor_name']}, {best['qty']:,} units)",
    ]
    out.append(
        f"  Portfolio best ever achieved    Rs {portfolio_floor:.2f}"
        if portfolio_floor else "  Portfolio best ever achieved    no history")
    out.append(
        f"  This vendor's own floor         Rs {vendor_floor:.2f}   (their historical low, same SKU)"
        if vendor_floor else "  This vendor's own floor         no history with this vendor")

    out += ["", "BATNA - ALTERNATE QUALIFIED VENDORS", _rule()]
    if alternates:
        for a in alternates:
            hist = f", historical low Rs {a['best_history']:.2f}" if a["best_history"] else ""
            out.append(f"  {a['vendor_name']:<30} live Rs {a['best_live']:.2f}{hist}")
        out.append("  -> volume is movable. Do not disclose consolidated volume until commit.")
    else:
        out.append("  NONE. No alternate vendor is quoting this SKU - negotiating position is weak,")
        out.append("  and qualifying a second source should precede consolidating here.")

    notes = []
    for o in all_opportunities:
        if o.canonical_id != canonical_id:
            continue
        if o.kind == "lead_time_drift":
            notes.append(f"  LEAD TIME   {o.headline}")
        if o.kind == "vendor_concentration":
            notes.append(f"  CONCENTRATION  {o.headline}")
    lt_mean = mean_lead_time(conn, canonical_id, target_vendor_gstin)
    if lt_mean:
        notes.append(f"  LEAD TIME   {best['chosen']['vendor_name']} trailing mean {lt_mean:.1f} days"
                     f" on this SKU; quoted now {best['chosen']['lead_time_days']} days")
    if len(alternates) == 0:
        notes.append("  CONCENTRATION  consolidating here creates a single point of failure")
    out += ["", "RISK NOTES", _rule()] + (notes or ["  None flagged."])

    out += [
        "",
        "TARGET",
        _rule(),
        f"  Target price          Rs {target_price:.2f} / unit",
        f"  Reasoning             best live price is Rs {best['unit_price']:.2f} at "
        f"{best['qty']:,} units, which is",
        f"                        {best['qty'] / p['moq']:.0%} of MOQ and therefore carries a "
        f"{p['penalty']:.0%} sub-MOQ premium.",
        f"                        Removing that premium: Rs {best['unit_price']:.2f} / "
        f"{1 + p['penalty']:.2f} = Rs {target_price:.2f}.",
        f"                        At {p['combined_qty']:,} units the order clears MOQ, so the premium",
        "                        should not apply at all.",
    ]
    if portfolio_floor and target_price < portfolio_floor:
        out.append(f"  Sanity check          target is below the portfolio's best-ever "
                   f"Rs {portfolio_floor:.2f} - treat")
        out.append("                        as a stretch anchor, not a walk-away number.")
    out += [
        f"  Expected saving       Rs {opportunity.rupee_impact:,.2f} vs current separate ordering",
        "",
        _rule("="),
        "AWAITING HUMAN APPROVAL - GATE 2. This system does not commit spend.",
        "It has not contacted this vendor and will not. Gate 3 covers vendor communication:",
        "a category manager sends anything that leaves the building.",
        _rule("="),
    ]
    return "\n".join(out)
