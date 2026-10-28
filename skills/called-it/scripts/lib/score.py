"""Turn Jev answers into verdicts and verdicts into the numbers the scorecard shows.

Policy lives here, in code, and is printed in every report: a bar is met when the grader says the
criterion is met with probability at or above `yes` AND the best evidence clears `min_strength`.
A bar is not met when the grader says the evidence contradicts the criterion at or above `yes`.
Everything else is unresolved, with a reason.
"""
from __future__ import annotations

from . import config, jev


def grading_questions() -> dict:
    return {
        "met": jev.noul(
            "Given only the evidence listed in `evidence`, and measuring the way `measure` says, is the `criterion` met as of `as_of`?",
            true="At least one evidence item that supports the criterion comes from a source with standing (tier 1, 2 or 3, or a tier 4 admission by the author) and directly establishes what the criterion requires.",
            false="No evidence item with standing establishes the criterion. Items that are only about the same topic, that only predict, or that come from people without standing do not count.",
        ),
        "contradicted": jev.noul(
            "Given only the evidence listed in `evidence`, does the evidence show that the `criterion` was NOT met as of `as_of`?",
            true="At least one evidence item with standing reports the opposite of what the criterion requires, or reports that the required thing did not happen within the window.",
            false="Nothing in the evidence shows the criterion failed; the evidence may simply be silent or insufficient.",
        ),
        "strength": jev.score(
            "How strong is the best evidence bearing on the `criterion`, considering source standing and directness?",
            config.STRENGTH_LEVELS,
        ),
    }


def grading_state(run: dict, claim: dict, bar: str, criterion: str, evidence: list[dict], measure: str = "") -> dict:
    return {
        "subject": run["subject"]["name"],
        "target_year": run["target_year"],
        "as_of": run["evidence_window"]["end"],
        "claim": {"quote": claim["quote"], "author": claim.get("author"), "date": claim.get("date"),
                  "context": claim.get("context", "")},
        "bar": bar,
        "criterion": criterion,
        "measure": measure or "Judge the criterion on the evidence as written.",
        "evidence_tiers": {str(k): v for k, v in config.EVIDENCE_TIERS.items()},
        "evidence": [
            {"tier": e["tier"], "tier_meaning": config.EVIDENCE_TIERS[e["tier"]], "date": e["date"], "source": e["source"],
             "direction": e["direction"], "quote": e["quote"], "url": e["url"]}
            for e in evidence
        ],
    }


def verdict(met_p: float, contradicted_p: float, strength: float, thresholds: dict) -> tuple[str, str]:
    yes, no, min_s = thresholds["yes"], thresholds["no"], thresholds["min_strength"]
    if contradicted_p >= yes and met_p < yes:
        return "not_met", "evidence shows the criterion was not met"
    if met_p >= yes and strength >= min_s and contradicted_p < yes:
        return "met", "criterion met on evidence with standing"
    if met_p >= yes and strength < min_s:
        return "unresolved", "claimed but the evidence lacks standing"
    if met_p >= yes and contradicted_p >= yes:
        return "unresolved", "evidence conflicts"
    if met_p <= no and contradicted_p <= no:
        return "unresolved", "evidence is silent"
    return "unresolved", "grader is uncertain"


def monotone(grades: list[dict]) -> int:
    """Enforce the nesting of the bars. Strict is a subset of standard is a subset of lenient by construction,
    so a stricter bar met implies the looser ones met, and a looser bar not met implies the stricter ones
    not met. The grader answers each bar alone and can disagree with itself across bars; this pass records
    the implication in `implied_from` and leaves the raw probabilities untouched. Returns the count changed."""
    by_claim: dict[str, dict[str, dict]] = {}
    for g in grades:
        by_claim.setdefault(g["claim_id"], {})[g["bar"]] = g
    changed = 0
    order = list(config.BARS)  # strict, standard, lenient
    for rows in by_claim.values():
        for i, bar in enumerate(order):
            g = rows.get(bar)
            if not g:
                continue
            if g["verdict"] == "met":
                for looser in order[i + 1:]:
                    h = rows.get(looser)
                    if h and h["verdict"] != "met":
                        h["verdict"], h["reason"], h["implied_from"] = "met", f"implied: the {bar} bar is met", bar
                        changed += 1
            if g["verdict"] == "not_met":
                for stricter in order[:i]:
                    h = rows.get(stricter)
                    if h and h["verdict"] != "not_met":
                        h["verdict"], h["reason"], h["implied_from"] = "not_met", f"implied: the {bar} bar is not met", bar
                        changed += 1
    return changed


def aggregate(grades: list[dict], claims: list[dict]) -> dict:
    per_bar, raw_all = {}, {}
    for bar in config.BARS:
        rows = [g for g in grades if g["bar"] == bar]
        met = sum(1 for g in rows if g["verdict"] == "met")
        not_met = sum(1 for g in rows if g["verdict"] == "not_met")
        unresolved = sum(1 for g in rows if g["verdict"] == "unresolved")
        resolved = met + not_met
        raw_all[bar] = met / len(rows) if rows else None
        per_bar[bar] = {
            "met": met, "not_met": not_met, "unresolved": unresolved, "resolved": resolved,
            "hit_rate": round(met / resolved, 3) if resolved else None,
            "hit_rate_all": round(raw_all[bar], 3) if rows else None,
        }
    strict, lenient = raw_all["strict"], raw_all["lenient"]
    gap = round(lenient - strict, 3) if strict is not None and lenient is not None else None
    # Per-claim ladder: the highest bar met, or the lowest bar not met, or unresolved.
    ladder = {}
    for c in claims:
        rows = {g["bar"]: g for g in grades if g["claim_id"] == c["id"]}
        best = None
        for bar in config.BARS:  # strict first
            if rows.get(bar, {}).get("verdict") == "met":
                best = bar
                break
        if best:
            ladder[c["id"]] = f"met:{best}"
        elif any(rows.get(b, {}).get("verdict") == "not_met" for b in config.BARS):
            ladder[c["id"]] = "not_met"
        else:
            ladder[c["id"]] = "unresolved"
    counts = {"met_strict": 0, "met_standard": 0, "met_lenient": 0, "not_met": 0, "unresolved": 0}
    for v in ladder.values():
        key = v.replace("met:", "met_") if v.startswith("met:") else v
        counts[key] += 1
    return {"per_bar": per_bar, "generosity_gap": gap, "ladder": ladder, "ladder_counts": counts, "n_claims": len(claims)}
