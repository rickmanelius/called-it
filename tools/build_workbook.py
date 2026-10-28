#!/usr/bin/env python3
"""Build the combined workbook across every graded run: article/data/called-it-<year>.xlsx.

Sheets: Summary (one row per subject), Inventory (every source across runs), Claims (every claim with
its outcome at each bar), Rubrics+Grades, Evidence. Deterministic; standard library only.

    python3 tools/build_workbook.py [--out article/data/called-it-2026.xlsx] [runs/every runs/ippolito ...]
"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "called-it" / "scripts"))
from lib import schema, score, xlsx  # noqa: E402
import called_it  # noqa: E402


def main(argv):
    args = argv[1:]
    out = ROOT / "article" / "data" / "called-it-2026.xlsx"
    if "--out" in args:
        i = args.index("--out")
        out = pathlib.Path(args[i + 1])
        args = args[:i] + args[i + 2:]
    runs = [pathlib.Path(a) for a in args] or sorted(p for p in (ROOT / "runs").iterdir() if (p / "grades.jsonl").exists())
    summary, inventory, claims_rows, rubric_rows, evidence_rows = [], [], [], [], []
    headers = {}
    for d in runs:
        run = json.loads((d / "run.json").read_text())
        sources = schema.read_jsonl(d / "sources.jsonl")
        claims = schema.read_jsonl(d / "claims.jsonl")
        rubrics = schema.read_jsonl(d / "rubrics.jsonl")
        evidence = schema.read_jsonl(d / "evidence.jsonl")
        grades = schema.read_jsonl(d / "grades.jsonl")
        if not grades:
            continue
        graded_ids = {g["claim_id"] for g in grades}
        scope = [c for c in claims if c["id"] in graded_ids]
        agg = score.aggregate(grades, scope)
        sheets = {s["name"]: s for s in called_it.workbook_sheets(run, sources, claims, rubrics, evidence, grades, agg)}
        pb = agg["per_bar"]
        summary.append([run["subject"]["name"], run["name"], run["subject"]["kind"], run["target_year"], run["evidence_window"]["end"],
                        len(sources), len(claims), agg["n_claims"], len(evidence),
                        pb["strict"]["met"], pb["strict"]["not_met"], pb["strict"]["unresolved"], pb["strict"]["hit_rate_all"],
                        pb["standard"]["met"], pb["standard"]["not_met"], pb["standard"]["unresolved"], pb["standard"]["hit_rate_all"],
                        pb["lenient"]["met"], pb["lenient"]["not_met"], pb["lenient"]["unresolved"], pb["lenient"]["hit_rate_all"],
                        agg["generosity_gap"], sum(1 for g in grades if g.get("implied_from")), run["grader"].get("model", "")])
        inventory += sheets["Sources"]["rows"]
        claims_rows += sheets["Claims"]["rows"]
        rubric_rows += sheets["Rubrics+Grades"]["rows"]
        evidence_rows += sheets["Evidence"]["rows"]
        headers = {k: (v["headers"], v.get("widths"), v.get("wrap", [])) for k, v in sheets.items()}
    if not summary:
        sys.exit("no graded runs")
    out.parent.mkdir(parents=True, exist_ok=True)
    xlsx.write_xlsx(out, [
        {"name": "Summary", "headers": ["subject", "run", "kind", "year", "as_of", "sources", "claims_found", "claims_graded", "evidence_rows",
                                        "strict_met", "strict_not_met", "strict_unresolved", "strict_hit_rate",
                                        "standard_met", "standard_not_met", "standard_unresolved", "standard_hit_rate",
                                        "lenient_met", "lenient_not_met", "lenient_unresolved", "lenient_hit_rate",
                                        "generosity_gap", "implied_cells", "grader"],
         "widths": [18, 10, 9, 6, 11, 8, 11, 12, 12, 9, 12, 15, 13, 11, 14, 17, 15, 10, 13, 16, 14, 13, 12, 12], "rows": summary},
        {"name": "Inventory", "headers": headers["Sources"][0], "widths": headers["Sources"][1], "wrap": headers["Sources"][2], "rows": inventory},
        {"name": "Claims", "headers": headers["Claims"][0], "widths": headers["Claims"][1], "wrap": headers["Claims"][2], "rows": claims_rows},
        {"name": "Rubrics+Grades", "headers": headers["Rubrics+Grades"][0], "widths": headers["Rubrics+Grades"][1], "wrap": headers["Rubrics+Grades"][2], "rows": rubric_rows},
        {"name": "Evidence", "headers": headers["Evidence"][0], "widths": headers["Evidence"][1], "wrap": headers["Evidence"][2], "rows": evidence_rows},
    ], title="called-it: 2026 predictions graded at three bars")
    print(f"wrote {out}: {len(summary)} subjects, {len(inventory)} sources, {len(claims_rows)} claims, {len(rubric_rows)} bar rows, {len(evidence_rows)} evidence rows")


if __name__ == "__main__":
    main(sys.argv)
