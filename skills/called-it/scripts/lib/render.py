"""Render a run into report.md, report.html and data.json.

The HTML is dark only, on the Called It! brand tokens in lib/brand.py (sample B: ground #0F1218,
amber accent, Space Grotesk for text, IBM Plex Mono for numerals). The fonts are self-hosted under
site/assets/fonts/; the page states where they are through `font_prefix` (default: the path from a
run folder to the site's fonts; the site builder rewrites it in its copies). Every verdict cell
carries a glyph and a word as well as a colour, and every bar carries its label and value.
"""
from __future__ import annotations

import html
import json

from . import brand, config

GLYPH = {"met": "✓", "not_met": "✗", "unresolved": "○"}
WORD = {"met": "met", "not_met": "not met", "unresolved": "unresolved"}
BAR_LABEL = {"strict": "Strict", "standard": "Standard", "lenient": "Lenient"}


def _short(s: str, n: int = 110) -> str:
    s = " ".join((s or "").split())
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _pct(x) -> str:
    return "n/a" if x is None else f"{round(x * 100)}%"


def _esc(s) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def badge(run: dict, models: dict[str, int]) -> str:
    grader = ", ".join(sorted(models)) if models else "no grader answers yet"
    return f"{config.BADGE_EMOJI} {config.NAME} v{config.VERSION} · {run['subject']['name']} · {run['target_year']} · graded {run['evidence_window']['end']} · {grader}"


def footer(run: dict, sources, claims, evidence, grades, agg, models, extras) -> str:
    tiers = {t: sum(1 for e in evidence if e["tier"] == t) for t in config.EVIDENCE_TIERS}
    readable = sum(1 for s in sources if s.get("access") != "unreadable")
    th = run["thresholds"]
    lines = [
        "<!-- PASS-THROUGH FOOTER -->",
        "---",
        f"**{config.NAME} v{config.VERSION}** · run `{run['name']}` · target year {run['target_year']} · season {run['season_window']['start']} to {run['season_window']['end']} · evidence {run['evidence_window']['start']} to {run['evidence_window']['end']}",
        f"Grader: {', '.join(f'{m} ({n} answers)' for m, n in sorted(models.items())) or 'none'} · policy: met needs P(met) ≥ {th['yes']} and evidence strength ≥ {th['min_strength']}; not met needs P(contradicted) ≥ {th['yes']}; bars are nested, so a stricter bar met implies the looser ones met and a looser bar not met implies the stricter ones not met ({sum(1 for g in grades if g.get('implied_from'))} cells implied)",
        f"Sources {len(sources)} ({readable} readable) · claims graded {agg['n_claims']} · evidence items {len(evidence)} (T1 {tiers[1]}, T2 {tiers[2]}, T3 {tiers[3]}, T4 {tiers[4]}, T5 {tiers[5]}) · (claim, bar) pairs {len(grades)}",
        f"Hit rate strict {_pct(agg['per_bar']['strict']['hit_rate_all'])} · standard {_pct(agg['per_bar']['standard']['hit_rate_all'])} · lenient {_pct(agg['per_bar']['lenient']['hit_rate_all'])} · generosity gap {('n/a' if agg['generosity_gap'] is None else f'{round(agg['generosity_gap'] * 100)} points')}",
    ]
    if extras.get("x_posts"):
        lines.append(f"X API posts read {extras['x_posts']} (about ${extras['x_spend']:.2f}) · Jev input tokens {extras.get('jev_tokens', 'n/a')}")
    lines += ["---", "<!-- END PASS-THROUGH FOOTER -->"]
    return "\n".join(lines)


# ------------------------------------------------------------------ markdown

def frontmatter(run: dict, models: dict, extras: dict) -> str:
    lines = ["---", f"tool: {config.NAME} {config.VERSION}", f"run: {run['name']}", f"subject: {json.dumps(run['subject']['name'])}",
             f"target_year: {run['target_year']}", f"season_window: {run['season_window']['start']} to {run['season_window']['end']}",
             f"evidence_window: {run['evidence_window']['start']} to {run['evidence_window']['end']}",
             f"grader: {json.dumps(', '.join(sorted(models)) or 'none')}",
             f"thresholds: {json.dumps(run['thresholds'])}"]
    if extras.get("input_sha256"):
        lines.append("inputs_sha256:")
        for k, v in extras["input_sha256"].items():
            lines.append(f"  {k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def markdown(run, sources, claims, rubrics, evidence, grades, agg, models, extras) -> str:
    by_id = {c["id"]: c for c in claims}
    rub = {r["claim_id"]: r for r in rubrics}
    g = {(x["claim_id"], x["bar"]): x for x in grades}
    ev_by = {}
    for e in evidence:
        ev_by.setdefault(e["claim_id"], []).append(e)
    src = {s["id"]: s for s in sources}
    pb = agg["per_bar"]
    out = [frontmatter(run, models, extras), "", badge(run, models), ""]
    out.append(f"# {run['subject']['name']}: {run['target_year']} predictions, graded")
    out.append("")
    out.append(f"{agg['n_claims']} claims graded at three bars. Hit rate **{_pct(pb['strict']['hit_rate_all'])} strict**, "
               f"**{_pct(pb['standard']['hit_rate_all'])} standard**, **{_pct(pb['lenient']['hit_rate_all'])} lenient**. "
               f"Generosity gap (lenient minus strict): **{'n/a' if agg['generosity_gap'] is None else str(round(agg['generosity_gap'] * 100)) + ' points'}**. "
               f"Unresolved at the strict bar: {pb['strict']['unresolved']}.")
    out.append("")
    out.append("| Bar | Met | Not met | Unresolved | Hit rate (all claims) | Hit rate (resolved only) |")
    out.append("|---|---:|---:|---:|---:|---:|")
    for bar in config.BARS:
        s = pb[bar]
        out.append(f"| {BAR_LABEL[bar]} | {s['met']} | {s['not_met']} | {s['unresolved']} | {_pct(s['hit_rate_all'])} | {_pct(s['hit_rate'])} |")
    out.append("")
    out.append("## Ladder")
    out.append("")
    out.append("| # | Claim | Author | Strict | Standard | Lenient | Best evidence |")
    out.append("|---|---|---|:---:|:---:|:---:|---|")
    ordered = sorted(claims, key=lambda c: c.get("rank", 999))
    any_prov = False
    for c in ordered:
        cells = []
        for bar in config.BARS:
            gr = g.get((c["id"], bar), {})
            v = gr.get("verdict", "unresolved")
            mark = "°" if gr.get("provisional") else ""
            any_prov = any_prov or bool(gr.get("provisional"))
            cells.append(f"{GLYPH[v]} {WORD[v]}{mark}")
        evs = sorted(ev_by.get(c["id"], []), key=lambda e: e["tier"])
        best = f"T{evs[0]['tier']} [{_esc(evs[0]['source'])}]({evs[0]['url']})" if evs else "none"
        out.append(f"| {c['id']} | {_short(c['quote'])} | {c.get('author', '')} | {cells[0]} | {cells[1]} | {cells[2]} | {best} |")
    out.append("")
    if any_prov:
        out.append(f"° provisional: the claim's horizon is after {run['evidence_window']['end']}, so this is the standing as of the run date, not a final grade.")
        out.append("")
    out.append("## Claims")
    out.append("")
    for c in ordered:
        s = src.get(c["source_id"], {})
        out.append(f"### {c['id']}. {_short(c['quote'], 140)}")
        out.append("")
        out.append(f"> {c['quote']}")
        out.append("")
        meta = f"{c.get('author', '')}, {c.get('date', '')}, [{_esc(s.get('title', c['source_id']))}]({s.get('url', '')})"
        if c.get("attribution") == "guest":
            meta += " (guest, not the subject)"
        if c.get("split_of"):
            meta += f" (split from {c['split_of']})"
        out.append(meta)
        if c.get("context"):
            out.append("")
            out.append(f"Context: {c['context']}")
        out.append("")
        r = rub.get(c["id"])
        for bar in config.BARS:
            gr = g.get((c["id"], bar), {})
            v = gr.get("verdict", "unresolved")
            crit = r["bars"][bar]["criterion"] if r else "(no rubric)"
            probs = ""
            if gr.get("met_p") is not None:
                probs = f" · P(met) {gr['met_p']:.2f}, P(contradicted) {gr['contradicted_p']:.2f}, strength {gr['strength']:.2f}"
            out.append(f"- **{BAR_LABEL[bar]}: {GLYPH[v]} {WORD[v]}**{probs}. {crit}" + (f" ({gr.get('reason')})" if gr.get("reason") and v == "unresolved" else ""))
        evs = sorted(ev_by.get(c["id"], []), key=lambda e: (e["tier"], e["date"]))
        if evs:
            out.append("")
            out.append("Evidence:")
            for e in evs:
                bars = f" [{', '.join(e['bars'])}]" if e.get("bars") else ""
                out.append(f"- T{e['tier']} {e['direction']}{bars} · {e['date']} · [{_esc(e['source'])}]({e['url']}): \"{_short(e['quote'], 220)}\"")
        out.append("")
    out.append(footer(run, sources, claims, evidence, grades, agg, models, extras))
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------ html

REPORT_CSS = """
body { font-size: 15px; line-height: 1.5; }
main { max-width: 1040px; margin: 0 auto; padding: 32px 16px 64px; }
.badge { color: var(--muted); font-size: 13px; letter-spacing: .04em; text-transform: uppercase; }
h1 { font-size: 30px; font-weight: 700; margin: 10px 0 4px; letter-spacing: -.02em; }
h2 { font-size: 21px; font-weight: 700; margin: 40px 0 12px; letter-spacing: -.01em; }
h3 { font-size: 16px; font-weight: 700; margin: 28px 0 8px; }
.lede { color: var(--ink-2); max-width: 70ch; }
.tiles { display:grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 20px 0; }
.tile { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; }
.tile .k { color: var(--muted); font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
.tile .v { font-family: var(--font-mono); font-variant-numeric: tabular-nums; font-size: 32px; font-weight: 600; margin-top: 2px; line-height: 1.1; }
.tile .s { color: var(--muted); font-size: 12px; margin-top: 4px; }
.tile.gap { background: var(--accent); border-color: var(--accent); color: var(--on-accent); }
.tile.gap .k, .tile.gap .s { color: var(--on-accent-small); }
.chart { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px; }
.chart svg { width: 100%; height: auto; display: block; }
.chart .bar-strict { fill: var(--bar-strict); } .chart .bar-standard { fill: var(--bar-standard); } .chart .bar-lenient { fill: var(--bar-lenient); }
.chart .bar:hover { opacity: .85; }
.chart text { fill: var(--ink); font-size: 13px; font-family: var(--font-text); }
.chart .val { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
.chart .axis-label { fill: var(--muted); font-size: 12px; font-family: var(--font-mono); }
.chart .grid { stroke: var(--border); stroke-width: 1; }
.chart .baseline { stroke: var(--border); stroke-width: 1; }
table { width: 100%; border-collapse: collapse; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; font-size: 14px; }
th, td { text-align: left; padding: 9px 10px; border-top: 1px solid var(--border); vertical-align: top; }
th { color: var(--muted); font-weight: 700; font-size: 12px; text-transform: uppercase; letter-spacing: .06em; border-top: 0; }
td.num, th.num { text-align: right; font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
.v { white-space: nowrap; font-weight: 700; font-size: 13px; }
.v .dot { display:inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; vertical-align: -1px; box-shadow: 0 0 0 2px var(--surface); }
.v-met .dot { background: var(--good); } .v-met { color: var(--good); }
.v-not_met .dot { background: var(--critical); } .v-not_met { color: var(--critical); }
.v-unresolved .dot { background: var(--open); } .v-unresolved { color: var(--ink-2); }
.claim { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; margin: 14px 0; }
.claim blockquote { margin: 0 0 8px; padding-left: 12px; border-left: 3px solid var(--accent); color: var(--ink); font-size: 16px; }
.claim .meta, .claim .ctx { color: var(--ink-2); font-size: 13px; }
.bars { list-style: none; padding: 0; margin: 12px 0 0; }
.bars li { padding: 8px 0; border-top: 1px solid var(--border); }
.bars .crit { color: var(--ink-2); font-size: 14px; }
.bars .p { color: var(--muted); font-size: 12px; font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
.ev { margin: 10px 0 0; padding-left: 18px; font-size: 13px; color: var(--ink-2); }
.ev li { margin: 4px 0; }
.tier { display:inline-block; min-width: 24px; text-align:center; font-size: 11px; font-weight: 600; font-family: var(--font-mono); border: 1px solid var(--border); border-radius: 4px; padding: 0 4px; margin-right: 6px; color: var(--ink); background: var(--surface-2); }
footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--border); color: var(--ink-2); font-size: 13px; }
footer code { font-size: 12px; }
@media (max-width: 640px) { h1 { font-size: 22px; } .tile .v { font-size: 24px; } th, td { padding: 7px 6px; } }
"""


def css(font_prefix: str = brand.DEFAULT_FONT_PREFIX) -> str:
    return brand.base_css(font_prefix) + "\n" + REPORT_CSS


def _verdict_cell(v: str) -> str:
    return f'<span class="v v-{v}" title="{WORD[v]}"><span class="dot" aria-hidden="true"></span>{GLYPH[v]} {WORD[v]}</span>'


def _bar_chart(agg: dict) -> str:
    """Three horizontal bars (one hue, direct labels, no legend), with native tooltips per bar."""
    w, row_h, left, right, top = 720, 44, 110, 60, 12
    h = top + row_h * 3 + 28
    inner = w - left - right
    parts = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Hit rate at each bar">']
    for i, t in enumerate((0, 0.25, 0.5, 0.75, 1.0)):
        x = left + inner * t
        parts.append(f'<line class="grid" x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top + row_h * 3}"/>')
        parts.append(f'<text class="axis-label" x="{x:.1f}" y="{top + row_h * 3 + 20}" text-anchor="middle">{round(t * 100)}%</text>')
    for i, bar in enumerate(config.BARS):
        s = agg["per_bar"][bar]
        rate = s["hit_rate_all"] or 0
        y = top + i * row_h + 8
        bw = max(inner * rate, 0)
        parts.append(f'<text x="{left - 12}" y="{y + 18}" text-anchor="end">{BAR_LABEL[bar]}</text>')
        parts.append(f'<rect class="bar bar-{bar}" x="{left}" y="{y}" width="{bw:.1f}" height="26" rx="3" ry="3">'
                     f'<title>{BAR_LABEL[bar]}: {s["met"]} met, {s["not_met"]} not met, {s["unresolved"]} unresolved</title></rect>')
        parts.append(f'<text class="val" x="{left + bw + 8:.1f}" y="{y + 18}">{_pct(s["hit_rate_all"])} <tspan class="axis-label">({s["met"]} of {s["met"] + s["not_met"] + s["unresolved"]})</tspan></text>')
    parts.append(f'<line class="baseline" x1="{left}" y1="{top}" x2="{left}" y2="{top + row_h * 3}"/>')
    parts.append("</svg>")
    return "\n".join(parts)


def html_report(run, sources, claims, rubrics, evidence, grades, agg, models, extras, font_prefix: str = brand.DEFAULT_FONT_PREFIX) -> str:
    rub = {r["claim_id"]: r for r in rubrics}
    g = {(x["claim_id"], x["bar"]): x for x in grades}
    ev_by = {}
    for e in evidence:
        ev_by.setdefault(e["claim_id"], []).append(e)
    src = {s["id"]: s for s in sources}
    pb = agg["per_bar"]
    gap = agg["generosity_gap"]
    ordered = sorted(claims, key=lambda c: c.get("rank", 999))
    title = f"{run['subject']['name']} {run['target_year']} predictions"
    o = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">',
         f"<title>{_esc(title)}</title><style>{css(font_prefix)}</style>"
         "</head><body><main>",
         f'<div class="badge">{_esc(badge(run, models))}</div>',
         f"<h1>{_esc(run['subject']['name'])}: {run['target_year']} predictions, graded</h1>",
         f'<p class="lede">{agg["n_claims"]} claims, each graded at three bars against evidence from {run["evidence_window"]["start"]} to {run["evidence_window"]["end"]}. '
         f'The strict bar is what a hostile critic would require, the lenient bar is the weakest reading a critic would still concede, and the gap between them is how much the grade depends on who is grading.</p>',
         '<div class="tiles">']
    for bar in config.BARS:
        s = pb[bar]
        o.append(f'<div class="tile"><div class="k">{BAR_LABEL[bar]}</div><div class="v">{_pct(s["hit_rate_all"])}</div><div class="s">{s["met"]} met · {s["not_met"]} not met · {s["unresolved"]} unresolved</div></div>')
    o.append(f'<div class="tile gap"><div class="k">Generosity gap</div><div class="v">{"n/a" if gap is None else f"{round(gap * 100)} pts"}</div><div class="s">lenient minus strict</div></div>')
    o.append("</div>")
    o.append(f'<div class="chart">{_bar_chart(agg)}</div>')
    o.append("<h2>Ladder</h2>")
    o.append('<table><thead><tr><th>#</th><th>Claim</th><th>Author</th><th>Strict</th><th>Standard</th><th>Lenient</th><th>Best evidence</th></tr></thead><tbody>')
    for c in ordered:
        evs = sorted(ev_by.get(c["id"], []), key=lambda e: e["tier"])
        best = f'<span class="tier">T{evs[0]["tier"]}</span><a href="{_esc(evs[0]["url"])}">{_esc(evs[0]["source"])}</a>' if evs else '<span class="ev">none</span>'
        cells = "".join(
            f"<td>{_verdict_cell(g.get((c['id'], b), {}).get('verdict', 'unresolved'))}"
            + ('<div class="p">provisional</div>' if g.get((c["id"], b), {}).get("provisional") else "") + "</td>"
            for b in config.BARS)
        o.append(f'<tr><td>{_esc(c["id"])}</td><td><a href="#{_esc(c["id"])}">{_esc(_short(c["quote"]))}</a></td><td>{_esc(c.get("author", ""))}</td>{cells}<td>{best}</td></tr>')
    o.append("</tbody></table>")
    o.append("<h2>Claims</h2>")
    for c in ordered:
        s = src.get(c["source_id"], {})
        o.append(f'<section class="claim" id="{_esc(c["id"])}"><h3>{_esc(c["id"])}. {_esc(_short(c["quote"], 140))}</h3>')
        o.append(f"<blockquote>{_esc(c['quote'])}</blockquote>")
        meta = f'{_esc(c.get("author", ""))}, {_esc(c.get("date", ""))}, <a href="{_esc(s.get("url", ""))}">{_esc(s.get("title", c["source_id"]))}</a>'
        if c.get("attribution") == "guest":
            meta += " · guest, not the subject"
        if c.get("split_of"):
            meta += f" · split from {_esc(c['split_of'])}"
        o.append(f'<div class="meta">{meta}</div>')
        if c.get("context"):
            o.append(f'<div class="ctx">Context: {_esc(c["context"])}</div>')
        r = rub.get(c["id"])
        o.append('<ul class="bars">')
        for bar in config.BARS:
            gr = g.get((c["id"], bar), {})
            v = gr.get("verdict", "unresolved")
            crit = r["bars"][bar]["criterion"] if r else "(no rubric)"
            p = ""
            if gr.get("met_p") is not None:
                p = f'<div class="p">P(met) {gr["met_p"]:.2f} · P(contradicted) {gr["contradicted_p"]:.2f} · evidence strength {gr["strength"]:.2f} of 2</div>'
            elif gr.get("reason"):
                p = f'<div class="p">{_esc(gr["reason"])}</div>'
            o.append(f'<li><div><strong>{BAR_LABEL[bar]}</strong> &nbsp; {_verdict_cell(v)}</div><div class="crit">{_esc(crit)}</div>{p}</li>')
        o.append("</ul>")
        evs = sorted(ev_by.get(c["id"], []), key=lambda e: (e["tier"], e["date"]))
        if evs:
            o.append('<ul class="ev">')
            for e in evs:
                bars = f' [{", ".join(e["bars"])}]' if e.get("bars") else ""
                o.append(f'<li><span class="tier">T{e["tier"]}</span>{_esc(e["direction"])}{_esc(bars)} · {_esc(e["date"])} · <a href="{_esc(e["url"])}">{_esc(e["source"])}</a>: “{_esc(_short(e["quote"], 220))}”</li>')
            o.append("</ul>")
        o.append("</section>")
    foot = footer(run, sources, claims, evidence, grades, agg, models, extras)
    foot_html = "<br>".join(_esc(l) for l in foot.splitlines() if l and not l.startswith(("<!--", "---")))
    o.append(f"<footer>{foot_html}</footer></main></body></html>")
    return "\n".join(o)


# ------------------------------------------------------------------ data

def data(run, sources, claims, rubrics, evidence, grades, agg, models, extras) -> dict:
    return {
        "tool": {"name": config.NAME, "version": config.VERSION},
        "run": {k: run[k] for k in ("name", "subject", "target_year", "season_window", "evidence_window", "thresholds")},
        "grader_models": models,
        "aggregate": agg,
        "claims": [{k: c.get(k) for k in ("id", "quote", "author", "date", "attribution", "kind", "domain", "rank", "scores", "split_of", "source_id")} for c in claims],
        "rubrics": rubrics,
        "grades": grades,
        "evidence": evidence,
        "sources": sources,
        "extras": extras,
    }


def render(run, sources, claims, rubrics, evidence, grades, agg, models, extras=None) -> dict:
    extras = extras or {}
    return {
        "markdown": markdown(run, sources, claims, rubrics, evidence, grades, agg, models, extras),
        "html": html_report(run, sources, claims, rubrics, evidence, grades, agg, models, extras),
        "data": data(run, sources, claims, rubrics, evidence, grades, agg, models, extras),
    }
