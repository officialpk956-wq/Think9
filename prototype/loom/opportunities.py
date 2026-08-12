"""L4 opportunity detection: five always-on detectors over the spec graph.

Every rupee figure here shows its own arithmetic in `Opportunity.working`.
A category manager has to be able to audit a number before acting on it,
and "the model said so" is not auditable.
"""
from __future__ import annotations

import sqlite3
from collections import defaultdict
from datetime import date

from loom.graph import historical_floor, live_lines, mean_lead_time
from loom.models import TODAY, Opportunity

# Sub-MOQ premium by how far below MOQ the order sits. Industry reporting for
# 2026: suppliers accept ~500 units if buyers pay 20-30% more per unit. The
# further below MOQ, the worse the surcharge.
PENALTY_TIERS = [(0.25, 0.30), (0.50, 0.25), (0.75, 0.20), (1.00, 0.12)]

PRICE_OUTLIER_THRESHOLD = 0.15   # >15% above portfolio best
CONCENTRATION_MIN_BRANDS = 3     # sole vendor serving >=3 brands
LEAD_TIME_DRIFT_THRESHOLD = 0.20  # >20% above vendor's trailing mean
EXPIRY_WINDOW_DAYS = 7


def sub_moq_penalty(qty: int, moq: int) -> float:
    """Premium fraction baked into a quoted price because it is below MOQ."""
    if moq <= 0 or qty >= moq:
        return 0.0
    ratio = qty / moq
    for bound, penalty in PENALTY_TIERS:
        if ratio < bound:
            return penalty
    return 0.0


def _by_canonical(rows) -> dict[str, list]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["canonical_id"]].append(row)
    return grouped


def consolidate_by_brand(rows) -> list[dict]:
    """Collapse competing quotes into one requirement per (brand, SKU).

    Several vendors quoting the same brand for the same object are competing
    offers on ONE requirement, not additive demand. Summing raw quote lines
    would double-count that brand's volume and inflate the consolidated
    figure - the exact error that makes a bundling number collapse the
    moment someone checks it.

    Each brand therefore contributes once, at the best live price available
    to it; the losing quotes are retained as that brand's BATNA rather than
    as extra units.
    """
    requirements = []
    for brand, brand_rows in _group(rows, "brand_id").items():
        chosen = min(brand_rows, key=lambda r: r["unit_price"])
        # When a brand's competing quotes disagree on quantity, take the
        # smallest. A consolidated volume must never overstate real demand.
        qty = min(r["qty"] for r in brand_rows)
        requirements.append({
            "brand": brand,
            "qty": qty,
            "unit_price": chosen["unit_price"],
            "chosen": chosen,
            "alternates": [r for r in brand_rows if r["id"] != chosen["id"]],
        })
    return sorted(requirements, key=lambda req: req["unit_price"])


def _group(rows, key: str) -> dict:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row[key]].append(row)
    return grouped


def detect_moq_bundling(conn, today: date = TODAY) -> list[Opportunity]:
    """The money. Same object, >=2 brands, co-valid quotes, combined volume clears MOQ."""
    found = []
    for canonical_id, rows in _by_canonical(live_lines(conn, today)).items():
        requirements = consolidate_by_brand(rows)
        if len(requirements) < 2:
            continue
        moq = rows[0]["canonical_moq"]
        combined_qty = sum(req["qty"] for req in requirements)
        if combined_qty < moq:
            continue

        current_total = sum(req["qty"] * req["unit_price"] for req in requirements)
        best = requirements[0]  # sorted by price
        penalty = sub_moq_penalty(best["qty"], moq)
        # Strip the sub-MOQ surcharge out of the best price observed. That
        # de-penalised price is what the same vendor prices at once volume
        # clears MOQ - the saving is a surcharge stopping, not a negotiation win.
        base_price = best["unit_price"] / (1 + penalty)
        consolidated = combined_qty * base_price
        savings = current_total - consolidated

        chosen_rows = [req["chosen"] for req in requirements]
        soonest = min(chosen_rows, key=lambda r: r["days_to_expiry"])
        expiring = soonest["days_to_expiry"] <= EXPIRY_WINDOW_DAYS
        cm_qty = sum(req["qty"] for req in requirements
                     if req["chosen"]["procurement_mode"] == "cm_embedded")

        working = ["today, each brand buying separately and each below MOQ:"]
        for req in requirements:
            flags = []
            if req["alternates"]:
                flags.append(f"+{len(req['alternates'])} competing")
            if req["chosen"]["procurement_mode"] == "cm_embedded":
                flags.append("CM-embedded")
            working.append(
                f"    {req['brand']:<14}{req['qty']:>6,} x Rs {req['unit_price']:>6.2f}"
                f" = Rs {req['qty'] * req['unit_price']:>10,.2f}  {req['chosen']['vendor_name'][:26]:<27}"
                + (f"[{', '.join(flags)}]" if flags else ""))
        working += [
            f"    {'requirement':<14}{combined_qty:>6,} units{'':<11}Rs {current_total:>10,.2f}",
            "",
            f"one requirement per brand - competing quotes for the same requirement are",
            f"counted once at the best price, never summed as extra volume",
            "",
            f"combined volume = {combined_qty:,} units  vs MOQ {moq:,}  -> clears MOQ",
            f"best price seen = Rs {best['unit_price']:.2f} @ {best['qty']:,} units "
            f"({best['chosen']['vendor_name']}, {best['brand']})",
            f"  that order is {best['qty'] / moq:.0%} of MOQ -> carries a {penalty:.0%} sub-MOQ premium",
            f"base price      = Rs {best['unit_price']:.2f} / {1 + penalty:.2f} = Rs {base_price:.2f}",
            f"consolidated    = {combined_qty:,} x Rs {base_price:.2f} = Rs {consolidated:,.2f}",
            f"SAVING          = Rs {current_total:,.2f} - Rs {consolidated:,.2f} = Rs {savings:,.2f}",
        ]
        if cm_qty:
            working.append(
                f"note            {cm_qty:,} of these units are CM-embedded - that volume needs the")
            working.append(
                "                contract manufacturer's agreement, not just a Think9 PO")

        found.append(Opportunity(
            kind="moq_bundling", canonical_id=canonical_id,
            headline=f"Bundle {len(requirements)} brands on {canonical_id} "
                     f"({rows[0]['canonical_description']})",
            rupee_impact=savings, additive=True, expiry_pressure=expiring,
            working=working,
            payload={"requirements": requirements, "moq": moq, "combined_qty": combined_qty,
                     "base_price": base_price, "current_total": current_total,
                     "consolidated": consolidated, "brands": sorted(r["brand"] for r in requirements),
                     "best": best, "soonest_expiry": soonest, "penalty": penalty},
        ))
    return found


def detect_price_outliers(conn, today: date = TODAY) -> list[Opportunity]:
    """A brand paying >15% above the best price the portfolio has ever achieved."""
    found = []
    for canonical_id, rows in _by_canonical(live_lines(conn, today)).items():
        # Compare each brand's BEST available price, not every quote line - a
        # brand holding two competing quotes would never transact at the worse
        # one, so flagging it for that price would be a false positive.
        requirements = consolidate_by_brand(rows)
        floor_hist = historical_floor(conn, canonical_id)
        best_live = min(req["unit_price"] for req in requirements)
        portfolio_best = min([p for p in (floor_hist, best_live) if p is not None])
        for req in requirements:
            excess = req["unit_price"] / portfolio_best - 1
            if excess <= PRICE_OUTLIER_THRESHOLD:
                continue
            r = req["chosen"]
            savings = req["qty"] * (req["unit_price"] - portfolio_best)
            found.append(Opportunity(
                kind="price_outlier", canonical_id=canonical_id,
                headline=f"{req['brand']} paying {excess:.0%} above portfolio best on {canonical_id}",
                rupee_impact=savings, additive=True,
                expiry_pressure=r["days_to_expiry"] <= EXPIRY_WINDOW_DAYS,
                working=[
                    f"best available = Rs {req['unit_price']:.2f} @ {req['qty']} units"
                    f" ({r['vendor_name']}, {req['brand']})",
                    f"portfolio best = Rs {portfolio_best:.2f}"
                    + (f" (historical PO, same SKU)" if portfolio_best == floor_hist else " (live quote)"),
                    f"gap            = {excess:.1%}  (threshold {PRICE_OUTLIER_THRESHOLD:.0%})",
                    f"SAVING         = {req['qty']} x (Rs {req['unit_price']:.2f}"
                    f" - Rs {portfolio_best:.2f}) = Rs {savings:,.2f}",
                ],
                payload={"row": r, "portfolio_best": portfolio_best},
            ))
    return found


def detect_vendor_concentration(conn, today: date = TODAY) -> list[Opportunity]:
    """One vendor as the portfolio's single point of failure on a component."""
    found = []
    for canonical_id, rows in _by_canonical(live_lines(conn, today)).items():
        vendors = {r["vendor_gstin"] for r in rows}
        brands = {r["brand_id"] for r in rows}
        if len(vendors) != 1 or len(brands) < CONCENTRATION_MIN_BRANDS:
            continue
        exposure = sum(r["qty"] * r["unit_price"] for r in rows)
        vendor_name = rows[0]["vendor_name"]
        found.append(Opportunity(
            kind="vendor_concentration", canonical_id=canonical_id,
            headline=f"{vendor_name} is sole source for {len(brands)} brands on {canonical_id}",
            rupee_impact=exposure, additive=False,
            working=[
                f"brands exposed = {', '.join(sorted(brands))}",
                f"qualified alternate vendors quoting this SKU = 0",
                f"EXPOSURE       = Rs {exposure:,.2f} of live quoted spend behind one vendor",
                "risk           a disruption at this vendor stops packaging for the whole portfolio,",
                "               and consolidating volume here would deepen the dependency",
            ],
            payload={"rows": rows, "brands": sorted(brands), "vendor_name": vendor_name},
        ))
    return found


def detect_lead_time_drift(conn, today: date = TODAY) -> list[Opportunity]:
    """Quoted lead time running above that vendor's own trailing mean for the SKU."""
    found = []
    for r in live_lines(conn, today):
        if r["lead_time_days"] is None:
            continue
        mean = mean_lead_time(conn, r["canonical_id"], r["vendor_gstin"])
        if not mean:
            continue
        drift = r["lead_time_days"] / mean - 1
        if drift <= LEAD_TIME_DRIFT_THRESHOLD:
            continue
        found.append(Opportunity(
            kind="lead_time_drift", canonical_id=r["canonical_id"],
            headline=f"{r['vendor_name']} lead time on {r['canonical_id']} up {drift:.0%} vs its own history",
            rupee_impact=r["qty"] * r["unit_price"], additive=False,
            expiry_pressure=r["days_to_expiry"] <= EXPIRY_WINDOW_DAYS,
            working=[
                f"quoted now     = {r['lead_time_days']} days ({r['brand_id']}, {r['source_file']})",
                f"trailing mean  = {mean:.1f} days from historical POs with this vendor",
                f"DRIFT          = +{drift:.0%}  (threshold {LEAD_TIME_DRIFT_THRESHOLD:.0%})",
                "read           capacity tightening or deprioritisation - worth raising before it",
                "               becomes a stockout, and worth pricing into any consolidation",
            ],
            payload={"row": r, "mean": mean, "drift": drift},
        ))
    return found


def detect_expiry_pressure(conn, bundles: list[Opportunity], today: date = TODAY) -> list[Opportunity]:
    """Bundleable savings about to lapse. Time-critical, so it ranks to the top.

    Non-additive: these are the same rupees as the bundle they refer to,
    characterised by urgency rather than a separate pot of money.
    """
    found = []
    for bundle in bundles:
        if not bundle.expiry_pressure:
            continue
        soonest = bundle.payload["soonest_expiry"]
        days = int(soonest["days_to_expiry"])
        found.append(Opportunity(
            kind="expiry_pressure", canonical_id=bundle.canonical_id,
            headline=f"Rs {bundle.rupee_impact:,.0f} on {bundle.canonical_id} lapses in"
                     f" {days} day{'' if days == 1 else 's'}",
            rupee_impact=bundle.rupee_impact, additive=False, expiry_pressure=True,
            working=[
                f"earliest lapse = {soonest['valid_until']} ({soonest['vendor_name']}, {soonest['brand_id']})",
                f"days remaining = {days}  (window {EXPIRY_WINDOW_DAYS} days)",
                f"AT RISK        = Rs {bundle.rupee_impact:,.2f} of bundling saving",
                "               once this quote lapses the bundle has to be re-quoted from scratch",
            ],
            payload=bundle.payload,
        ))
    return found


def detect_all(conn: sqlite3.Connection, today: date = TODAY) -> list[Opportunity]:
    """Run all five detectors and rank them.

    Ranked by rupee impact, except that anything time-critical sorts above
    anything that isn't - a larger saving that lapses next month is worth
    less than a smaller one that lapses on Thursday.
    """
    bundles = detect_moq_bundling(conn, today)
    everything = (bundles + detect_price_outliers(conn, today) + detect_vendor_concentration(conn, today)
                  + detect_lead_time_drift(conn, today) + detect_expiry_pressure(conn, bundles, today))
    return sorted(everything, key=lambda o: (o.expiry_pressure, o.rupee_impact), reverse=True)


def portfolio_total(opportunities: list[Opportunity]) -> float:
    """Only additive findings - never double-count exposure as savings."""
    return sum(o.rupee_impact for o in opportunities if o.additive)
