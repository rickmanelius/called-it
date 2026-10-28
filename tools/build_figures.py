#!/usr/bin/env python3
"""Build the article's cross-subject figures from runs/*/data.json. Deterministic; standard library only.

    python3 tools/build_figures.py [--out article/figures] [runs/every runs/ippolito runs/doll]

Writes hit-rates.svg (small multiples, one panel per subject, three bars per panel with direct labels) and
generosity-gap.svg (one bar per subject), each wrapped in a minimal .html for rendering with
tools/render_png.py. Colours and type are the Called It! brand tokens (lib/brand.py, dark only): strict,
standard and lenient each keep their own bar colour in every chart, and every bar carries its label and value.
"""
from __future__ import annotations

import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "called-it" / "scripts"))
from lib import brand  # noqa: E402

C = brand.COLORS
INK, INK2, MUTED, GRID, AXIS, SURFACE, ACCENT = C["ink"], C["text2"], C["muted"], C["border"], C["border"], C["ground"], C["accent"]
PANEL = C["surface"]
FONT = brand.FONT_TEXT.replace("'", "")
MONO = brand.FONT_MONO.replace("'", "")
FONT_PREFIX = "../../site/assets/fonts/"  # from article/figures/ to the self-hosted fonts
BARS = (("strict", "Strict"), ("standard", "Standard"), ("lenient", "Lenient"))


def color_for(label: str) -> str:
    """Bar colour by what the row is: the three bars keep their own colours everywhere; verdict rows take status colours."""
    l = label.lower()
    for key, _ in BARS:
        if l.startswith(key):
            return brand.BAR_COLORS[key]
    if l.startswith("not met") or l.startswith("wrong"):
        return C["not_met"]
    if l.startswith("met") or l.startswith("right"):
        return C["met"]
    if l.startswith("unresolved") or l.startswith("too soon"):
        return C["unresolved"]
    return C["text2"]


def load(run_dirs):
    out = []
    for d in run_dirs:
        p = pathlib.Path(d) / "data.json"
        if not p.exists():
            continue
        data = json.loads(p.read_text())
        if not data.get("grades"):
            continue
        out.append(data)
    return out


def pct(x):
    return "n/a" if x is None else f"{round(x * 100)}%"


def hit_rates_svg(datas) -> str:
    w, left, right = 1200, 150, 40
    panel_h, row_h, top_pad = 190, 42, 96
    h = top_pad + panel_h * len(datas)
    inner = w - left - right
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family=\'{FONT}\'>',
         f'<rect width="{w}" height="{h}" fill="{SURFACE}"/>',
         f'<text x="{left}" y="34" font-size="22" font-weight="600" fill="{INK}">Hit rate at each bar, by subject</text>',
         f'<text x="{left}" y="54" font-size="13" fill="{INK2}">Share of graded claims met at the strict, standard and lenient bar, as of the run date. Unresolved claims count against the rate.</text>']
    for i, data in enumerate(datas):
        y0 = top_pad + i * panel_h
        agg = data["aggregate"]["per_bar"]
        name = data["run"]["subject"]["name"]
        s.append(f'<text x="{left}" y="{y0}" font-size="16" font-weight="600" fill="{INK}">{html.escape(name)}</text>')
        s.append(f'<text x="{left}" y="{y0 + 18}" font-size="12" fill="{MUTED}">{data["aggregate"]["n_claims"]} claims · gap {("n/a" if data["aggregate"]["generosity_gap"] is None else str(round(data["aggregate"]["generosity_gap"] * 100)) + " pts")}</text>')
        gy = y0 + 28
        for t in (0, 0.25, 0.5, 0.75, 1.0):
            x = left + inner * t
            s.append(f'<line x1="{x:.1f}" y1="{gy}" x2="{x:.1f}" y2="{gy + row_h * 3}" stroke="{GRID}" stroke-width="1"/>')
            if i == len(datas) - 1:
                s.append(f'<text x="{x:.1f}" y="{gy + row_h * 3 + 18}" font-size="12" fill="{MUTED}" text-anchor="middle">{round(t * 100)}%</text>')
        for j, (key, label) in enumerate(BARS):
            st = agg[key]
            rate = st["hit_rate_all"] or 0
            y = gy + j * row_h + 7
            bw = inner * rate
            s.append(f'<text x="{left - 12}" y="{y + 18}" font-size="14" fill="{INK}" text-anchor="end">{label}</text>')
            s.append(f'<rect x="{left}" y="{y}" width="{bw:.1f}" height="26" rx="3" fill="{brand.BAR_COLORS[key]}"><title>{label}: {st["met"]} met, {st["not_met"]} not met, {st["unresolved"]} unresolved</title></rect>')
            s.append(f'<text x="{left + bw + 8:.1f}" y="{y + 18}" font-size="13" font-family=\'{MONO}\' fill="{INK}">{pct(st["hit_rate_all"])} <tspan fill="{MUTED}">({st["met"]} of {st["met"] + st["not_met"] + st["unresolved"]})</tspan></text>')
        s.append(f'<line x1="{left}" y1="{gy}" x2="{left}" y2="{gy + row_h * 3}" stroke="{AXIS}" stroke-width="1"/>')
    s.append("</svg>")
    return "\n".join(s)


def gap_svg(datas) -> str:
    w, left, right, row_h, top = 1200, 150, 40, 48, 70
    h = top + row_h * len(datas) + 40
    inner = w - left - right
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family=\'{FONT}\'>',
         f'<rect width="{w}" height="{h}" fill="{SURFACE}"/>',
         f'<text x="{left}" y="34" font-size="22" font-weight="600" fill="{INK}">The generosity gap</text>',
         f'<text x="{left}" y="54" font-size="13" fill="{INK2}">Lenient hit rate minus strict hit rate, in percentage points. How much the grade depends on who is grading.</text>']
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        x = left + inner * t
        s.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + row_h * len(datas)}" stroke="{GRID}" stroke-width="1"/>')
        s.append(f'<text x="{x:.1f}" y="{top + row_h * len(datas) + 18}" font-size="12" fill="{MUTED}" text-anchor="middle">{round(t * 100)} pts</text>')
    for i, data in enumerate(datas):
        gap = data["aggregate"]["generosity_gap"] or 0
        y = top + i * row_h + 10
        bw = inner * max(gap, 0)
        s.append(f'<text x="{left - 12}" y="{y + 18}" font-size="14" fill="{INK}" text-anchor="end">{html.escape(data["run"]["subject"]["name"])}</text>')
        s.append(f'<rect x="{left}" y="{y}" width="{bw:.1f}" height="26" rx="3" fill="{ACCENT}"/>')
        s.append(f'<text x="{left + bw + 8:.1f}" y="{y + 18}" font-size="13" font-family=\'{MONO}\' fill="{INK}">{round(gap * 100)} pts</text>')
    s.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + row_h * len(datas)}" stroke="{AXIS}" stroke-width="1"/>')
    s.append("</svg>")
    return "\n".join(s)


def _hbar_chart(title: str, subtitle: str, groups: list[tuple[str, str, list[tuple[str, float | None, str]]]], axis_max: float = 1.0, axis_fmt=lambda t: f"{round(t * 100)}%") -> str:
    """Generic small-multiples horizontal bars: groups of (name, note, [(label, value, annotation), ...])."""
    w, left, right, row_h, gap = 1200, 190, 210, 40, 54
    inner = w - left - right
    # Wrap the subtitle at about 120 characters so it never runs past the right edge.
    sub_lines, line = [], ""
    for word in subtitle.split():
        if len(line) + len(word) + 1 > 120:
            sub_lines.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        sub_lines.append(line)
    top_pad = 96 + 18 * (len(sub_lines) - 1)
    h = top_pad + sum(28 + row_h * len(rows) + gap for _, _, rows in groups) + 10  # 28 px of group heading per group
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" font-family=\'{FONT}\'>',
         f'<rect width="{w}" height="{h}" fill="{SURFACE}"/>',
         f'<text x="{left}" y="34" font-size="22" font-weight="600" fill="{INK}">{html.escape(title)}</text>']
    for i, sl in enumerate(sub_lines):
        s.append(f'<text x="{left}" y="{54 + 18 * i}" font-size="13" fill="{INK2}">{html.escape(sl)}</text>')
    y0 = top_pad
    last_gy = 0
    for gi, (name, note, rows) in enumerate(groups):
        s.append(f'<text x="{left}" y="{y0}" font-size="16" font-weight="600" fill="{INK}">{html.escape(name)}</text>')
        if note:
            s.append(f'<text x="{left}" y="{y0 + 18}" font-size="12" fill="{MUTED}">{html.escape(note)}</text>')
        gy = y0 + 28
        for t in (0, 0.25, 0.5, 0.75, 1.0):
            x = left + inner * t
            s.append(f'<line x1="{x:.1f}" y1="{gy}" x2="{x:.1f}" y2="{gy + row_h * len(rows)}" stroke="{GRID}" stroke-width="1"/>')
        for j, (label, val, ann) in enumerate(rows):
            y = gy + j * row_h + 7
            bw = inner * (0 if val is None else min(val / axis_max, 1.0))
            s.append(f'<text x="{left - 12}" y="{y + 18}" font-size="14" fill="{INK}" text-anchor="end">{html.escape(label)}</text>')
            s.append(f'<rect x="{left}" y="{y}" width="{bw:.1f}" height="26" rx="3" fill="{color_for(label)}"/>')
            s.append(f'<text x="{left + bw + 8:.1f}" y="{y + 18}" font-size="13" font-family=\'{MONO}\' fill="{INK}">{"n/a" if val is None else axis_fmt(val)} <tspan fill="{MUTED}">{html.escape(ann)}</tspan></text>')
        s.append(f'<line x1="{left}" y1="{gy}" x2="{left}" y2="{gy + row_h * len(rows)}" stroke="{AXIS}" stroke-width="1"/>')
        last_gy = gy + row_h * len(rows)
        y0 = last_gy + gap
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        x = left + inner * t
        s.append(f'<text x="{x:.1f}" y="{last_gy + 20}" font-size="12" fill="{MUTED}" text-anchor="middle">{axis_fmt(t * axis_max)}</text>')
    s.append("</svg>")
    return "\n".join(s)


def resolved_vs_all_svg(datas) -> str:
    groups = []
    for data in datas:
        pb = data["aggregate"]["per_bar"]
        rows = []
        for key, label in (("strict", "Strict"), ("lenient", "Lenient")):
            st = pb[key]
            rows.append((f"{label}, all claims", st["hit_rate_all"], f"({st['met']} of {st['met'] + st['not_met'] + st['unresolved']})"))
            rows.append((f"{label}, resolved only", st["hit_rate"], f"({st['met']} of {st['resolved']})"))
        groups.append((data["run"]["subject"]["name"], f"{pb['strict']['unresolved']} of {data['aggregate']['n_claims']} unresolved at strict", rows))
    return _hbar_chart("The same list, two honest grades", "Hit rate counting unresolved claims against the author (all claims) versus ignoring them (resolved only). A grader can publish either number.", groups)


def numbers_vs_words_svg(datas) -> str:
    """Split every graded claim by the classifier's specificity score (0 to 3): 2.5 and above has a number, date or threshold."""
    buckets = {"Claims with a number, date or threshold (specificity 2.5 to 3)": [], "Claims without one (specificity below 2.5)": []}
    for data in datas:
        grades = {(g["claim_id"], g["bar"]): g for g in data["grades"]}
        for c in data["claims"]:
            sc = (c.get("scores") or {}).get("specificity")
            if sc is None or (c["id"], "strict") not in grades:
                continue
            key = list(buckets)[0] if sc >= 2.5 else list(buckets)[1]
            buckets[key].append({b: grades[(c["id"], b)]["verdict"] for b in ("strict", "standard", "lenient")})
    groups = []
    for name, rows in buckets.items():
        n = len(rows)
        out = []
        for b in ("strict", "standard", "lenient"):
            met = sum(1 for r in rows if r[b] == "met")
            out.append((b.title(), met / n if n else None, f"({met} of {n})"))
        strict = sum(1 for r in rows if r["strict"] == "met") / n if n else 0
        lenient = sum(1 for r in rows if r["lenient"] == "met") / n if n else 0
        groups.append((name, f"{n} claims across all subjects, generosity gap {round((lenient - strict) * 100)} points", out))
    return _hbar_chart("Numbers protect the reader", "Hit rate at each bar for claims with a number, date or threshold versus claims without, pooled across subjects. Specificity was scored by the classifier before any evidence was seen. A number narrows the gap and makes the author easier to catch.", groups)


def self_grade_svg(datas) -> str:
    """Bob Doll's own October scorecard beside called-it's standard bar. His tally is from his 4Q26 commentary."""
    doll = next((d for d in datas if d["run"]["name"] == "doll"), None)
    if not doll:
        return ""
    pb = doll["aggregate"]["per_bar"]["standard"]
    n = doll["aggregate"]["n_claims"]
    groups = [
        ("Bob Doll, grading himself (Oct 5, 2026)", "10 predictions: 5 heading in the right direction, 0 wrong, 5 too soon or too close to call",
         [("Right direction", 5 / 10, "(5 of 10)"), ("Wrong", 0.0, "(0 of 10)"), ("Too soon", 5 / 10, "(5 of 10)")]),
        ("called-it, standard bar (Oct 24, 2026)", f"{n} claims from the same 10 predictions",
         [("Met", pb["met"] / n, f"({pb['met']} of {n})"), ("Not met", pb["not_met"] / n, f"({pb['not_met']} of {n})"), ("Unresolved", pb["unresolved"] / n, f"({pb['unresolved']} of {n})")]),
    ]
    return _hbar_chart("The word 'wrong'", "The same ten predictions, graded by their author and by called-it at the standard bar, three weeks apart. The difference is almost entirely which outcomes get called wrong.", groups)


def wrap(svg: str, title: str) -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title>'
            f'<style>{brand.font_face_css(FONT_PREFIX)}\nhtml,body{{margin:0;background:{SURFACE}}}</style></head><body>{svg}</body></html>')


def main(argv):
    out = ROOT / "article" / "figures"
    runs = []
    args = argv[1:]
    if "--out" in args:
        i = args.index("--out")
        out = pathlib.Path(args[i + 1])
        args = args[:i] + args[i + 2:]
    runs = args or sorted((p for p in (ROOT / "runs").iterdir() if (p / "data.json").exists()),
                          key=lambda p: -(json.loads((p / "data.json").read_text())["aggregate"]["generosity_gap"] or 0))
    datas = load(runs)
    if not datas:
        sys.exit("no graded runs found")
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in (("hit-rates", hit_rates_svg), ("generosity-gap", gap_svg), ("resolved-vs-all", resolved_vs_all_svg),
                     ("numbers-vs-words", numbers_vs_words_svg), ("self-grade", self_grade_svg)):
        svg = fn(datas)
        if not svg:
            continue
        (out / f"{name}.svg").write_text(svg)
        (out / f"{name}.html").write_text(wrap(svg, name))
        print(f"wrote {out / name}.svg/.html for {len(datas)} subjects")
        if "--no-png" not in argv:
            import re
            import subprocess
            h = re.search(r'height="(\d+)"', svg).group(1)
            subprocess.run([sys.executable, str(ROOT / "tools" / "render_png.py"), str(out / f"{name}.html"), str(out / f"{name}.png"), "1200", h], check=True)


if __name__ == "__main__":
    main(sys.argv)
